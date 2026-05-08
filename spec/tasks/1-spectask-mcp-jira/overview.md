# 1: spectask-mcp (Jira MCP and task import)

## Source seed
- Path: none

## Status
- [x] Spec created
- [x] Self spec review passed
- [x] Spec review passed
- [x] Code implemented
- [x] Self code review passed
- [ ] Code review passed
- [ ] Design documents updated

## Goal
Ship a PyPI-installable `spectask-mcp` CLI and stdio MCP server that optionally connects to a **ticket system** (self-hosted PAT or Atlassian Cloud as common deployments), stores local config under `spec/.config/config.yaml`, integrates with the Spectask extension (`extsrc`), and documents task-folder naming when `task-code` matches an external ticket key.

## Design overview
- Affected modules: new Python package tree under `spectask_mcp/` plus **`pyproject.toml` at repo root** (published project `spectask-mcp`), `scripts/publish.py`, `extsrc/config.yaml`, new `extsrc/mcp/*.json`, new `extsrc/setup/` script, new `extsrc/skills/*.md`, mirrored `extsrc/files/spec/main.md`, repo `spec/main.md`.
- Files and symbols (paths to create or change):
  - `spectask_mcp/__init__.py`, `spectask_mcp/cli.py` (`main`, argparse: `interactive` + `--setup`, `run`, `serve`), `spectask_mcp/config.py` (`SpectaskLocalConfig`, `resolve_workspace_with_spec`, `config_yaml_path`, `load_optional_config`), `spectask_mcp/config_prompts.py` (`run_interactive(prompted_by_setup=...)`), `spectask_mcp/jira/base.py` (abstract `JiraBackend`: `get_issue_bundle`, `list_open_issues`), `spectask_mcp/jira/self_hosted.py` (`SelfHostedJiraClient`), `spectask_mcp/jira/cloud.py` (`AtlassianCloudJiraClient`), `spectask_mcp/jira/factory.py` (`backend_from_config`), `spectask_mcp/mcp_app.py` (`run_stdio`), `spectask_mcp/run_cmd.py` (`run_once`), optional `spectask_mcp/jira_actions.py` (`query_jira`).
  - `pyproject.toml` (repo root): `[project] name = "spectask-mcp"`, `[project.scripts] spectask-mcp = spectask_mcp.cli:main`, deps `mcp`, `httpx[socks]` (or equivalent SOCKS-capable stack), `PyYAML`, `version`.
  - `scripts/publish.py`: `main()`, optional `--pyproject` default `repo/pyproject.toml`, keep bump + `uv build` + `uv publish` behavior; refresh docstrings and env token name (`SPECTASK_MCP_PYPI_TOKEN` suggested; document migration from `SPAWN_CLI_PYPI_TOKEN` if removed).
  - `extsrc/config.yaml`: `git-ignore` / `agent-ignore` entries for `spec/.config/` (or `spec/.config/config.yaml`); `folders.spec/.config` artifact mode if required by Spawn schema; `setup.after-install` pointing to `setup/install_spectask_mcp.py`; new skill registration; optional `files` row for `spec/.config/config.yaml` description (local-only).
  - `extsrc/mcp/windows.json`, `linux.json`, `macos.json`: server `spectask-mcp-jira` (unique name), `stdio` transport, `command`/`args` invoking installed `spectask-mcp serve` (or `python -m spectask_mcp` per platform), **no secrets in repo** (`env` only if placeholders).
  - `extsrc/skills/spectask-task-from-jira.md`: workflow import a ticket into `spec/tasks/{KEY}-{slug}/`; fallback manual key + text when unreachable or missing config.
  - `spec/main.md` and `extsrc/files/spec/main.md`: broad English instructions for `spec/tasks/{task-code}-{slug}/`, suggested serial `task-code`, user confirmation when not ticket-sourced, ticket key as `task-code` when applicable; add `spec/.config/config.yaml` (see methodology there only).
- Data flow:
  - `interactive`: prompts -> validate -> write YAML to `spec/.config/config.yaml` (create parent dirs). Extension setup invokes `spectask-mcp interactive --setup`: first prompt asks whether to configure now; **No** exits `0` without changing files; **Yes** continues with full wizard. Plain `spectask-mcp interactive` (manual) skips that gate and starts at host type.
  - `serve`: read config -> if missing/invalid YAML or missing required keys for the configured ticket connector -> MCP server exposes **zero tools** (empty tool list).
  - `serve` with valid config: register tools (e.g. `jira_query`) that fetch by issue key or list open issues when key absent/unknown; TLS verify flag honored; SOCKS proxy applied to HTTP layer.
  - `run [--issue ISSUE]` same fetching rules for stdout (human-readable or JSON lines TBD in implementation; prefer stable text for scripting).
- Integration points: PyPI `spectask-mcp`, Spawn extension MCP merge (`extsrc/mcp`), extension `setup.after-install` installs/upgrades the wheel then runs `spectask-mcp interactive --setup` (see Extension setup). If stdin is not a TTY, `run_interactive(prompted_by_setup=True)` returns `0` immediately without prompts (headless install).

## Before -> After

### Before
- No standalone ticket-system MCP package in-repo yet; untracked `scripts/publish.py` targets spawn-cli-only narrative; methodology does not describe `spec/.config/` or ticket-key task dirs; Spectask extension has no MCP server or ticket import skill.

### After
- Installable `spectask-mcp` with `interactive` / `interactive --setup` / `run` / `serve`; local config at `spec/.config/config.yaml` (ignored from VCS/agent); extension bundle runs setup hook plus optional wizard gate; methodology (in `spec/main.md` only) documents task folders and external ticket keys in English.

## Details

### Config file (`spec/.config/config.yaml`)

