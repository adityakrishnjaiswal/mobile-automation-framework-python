"""Base page object with common helpers and fallback-aware finders."""

import logging
from typing import Optional, Dict, Tuple, Any

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException

from drivers.driver_factory import find_with_fallback, LocatorInput


class BasePage:
    """Shared helpers for all pages.

    Provides consistent interaction helpers so individual pages stay lean and
    test code reads like a script. All methods return the element for fluent
    chaining in tests when desired.
    """

    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.log = logging.getLogger(self.__class__.__name__)

    def find(self, locator: LocatorInput, alternates: Optional[list[LocatorInput]] = None):
        """Find an element using primary locator and ordered fallbacks."""
        return find_with_fallback(self.driver, locator, alternates)

    def click(self, locator: LocatorInput, alternates: Optional[list[LocatorInput]] = None):
        """Tap/click an element; tolerates alternate locators."""
        elem = self.find(locator, alternates)
        elem.click()
        return elem

    def type(self, locator: LocatorInput, text: str, alternates: Optional[list[LocatorInput]] = None):
        """Clear then type into an element."""
        elem = self.find(locator, alternates)
        elem.clear()
        elem.send_keys(text)
        return elem

    def is_visible(self, locator: Tuple[str, str]) -> bool:
        """Return True if element exists and is displayed; False otherwise."""
        try:
            return self.driver.find_element(*locator).is_displayed()
        except NoSuchElementException:
            return False


__all__ = ["BasePage"]
