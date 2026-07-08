# Step 1: MCP transport uvx

Status: Done | model: composer-2.5-fast

## Goal
Point all three Spawn MCP platform descriptors at `uvx spectask-mcp serve` with identical server names and transport shape.

## Approach
Edit `transport.command` and `transport.args` only; keep `servers[0].name` (`spectask-mcp-jira`) and `transport.type` (`stdio`) unchanged. Apply the same payload to `windows.json`, `linux.json`, and `macos.json` (homogeneous setup per spawn-ext-mcp skill). Run `spawn extension check .` after edits.

## Affected files
- `extsrc/mcp/windows.json` — `servers[0].transport`
- `extsrc/mcp/linux.json` — `servers[0].transport`
- `extsrc/mcp/macos.json` — `servers[0].transport`

## Code changes (before / after)

### `extsrc/mcp/windows.json` — `servers[0].transport.command` / `args`

**Before**
```json
"transport": {
  "type": "stdio",
  "command": "spectask-mcp",
  "args": ["serve"]
}
```
Spawns the `spectask-mcp` console script from PATH.

**After**
```json
"transport": {
  "type": "stdio",
  "command": "uvx",
  "args": ["spectask-mcp", "serve"]
}
```
Spawns `uvx`, which resolves and runs the latest `spectask-mcp` PyPI entry with subcommand `serve`.

### `extsrc/mcp/linux.json` — `servers[0].transport.command` / `args`

**Before**
```json
"transport": {
  "type": "stdio",
  "command": "spectask-mcp",
  "args": ["serve"]
}
```
Same direct console-script launch as Windows/macOS today.

**After**
```json
"transport": {
  "type": "stdio",
  "command": "uvx",
  "args": ["spectask-mcp", "serve"]
}
```
Same uvx launch as Windows/macOS after this step.

### `extsrc/mcp/macos.json` — `servers[0].transport.command` / `args`

**Before**
```json
"transport": {
  "type": "stdio",
  "command": "spectask-mcp",
  "args": ["serve"]
}
```
Same direct console-script launch as other platforms today.

**After**
```json
"transport": {
  "type": "stdio",
  "command": "uvx",
  "args": ["spectask-mcp", "serve"]
}
```
Same uvx launch as other platforms after this step.

## Additional actions
- Run `spawn extension check .` and fix any reported MCP JSON issues.
