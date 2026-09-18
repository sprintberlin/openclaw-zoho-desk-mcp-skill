# Zoho Desk MCP Action Profiles & Task Recipes

This document provides human-readable guidance on the least-privilege profiles and task recipes configured in this skill.

The machine-readable source of truth is [`references/profiles.json`](profiles.json), validated against [`references/actions.jsonl`](actions.jsonl). Use the bundled CLI `scripts/lookup_actions.py` for automated inspection, token-efficient queries, and copy-ready lists.

## Role Profiles Overview

Start with the smallest role profile that covers the user or agent's responsibilities.

```bash
# List all role profiles
python3 scripts/lookup_actions.py --profiles

# Inspect actions in a profile (including inherited actions)
python3 scripts/lookup_actions.py --profile ticket-agent
python3 scripts/lookup_actions.py --profile desk-admin

# Get copy-ready action names only (one per line)
python3 scripts/lookup_actions.py --profile ticket-agent --names-only
python3 scripts/lookup_actions.py --profile desk-admin --names-only
```

### 1. Desk Ticket Agent (`ticket-agent`)
- **Focus:** Daily frontline support operations.
- **Allowed:** Search and view tickets, threads, comments, contacts, and accounts; draft and send customer email replies (`draftsReply`, `sendReply`, `sendForReview`); add internal comments with mentions (`createTicketComment`); log work time (`createTicketTimeEntry`); update status, priority, and ticket fields (`updateTicket`, `closeTickets`, `moveTicket`); associate tags; execute blueprint transitions (`performBlueprintTransition`).
- **Excluded:** Any helpdesk settings, department alterations, custom fields, email templates, workflows, SLAs, and permanent deletions.

### 2. Desk Administrator (`desk-admin`)
- **Inherits:** `ticket-agent`.
- **Focus:** Complete operational and administrative control over Zoho Desk configuration.
- **Allowed:** Everything in `ticket-agent` plus email templates (`addTemplate`, `updateTemplate`), ticket templates, departments (`addDepartment`, `updateDepartment`), custom fields and layouts (`createField`, `updateLayout`), business hours, holiday lists, skill routing, blueprint authoring, and knowledge base root categories and articles.
- **Explicitly Denied (Safety):** Permanent spam emptying (`deleteAllSpamTickets`, `emptySpamTickets`), bulk trash purges, Subject Access Request permanent data export/purge (`sarExport`, `sarExportAll`), and unconfirmed agent anonymization.

## Task Recipes Overview

Task recipes answer the question: *"Which specific Actions do I need to unlock on the MCP server to solve this exact job?"*

```bash
# List all configured task recipes
python3 scripts/lookup_actions.py --tasks

# Inspect a specific task recipe
python3 scripts/lookup_actions.py --task ticket-reply-and-draft

# Copy-ready action names for Zoho MCP setup UI
python3 scripts/lookup_actions.py --task ticket-reply-and-draft --names-only
```

Available recipes:
- `ticket-lookup-and-search`: Find tickets by number, contact, account, or tag; inspect full thread conversations and metrics.
- `ticket-reply-and-draft`: Draft and send email responses to customers with templates and placeholders.
- `ticket-triage-and-resolution`: Update ticket properties, status, department, and close tickets.
- `ticket-internal-notes-and-time`: Add internal notes and log billing time entries on tickets.
- `ticket-blueprint-transition`: Inspect and execute compliant blueprint transitions on tickets.
- `template-management`: Manage email templates, ticket templates, folders, and placeholders.
- `department-and-routing-setup`: Manage departments, From addresses, business hours, and skill-based assignment.
- `fields-and-layouts`: Inspect and configure layouts, custom fields, and dependency mappings.
- `knowledge-base-management`: Author and maintain knowledge base categories, sections, and articles.

## Format and Philosophy

See [`references/CATALOG_FORMAT.md`](CATALOG_FORMAT.md) for full documentation on why and how the catalog format is standardized on JSONL + JSON across the SprintCX Zoho MCP skills.
