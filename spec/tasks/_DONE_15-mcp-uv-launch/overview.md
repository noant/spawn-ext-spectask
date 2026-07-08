# 15: MCP launch via uvx (always latest PyPI)

## Source seed
- Path: none

## Status
- [V] Spec created [claude-4.6-sonnet-medium]
- [V] Self spec review passed [claude-4.6-sonnet-medium]
- [V] Spec review passed
- [V] Code implemented [composer-2.5-fast]
- [V] Self code review passed [composer-2.5-fast]
- [V] Code review passed
- [V] Design documents updated [claude-4.6-sonnet-medium]

## Goal
Run the bundled MCP server through `uvx spectask-mcp serve` so each IDE session resolves the latest PyPI release while the after-install hook keeps `uv tool install` / `uv tool upgrade` for CLI and interactive setup.

## Design overview
- Affected modules: Spawn extension MCP transport descriptors and user-facing install docs only; no Python package code changes. Step 7 updates `spec/design/hla.md` MCP launch paragraph.
- Files and symbols (concrete paths; class / method / function / module names to touch):
  - `extsrc/mcp/windows.json`, `extsrc/mcp/linux.json`, `extsrc/mcp/macos.json` — JSON `servers[0].name` (`spectask-mcp-jira`), `servers[0].transport.command`, `servers[0].transport.args`.
  - `README.md` — Jira integration and MCP section (stdio launch description).
  - `extsrc/config.yaml` — top-level `version` (consumer-visible MCP transport change).
  - Unchanged: `extsrc/setup/install_spectask_mcp.py` (`main`, `_run_uv_best_effort`, `_run_interactive_setup`) continues `uv tool install` / `uv tool upgrade` and `spectask-mcp interactive --setup`.
  - Step 7: `spec/design/hla.md` and `extsrc/files/spec/design/hla.md` — final paragraph (Spawn MCP stdio launch via `uvx`, separate from `uv tool` CLI install).
  - Out of scope: `.cursor/mcp.json` (repo dev override stays as-is).
- Data flow changes: IDE still spawns a stdio child process; executable becomes `uvx` with argv `spectask-mcp serve` instead of `spectask-mcp serve`. `uvx` fetches or reuses cached PyPI metadata for `spectask-mcp` on each MCP start. MCP may run a newer PyPI build than the `uv tool`-installed CLI until the user re-runs after-install or upgrades the tool copy.
- Integration points: Spawn merges `extsrc/mcp/*.json` per host OS; Cursor and other adapters materialize `command` / `args`; users must have `uv` on PATH (already documented for Spawn CLI install).

## Before → After
### Before
- All three platform MCP files launch `spectask-mcp serve` directly, using whatever console script version is on PATH (from a prior `uv tool install` or local venv). Stale installs can run until the user re-runs extension setup or upgrades manually.

### After
- All three platform MCP files launch `uvx spectask-mcp serve`, so MCP starts through uv's ephemeral runner and picks up the latest published `spectask-mcp` (subject to uv cache). After-install still installs/upgrades the `uv tool` copy for CLI (`spectask-mcp run`, `spectask-mcp interactive`).

## Details

**Clarifications (Step 1.1, user-confirmed):**
- Task code: `15-mcp-uv-launch`.
- UV mode: `uvx spectask-mcp serve` (not `uv tool run`).
- After-install: keep `uv tool install` / `uv tool upgrade` in `install_spectask_mcp.py`; MCP path is separate.
- Dev config: do not edit `.cursor/mcp.json`.
- Prerequisite: `uv` on PATH (same as README Spawn install section).

**Reference — spawn-ext-guide `uv_wrapper_fragment` pattern:** stdio `command` is the runner (`uvx` here), `args` carry the package entry and subcommand.

**Step 7 — `spec/design/hla.md` and `extsrc/files/spec/design/hla.md` (after code review, not in Execution Scheme subtasks):**

**Before**
```markdown
Spawn ships stdio MCP descriptors under `extsrc/mcp/` (`windows.json`, `linux.json`, `macos.json`) for server `spectask-mcp-jira`. Each platform runs `spectask-mcp serve` so the MCP process uses the same installed package and third-party dependencies (for example pycontribs `jira`) as the CLI entry point.
```
Implies MCP and CLI share one installed package on PATH.

**After**
```markdown
Spawn ships stdio MCP descriptors under `extsrc/mcp/` (`windows.json`, `linux.json`, `macos.json`) for server `spectask-mcp-jira`. Each platform runs `uvx spectask-mcp serve` so MCP resolves the latest PyPI release on start (requires `uv` on PATH). The after-install hook still runs `uv tool install` / `uv tool upgrade` for CLI commands (`spectask-mcp run`, `spectask-mcp interactive`); MCP and CLI may run different package versions until the user upgrades the tool.
```
Documents uvx MCP launch and split from CLI tool install.

**Verification after implementation:**
- With `uv` on PATH: `uvx spectask-mcp serve` stays up (no immediate import traceback).
- `spawn extension check .` passes (matching server names across three MCP JSON files).
- README MCP paragraph describes `uvx` launch and `uv` prerequisite.

## Execution Scheme
> Each step id is the subtask filename (e.g. `1-abstractions`).
> MANDATORY! Each step is executed by a dedicated subagent (Task tool). Do NOT implement inline. No exceptions — even if a step seems trivial or small.
- Phase 1 (sequential): step 1-mcp-transport-uvx → step 2-readme-extension-version
