#!/usr/bin/env python3
"""Build the public site catalog from the immutable Discord posting history.

The Discord registry determines *which* opportunities belong in the catalog.
Saved posting batches supply details. The latest report determines which posted
entries are still in the verified open/rolling roster. This never edits the
Discord registry or reads the webhook.
"""

from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from participation import classify
from rewards import select_award


SITE_DIR = Path(__file__).resolve().parent
WORK_DIR = SITE_DIR.parent.parent
POSTER_DIR = WORK_DIR / "work" / "discord-opportunity-poster"
REGISTRY = POSTER_DIR / "posted_opportunities.json"
DEFAULT_OUTPUT = SITE_DIR / "dist" / "opportunities.json"
AWARD_ASSESSMENTS = SITE_DIR / "data" / "max-awards.json"
MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}
DETAIL_FIELDS = (
    "type", "fit", "dates", "apply_by", "submit_by", "eligibility",
    "location", "reward", "description", "team_min", "team_max",
    "solo_allowed", "student_only", "entry_open",
    "participation_mode", "remote_eligible", "attendance_required",
    "attendance_region", "participation_note", "participation_evidence_url",
    "attendance_countries",
)


def canonical(value: str) -> str:
    return " ".join(re.findall(r"[a-z0-9]+", value.casefold()))


def saved_batches(batches_dir: Path | None = None, registry_path: Path | None = None) -> list[dict]:
    records: list[dict] = []
    for path in sorted((batches_dir or POSTER_DIR).glob("*.json")):
        if path.resolve() == (registry_path or REGISTRY).resolve():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        items = data.get("opportunities") if isinstance(data, dict) else data
        if isinstance(items, list):
            records.extend(item for item in items if isinstance(item, dict))
    return records


def section(markdown: str, heading: str) -> str:
    match = re.search(rf"(?ms)^## {re.escape(heading)}\n(.*?)(?=^## |\Z)", markdown)
    return match.group(1) if match else ""


def table_rows(text: str) -> list[list[str]]:
    rows = []
    for line in text.splitlines():
        if not line.startswith("| ") or line.startswith("| Opportunity ") or line.startswith("| Program "):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and not all(re.fullmatch(r"[-: ]+", cell) for cell in cells):
            rows.append(cells)
    return rows


def report_entries(markdown: str) -> list[dict]:
    entries = []
    for cells in table_rows(section(markdown, "Open now")):
        if len(cells) >= 9:
            entries.append(dict(name=cells[0], type_fit=cells[1], dates=cells[2],
                                apply_by=cells[3], submit_by=cells[4],
                                eligibility=cells[5], location=cells[6], reward=cells[7],
                                rolling=False))
    for cells in table_rows(section(markdown, "Rolling or no-deadline grants")):
        if len(cells) >= 6:
            entries.append(dict(name=cells[0], type_fit=cells[1], dates=cells[1],
                                apply_by=cells[2], submit_by="Not stated",
                                eligibility=cells[3], location="Not stated", reward=cells[4],
                                rolling=True))
    return entries


def matching_report_entry(record: dict, entries: list[dict]) -> dict | None:
    names = [record.get("name", ""), *(record.get("aliases") or [])]
    names = [canonical(name) for name in names if name]
    exact = [entry for entry in entries if canonical(entry["name"]) in names]
    if len(exact) == 1:
        return exact[0]
    if len(exact) > 1:
        return None
    scored = sorted(
        ((max(SequenceMatcher(None, name, canonical(entry["name"])).ratio()
              for name in names), entry) for entry in entries),
        key=lambda pair: pair[0], reverse=True,
    ) if names else []
    if scored and scored[0][0] >= 0.90 and (len(scored) == 1 or scored[0][0] - scored[1][0] >= 0.08):
        return scored[0][1]
    return None


def matching_concern(record: dict, concerns: list[dict]) -> dict | None:
    def comparable(name: str) -> str:
        return re.sub(r"\b20\d{2}\b", "", canonical(name)).strip()

    identities = {str(record.get("identity", ""))}
    names = {comparable(str(name)) for name in [record.get("name", ""), *(record.get("aliases") or [])] if name}
    organizer = canonical(str(record.get("organizer", "")))
    for concern in concerns:
        if str(concern.get("identity", "")) in identities:
            return concern
        other_names = {comparable(str(name)) for name in [concern.get("name", ""), *(concern.get("aliases") or [])] if name}
        if names & other_names:
            return concern
        other_organizer = canonical(str(concern.get("organizer", "")))
        if organizer and organizer == other_organizer and any(
            SequenceMatcher(None, first, second).ratio() >= 0.90
            for first in names for second in other_names
        ):
            return concern
    return None


