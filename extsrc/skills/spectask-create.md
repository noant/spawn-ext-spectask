---
name: spectask-create
description: Use when drafting a new spectask (specification only, per spec/main.md).
---

Operate within the **spectask** process defined in attached **spec/main.md**.
**task-code** naming and confirmations: **Embedded rules** 3-4 in **spec/main.md**.
Complete **Steps 1–2** only — then stop and wait for the user’s **Step 3** (spec review).

Before drafting and in Self Spec Review: follow **Embedded rule 10** in **spec/main.md** (via Step 1.1 / Step 2).

Under this skill, writing implementation code without an approved specification is not allowed — stay within Steps 1–2 (overview.md and subtasks) until spec review passes.

If work began from **`spec/seeds/`**, tie the seed to the new task in **Step 1** (**`linked task:`** + **Source seed** in **`overview.md`**) and close it in **Step 7** item **6**, per **`spec/main.md`**.

When launching the Step 2 sub-agent, include this in the prompt: "End your final response with the line `My model: X` where X is your actual model identifier (e.g. `claude-sonnet-4-6`, `gpt-4o`) — write your actual model identifier in place of X." Use the returned model name when filling `- [V] Self spec review passed [model-name]`.