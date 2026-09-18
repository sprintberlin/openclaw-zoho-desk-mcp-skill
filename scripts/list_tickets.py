#!/usr/bin/env python3
"""List or search Zoho Desk tickets through mcporter."""

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
    ("ID", ["id", "ticketId"]),
    ("Number", ["ticketNumber", "number"]),
    ("Subject", ["subject", "title"]),
    ("Status", ["status", "statusType"]),
    ("Priority", ["priority"]),
    ("Contact", ["contact", "contactId", "email"]),
    ("Department", ["department", "departmentId"]),
]


def build_parser():
    parser = build_base_parser("List or search Zoho Desk tickets.")
    parser.add_argument("--search", metavar="TEXT", help="search tickets by subject, number, or email")
    parser.add_argument("--department-id", metavar="ID", help="restrict results to one department")
    parser.add_argument("--limit", type=positive_int, help="return at most this many tickets")
    parser.add_argument("--page-size", type=positive_int, default=50, help="page size (default: 50)")
    parser.add_argument("--full", action="store_true", help="with --json, print complete records")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    ENDPOINT.configure(args)

    params = {}
    if args.department_id:
        params["departmentId"] = args.department_id

    if args.search:
        params["searchStr"] = args.search
        result = paginate(
            "searchTickets",
            params,
            page_size=args.page_size,
            max_records=args.limit,
            timeout=args.timeout,
        )
    else:
        result = paginate(
            "getTickets",
            params,
            page_size=args.page_size,
            max_records=args.limit,
            timeout=args.timeout,
        )

    records = rows(result) if "error" not in result else []
    if args.json and args.full:
        args.json = True
        return finish(result, records, args, COLUMNS, empty="No tickets found.")

    if args.json and not args.full:
        simplified = [
            {
                "id": field(row, ["id", "ticketId"], ""),
                "ticketNumber": field(row, ["ticketNumber", "number"], ""),
                "subject": field(row, ["subject", "title"], ""),
                "status": field(row, ["status", "statusType"], ""),
                "priority": field(row, ["priority"], ""),
            }
            for row in records
        ]
        return finish(result, simplified, args, COLUMNS, empty="No tickets found.")

    return finish(result, records, args, COLUMNS, empty="No tickets found.")


if __name__ == "__main__":
    sys.exit(main())
