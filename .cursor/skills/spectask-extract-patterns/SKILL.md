---
name: spectask-extract-patterns
description: After Step 7 — present reusable patterns as a single list to the user (no preliminary questions), then write per user's per-candidate decision.
---


Operate within the **spectask** process defined in attached **spec/main.md**.

Run **Optional: Pattern extract (after Step 7)** for the task just closed (or the completed / `_DONE_*` task the user names).

1. Review the closed task: overview, subtasks, and what actually landed (code + design updates).
2. Draft candidate standards, then **filter hard** with the selection criteria in **spec/main.md** — drop junk before the user sees the list.
3. If filtering leaves zero candidates, say so briefly and stop (do not ask, do not present, do not invent fillers).
4. Otherwise **Present the filtered list to the user in one message**, in this run, right after Step 7 — **no `R10-ask`, no per-candidate tool questions, no pauses**. For each survivor: short title + one-line rationale + suggested scope (Required = `read-required`, Optional = `read-contextual`). End the message with an explicit reply request: tell the user how to respond (per-candidate Required/Optional/Decline, or "decline all" to skip everything).
5. **Wait** for the user's reply. Do not write rules yet, do not run `spawn refresh`, do not start the next task.
6. After the reply, apply the user's answer: write only Required/Optional candidates under **`spawn/rules/`**, register them in **`spawn/navigation.yaml`** with that scope, and run exactly **`spawn refresh`** in the terminal per the Write rules in **spec/main.md**. Candidates not addressed in the reply default to **Decline**. If every candidate is Declined, write nothing.


Hints:
- Use the platform ask tool when available (R10-ask in spec/main.md); otherwise, stop and request input from the user.
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