def date_key(label: str) -> str | None:
    lower = label.casefold()
    if any(phrase in lower for phrase in ("cutoff not stated", "deadline not stated", "no fixed deadline", "no separate cutoff")):
        return None
    match = re.search(
        r"\b(January|February|March|April|May|June|July|August|September|October|November|December|"
        r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)\.?\s+(\d{1,2})\b",
        label, re.IGNORECASE,
    )
    if not match:
        return None
    month = MONTHS[match.group(1)[:3].lower()]
    day = int(match.group(2))
    if not 1 <= day <= 31:
        return None
    year_match = re.search(r"\b20\d{2}\b", label)
    year = int(year_match.group()) if year_match else 2026
    return f"{year:04d}-{month:02d}-{day:02d}"


def build(report_path: Path, registry_path: Path | None = None, batches_dir: Path | None = None,
          awards_path: Path | None = None) -> dict:
    registry_path = registry_path or REGISTRY
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    posted = registry["posted"]
    concerns = registry.get("trust_concerns_posted", [])
    if not isinstance(concerns, list):
        raise ValueError("Invalid trust-concerns registry")
    batches = saved_batches(batches_dir, registry_path)
    awards = json.loads((awards_path or AWARD_ASSESSMENTS).read_text(encoding="utf-8"))
    report = report_path.read_text(encoding="utf-8")
    active_entries = report_entries(report)
    by_identity: dict[str, list[dict]] = {}
    by_name: dict[str, list[dict]] = {}
    for item in batches:
        if item.get("identity"):
            by_identity.setdefault(str(item["identity"]), []).append(item)
        if item.get("name"):
            by_name.setdefault(canonical(str(item["name"])), []).append(item)

    catalog = []
    detailed_count = 0
    active_count = 0
    for prior in posted:
        record = {key: prior.get(key) for key in ("identity", "name", "organizer", "aliases", "url", "posted_at")}
        details = by_identity.get(str(prior.get("identity", "")), [])
        if not details:
            details = by_name.get(canonical(str(prior.get("name", ""))), [])
        for detail in details:
            for key in DETAIL_FIELDS:
                if detail.get(key) is not None and detail.get(key) != "":
                    record[key] = detail[key]
        record.update(select_award(awards.get(str(prior.get("identity", "")), {}), *details))
        if details:
            detailed_count += 1
        report_item = matching_report_entry(record, active_entries)
        record["status"] = "open" if report_item else "archived"
        record["rolling"] = bool(report_item and report_item["rolling"])
        if report_item:
            active_count += 1
            for field in ("dates", "apply_by", "submit_by", "eligibility", "location", "reward"):
                if report_item[field] != "Not stated":
                    record[field] = report_item[field]
            if not record.get("type"):
                record["type"] = report_item["type_fit"].split(" · ")[0]
            if not record.get("fit"):
                record["fit"] = report_item["type_fit"].split(" · ")[-1]
        record["deadline_date"] = date_key(str(record.get("apply_by") or ""))
        record["name"] = record.get("name") or "Untitled opportunity"
        record["url"] = record.get("url") or ""
        record.update(classify(record))
        concern = matching_concern(record, concerns)
        if concern:
            record["trust_status"] = "concern"
            record["trust_reason"] = concern.get("reason", "")
            record["trust_evidence_url"] = concern.get("evidence_url", "")
        catalog.append(record)

    return {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "report_date": report_path.stem[-10:],
        "entries": catalog,
        "trust_concerns": [
            {key: concern.get(key) for key in (
                "identity", "name", "organizer", "url", "reason", "evidence_url", "assessed_at"
            )}
            for concern in concerns
        ],
        "summary": {"total": len(catalog), "open": active_count,
                    "archived": len(catalog) - active_count,
                    "trust_concerns": len(concerns),
                    "with_saved_details": detailed_count},
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--registry", type=Path, default=REGISTRY, help="External private posting registry (read-only)")
    parser.add_argument("--batches-dir", type=Path, default=POSTER_DIR, help="External saved posting batches")
    args = parser.parse_args()
    catalog = build(args.report, registry_path=args.registry, batches_dir=args.batches_dir)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(".tmp")
    temporary.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    # A companion script lets the same catalog open directly from file://,
    # where browsers disallow fetch() of a neighboring JSON file.
    script_output = args.output.with_suffix(".js")
    script_temporary = script_output.with_suffix(".js.tmp")
    script_temporary.write_text(
        "window.OPPORTUNITY_CATALOG = " + json.dumps(catalog, ensure_ascii=True) + ";\n",
        encoding="utf-8",
    )
    script_temporary.replace(script_output)
    print(json.dumps(catalog["summary"]))


if __name__ == "__main__":
    main()
