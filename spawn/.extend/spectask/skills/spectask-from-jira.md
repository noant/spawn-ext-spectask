---
name: spectask-from-jira
description: Import a ticket from an external tracker into spec/tasks; manual fallback if MCP/config missing.
---

Operate within the **spectask** process in attached **spec/main.md**.
**task-code**: ticket key per **Embedded rule 4** (e.g. `PROJ-123`).

**Step 1. Fetch ticket**

1. Prefer MCP tool `jira_fetch` (pass issue key). On failure try `spectask-mcp run --issue KEY`. On failure ask the user for key + pasted title/body.

**Step 2. Scaffold**

2. Derive a kebab-case slug from the ticket summary.
3. Create `spec/tasks/{task-code}-{slug}/`.

**Step 3. Spec (Steps 1-2 per spec/main.md)**

Ticket body is source requirements only — not a finished spec. Do not copy it as-is into overview.md.

4. Explore the repo and relevant **spec/design/** docs to map ticket intent to concrete paths and symbols before writing anything.
5. In **Details**, add a **Jira source** subsection (key, summary, relevant ticket fields/body). Clarifications and constraints go below it.
6. Complete **Steps 1-2** exactly as in **spec/main.md** and **spectask-create** — then stop and wait for the user's Step 3.
