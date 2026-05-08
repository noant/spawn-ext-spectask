---
name: spectask-task-from-jira
description: Import a ticket from an external tracker into spec/tasks; manual fallback if MCP/config missing.
---

### Workflow

1. Prefer the MCP tool `jira_fetch` (pass the issue key when known). If MCP is unavailable or the call fails, fall back to `spectask-mcp run --issue KEY`.
2. On success: mkdir `spec/tasks/{task-code}-{slug}/` with `task-code` = ticket key; write `overview.md` using spectask template; copy ticket body into Details.
3. On failure: ask user for key + pasted description; same layout.

For full **Step 1** spec work after the scaffold exists, follow **spectask-create** and **spec/main.md** (`task-code` rules 3-4).
