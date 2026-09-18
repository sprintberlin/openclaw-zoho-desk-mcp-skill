# Zoho Desk MCP

Connect your agent to Zoho Desk through the Model Context Protocol (MCP). This skill provides everything you need to look up tickets, inspect conversations, draft and send replies, list contacts and departments, and manage templates using `mcporter`.

This repository contains the public source for the ClawHub skill [`@sprintcx/zoho-desk-mcp`](https://clawhub.ai/sprintcx/skills/zoho-desk-mcp).

## What This Skill Includes

- Agent Skill instructions in `SKILL.md` (portable SKILL.md format)
- ClawHub release card metadata in `skill-card.md`
- Ready-to-use Python helpers for tickets, contacts, departments, and templates
- A JSON Action catalog with two least-privilege profiles: **ticket-agent** and **desk-admin**
- Security-conscious `mcporter` calls through `subprocess.run([...])` without shell expansion

## Requirements

| Requirement | Details |
|---|---|
| Zoho Desk MCP Server | A configured endpoint from [mcp.zoho.eu](https://mcp.zoho.eu) |
| mcporter | MCP client CLI (bundled with OpenClaw; elsewhere `npm i -g mcporter`) |
| Endpoint selection | `ZOHO_DESK_MCP_URL` for one account; named profiles or `--mcp-url` for multiple accounts |

### Single-account setup

For the common single-account case, set `ZOHO_DESK_MCP_URL`. The helper scripts also support named profiles and one-off URL overrides.

Add this to your shell profile, for example `~/.bashrc` or `~/.zshrc`:

```bash
export ZOHO_DESK_MCP_URL="https://your-org-zoho-desk-xxxxx.zohomcp.eu/mcp/YOUR_TOKEN/message"
```

Or set it per session:

```bash
ZOHO_DESK_MCP_URL="https://your-org-zoho-desk-xxxxx.zohomcp.eu/mcp/YOUR_TOKEN/message" python3 scripts/list_tickets.py
```

To verify that it is set without printing the credential:

```bash
if [ -n "$ZOHO_DESK_MCP_URL" ]; then echo "ZOHO_DESK_MCP_URL is set"; else echo "ZOHO_DESK_MCP_URL is not set"; fi
```

Treat `ZOHO_DESK_MCP_URL` like a password. It contains Desk access credentials.

## How to Get Your MCP URL

1. Go to [mcp.zoho.eu](https://mcp.zoho.eu) and sign in with your Zoho account.
2. Click **Add Connection** or **New Connection**.
3. Select **Zoho Desk** from the list of available apps.
4. Choose the data center matching your Zoho account: EU, US, IN, AU, JP, or CN.
5. Grant the requested OAuth scopes. Enable only the Actions from the profile you intend to use.
6. After authorization, copy the generated MCP endpoint URL. It looks like:

   ```text
   https://your-org-zoho-desk-xxxxx.zohomcp.eu/mcp/abc123def456/message
   ```

7. Set it as `ZOHO_DESK_MCP_URL`.

### Multiple organizations and customer accounts

Use one shared profile file instead of changing global environment variables:

```json
{
  "version": 1,
  "profiles": {
    "acme": {
      "services": {
        "desk": {"env": "ACME_DESK_MCP_URL"}
      }
    }
  }
}
```

```bash
python3 scripts/list_tickets.py --profile acme
```

The default file is `~/.config/zoho-mcp/profiles.json`. Endpoint resolution is `--mcp-url`, selected profile, then the app environment variable. Prefer profile entries using `env` or `url_file`; direct URLs in JSON are supported but make the file credential-bearing. Full format: [`references/MULTI_ACCOUNT.md`](references/MULTI_ACCOUNT.md).

## Quick Start

### List available tools on your MCP server

```bash
mcporter list $ZOHO_DESK_MCP_URL
```

### Look up tickets

```bash
cat << 'EOF' > /tmp/desk_tickets.json
{
  "query_params": {"from": 1, "limit": 20}
}
EOF
mcporter call "$ZOHO_DESK_MCP_URL.ZohoDesk_getTickets" --args "$(< /tmp/desk_tickets.json)"
```

### Inspect one ticket

```bash
cat << 'EOF' > /tmp/desk_ticket.json
{
  "path_variables": {"id": "123456789"}
}
EOF
mcporter call "$ZOHO_DESK_MCP_URL.ZohoDesk_getTicket" --args "$(< /tmp/desk_ticket.json)"
```

## Python Scripts

Ready-to-use scripts for common Desk operations. They accept `--profile`, `--profiles-file`, and `--mcp-url`, with `ZOHO_DESK_MCP_URL` as the single-account fallback.

The bundled Python scripts call `mcporter` directly through `subprocess.run([...])` and do not invoke a shell. This avoids shell expansion of the credential-bearing `ZOHO_DESK_MCP_URL`.

### `list_tickets.py`

```bash
python3 scripts/list_tickets.py
python3 scripts/list_tickets.py --search "login issue"
python3 scripts/list_tickets.py --search "login issue" --json --limit 20
```

### `inspect_ticket.py`

```bash
python3 scripts/inspect_ticket.py 123456789
python3 scripts/inspect_ticket.py 123456789 --conversations --json
```

### `list_contacts.py`

```bash
python3 scripts/list_contacts.py --search "Miller"
python3 scripts/list_contacts.py --search "Miller" --json --limit 20
```

### `list_departments.py`

```bash
python3 scripts/list_departments.py
python3 scripts/list_departments.py --json
```

### `list_templates.py`

```bash
python3 scripts/list_templates.py --department-id 987654321
python3 scripts/list_templates.py --department-id 987654321 --json
```

## Desk Action Catalog and Profiles

Zoho Desk exposes 618 MCP Actions, but a single Zoho MCP server accepts at most **300 selected Actions**. Enabling everything is therefore impossible, and enabling too much also gives a normal agent unnecessary access to helpdesk settings, layout changes, and destructive deletes while inflating the per-session tool catalog.

Both profiles in this skill are sized to fit one MCP server:

| Profile | Actions | Fits the 300 limit |
|---|---|---|
| `ticket-agent` | 180 | yes |
| `desk-admin` (inherits `ticket-agent`) | 284 | yes |

The catalog is JSON, not prose, so an agent can answer "which Actions do I need for this task" without reading thousands of lines:

- [`references/actions.jsonl`](references/actions.jsonl) is the complete catalog, one JSON object per Action, with the description Zoho itself delivers.
- [`references/profiles.json`](references/profiles.json) holds the role profiles and the per-task Action recipes.
- [`references/CATALOG_FORMAT.md`](references/CATALOG_FORMAT.md) documents the format and how to refresh it after a Zoho catalog change.
- [`references/ACTION_PROFILES.md`](references/ACTION_PROFILES.md) is a short human-readable overview of the configured profiles and tasks.
- [`references/COMMON_WORKFLOWS.md`](references/COMMON_WORKFLOWS.md) contains verified step-by-step procedures.

Query it with the bundled CLI:

```bash
# Which role profiles and task recipes exist
python3 scripts/lookup_actions.py --profiles
python3 scripts/lookup_actions.py --tasks

# Which Actions does a role need, inheritance resolved
python3 scripts/lookup_actions.py --profile ticket-agent
python3 scripts/lookup_actions.py --profile desk-admin

# Which Actions does one concrete job need, copy-ready for the Zoho setup UI
python3 scripts/lookup_actions.py --task ticket-reply-and-draft --names-only

# Find an Action, or read its full Zoho description
python3 scripts/lookup_actions.py --search "template"
python3 scripts/lookup_actions.py --action sendReply

# Check that profiles and tasks still match the catalog
python3 scripts/lookup_actions.py --validate
```

There is no read-only profile. The two roles this skill ships are:

1. **Desk Ticket Agent** (`ticket-agent`, 180 Actions): daily support work. Look up tickets and conversations, draft and send replies, add internal comments, log time, triage, tag, manage followers, execute blueprint transitions, and search contacts, accounts, and knowledge base articles. Field, layout, department, and agent metadata is included read-only so writes use correct IDs and API names. No template, department, field, or settings changes. Community forum, IM sessions, calls, events, contracts, and KB translation management are deliberately excluded to stay within the 300-Action limit.
2. **Desk Administrator** (`desk-admin`, 284 Actions resolved): inherits `ticket-agent` and adds 104 administrative Actions covering templates, departments and From addresses, layouts, custom fields, business hours, holiday lists, skills, routing, blueprint authoring, agents and teams, and knowledge base administration. All deletes, permanent spam empties, bulk purges, and SAR data export stay denied.

When a specific job needs an Action outside these profiles, add it from a task recipe instead of enabling a whole module:

```bash
python3 scripts/lookup_actions.py --task template-management --names-only
```

After configuring the connection at [mcp.zoho.eu](https://mcp.zoho.eu), verify the actual result rather than trusting the profile document:

```bash
mcporter list "$ZOHO_DESK_MCP_URL"
```

The profile and catalog use the Action names shown in the Zoho MCP setup UI. Runtime tool names normally add the `ZohoDesk_` prefix.

## Token Optimization (Large MCP Catalogs)

Connecting large MCP servers to OpenClaw can cost a large number of input tokens per session if all tool schemas are loaded eagerly up front.

To avoid loading schemas on session start, enable OpenClaw's built-in Tool Search in `~/.openclaw/openclaw.json`:

```json5
{
  tools: {
    toolSearch: {
      mode: "directory"
    }
  }
}
```

## Troubleshooting

### No endpoint configured

Set `ZOHO_DESK_MCP_URL`, use `--profile`, or pass `--mcp-url`. For profile errors, verify the selected name, `--profiles-file`, and the `services.desk` entry. See [Multi-account profiles](references/MULTI_ACCOUNT.md).

### `Invalid oauth scope to access this URL`

The MCP connection token may have expired or may not include the required scope. Go to [mcp.zoho.eu](https://mcp.zoho.eu), revoke and reconnect the affected app to get a fresh token.

### From address rejected

`sendReply` and `draftsReply` require a From address that is already configured in the help desk portal. Resolve it with `getReplyMailAddresses` before sending.

## Repository Files

- `SKILL.md`: Agent Skill instructions.
- `CONTRIBUTING.md`: Issue and pull request workflows for humans and agents.
- `references/actions.jsonl`: Complete Action catalog, one JSON object per Action.
- `references/profiles.json`: Role profiles and per-task Action recipes.
- `references/CATALOG_FORMAT.md`: Catalog format, record shape, and refresh procedure.
- `references/ACTION_PROFILES.md`: Human-readable overview of profiles and task recipes.
- `references/COMMON_WORKFLOWS.md`: Verified workflows for frequent Desk tasks.
- `references/MULTI_ACCOUNT.md`: Portable single-account and multi-account endpoint profiles.
- `skill-card.md`: ClawHub release card metadata.
- `scripts/lookup_actions.py`: Query Actions, profiles, and task recipes; validate them.
- `scripts/import_actions.py`: Rebuild the catalog from a Zoho MCP setup UI dump.
- `scripts/list_tickets.py`: List or search Zoho Desk tickets.
- `scripts/inspect_ticket.py`: Inspect one ticket and optionally its conversations.
- `scripts/list_contacts.py`: List or search Desk contacts.
- `scripts/list_departments.py`: List Desk departments.
- `scripts/list_templates.py`: List email templates for a department.
- `scripts/desk_client.py`: Shared MCP caller, pagination, and table helpers.
- `scripts/mcp_endpoint.py`: Shared endpoint and profile resolver.
- `tests/test_endpoint_resolution.py`: Credential-free resolver tests.
- `tests/test_actions_lookup.py`: Catalog, profile, and lookup CLI tests.
- `tests/test_desk_helpers.py`: CLI parser and client helper tests.

## Security Notes

The repository version calls `mcporter` directly through `subprocess.run([...])` without shell expansion.

Zoho Desk contains customer support data. Load only required records and never copy contents into chats, logs, or repositories.

## Publish

Publish under the SprintCX ClawHub organization:

```bash
clawhub skill publish . \
  --slug zoho-desk-mcp \
  --name "Zoho Desk MCP" \
  --owner sprintcx \
  --version 1.0.0 \
  --source-repo sprintberlin/openclaw-zoho-desk-mcp-skill \
  --source-ref main \
  --source-path . \
  --changelog "Initial public Desk MCP skill with JSON action catalog, ticket-agent and desk-admin profiles, and helper CLIs"
```
