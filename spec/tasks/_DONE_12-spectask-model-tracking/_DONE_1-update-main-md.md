# Step 1: Update extsrc/files/spec/main.md templates and instructions

Status: Done | model: claude-sonnet-4-6

## Goal
Apply all model-tracking additions to `extsrc/files/spec/main.md`, `spec/main.md`, `extsrc/skills/spectask-create.md`, and `extsrc/skills/spectask-execute.md`: status-line `[model]` placeholders in the overview template, the `Status:` line in the subtask template, sub-agent prompt requirements in Steps 2/4/5, model-recording instructions in Steps 1 and 7, and `My model:` hints in the two skills.

## Approach
1. Open `extsrc/files/spec/main.md`.
2. Apply edits 1-7 below.
3. Verify no other lines were accidentally changed.
4. Apply the same 7 edits to `spec/main.md` (locally active copy; content is identical except a trailing newline).
5. Apply Edit 8 to `extsrc/skills/spectask-create.md`.
6. Apply Edit 9 to `extsrc/skills/spectask-execute.md`.

## Affected files
- `extsrc/files/spec/main.md`
- `spec/main.md`
- `extsrc/skills/spectask-create.md`
- `extsrc/skills/spectask-execute.md`

## Code changes (before / after)

Placeholder convention used in After blocks:
- `[model]` — suffix added to a checkbox status line template.
- `{model}` — placeholder inside `Status:` lines in subtask files.
- `[model-name]` — literal example token shown in instruction text.

---

### Edit 1 — overview.md template, Status block (lines 134-140)

**Before**
```markdown
- [ ] Spec created
- [ ] Self spec review passed
- [ ] Spec review passed
- [ ] Code implemented
- [ ] Self code review passed
- [ ] Code review passed
- [ ] Design documents updated
```
Plain checkboxes; no model info.

**After**
```markdown
- [ ] Spec created [model]
- [ ] Self spec review passed [model]
- [ ] Spec review passed
- [ ] Code implemented [model]
- [ ] Self code review passed [model]
- [ ] Code review passed
- [ ] Design documents updated [model]
```
Five agent-executed lines gain a `[model]` suffix. User-confirmed lines unchanged.

---

### Edit 2 — subtask file template, header block (lines 178-180)

**Before**
```markdown
# Step {N}: {Short title}

## Goal
```
No execution status or model field.

**After**
```markdown
# Step {N}: {Short title}

Status: Not implemented | model: {model}

## Goal
```
`Status:` line inserted between title and `## Goal`. Agent sets it to `Status: Done | model: {model}` when the subtask completes.

---

### Edit 3 — Step 1 instructions, set [V] arrow line (line 47)

**Before**
```markdown
→ set [V] "Spec created"
```
No model attribution.

**After**
```markdown
→ set [V] "Spec created" — fill model name in brackets: `- [V] Spec created [model-name]`
```
Step 1 is executed by the current (parent) agent; it records its own model name.

---

### Edit 4 — Step 2 executor block (lines 51-58)

**Before**
```markdown
## Step 2: Self Spec Review

**Executor:** AI Agent (New sub-agent)

Review the spec for: architectural impact, implementation errors, sequencing issues; verify every step and overview list concrete files, modules, and symbols (classes, methods, functions) per Embedded rule 7. Fix if needed.

→ set [V] "Self spec review passed"
→ prompt: "Self spec review passed — spec is ready for your review (Step 3). Reply 'spec review passed', 'lgtm', or 'ok' when satisfied."
```
Sub-agent is launched but never asked to identify its model; parent has no way to record it.

**After**
```markdown
## Step 2: Self Spec Review

**Executor:** AI Agent (New sub-agent)

Sub-agent prompt must include: "Start your response with the line `My model: {model-name}`."

Review the spec for: architectural impact, implementation errors, sequencing issues; verify every step and overview list concrete files, modules, and symbols (classes, methods, functions) per Embedded rule 7. Fix if needed.

→ set [V] "Self spec review passed" — read the first line of the sub-agent response, extract model name, fill in brackets: `- [V] Self spec review passed [model-name]`
→ prompt: "Self spec review passed — spec is ready for your review (Step 3). Reply 'spec review passed', 'lgtm', or 'ok' when satisfied."
```
Sub-agent identifies itself; parent extracts the name from the first response line.

---

### Edit 5 — Step 4 executor block (lines 72-83)

**Before**
```markdown
## Step 4: Code Implemented

**Executor:** AI Agent (current context) — reads `spec/extend/`, follows Execution Scheme, launches one sub-agent per step.
**Each step in the Execution Scheme:** AI Agent (New sub-agent).

On "run it" / "implement" / "execute" / any direct instruction to start implementation:
0. If "Spec review passed" is not yet marked, set [V] "Spec review passed" automatically — the user's implementation command implies approval.
1. Read all files in spec/extend/ first.
2. MANDATORY! Launch a subagent per step — do NOT implement inline. No exceptions — even if a step seems trivial or small.
3. Follow Execution Scheme: → sequential, || parallel.

→ set [V] "Code implemented", rename done subtasks to _DONE_
```
Sub-agents are launched without a model identification requirement; no model recorded in subtask files or overview.

