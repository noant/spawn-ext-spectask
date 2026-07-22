---
name: spectask-extract-patterns
description: After Step 7 — optional extract of reusable patterns into spawn/rules/ and navigation (spec/main.md).
---


Operate within the **spectask** process defined in attached **spec/main.md**.

Run **Optional: Pattern extract (after Step 7)** for the task just closed (or the completed / `_DONE_*` task the user names).

1. Review the closed task: overview, subtasks, and what actually landed (code + design updates).
2. Draft candidate standards, then **filter hard** with the selection criteria in **spec/main.md** — drop junk before the user sees the list.
3. Ask via Embedded rule 9: **one question per survivor** (title + one-line rationale) with options **Required** / **Optional** / **Decline**.
4. Write only Required/Optional answers under **`spawn/rules/`**, register them in **`spawn/navigation.yaml`** with that scope, and run **`spawn rules refresh`** per the Write rules in **spec/main.md**. If all Declined: write nothing.


Hints:
- Use the platform ask tool when available (rule 9 in spec/main.md); plain chat otherwise.
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
