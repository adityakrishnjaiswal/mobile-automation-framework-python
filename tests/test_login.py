import os
import pytest

if os.getenv("RUN_MOBILE_TESTS") != "true":
    pytest.skip("Skipping mobile tests in CI", allow_module_level=True)
"""Sample login test using POM and fixtures."""

from __future__ import annotations

import os
import pytest

if os.getenv("RUN_MOBILE_TESTS") != "true":
    pytest.skip("Skipping mobile tests in CI", allow_module_level=True)

from pages.login_page import LoginPage


@pytest.mark.requires_device
def test_user_can_login(driver, creds):
    login = LoginPage(driver)
    login.login(creds["username"], creds["password"])
    assert login.is_logged_in()
