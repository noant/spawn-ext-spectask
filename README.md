# Spectask (Spawn extension)

Spectask is a methodology and structured workflow that enforces specification before implementation in AI-assisted development. This repository packages Spectask as a **Spawn extension**: methodology files, agent skills, and folder modes (`static` vs `artifact`) are declared in `extsrc/config.yaml` and installed into your project with the Spawn CLI.

## Install

From the **root of the target git repository**, run (initialize Spawn once per repo, then add the extension):

```bash
spawn init
spawn extension add https://github.com/noant/spawn-ext-spectask.git
```
## How it works

Before anything is implemented, the agent composes a task document: a one-sentence goal, a before/after description, affected modules, and resolution of any ambiguous points. After that come two explicit human checkpoints: you approve the **plan**, then you approve the **code**. Between those points the agent must not drift from what was agreed.

The full cycle:

1. Agent drafts the specification and asks clarifying questions if anything is ambiguous
2. Agent self-reviews the spec in a **dedicated subagent** (architectural impact, correctness, sequencing) — a separate context window focuses the review and usually catches more than an inline pass in the same thread
3. **You approve the plan** ("ok" / "lgtm" / "spec review passed")
4. Agent implements following the **Execution Scheme** in the spec — sequential and parallel phases — with one dedicated subagent per step
5. Agent self-reviews the code in a **dedicated subagent** (naming, imports, alignment with the spec), because a separate context window keeps the focus on the changes and the spec instead of the implementation thread that wrote them, which usually surfaces inconsistencies before your review
6. **You approve the code** ("ok" / "lgtm" / "code review passed")
7. Agent updates `spec/design/hla.md`, reconciles `spec/design.yaml` if needed, and marks the task as done

## The `spec/` layout

All significant methodology layout lives under `spec/` as defined in the shipped `spec/main.md`. Only allowed paths — no arbitrary documents alongside.

- `spec/main.md` — process rules and the `overview.md` template
- `spec/design.yaml` — index of architecture documents under `spec/design/` (path + description per entry)
- `spec/design/hla.md` — current architecture overview; updated after every completed task
- `spec/design/{name}.md` — additional architecture documents (ADRs, notes, etc.); register entries in `spec/design.yaml` and declare paths in the extension (or follow your org’s Spawn layout) so agents see them via merged navigation
- `spec/tasks/{X}-{name}/overview.md` — task specification
- `spec/tasks/{X}-{name}/{N}-{description}.md` — subtask files when decomposition is needed
- `spec/seeds/{X}-{slug}.md` — optional rough ideas before a full task; see [Seeds](#seeds)

After **your** code approval (Step 6), Step 7 renames the task folder to `_DONE_{X}-{name}` — not before. That keeps history readable in the repository.

## Core principles

**Specification before implementation.** The task is captured in a document that becomes the shared source of truth for you and the agent. This eliminates guesswork and rework.

**Agent self-review.** Before asking you, the agent re-reads the specification and the changes it made. Small issues are caught before they reach you.

**Shared context via Spawn.** Org-wide rules and extra readable paths usually arrive through **additional Spawn extensions** (or extra `files:` entries in your own pack): declare them in `extsrc/config.yaml` with the right `globalRead` / `localRead` so they appear in merged **`spawn/navigation.yaml`** — same idea as registering extra `spec/design/{name}.md` files.

**Explicit decomposition.** If a task touches more than one file, `overview.md` contains an explicit execution scheme: sequential and parallel phases, each step handled by a dedicated subagent. No "everything at once".

**Architecture lives in the repo.** The baseline is `spec/design/hla.md` — a living overview updated after every task — but you can keep ADRs and other write-ups as additional `spec/design/{name}.md` files listed in `spec/design.yaml`.

## Seeds

**Seeds** are optional Markdown files under `spec/seeds/` for capturing an idea quickly — informal notes, not a full Spectask specification. The full Steps 1–7 workflow does not require a seed unless you deliberately start there.

- Use the **`spectask-seed-create`** skill (or equivalent prompt) so the agent follows the **Seed** section and **Seed file template (header)** in `spec/main.md`: pick a kebab-case slug and the next numeric prefix `X`, create `spec/seeds/{X}-{slug}.md` with `linked task: none` until it binds to a task.
- When you promote the idea into real work, run **`spectask-create`** and link the seed from `overview.md` (**Source seed** in the template). Step 7 includes renaming the linked seed with `_DONE_` when the task closes.

This extension declares `spec/seeds/` as an **artifact** folder in `extsrc/config.yaml`, so seed files are project-owned and are not overwritten on extension updates.

## Skills

After install, invoke methodology steps using these **skills** by name; Spawn renders them into your IDE’s skill/rules layout.

| Skill | Purpose |
|--------|--------|
| **spectask-create** | Draft a new task spec only — **Steps 1–2** in `spec/main.md` (no implementation, no HLA update). |
| **spectask-spec-review-passed** | Step 3: **Spec review passed** in `overview.md` + Step 3 prompt. |
| **spectask-execute** | **Steps 4–5** in `spec/main.md` (implement + self code review); then wait for the user — **Step 6**. |
| **spectask-code-review-passed** | Step 6: **Code review passed** in `overview.md` + Step 6 prompt; then **Step 7** in `spec/main.md`. |
| **spectask-design** | Register architecture files in `spec/design.yaml` or draft `spec/design/*.md`. |
| **spectask-seed-create** | Capture a rough idea as `spec/seeds/{X}-{slug}.md`; offer **spectask-create** when the user promotes. |

## Navigation and reads

**`spawn/navigation.yaml`** (generated by Spawn after install) is the merged index of what agents should read first (`read-required` / contextual reads). It replaces a hand-maintained `spec/navigation.yaml` from older standalone Spectask layouts.

**`spec/design.yaml`** is your project’s explicit list of architecture markdown paths under `spec/design/` with short descriptions. Keep it aligned whenever you add or rename design docs.

**spectask-design** covers entries in `spec/design.yaml` and companion files under `spec/design/`.

Task work under `spec/tasks/` is not listed as a registry file — those folders are opened directly when working on a task.
