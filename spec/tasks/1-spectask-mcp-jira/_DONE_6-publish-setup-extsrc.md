# Step 6: PyPI publish script, MCP JSON, ignores, setup hook

## Goal
Publish `spectask-mcp` with `scripts/publish.py`; add extension MCP entries, ignore rules for `spec/.config/`, and `after-install` uv install/upgrade wiring.

## Approach
Extend `scripts/publish.py`:
- Rename env token default expectation to project-specific documented name (`SPECTASK_MCP_PYPI_TOKEN`).
- `--pyproject` argparse default `./pyproject.toml`.
- Preserve bump-version + clean `dist/` + `uv build` + `uv publish` sequencing.

Seed `extsrc/mcp/`:
- Follow `spawn-ext-guide/ai/mcp-json.md` — three files `{windows,linux,macos}.json` with aligned `servers[].name` e.g. `spectask-mcp-jira`, stdio `command` / `args` invoking `spectask-mcp` + `serve` (or `python -m spectask_mcp serve` on Windows if needed).

Update `extsrc/config.yaml`:
- `agent-ignore` and `git-ignore` include `spec/.config/**` (or `spec/.config/config.yaml`).
- `folders:` add `spec/.config` with `mode: artifact` if extension schema requires declared folders for generated content.
- `setup.after-install: install_spectask_mcp.py` under `extsrc/setup/`.

Implement `extsrc/setup/install_spectask_mcp.py`:
- Use `subprocess.run(['uv', 'pip', 'install', 'spectask-mcp'], check=False)` then `['uv', 'pip', 'install', '--upgrade', 'spectask-mcp']` (or equivalent single command with upgrade semantics). Log non-zero but do not fail extension install hard unless team policy says otherwise — **default:** exit `0` after best-effort with stderr message on failure.
- Then run `subprocess.run(['spectask-mcp', 'interactive', '--setup'], cwd=<workspace root as provided by setup context or `os.getcwd()`>, check=False)`. If `spectask-mcp` missing on PATH after install, try `python -m spectask_mcp interactive --setup` (platform-specific `python3` on Linux if needed). Implementer follows Spawn `after-install` contract for `cwd` when documented in `spawn-ext-guide`.

## Affected files
- `scripts/publish.py` — `main`, argparse, docstring, token env name
- `extsrc/mcp/windows.json` (new or extend `{"servers":[]}`)
- `extsrc/mcp/linux.json` (new)
- `extsrc/mcp/macos.json` (new)
- `extsrc/config.yaml`
- `extsrc/setup/install_spectask_mcp.py` (new)

## Code changes (before / after)

### `scripts/publish.py` — generalize branding and path

**Before**
```python
_TOKEN_ENV = "SPAWN_CLI_PYPI_TOKEN"
_MSG_PREFIX = "spawn-cli publish:"
...
def main() -> None:
    p = argparse.ArgumentParser(
        description="spawn-cli: uv build + uv publish to PyPI",
    )
...
    token = args.token or os.environ.get(_TOKEN_ENV)
...
    bump_pyproject_version(pyproject)

    remove_dist_build_artifacts(root / "dist")

    _run(["uv", "build"], cwd=root)
```

**After**
```python
_TOKEN_ENV = "SPECTASK_MCP_PYPI_TOKEN"
_MSG_PREFIX = "spectask-mcp publish:"
...
def main() -> None:
    p = argparse.ArgumentParser(
        description="spectask-mcp: uv build + uv publish to PyPI",
    )
    p.add_argument(
        "--pyproject",
        type=Path,
        default=None,
        help="Path to pyproject.toml (default: <repo-root>/pyproject.toml)",
    )
...
    pyproject = (args.pyproject if args.pyproject is not None else root / "pyproject.toml").resolve()
    if not pyproject.is_file(): ...
...
    pkg_root = pyproject.parent
    _run(["uv", "build"], cwd=pkg_root)
    _run(["uv", "publish"], cwd=pkg_root, env=publish_env)
```

Behavior:
- Bump version in referenced `pyproject.toml`.
- Runs `uv build` / `publish` with `cwd == pyproject.parent` so dist lands next to manifest.
- Cleans `dist/` under same parent.

Dist path note: `_repo_root()` may still derive git root — implementer aligns `dist` cleanup with chosen `cwd` (pyproject parent) not necessarily git root unless same.

### `extsrc/config.yaml` — MCP + ignores + setup

**Before**
```yaml
schema: 1
name: spectask
version: "1.2.9"

folders:
  spec/tasks:
    mode: artifact
  spec/seeds:
    mode: artifact

agent-ignore:
  - spec/seeds/_DONE_*.md
  - spec/tasks/**/_DONE_*/_DONE_*.md

files:
...
```

**After**
```yaml
schema: 1
name: spectask
version: "1.2.9"

folders:
  spec/tasks:
    mode: artifact
  spec/seeds:
    mode: artifact
  spec/.config:
    mode: artifact

agent-ignore:
  - spec/seeds/_DONE_*.md
  - spec/tasks/**/_DONE_*/_DONE_*.md
  - spec/.config/**

git-ignore:
  - spec/.config/**

setup:
  after-install: install_spectask_mcp.py

...
```

Exact YAML keys follow `spawn-ext-guide/ai/config-yaml.md` if `folders` dotted paths require quoting — adjust to valid YAML (`"spec/.config":` mapping key).

Behavior: Spawn installs MCP definitions; hides local secrets from indexing; installs wheel then offers optional Jira config wizard (skipped when non-interactive).

### `extsrc/mcp/linux.json` — sample server stanza (new file)

**Before**
```text
(file absent)
```

**After**
```json
{
  "servers": [
    {
      "name": "spectask-mcp-jira",
      "transport": {
        "type": "stdio",
        "command": "spectask-mcp",
        "args": ["serve"]
      }
    }
  ]
}
```

Behavior: duplicate structure to `windows.json` / `macos.json` adjusting `command` if necessary.

## Additional actions
- Run `spawn extension check .` after edits (local dev).
