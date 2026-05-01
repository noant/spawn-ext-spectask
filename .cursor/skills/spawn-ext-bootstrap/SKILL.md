---
name: spawn-ext-bootstrap
description: Bootstrap a new Spawn extension repo with extsrc skeleton and stable id.
---


Goal: start a new Spawn extension (methodology pack) from zero or from an existing repo that lacks `extsrc/`.

1. Confirm or choose extension id (`name`): kebab-case, stable across releases; decide initial `version` string.
2. From the extension repo root run `spawn extension init . --name <id>` so `extsrc/` and `config.yaml` exist.
3. Set `schema: 1`, `name`, `version` in `config.yaml`; remove empty stub keys you will not use yet if the tool allows, or leave minimal valid maps.
4. Plan top-level namespaces under `extsrc/files/` (e.g. `my-org/spec/`, `my-org/guides/`) so paths do not collide with other extensions in combined targets.
5. Next steps: use sibling skills to declare `files`/`folders`, add templates under `extsrc/files/`, then `spawn extension check . --strict`.
6. **Later:** whenever packaging meaningfully evolves after bootstrap, **prompt** a **`version`** bump using **`spawn-ext-increment-version`** before publishing (initial `0.1.0` or `1.0.0` is typical until first stable story).


Mandatory reads:
- `spawn-ext-guide/ai/core.md` - Machine baseline — terms, extsrc tree rules, static vs artifact, name and uniqueness, install outputs.
- `spawn-ext-guide/ai/cli.md` - Machine CLI reference — spawn init/extension/build commands, extensions.yaml bundle shape, authoring checklist.
- `spawn/navigation.yaml` - Merged Spawn navigation (read-required, read-contextual).

Contextual reads:
- `spawn-ext-guide/ai/config-yaml.md` - Machine schema for config.yaml — keys, files/folders/skills modes, reads, ignores, setup, annotated example.
- `spawn-ext-guide/ai/skill-sources.md` - Machine rules for extsrc/skills/*.md — frontmatter, name/description resolution, rendered skill shape, example.
- `spawn-ext-guide/ai/mcp-json.md` - Machine schema for extsrc/mcp.json — servers, transport, env, capabilities, JSON examples.
