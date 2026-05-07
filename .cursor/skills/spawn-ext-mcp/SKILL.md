---
name: spawn-ext-mcp
description: Add or edit extsrc/mcp/*.json — three platform files, Spawn servers shape, matching server names, safe env placeholders.
---


Goal: declare MCP servers bundled with the extension so Spawn merges them per host OS into IDE configs.

### Layout

- Use **`extsrc/mcp/windows.json`**, **`extsrc/mcp/linux.json`**, **`extsrc/mcp/macos.json`** only (`spawn extension init` scaffolds all three as `{"servers": []}`).
- **Do not** add **`extsrc/mcp.json`** — obsolete; **`spawn extension check`** flags it.

### Editing workflow (add or change servers)

1. **Plan globally unique **`servers[].name`** values** across every extension that might install beside this one in the same target (prefer prefixed ids, e.g. `myorg-docs-mcp`).
2. **Keep the server `name` set identical** in all three JSON files (same names; order may differ per file).
3. For each OS file, edit the **`servers`** array with the Spawn shape: top-level **`servers`** — not IDE **`mcpServers`**.
4. **`transport`**: default mental model **`stdio`** with **`command`** / **`args`** / **`cwd`**; **`sse`** / **`streamable-http`** use **`url`** where the adapter supports that **`type`**.
5. **`env`**: never commit secrets; structured objects with **`secret`** / **`required`**, or non-object placeholders — generated IDE config uses placeholders for user values.
6. **`capabilities`**: set when defaults (tools on, resources/prompts off) are wrong for the server.
7. When transport truly differs by OS (e.g. **`python`** vs **`python3`**, or Windows-specific exe), duplicate the server **`name`** in each file but adjust only **`transport`** (and **`env`** if needed) per platform.
8. **Homogeneous setups:** duplicate the **same** JSON payload into **`windows.json`**, **`linux.json`**, and **`macos.json`** if all three match — still three files required.
9. Run **`spawn extension check .`** (`--strict` in CI): parsing, stray obsolete **`extsrc/mcp.json`**, and **matching `name`** sets across **`extsrc/mcp/*.json`**.

### Release discipline

Changing **`servers`**, transports, **`env`** contract, or **`capabilities`** is consumer-visible MCP behavior — **prompt** the author to bump **`version`** via **`spawn-ext-increment-version`** before publishing.


Hints:
- No emojis or exotic Unicode in code, logs, documentation, or messages; plain ASCII where practical.
- User-facing replies, documentation, and task descriptions: concise wording; minimal markdown (avoid decorative bold/italic); explain with lists and structure; short, clear sentences.
- If the user only asked a question, answer first; do not edit files unless changes are clearly needed.

Mandatory reads:
- `spawn-ext-guide/ai/core.md` - Machine baseline — terms, extsrc tree rules, static vs artifact, name and uniqueness, install outputs.
- `spawn-ext-guide/ai/mcp-json.md` - Machine schema for extsrc/mcp/windows.json, linux.json, macos.json — servers, OS selection, aligned name sets, transport, env, capabilities, JSON examples.
- `spawn/navigation.yaml` - Merged Spawn navigation (read-required, read-contextual).

Contextual reads:
- `spawn-ext-guide/ai/config-yaml.md` - Machine schema for config.yaml — keys, files/folders/skills modes, reads, ignores, setup, annotated example.
- `spawn-ext-guide/ai/skill-sources.md` - Machine rules for extsrc/skills/*.md — frontmatter, name/description resolution, rendered skill shape, example.
- `spawn-ext-guide/ai/cli.md` - Machine CLI reference — spawn init/extension/build commands, extensions.yaml bundle shape, authoring checklist.
