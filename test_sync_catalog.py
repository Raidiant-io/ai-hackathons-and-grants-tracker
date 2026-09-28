import json
import io
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

import sync_catalog
from participation import classify


class ParticipationTests(unittest.TestCase):
    def test_online_build_with_required_final_is_not_remote(self):
        result = classify({"location": "Online build; mandatory in-person finale in Tokyo, Japan"})
        self.assertEqual(result["participation_mode"], "hybrid")
        self.assertFalse(result["remote_eligible"])
        self.assertEqual(result["attendance_region"], "Other")

    def test_unclear_local_final_does_not_promise_remote_prize_access(self):
        for location in ["Online build; Yogyakarta, Indonesia Demo Day; attendance requirement not stated", "Valencia + online"]:
            with self.subTest(location=location):
                self.assertEqual(classify({"location": location})["participation_mode"], "hybrid")
                self.assertIsNone(classify({"location": location})["remote_eligible"])

    def test_optional_local_activities_do_not_exclude_remote_entrants(self):
        result = classify({"location": "Online; optional Santa Clara activities"})
        self.assertTrue(result["remote_eligible"])
        self.assertFalse(result["attendance_required"])

    def test_missing_mode_and_application_only_are_not_remote_proof(self):
        for location in ["Worldwide", "Online application; geography not stated", "Worldwide application; finalists present remotely or as directed, format not stated"]:
            with self.subTest(location=location):
                self.assertIsNone(classify({"location": location})["remote_eligible"])

    def test_in_person_regions_and_explicit_verified_fields(self):
        for location, region in [("Turku, Finland; in person", "Europe"), ("Santiago, Chile; in person", "Chile"), ("Boston, USA; in person", "Other")]:
            with self.subTest(location=location):
                self.assertEqual(classify({"location": location})["attendance_region"], region)
        self.assertTrue(classify({"location": "Worldwide", "participation_mode": "remote", "remote_eligible": True, "attendance_required": False})["remote_eligible"])


    def test_countries_use_stated_names_and_preserve_new_verified_destinations(self):
        self.assertEqual(classify({"location": "Online build; final in Tokyo, Japan"})["attendance_countries"], ["Japan"])
        self.assertEqual(classify({"location": "Worldwide; in person at ten European locations"})["attendance_countries"], [])
        self.assertEqual(classify({"location": "In person; destination not stated", "attendance_countries": ["Peru", "Chile", "Peru"]})["attendance_countries"], ["Chile", "Peru"])
        self.assertEqual(classify({"location": "Valencia + online"})["attendance_countries"], [])

    def test_countries_do_not_guess_from_cities_or_worldwide_eligibility(self):
        self.assertEqual(classify({"location": "Worldwide remote; organizer based in Japan"})["attendance_countries"], [])
        self.assertEqual(classify({"location": "In person in an unnamed city"})["attendance_countries"], [])


class TrustCatalogTests(unittest.TestCase):
    def test_cli_reads_explicit_external_inputs_without_changing_registry(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            registry = root / "private-history.json"
            registry.write_text(json.dumps({"posted": [{"identity": "build", "name": "Build", "organizer": "Example", "url": "https://example.org"}]}))
            original_registry = registry.read_bytes()
            batches = root / "batches"
            batches.mkdir()
            (batches / "candidate.json").write_text(json.dumps({"opportunities": [{"identity": "build", "location": "In person in Japan", "reward": "$100"}, {"identity": "unaccepted", "name": "Not accepted"}]}))
            report = root / "report-2026-09-28.md"
            report.write_text("## Open now\n\n| Build | Hackathon | Oct 1 | Oct 1 | Oct 2 | Solo | In person in Japan | $100 | Link |\n")
            output = root / "public" / "opportunities.json"
            with mock.patch.object(sys, "argv", ["sync", "--report", str(report), "--registry", str(registry), "--batches-dir", str(batches), "--output", str(output)]), redirect_stdout(io.StringIO()):
                sync_catalog.main()
            data = json.loads(output.read_text())
            self.assertEqual([entry["identity"] for entry in data["entries"]], ["build"])
            self.assertEqual(data["entries"][0]["attendance_countries"], ["Japan"])
            self.assertEqual(data["entries"][0]["status"], "open")
            self.assertEqual(registry.read_bytes(), original_registry)

    def test_sync_writes_equivalent_json_and_local_openable_script(self):
        catalog = {"entries": [{"name": "Builder Prize"}], "trust_concerns": [],
                   "summary": {"total": 1}}
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "opportunities.json"
            with mock.patch.object(sync_catalog, "build", return_value=catalog), \
                 mock.patch.object(sys, "argv", ["sync", "--report", "unused.md", "--output", str(output)]), \
                 redirect_stdout(io.StringIO()):
                sync_catalog.main()
            json_data = json.loads(output.read_text())
            script = output.with_suffix(".js").read_text()
            self.assertEqual(json_data, catalog)
            self.assertTrue(script.startswith("window.OPPORTUNITY_CATALOG = "))
            self.assertEqual(json.loads(script.removeprefix("window.OPPORTUNITY_CATALOG = ").removesuffix(";\n")), json_data)

    def test_accepted_concerns_are_listed_and_mark_matching_posted_entry(self):
        with tempfile.TemporaryDirectory() as directory:
            directory = Path(directory)
            registry = directory / "posted_opportunities.json"
            registry.write_text(json.dumps({
                "posted": [{"identity": "builder-prize", "name": "Builder Prize 2026",
                            "organizer": "Example Org", "url": "https://example.org/prize"}],
                "trust_concerns_posted": [
                    {"identity": "renamed-prize", "name": "Builder Prize", "organizer": "Example Org",
                     "reason": "Official organizer denial", "evidence_url": "https://example.org/denial",
                     "discord_message_id": "private-message-id"},
                    {"identity": "unposted", "name": "Unposted Warning", "organizer": "Other Org",
                     "reason": "Official organizer denial", "evidence_url": "https://other.org/denial"},
                ],
            }))
            report = directory / "report-2026-09-23.md"
            report.write_text("## Open now\n\n## Rolling or no-deadline grants\n")
            with mock.patch.object(sync_catalog, "REGISTRY", registry), \
                 mock.patch.object(sync_catalog, "POSTER_DIR", directory):
                result = sync_catalog.build(report)
            self.assertEqual(len(result["entries"]), 1)
            self.assertEqual(result["entries"][0]["trust_status"], "concern")
            self.assertEqual(result["entries"][0]["trust_reason"], "Official organizer denial")
            self.assertEqual(len(result["trust_concerns"]), 2)
            self.assertNotIn("discord_message_id", result["trust_concerns"][0])


if __name__ == "__main__":
    unittest.main()
