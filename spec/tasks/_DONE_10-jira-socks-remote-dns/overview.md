# 10: Jira SOCKS proxy remote DNS (socks5h)

## Source seed
- Path: none

## Status
- [V] Spec created
- [V] Self spec review passed
- [V] Spec review passed
- [V] Code implemented
- [V] Self code review passed
- [V] Code review passed
- [V] Design documents updated

## Goal
Expose optional SOCKS5 remote DNS for the Jira HTTP client so hostnames resolve on the proxy (socks5h) when local DNS cannot resolve the Jira host.

## Design overview
- Affected modules: local config load/serialize, Jira pycontribs factory, interactive config wizard.
- Files and symbols:
  - `spectask_mcp/config.py` -- `ProxySection`, `_parse_proxy_section`, `config_to_ordered_dict`
  - `spectask_mcp/jira/pycontribs_factory.py` -- `_socks_proxy_url`, `connect_jira_client`
  - `spectask_mcp/config_prompts.py` -- `run_interactive`
- Data flow changes: When `proxy.remote_dns` is true, `proxies` passed into `jira.JIRA` use `socks5h://` URLs so hostname resolution for the Jira server happens via the SOCKS proxy; when false or omitted in YAML, behavior stays `socks5://` with local resolution.
- Integration points: `spec/.config/config.yaml` `proxy.remote_dns`; CLI `spectask-mcp interactive` and `spectask-mcp interactive --setup` (same `run_interactive` path).

## Before -> After

### Before
- SOCKS URL was always `socks5://`; Jira hostname was resolved by the OS before the proxy tunnel, which fails for internal names without local DNS or VPN.

### After
- YAML and wizard can set `remote_dns`; library stack uses `socks5h://` when enabled so the proxy performs name resolution.

## Details
- Config key: `proxy.remote_dns` (boolean). Missing key parses as `false` (backward compatible).
- Interactive: after SOCKS host, port, optional credentials, ask: `Resolve Jira hostname through the proxy (remote DNS / socks5h)?` with default No (empty = false).
- Depends on PySocks/urllib3 supporting `socks5h` in proxy URLs (same stack as existing SOCKS5 support).

## Execution Scheme
> Each step id is the subtask filename.
> MANDATORY! Each step is executed by a dedicated subagent (Task tool). Do NOT implement inline. No exceptions -- even if a step seems trivial or small.
- Phase 1 (sequential): step `_DONE_1-config-proxy-remote-dns` -> step `_DONE_2-interactive-proxy-remote-dns`
- Phase 2 (sequential): step review -- inspect all changes, fix inconsistencies
