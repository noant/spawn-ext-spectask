---
name: spectask-create
description: Use when drafting a new spectask (specification only, per spec/main.md).
---

**Mandatory:** read **spec/main.md** in full.

**Role:** `A1-drafter`

**Rules:** `R3-code-num`, `R4-code-tracker`, `R5-new-task`, `R7-process`, `R8-concrete`, `R9-greenfield`, `R10-ask`, `R11-navigation`, `R13-model-line`, `R14-changed-files`, `R16-ambient`, `R23-review-scheme`

**Roles involved:** `A1-drafter`, optional `A3-explorer`/`A2-researcher` (Step 1, 2.6), `A4-reviewer` (Steps 1.2.4, 3), `A6-coordinator` (auto mode, Step 5)

**Mandatory gate** — in order, before anything else:

1. **Classify** per `R17-classify`: `[A]` Question → answer directly, gate ends; `[B]` Initiative → continue; unclear → ask via `R10-ask` and wait.
2. **Read spec/main.md fully** (Folder Structure, Embedded rules, Roles, Subagent run protocol, Process Overview, templates).
3. **Combined Step 1.1 ask** — ask ALL of it in ONE `R10-ask` call, each question with a proposed default: run mode ([interactive] (default) / [auto]); research depth ([inline]/[medium] (default)/[medium-cross]/[high]/[high-cross]/[skip] — offer [skip] first when trivial); cross model menu; research/spec/code review schemes (single or cross, `R23-review-scheme`); motivation; invasiveness level; task code (`R3-code-num`); ambient context (`R16-ambient`) when unset. No follow-up asks; Steps 1.2, 2.2, 3, 6 reuse the answers.

**Flow:**

1. **Step 1: Research** (spec/main.md 1.1–1.3) at the chosen depth, per the chosen research review scheme.
2. **Step 2: Spec drafting** (spec/main.md 2.1–2.6).
3. **Step 3: Spec self-review** via `A4-reviewer` per the Spec review scheme from `## Review models`.
4. **Run mode branch:**
   - `[interactive]` — stop; wait for user Step 4. No implementation until spec review passes.
   - `[auto]` — do NOT stop at Step 4: run Step 4 as skipped (checkbox unchecked), then start **Steps 5-6** automatically per spec/main.md (new `A6-coordinator` sub-agent when Steps 1-3 are in this chat), then **Step 8** (Step 7 skipped, unchecked) and Pattern extract.

**Constraint:** no product implementation until spec review passes (interactive) or Step 3 completes (auto).


Hints:
- Use the platform ask tool when available (R10-ask in spec/main.md); otherwise, stop and request input from the user.
- No emojis or exotic Unicode in code, logs, documentation, or messages; plain ASCII where practical.
- User-facing replies, documentation, and task descriptions: concise wording; minimal markdown (avoid decorative bold/italic); explain with lists and structure; short, clear sentences.
- Specifications, code comments, and project documentation must be written in English.
- If the user only asked a question, answer first; do not edit files unless changes are clearly needed.

Mandatory reads:
- `spec/main.md` - Spec-Tasks methodology — folder structure, eight-step process, overview template.
- `spec/design.yaml` - Index of architecture documents under spec/design/ — path and description per entry.
- `spawn/navigation.yaml` - Merged Spawn navigation (read-required, read-contextual).

Contextual reads:
- `spec/design/hla.md` - Project high-level architecture; updated in Step 8.
