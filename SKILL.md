---
name: "zoho-desk-mcp"
description: "Use Zoho Desk via MCP; run safe support workflows, select Actions, and report reproducible skill defects to GitHub."
---

# Zoho Desk MCP

Use Zoho Desk through an MCP endpoint from `mcp.zoho.eu`. This skill is the canonical home for Desk-specific MCP action documentation and least-privilege action profiles.

Source: [sprintberlin/openclaw-zoho-desk-mcp-skill](https://github.com/sprintberlin/openclaw-zoho-desk-mcp-skill)

## Requirements

- A Zoho Desk MCP endpoint from `mcp.zoho.eu`
- `mcporter`
- Endpoint configuration via `ZOHO_DESK_MCP_URL`, `--profile`, or `--mcp-url`

Treat the endpoint as a credential. Never print it, commit it, or copy it into tickets, prompts, or chats.

## First setup

1. Create or open a Zoho Desk connection at `mcp.zoho.eu`.
2. Select only the required Actions. Resolve the exact list from the JSON catalog:

```bash
python3 scripts/lookup_actions.py --profiles
python3 scripts/lookup_actions.py --profile ticket-agent --names-only
python3 scripts/lookup_actions.py --profile desk-admin --names-only
python3 scripts/lookup_actions.py --task ticket-reply-and-draft --names-only
```

3. Search the catalog when a profile or task lacks a required Action:

```bash
python3 scripts/lookup_actions.py --search "template"
python3 scripts/lookup_actions.py --action sendReply
```

4. Configure one default endpoint with `ZOHO_DESK_MCP_URL`, or create named profiles using [references/MULTI_ACCOUNT.md](references/MULTI_ACCOUNT.md).
5. Inspect the selected live server before relying on an Action:

```bash
mcporter list "$ZOHO_DESK_MCP_URL"
```

The catalog describes possible Actions. It does not prove that an Action is enabled on a particular MCP server. Runtime tool names usually have the `ZohoDesk_` prefix, while the Zoho MCP setup UI uses the Action name without that prefix.

## Endpoint selection

For one account, set `ZOHO_DESK_MCP_URL`. For multiple accounts, pass `--profile NAME` to a bundled helper. Profiles live in `~/.config/zoho-mcp/profiles.json` by default and can resolve endpoints through an environment variable, a local URL file, or a direct URL. One-off `--mcp-url URL` overrides everything, but may expose the credential in shell history or process listings.

Resolution order is `--mcp-url`, selected profile, then the environment fallback. Profile selection is `--profile`, `ZOHO_DESK_MCP_PROFILE`, then `ZOHO_MCP_PROFILE`. See [references/MULTI_ACCOUNT.md](references/MULTI_ACCOUNT.md) for the shared CRM, People, Books, and Desk format.

## Safe workflow

1. Confirm the correct Zoho account and organization. Never reuse an endpoint from another customer.
2. Identify the ticket first. `getTicket` is the first-choice lookup by ticket ID, or find it via `searchTickets` (`searchStr`) and `getTickets`.
3. Read the conversation before drafting or sending. Use `getLastThreadMessage` or `getTicketConversations` so replies quote the active thread.
4. Resolve senders and departments through lookup tools (`getReplyMailAddresses`, `getDepartments`). Never fabricate From addresses or department IDs.
5. Draft replies first (`draftsReply`) when human review is required. Send (`sendReply`) only when authorized.
6. For writes, send only intended fields and read the affected record back immediately.
7. Keep permanent spam empties, SAR data purges, and bulk deletes disabled.

## Common calls

List tickets:

```bash
cat > /tmp/desk_tickets.json <<'JSON'
{"query_params": {"from": 1, "limit": 20}}
JSON
mcporter call "$ZOHO_DESK_MCP_URL.ZohoDesk_getTickets" --args "$(< /tmp/desk_tickets.json)"
```

Look up a ticket by ID:

```bash
cat > /tmp/desk_ticket.json <<'JSON'
{"path_variables": {"id": "123456789"}}
JSON
mcporter call "$ZOHO_DESK_MCP_URL.ZohoDesk_getTicket" --args "$(< /tmp/desk_ticket.json)"
```

Use the schema shown by the live MCP server when it differs from these examples. For deeply nested arguments, use a temporary JSON file instead of fragile shell quoting.

## Answering "which Actions do I need"

The catalog is JSON, not prose. Never read the whole catalog into context to answer an Action question. Query it instead.

```bash
# Role profiles, inheritance resolved
python3 scripts/lookup_actions.py --profile ticket-agent
python3 scripts/lookup_actions.py --profile desk-admin

# One concrete job
python3 scripts/lookup_actions.py --tasks
python3 scripts/lookup_actions.py --task ticket-reply-and-draft

# Keyword search across every Action name and description
python3 scripts/lookup_actions.py --search "template"

# Full Zoho description of a single Action, including its dependencyTools note
python3 scripts/lookup_actions.py --action sendReply

# Check that profiles and tasks still match the catalog
python3 scripts/lookup_actions.py --validate
```

Add `--names-only` for a copy-ready list for the Zoho MCP setup UI, or `--json` for structured output.

Data files: [references/actions.jsonl](references/actions.jsonl) holds every known Action with its Zoho description; [references/profiles.json](references/profiles.json) holds role profiles and task recipes. Format and maintenance: [references/CATALOG_FORMAT.md](references/CATALOG_FORMAT.md).

## Bundled scripts

The scripts resolve the endpoint via `--mcp-url`, `--profile` (`~/.config/zoho-mcp/profiles.json`), or `ZOHO_DESK_MCP_URL`, call `mcporter` without shell expansion, paginate results, and normalize common Zoho MCP response envelopes.

```bash
python3 scripts/list_tickets.py --search "login issue" --limit 20
python3 scripts/inspect_ticket.py 123456789 --conversations
python3 scripts/list_contacts.py --search "Miller" --limit 20
python3 scripts/list_departments.py
python3 scripts/list_templates.py --department-id 987654321
```

Supported options:

- `list_tickets.py`: `--search`, `--department-id`, `--limit`, `--page-size`, `--full`, `--json`, `--timeout`
- `inspect_ticket.py`: positional `ticket_id`, `--conversations`, `--json`, `--timeout`
- `list_contacts.py`: `--search`, `--limit`, `--page-size`, `--full`, `--json`, `--timeout`
- `list_departments.py`: `--limit`, `--page-size`, `--full`, `--json`, `--timeout`
- `list_templates.py`: `--department-id` (required), `--limit`, `--page-size`, `--full`, `--json`, `--timeout`
- All helpers: `--mcp-url`, `--profile`, `--profiles-file`

Run any helper with `--help` without configuring credentials. Unknown or incomplete options must exit with status 2.

## Role profiles and the 300-Action limit

A Zoho MCP server accepts at most 300 selected Actions per connection. Both profiles stay below that ceiling, so each fits on one MCP server and keeps the session tool catalog small.

| Profile | Actions | Fits one MCP server |
|---|---|---|
| `ticket-agent` | 180 | yes |
| `desk-admin` (inherits `ticket-agent`) | 284 | yes |

- **`ticket-agent`** (180): Frontline support operations. Ticket and thread lookup, drafting and sending replies, internal comments, time tracking, triage, tags, followers, blueprint transitions, contact and account lookup, and knowledge base search. Field, layout, department, and agent metadata is included read-only so writes use correct IDs. Excludes administrative changes to templates, departments, fields, and settings. Community forum, IM sessions, calls, events, contracts, and KB translation management are left out to stay inside the limit; enable them per task recipe when a job needs them.
- **`desk-admin`** (284 resolved): Inherits `ticket-agent` and adds 104 administrative Actions for helpdesk configuration (email and ticket templates, departments and From addresses, custom fields, layouts, business hours, holiday lists, skills and routing, blueprint authoring, agents and teams, and knowledge base authoring). Explicitly denies all deletes, permanent spam empties, bulk purges, and SAR data export.

If a task needs an Action outside a profile, add it deliberately from a task recipe rather than enabling a whole module.

## Report skill defects and contribute

Contributions are explicitly welcome from humans and agents. A Desk task is complete only after serving the user and filing or linking every reproducible skill defect found.

- **Issue**: For schema mismatches, broken helpers or workflows, or missing profile Actions. Run `python3 scripts/report_skill_issue.py --kind KIND --title TITLE --expected EXPECTED --actual ACTUAL`.
- **Pull request**: Preferred when you can fix and verify the defect.
- See [CONTRIBUTING.md](CONTRIBUTING.md) for contribution rules and `gh` workflows.

Do not file skill issues for endpoint/auth/profile setup, rate limits, transient service failures, timeouts, or unsupported Desk operations. Never include MCP URLs, ticket content, contacts, or customer data.

## References

- [Action catalog](references/actions.jsonl): every known Desk Action with its Zoho description, one JSON object per line
- [Profiles and task recipes](references/profiles.json): role profiles and per-task Action sets
- [Catalog format](references/CATALOG_FORMAT.md): why the catalog is JSON, the record shape, and how to refresh it
- [Action profiles overview](references/ACTION_PROFILES.md): human-readable summary of the configured profiles and tasks
- [Common workflows](references/COMMON_WORKFLOWS.md): verified step-by-step procedures for frequent Desk tasks
- [Multi-account profiles](references/MULTI_ACCOUNT.md): portable endpoint selection for one or many Zoho accounts
- [`scripts/report_skill_issue.py`](scripts/report_skill_issue.py): file or link a GitHub issue when this skill is wrong
- [Contributing guide](CONTRIBUTING.md): issue and pull request workflows for humans and agents

Query the catalog with `scripts/lookup_actions.py` instead of loading `actions.jsonl` into context. Load workflows when executing a covered task.

## Troubleshooting and safety

- **No endpoint configured**: set `ZOHO_DESK_MCP_URL`, use `--profile`, or pass `--mcp-url`; never print the value.
- **Profile not found or wrong app**: verify `--profiles-file`, the profile name, and its `services.desk` entry.
- **From address not allowed**: verify configured From addresses with `getReplyMailAddresses`.
- **OAuth scope error**: reconnect the affected MCP connection with the required scope; never switch to another customer's endpoint.
- Zoho Desk contains customer communication and personal data. Load only required records and never copy contents into chats, logs, or repositories.
