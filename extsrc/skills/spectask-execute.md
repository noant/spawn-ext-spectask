---
name: spectask-execute
description: Steps 4–5 in spec/main.md; then wait for user Step 6.
---

Operate within the **spectask** process defined in attached **spec/main.md**.

**Same chat as Steps 1–2:** do not run Steps 4–5 in this agent. Launch **one** sub-agent that completes Steps 4–5 as coordinator (per **spec/main.md** Step 4 Executor); that sub-agent launches child sub-agents per Execution Scheme. After it finishes, wait here for the user for **Step 6**.

**Fresh execute chat:** you are the coordinator — complete **Steps 4–5** yourself. Then wait for the user for **Step 6**.

When launching sub-agents in Step 4 (one per Execution Scheme step) and Step 5 (self code review), include the line from **`R13-model-line`** in each prompt. Use each returned model name when filling subtask `Status:` lines (Step 4) and `- [V] Self code review passed [model-name]` (Step 5).
