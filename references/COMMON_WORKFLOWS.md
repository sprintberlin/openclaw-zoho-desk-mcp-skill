# Verified Zoho Desk MCP Workflows

Step-by-step procedures for frequent Desk tasks. All operations assume `mcporter` and a configured `ZOHO_DESK_MCP_URL`. Inspect the live tool schema with `mcporter list` before the first write.

## 1. Find a ticket and inspect its conversation

```text
searchTickets / getTickets -> getTicket -> getTicketConversations
```

1. Search with `searchTickets` (`searchStr` = ticket number, subject, or customer email) or list with `getTickets`.
2. Open the exact record with `getTicket` using the ticket ID, not a display number guessed from chat.
3. Load threads and comments with `getTicketConversations` or `getThreads` / `getTicketComments`.
4. For the latest inbound or outbound email, use `getLastThreadMessage`.

## 2. Reply to a customer

```text
getTicket -> getLastThreadMessage -> getReplyMailAddresses -> draftsReply / sendReply
```

1. Confirm the ticket ID, department, and current status.
2. Read the latest thread so the reply quotes the right conversation.
3. Resolve a configured From address with `getReplyMailAddresses`. Never invent a sender.
4. Optional: render a template with `applyTemplate` or a canned IM message with `applyCannedMessage`.
5. Draft first with `draftsReply` when a human should review. Send with `sendReply` only when the reply is authorized.
6. Read the ticket back (`getTicketConversations` or `getLastThreadMessage`) to confirm the outbound thread exists.

The From address in the email must already be configured in the help desk portal.

## 3. Add an internal note and log time

```text
getTicket -> createTicketComment -> createTicketTimeEntry
```

1. Confirm the ticket ID.
2. Add an internal comment with `createTicketComment`. For an @mention use `zsu[@user:{zuid}]zsu`.
3. If billable or tracked work is required, add `createTicketTimeEntry` with the ticket ID and duration.
4. Verify with `getTicketComments` and `getTicketTimeEntries`.

## 4. Triage, reassign, or close a ticket

```text
getTicket -> getAgentsInDepartment / getDepartments -> updateTicket / closeTickets
```

1. Read the current ticket so status, owner, and department are known.
2. Resolve department and agent IDs through lookup tools. Never copy IDs from another customer or from free text.
3. Update fields with `updateTicket` (status, priority, assignee, department).
4. Close with `closeTickets` only when the conversation is complete and a resolution note exists or is not required.
5. Read the ticket back immediately.

## 5. Execute a blueprint transition

```text
getTicket -> getBlueprint / getDuringTransitionForm -> performBlueprintTransition
```

1. Confirm the ticket is on a blueprint (`getTicket`).
2. Inspect allowed transitions with `getDuringTransitionForm`.
3. Supply only the action payloads the transition requires (comment, reply, field update, resolution).
4. Execute `performBlueprintTransition`, then read the ticket back.

## 6. Maintain email templates (admin)

```text
getDepartments -> getTemplates -> getTemplate / getPlaceHolders -> addTemplate / updateTemplate
```

1. Resolve the department ID.
2. List existing templates with `getTemplates`.
3. Inspect placeholders with `getPlaceHolders` before inserting merge fields.
4. Create or update with `addTemplate` / `updateTemplate` / `patchTemplate`.
5. Read the template back with `getTemplate`.

## 7. Look up a contact and their tickets

```text
searchContacts -> getContact -> getTicketsByContact
```

1. Search by name, email, or phone with `searchContacts`.
2. Open the contact with `getContact`.
3. List related tickets with `getTicketsByContact` or `getContactTicketHistory`.
4. Create a missing contact with `createContact` only after a search returned no match.
