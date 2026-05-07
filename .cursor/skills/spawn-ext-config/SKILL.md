---
name: spawn-ext-config
description: Declare config.yaml files/folders/ignores/setup and mirror every path under extsrc/files.
---


Goal: wire every template path under `extsrc/files/` into `config.yaml` with correct `mode`, `globalRead`/`localRead`, and optional `folders`/`setup`/`agent-ignore`/`git-ignore`/`hints`.

1. List every file under `extsrc/files/`; each MUST have a matching key under `files:` (POSIX path relative to target root). Fix gaps before strict check.
2. For each path choose `mode`: `static` for shared methodology the pack may overwrite on update; `artifact` for repo-owned outputs (tasks, local notes) that must never be overwritten after creation.
3. Set `globalRead`/`localRead` so humans and agents discover the right docs (`required`/`auto`/`no`). Any non-`no` read flag needs a non-empty `description` under strict validation.
4. Use `folders:` for directories whose ownership/update policy matters even when templates are sparse.
5. Reference setup scripts only with basenames that exist under `extsrc/setup/`; hooks must be idempotent and safe for artifact data.
6. For optional plain-text **`hints`** (`global` / `local` string lists merged into navigation and rendered skills — not a substitute for read surfaces), follow **`spawn-ext-hints`**.
7. Run `spawn extension check . --strict` and fix reported issues.
8. **Version:** If these edits materially change what consumers get (paths, read surfaces, ignores, setup, hints), **prompt** the author to bump **`version`** using **`spawn-ext-increment-version`** before tagging or publishing. Trivial typo-only fixes to existing templates may skip a bump — ask if unsure.


Hints:
- No emojis or exotic Unicode in code, logs, documentation, or messages; plain ASCII where practical.
- User-facing replies, documentation, and task descriptions: concise wording; minimal markdown (avoid decorative bold/italic); explain with lists and structure; short, clear sentences.
- If the user only asked a question, answer first; do not edit files unless changes are clearly needed.

Mandatory reads:
- `spawn-ext-guide/ai/core.md` - Machine baseline — terms, extsrc tree rules, static vs artifact, name and uniqueness, install outputs.
- `spawn-ext-guide/ai/config-yaml.md` - Machine schema for config.yaml — keys, files/folders/skills modes, reads, ignores, setup, annotated example.
- `spawn/navigation.yaml` - Merged Spawn navigation (read-required, read-contextual).

Contextual reads:
- `spawn-ext-guide/ai/skill-sources.md` - Machine rules for extsrc/skills/*.md — frontmatter, name/description resolution, rendered skill shape, example.
- `spawn-ext-guide/ai/mcp-json.md` - Machine schema for extsrc/mcp/windows.json, linux.json, macos.json — servers, OS selection, aligned name sets, transport, env, capabilities, JSON examples.
- `spawn-ext-guide/ai/cli.md` - Machine CLI reference — spawn init/extension/build commands, extensions.yaml bundle shape, authoring checklist.
