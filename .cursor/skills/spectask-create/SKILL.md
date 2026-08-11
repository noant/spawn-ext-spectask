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

Ambient context (`R16-ambient`): if not set in this chat, clarify via **`R10-ask`** before any sub-agent launch. `Ambient context: none` means set — do not ask.

On each subtask (Step 1.6): set `Suggested model`; leave `Used model` empty.
With `## Execution Scheme`: set `Suggested coordinator model`.
If motivation is unclear from the request: ask via **`R10-ask`** (multiple choice); put the answer in **`## Motivation`** after **Goal**.

When launching any sub-agent (Explorer, Step 2 Reviewer, etc.): follow **Subagent run protocol** — Ambient block first (`R16-ambient`), then the line from **`R13-model-line`**. Use the returned model name when filling `- [V] Spec self-review [model-name]`.
