---
name: spawn-ext-hints
description: Add optional hints.global / hints.local in config.yaml — plain-text agent reminders merged like global reads vs pack-local skills.
---


Goal: add short methodology reminders Spawn injects beside reads and skills — without replacing `globalRead` / `localRead` / skill `required-read`.

1. Add optional top-level **`hints`** with **`global`** and/or **`local`**, each a **YAML list of strings**. Content is **plain text only** (no pointers into other files).
2. **`global`**: included in **`spawn/navigation.yaml`** on this pack’s **`read-required` → `- ext:`** as **`hints`**, echoed into **every rendered skill** (each pack’s `hints.global`, in installed-extension order — same breadth idea as merged global mandatory reads), and merged into **`AGENTS.md`** / entry rollup together with maintainer hints.
3. **`local`**: appended only when rendering skills **owned by this pack**, after globals for that lineage; **not** written under the navigation ext **`hints`** block; **not** folded into **`AGENTS.md`**.
4. Expect **strip + dedupe by exact string** (first occurrence wins). Long lines may emit **`SpawnWarning`**; **`spawn/navigation.yaml`** may **truncate past 512 Unicode codepoints** per string; rendered skill **Hints** blocks may truncate total payload; **`AGENTS.md`** keeps full text but may warn on same thresholds — keep entries terse.
5. Use hints for durable one-liners (conventions, “always run X before Y”). Prefer real specs as **`files:`** entries with **`globalRead`** / **`localRead`** or skill **`required-read`** when the agent must load a document body.
6. **Version:** If hint text or which strings are global vs local changes observable behavior for consumers, **prompt** the author to bump **`version`** via **`spawn-ext-increment-version`** before release.


Hints:
- No emojis or exotic Unicode in code, logs, documentation, or messages; plain ASCII where practical.
- User-facing replies, documentation, and task descriptions: concise wording; minimal markdown (avoid decorative bold/italic); explain with lists and structure; short, clear sentences.
- Specifications, code comments, and project documentation must be written in English.
- If the user only asked a question, answer first; do not edit files unless changes are clearly needed.

Mandatory reads:
- `spawn-ext-guide/ai/core.md` - Machine baseline — terms, extsrc tree rules, static vs artifact, name and uniqueness, install outputs.
- `spawn-ext-guide/ai/config-yaml.md` - Machine schema for config.yaml — keys, files/folders/skills modes, reads, ignores, setup, annotated example.
- `spawn-ext-guide/user-guide.md` - Human-readable standalone guide — narrative for all authoring topics.
- `spawn/navigation.yaml` - Merged Spawn navigation (read-required, read-contextual).

Contextual reads:
- `spawn-ext-guide/ai/skill-sources.md` - Machine rules for extsrc/skills/*.md — frontmatter, name/description resolution, rendered skill shape, example.
- `spawn-ext-guide/ai/mcp-json.md` - Machine schema for extsrc/mcp/windows.json, linux.json, macos.json — servers, OS selection, aligned name sets, transport, env, capabilities, JSON examples.
- `spawn-ext-guide/ai/cli.md` - Machine CLI reference — spawn init/extension/build commands, extensions.yaml bundle shape, authoring checklist.
- `spec/main.md` - Spec-Tasks methodology — folder structure, seven-step process, overview template.
- `spec/design/hla.md` - Project high-level architecture; updated in Step 7.
- `spec/design.yaml` - Index of architecture documents under spec/design/ — path and description per entry.
