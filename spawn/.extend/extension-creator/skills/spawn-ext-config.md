---
name: spawn-ext-config
description: Declare and maintain config.yaml files, folders, ignores, setup hooks, and template layout under extsrc/files.
---

Goal: wire every template path under `extsrc/files/` into `config.yaml` with correct `mode`, `globalRead`/`localRead`, and optional `folders`/`setup`/`agent-ignore`/`git-ignore`.

1. List every file under `extsrc/files/`; each MUST have a matching key under `files:` (POSIX path relative to target root). Fix gaps before strict check.
2. For each path choose `mode`: `static` for shared methodology the pack may overwrite on update; `artifact` for repo-owned outputs (tasks, local notes) that must never be overwritten after creation.
3. Set `globalRead`/`localRead` so humans and agents discover the right docs (`required`/`auto`/`no`). Any non-`no` read flag needs a non-empty `description` under strict validation.
4. Use `folders:` for directories whose ownership/update policy matters even when templates are sparse.
5. Reference setup scripts only with basenames that exist under `extsrc/setup/`; hooks must be idempotent and safe for artifact data.
6. Run `spawn extension check . --strict` and fix reported issues.
7. **Version:** If these edits materially change what consumers get (paths, read surfaces, ignores, setup), **prompt** the author to bump **`version`** using **`spawn-ext-increment-version`** before tagging or publishing. Trivial typo-only fixes to existing templates may skip a bump — ask if unsure.
