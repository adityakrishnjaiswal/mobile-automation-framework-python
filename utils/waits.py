"""Wait helpers to keep explicit waits readable."""

from __future__ import annotations

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def wait_for_clickable(driver, locator, timeout: int = 15):
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))


def wait_for_visible(driver, locator, timeout: int = 15):
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))


__all__ = ["wait_for_clickable", "wait_for_visible"]
