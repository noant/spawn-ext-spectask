# Step 2: Config model, path resolution, and interactive writer

## Goal
Implement typed loading of `spec/.config/config.yaml`, deterministic path resolution toward a repo `spec/` directory, and `interactive` prompts that serialize the schema from the task overview.

## Approach
Implement `spectask_mcp/config.py` with `@dataclass` or Pydantic model `SpectaskLocalConfig`, nested `JiraSection`/`ProxySection`, enum or `Literal` for `jira.type`. Functions: `resolve_workspace_with_spec() -> Path | None`, `config_yaml_path(workspace) -> Path`, `load_optional_config() -> SpectaskLocalConfig | None` (resolves path via workspace walk). Implement `spectask_mcp/config_prompts.py`: **`def run_interactive(*, prompted_by_setup: bool = False) -> int`**. When **`prompted_by_setup` is True** (invoked from `spectask-mcp interactive --setup`): if **`not sys.stdin.isatty()`**, return **`0`** immediately (headless). Otherwise print one line: configure Jira MCP now? (**default No** / **`[y/N]`**); on No return **`0`** without writing YAML. When **`prompted_by_setup` is False**, skip that gate. Then use `input()` / `getpass` for the remaining questions from `overview.md Details`, validate URLs and ports, normalize trailing slashes off Jira bases, write atomically (`tmp` + rename) to `config_yaml_path(ws)` once `spec/` ensured, create `.config/` (mode `0o700` where OS allows). Return **`0`** on success, non-zero on user cancel or invalid input after Yes.

## Affected files
- `spectask_mcp/config.py` (new)
- `spectask_mcp/config_prompts.py` (new)
- `spectask_mcp/cli.py` — pass **`prompted_by_setup`** from **`interactive --setup`** (`step 1`).

## Code changes (before / after)

### `spectask_mcp/config.py` — load/save helpers (new file)

**Before**
```python
(file absent)
```

**After**
```python
"""Load optional Jira config from spec/.config/config.yaml."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

import yaml

JiraType = Literal["self_hosted", "atlassian_cloud"]


@dataclass
class ProxySection:
    enabled: bool
    socks_host: str
    socks_port: int
    socks_username: str
    socks_password: str


@dataclass
class JiraSection:
    type: JiraType
    address: str
    ignore_tls: bool
    pat_token: str | None
    email: str | None
    api_token: str | None


@dataclass
class SpectaskLocalConfig:
    jira: JiraSection
    proxy: ProxySection


def resolve_workspace_with_spec(start: Path | None = None) -> Path | None:
    """Walk parents from start or cwd; return first directory that has subdirectory ./spec."""


def config_yaml_path(workspace: Path) -> Path:
    """`<workspace>/spec/.config/config.yaml` (call only when workspace is not None)."""
    return workspace / "spec" / ".config" / "config.yaml"


def load_optional_config(path: Path | None = None) -> SpectaskLocalConfig | None:
    """Resolve workspace with spec; load parsed config or None if file missing/unreadable/invalid."""
    ...
```

Behavior: centralized schema and safe parse; callers distinguish unset vs malformed.

### `spectask_mcp/config_prompts.py` — interactive writer (new file)

**Before**
```python
(file absent)
```

**After**
```python
"""Prompt for Jira-related settings and write spec/.config/config.yaml."""

from __future__ import annotations


def run_interactive(*, prompted_by_setup: bool = False) -> int:
    """Optional setup gate, then questionnaire; write YAML; return process exit code."""
    ...
```

Behavior: setup path asks first whether to configure; plain interactive runs full wizard immediately; masks token input via `getpass`; never blocks on stdin when non-TTY and **`prompted_by_setup`**.

## Additional actions
- Manual verify `spectask-mcp interactive` and `spectask-mcp interactive --setup`; pipe stdin closed / non-TTY exits `0` quickly for `--setup`.

