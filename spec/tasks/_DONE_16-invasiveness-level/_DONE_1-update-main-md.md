# Step 1: Update extsrc/files/spec/main.md

Status: Done
Suggested model: deepseek-v4-flash
Used model: deepseek-v4-pro-a

## Goal
Add the invasiveness-level clarification to Step 2.2 and the `## Invasiveness level` field to the `overview.md` template in `extsrc/files/spec/main.md`.

## Approach
1. Open `extsrc/files/spec/main.md`.
2. Apply Edit 1 (Step 2.2 block) and Edit 2 (overview.md template) below.
3. Verify no other lines were accidentally changed.
4. Do not edit `spec/main.md` or `spawn/.extend/spectask/files/spec/main.md` directly — those are regenerated from the source.

## Affected files
- `extsrc/files/spec/main.md`

## Code changes (before / after)

### Edit 1 — Step 2.2 "Implementation clarifications" block

Insert the invasiveness-level question as a new bullet immediately after the motivation bullet (`- Put the chosen motivation in **`## Motivation`** (after **Goal**).`), i.e. as the last bullet of Step 2.2. All existing bullets are preserved unchanged.

**Before**
```markdown
- Put the chosen motivation in **`## Motivation`** (after **Goal**).
```
The last bullet of Step 2.2; no edit-scope question exists.

**After**
```markdown
- Put the chosen motivation in **`## Motivation`** (after **Goal**).
- Ask the user to choose an **invasiveness level** (`R10-ask`, multiple choice) — the edit scope the spec must respect:
  - **minimally-invasive** — edits confined to a single layer or library; all other layers/libraries are left untouched, even if the solution is a workaround (crutch).
  - **medium-invasive** — edits may span several adjacent layers or domains, e.g. backend + frontend, or domain1 + domain2.
  - **maximally-invasive** — edits may span all layers and all domains; the LLM follows the principle of deep rework over a superficial fix with compromises.
- Record the chosen level in **`## Invasiveness level`** (after **`## Motivation`**). Every affected file/symbol in the spec must stay within the chosen scope.
```
Appends the invasiveness-level question and recording instruction as the final bullets of Step 2.2.

### Edit 2 — overview.md template, new field after `## Motivation`

**Before**
```markdown
## Motivation
{Why this change — from the user request, or from the clarification answer.}

## Research summary
```
No field records the chosen edit scope.

**After**
```markdown
## Motivation
{Why this change — from the user request, or from the clarification answer.}

## Invasiveness level
{minimally-invasive | medium-invasive | maximally-invasive — chosen in Step 2.2; constrains the edit scope of the spec.}

## Research summary
```
Adds a field recording the chosen invasiveness level.

## Additional actions
None.
