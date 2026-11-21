# Step 1: Rotation script

Status: Done
Suggested model: glm-5.3-flash
Used model: glm-5.3-flash

## Goal
Create `spec/scripts/rotate_history.py` (repo copy) and its identical extension template `extsrc/files/spec/scripts/rotate_history.py`.

## Approach
Stdlib-only, Python >= 3.11, style of `scripts/publish.py` (shebang, module docstring with Usage, typed signatures). Default applies rotation; `--dry-run` prints only. Verify with `--dry-run` against the real `spec/tasks/` (expect 5 moves: codes 1, 2, 3, 5, 6) and a temporary sandbox for the applying run — do NOT apply the real rotation yet (Step 8 of THIS task will trigger it naturally at close, or the user runs it manually).

## Affected files
- `spec/scripts/rotate_history.py` — new; `main()`, `_done_code(name) -> int | None`, `plan_rotation(tasks_dir: Path, keep: int = 10) -> list[tuple[Path, Path]]`
- `extsrc/files/spec/scripts/rotate_history.py` — new; byte-identical template copy

## Code changes (before / after)

### `spec/scripts/rotate_history.py` — new file (R9-greenfield)

**Before**
```code
(no file; spec/scripts/ does not exist)
```
No rotation mechanism; `_DONE_*` folders accumulate in `spec/tasks/`.

**After**
```python
#!/usr/bin/env python3
"""Rotate done spec task folders into spec/tasks/__history/.

Keeps the newest KEEP done folders (by numeric task code) in spec/tasks/
and moves older ones into spec/tasks/__history/.

Usage:
    py spec/scripts/rotate_history.py            # Windows, apply
    python3 spec/scripts/rotate_history.py       # Linux/macOS, apply
    python3 spec/scripts/rotate_history.py --dry-run
"""
from __future__ import annotations

import argparse
import re
import shutil
import sys
from pathlib import Path

_KEEP = 10
_DONE_CODE_RE = re.compile(r"^_DONE_(\d+)-")


def _done_code(name: str) -> int | None:
    """Return the numeric task code of a done folder name, or None."""
    match = _DONE_CODE_RE.match(name)
    return int(match.group(1)) if match else None


def plan_rotation(tasks_dir: Path, keep: int = _KEEP) -> list[tuple[Path, Path]]:
    """Return (src, dst) pairs for done folders older than the newest `keep`."""
    if not tasks_dir.is_dir():
        return []
    done = [
        (code, entry)
        for entry in tasks_dir.iterdir()
        if entry.is_dir() and (code := _done_code(entry.name)) is not None
    ]
    done.sort(key=lambda pair: pair[0], reverse=True)
    history = tasks_dir / "__history"
    return [
        (entry, history / entry.name)
        for _, entry in done[keep:]
    ]


def main(argv: list[str] | None = None) -> int:
    """Apply the rotation; return 0 (warnings are non-fatal)."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="print the plan without moving")
    args = parser.parse_args(argv)
    tasks_dir = Path(__file__).resolve().parents[1] / "tasks"
    moves = plan_rotation(tasks_dir)
    if not moves:
        print("nothing to rotate")
        return 0
    for src, dst in moves:
        if dst.exists():
            print(f"skip (exists): {dst}")
            continue
        print(f"{src} -> {dst}")
        if not args.dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```
Behavior: newest 10 numeric `_DONE_*` stay; older ones move into `spec/tasks/__history/`; a missing `spec/tasks/`, destination conflicts, and tracker-coded folders are skipped safely; `--dry-run` prints the plan without moving; exit code is always 0.

### `extsrc/files/spec/scripts/rotate_history.py` — new template
**Before**
```code
(no file)
```
**After**
```code
(byte-identical copy of spec/scripts/rotate_history.py)
```
Extension template so `spawn extension add` / `spawn refresh` deploys the script to consumer repos.

## Additional actions
- `python3 spec/scripts/rotate_history.py --dry-run` must list exactly 5 moves (codes 1, 2, 3, 5, 6) while task 17 is still open. The first real Step-8 run (after `spec/tasks/_DONE_17-task-history-rotation/` appears) will move 6 folders (codes 1, 2, 3, 5, 6, 7).
- Sandbox check: copy `spec/tasks` and the script into a temp dir preserving `spec/scripts/` + `spec/tasks/` layout, run the script there, confirm moves and an idempotent second run (nothing to rotate). Do NOT apply the real rotation during implementation.
