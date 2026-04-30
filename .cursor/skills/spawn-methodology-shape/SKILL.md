---
name: spawn-methodology-shape
description: Design methodology namespaces, static vs artifact layout, and read surfaces before packing.
---

Read `spawn/navigation.yaml` first.

Mandatory reads:
- `spawn-ext-guide/ai/core.md` - Machine baseline — terms, extsrc tree rules, static vs artifact, name and uniqueness, install outputs.
- `spawn-ext-guide/ai/config-yaml.md` - Machine schema for config.yaml — keys, files/folders/skills modes, reads, ignores, setup, annotated example.
- `spawn-ext-guide/user-guide.md` - Human-readable standalone guide — narrative for all authoring topics.

Contextual reads:
- `spawn-ext-guide/ai/config-yaml.md` - Machine schema for config.yaml — keys, files/folders/skills modes, reads, ignores, setup, annotated example.
- `spawn-ext-guide/ai/skill-sources.md` - Machine rules for extsrc/skills/*.md — frontmatter, name/description resolution, rendered skill shape, example.
- `spawn-ext-guide/ai/mcp-json.md` - Machine schema for extsrc/mcp.json — servers, transport, env, capabilities, JSON examples.
- `spawn-ext-guide/ai/cli.md` - Machine CLI reference — spawn init/extension/build commands, extensions.yaml bundle shape, authoring checklist.


Goal: before editing YAML heavily, decide what the methodology teaches and where files live under `extsrc/files/`.

1. Define audiences (human vs agent) and primary workflows; map each to concrete paths under a single namespace prefix.
2. Classify each deliverable as `static` (canonical methodology the pack maintains) vs `artifact` (per-repo living documents).
3. Choose what belongs in global navigation (`globalRead`) vs only when using this pack’s skills (`localRead`).
4. Split long specs into `extsrc/files/` and keep `extsrc/skills/*.md` as thin procedures that point to those reads.
5. Align names with uniqueness rules (prefixed skill ids, MCP server ids, path prefixes) if this pack coexists with others.
6. Implement the tree under `extsrc/files/`, then run `spawn-ext-config` and `spawn-ext-verify` workflows.
