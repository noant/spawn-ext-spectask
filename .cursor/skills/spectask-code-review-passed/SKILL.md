---
name: spectask-code-review-passed
description: After user confirms code review / debugging — Steps 7–8 then optional pattern extract (spec/main.md).
---


**Mandatory:** read **spec/main.md** in full before acting — especially Steps 7–8 and Optional: Pattern extract.

**Role:** `A1-drafter`

**Steps:** 7 → 8 → optional Pattern extract (same run).

**Rules:** `R1-paths`, `R2-no-clutter`, `R7-process`, `R14-changed-files`

**Roles involved:** User (Step 7 confirmation); `A1-drafter` (mark 7, run 8, pattern extract)

**Flow:**

1. Read **spec/main.md** fully — **Step 7: Code review / debugging**, **Step 8: Design document update**, **Optional: Pattern extract (after Step 8)**.
2. Execute **Step 7** exactly as written (mark `[V]` and prompt).
3. Execute **Step 8** exactly as written.
4. Execute **Optional: Pattern extract** exactly as written (or via **spectask-extract-patterns**): filter candidates, then present the entire filtered list to the user in one message in this run, then wait for the user to reply with per-candidate Required/Optional/Decline. Do not write under **`spawn/rules/`** or edit **`spawn/navigation.yaml`** until the user answers.


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
