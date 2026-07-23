# Spec-Tasks: AI-Oriented Development Methodology

## Folder Structure

- spec/main.md — this file.
- spec/design.yaml — index of architecture documents (`path` + `description` per entry); optional but recommended when multiple design files exist.
- spec/design/hla.md — project high-level architecture (required).
- spec/design/{name}.md — other architecture documents (optional; ADRs, notes, etc.); register in **spec/design.yaml** and declare as readable paths for agents — typically via a Spawn extension's `files:` (with appropriate reads) so they appear in `spawn/navigation.yaml`.
- spec/tasks/{task-code}-{slug}/ — task folder (artifact tree). `{task-code}` identifies the task (often a serial code; may instead be a key from an external tracker). `{slug}` is a short descriptive name.
- spec/tasks/{task-code}-{slug}/overview.md — task overview (required).
- spec/tasks/{task-code}-{slug}/{N}-{description}.md — subtask files (optional; required when `## Execution Scheme` defines 2+ steps).
- spec/seeds/{X}-{slug}.md — seed file (artifact tree in this methodology pack).

**Embedded rules:**

Every rule has a stable label `[R{n}-{slug}]`. Reference rules by label (e.g. `R10-ask`), not by number — the label survives renumbering.

_Folder hygiene_

1. **`R1-paths`** — Under `spec/`, only paths allowed by the Folder Structure are permitted; no other files.
2. **`R2-no-clutter`** — Do not create READMEs or other extraneous docs under `spec/` (a special case of `R1-paths`).

_Task identification_

3. **`R3-code-num`** — Numeric `task-code`: suggest the next number (`R10-ask`) and wait for an explicit reply before creating `spec/tasks/{task-code}-{slug}/`. Next number = the highest existing `{task-code}` under `spec/tasks/` (including `_DONE_`) plus 1.
4. **`R4-code-tracker`** — A `task-code` from an external tracker must be the ticket key (e.g. `PROJ-123`). Segments after the first `-` may carry the slug.

_Task specs_

5. **`R5-new-task`** — New spec tasks follow Step 1 and the overview template at the end of this file.
6. **`R6-legacy-done`** — Older `spec/tasks/_DONE_*` overviews may predate the current template; do not copy their structure unless it matches the template.
7. **`R7-process`** — Status marks `[V]` and user prompts must reproduce the wording from the corresponding Step exactly; Steps run in order unless the process explicitly allows otherwise.
8. **`R8-concrete`** — Specs are executable edits, not intentions: every overview and subtask names concrete paths and symbols (packages/modules, classes, methods, functions) under change, and every Before / After pair in Code changes is a fenced minimal excerpt (real lines or the exact replacement) plus a behavior line. Prose-only or "change X to Y" without code is invalid. Self Spec Review treats missing concrete targets, non-concrete Before/After, or template violations as defects before Step 3.
9. **`R9-greenfield`** — For new symbols, the same Before/After discipline as `R8-concrete`, with two differences: Before may be insertion-context only (nothing to quote); After is still fenced code plus a behavior line.

_Interaction and context_

10. **`R10-ask`** — When you must ask the user (clarifications, confirmations, choices), use the platform structured ask tool (see `R12-ask-tools`), preferring multiple choice. Fallback order: platform tool -> installed MCP (elicitation) -> plain chat question.
11. **`R11-navigation`** — Before drafting a spec, open **`spawn/navigation.yaml`**, read all `read-required`, read task-relevant `read-contextual`, and apply them in the spec. If the file is absent, the rule is a no-op (proceed). Self Spec Review re-checks compliance; violations are defects.
12. **`R12-ask-tools`** — User-question tools by platform (data for `R10-ask`):
    - **Cursor:** AskQuestion / cursor/ask_question
    - **VS Code/Copilot:** AskQuestions / vscode_askQuestions
    - **Claude Code:** AskUserQuestion; MCP elicitation/create
    - **Codex:** request_user_input
    - **Other:** IDE embedded tool or installed MCP; fallback is a plain text question.
