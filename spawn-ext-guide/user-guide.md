# Spawn extension author guide

This document is a practical guide for **authoring** an extension: directory layout, `config.yaml`, how it ties to files in the target repository, and what to validate before install. The normative specification is [`extensions.md`](extensions.md); CLI commands are in [`utility.md`](utility.md).

## Audience and goals

An **extension** is an installable methodology pack (rules, agent skills, optional MCP, and scripts). You develop it in an **extension repository**; after install, the **target project repository** gets a copy of the extension source plus Spawn-generated artifacts.

As an author you separate:

- what **may be overwritten** on extension update (shared methodology);
- what **belongs to the project** and must not be clobbered on update;
- what the IDE surfaces to the agent (navigation, required reads, skills).

## Extension repository layout

Extension source lives only under **`extsrc/`**. The repo root can hold anything for development; **only the `extsrc/` tree is copied into a target**, not the whole git repo.

```text
extend-repo/
  extsrc/
    config.yaml          # required — extension contract
    mcp.json             # optional — MCP payload for IDE adapters
    skills/
      {name}.md          # skill sources (filename = key in config.yaml)
    files/
      {relative/path/as/in/target}   # templates for the target repository
    setup/
      {script}.py        # install / uninstall / healthcheck hooks
```

**Required:** `extsrc/config.yaml`.  
**Optional:** everything else above — but anything under `extsrc/files/` **must** be listed under `files` in the config (strict checks treat undeclared files as errors).

## Extension name and on-disk folder

In `config.yaml`, **`name`** is the stable id (prefer **`kebab-case`**, lowercase). The installed copy lives at:

`target-repository/spawn/.extend/{name}/`

If **`name`** is missing, install falls back to the placeholder name `extension` — avoid that: set **`name` explicitly** and keep it stable across versions unless you mean to migrate.

## `config.yaml`: sections and how they map to disk

Minimal valid shape (see also [`ExtensionConfig`](../../src/spawn_cli/models/config.py) in code):

| YAML field | Role |
|------------|------|
| `schema` | Config schema version (currently **`1`**). |
| `version` | Extension version string (compared on update). |
| `name` | Id and folder name `spawn/.extend/{name}/`. |
| `files` | Map of **paths in the target repo** → metadata (mode, description, read rules). |
| `folders` | Target directories with `static` / `artifact` mode (uninstall bookkeeping and spec; see [`extensions.md`](extensions.md)). |
| `skills` | Map of **`skills/` filename** → skill name/description and extra `required-read`. |
| `agent-ignore` | Globs for **agent ignore** in the IDE (Spawn merges into the adapter’s ignore mechanism). |
| `git-ignore` | Lines for the target **`.gitignore`**. |
| `setup` | Optional paths to scripts under `extsrc/setup/` for lifecycle phases. |

Unknown top-level fields may become warnings or strict-mode errors in the future — keep the file aligned with the current schema.

### `files` and the `extsrc/files/` directory

- Each **key** in `files` is a path **from the target repo root**, POSIX-style (e.g. `spec/main.md`).
- The **template file** goes under `extsrc/files/` with the **same relative path** as the key (e.g. `extsrc/files/spec/main.md`).

Materialization behavior (simplified):

- **`mode: static`** (default): if the template exists under `extsrc/files/`, it is copied into the target; an existing target file may be **overwritten** (with a warning). Use for methodology that should track the extension release.
- **`mode: artifact`**: the template is copied **only if the target file does not exist** — afterwards the file is treated as **project-owned** and is **not** overwritten on extension update. Use for tasks, architecture notes, and other evolving project content.

### `skills` and `extsrc/skills/`

- Each key in `skills` is a **Markdown filename** under `extsrc/skills/` (e.g. `spectask-execute.md`).
- The value may set `name`, `description`, and **`required-read`**: paths in the **target** repo that are mandatory **for that skill**, in addition to global/local read rules from `files`.

IDE skills are **not copied verbatim**: Spawn **generates** IDE-specific skills from normalized metadata (name, description, body without optional frontmatter, read lists). Keep sources **procedural**; long reference text belongs in `files` entries with `globalRead` / `localRead`.

See **Skill source format** and **Extension `mcp.json` format** below.

### `globalRead` and `localRead` (on `files` entries)

These apply to paths declared under `files`:

- **`globalRead`**: inclusion in the global `spawn/navigation.yaml` index — `required` (always read), `auto` (listed; agent decides), `no` (omit from global index). Default **`no`**.
- **`localRead`**: how the same path appears in **rendered skills for this extension**. Default **`no`**.

If either `globalRead` or `localRead` is not `no`, **strict validation requires a non-empty `description`** — that string is the human-facing label in navigation/skills.

