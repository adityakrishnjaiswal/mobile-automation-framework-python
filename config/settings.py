"""Centralized configuration handling for the mobile test framework.

This module loads environment-specific settings (dev/staging/etc.) and exposes
a simple data container that the rest of the framework can rely on. Values can
be overridden at runtime via environment variables to keep secrets like
BrowserStack credentials or app URLs out of source control.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Any
import os
import yaml


ROOT_DIR = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class EnvConfig:
    """Typed configuration snapshot for a single test run."""

    name: str
    platform: str
    server_url: str
    capabilities: Dict[str, Any]
    credentials: Dict[str, str]
    implicit_wait: int = 10


def _load_yaml(env_name: str) -> Dict[str, Any]:
    env_path = Path(__file__).parent / "environments" / f"{env_name}.yaml"
    if not env_path.exists():
        raise FileNotFoundError(
            f"Config file not found for env '{env_name}'. Expected at {env_path}"
        )
    with env_path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle)


def get_settings(env_name: str | None = None, platform: str | None = None) -> EnvConfig:
    """Return fully-resolved framework settings for the requested env/platform.

    Order of precedence for overrides:
    1) Environment variables
    2) YAML in `config/environments/<env>.yaml`
    """

    resolved_env = (env_name or os.getenv("TEST_ENV", "dev")).lower()
    resolved_platform = (platform or os.getenv("APP_PLATFORM", "android")).lower()

    yaml_data = _load_yaml(resolved_env)

    if resolved_platform not in yaml_data.get("platforms", {}):
        raise ValueError(
            f"Platform '{resolved_platform}' not configured for env '{resolved_env}'."
        )

    platform_block = yaml_data["platforms"][resolved_platform]

    bs_user = os.getenv("BS_USER", yaml_data.get("bs_user", ""))
    bs_key = os.getenv("BS_KEY", yaml_data.get("bs_key", ""))
    raw_server_url = yaml_data.get("server_url", "http://localhost:4723/wd/hub")
    server_url = raw_server_url.format(user=bs_user, key=bs_key)

    capabilities = dict(platform_block.get("capabilities", {}))
    app_override = os.getenv("APP_URL")
    if app_override:
        capabilities["appium:app"] = app_override
    elif platform_block.get("app"):
        capabilities.setdefault("appium:app", platform_block["app"])

    credentials = {
        "username": os.getenv(
            "TEST_EMAIL", yaml_data.get("credentials", {}).get("username", "demo@example.com")
        ),
        "password": os.getenv(
            "TEST_PASS", yaml_data.get("credentials", {}).get("password", "Password!23")
        ),
    }

    implicit_wait = int(os.getenv("IMPLICIT_WAIT", yaml_data.get("implicit_wait", 10)))

    return EnvConfig(
        name=resolved_env,
        platform=resolved_platform,
        server_url=server_url,
        capabilities=capabilities,
        credentials=credentials,
        implicit_wait=implicit_wait,
    )


__all__ = ["EnvConfig", "get_settings", "ROOT_DIR"]
