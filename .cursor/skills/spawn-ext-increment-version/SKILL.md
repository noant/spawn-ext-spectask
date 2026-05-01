---
name: spawn-ext-increment-version
description: Bump extension version in extsrc/config.yaml for releases (semver-oriented guidance).
---


Goal: update **`version`** at the top level of **`extsrc/config.yaml`** before publishing or tagging so consumers and `spawn extension update` flows see a monotonic, intentional change.

1. Open **`extsrc/config.yaml`** and locate **`version`** (required string; compared **as a string** on extension update — ordering follows Spawn/tooling string rules, so prefer **semantic versioning** `MAJOR.MINOR.PATCH` for predictable ordering).
2. Choose bump level:
   - **PATCH** (`1.0.0` → `1.0.1`): fixes, docs-only template tweaks that do not change behavior contracts.
   - **MINOR** (`1.0.1` → `1.1.0`): backward-compatible additions (new optional files, new skills, stricter defaults that remain compatible).
   - **MAJOR** (`1.1.0` → `2.0.0`): breaking changes (removed paths, renamed skills, changed `name`, incompatible template or read semantics).
3. Edit **`version`** to the new value only — keep **`schema`**, **`name`**, and **`version`** consistent with prior releases (**`name`** MUST stay stable across releases unless you intentionally ship a new extension id).
4. If the repo keeps a **changelog**, add an entry for this version in that file (optional; not part of Spawn manifest).
5. Run **`spawn extension check . --strict`** from the extension source root.

Do **not** bump **`schema`** unless you migrate to a new Spawn **`config.yaml`** format version documented by Spawn.


Mandatory reads:
- `spawn-ext-guide/ai/core.md` - Machine baseline — terms, extsrc tree rules, static vs artifact, name and uniqueness, install outputs.
- `spawn-ext-guide/ai/config-yaml.md` - Machine schema for config.yaml — keys, files/folders/skills modes, reads, ignores, setup, annotated example.
- `spawn-ext-guide/ai/cli.md` - Machine CLI reference — spawn init/extension/build commands, extensions.yaml bundle shape, authoring checklist.
- `spawn/navigation.yaml` - Merged Spawn navigation (read-required, read-contextual).

Contextual reads:
- `spawn-ext-guide/ai/skill-sources.md` - Machine rules for extsrc/skills/*.md — frontmatter, name/description resolution, rendered skill shape, example.
- `spawn-ext-guide/ai/mcp-json.md` - Machine schema for extsrc/mcp.json — servers, transport, env, capabilities, JSON examples.
