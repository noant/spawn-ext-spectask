---
name: spectask-create
description: Use when drafting a new spectask (specification only, per spec/main.md).
---


Operate within the **spectask** process defined in attached **spec/main.md**.
Complete **Steps 1–2** only — then stop and wait for the user’s **Step 3** (spec review).

Under this skill, writing implementation code without an approved specification is not allowed — stay within Steps 1–2 (overview.md and subtasks) until spec review passes.

If work began from **`spec/seeds/`**, tie the seed to the new task in **Step 1** (**`linked task:`** + **Source seed** in **`overview.md`**) and close it in **Step 7** item **6**, per **`spec/main.md`**.

Hints:
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
