# 18: Move design index from spec/design.yaml into spawn/navigation.yaml

## Source seed
- Path: none

## Status
- [V] Research [glm-5.4]
- [ ] User research review
- [V] Spec drafting [glm-5.3]
- [V] Spec self-review [glm-5.3 + kimi-k3.1-pro]
- [V] Spec review
- [V] Code implementation [glm-5.3]
- [V] Code self-review [glm-5.3 + kimi-k3.1-pro]
- [ ] Code review / debugging
- [V] Design document update [glm-5.3]

## Goal
Remove spec/design.yaml from the spectask pack; design docs are indexed as rules rows in spawn/navigation.yaml read-contextual; after-install hook migrates existing target-repo design.yaml.

## Motivation
Single navigation source: design docs render into AGENTS.md directly and survive spawn refresh (requires spawn-cli 35).

## Invasiveness level
medium-invasive

## Review models
- Research review: cross-review: glm-5.3, kimi-k3.1-pro
- Spec review: cross-review: glm-5.3, kimi-k3.1-pro
- Code review: cross-review: glm-5.3, kimi-k3.1-pro
- fallback: deepseek-v4-pro

## Run mode
auto

## Research summary
- extsrc/config.yaml:45-49 declares spec/design.yaml (mode: artifact, localRead: required); template extsrc/files/spec/design.yaml.
- References: extsrc/skills/spectask-design.md:3,10,16,18; extsrc/config.yaml:99 (skill description); extsrc/files/spec/main.md:6,9,491,493,497; repo-root spec/main.md:6,9,480,482,486; README.md:55,66,68,84,88,114,178,180.
- Setup: single after-install hook extsrc/setup/install_spectask_mcp.py (uv tool install/upgrade + interactive setup; run with target root as cwd; non-blocking).
- Version 1.27.0; spawn-cli rejects same-version extension updates.
- Generated copies (AGENTS.md, .cursor/skills/*, spawn/.extend/spectask/*) refresh from sources; not manual targets.

## Design overview
- Affected modules: pack config, shipped skill, shipped spec template, setup hook
- Files & symbols: extsrc/config.yaml (files section, skills.spectask-design description, version), extsrc/files/spec/design.yaml (delete), extsrc/files/spec/main.md, extsrc/skills/spectask-design.md, extsrc/setup/install_spectask_mcp.py (new migrate function called before uv calls), repo-root spec/main.md, README.md
- Data flow changes: design index lives in spawn/navigation.yaml read-contextual rules rows; migration moves documents from spec/design.yaml
- Integration points: spawn-cli 35 (external rules paths survive refresh)

## Before → After
### Before
- spec/design.yaml artifact indexes design docs; skills and spec/main.md instruct registering rows there.
### After
- No design.yaml in the pack; design docs are rules rows in spawn/navigation.yaml read-contextual; existing target design.yaml migrated by the after-install hook and deleted.

## Details
- main.md edits: concise wording, only where the old index is referenced; in Folder Structure mention the design folder only (no navigation.yaml mention at the top).
- Migration: parse spec/design.yaml documents, append as {path, description} rows to the first read-contextual rules group (create if absent), skip duplicates, then unlink(missing_ok=True) the file. Runs BEFORE uv calls (uv may be absent). Idempotent.
- Version: 2.0.0 (removed shipped path — breaking).

## Execution Scheme
Suggested coordinator model: glm-5.3
- Phase 1 (sequential): step 1-remove-design-yaml-from-pack → step 2-migration-hook
