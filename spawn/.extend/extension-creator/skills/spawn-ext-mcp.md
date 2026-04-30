---
name: spawn-ext-mcp
description: Add or update extsrc/mcp.json with Spawn extension servers format and safe env handling.
---

Goal: declare MCP servers bundled with the extension.

1. Create or edit `extsrc/mcp.json` as valid JSON with top-level `servers` array (not IDE-native `mcpServers` shape).
2. Each server MUST have a unique `name` across every extension in the same target — use a prefixed id.
3. Configure `transport`: default mindset `stdio` with `command`/`args`/`cwd`; remote servers use `type` and `url` per adapter support.
4. Secrets: never commit real tokens; use structured `env` objects with `secret`/`required` or placeholders — generated IDE config uses placeholders for user-supplied values.
5. Set `capabilities` when defaults (tools on, resources/prompts off) are wrong for the server.
6. Run `spawn extension check .` for JSON parse; fix adapter/runtime issues when integrating in the IDE.
7. **Version:** Changing **`servers`**, transports, env contract, or capabilities changes bundled MCP behavior — **prompt** the author to bump **`version`** via **`spawn-ext-increment-version`** before publishing.
