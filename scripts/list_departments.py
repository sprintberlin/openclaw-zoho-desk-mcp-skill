#!/usr/bin/env python3
"""List Zoho Desk departments through mcporter."""

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
    ("ID", ["id", "departmentId"]),
    ("Name", ["name", "nameInCustomerPortal", "displayName"]),
    ("Description", ["description"]),
    ("Enabled", ["isEnabled", "enabled"]),
]


def build_parser():
    parser = build_base_parser("List Zoho Desk departments.")
    parser.add_argument("--limit", type=positive_int, help="return at most this many departments")
    parser.add_argument("--page-size", type=positive_int, default=50, help="page size (default: 50)")
    parser.add_argument("--full", action="store_true", help="with --json, print complete records")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    ENDPOINT.configure(args)

    result = paginate(
        "getDepartments",
        {},
        page_size=args.page_size,
        max_records=args.limit,
        timeout=args.timeout,
    )
    records = rows(result) if "error" not in result else []
    if args.json and not args.full:
        records = [
            {
                "id": field(row, ["id", "departmentId"], ""),
                "name": field(row, ["name", "displayName"], ""),
                "isEnabled": field(row, ["isEnabled", "enabled"], ""),
            }
            for row in records
        ]
    return finish(result, records, args, COLUMNS, empty="No departments found.")


if __name__ == "__main__":
    sys.exit(main())
