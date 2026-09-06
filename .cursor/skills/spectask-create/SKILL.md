---
name: spectask-create
description: Use when drafting a new spectask (specification only, per spec/main.md).
---


**Mandatory:** read **spec/main.md** in full before acting. Do not invent procedure beyond that file.

**Role:** `A1-drafter`

**Steps:** 1–3 only (Research, Spec drafting, Spec self-review) — then stop for user Step 4.

**Rules:** `R3-code-num`, `R4-code-tracker`, `R5-new-task`, `R7-process`, `R8-concrete`, `R9-greenfield`, `R10-ask`, `R11-navigation`, `R13-model-line`, `R14-changed-files`, `R16-ambient`

**Roles involved:** `A1-drafter`, optional `A3-explorer`/`A2-researcher` (Step 1, 2.6), `A4-reviewer` (Steps 1.2.4, 3)

**Flow:**

0. Classify the request per `R17-classify`: `[A]` Question → answer directly (no Steps 1–3); `[B]` Initiative → continue below.
1. Read **spec/main.md** fully — Folder Structure, Embedded rules, Roles, Subagent run protocol, Process Overview, overview and subtask templates.
2. Execute **Step 1: Research** as `A1-drafter` (items 1.1–1.3) exactly as written in **spec/main.md** — select research depth, run the research loop, then get user research review.
3. Execute **Step 2: Spec drafting** as `A1-drafter` (items 2.1–2.6) exactly as written in **spec/main.md**.
4. Execute **Step 3: Spec self-review** via `A4-reviewer` exactly as written in **spec/main.md**.
5. Stop — wait for user Step 4. Do not start Steps 5–8.

**Constraint:** no product implementation until spec review passes.


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
