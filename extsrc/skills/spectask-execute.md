---
name: spectask-execute
description: Steps 4–5 in spec/main.md; then wait for user Step 6.
---

Operate within the **spectask** process defined in attached **spec/main.md**.

Complete **Steps 4–5**. Then wait for the user for **Step 6**.

When launching sub-agents in Step 4 (one per Execution Scheme step) and Step 5 (self code review), include this in each prompt: "Start your response with the line `My model: X` where X is your actual model identifier (e.g. `claude-sonnet-4-6`, `gpt-4o`) — write your actual model identifier in place of X." Use each returned model name when filling subtask `Status:` lines (Step 4) and `- [V] Self code review passed [model-name]` (Step 5).
