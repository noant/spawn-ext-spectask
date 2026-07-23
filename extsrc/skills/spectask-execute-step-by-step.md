---
name: spectask-execute-step-by-step
description: Step 4 — one Execution Scheme subtask per run with per-step self-review; auto Step 5 when all done (spec/main.md).
---

Operate within the **spectask** process defined in attached **spec/main.md**.

Run **Step 4** one subtask at a time. If which task is unclear, use **`R10-ask`** to ask.

1. Open `overview.md` and `## Execution Scheme`; set **Spec review passed** if not yet marked.
2. Pick the next pending step (subtask file without `_DONE_` prefix). Respect sequential phases.
3. Launch **one** sub-agent for that step — do NOT implement inline. Include the line from **`R13-model-line`** in the prompt.
4. Rename subtask to `_DONE_{name}`, set `Status: Done | model: {model}`.
5. In the same run, launch **one** self-review sub-agent scoped to this step only — its changes and its subtask file; not other steps. Criteria as **spec/main.md** Step 5 (inconsistencies, naming, missing imports, broken contracts); fix if needed. Same **`R13-model-line`** prompt line. Do not mark overview **Self code review passed** here.
6. If steps remain: stop — prompt: "Step `{step-id}` done (implemented + self-reviewed). Reply to run the next step."
7. If all steps done: set `[V] Code implemented [model]`, then run **Step 5** automatically (full self code review sub-agent per **spec/main.md**); set `[V] Self code review passed [model]`; prompt for user Step 6.
