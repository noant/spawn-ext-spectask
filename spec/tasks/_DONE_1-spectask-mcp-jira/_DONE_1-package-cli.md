# Step 1: Package scaffold and CLI entry

## Goal
Add repo-root packaging for `spectask-mcp` and a `spectask-mcp` console script delegating to subcommand stubs (`interactive`, `run`, `serve`).

## Approach
Create `pyproject.toml` using setuptools (or hatchling) compatible with `uv build`; add package `spectask_mcp/` with `cli.main()` wired through `Typer` or `argparse` (match minimal deps). Stub handlers call `sys.exit('not implemented')` or trivial placeholder until later steps replace them. Declare Python 3.11+.

## Affected files
- `pyproject.toml` (new)
- `spectask_mcp/__init__.py` (new)
- `spectask_mcp/__main__.py` (new, optional `python -m spectask_mcp`)
- `spectask_mcp/cli.py` (new, `main` function entry)

## Code changes (before / after)

### `pyproject.toml` — root project metadata (new file)

**Before**
```text
(file absent)
```
No Python packaging at repo root yet.

**After**
```toml
[project]
name = "spectask-mcp"
version = "0.1.0"
description = "Stdio MCP and CLI for Spectask-Jira workflows"
requires-python = ">=3.11"
dependencies = [
  "mcp>=1.2.0",
  "httpx[socks]>=0.27.0",
  "PyYAML>=6.0.1",
]

[project.scripts]
spectask-mcp = "spectask_mcp.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["spectask_mcp"]
```
Pins may float at implementation time; declares script entrypoint and hatchling wheel for `spectask_mcp/` package dir.

Behavior: `uv pip install -e .` / PyPI installs expose executable `spectask-mcp`; `uv build` produces artifacts.

### `spectask_mcp/cli.py` — `main()` and argparse subcommands (new file)

**Before**
```python
(file absent)
```

**After**
```python
"""CLI entry for spectask-mcp."""

from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> None:
    argv = argv if argv is not None else sys.argv[1:]
    p = argparse.ArgumentParser(prog="spectask-mcp")
    sub = p.add_subparsers(dest="cmd", required=True)

    p_int = sub.add_parser("interactive", help="Write spec/.config/config.yaml via prompts")
    p_int.add_argument(
        "--setup",
        action="store_true",
        help="Called from extension setup: ask whether to configure before the wizard",
    )
    p_run = sub.add_parser("run", help="Fetch Jira issue or list open issues once")
    p_run.add_argument("--issue", default=None, help="Jira issue key, e.g. PROJ-123")
    sub.add_parser("serve", help="Run stdio MCP server")

    ns = p.parse_args(argv)

    if ns.cmd == "interactive":
        from spectask_mcp.config_prompts import run_interactive
        raise SystemExit(run_interactive(prompted_by_setup=ns.setup))

    if ns.cmd == "run":
        from spectask_mcp.run_cmd import run_once
        raise SystemExit(run_once(issue_key=ns.issue))

    if ns.cmd == "serve":
        from spectask_mcp.mcp_app import run_stdio
        raise SystemExit(run_stdio())


if __name__ == "__main__":
    main()
```
Behavior: dispatches three subcommands; **`interactive`** accepts **`--setup`** for extension installs; imports deferred until handler runs.

### `spectask_mcp/__init__.py` — package marker (new file)

**Before**
```python
(file absent)
```

**After**
```python
"""spectask-mcp distribution package."""
```
Behavior: declares namespace for imports.

### `spectask_mcp/__main__.py` — `python -m spectask_mcp` (new file)

**Before**
```python
(file absent)
```

**After**
```python
from spectask_mcp.cli import main

if __name__ == "__main__":
    main()
```
Behavior: allows `python -m spectask_mcp serve` style invocations without console script on PATH.

## Additional actions
- Omit PEP 621 `readme` key unless Hatch requires one; avoid adding unsolicited root README.
