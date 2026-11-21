# 17: Task history rotation

## Source seed
- Path: none

## Status
- [V] Research [glm-5.3-flash]
- [V] User research review
- [V] Spec drafting [glm-5.3]
- [V] Spec self-review [glm-5.3 + deepseek-v4-pro]
- [V] Spec review
- [V] Code implementation [glm-5.3]
- [V] Code self-review [glm-5.3 + deepseek-v4-pro]
- [V] Code review / debugging
- [V] Design document update [glm-5.3]

## Goal
Add a Python rotation script that moves all but the newest 10 done task folders into `spec/tasks/__history/`, run automatically by the agent right after task close (Step 8), with the history folder added to the extension's agent-ignore.

## Motivation
Reliability / ops + tech debt: `spec/tasks/` accumulates `_DONE_*` folders (15 already), inflating agent context; rotation keeps only the newest 10 visible while old tasks stay in git history folder.

## Invasiveness level
maximally-invasive

## Review models
- Research review: single agent: glm-5.3
- Spec review: cross-review: glm-5.3, deepseek-v4-pro
- Code review: cross-review: glm-5.3, deepseek-v4-pro

## Run mode
interactive

## Research summary
- `spec/main.md` edit points: Folder Structure (L3-16), Step 8 (insert rotation action after seed-rename line L486). `R3-code-num` unchanged.
- `.cursorignore` / `.gitignore` are generated; source of truth is `extsrc/config.yaml` (`agent-ignore` L17-20, `git-ignore` L22-23). After ignore/`files:` changes: bump `version` via `spawn-ext-increment-version` and run `spawn refresh` (`spawn-ext-guide/ai/cli.md` L62-64).
- Extension templates live under `extsrc/files/`; `spec/main.md` has a template twin `extsrc/files/spec/main.md` — the template is currently AHEAD of the repo copy (contains `R24-review-no-fix`); the task applies its edits to both, without syncing the pre-existing divergence.
- Script conventions from `scripts/publish.py`: Python >= 3.11, stdlib-only, shebang, typed signatures, module constants in `_UPPER_SNAKE`.
- Done folders: `_DONE_{code}-{slug}`, 15 exist, numeric codes with gaps; mtime unreliable (checkout resets it) — "newest" = highest numeric code. Non-numeric (tracker, `R4-code-tracker`) codes are never moved.
- Decision (user): agent-ignore only; `spec/tasks/__history/` stays tracked in git.
- Decision (user): script applies rotation by default; `--dry-run` only prints.
- Decision (user, refined): `R3-code-num` stays unchanged — the highest code is always among the newest 10 kept in `spec/tasks/`, so rotation cannot cause number reuse.

## Design overview
- Affected modules: spec methodology docs (`spec/main.md` + template twin), extension packaging (`extsrc/config.yaml`), new script `spec/scripts/rotate_history.py` (+ template under `extsrc/files/`).
- Files & symbols: `spec/scripts/rotate_history.py` (new; functions `main()`, `_done_code(name) -> int | None`, `plan_rotation(tasks_dir) -> list[tuple[Path, Path]]`), `extsrc/files/spec/scripts/rotate_history.py` (identical template), `spec/main.md` (Folder Structure, Step 8), `extsrc/files/spec/main.md` (same edits), `extsrc/config.yaml` (`agent-ignore`, `files`, `version`).
- Data flow changes: on task close the agent runs the script; it scans `spec/tasks/`, keeps the 10 `_DONE_*` folders with the highest numeric codes, moves the rest into `spec/tasks/__history/` (folder moves, names preserved).
- Integration points: Step 8 of `spec/main.md` (agent action, no new status); Spawn extension ignore mechanism (`agent-ignore` glob `spec/tasks/__history/**`); extension refresh regenerates `.cursorignore`/`.gitignore`.

## Before → After
### Before
- 15 `_DONE_*` folders sit directly in `spec/tasks/`; nothing rotates them; `spec/scripts/` does not exist; `agent-ignore` has no `__history` entry.
### After
- `spec/scripts/rotate_history.py` exists (repo + extension template); after each task close the agent runs it; `spec/tasks/` holds at most 10 newest `_DONE_*` folders; older ones live in `spec/tasks/__history/` (agent-ignored, git-tracked); `spec/main.md` documents the paths and the one-line action with `py` / `python3` examples.

## Details
- Script behavior:
  - Locate `spec/tasks` relative to the script file (`Path(__file__).resolve().parents[1] / "tasks"`), so it works from any CWD.
  - Select `_DONE_*` folders whose name matches `_DONE_(\d+)-` (numeric codes only); sort by `int(code)` descending; keep the first 10; move the rest to `spec/tasks/__history/` (created on demand).
  - If a destination name already exists in `__history/`, print a warning and skip that folder (never overwrite); exit code stays 0.
  - Fewer than 11 candidates: print nothing to move, exit 0.
  - Default applies moves (prints each `src -> dst`); `--dry-run` prints the plan without moving.
  - Tracker-coded done folders (`_DONE_PROJ-123-*`) are ignored by the rotation.
- `spec/main.md` wording must be minimal: one Folder Structure bullet pair, one Step 8 action line with both command examples:
  - `py spec/scripts/rotate_history.py` (Windows)
  - `python3 spec/scripts/rotate_history.py` (Linux/macOS)
- Extension packaging: add `spec/scripts/rotate_history.py` to `extsrc/config.yaml` `files:` (mode `static`, `globalRead: no`, `localRead: no` — script is executed, not read; short description kept) and `spec/tasks/__history/**` to `agent-ignore`; bump `version`; run `spawn extension check . --strict`; verify `.cursorignore`/`.gitignore` regenerated (agent-ignore entry present, git-ignore unchanged).
- First run: `--dry-run` during implementation (task 17 still open) lists 5 moves (codes 1, 2, 3, 5, 6); the first real Step-8 run after `_DONE_17` appears moves 6 folders (adds code 7).

## Execution Scheme
Suggested coordinator model: glm-5.3
> Each step id is the subtask filename (e.g. `1-abstractions`).
> Each step is executed by a dedicated `A5-coder` subagent (see Step 5).
- Phase 1 (sequential): step 1-rotation-script → step 2-main-md-rules → step 3-ext-config-ignore
- Phase 2 (sequential): step review — inspect all changes, fix inconsistencies
