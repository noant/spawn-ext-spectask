# Step 1: Remove design.yaml from the pack

Status: Done
Suggested model: glm-5.3-flash
Used model: GLM-5.3-flash

## Goal
Pack no longer ships or references spec/design.yaml; docs updated to the navigation-based flow.

## Approach
Edit only existing references; no new instructions. Concise wording in main.md.

## Affected files
- `extsrc/config.yaml` — files section, skills description, version
- `extsrc/files/spec/design.yaml` — delete
- `extsrc/files/spec/main.md` — lines 6-10, 491-497
- `extsrc/skills/spectask-design.md` — lines 3, 10, 16, 18
- `spec/main.md` (repo root live copy) — lines 6, 9, 480, 482, 486
- `README.md` — lines 55, 66, 68, 84, 88, 114, 178, 180

## Code changes (before / after)

### `extsrc/config.yaml` — files entry

**Before**
```yaml
  spec/design.yaml:
    description: "Index of architecture documents under spec/design/ — path and description per entry."
    mode: artifact
    globalRead: auto
    localRead: required
```
Ships the index file.

**After**
```yaml
```
Entry removed; design docs become navigation rules rows.

### `extsrc/config.yaml` — version

**Before**
```yaml
version: "1.27.0"
```
**After**
```yaml
version: "2.0.0"
```
Removed shipped path — breaking change.

### `extsrc/config.yaml:99` — spectask-design skill description

**Before**
`...registering architecture files in spec/design.yaml...`
**After**
`...registering architecture files in spawn/navigation.yaml read-contextual...`

### `extsrc/files/spec/design.yaml` — delete file

**Before**
Template with schema/documents entries.
**After**
File deleted; migration (step 2) converts target copies.

### `extsrc/files/spec/main.md` — Folder Structure (6-10)

**Before**
```markdown
- spec/design.yaml — indexes architecture documents (`path` + `description` per entry); optional but recommended for multiple design files.
- spec/design/hla.md — project high-level architecture (required).
- spec/design/{name}.md — other architecture documents (optional; ADRs, notes, etc.)
  - register in **spec/design.yaml**
  - declare as readable paths for agents, typically via a Spawn extension's `files:` (with appropriate reads), so they appear in `spawn/navigation.yaml**
```
**After**
```markdown
- spec/design/ — architecture documents; `hla.md` (required) plus optional ADRs and notes.
  - declare design docs as readable paths for agents in `spawn/navigation.yaml` read-contextual
```
Folder mention only; navigation referenced as the declaration point, not as a spec/ file.

### `extsrc/files/spec/main.md` — Step 8 (491-497)

**Before**
```markdown
- **Index** — read **spec/design.yaml**
  - if missing, only **spec/design/hla.md** applies (Folder Structure)
  - add **spec/design.yaml** when you register more than one path under **spec/design/**
...
- if the task introduced or renamed architecture docs under **spec/design/**, update **spec/design.yaml** (`path` + `description` for each)
```
**After**
```markdown
- **Index** — read the design rows in **spawn/navigation.yaml** (read-contextual).
...
- if the task introduced or renamed architecture docs under **spec/design/**, add or update their rows in **spawn/navigation.yaml** (`path` + `description`)
```

### `extsrc/skills/spectask-design.md` — 3, 10, 16, 18

**Before**
References to `spec/design.yaml` (description, steps, "Register or update rows in spec/design.yaml").
**After**
Same lines reference `spawn/navigation.yaml` read-contextual rows; step wording: "Register or update rows in `spawn/navigation.yaml` (read-contextual)".

### `spec/main.md` (repo root) — 6, 9, 480, 482, 486
Mirror the same replacements as the shipped template.

### `README.md` — 55, 66, 68, 84, 88, 114, 178, 180
Replace spec/design.yaml mentions with the navigation-based flow (concise, no new sections).

## Additional actions
- `python3 -c "import yaml; yaml.safe_load(open('extsrc/config.yaml'))"` to validate config.
- grep check: `grep -rn "design.yaml" extsrc/ README.md spec/` must return no hits.
