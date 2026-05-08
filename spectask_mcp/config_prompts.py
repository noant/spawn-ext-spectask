"""Prompt for Jira-related settings and write spec/.config/config.yaml."""

from __future__ import annotations

import os
import sys
import tempfile
from getpass import getpass
from pathlib import Path

import yaml

from spectask_mcp.config import (
    JiraSection,
    ProxySection,
    SpectaskLocalConfig,
    config_to_ordered_dict,
    config_yaml_path,
    is_valid_http_url,
    normalize_jira_base_url,
    resolve_workspace_with_spec,
)


def _ensure_spec_and_config_dirs(workspace: Path) -> Path:
    """Ensure `<workspace>/spec` and `<workspace>/spec/.config` exist; chmod `.config` to 0o700 when supported."""
    spec_dir = workspace / "spec"
    spec_dir.mkdir(parents=True, exist_ok=True)
    cfg_dir = workspace / "spec" / ".config"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    try:
        cfg_dir.chmod(0o700)
    except (NotImplementedError, OSError):
        pass
    return cfg_dir


def _atomic_write_yaml(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix="config.",
        suffix=".tmp",
        dir=str(path.parent),
    )
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            yaml.safe_dump(
                payload,
                handle,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )
        os.replace(tmp_path, path)
    except Exception:
        try:
            tmp_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def _prompt_yes_no(prompt: str, *, default_no: bool) -> bool | None:
    """Return True/False, or None on EOF or unrecognized answer."""
    hint = "[y/N]" if default_no else "[Y/n]"
    try:
        raw = input(f"{prompt} {hint}: ").strip().lower()
    except EOFError:
        return None
    if raw == "":
        return not default_no
    if raw in ("y", "yes"):
        return True
    if raw in ("n", "no"):
        return False
    return None


def _prompt_nonempty(prompt: str) -> str | None:
    try:
        value = input(prompt).strip()
    except EOFError:
        return None
    if not value:
        return None
    return value


def _prompt_optional_line(prompt: str) -> str | None:
    """Return line (possibly empty), or None on EOF."""
    try:
        return input(prompt).strip()
    except EOFError:
        return None


def _prompt_port(prompt: str) -> int | None:
    try:
        raw = input(prompt).strip()
    except EOFError:
        return None
    try:
        n = int(raw, 10)
    except ValueError:
        return None
    if 1 <= n <= 65535:
        return n
    return None


def _prompt_jira_type() -> str | None:
    print(
        "Choose Jira deployment:\n"
        "  1) Self-hosted server\n"
        "  2) Atlassian Cloud\n",
        end="",
    )
    try:
        raw = input("Enter choice (1 or 2): ").strip()
    except EOFError:
        return None
    if raw == "1":
        return "self_hosted"
    if raw == "2":
        return "atlassian_cloud"
    return None


def _prompt_url(prompt: str) -> str | None:
    try:
        raw = input(prompt).strip()
    except EOFError:
        return None
    normalized = normalize_jira_base_url(raw)
    if not is_valid_http_url(normalized):
        return None
    return normalized


def run_interactive(*, prompted_by_setup: bool = False) -> int:
    """Optional setup gate, then questionnaire; write YAML; return process exit code."""
    if prompted_by_setup and not sys.stdin.isatty():
        return 0

    try:
        if prompted_by_setup:
            yn = _prompt_yes_no("Configure Jira MCP now?", default_no=True)
            if yn is None:
                print("Answer y or n (empty means No); aborted.", file=sys.stderr)
                return 1
            if not yn:
                return 0

        workspace = resolve_workspace_with_spec()
        if workspace is None:
            workspace = Path.cwd()
            try:
                (workspace / "spec").mkdir(parents=False, exist_ok=True)
            except OSError as exc:
                print(f"Could not create ./spec directory: {exc}", file=sys.stderr)
                return 1

        _ensure_spec_and_config_dirs(workspace)

        jira_type = _prompt_jira_type()
        if jira_type is None:
            print("Invalid or missing choice; aborted.", file=sys.stderr)
            return 1

        ignore_tls = False
        address: str | None = None
        pat_token: str | None = None
        email: str | None = None
        api_token: str | None = None

        if jira_type == "self_hosted":
            while True:
                address = _prompt_url(
                    "Jira base URL (https://jira.example.com): ",
                )
                if address is not None:
                    break
                print("Enter a valid http(s) URL with a host.", file=sys.stderr)

            while True:
                secret = getpass("Personal access token (input hidden): ")
                if secret != "":
                    pat_token = secret
                    break
                print("Token must not be empty.", file=sys.stderr)

            yn_tls = _prompt_yes_no(
                "Ignore TLS certificate verification?",
                default_no=True,
            )
            if yn_tls is None:
                print("Answer y or n (empty means No); aborted.", file=sys.stderr)
                return 1
            ignore_tls = yn_tls

        else:
            while True:
                em = _prompt_nonempty("Atlassian account email: ")
                if em is None:
                    print("Email required; aborted.", file=sys.stderr)
                    return 1
                if "@" in em:
                    email = em
                    break
                print("Enter an email address.", file=sys.stderr)

            while True:
                secret = getpass("Atlassian API token (input hidden): ")
                if secret != "":
                    api_token = secret
                    break
                print("API token must not be empty.", file=sys.stderr)

            while True:
                address = _prompt_url(
                    "Jira site URL (https://your-domain.atlassian.net): ",
                )
                if address is not None:
                    break
                print("Enter a valid http(s) URL with a host.", file=sys.stderr)

        yn_proxy = _prompt_yes_no("Use a SOCKS5 proxy?", default_no=True)
        if yn_proxy is None:
            print("Answer y or n (empty means No); aborted.", file=sys.stderr)
            return 1
        proxy_enabled = yn_proxy

        socks_host = "127.0.0.1"
        socks_port = 1080
        socks_username = ""
        socks_password = ""

        if proxy_enabled:
            host = _prompt_nonempty("SOCKS5 host: ")
            if host is None:
                print("Host required; aborted.", file=sys.stderr)
                return 1
            socks_host = host

            while True:
                port = _prompt_port("SOCKS5 port (1-65535): ")
                if port is not None:
                    socks_port = port
                    break
                print("Enter a valid integer port between 1 and 65535.", file=sys.stderr)

            opt_user = _prompt_optional_line("SOCKS5 username (optional, Enter to skip): ")
            if opt_user is None:
                print("No input; aborted.", file=sys.stderr)
                return 1
            socks_username = opt_user

            socks_password = getpass("SOCKS5 password (optional, input hidden): ")

        jira = JiraSection(
            type=jira_type,
            address=address,
            ignore_tls=ignore_tls,
            pat_token=pat_token,
            email=email,
            api_token=api_token,
        )
        proxy = ProxySection(
            enabled=proxy_enabled,
            socks_host=socks_host,
            socks_port=socks_port,
            socks_username=socks_username,
            socks_password=socks_password,
        )
        cfg = SpectaskLocalConfig(jira=jira, proxy=proxy)
        target = config_yaml_path(workspace)
        _atomic_write_yaml(target, config_to_ordered_dict(cfg))

    except KeyboardInterrupt:
        print("", file=sys.stderr)
        print("Interrupted.", file=sys.stderr)
        return 130

    return 0
