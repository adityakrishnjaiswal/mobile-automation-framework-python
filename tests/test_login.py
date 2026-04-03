"""Sample login test using POM and fixtures."""

from __future__ import annotations

from pages.login_page import LoginPage


def test_user_can_login(driver, creds):
    login = LoginPage(driver)
    login.login(creds["username"], creds["password"])
    assert login.is_logged_in()
