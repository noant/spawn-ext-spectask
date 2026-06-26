# 12: Track LLM model name in spectask status lines

## Source seed
- Path: none

## Status
- [V] Spec created [claude-sonnet-4-5]
- [V] Self spec review passed [composer]
- [V] Spec review passed
- [V] Code implemented [claude-sonnet-4-6]
- [V] Self code review passed [claude-sonnet-4-5]
- [V] Code review passed
- [V] Design documents updated [claude-sonnet-4-6]

## Goal
Update `extsrc/files/spec/main.md`, `spec/main.md`, and the two skills that run sub-agents (`extsrc/skills/spectask-create.md`, `extsrc/skills/spectask-execute.md`) so that every agent-executed status line records the LLM model that performed the work, and every subtask file records its execution status and model.

## Design overview
- Affected modules: `extsrc/files/spec/main.md` (Spawn extension source), `spec/main.md` (locally active copy), `extsrc/skills/spectask-create.md`, `extsrc/skills/spectask-execute.md`
- Files & symbols (concrete paths): `extsrc/files/spec/main.md` and `spec/main.md` — overview.md template Status block, subtask file template header, Step 1 arrow line, Step 2 executor block, Step 4 executor block, Step 5 executor block, Step 7 arrow line; `extsrc/skills/spectask-create.md` — body text; `extsrc/skills/spectask-execute.md` — body text
- Data flow changes: none (documentation/template change only)
- Integration points: Spawn extension pack — `extsrc/files/spec/main.md` is the source that gets distributed; no runtime code is affected

## Before → After
### Before
- `extsrc/files/spec/main.md` / `spec/main.md`: status lines in overview.md template are plain checkboxes with no model placeholder; subtask template header has no status or model field; Step instructions for Steps 1, 2, 4, 5, 7 do not mention recording the model name; sub-agent prompts in Steps 2, 4, 5 do not ask the sub-agent to identify its model.
- `extsrc/skills/spectask-create.md` and `extsrc/skills/spectask-execute.md`: no reminder about the `My model:` sub-agent prompt requirement.

### After
- `extsrc/files/spec/main.md` / `spec/main.md`: agent-executed status lines carry a model placeholder in brackets: `- [ ] Spec created [model]`, `- [ ] Self spec review passed [model]`, `- [ ] Code implemented [model]`, `- [ ] Self code review passed [model]`, `- [ ] Design documents updated [model]`.
- User-confirmed status lines (Spec review passed, Code review passed) remain plain checkboxes.
- Subtask file template has a `Status:` line immediately after the title: `Status: Not implemented | model: {model}`.
- Steps 2 and 5 executor instructions require the sub-agent prompt to include: "Start your response with `My model: {model-name}`." The parent agent reads the first line and uses that name when filling the overview status line.
- Step 4 executor instructions require the same sub-agent prompt for each step sub-agent. The coordinator fills the overview `Code implemented [model]` line with its own model; the coordinator fills each subtask `Status: Done | model: {model}` line with that sub-agent's model name read from its first response line.
- Step 1 and Step 7 arrow lines carry a model-recording reminder (no sub-agent — same agent fills in its own model).
- Step 4 instructions state: when renaming a subtask to `_DONE_`, also set `Status: Done | model: {model}` in that subtask file.
- `extsrc/skills/spectask-create.md` gains a hint: when launching the Step 2 sub-agent, include `"Start your response with My model: {model-name}"` in the prompt.
- `extsrc/skills/spectask-execute.md` gains a hint: when launching sub-agents in Steps 4 and 5, include `"Start your response with My model: {model-name}"` in the prompt.

## Details

Textual edits to `extsrc/files/spec/main.md`, its locally active mirror `spec/main.md`, and two skill files. No code, no config, no other files.

Specific changes:

1. Overview template Status block: add `[model]` suffix to five agent-executed lines:
   - `- [ ] Spec created` → `- [ ] Spec created [model]`
   - `- [ ] Self spec review passed` → `- [ ] Self spec review passed [model]`
   - `- [ ] Code implemented` → `- [ ] Code implemented [model]`
   - `- [ ] Self code review passed` → `- [ ] Self code review passed [model]`
   - `- [ ] Design documents updated` → `- [ ] Design documents updated [model]`
   User-confirmed lines (Spec review passed, Code review passed) are left as plain checkboxes.

2. Subtask file template: add immediately after `# Step {N}: {Short title}`:
   ```
   Status: Not implemented | model: {model}
   ```

3. Step 1 arrow line: append model-recording instruction (same agent, no sub-agent).
4. Step 2 executor block: add sub-agent prompt requirement to start response with `My model: {model-name}`; add parent-agent instruction to extract and fill that name in the status line.
5. Step 4 executor block: same sub-agent prompt requirement for each step sub-agent; add parent-agent instruction to extract model per sub-agent and fill into that subtask's `Status:` line; coordinator fills its own model on the overview `Code implemented` status line.
6. Step 5 executor block: same sub-agent prompt requirement; parent fills status line.
7. Step 7 arrow line: append model-recording instruction (same agent, no sub-agent).

After editing `extsrc/files/spec/main.md`, also update `spec/main.md` at the repo root to match (that file is the locally active copy).

8. `extsrc/skills/spectask-create.md`: append a hint about the `My model:` sub-agent prompt requirement for Step 2.
9. `extsrc/skills/spectask-execute.md`: append a hint about the `My model:` sub-agent prompt requirement for Steps 4 and 5.

## Execution Scheme
> Each step id is the subtask filename (e.g. `1-abstractions`).
> MANDATORY! Each step is executed by a dedicated subagent (Task tool). Do NOT implement inline. No exceptions -- even if a step seems trivial or small.
> Note: single-step decomposition; Execution Scheme is kept to enforce the subagent mandate (Step 4 rule 2).
- Phase 1 (sequential): step 1-update-main-md
