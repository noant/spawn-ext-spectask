---
name: spectask-execute
description: Steps 4–5 in spec/main.md; then wait for user Step 6.
---


**Mandatory:** read **spec/main.md** in full before acting — especially Steps 4–5, Coder protocol, Subagent run protocol.

**Role:** `A6-coordinator`

**Steps:** 4–5 — then wait for user Step 6.

**Rules:** `R7-process`, `R10-ask`, `R13-model-line`, `R14-changed-files`, `R15-done-marking`, `R16-ambient`

**Roles involved:** `A6-coordinator`, `A5-coder` (per step), `A4-reviewer` (Step 5). Same chat as Steps 1–2: `A1-drafter` must not be coordinator — launch a new `A6-coordinator` sub-agent.

**Flow:**

1. Read **spec/main.md** fully — Roles, Subagent run protocol, **Step 4: Code implementation**, **Step 5: Code self-review**, Coder protocol, `R13`–`R16`.
2. Assume coordinator role per Step 4 Executor rules (same-chat → launch `A6-coordinator` sub-agent; fresh chat → current agent is coordinator).
3. Execute **Step 4** exactly as written in **spec/main.md**.
4. Execute **Step 5** exactly as written in **spec/main.md**.
5. Stop — wait for user Step 6. Do not start Step 7.


Hints:
- Use the platform ask tool when available (R10-ask in spec/main.md); otherwise, stop and request input from the user.
- No emojis or exotic Unicode in code, logs, documentation, or messages; plain ASCII where practical.
- User-facing replies, documentation, and task descriptions: concise wording; minimal markdown (avoid decorative bold/italic); explain with lists and structure; short, clear sentences.
- Specifications, code comments, and project documentation must be written in English.
- If the user only asked a question, answer first; do not edit files unless changes are clearly needed.

Mandatory reads:
- `spec/main.md` - Spec-Tasks methodology — folder structure, seven-step process, overview template.
- `spec/design.yaml` - Index of architecture documents under spec/design/ — path and description per entry.
- `spawn/navigation.yaml` - Merged Spawn navigation (read-required, read-contextual).

Contextual reads:
- `spec/design/hla.md` - Project high-level architecture; updated in Step 7.
