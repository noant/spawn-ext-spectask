---
name: spectask-execute-step-by-step
description: Step 4 — one Execution Scheme subtask per run with per-step self-review; auto Step 5 when all done (spec/main.md).
---


Operate within the **spectask** process defined in attached **spec/main.md**.

Run **Step 4** one subtask at a time. If which task is unclear, use **`R10-ask`** to ask.

1. Open `overview.md` and `## Execution Scheme`; set **Spec review passed** if not yet marked.
2. Pick the next pending step (subtask file without `_DONE_` prefix). Respect sequential phases.
3. Launch **one** sub-agent for that step — do NOT implement inline. Prefer `Suggested model` (Task `model` when supported; else prompt + nearest slug). Include **`R13-model-line`**, **`R14-changed-files`**, and Step 4 **Sub-agent protocol** (worker sets `Status: Done`; does not rename).
4. Mark done per **`R15-done-marking`** (rename + `Used model`). Forward changed-file list per **`R14-changed-files`**.
5. In the same run, launch **one** self-review sub-agent scoped to this step only — its changes and its subtask file; not other steps. Criteria as **spec/main.md** Step 5 (inconsistencies, naming, missing imports, broken contracts); fix if needed. Same **`R13-model-line`** / **`R14-changed-files`**. Do not mark overview **Self code review passed** here.
6. If steps remain: stop — prompt: "Step `{step-id}` done (implemented + self-reviewed). Reply to run the next step." Include the forwarded changed-file list.
7. If all steps done: set `[V] Code implemented [model]`, then run **Step 5** automatically (full self code review sub-agent per **spec/main.md**); set `[V] Self code review passed [model]`; forward aggregated changed files; prompt for user Step 6.


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
