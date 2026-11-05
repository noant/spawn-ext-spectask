---
name: spectask-extract-patterns
description: After Step 8 - present reusable patterns as a single list, ask per-candidate via the ask tool, then write per the user's decision.
---

**Mandatory:** read **spec/main.md** in full — **Pattern extract (after Step 8)**.

**Role:** `A1-drafter`

**Steps:** after Step 8 only — not a Status checkbox.

**Rules:** `R14-changed-files` (+ Selection criteria and Write rules in **spec/main.md**)

**Flow:**

1. Read **spec/main.md** fully — Pattern extract (Discover, Selection criteria, Present, Ask, Apply, Write).
2. **Discover** exactly as written.
3. Zero candidates → say so briefly and stop (no ask, no present, no fillers).
4. `[auto]` run mode: skip Present/Ask — write ALL survivors as Optional (read-contextual), add them to `spawn/navigation.yaml`, run `spawn refresh`, list changed files (`R14`), and stop.
5. `[interactive]`: **Present** the entire filtered list in **one message** right after Step 8; per survivor: short title + one-line rationale + scope (Required = `read-required`, Optional = `read-contextual`).
6. `[interactive]`: **Ask** per-candidate Required/Optional/Decline plus "decline all" via the ask tool (`R10-ask`); wait. Do not write rules, run `spawn refresh`, or start the next task yet.
7. **Apply**: write only Required/Optional candidates; unanswered candidates default to Decline; all Declined → write nothing.
8. **Write** exactly as written (Required/Optional only), then `spawn refresh`.


Hints:
- Use the platform ask tool when available (R10-ask in spec/main.md); otherwise, stop and request input from the user.
- No emojis or exotic Unicode in code, logs, documentation, or messages; plain ASCII where practical.
- User-facing replies, documentation, and task descriptions: concise wording; minimal markdown (avoid decorative bold/italic); explain with lists and structure; short, clear sentences.
- Specifications, code comments, and project documentation must be written in English.
- If the user only asked a question, answer first; do not edit files unless changes are clearly needed.

Mandatory reads:
- `spec/main.md` - Spec-Tasks methodology — folder structure, eight-step process, overview template.
- `spec/design.yaml` - Index of architecture documents under spec/design/ — path and description per entry.
- `spawn/navigation.yaml` - Merged Spawn navigation (read-required, read-contextual).

Contextual reads:
- `spec/design/hla.md` - Project high-level architecture; updated in Step 8.
