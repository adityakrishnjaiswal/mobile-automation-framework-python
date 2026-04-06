"""Wait helpers to keep explicit waits readable."""

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webdriver import WebDriver
from typing import Tuple


def wait_for_clickable(driver: WebDriver, locator: Tuple[str, str], timeout: int = 15):
    """Wait until element is clickable and return it."""
    return WebDriverWait(driver, timeout).until(EC.element_to_be_clickable(locator))


def wait_for_visible(driver: WebDriver, locator: Tuple[str, str], timeout: int = 15):
    """Wait until element is visible and return it."""
    return WebDriverWait(driver, timeout).until(EC.visibility_of_element_located(locator))


__all__ = ["wait_for_clickable", "wait_for_visible"]
