---
name: spectask-extract-patterns
description: After Step 7 — optional extract of reusable patterns into spawn/rules/ and navigation (spec/main.md).
---

Operate within the **spectask** process defined in attached **spec/main.md**.

Run **Optional: Pattern extract (after Step 7)** for the task just closed (or the completed / `_DONE_*` task the user names).

1. Review the closed task: overview, subtasks, and what actually landed (code + design updates).
2. Draft candidate standards, then **filter hard** with the selection criteria in **spec/main.md** — drop junk before the user sees the list.
3. Ask via **`R10-ask`**: **one question per survivor** (title + one-line rationale) with options **Required** / **Optional** / **Decline**.
4. Write only Required/Optional answers under **`spawn/rules/`**, register them in **`spawn/navigation.yaml`** with that scope, and run **`spawn rules refresh`** per the Write rules in **spec/main.md**. If all Declined: write nothing.