Written only by `interactive` (manual edit allowed locally). Example shape:

```yaml
jira:
  type: self_hosted          # self_hosted | atlassian_cloud
  address: "https://jira.example.com"
  pat_token: "..."           # self_hosted only
  ignore_tls: false          # maps from prompt "ignore TLS certificate"
  # atlassian_cloud: use email + api_token; address is site URL e.g. https://your-domain.atlassian.net
  email: ""
  api_token: ""
proxy:
  enabled: false
  socks_host: "127.0.0.1"
  socks_port: 1080
  socks_username: ""
  socks_password: ""
```

Interactive flow (mirror user request):

- With `prompted_by_setup=True` (extension setup): step **0** — ask whether to configure the ticket connector for spectask-mcp now (**default No**); if No, exit `0` unchanged.
- Then (manual `interactive`, or setup after Yes): **1.** Ask hosted type -> `jira.type` (`self_hosted` vs `atlassian_cloud`; UI labels: self-hosted vs Atlassian Cloud servers).
- **2.** If self-hosted: address, PAT token, ignore TLS yes/no (`ignore_tls`).
- **3.** If Atlassian Cloud: email + API token; site/base URL (`address`).
- **4.** Ask SOCKS5 proxy yes/no (`proxy.enabled`); if yes, host, port, optional user/password.

Naming: CLI flags / internal Python use snake_case (`ignore_tls`); user-visible messages plain English.

### Ticket system connectivity

Two strategies share one facade (`JiraClient`): same method signatures; implementation modules differ (auth headers, base URL normalization). Self-hosted: PAT in `Authorization: Bearer` (or document server version caveats in code comments if Bearer unsupported). Cloud: Basic `email:api_token` or documented supported scheme for Atlassian Cloud ticket REST (Jira-compatible API v3).

Open issues: default JQL e.g. `resolution = Unresolved ORDER BY updated DESC` capped to a reasonable limit (configurable constant, e.g. 50) unless extended later.

Full issue payload: fields, description, status, assignee, and **all comments** (paginate comment API if needed). On connection error: tool/CLI returns a clear **ticket system unreachable** message (no stack trace in tool result).

### MCP behavior

- No valid config file: start stdio server with **no tools** (permitted by MCP; optional `list_tools` empty).
- Valid config: expose at least one tool, e.g. `jira_query` with optional `issue_key` string.
  - If `issue_key` provided and found: return full serialized issue + comments.
  - If `issue_key` missing or not found: return list of current open issues (summary + key).
  - If server down: structured error text in tool result.

### CLI

- `spectask-mcp interactive` -- write/update config (full wizard, no "configure?" gate).
- `spectask-mcp interactive --setup` -- same as above after optional "configure now?" gate (used by extension setup).
- `spectask-mcp run [--issue KEY]` -- one-shot fetch using config (stdout).
- `spectask-mcp serve` -- stdio MCP (used by `extsrc/mcp`).

### Publishing

- `scripts/publish.py` must build/publish the `spectask-mcp` package (path via flag or default to new `spectask_mcp/pyproject.toml`). Token env var name: keep or generalize (document in script docstring; e.g. `SPECTASK_MCP_PYPI_TOKEN` vs reuse existing if intentional).

### Extension setup

`after-install` script: (1) `uv pip install spectask-mcp` then `uv pip install --upgrade spectask-mcp` (no uninstall). (2) Run `spectask-mcp interactive --setup` with working directory on the target workspace when Spawn provides it, else process `cwd` – so `spec/` resolution matches the repo being set up. Headless / non-interactive sessions skip all questions (no hang).

### Task folders and task-code

- Folders live under **`spec/tasks/{task-code}-{slug}/`**: **`task-code`** is the identifying **code** for the spectask (**not necessarily** "just the next integer" unless you chose a numeric serial convention); **`slug`** is a short name (`-`-separated).
- **Suggested next numeric serial:** When continuing the usual numeric style (leading segment digits-only among existing tasks), compute **suggested** `1 + max(...)` among those folders (**include** `_DONE_{id}-*`). **If the task is not imported from an external ticket tracker:** present that suggestion to the user and **wait for explicit agreement** (or another allowed `task-code`) before creating the folder; do not finalize silently.
- **Imported from an external ticket tracker** (skill / import): **`task-code` must equal the ticket key** (for example **`PROJ-123`**); user-confirmation loop for numeric suggestions does **not** apply to that key. Slug follows as additional segments after another `-`.

### Typo corrections vs prompt

- Use `ignore_tls` (not "ingore").
- Use `atlassian_cloud` (not "atlasian server") in YAML.

### Open implementation choices (defaults)

- Python 3.11+.
- Official `mcp` PyPI package for stdio server.
- `httpx` for HTTP; SOCKS via documented extra or `httpx[socks]`.
- Config discovery: walk up from CWD for the first directory that contains `./spec`; config path is `{that}/spec/.config/config.yaml`. If absent, optionally create `./spec/` under CWD plus `.config/` (document in skill).


## Execution Scheme
> Each step id is the subtask filename (e.g. `_DONE_1-package-cli.md`). Completed steps are renamed with a `_DONE_` prefix per spec/main.md Step 4.
> MANDATORY! Each step is executed by a dedicated subagent (Task tool). Do NOT implement inline. No exceptions — even if a step seems trivial or small.
- Phase 1 (sequential): step `_DONE_1-package-cli` -> `_DONE_2-config-interactive` -> `_DONE_3-jira-clients`
- Phase 2 (parallel): `_DONE_4-mcp-server` || `_DONE_5-cli-run`
- Phase 3 (sequential): `_DONE_6-publish-setup-extsrc` -> `_DONE_7-methodology-skill-mirror`
