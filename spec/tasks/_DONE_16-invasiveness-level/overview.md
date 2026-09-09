# 16: Add invasiveness level clarification to spec drafting

## Source seed
- Path: none

## Status
- [V] Research [deepseek-v4-pro-a]
- [V] User research review
- [V] Spec drafting [deepseek-v4-pro-a]
- [V] Spec self-review [deepseek-v4-pro-a]
- [ ] Spec review
- [V] Code implementation [deepseek-v4-pro-a]
- [V] Code self-review [deepseek-v4-pro-a]
- [V] Code review / debugging
- [V] Design document update [deepseek-v4-pro-a]

## Goal
Add a mandatory invasiveness-level clarification to Step 2 (Spec drafting) of the Spec-Tasks methodology so the drafter asks the user to choose one of three edit scopes — minimally-invasive, medium-invasive, or maximally-invasive — together with the other implementation clarifications, and records the choice in the task overview.

## Motivation
The user wants the LLM to commit to an explicit edit scope before writing a spec, so the resulting specification matches the intended blast radius: a minimal single-layer fix, a medium multi-layer/domain change, or a maximum deep rework across all layers and domains.

## Design overview
- Affected modules: `extsrc/files/spec/main.md` (Spawn extension source, static methodology file)
- Files & symbols (concrete paths): `extsrc/files/spec/main.md` — Step 2.2 "Implementation clarifications" block, and the `overview.md` template (new field after `## Motivation`)
- Data flow changes: none (documentation/template change only)
- Integration points: Spawn extension pack — `extsrc/files/spec/main.md` is the source that gets distributed; regeneration materializes it to `spec/main.md` and `spawn/.extend/spectask/files/spec/main.md`

## Before → After
### Before
- Step 2.2 asks implementation clarifications (motivation, ambient context, ambiguous aspects) but has no notion of edit scope / invasiveness.
- `overview.md` template has no field recording the chosen invasiveness level.

### After
- Step 2.2 gains a mandatory invasiveness-level question, asked together with the other clarifications, offering three choices with concrete definitions.
- `overview.md` template gains an `## Invasiveness level` field (after `## Motivation`) recording the chosen level.

## Details

### Invasiveness level definitions (normative)

The drafter asks the user to choose one of three edit scopes. The chosen level constrains the spec: every affected file/symbol in the spec must stay within the chosen scope.

- **minimally-invasive** — edits are confined to a single layer or library; all other layers/libraries are left untouched, even if the resulting solution is a workaround (crutch). The spec must not touch adjacent layers.
- **medium-invasive** — edits may span several adjacent layers or domains, e.g. backend + frontend, or domain1 + domain2. The spec may connect these adjacent surfaces.
- **maximally-invasive** — edits may span all layers and all domains. The LLM follows the principle of deep rework over a superficial fix with compromises.

### Placement

The question is added to Step 2.2 "Implementation clarifications" as a mandatory item, asked together with the other clarifications (motivation, ambient context, ambiguous aspects). It is not a separate sub-step.

### Recording

The chosen level is recorded in the `overview.md` template as a new field `## Invasiveness level` placed immediately after `## Motivation`.

## Execution Scheme
Suggested coordinator model: deepseek-v4-flash
> Each step id is the subtask filename (e.g. `1-abstractions`).
> Each step is executed by a dedicated `A5-coder` subagent (see Step 5).
- Phase 1 (sequential): step 1-update-main-md
