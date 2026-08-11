---
name: spectask-execute-step-by-step
description: Step 4 — one Execution Scheme subtask per run with per-step self-review; auto Step 5 when all done (spec/main.md).
---


Operate within the **spectask** process defined in attached **spec/main.md**.

Run **Step 4** one subtask at a time. If which task is unclear, use **`R10-ask`** to ask.

1. Open `overview.md` and `## Execution Scheme`; set **Spec review** if not yet marked.
2. Pick the next pending step (subtask file without `_DONE_` prefix). Respect sequential phases.
3. Launch **one** sub-agent for that step — do NOT implement inline. Prefer `Suggested model` (Task `model` when supported; else prompt + nearest slug). Include **Subagent run protocol** (`R16-ambient`: resolve Ambient / clarify if missing; Ambient block first), **`R13-model-line`**, **`R14-changed-files`**, and Step 4 **Coder protocol** (worker sets `Status: Done`; does not rename).
4. Mark done per **`R15-done-marking`** (rename + `Used model`). Forward changed-file list per **`R14-changed-files`**.
5. In the same run, launch **one** self-review sub-agent scoped to this step only — its changes and its subtask file; not other steps. Criteria as **spec/main.md** Step 5 (inconsistencies, naming, missing imports, broken contracts); fix if needed. Same **Subagent run protocol** / **`R13-model-line`** / **`R14-changed-files`**. Do not mark overview **Code self-review** here.
6. If steps remain: stop — prompt: "Step `{step-id}` done (implemented + self-reviewed). Reply to run the next step." Include the forwarded changed-file list.
7. If all steps done: set `[V] Code implementation [model]`, then run **Step 5** automatically (full code self-review sub-agent per **spec/main.md**); set `[V] Code self-review [model]`; forward aggregated changed files; prompt for user Step 6.
