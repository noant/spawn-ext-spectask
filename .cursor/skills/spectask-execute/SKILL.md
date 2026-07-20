---
name: spectask-execute
description: Steps 4–5 in spec/main.md; then wait for user Step 6.
---


Operate within the **spectask** process defined in attached **spec/main.md**.

**Same chat as Steps 1–2:** do not run Steps 4–5 in this agent. Launch **one** sub-agent that completes Steps 4–5 as coordinator (per **spec/main.md** Step 4 Executor); that sub-agent launches child sub-agents per Execution Scheme. After it finishes, wait here for the user for **Step 6**.

**Fresh execute chat:** you are the coordinator — complete **Steps 4–5** yourself. Then wait for the user for **Step 6**.

When launching sub-agents in Step 4 (one per Execution Scheme step) and Step 5 (self code review), include this in each prompt: "End your final response with the line `My model: X` where X is your actual model identifier (e.g. `claude-sonnet-4-6`, `gpt-4o`) — write your actual model identifier in place of X." Use each returned model name when filling subtask `Status:` lines (Step 4) and `- [V] Self code review passed [model-name]` (Step 5).


Hints:
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