13. **`R13-model-line`** — Every sub-agent prompt must include this line verbatim:
    > End your final response with the line `My model: X` where X is your actual model identifier (e.g. `claude-sonnet-4-6`, `gpt-4o`) — write your actual model identifier in place of X.
    When recording `[V]`/`[model-name]` after a sub-agent: read the last line of its response, extract the model name, and fill it in the brackets.

---

## Process Overview

```
[1] Spec created → [2] Self spec review → [3] Spec review (user) → [4] Code implemented → [5] Self code review → [6] Code review / Debugging (user) → [7] Design documents updated → (optional) pattern extract to spawn/rules/
```

Mark each status [V] on completion. Prompt the user after steps 2, 5, and 6. After Step 7, offer optional Pattern extract (not a Status checkbox).

---

## Step 1: Spec created

**Executor:** AI Agent (current context)

1.1 **Project rules (navigation)** — **MANDATORY!** Follow `R11-navigation` before writing any spec content.
1.2 **Implementation clarifications** — **MANDATORY!** Before writing any spec content, identify ambiguous, optional, or convention-dependent aspects. Ask the user explicit questions (`R10-ask`) and wait for answers. Record answers (or agreed defaults) in **Details**. Skip only when there is a single obvious implementation path.
1.3 **Design overview** — in the task `overview.md`, add a **Design overview** section: affected modules; concrete paths and symbols (`R8-concrete`); data flow changes; integration points.
1.4 **Overview** — `spec/tasks/{task-code}-{slug}/overview.md` follows the overview.md template: sections through `## Details` (before/after and code examples go there); **Goal** = one sentence. Add `## Execution Scheme` only when work splits into 2+ steps.
1.5 **Execution Plan** — with 2+ steps: the step ids in `## Execution Scheme` must match the `{N}-{description}.md` filenames from 1.6.
1.6 **Decomposition** — create {N}-{description}.md per step: goal, approach, affected files (with named classes/methods/functions per path), code changes (before/after). You may launch a **new sub-agent** for read-only codebase analysis to determine accurate **Before** / **After** text, then merge its findings into the step files (analysis only; the parent agent owns decomposition and the spec).

→ set [V] "Spec created" `[model-name]` (record the model per `R13-model-line`): `- [V] Spec created [model-name]`

---

## Step 2: Self spec review

**Executor:** AI Agent (new sub-agent)

The sub-agent prompt must include the line from `R13-model-line`.

Review the spec for: architectural impact, implementation errors, sequencing issues; verify every step and overview list concrete files, modules, and symbols (classes, methods, functions) per `R8-concrete`; verify compliance with `R11-navigation`. Fix if needed.

→ set [V] "Self spec review passed" `[model-name]` (record the model per `R13-model-line`): `- [V] Self spec review passed [model-name]`
→ prompt: "Self spec review passed — spec is ready for your review (Step 3). Reply 'spec review passed', 'lgtm', or 'ok' when satisfied."

---

## Step 3: Spec review

**Executor:** User

On confirmation ("spec review passed", "lgtm", "ok"):
→ set [V] "Spec review passed"
→ prompt: "Reply 'implement' to start."

---

## Step 4: Code implemented

**Executor (coordination):**
- **Same chat as Steps 1–2:** the agent that created the spec must not coordinate Steps 4–5 itself. On the implementation command, launch **one new sub-agent** as the coordinator that owns Steps 4–5 end-to-end. The parent waits for the sub-agent, then waits for the user for Step 6. Do not open a separate chat manually.
- **Fresh execute chat** (Steps 1–2 not in context): the current agent is the coordinator.

**Coordinator** — follows the Execution Scheme, launches one sub-agent per step, then Step 5.
**Each step in the Execution Scheme:** AI Agent (new sub-agent) — child of the coordinator.

