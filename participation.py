"""Conservative participation metadata for saved public opportunity details.

Explicit verified batch fields take precedence. Legacy location text only
establishes a format when it actually describes participation, not merely an
online application or worldwide eligibility.
"""
import re


EUROPE = re.compile(r"\b(europe(?:an)?|albania|andorra|austria|belarus|belgi(?:um|an)|bosnia|bulgaria|croatia|cyprus|czech(?:ia)?|denmark|estonia|finland|france|germany|greece|hungary|iceland|ireland|italy|kosovo|latvia|liechtenstein|lithuania|luxembourg|malta|moldova|monaco|montenegro|netherlands|north macedonia|norway|poland|portugal|romania|san marino|serbia|slovakia|slovenia|spain|sweden|switzerland|ukraine|united kingdom|uk|england|scotland|wales|vatican|lisbon|turin|valencia|ghent|munich|hamburg)\b", re.I)
PHYSICAL = re.compile(r"in[ -]person|on[ -]?site|onsite|travel|final(?:e|ist)?(?: event)?|demo day|attend|campus|\bhq\b", re.I)
REMOTE = re.compile(r"\bonline\b|\bremote(?:ly)?\b|\bvirtual\b", re.I)

# Legacy country names/aliases actually present in saved location descriptions.
# New verified batches supply attendance_countries directly (any country).
COUNTRY_ALIASES = {
    "Belgium": r"belgium|belgian", "Canada": r"canada", "Chile": r"chile",
    "Finland": r"finland", "France": r"france", "Germany": r"germany",
    "Guatemala": r"guatemala", "India": r"india", "Indonesia": r"indonesia",
    "Italy": r"italy", "Japan": r"japan", "Kazakhstan": r"kazakhstan",
    "Lithuania": r"lithuania", "Moldova": r"moldova", "Nigeria": r"nigeria",
    "Portugal": r"portugal", "Singapore": r"singapore", "South Africa": r"south africa",
    "South Korea": r"south korea", "Spain": r"spain", "Switzerland": r"switzerland",
    "United Arab Emirates": r"united arab emirates|uae",
    "United Kingdom": r"united kingdom|uk", "United States": r"united states|usa|us",
    "Vietnam": r"vietnam",
}


def attendance_countries(record: dict, mode: str) -> list[str]:
    if "attendance_countries" in record:
        values = record["attendance_countries"]
        if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
            raise ValueError("attendance_countries must be a list of country names")
        return sorted({value.strip() for value in values if value.strip()})
    if mode not in ("in_person", "hybrid"):
        return []
    # Match stated country names, not cities, residence eligibility or regions.
    location = str(record.get("location") or "")
    return sorted(country for country, aliases in COUNTRY_ALIASES.items()
                  if re.search(rf"\b(?:{aliases})\b", location, re.I))


def classify(record: dict) -> dict:
    location = str(record.get("location") or "")
    text = location.casefold()
    # Negated attendance and optional local activities do not require travel.
    optional = bool(re.search(r"optional|no in-person.*required|fully virtual.*equal prize|online.*or onsite|remote teams expressly accepted", text))
    physical_text = re.sub(r"no in-person.*?required|remote participation not established|finale online", "", text)
    physical = bool(PHYSICAL.search(physical_text) or re.search(r"\bvalencia\s*\+\s*online", text))
    remote_text = re.sub(r"online (?:application|preparation)|remote participation not established|remote option not stated|remote(?:ly)? or as directed", "", text)
    remote = bool(REMOTE.search(remote_text))
    unknown = bool(re.search(r"format not stated|mode .*not stated", text))
    if unknown:
        physical = remote = False
    mode = "not_stated" if unknown else "hybrid" if remote and physical else "remote" if remote else "in_person" if physical else "not_stated"
    attendance = True if physical and not remote else False if remote and (optional or not physical) else True if physical and re.search(r"mandatory|required|teams attend|strictly", text) else None
    eligible = False if attendance is True else True if remote and (optional or not physical) and not unknown else None
    region = "Chile" if re.search(r"\bchile\b", text) else "Europe" if EUROPE.search(text) else "Other" if physical else "Not stated"
    note = "" if mode == "remote" or attendance is True or optional else "Attendance requirements not stated; confirm before planning travel." if mode == "hybrid" else "Participation format not stated; worldwide eligibility is not proof of remote entry." if mode == "not_stated" else ""
    if optional and physical:
        note = "Remote participation available; in-person attendance is optional."
    result = dict(participation_mode=mode, remote_eligible=eligible,
                  attendance_required=attendance, attendance_region=region,
                  participation_note=note, participation_evidence_url="")
    for field in result:
        if field in record and record[field] is not None:
            result[field] = record[field]
    # A required visit never belongs in the remote-only feed.
    if result["attendance_required"] is True:
        result["remote_eligible"] = False
    result["attendance_countries"] = attendance_countries(record, result["participation_mode"])
    return result
