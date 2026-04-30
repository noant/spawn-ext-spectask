---
name: spawn-ext-verify
description: Strict check extension layout and smoke-test install in a disposable target.
---

Read `spawn/navigation.yaml` first.

Mandatory reads:
- `spawn-ext-guide/ai/core.md` - Machine baseline — terms, extsrc tree rules, static vs artifact, name and uniqueness, install outputs.
- `spawn-ext-guide/ai/cli.md` - Machine CLI reference — spawn init/extension/build commands, extensions.yaml bundle shape, authoring checklist.

Contextual reads:
- `spawn-ext-guide/ai/config-yaml.md` - Machine schema for config.yaml — keys, files/folders/skills modes, reads, ignores, setup, annotated example.
- `spawn-ext-guide/ai/skill-sources.md` - Machine rules for extsrc/skills/*.md — frontmatter, name/description resolution, rendered skill shape, example.
- `spawn-ext-guide/ai/mcp-json.md` - Machine schema for extsrc/mcp.json — servers, transport, env, capabilities, JSON examples.
- `spawn-ext-guide/ai/cli.md` - Machine CLI reference — spawn init/extension/build commands, extensions.yaml bundle shape, authoring checklist.


Goal: ship only packs that pass strict validation and install cleanly.

1. From extension source root: `spawn extension check . --strict` — resolve missing skills, undeclared files, descriptions for non-no read flags, bad `mcp.json`, missing setup scripts.
2. In a throwaway clone or empty repo: `spawn init`, then `spawn extension add <path-or-url-to-your-extension-source>` (match consumer workflow).
3. Confirm materialized paths under `files:` exist as expected; confirm `artifact` paths are not overwritten on a repeat add/update where applicable.
4. If `healthcheck` is configured: `spawn extension healthcheck <name>` from the target.
5. Document distribution: plain repo URL/path, zip, or entry in an `extensions.yaml` bundle for `spawn build install`.
