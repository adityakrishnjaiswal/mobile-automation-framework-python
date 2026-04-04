"""Driver factory and lifecycle utilities for Appium sessions.

This module provides a pytest-friendly way to create and dispose of drivers.
It also hosts simple retry and locator fallback helpers to keep tests stable.
"""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

from appium import webdriver
from appium.options.common.base import AppiumOptions
from selenium.common.exceptions import NoSuchElementException, WebDriverException

from config.settings import EnvConfig
from drivers.dummy_driver import DummyDriver

logger = logging.getLogger(__name__)


def _options_from_caps(caps: Dict[str, Any]) -> AppiumOptions:
    opts = AppiumOptions()
    opts.load_capabilities(caps)
    return opts


def create_driver(env: EnvConfig):
    """Create and return an Appium driver based on the provided settings.

    Falls back to a lightweight DummyDriver when real device/server is not
    available. Controlled via USE_REAL_DEVICE env var (default: off).
    """

    use_real = os.getenv("USE_REAL_DEVICE", "0") == "1"
    if not use_real:
        logger.info("Using DummyDriver (USE_REAL_DEVICE not set).")
        return DummyDriver()

    try:
        options = _options_from_caps(env.capabilities)
        logger.info("Starting Appium session on %s for platform %s", env.server_url, env.platform)
        driver = webdriver.Remote(command_executor=env.server_url, options=options, keep_alive=True)
        driver.implicitly_wait(env.implicit_wait)
        driver.is_dummy = False
        return driver
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to start real driver (%s); falling back to DummyDriver.", exc)
        dummy = DummyDriver()
        dummy.startup_error = str(exc)
        return dummy


def quit_driver(driver) -> None:
    if getattr(driver, "is_dummy", False):
        return
    try:
        driver.quit()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Error quitting driver: %s", exc)


def find_with_fallback(driver, primary, alternates: Optional[list[Dict[str, str]]] = None):
    """Try primary locator then alternates.

    `primary` and each element in `alternates` should be a tuple (by, value) or dict
    with keys `by` and `value` for readability.
    """

    alternates = alternates or []
    try:
        return driver.find_element(*primary) if isinstance(primary, tuple) else driver.find_element(primary["by"], primary["value"])
    except NoSuchElementException:
        logger.debug("Primary locator failed, trying alternates (%d)", len(alternates))
        for alt in alternates:
            try:
                if isinstance(alt, tuple):
                    return driver.find_element(*alt)
                return driver.find_element(alt["by"], alt["value"])
            except NoSuchElementException:
                continue
        raise


__all__ = ["create_driver", "quit_driver", "find_with_fallback"]
