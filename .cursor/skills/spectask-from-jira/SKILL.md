---
name: spectask-from-jira
description: Import Jira tickets into spec/tasks/{task-code}-{slug}/; codebase analysis for Step 1-2; offline fallback.
---


Operate within the **spectask** process in attached **spec/main.md**.
**task-code**: ticket key per **Embedded rule 4** (e.g. `PROJ-123`).

**Step 1. Fetch ticket**

1. Prefer MCP tool `jira_fetch` (pass issue key). On failure try `spectask-mcp run --issue KEY`. On failure use Embedded rule 9 to ask the user for key + pasted title/body.

**Step 2. Scaffold**

2. Derive a kebab-case slug from the ticket summary.
3. Create `spec/tasks/{task-code}-{slug}/`.

**Step 3. Spec (Steps 1-2 per spec/main.md)**

Ticket body is source requirements only — not a finished spec. Do not copy it as-is into overview.md.

4. Explore the repo and relevant **spec/design/** docs to map ticket intent to concrete paths and symbols before writing anything.
5. In **Details**, add a **Jira source** subsection (key, summary, relevant ticket fields/body). Clarifications and constraints go below it.
6. Complete **Steps 1-2** exactly as in **spec/main.md** and **spectask-create** — then stop and wait for the user's Step 3.


Hints:
- Use the platform ask tool when available (rule 9 in spec/main.md); plain chat otherwise.
- No emojis or exotic Unicode in code, logs, documentation, or messages; plain ASCII where practical.
- User-facing replies, documentation, and task descriptions: concise wording; minimal markdown (avoid decorative bold/italic); explain with lists and structure; short, clear sentences.
- Specifications, code comments, and project documentation must be written in English.
- If the user only asked a question, answer first; do not edit files unless changes are clearly needed.

Mandatory reads:
- `spec/main.md` - Spec-Tasks methodology — folder structure, seven-step process, overview template.
- `spec/design.yaml` - Index of architecture documents under spec/design/ — path and description per entry.
- `spawn/navigation.yaml` - Merged Spawn navigation (read-required, read-contextual).

Contextual reads:
- `spec/design/hla.md` - Project high-level architecture; updated in Step 7.
