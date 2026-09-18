## Description: <br>
Connects an agent to Zoho Desk through MCP so it can look up tickets, inspect conversations, draft and send replies, manage templates and helpdesk settings, and use mcporter-based helper scripts for common Desk operations. <br>

This skill is ready for commercial/non-commercial use. <br>

## Publisher: <br>
[sprintcx](https://clawhub.ai/user/sprintcx) <br>

### License/Terms of Use: <br>
MIT <br>


## Use Case: <br>
Developers and support operators use this skill to connect an agent to Zoho Desk via MCP, configure least-privilege action profiles, look up tickets and contacts, send authorized replies, and administer templates or helpdesk settings through mcporter. <br>

### Deployment Geography for Use: <br>
Global <br>

## Known Risks and Mitigations: <br>
Risk: The ZOHO_DESK_MCP_URL endpoint is credential-bearing and could expose Desk access if echoed, logged, or shared. <br>
Mitigation: Treat the MCP URL like a password, avoid printing the full value, and enable only the Actions required for the chosen profile. <br>
Risk: Helper scripts pass the credential-bearing MCP endpoint to mcporter, so local process visibility and logs should be treated carefully. <br>
Mitigation: The scripts call mcporter directly without shell expansion and never print ZOHO_DESK_MCP_URL intentionally. Run them only on trusted systems. <br>
Risk: Read-write Zoho Desk actions can create tickets, send customer emails, change templates, and alter helpdesk settings if enabled on the MCP server. <br>
Mitigation: Start with the ticket-agent profile for reply work. Keep the desk-admin profile for template and settings work. Keep delete, spam-empty, and SAR export Actions disabled unless explicitly required. <br>
Risk: Zoho Desk contains customer support data, including emails and attachments. <br>
Mitigation: Load only required records and never copy contents into chats, logs, or repositories. <br>


## Reference(s): <br>
- [Zoho Desk MCP ClawHub page](https://clawhub.ai/sprintcx/skills/zoho-desk-mcp) <br>
- [GitHub source repository](https://github.com/sprintberlin/openclaw-zoho-desk-mcp-skill) <br>
- [Zoho MCP portal](https://mcp.zoho.eu) <br>


## Skill Output: <br>
**Output Type(s):** [guidance, shell commands, configuration, code] <br>
**Output Format:** [Markdown guidance with bash, JSON, and Python examples] <br>
**Output Parameters:** [1D] <br>
**Other Properties Related to Output:** [Requires ZOHO_DESK_MCP_URL, a named profile, or a one-off endpoint; bundled helper scripts can print table or JSON output from Zoho Desk MCP calls.] <br>

## Skill Version(s): <br>
1.0.0 <br>

## Ethical Considerations: <br>
Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment. <br>
