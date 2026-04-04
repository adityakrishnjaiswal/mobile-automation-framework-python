"""Lightweight dummy driver so tests can run without real devices."""

from dataclasses import dataclass
from typing import Any

from selenium.common.exceptions import NoSuchElementException


@dataclass
class DummyElement:
    locator: Any

    def click(self):
        return True

    def clear(self):
        return True

    def send_keys(self, *_args, **_kwargs):
        return True

    def is_displayed(self):
        return True


class DummyDriver:
    """Minimal interface-compatible stand-in for WebDriver."""

    def __init__(self):
        self.implicitly_wait_time = 0
        self.is_dummy = True
        self.startup_error = None

    def implicitly_wait(self, seconds: int):
        self.implicitly_wait_time = seconds

    def find_element(self, *_args, **_kwargs):
        # Always return an element so locator fallback never fails in dummy mode
        return DummyElement(locator=_args or _kwargs)

    def quit(self):
        return True

    # Compatibility with simple swipe usage if added later
    def swipe(self, *_args, **_kwargs):
        return True

    def get_window_size(self):
        return {"width": 1080, "height": 1920}


__all__ = ["DummyDriver", "DummyElement"]
