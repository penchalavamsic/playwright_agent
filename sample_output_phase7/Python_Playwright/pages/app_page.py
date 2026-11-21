"""Corporate Page Object for Shutterstock — Stock Images, Photos, Vectors, Video, and Music."""

import os
from typing import List, Optional
from playwright.sync_api import Locator, Page, expect
from pages.base_page import BasePage


class AppPage(BasePage):
    def __init__(self, page: Page, base_url: str = ""):
        resolved_url = base_url or os.getenv("BASE_URL", "")
        super().__init__(page, resolved_url)

    # -----------------------------------------------------------------------
    # Interactive Element Locators
    # -----------------------------------------------------------------------
    @property
    def search_input(self) -> Locator:
        """Locator for input [id]: Search Input"""
        return self.page.locator("#search-input")
    @property
    def dashboard_tab(self) -> Locator:
        """Locator for button [data-testid]: Dashboard Tab"""
        return self.page.get_by_test_id("dashboard-tab")

    # -----------------------------------------------------------------------
    # Flow Action Methods
    # -----------------------------------------------------------------------
    def search_and_submit(self, query: str) -> None:
        self.search_input.fill(query)
        self.page.keyboard.press("Enter")

    def click_dashboard_tab(self) -> None:
        self.dashboard_tab.click()
