---
name: spectask-seed-create
description: Capture a rough idea as spec/seeds/{X}-{slug}.md (not a full task); then offer to start spectask-create.
---


**Mandatory:** read **spec/main.md** in full before acting — especially Seed paragraph and Seed file template.

**Role:** `A1-drafter`

**Steps:** none of 1–8 — seed only. Promotion → **spectask-create**; seed close → Step 8 item 6.

**Rules:** `R1-paths`, `R2-no-clutter`, `R3-code-num` / `R4-code-tracker` (when promoting later), `R10-ask`

**Flow:**

1. Read **spec/main.md** fully — Folder Structure (`spec/seeds/`), Seed paragraph, Seed file template (header).
2. Create `spec/seeds/{X}-{slug}.md` exactly per that template (`linked task: none` unless already bound).
3. Offer **spectask-create** when the user wants to promote. Do not run Steps 1–8 in this skill.


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
