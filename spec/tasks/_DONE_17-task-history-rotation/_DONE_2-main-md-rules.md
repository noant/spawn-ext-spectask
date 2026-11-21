# Step 2: spec/main.md rules and Step 8 action

Status: Done
Suggested model: glm-5.3-flash
Used model: glm-5.3-flash

## Goal
Document `spec/scripts/` and `spec/tasks/__history/` in `spec/main.md` (Folder Structure) and add the brief post-close rotation action to Step 8 — in BOTH copies: `spec/main.md` and `extsrc/files/spec/main.md`.

## Approach
Minimal wording only. Two small edits, mirrored into the extension template. `R3-code-num` stays unchanged.

## Affected files
- `spec/main.md` — Folder Structure list, Step 8 bullet list
- `extsrc/files/spec/main.md` — identical edits (template twin)

## Code changes (before / after)

### `spec/main.md` — Folder Structure (after the `spec/seeds/` line)

**Before**
```markdown
- spec/seeds/{X}-{slug}.md — seed file (artifact tree in this methodology pack).
```
Last Folder Structure entry; no script or history paths documented.

**After**
```markdown
- spec/seeds/{X}-{slug}.md — seed file (artifact tree in this methodology pack).
- spec/scripts/ — helper scripts shipped with the methodology pack.
- spec/tasks/__history/ — archived `_DONE_*` task folders (see Step 8); agent-ignored.
```
Documents the two new paths so `R1-paths` permits them.

### `spec/main.md` — Step 8 (insert after the seed-rename bullet)

**Before**
```markdown
- if the Source seed Path in the overview is concrete and the listed spec/seeds file is linked to this overview, rename it once with _DONE_ added
- set [V] "Design document update" — fill the model name in brackets: `- [V] Design document update [model-name]`
```
Close sequence: rename folder, rename seed, mark status.

**After**
```markdown
- if the Source seed Path in the overview is concrete and the listed spec/seeds file is linked to this overview, rename it once with _DONE_ added
- run the history rotation (moves `_DONE_*` folders older than the newest 10 into `spec/tasks/__history/`):
  - Windows: `py spec/scripts/rotate_history.py`
  - Linux/macOS: `python3 spec/scripts/rotate_history.py`
- set [V] "Design document update" — fill the model name in brackets: `- [V] Design document update [model-name]`
```
After each task close the agent rotates done tasks automatically; no new status step.

### `extsrc/files/spec/main.md` — same two edits
**Before**
```markdown
(the corresponding template sections; note: the template is already AHEAD of spec/main.md — it contains `R24-review-no-fix` and fallback-model wording that the repo copy lacks)
```
**After**
```markdown
(template sections with exactly the same two edits applied; pre-existing divergence untouched)
```
Both copies get the same two edits; existing divergence (template ahead) is out of scope.

## Additional actions
- Verify each of the two edits exists in both files (grep the added lines); full-file diff equality is NOT expected — the template is already ahead of the repo copy.