On "run it" / "implement" / "execute" / any direct instruction to start implementation:
0. If "Spec review passed" is not yet marked, set [V] "Spec review passed" automatically — the implementation command implies approval.
0a. If this chat already completed Steps 1–2 for the task: launch the Steps 4–5 coordinator sub-agent (see Executor above) and stop coordinating inline. Include in its prompt: follow Steps 4–5 for `spec/tasks/{task-code}-{slug}/`; the line from `R13-model-line`.
1. MANDATORY! Launch a sub-agent for each step — do NOT implement inline. No exceptions, even if a step seems trivial. The sub-agent prompt must include the line from `R13-model-line`.
2. Follow the Execution Scheme: → sequential, || parallel.

→ set [V] "Code implemented" `[model-name]` of the coordinator (record the model per `R13-model-line`): `- [V] Code implemented [model-name]`; rename completed subtasks to _DONE_ and set `Status: Done | model: {model}` in each subtask file, taking the model name from the corresponding sub-agent's response

---

## Step 5: Self code review

**Executor:** AI Agent (new sub-agent)

The sub-agent prompt must include the line from `R13-model-line`.

Review all changes: inconsistencies, naming, missing imports, broken contracts. Fix if needed.

→ set [V] "Self code review passed" `[model-name]` (record the model per `R13-model-line`): `- [V] Self code review passed [model-name]`
→ prompt: "Self review done. Reply 'code review passed' to proceed."

---

## Step 6: Code review / Debugging

**Executor:** User

On confirmation ("code review passed", "lgtm", "ok"):
→ set [V] "Code Review / Debugging passed"
→ prompt: "Will now update design documents (Step 7)."

---

## Follow-up changes after implementation

If the user requests rework or fixes after Step 4:

1. Carry out the changes.
2. Ask via `R10-ask`: "Do you want to update the specifications of the current task?"
   - Yes: edit the affected subtask files and/or `overview.md` to match the actual state; do not re-run the spec cycle.
   - No: proceed without changes.

---

## Step 7: Design documents updated

**Executor:** AI Agent (current context)

Do not start Step 7 until **Code Review / Debugging passed** is marked (Step 6).

