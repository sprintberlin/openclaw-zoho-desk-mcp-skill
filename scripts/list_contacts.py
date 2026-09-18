#!/usr/bin/env python3
"""List or search Zoho Desk contacts through mcporter."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from desk_client import (  # noqa: E402
    ENDPOINT,
    build_base_parser,
    field,
    finish,
    paginate,
    positive_int,
    rows,
)

COLUMNS = [
    ("ID", ["id", "contactId"]),
    ("Name", ["lastName", "fullName", "firstName", "name"]),
    ("Email", ["email", "emailId"]),
    ("Phone", ["phone", "mobile", "phoneNumber"]),
    ("Account", ["account", "accountId", "accountName"]),
]


def build_parser():
    parser = build_base_parser("List or search Zoho Desk contacts.")
    parser.add_argument("--search", metavar="TEXT", help="search contacts by name, email, or phone")
    parser.add_argument("--limit", type=positive_int, help="return at most this many contacts")
    parser.add_argument("--page-size", type=positive_int, default=50, help="page size (default: 50)")
    parser.add_argument("--full", action="store_true", help="with --json, print complete records")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    ENDPOINT.configure(args)

    params = {}
    tool = "searchContacts" if args.search else "getContacts"
    if args.search:
        params["searchStr"] = args.search

    result = paginate(
        tool,
        params,
        page_size=args.page_size,
        max_records=args.limit,
        timeout=args.timeout,
    )
    records = rows(result) if "error" not in result else []
    if args.json and not args.full:
        records = [
            {
                "id": field(row, ["id", "contactId"], ""),
                "name": field(row, ["lastName", "fullName", "firstName", "name"], ""),
                "email": field(row, ["email", "emailId"], ""),
                "phone": field(row, ["phone", "mobile"], ""),
            }
            for row in records
        ]
    return finish(result, records, args, COLUMNS, empty="No contacts found.")


if __name__ == "__main__":
    sys.exit(main())
