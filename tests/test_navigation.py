"""Sample navigation test."""

import os
import pytest

# Abort collection early unless explicitly enabled; keeps CI green by default.
if os.getenv("RUN_MOBILE_TESTS") != "true":
    pytest.skip("Skipping mobile tests in CI", allow_module_level=True)

from pages.login_page import LoginPage
from pages.home_page import HomePage


@pytest.mark.requires_device
def test_navigate_to_calls_tab(driver, creds):
    """Login and navigate to Calls tab using POM helpers."""
    login = LoginPage(driver).login(creds["username"], creds["password"])
    home = HomePage(driver)
    home.open_calls()
    assert home.is_visible(home.calls_tab)
