"""Tests for the Desk actions catalog, profiles, and lookup CLI."""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest

REPOSITORY = Path(__file__).resolve().parents[1]
CATALOG_PATH = REPOSITORY / "references" / "actions.jsonl"
PROFILES_PATH = REPOSITORY / "references" / "profiles.json"
LOOKUP_SCRIPT = REPOSITORY / "scripts" / "lookup_actions.py"

sys.path.insert(0, str(REPOSITORY / "scripts"))
import lookup_actions  # noqa: E402
import import_actions  # noqa: E402


class ActionsCatalogAndLookupTests(unittest.TestCase):
    def test_catalog_file_is_valid_jsonl(self):
        self.assertTrue(CATALOG_PATH.exists(), f"missing {CATALOG_PATH}")
        lines = [
            line.strip()
            for line in CATALOG_PATH.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        self.assertGreaterEqual(len(lines), 618)
        keys = set()
        for idx, line in enumerate(lines, start=1):
            data = json.loads(line)
            for required in ("key", "name", "summary", "description"):
                self.assertIn(required, data)
                self.assertTrue(str(data[required]).strip())
            self.assertNotIn(data["key"], keys, f"duplicate key {data['key']} at line {idx}")
            keys.add(data["key"])

    def test_profiles_file_is_valid_and_consistent(self):
        self.assertTrue(PROFILES_PATH.exists(), f"missing {PROFILES_PATH}")
        data = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
        self.assertEqual(data.get("version"), 1)
        self.assertEqual(data.get("service"), "desk")
        self.assertIn("profiles", data)
        self.assertIn("tasks", data)

        result = subprocess.run(
            [sys.executable, str(LOOKUP_SCRIPT), "--validate"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(
            result.returncode, 0, f"validation failed:\n{result.stdout}\n{result.stderr}"
        )
        self.assertIn("Validation OK", result.stdout)

    def test_lookup_cli_profiles_listing(self):
        result = subprocess.run(
            [sys.executable, str(LOOKUP_SCRIPT), "--profiles"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("ticket-agent", result.stdout)
        self.assertIn("desk-admin", result.stdout)

    def test_lookup_cli_task_inspection(self):
        result = subprocess.run(
            [sys.executable, str(LOOKUP_SCRIPT), "--task", "ticket-reply-and-draft"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("sendReply", result.stdout)
        self.assertIn("draftsReply", result.stdout)

    def test_lookup_cli_search_names_only(self):
        result = subprocess.run(
            [sys.executable, str(LOOKUP_SCRIPT), "--search", "template", "--names-only"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("addTemplate", result.stdout)

    def test_lookup_cli_action_inspection(self):
        result = subprocess.run(
            [sys.executable, str(LOOKUP_SCRIPT), "--action", "sendReply", "--json"],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0)
        data = json.loads(result.stdout)
        self.assertEqual(data.get("key"), "sendReply")
        self.assertIn("email reply", data.get("description", ""))

    def test_ticket_agent_profile_allows_reply_but_not_admin(self):
        data = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
        profiles = data["profiles"]
        agent_actions = lookup_actions.resolve_profile_actions("ticket-agent", profiles)
        self.assertIn("sendReply", agent_actions)
        self.assertIn("draftsReply", agent_actions)
        self.assertIn("createTicketComment", agent_actions)
        self.assertIn("updateTicket", agent_actions)
        self.assertNotIn("addTemplate", agent_actions)
        self.assertNotIn("updateDepartment", agent_actions)
        self.assertNotIn("createField", agent_actions)

    def test_desk_admin_inherits_agent_and_adds_settings(self):
        data = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
        profiles = data["profiles"]
        admin_actions = lookup_actions.resolve_profile_actions("desk-admin", profiles)
        self.assertIn("sendReply", admin_actions)
        self.assertIn("addTemplate", admin_actions)
        self.assertIn("updateTemplate", admin_actions)
        self.assertIn("updateDepartment", admin_actions)
        self.assertIn("createField", admin_actions)
        self.assertIn("updateLayout", admin_actions)

    def test_desk_admin_denies_destructive_actions(self):
        data = json.loads(PROFILES_PATH.read_text(encoding="utf-8"))
        profiles = data["profiles"]
        admin_actions = lookup_actions.resolve_profile_actions("desk-admin", profiles)
        for denied in (
            "deleteTicket",
            "emptySpamTickets",
            "deleteAllSpamTickets",
            "sarExportAll",
            "moveToTrash",
        ):
            self.assertNotIn(denied, admin_actions)

    def test_importer_parses_dump_and_handles_variants(self):
        sample_dump = (
            "Authorize On Demand\n"
            "Group view\n"
            "All Tools\n"
            "Tools Name\n"
            "sendReply This API sends an email reply.\n"
        )
        parsed = import_actions.parse_dump(sample_dump)
        keys = {entry["key"]: entry for entry in parsed}
        self.assertIn("sendReply", keys)
        self.assertEqual(keys["sendReply"]["name"], "sendReply")

    def test_importer_merges_additions_and_marks_removals(self):
        known = {
            "oldAction": {
                "key": "oldAction",
                "name": "oldAction",
                "summary": "Old",
                "description": "Old action",
                "added": "2026-08-01",
            }
        }
        current_entries = [
            {
                "key": "newAction",
                "name": "newAction",
                "summary": "New",
                "description": "New action",
            }
        ]
        merged = import_actions.merge(current_entries, known, today="2026-09-18")
        by_key = {item["key"]: item for item in merged}
        self.assertEqual(by_key["newAction"]["added"], "2026-09-18")
        self.assertNotIn("removed", by_key["newAction"])
        self.assertEqual(by_key["oldAction"]["removed"], "2026-09-18")


if __name__ == "__main__":
    unittest.main()