**After**
```markdown
## Step 4: Code Implemented

**Executor:** AI Agent (current context) — reads `spec/extend/`, follows Execution Scheme, launches one sub-agent per step.
**Each step in the Execution Scheme:** AI Agent (New sub-agent).

On "run it" / "implement" / "execute" / any direct instruction to start implementation:
0. If "Spec review passed" is not yet marked, set [V] "Spec review passed" automatically — the user's implementation command implies approval.
1. Read all files in spec/extend/ first.
2. MANDATORY! Launch a subagent per step — do NOT implement inline. No exceptions — even if a step seems trivial or small. Sub-agent prompt must include: "Start your response with the line `My model: {model-name}`."
3. Follow Execution Scheme: → sequential, || parallel.

→ set [V] "Code implemented" — fill coordinator model name in brackets: `- [V] Code implemented [model-name]`; rename done subtasks to _DONE_ and set `Status: Done | model: {model}` in each subtask file using the model name read from that sub-agent's first response line
```
Each sub-agent identifies itself; parent records its name in the subtask file. Coordinator records its own model on the overview status line.

---

### Edit 6 — Step 5 executor block (lines 87-94)

**Before**
```markdown
## Step 5: Self Code Review

**Executor:** AI Agent (New sub-agent)

Review all changes: inconsistencies, naming, missing imports, broken contracts. Fix if needed.

→ set [V] "Self code review passed"
→ prompt: "Self review done. Reply 'code review passed' to proceed."
```
Sub-agent is launched but never asked to identify its model.

**After**
```markdown
## Step 5: Self Code Review

**Executor:** AI Agent (New sub-agent)

Sub-agent prompt must include: "Start your response with the line `My model: {model-name}`."

Review all changes: inconsistencies, naming, missing imports, broken contracts. Fix if needed.

→ set [V] "Self code review passed" — read the first line of the sub-agent response, extract model name, fill in brackets: `- [V] Self code review passed [model-name]`
→ prompt: "Self review done. Reply 'code review passed' to proceed."
```
Sub-agent identifies itself; parent extracts and records the name.

---

### Edit 7 — Step 7 instructions, set [V] arrow line (line 121)

**Before**
```markdown
→ set [V] "Design documents updated"
```
No model attribution.

**After**
```markdown
→ set [V] "Design documents updated" — fill model name in brackets: `- [V] Design documents updated [model-name]`
```
Step 7 is executed by the current (parent) agent; it records its own model name.

---

### Edit 8 — `extsrc/skills/spectask-create.md` — body text

**Before**
```markdown
Operate within the **spectask** process defined in attached **spec/main.md**.
**task-code** naming and confirmations: **Embedded rules** 3-4 in **spec/main.md**.
Complete **Steps 1–2** only — then stop and wait for the user’s **Step 3** (spec review).

Under this skill, writing implementation code without an approved specification is not allowed — stay within Steps 1–2 (overview.md and subtasks) until spec review passes.

If work began from **`spec/seeds/`**, tie the seed to the new task in **Step 1** (**`linked task:`** + **Source seed** in **`overview.md`**) and close it in **Step 7** item **6**, per **`spec/main.md`**.
```
No mention of the `My model:` requirement for the Step 2 sub-agent prompt.

**After**
```markdown
Operate within the **spectask** process defined in attached **spec/main.md**.
**task-code** naming and confirmations: **Embedded rules** 3-4 in **spec/main.md**.
Complete **Steps 1–2** only — then stop and wait for the user’s **Step 3** (spec review).

Under this skill, writing implementation code without an approved specification is not allowed — stay within Steps 1–2 (overview.md and subtasks) until spec review passes.

If work began from **`spec/seeds/`**, tie the seed to the new task in **Step 1** (**`linked task:`** + **Source seed** in **`overview.md`**) and close it in **Step 7** item **6**, per **`spec/main.md`**.

When launching the Step 2 sub-agent, include this line in the prompt: "Start your response with `My model: {model-name}`." Use the returned model name when filling `- [V] Self spec review passed [model-name]`.
```
Adds a concrete reminder so the sub-agent prompt always contains the model identification requirement.

---

### Edit 9 — `extsrc/skills/spectask-execute.md` — body text

**Before**
```markdown
Operate within the **spectask** process defined in attached **spec/main.md**.

Complete **Steps 4–5**. Then wait for the user for **Step 6**.
```
No mention of the `My model:` requirement for Step 4 or Step 5 sub-agent prompts.

**After**
```markdown
Operate within the **spectask** process defined in attached **spec/main.md**.

Complete **Steps 4–5**. Then wait for the user for **Step 6**.

When launching sub-agents in Step 4 (one per Execution Scheme step) and Step 5 (self code review), include this line in each prompt: "Start your response with `My model: {model-name}`." Use each returned model name when filling subtask `Status:` lines (Step 4) and `- [V] Self code review passed [model-name]` (Step 5).
```
Adds a concrete reminder covering both sub-agent launches in this skill's scope.

---

### `spec/main.md` — all edits above

`spec/main.md` is the locally active copy; content is identical to `extsrc/files/spec/main.md` at all cited lines (files differ only by a trailing newline).

Apply the same replacements in `spec/main.md`. Before blocks are identical to those listed above.

Representative excerpt confirming identity (Status block, line 134):

**Before**
```markdown
- [ ] Spec created
- [ ] Self spec review passed
- [ ] Spec review passed
- [ ] Code implemented
- [ ] Self code review passed
- [ ] Code review passed
- [ ] Design documents updated
```
Same plain checkboxes as in the extsrc copy.

**After**
```markdown
- [ ] Spec created [model]
- [ ] Self spec review passed [model]
- [ ] Spec review passed
- [ ] Code implemented [model]
- [ ] Self code review passed [model]
- [ ] Code review passed
- [ ] Design documents updated [model]
```
Same result as Edit 1; keeps the locally active copy in sync.

## Additional actions
None.
