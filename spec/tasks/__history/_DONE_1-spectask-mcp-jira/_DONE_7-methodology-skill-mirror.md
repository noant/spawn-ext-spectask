# Step 7: Methodology text, new skill, extension mirror

## Goal
Update **English-only** methodology in `spec/main.md` (mirrored in `extsrc/files/spec/main.md`): broad `{task-code}-{slug}` task folders, optional `spec/.config/config.yaml`, rules for suggested serial codes, user confirmation when not ticket-sourced, ticket key as `task-code` when imported from an external tracker; add `spectask-task-from-jira` skill.

## Approach
Edit repo **`spec/main.md`** **Folder Structure** section (then mirror to **`extsrc/files/spec/main.md`** verbatim):
- Add **`spec/.config/config.yaml`** bullet: local-only connector config (ticket-system MCP / `spectask-mcp`); artifact; do not commit secrets.
- Replace task folder paths with **`spec/tasks/{task-code}-{slug}/`** (`{task-code}` = task identifier — often serial digits, may be an external ticket key; `{slug}` = short name).

**Embedded rules** (insert and renumber — see **After** block below): suggested next numeric **task-code**, user must confirm before creating a folder when **not** sourcing from an external ticket tracker, external ticket import uses that ticket key as **task-code**.

Add **`extsrc/skills/spectask-task-from-jira.md`** per `spawn-ext-guide/ai/skill-sources.md`. Body: when user wants a ticket-backed spectask, use MCP/config when available; else manual key + text. Cross-reference `spectask-create`.

Register skill in **`extsrc/config.yaml`** under **`skills:`**.

Optionally one line in **`spectask-create.md`** / **`spectask-seed-create.md`**: point to `spec/main.md` rules for **task-code** and confirmations.

## Affected files
- `spec/main.md`
- `extsrc/files/spec/main.md`
- `extsrc/skills/spectask-task-from-jira.md` (new)
- `extsrc/config.yaml` — `skills:` registration
- `extsrc/skills/spectask-create.md` (optional)
- `extsrc/skills/spectask-seed-create.md` (optional)

## Code changes (before / after)

### `spec/main.md` — folder list and embedded rules (same diff in `extsrc/files/spec/main.md`)

**Before**
```markdown
- spec/tasks/{X}-{name}/ — task folder (artifact tree in this methodology pack).
- spec/tasks/{X}-{name}/overview.md — task overview (required).
- spec/tasks/{X}-{name}/{N}-{description}.md — subtask files (optional; required when `## Execution Scheme` defines 2+ steps).
- spec/seeds/{X}-{slug}.md — seed file (artifact tree in this methodology pack).
```

**After**
```markdown
- spec/.config/config.yaml — optional local-only connector config (e.g. ticket-system MCP for `spectask-mcp`); artifact; must stay untracked — do not commit credentials.
- spec/tasks/{task-code}-{slug}/ — task folder (artifact tree). `{task-code}` identifies the task (often a serial code; may instead be a key from an external ticket/issue tracker). `{slug}` is a short descriptive name (use `-` separators).
- spec/tasks/{task-code}-{slug}/overview.md — task overview (required).
- spec/tasks/{task-code}-{slug}/{N}-{description}.md — subtask files (optional; required when `## Execution Scheme` defines 2+ steps).
- spec/seeds/{X}-{slug}.md — seed file (artifact tree in this methodology pack).
```

**Before** (embedded rule 3 fragment)
```markdown
3. **Next task `X`:** 1 + max task id from every `spec/tasks/` subfolder (`{id}-*` and `_DONE_{id}-*`); if none, **1**.
```

**After** (replace rules 3–9 with 3–11; former rules 4–9 become 6–11)
```markdown
3. **Suggested next numeric `task-code`:** Among `spec/tasks/` folder names whose **first** segment (before the first `-`) is **only** decimal digits, compute 1 + max of those ids (include `_DONE_{id}-*` directories); if none exist, **1**. This is a **suggestion** for the next serial `task-code`, not final until the user agrees (see rule 4).
4. **User confirmation (`task-code`, not from ticket tracker):** When creating a task **not** sourced from a row in an external ticket/issue tracker (numeric-style `task-code`), state the suggestion from rule 3, ask the user to confirm or substitute another allowed `task-code`, and **wait** for explicit approval before creating `spec/tasks/{task-code}-{slug}/`.
5. **`task-code` from external tracker:** When the task is imported from an external ticket/issue tracker, `task-code` **must** be that ticket key (e.g. `PROJ-123`); rule 4 does not apply. Additional `-` segments may carry the slug as usual.
6. **New spec tasks:** follow **Step 1** and the overview template at the end of this file. Older `spec/tasks/_DONE_*` overviews may predate the template; **do not** copy their structure unless it already matches the template.
7. **`read-required` (and contextual reads) in `spawn/navigation.yaml`:** obey Spawn's merged navigation — treat required entries like **`read: required`** on the old registry.
8. **Task-scoped reads:** from `spawn/navigation.yaml`, read every path the active task context clearly needs (not only globally required entries).
9. **Process:** follow the workflow in this document — Steps 1–7, status marks, and user prompts as written.
10. **Concrete codebase targets:** Every overview and subtask must name specific paths and symbols (packages/modules, classes, methods, functions) under change. In subtasks, each **Code changes** **Before** / **After** pair is a fenced minimal excerpt — real lines or the exact replacement — plus the short behavior line from the subtask file template. Prose-only or “change X to Y” without code is invalid. Specs are executable edits, not intentions. Self Spec Review treats missing targets, non-concrete Before/After, or template violations as defects before Step 3.
11. **Greenfield (new symbols):** Same **Before**/**After** under **Code changes**. **Before** may be context-only (location/insertion — nothing to quote); **After** is fenced code + behavior line, like rule 10. Vague **Before** or non-concrete **After** — Self Spec Review defects before Step 3.
```

Also in **`spec/main.md`**: **`## overview.md Template`** title line `{X}` to **`{task-code}`**; **Step 7** bullet `Rename folder to _DONE_{X}-{name}` to **`_DONE_{task-code}-{name}`** (same for any other `{X}` referring to task folder id in that section).

Behavior: methodology text is **English only** and uses broad “external ticket/issue tracker” wording; implementation details stay in the MCP package, not in methodology naming.

### `extsrc/config.yaml` — register skill

**Before**
```yaml
skills:
  spectask-create.md:
    name: spectask-create
```

**After**
```yaml
skills:
  spectask-task-from-jira.md:
    name: spectask-task-from-jira
    description: "Import external tracker tickets into spec/tasks/{task-code}-{slug}/; offline fallback."
  spectask-create.md:
    name: spectask-create
```

### `extsrc/skills/spectask-task-from-jira.md` — new skill file

**Before**
```markdown
(file absent)
```

**After**
```markdown
---
name: spectask-task-from-jira
description: Import a ticket from an external tracker into spec/tasks; manual fallback if MCP/config missing.
---

### Workflow

1. Detect `spec/.config/config.yaml` and try `spectask-mcp run --issue KEY` or MCP tool `jira_fetch`.
2. On success: mkdir `spec/tasks/{task-code}-{slug}/` with `task-code` = ticket key; write `overview.md` using spectask template; copy ticket body into Details.
3. On failure: ask user for key + pasted description; same layout.
```

Behavior: aligns with `spec/main.md` embedded rules on `task-code`.

## Additional actions
- Bump extension `version` in `extsrc/config.yaml` when shipping MCP/skills alongside methodology changes (`spawn-ext-mcp` / `spawn-ext-increment-version`).
