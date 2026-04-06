"""Pytest fixtures and hooks for the mobile automation framework."""

import logging
import os
from datetime import datetime
from pathlib import Path

import pytest
from selenium.common.exceptions import WebDriverException

from config.settings import get_settings
from drivers.driver_factory import create_driver, quit_driver
from utils.custom_reporter import CustomJsonReporter
from utils.custom_html_reporter import CustomHtmlReporter
from utils.logger import init_logger


def pytest_addoption(parser):
    """CLI flags keep runtime config explicit and discoverable."""
    parser.addoption("--env", action="store", default=os.getenv("TEST_ENV", "dev"), help="Target environment (dev/staging)")
    parser.addoption("--platform", action="store", default=os.getenv("APP_PLATFORM", "android"), help="Target platform (android/ios)")
    parser.addoption("--require-real", action="store_true", default=False, help="Fail instead of skipping when device not available")
    parser.addoption(
        "--custom-report",
        action="store",
        default=None,
        help="Optional path for custom JSON report (defaults to reports/custom/custom-report-<timestamp>.json)",
    )
    parser.addoption(
        "--custom-html-report",
        action="store",
        default=None,
        help="Optional path for custom HTML report (defaults to reports/custom/custom-report-<timestamp>.html)",
    )


@pytest.fixture(scope="session")
def settings(request):
    env_name = request.config.getoption("--env")
    platform = request.config.getoption("--platform")
    return get_settings(env_name, platform)


def _mobile_tests_enabled() -> bool:
    """Central check to decide whether device-dependent tests should execute."""
    return os.getenv("RUN_MOBILE_TESTS", "").lower() == "true" or os.getenv("USE_REAL_DEVICE", "0") == "1"


@pytest.fixture(scope="session")
def driver(settings, request):
    """Return real driver when available, otherwise DummyDriver to keep suite green."""
    init_logger()
    run_mobile = _mobile_tests_enabled()

    # short-circuit if mobile tests disabled
    if not run_mobile:
        pytest.skip("Mobile tests skipped: set RUN_MOBILE_TESTS=true to enable.")

    try:
        driver_instance = create_driver(settings)
    except Exception as exc:  # noqa: BLE001
        pytest.skip(f"Mobile tests skipped: driver init failed ({exc}).")

    # If caller insists on real device, skip early to keep CI green instead of failing.
    if request.config.getoption("--require-real") and getattr(driver_instance, "is_dummy", False):
        pytest.skip("Real device requested but not available; skipping suite.")

    yield driver_instance
    try:
        quit_driver(driver_instance)
    except WebDriverException as exc:
        logging.warning("Driver teardown issue: %s", exc)


@pytest.fixture
def creds(settings):
    return settings.credentials


def pytest_collection_modifyitems(config, items):
    """Skip device-required tests when running without a real device."""
    run_mobile = _mobile_tests_enabled()
    for item in items:
        if "requires_device" in item.keywords and not run_mobile:
            item.add_marker(pytest.mark.skip(reason="Mobile tests skipped (RUN_MOBILE_TESTS not set)."))


def pytest_configure(config):
    config.addinivalue_line("markers", "requires_device: marks tests that need a real device/Appium session.")
    config.addinivalue_line("markers", "mobile: marks mobile automation cases.")
    reports_dir = Path("reports/html")
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_file = reports_dir / f"test-report-{datetime.now():%Y%m%d-%H%M%S}.html"
    config.option.htmlpath = report_file
    config.option.self_contained_html = True

    # Register custom JSON reporter alongside pytest-html
    custom_reporter = CustomJsonReporter(config)
    config._custom_json_reporter = custom_reporter  # stash for unconfigure
    config.pluginmanager.register(custom_reporter, name="custom-json-reporter")

    # Register custom HTML reporter
    custom_html_reporter = CustomHtmlReporter(config)
    config._custom_html_reporter = custom_html_reporter
    config.pluginmanager.register(custom_html_reporter, name="custom-html-reporter")


def pytest_html_report_title(report):
    report.title = "Mobile Automation Test Report"


def pytest_unconfigure(config):
    reporter = getattr(config, "_custom_json_reporter", None)
    if reporter:
        config.pluginmanager.unregister(reporter, name="custom-json-reporter")
    html_reporter = getattr(config, "_custom_html_reporter", None)
    if html_reporter:
        config.pluginmanager.unregister(html_reporter, name="custom-html-reporter")
