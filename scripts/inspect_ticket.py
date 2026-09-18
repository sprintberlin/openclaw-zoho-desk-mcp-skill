#!/usr/bin/env python3
"""Inspect one Zoho Desk ticket by ID through mcporter."""

from __future__ import annotations

import json
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from desk_client import ENDPOINT, build_base_parser, call, field  # noqa: E402


def build_parser():
    parser = build_base_parser("Inspect one Zoho Desk ticket.")
    parser.add_argument("ticket_id", help="Desk ticket ID")
    parser.add_argument(
        "--conversations",
        action="store_true",
        help="also fetch threads and comments for the ticket",
    )
    return parser


def print_summary(ticket):
    print(f"Ticket:     {field(ticket, ['ticketNumber', 'number'])} ({field(ticket, ['id'])})")
    print(f"Subject:    {field(ticket, ['subject', 'title'])}")
    print(f"Status:     {field(ticket, ['status', 'statusType'])}")
    print(f"Priority:   {field(ticket, ['priority'])}")
    print(f"Department: {field(ticket, ['department', 'departmentId'])}")
    print(f"Assignee:   {field(ticket, ['assignee', 'assigneeId', 'agent'])}")
    print(f"Contact:    {field(ticket, ['contact', 'email', 'contactId'])}")
    print(f"Created:    {field(ticket, ['createdTime', 'createdDate'])}")
    print(f"Modified:   {field(ticket, ['modifiedTime', 'modifiedDate'])}")


def main(argv=None):
    args = build_parser().parse_args(argv)
    ENDPOINT.configure(args)

    result = call(
        "getTicket",
        {"path_variables": {"ticketId": args.ticket_id}},
        timeout=args.timeout,
    )
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        return 1

    ticket = result.get("data", result)
    if isinstance(ticket, dict) and isinstance(ticket.get("data"), dict):
        ticket = ticket["data"]

    payload = {"ticket": ticket}
    if args.conversations:
        conversations = call(
            "getTicketConversations",
            {"path_variables": {"ticketId": args.ticket_id}, "query_params": {"from": 1, "limit": 50}},
            timeout=args.timeout,
        )
        if "error" in conversations:
            print(f"Error: {conversations['error']}", file=sys.stderr)
            return 1
        payload["conversations"] = conversations.get("data", conversations)

    if args.json:
        print(json.dumps(payload, indent=2, ensure_ascii=False))
        return 0

    print_summary(ticket if isinstance(ticket, dict) else {})
    if args.conversations:
        items = payload.get("conversations")
        if isinstance(items, dict):
            items = items.get("data") or items.get("conversations") or []
        if not items:
            print("\nNo conversations found.")
        else:
            print(f"\n{len(items)} conversation item(s):")
            for item in items:
                kind = field(item, ["type", "channel", "direction"], "item")
                summary = field(item, ["content", "summary", "subject", "plainText"], "")
                if len(summary) > 120:
                    summary = summary[:117] + "..."
                print(f"  - {kind}: {summary}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
