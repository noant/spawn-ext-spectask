---
name: spectask-execute
description: Steps 4–5 in spec/main.md; then wait for user Step 6.
---


Operate within the **spectask** process defined in attached **spec/main.md**.

**Same chat as Steps 1–2:** do not run Steps 4–5 in this agent. Launch **one** coordinator sub-agent for Steps 4–5; prefer `Suggested coordinator model` (Task `model` when supported; else prompt + nearest slug). After it finishes, wait here for **Step 6**.

**Fresh execute chat:** you are the coordinator — complete **Steps 4–5** yourself. Then wait for the user for **Step 6**.

Step 4: prefer each subtask `Suggested model` (Task `model` when supported; else prompt + nearest slug). Include **`R13-model-line`**, **`R14-changed-files`**, and Step 4 **Sub-agent protocol** (worker sets `Status: Done`; does not rename). After each subtask, mark done per **`R15-done-marking`** (rename + `Used model`). Aggregate changed-file lists and forward them per **`R14-changed-files`**.

Step 5: include **`R13-model-line`**; fill `- [V] Self code review passed [model-name]` per **`R13-model-line`**; forward any further changed files per **`R14-changed-files`**.


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