Skill-level **`required-read`** should not duplicate paths already covered by `globalRead: required` or `localRead: required` on `files`; Spawn merges and de-duplicates anyway.

### `agent-ignore` and `git-ignore`

- **`agent-ignore`**: path globs Spawn adds so the agent does not pull irrelevant trees (e.g. caches).
- **`git-ignore`**: lines appended for the target repository’s `.gitignore`.

### `setup`

Optional phases; for each phase either **omit the key** or point to a **file that exists** under `extsrc/setup/`:

- `before-install`, `after-install`, `before-uninstall`, `after-uninstall`, `healthcheck`.

Scripts are **trusted extension code**; do not silently destroy user-owned artifacts. Blocking vs warning behavior on failure is described in [`utility.md`](utility.md).

## Skill source format (`extsrc/skills/*.md`)

Each skill is a **UTF-8 Markdown** file whose **basename** (e.g. `my-flow.md`) is the key in `config.yaml` → `skills`.

### Optional YAML frontmatter

If the file starts with a line `---`, the next closing `---` line ends the frontmatter block. The block is parsed as **YAML** (safe load). Typical keys:

| Frontmatter key | Meaning |
|-----------------|--------|
| `name` | Display / identity string for the skill (used if not overridden in `config.yaml`). |
| `description` | Short summary (used if not overridden in `config.yaml`). |

If there is no frontmatter, the whole file is treated as the skill **body**.

### How `name` and `description` are resolved

For each skill file, Spawn builds metadata in this order:

1. If `config.yaml` lists that filename under `skills` and sets **`name`**, use it.
2. Else if frontmatter has **`name`**, use it.
3. Else use the filename **without** `.md`.

Same priority for **`description`**: `config.yaml` entry → frontmatter `description` → empty string.

The text **after** the frontmatter (or the whole file if no frontmatter) becomes the **skill body**. That body is what gets embedded in the **rendered** IDE skill (along with generated “mandatory reads”, “contextual reads”, and the `spawn/navigation.yaml` hint — see [`_helpers.render_skill_md`](../../src/spawn_cli/ide/_helpers.py)).

### Authoring tips

- Prefer short, imperative instructions in the body; put long reference material in `files` and expose it via `globalRead` / `localRead` or skill `required-read`.
- Pick a **stable** `name` (or config override) so normalized names stay unique across extensions; see **Uniqueness and collisions**.

### Example `extsrc/skills/acme-run-task.md`

```markdown
---
name: acme-run-task
description: Execute the Acme task flow in the current repo.
---

When the user wants to run an Acme task:

1. Read the mandatory context injected into this skill.
2. Open or create the task under `spec/tasks/` as described in the methodology guide.
3. Report blockers explicitly instead of guessing.
```

If `config.yaml` already sets `name` and `description` for `acme-run-task.md`, you can omit the frontmatter and keep only the procedural body.

## Extension `mcp.json` format

Place **`extsrc/mcp.json`** next to `config.yaml`. It must be **valid JSON**. `spawn extension check` only verifies parseability; structural validation happens when MCP is loaded for rendering.

This file is **not** identical to a Cursor/Claude **project** `.mcp.json`: those often use a top-level **`mcpServers`** object. In an extension, Spawn reads a top-level **`servers`** **array** of server objects, normalizes them, then IDE adapters map them to each tool’s on-disk format (see [`list_mcp`](../../src/spawn_cli/core/low_level.py), [`ide-adapters.md`](ide-adapters.md)).

### Top level

| Field | Type | Meaning |
|-------|------|--------|
| `servers` | array | List of server definitions. Omitted or empty means no MCP from this extension. |

### Each element of `servers`

| Field | Type | Meaning |
|-------|------|--------|
| `name` | string | **Required.** Server id; must be **globally unique** among all extensions in the target. Adapters use this to merge/remove entries. |
| `transport` | object | How to reach the server; see below. |
| `env` | object | Optional environment variables; see below. |
| `capabilities` | object | Optional; defaults tools on, resources/prompts off. Shape: `tools` (bool), `resources` (bool), `prompts` (bool). |

### `transport` object

Parsed fields (defaults in parentheses):

| Field | Meaning |
|-------|--------|
| `type` | `"stdio"` (default), or values adapters treat as remote (e.g. `"sse"`, `"streamable-http"`). |
| `command` | Command for stdio-like transports. |
| `args` | Array of string arguments. |
| `cwd` | Working directory string (default `"."`). |
| `url` | URL for HTTP/SSE-style transports. |

### `env` object

Each key is a variable name. Each value is either:

