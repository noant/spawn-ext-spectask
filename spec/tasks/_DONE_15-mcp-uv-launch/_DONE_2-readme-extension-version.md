# Step 2: README and extension version

Status: Done | model: composer-2.5-fast

## Goal
Document the uvx MCP launch in README and bump the extension pack version for the consumer-visible transport change.

## Approach
Update the Jira integration and MCP paragraph in README to describe `uvx spectask-mcp serve` and the `uv` prerequisite. Bump patch version in `extsrc/config.yaml` (currently `1.6.2` → `1.6.3`). Do not change `extsrc/setup/install_spectask_mcp.py`.

## Affected files
- `README.md` — Jira integration and MCP section
- `extsrc/config.yaml` — top-level `version` field

## Code changes (before / after)

### `README.md` — Jira integration and MCP launch sentence

**Before**
```markdown
This extension ships MCP server entries under `extsrc/mcp/` (per platform). After you install the pack with Spawn, those definitions are merged into your workspace; your IDE typically lists the **spectask-mcp-jira** server from that merge so you do not maintain a separate MCP JSON snippet for this tool. The server runs **spectask-mcp** in stdio mode (`spectask-mcp serve`). The same PyPI package also exposes a small **CLI** for non-MCP use.
```
States MCP uses the `spectask-mcp` console script directly.

**After**
```markdown
This extension ships MCP server entries under `extsrc/mcp/` (per platform). After you install the pack with Spawn, those definitions are merged into your workspace; your IDE typically lists the **spectask-mcp-jira** server from that merge so you do not maintain a separate MCP JSON snippet for this tool. The server runs **spectask-mcp** via **uvx** in stdio mode (`uvx spectask-mcp serve`), resolving the latest PyPI release on each MCP start; **uv** must be on PATH. The same PyPI package also exposes a small **CLI** for non-MCP use (`spectask-mcp run`, `spectask-mcp interactive`), installed by the after-install hook with `uv tool install` / `uv tool upgrade`.
```
Documents uvx MCP launch, uv prerequisite, and separates CLI tool install from MCP.

### `extsrc/config.yaml` — `version`

**Before**
```yaml
version: "1.6.2"
```
Current extension pack version before MCP transport change.

**After**
```yaml
version: "1.6.3"
```
Patch bump for consumer-visible MCP `command` / `args` change.

## Additional actions
- None.
