---
name: spawn-ext-verify
description: Validate extension layout with Spawn CLI and smoke-test install in a disposable target.
---

Goal: ship only packs that pass strict validation and install cleanly.

1. From extension source root: `spawn extension check . --strict` — resolve missing skills, undeclared files, descriptions for non-no read flags, bad `mcp.json`, missing setup scripts.
2. In a throwaway clone or empty repo: `spawn init`, then `spawn extension add <path-or-url-to-your-extension-source>` (match consumer workflow).
3. Confirm materialized paths under `files:` exist as expected; confirm `artifact` paths are not overwritten on a repeat add/update where applicable.
4. If `healthcheck` is configured: `spawn extension healthcheck <name>` from the target.
5. Document distribution: plain repo URL/path, zip, or entry in an `extensions.yaml` bundle for `spawn build install`.
