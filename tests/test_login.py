"""Sample login test using POM and fixtures."""

import os
import pytest

# Abort collection early unless explicitly enabled; keeps CI green by default.
if os.getenv("RUN_MOBILE_TESTS") != "true":
    pytest.skip("Skipping mobile tests in CI", allow_module_level=True)

from pages.login_page import LoginPage


@pytest.mark.requires_device
def test_user_can_login(driver, creds):
    """User should reach chat tab after authenticating with valid creds."""
    login = LoginPage(driver)
    login.login(creds["username"], creds["password"])
    assert login.is_logged_in()
