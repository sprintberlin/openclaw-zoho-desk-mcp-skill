"""Credential-free tests for Desk helper CLIs and shared client helpers."""

from __future__ import annotations

import json
from pathlib import Path
import sys
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import desk_client  # noqa: E402
import inspect_ticket  # noqa: E402
import list_contacts  # noqa: E402
import list_departments  # noqa: E402
import list_templates  # noqa: E402
import list_tickets  # noqa: E402


class DeskClientHelperTests(unittest.TestCase):
    def test_rows_unwraps_nested_data_lists(self):
        result = {"data": {"data": [{"id": "1"}, {"id": "2"}]}}
        self.assertEqual(desk_client.rows(result), [{"id": "1"}, {"id": "2"}])

    def test_rows_returns_empty_on_error(self):
        self.assertEqual(desk_client.rows({"error": "boom"}), [])

    def test_field_reads_nested_name(self):
        record = {"contact": {"name": "Ada Lovelace", "id": "9"}}
        self.assertEqual(desk_client.field(record, ["contact"]), "Ada Lovelace")

    def test_positive_int_rejects_zero(self):
        with self.assertRaises(Exception):
            desk_client.positive_int("0")


class HelperParserTests(unittest.TestCase):
    def test_list_tickets_help_exits_zero(self):
        with self.assertRaises(SystemExit) as ctx:
            list_tickets.build_parser().parse_args(["--help"])
        self.assertEqual(ctx.exception.code, 0)

    def test_list_tickets_unknown_option_exits_two(self):
        with self.assertRaises(SystemExit) as ctx:
            list_tickets.build_parser().parse_args(["--not-a-real-flag"])
        self.assertEqual(ctx.exception.code, 2)

    def test_inspect_ticket_requires_id(self):
        with self.assertRaises(SystemExit) as ctx:
            inspect_ticket.build_parser().parse_args([])
        self.assertEqual(ctx.exception.code, 2)

    def test_list_templates_requires_department(self):
        with self.assertRaises(SystemExit) as ctx:
            list_templates.build_parser().parse_args([])
        self.assertEqual(ctx.exception.code, 2)

    def test_list_contacts_and_departments_help(self):
        with self.assertRaises(SystemExit) as contacts:
            list_contacts.build_parser().parse_args(["--help"])
        with self.assertRaises(SystemExit) as departments:
            list_departments.build_parser().parse_args(["--help"])
        self.assertEqual(contacts.exception.code, 0)
        self.assertEqual(departments.exception.code, 0)

    def test_list_tickets_without_endpoint_exits_one(self):
        with mock.patch.object(list_tickets.ENDPOINT, "configure"):
            with mock.patch.object(
                list_tickets,
                "paginate",
                return_value={"error": "no Zoho Desk MCP endpoint configured"},
            ):
                code = list_tickets.main(["--search", "login"])
        self.assertEqual(code, 1)


if __name__ == "__main__":
    unittest.main()
