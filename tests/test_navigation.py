"""Sample navigation test."""

from __future__ import annotations

from pages.login_page import LoginPage
from pages.home_page import HomePage


def test_navigate_to_calls_tab(driver, creds):
    login = LoginPage(driver).login(creds["username"], creds["password"])
    home = HomePage(driver)
    home.open_calls()
    assert home.is_visible(home.calls_tab)
