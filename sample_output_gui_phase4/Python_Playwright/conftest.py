"""Pytest configuration and corporate Playwright browser fixtures."""

import pytest
from playwright.sync_api import Browser, BrowserContext, Page, Playwright


@pytest.fixture(scope="session")
def base_url() -> str:
    return "http://127.0.0.1:50992/"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {
        **browser_context_args,
        "ignore_https_errors": True,
        "viewport": {"width": 1440, "height": 900},
    }