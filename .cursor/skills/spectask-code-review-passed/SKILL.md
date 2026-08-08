---
name: spectask-code-review-passed
description: After user confirms Code Review / Debugging — Steps 6–7 then optional pattern extract (spec/main.md).
---


Operate within the **spectask** process defined in attached **spec/main.md**.

On the active `spec/tasks/{X}-{name}/overview.md`, finish **Step 6** (mark **Code Review / Debugging passed** and the Step 6 prompt), then complete **Step 7** through **Design documents updated** in the same run. If **`overview.md`** ties a **`spec/seeds/`** file to this task, run **Step 7** item **6** (seed `_DONE_` rename) per **`spec/main.md`**. If which task is unclear, use **`R10-ask`** to ask.

After Step 7, run **Optional: Pattern extract (after Step 7)** per **`spec/main.md`** (same procedure as skill **spectask-extract-patterns**): filter candidates, then ask per candidate **Required** / **Optional** / **Decline**. Do not write under **`spawn/rules/`** or edit **`spawn/navigation.yaml`** until the user answers.


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
