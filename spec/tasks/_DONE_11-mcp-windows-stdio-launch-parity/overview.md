# 11: Windows MCP stdio launch parity (fix missing jira module)

## Source seed
- Path: none

## Status
- [x] Spec created
- [x] Self spec review passed
- [x] Spec review passed
- [x] Code implemented
- [x] Self code review passed
- [x] Code review passed
- [x] Design documents updated

## Goal
Make the Windows Spawn MCP server start the same way as Linux and macOS so the process runs with project dependencies (including `jira`) rather than a bare `python` that may lack them.

## Design overview
- Affected modules: Spawn extension MCP transport config only (no Python package logic change required for the primary fix).
- Files and symbols: `extsrc/mcp/windows.json` — JSON `servers[0].transport.command` and `args` for server `spectask-mcp-jira`. Reference consumers (unchanged): `spectask_mcp/jira/http_cloud.py` (`from jira import JIRA`), `spectask_mcp/jira/http_self_hosted.py`, `spectask_mcp/jira/http_common.py`, `spectask_mcp/jira/pycontribs_factory.py` — all require the third-party `jira` distribution at import time; `spectask_mcp/mcp_app.py` imports Jira stack transitively.
- Data flow changes: Stdio MCP client still spawns a process and sends JSON-RPC over stdin/stdout; only the executable and argv change on Windows.
- Integration points: Cursor/Spawn reads materialized `extsrc/mcp/windows.json`; after-install script `extsrc/setup/install_spectask_mcp.py` already runs `uv tool install` / `uv tool upgrade` for `spectask-mcp`, which places the `spectask-mcp` console script on PATH when that workflow is used.

## Before → After
### Before
- Windows MCP uses `python -m spectask_mcp serve`, which resolves to whatever `python` is on PATH. If that interpreter does not have the wheel/editable install with `pyproject.toml` dependencies, import of `spectask_mcp.jira.http_cloud` fails with `ModuleNotFoundError: No module named 'jira'` (failure seen when connecting MCP on Windows).

### After
- Windows MCP uses the same entry as Linux/macOS: `spectask-mcp serve`, so the launched process matches the installed package environment (typically from `uv tool install spectask-mcp` or a venv where `pip install -e .` created the `spectask-mcp` script).

## Details

**Clarifications (Step 1.1 defaults):**
- Primary fix is config parity across platforms, not adding a new dependency ( `jira>=3.10.0` is already in `pyproject.toml` ).
- Developers who never install the console script must override MCP command locally (for example full path to `.venv\Scripts\spectask-mcp.exe` on Windows or `python -m spectask_mcp serve` with an interpreter that has `pip install -e .` applied); that is out of scope for the packaged `windows.json` change.

**Reference — other platforms (no edit in this task):**

`extsrc/mcp/linux.json` and `extsrc/mcp/macos.json` already use:

```json
"command": "spectask-mcp",
"args": ["serve"]
```

**Code change — Windows only:**

`extsrc/mcp/windows.json`

**Before**

```json
"command": "python",
"args": ["-m", "spectask_mcp", "serve"]
```

**After**

```json
"command": "spectask-mcp",
"args": ["serve"]
```

Full-file shape stays: one server named `spectask-mcp-jira`, `transport.type` `stdio`, only `command` / `args` updated as above.

**Verification after implementation:**
- From a shell where `spectask-mcp` resolves after install: run `spectask-mcp serve` and confirm process stays up (no immediate import traceback).
- Optional: `python -c "import spectask_mcp.mcp_app"` using the same environment the user relies on for MCP.