1. **Index** — read **spec/design.yaml**. If missing, only **spec/design/hla.md** applies (Folder Structure); add **spec/design.yaml** when you register more than one path under **spec/design/**.
2. **Scope** — from subtasks, the Execution Scheme, and the files changed/added in this task, choose the `path` rows to update; update those that matter, skip the rest.
3. **Write** — for each chosen path, align the markdown with the repo after this task; create the file if it is listed but missing.
4. If the task introduced or renamed architecture docs under **spec/design/**, update **spec/design.yaml** (`path` + `description` for each).
5. Rename the folder to _DONE_{task-code}-{name}.
6. If the Source seed Path in the overview is concrete and the listed spec/seeds file is linked to this overview, rename it once with _DONE_ added.

→ set [V] "Design documents updated" — fill the model name in brackets: `- [V] Design documents updated [model-name]`
→ continue with **Optional: Pattern extract** below (same run when closing via Steps 6–7).

---

## Optional: Pattern extract (after Step 7)

**Executor:** AI Agent (current context)

After Step 7, optionally extract reusable approaches into **`spawn/rules/`** as project-standard candidates. Not a Status item. Skill: **spectask-extract-patterns**.

Ask once after Step 7 unless already declined in this close-out.

### Selection criteria (filter before asking)

Propose only candidates that pass all of:

1. **Reusable** — a pattern, approach, or convention useful beyond this single task (not a one-off edit).
2. **Actionable** — can become a short rule an agent can follow.
3. **Standard candidate** — plausible as a lasting convention for this project.
4. **Not already covered** — check existing **`spawn/rules/`**, **`spawn/navigation.yaml`** rule rows, and related Spawn reads / methodology files for duplicates or near-duplicates.
5. **Pre-existing code OK** — a pattern already present in the codebase before this task but not yet captured in rules remains a valid candidate. Do not reject it only because this task did not introduce it; discovery during close-out is enough.
6. **Code examples** — prefer short real (or minimally realistic) excerpts that show the pattern. Prose-only when necessary.

Reject immediately (do not offer):

- Task-specific wiring, ticket ids, temporary workarounds
- Restatements of HLA, language defaults, or existing rules
- Vague slogans without an enforceable rule
- Low-value or speculative ideas (junk)

If filtering leaves zero candidates: say so briefly and stop (do not invent fillers).

### Ask (`R10-ask`)

Ask **one question per filtered candidate** (short title + one-line rationale). Options for each:

- **Required** — `read-required`
- **Optional** — `read-contextual`
- **Decline** — skip this rule

Wait for answers. Write only candidates marked Required or Optional, each with its scope. If every answer is Decline (or there were no candidates), write nothing.

### Write

1. Write under **`spawn/rules/`** (create the folder if missing).
2. Prefer an existing **`spawn/rules/`** file on the same topic — merge or revise it. If none fits, create a new kebab-case Markdown file.
3. Prefer short code examples in each rule when applicable (criterion 6).
4. Add each file to **`spawn/navigation.yaml`** under **`read-required` → `rules`** or **`read-contextual` → `rules`** as the user chose. Row: **`path`** + short **`description`** (not hint-only). Never list the same path in both.
5. Run exactly **`spawn refresh`** in the terminal — this applies the new rules across skills and rule files.

---

## overview.md Template

```markdown
# {task-code}: {Title}

## Source seed
- Path: {seed path or none}

## Status
- [ ] Spec created [model]
- [ ] Self spec review passed [model]
- [ ] Spec review passed
- [ ] Code implemented [model]
- [ ] Self code review passed [model]
- [ ] Code Review / Debugging passed
- [ ] Design documents updated [model]

## Goal
{One concise sentence.}

## Design overview
- Affected modules: {list}
- Files & symbols (concrete paths; class / method / function / module names to touch): {list}
- Data flow changes: {description}
- Integration points: {list}

## Before → After
### Before
- {current state}
### After
- {desired state}

## Details
{Clarifying details, code examples, constraints.}

## Execution Scheme
> Each step id is the subtask filename (e.g. `1-abstractions`).
> MANDATORY! Each step is executed by a dedicated subagent (Task tool). Do NOT implement inline. No exceptions — even if a step seems trivial or small.
- Phase 1 (sequential): step {N}-{description} → step {N}-{description}
- Phase 2 (parallel):   step {N}-{description} || step {N}-{description}
- Phase 3 (sequential): step review — inspect all changes, fix inconsistencies
```

Omit `## Execution Scheme` if there is no decomposition (single-file spec).

---

## Subtask file template

Filename must match the step id from `## Execution Scheme` (e.g. `1-abstractions.md`). One file per step.

````markdown
# Step {N}: {Short title}

Status: Not implemented | model: {model}

## Goal
{One sentence — outcome of this step.}

## Approach
{Order of work, constraints, references to spec/design if needed.}

## Affected files
- `{path/relative/to/repo/root}`
- `{...}` — {...}

## Code changes (before / after)

### `{path/to/file.ext}` — {path plus named symbols (module, class, method, or function) + what changes}

**Before**
```code
{concrete minimal excerpt or exact lines, not vague prose}
```
{what this code does — behavior, not a repeat of the diff}

**After**
```code
{replacement or new block — one-to-one with Before when editing existing text}
```
{what the new code does — behavior, not a repeat of the diff}

### `{path/to/other.ext}` — {where}
**Before**
```code
{concrete minimal excerpt or exact lines, not vague prose}
```
{what this code does — behavior, not a repeat of the diff}
**After**
```code
{replacement or new block — one-to-one with Before when editing existing text}
```
{what the new code does — behavior, not a repeat of the diff}

## Additional actions
{Optional: shell commands, manual verification steps, follow-up tasks, or other non–file-edit work for this step.}
````

---

**Seed** — optional: a Markdown file in `spec/seeds/` to capture an idea fast; Steps 1–7 do not require it unless you deliberately start there. Link from `overview.md` when you promote into a spectask; apply Step 7 item 6 when closing the linked seed.

## Seed file template (header)

```markdown
linked task: {task path or none}

{idea content}
```