- A **string** or other non-object: treated as a **user-provided secret** placeholder when rendering (do not put real secrets in the extension repo).
- An **object** validated as `McpEnvVar`: `source`, `required`, `secret`, optional `value` (see [`mcp.py`](../../src/spawn_cli/models/mcp.py)).

Rendered IDE configs use placeholders so secrets are filled in locally, not committed.

### Example `extsrc/mcp.json`

```json
{
  "servers": [
    {
      "name": "acme-docs-mcp",
      "transport": {
        "type": "stdio",
        "command": "npx",
        "args": ["-y", "@acme/mcp-server", "--stdio"],
        "cwd": "."
      },
      "env": {
        "ACME_API_TOKEN": {
          "source": "user",
          "required": true,
          "secret": true
        }
      },
      "capabilities": {
        "tools": true,
        "resources": false,
        "prompts": false
      }
    }
  ]
}
```

## Annotated `config.yaml` example

The example below matches the schema in [`ExtensionConfig`](../../src/spawn_cli/models/config.py). Comments explain each part; omit sections you do not need.

```yaml
# Schema version for this file format (use 1).
schema: 1

# Stable id for the extension and for spawn/.extend/{name}/.
# Required in practice — if omitted, install uses the placeholder name "extension".
name: acme-methodology

# Extension release version (string compared on update).
version: "1.0.0"

# Target-repo paths -> how they are installed and how agents see them.
files:
  methodology/guide.md:
    description: "Core methodology; read when using Acme skills."
    mode: static
    globalRead: auto
    localRead: required
  spec/design/notes.md:
    description: "Team architecture notes (per-repo)."
    mode: artifact
    globalRead: no
    localRead: auto

# Directories in the target repo (static vs artifact for uninstall/update policy).
folders:
  spec/tasks:
    mode: artifact

# Skills: key MUST match filename under extsrc/skills/.
skills:
  acme-run-task.md:
    name: acme-run-task
    description: "Execute the Acme task flow in the current repo."
    required-read:
      - methodology/guide.md

# Globs merged into IDE agent-ignore by Spawn.
agent-ignore:
  - spawn/.extend/**
  - .spawn-cache/**

# Lines merged into the target .gitignore.
git-ignore:
  - .spawn-cache/**

# Optional lifecycle hooks under extsrc/setup/ (values are filenames).
setup:
  after-install: after_install.py
  healthcheck: healthcheck.py
```

**How this ties to the tree:**

- `extsrc/files/methodology/guide.md` and `extsrc/files/spec/design/notes.md` must exist because those paths are declared under `files` (and strict check fails on extra files under `files/` that are not listed).
- `extsrc/skills/acme-run-task.md` must exist because it is listed under `skills`.
- Optional `extsrc/setup/after_install.py`, `extsrc/setup/healthcheck.py` if `setup` references them.
- Optional `extsrc/mcp.json` using the **`servers`** format above — not shown in this YAML, but independent of `config.yaml` except for global uniqueness of server `name`.

## Uniqueness and collisions

- **Skill** and **MCP** names must not collide across extensions in one target after normalization — install/update assumes a single owner per name.
- Choose `files` / `folders` paths that avoid clashes with other extensions (narrow prefixes, methodology namespace).

## What appears in the target after install

1. A full copy of **`extsrc/`** under `spawn/.extend/{name}/` (including `config.yaml`, skill sources, `files`, `setup`, and `mcp.json` when present).
2. Files from `extsrc/files/` are **materialized** at the target repo root according to each path’s `mode`.
3. Spawn refreshes navigation, rendered skills, MCP, and ignore files for connected IDEs (see [`extensions.md`](extensions.md), [`ide-adapters.md`](ide-adapters.md)).

## Typical authoring flow

1. Scaffold: in the extension repo run **`spawn extension init . --name <id>`** (or create `extsrc/` by hand as above).
2. Add templates under **`extsrc/files/`** and declare every path under **`files`** with the right **`mode`** and read rules.
3. Add Markdown under **`extsrc/skills/`** and list them under **`skills`**.
4. Optionally add **`mcp.json`**, **`setup`**, **`agent-ignore`**, **`git-ignore`**, **`folders`**.
5. Validate: **`spawn extension check .`** (use **`--strict`** for errors on missing skills, undeclared files, etc. — see [`utility.md`](utility.md)).
6. Install into a **throwaway target**: from the target root, **`spawn extension add <source>`**, then inspect navigation, skills, and MCP.
7. Optionally **`spawn extension healthcheck <name>`** in the target.
8. Publish: give consumers a **git URL, local path, or zip** that contains a valid `extsrc/` (there is no separate extension package registry in this model).

## Bundling several extensions (build)

To install multiple extensions with one command, use a repo with **`extensions.yaml`** (see [`extensions.md`](extensions.md), command **`spawn build install`**).