"""Corporate Playwright Test Case: TC-02 Page Load & Core UI Component Sanity.

Adheres strictly to IEEE 829 Test Plan.
"""

import pytest
from playwright.sync_api import Page, expect
from pages.app_page import AppPage


class Test002PageLoadAndCoreUiSanity:
    """TC-02: Page Load & Core Interactive Controls Visibility Sanity."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.page = page
        self.app = AppPage(page, base_url=base_url or "https://www.saucedemo.com")
        self.app.navigate()

    def test_tc02_core_ui_component_sanity(self):
        """Verify visibility of core UI components identified during inspection."""
        expect(self.app.open_menu).to_be_visible()
        expect(self.app.all_items).to_be_visible()
        expect(self.app.dynamic_catalog).to_be_visible()
        expect(self.app.about).to_be_visible()
        expect(self.app.logout).to_be_visible()
        expect(self.app.reset_app_state).to_be_visible()
