---
name: spectask-execute
description: Steps 4–5 in spec/main.md; then wait for user Step 6.
---

Operate within the **spectask** process defined in attached **spec/main.md**.

**Same chat as Steps 1–2:** do not run Steps 4–5 in this agent. Launch **one** coordinator sub-agent for Steps 4–5; prefer `Suggested coordinator model` (Task `model` when supported; else prompt + nearest slug). After it finishes, wait here for **Step 6**.

**Fresh execute chat:** you are the coordinator — complete **Steps 4–5** yourself. Then wait for the user for **Step 6**.

Step 4: prefer each subtask `Suggested model` (Task `model` when supported; else prompt + nearest slug). Include **`R13-model-line`**. On done, **coordinator** sets `Status: Done` and `Used model` per **`R13-model-line`** (tool `model` param if passed; else `My model:`). Sub-agent must not write `Used model`.

Step 5: include **`R13-model-line`**; fill `- [V] Self code review passed [model-name]` per **`R13-model-line`**.
