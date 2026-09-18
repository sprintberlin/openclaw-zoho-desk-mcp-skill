#!/usr/bin/env python3
"""List Zoho Desk email templates through mcporter."""

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
    ("ID", ["id", "templateId"]),
    ("Name", ["name", "templateName"]),
    ("Folder", ["folder", "folderId", "folderName"]),
    ("Department", ["department", "departmentId"]),
]


def build_parser():
    parser = build_base_parser("List Zoho Desk email templates.")
    parser.add_argument("--department-id", metavar="ID", required=True, help="department ID (required by Desk)")
    parser.add_argument("--limit", type=positive_int, help="return at most this many templates")
    parser.add_argument("--page-size", type=positive_int, default=50, help="page size (default: 50)")
    parser.add_argument("--full", action="store_true", help="with --json, print complete records")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    ENDPOINT.configure(args)

    result = paginate(
        "getTemplates",
        {"departmentId": args.department_id},
        page_size=args.page_size,
        max_records=args.limit,
        timeout=args.timeout,
    )
    records = rows(result) if "error" not in result else []
    if args.json and not args.full:
        records = [
            {
                "id": field(row, ["id", "templateId"], ""),
                "name": field(row, ["name", "templateName"], ""),
                "folder": field(row, ["folder", "folderName"], ""),
            }
            for row in records
        ]
    return finish(result, records, args, COLUMNS, empty="No templates found.")


if __name__ == "__main__":
    sys.exit(main())
