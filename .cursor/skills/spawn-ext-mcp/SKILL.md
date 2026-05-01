---
name: spawn-ext-mcp
description: Add extsrc/mcp.json using Spawn servers format and safe env placeholders.
---


Goal: declare MCP servers bundled with the extension.

1. Create or edit `extsrc/mcp.json` as valid JSON with top-level `servers` array (not IDE-native `mcpServers` shape).
2. Each server MUST have a unique `name` across every extension in the same target — use a prefixed id.
3. Configure `transport`: default mindset `stdio` with `command`/`args`/`cwd`; remote servers use `type` and `url` per adapter support.
4. Secrets: never commit real tokens; use structured `env` objects with `secret`/`required` or placeholders — generated IDE config uses placeholders for user-supplied values.
5. Set `capabilities` when defaults (tools on, resources/prompts off) are wrong for the server.
6. Run `spawn extension check .` for JSON parse; fix adapter/runtime issues when integrating in the IDE.
7. **Version:** Changing **`servers`**, transports, env contract, or capabilities changes bundled MCP behavior — **prompt** the author to bump **`version`** via **`spawn-ext-increment-version`** before publishing.


Mandatory reads:
- `spawn-ext-guide/ai/core.md` - Machine baseline — terms, extsrc tree rules, static vs artifact, name and uniqueness, install outputs.
- `spawn-ext-guide/ai/mcp-json.md` - Machine schema for extsrc/mcp.json — servers, transport, env, capabilities, JSON examples.
- `spawn/navigation.yaml` - Merged Spawn navigation (read-required, read-contextual).

Contextual reads:
- `spawn-ext-guide/ai/config-yaml.md` - Machine schema for config.yaml — keys, files/folders/skills modes, reads, ignores, setup, annotated example.
- `spawn-ext-guide/ai/skill-sources.md` - Machine rules for extsrc/skills/*.md — frontmatter, name/description resolution, rendered skill shape, example.
- `spawn-ext-guide/ai/cli.md` - Machine CLI reference — spawn init/extension/build commands, extensions.yaml bundle shape, authoring checklist.
