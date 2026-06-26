---
name: spectask-from-jira
description: Import external tracker tickets into spec/tasks/{task-code}-{slug}/; offline fallback.
---


### Workflow

1. Prefer the MCP tool `jira_fetch` (pass the issue key when known). If MCP is unavailable or the call fails, fall back to `spectask-mcp run --issue KEY`.
2. On success: mkdir `spec/tasks/{task-code}-{slug}/` with `task-code` = ticket key; write `overview.md` using spectask template; copy ticket body into Details.
3. On failure: ask user for key + pasted description; same layout.

For full **Step 1** spec work after the scaffold exists, follow **spectask-create** and **spec/main.md** (`task-code` rules 3-4).


Hints:
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
