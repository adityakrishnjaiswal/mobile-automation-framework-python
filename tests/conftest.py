"""Pytest fixtures and hooks for the mobile automation framework."""

from __future__ import annotations

import logging
import os
from datetime import datetime
from pathlib import Path

import pytest
from selenium.common.exceptions import WebDriverException

from config.settings import get_settings
from drivers.driver_factory import create_driver, quit_driver
from utils.logger import init_logger


def pytest_addoption(parser):
    parser.addoption("--env", action="store", default=os.getenv("TEST_ENV", "dev"), help="Target environment (dev/staging)")
    parser.addoption("--platform", action="store", default=os.getenv("APP_PLATFORM", "android"), help="Target platform (android/ios)")


@pytest.fixture(scope="session")
def settings(request):
    env_name = request.config.getoption("--env")
    platform = request.config.getoption("--platform")
    return get_settings(env_name, platform)


@pytest.fixture(scope="session")
def driver(settings):
    init_logger()
    driver_instance = create_driver(settings)
    yield driver_instance
    try:
        quit_driver(driver_instance)
    except WebDriverException as exc:
        logging.warning("Driver teardown issue: %s", exc)


@pytest.fixture
def creds(settings):
    return settings.credentials


def pytest_configure(config):
    reports_dir = Path("reports/html")
    reports_dir.mkdir(parents=True, exist_ok=True)
    report_file = reports_dir / f"test-report-{datetime.now():%Y%m%d-%H%M%S}.html"
    config.option.htmlpath = report_file
    config.option.self_contained_html = True


def pytest_html_report_title(report):
    report.title = "Mobile Automation Test Report"
