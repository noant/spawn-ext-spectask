---
name: spectask-create
description: Use when drafting a new spectask (specification only, per spec/main.md).
---

Operate within the **spectask** process defined in attached **spec/main.md**.
**task-code** naming and confirmations: rules **`R3-code-num`** / **`R4-code-tracker`** in **spec/main.md**.
Complete **Steps 1–2** only — then stop and wait for the user’s **Step 3** (spec review).

Before drafting and in Self Spec Review: follow **`R11-navigation`** in **spec/main.md** (via Step 1.1 / Step 2).

Under this skill, writing implementation code without an approved specification is not allowed — stay within Steps 1–2 (overview.md and subtasks) until spec review passes.

If work began from **`spec/seeds/`**, tie the seed to the new task in **Step 1** (**`linked task:`** + **Source seed** in **`overview.md`**) and close it in **Step 7** item **6**, per **`spec/main.md`**.

When launching the Step 2 sub-agent, include the line from **`R13-model-line`** in the prompt. Use the returned model name when filling `- [V] Self spec review passed [model-name]`.