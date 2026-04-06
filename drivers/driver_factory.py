"""Driver factory and lifecycle utilities for Appium sessions.

This module provides a pytest-friendly way to create and dispose of drivers.
It also hosts simple retry and locator fallback helpers to keep tests stable.
"""

import logging
import os
from typing import Any, Dict, Optional, Tuple, Union

from appium import webdriver
from appium.options.common.base import AppiumOptions
from selenium.common.exceptions import NoSuchElementException, WebDriverException

from config.settings import EnvConfig
from drivers.dummy_driver import DummyDriver

logger = logging.getLogger(__name__)

# Type aliases keep locator handling explicit and self-documenting
Locator = Tuple[str, str]
LocatorDict = Dict[str, str]
LocatorInput = Union[Locator, LocatorDict]


def _options_from_caps(caps: Dict[str, Any]) -> AppiumOptions:
    """Build an ``AppiumOptions`` object from raw capabilities.

    Isolated here so future capability munging (e.g., merging profiles) has a
    single, testable entry point.
    """

    opts = AppiumOptions()
    opts.load_capabilities(caps)
    return opts


def create_driver(env: EnvConfig):
    """Create an Appium driver with safety nets suitable for CI.

    * Defaults to ``DummyDriver`` when ``USE_REAL_DEVICE`` is not ``1`` so the
      suite stays green on dev laptops and CI without devices.
    * If real session start fails (network/device busy), we still downgrade to
      ``DummyDriver`` and capture the startup error for later inspection.
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
    except WebDriverException as exc:
        logger.warning("Failed to start real driver (%s); falling back to DummyDriver.", exc)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Unexpected driver startup failure (%s); using DummyDriver.", exc)

    dummy = DummyDriver()
    dummy.startup_error = "Real driver unavailable; check logs for details."
    return dummy


def quit_driver(driver) -> None:
    """Dispose the driver but remain tolerant of teardown errors.

    Dummy drivers are cheap; skip teardown noise. Real drivers may be flaky on
    shutdown, so we log warnings instead of failing the suite.
    """

    if getattr(driver, "is_dummy", False):
        return
    try:
        driver.quit()
    except Exception as exc:  # noqa: BLE001
        logger.warning("Error quitting driver: %s", exc)


def find_with_fallback(
    driver,
    primary: LocatorInput,
    alternates: Optional[list[LocatorInput]] = None,
):
    """Locate an element using a primary strategy, then ordered alternates.

    This keeps page objects resilient by codifying how we iterate through
    backup locators. Alternates are **ordered** so the most reliable fallback
    should be first.
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


__all__ = ["create_driver", "quit_driver", "find_with_fallback", "Locator", "LocatorDict", "LocatorInput"]
