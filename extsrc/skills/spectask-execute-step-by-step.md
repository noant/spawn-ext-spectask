---
name: spectask-execute-step-by-step
description: Step 4 — one Execution Scheme subtask per run; wait for user between steps (spec/main.md).
---

Operate within the **spectask** process defined in attached **spec/main.md**.

Run **Step 4** one subtask at a time. Ask which task if unclear.

1. Open `overview.md` and `## Execution Scheme`; set **Spec review passed** if not yet marked.
2. On first run for this task, read all files in `spec/extend/` first.
3. Pick the next pending step (subtask file without `_DONE_` prefix). Respect sequential phases.
4. Launch **one** sub-agent for that step — do NOT implement inline. Include in prompt: "End your final response with the line `My model: X` where X is your actual model identifier."
5. Rename subtask to `_DONE_{name}`, set `Status: Done | model: {model}`.
6. If steps remain: stop — prompt: "Step `{step-id}` done. Reply to run the next step."
7. If all steps done: set `[V] Code implemented [model]`, then prompt per **spec/main.md** Step 5. Do not run self code review automatically.
