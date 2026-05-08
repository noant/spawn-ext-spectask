# Step 3: Dual Jira backends and SOCKS-aware HTTP

## Goal
Implement `SelfHostedJiraClient` and `AtlassianCloudJiraClient` behind shared call surface `JiraBackend.get_issue_bundle`, `JiraBackend.list_open_issues`; apply proxy TLS settings from `SpectaskLocalConfig`.

## Approach
Implement `spectask_mcp/jira/types.py`: `IssueBundle` dataclass (`key`, `summary`, `fields` dict dump, `comments` ordered list text). Implement `spectask_mcp/jira/factory.py`: `backend_from_config(cfg: SpectaskLocalConfig) -> JiraBackend` protocol/class. Implement `spectask_mcp/jira/http_common.py`: `build_httpx_client(cfg) -> httpx.Client` honoring `proxy.enabled` (socks5 URL), `ignore_tls`. Self-hosted REST: Bearer PAT on `/rest/api/3/issue/{key}` with `expand=renderedFields` as needed plus paginated `/rest/api/3/issue/{key}/comment`. Cloud same paths against `cfg.jira.address` with Basic(email, api_token). Map `HTTPError`/timeouts to semantic `JiraConnectionError(message)` used by MCP/CLI layers.

## Affected files
- `spectask_mcp/jira/__init__.py` (new)
- `spectask_mcp/jira/types.py` (new)
- `spectask_mcp/jira/http_common.py` (new)
- `spectask_mcp/jira/base.py` (new, abstract `JiraBackend`)
- `spectask_mcp/jira/self_hosted.py` (new)
- `spectask_mcp/jira/cloud.py` (new)
- `spectask_mcp/jira/factory.py` (new)

## Code changes (before / after)

### `spectask_mcp/jira/base.py` — shared interface (new file)

**Before**
```python
(file absent)
```

**After**
```python
"""Abstract backend for issue fetch operations."""

from __future__ import annotations

from abc import ABC, abstractmethod

from spectask_mcp/jira.types import IssueBundle


class JiraBackend(ABC):
    @abstractmethod
    def get_issue_bundle(self, key: str) -> IssueBundle | None:
        ...

    @abstractmethod
    def list_open_issues(self, limit: int = 50) -> list[tuple[str, str]]:
        """Return tuples (key, summary)."""
```

Behavior: MCP and CLI depend on ABC only.

### `spectask_mcp/jira/self_hosted.py` — PAT client (new file)

**Before**
```python
(file absent)
```

**After**
```python
"""REST client for Jira Server/Data Center (self-hosted PAT)."""

from spectask_mcp.jira.base import JiraBackend
from spectask_mcp.config import SpectaskLocalConfig


class SelfHostedJiraClient(JiraBackend):
    def __init__(self, cfg: SpectaskLocalConfig): ...
```
Behavior: uses Bearer PAT; supports `ignore_tls` from shared httpx helper.

### `spectask_mcp/jira/cloud.py` — email + API token (new file)

**Before**
```python
(file absent)
```

**After**
```python
"""REST client for Atlassian Cloud (site URL + email/API token Basic)."""

from spectask_mcp.jira.base import JiraBackend
from spectask_mcp.config import SpectaskLocalConfig


class AtlassianCloudJiraClient(JiraBackend):
    def __init__(self, cfg: SpectaskLocalConfig): ...
```

Behavior: attaches Basic auth tuple to httpx client.

## Additional actions
- If bearer unsupported on legacy Jira, document fallback (Personal Access Token endpoints) as follow-up TODO in code comments only if discovered during integration testing.

