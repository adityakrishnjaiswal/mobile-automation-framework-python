"""Base page object with common helpers and fallback-aware finders."""

from __future__ import annotations

import logging
from typing import Optional, Dict
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.common.exceptions import NoSuchElementException

from drivers.driver_factory import find_with_fallback


class BasePage:
    def __init__(self, driver: WebDriver):
        self.driver = driver
        self.log = logging.getLogger(self.__class__.__name__)

    def find(self, locator: tuple[str, str], alternates: Optional[list[Dict[str, str]]] = None):
        return find_with_fallback(self.driver, locator, alternates)

    def click(self, locator: tuple[str, str], alternates: Optional[list[Dict[str, str]]] = None):
        elem = self.find(locator, alternates)
        elem.click()
        return elem

    def type(self, locator: tuple[str, str], text: str, alternates: Optional[list[Dict[str, str]]] = None):
        elem = self.find(locator, alternates)
        elem.clear()
        elem.send_keys(text)
        return elem

    def is_visible(self, locator: tuple[str, str]) -> bool:
        try:
            return self.driver.find_element(*locator).is_displayed()
        except NoSuchElementException:
            return False


__all__ = ["BasePage"]
