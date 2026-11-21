"""Corporate Page Object for Shutterstock Studio Portal."""

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
    def search_stock_images(self) -> Locator:
        """Locator for input [id]: Search stock images..."""
        return self.page.locator("#search-input")
    @property
    def explore_gallery(self) -> Locator:
        """Locator for button [id]: Explore Gallery"""
        return self.page.locator("#dashboard-tab")

    # -----------------------------------------------------------------------
    # Flow Action Methods
    # -----------------------------------------------------------------------
    def search_and_submit(self, query: str) -> None:
        self.search_stock_images.fill(query)
        self.page.keyboard.press("Enter")

    def click_dashboard_tab(self) -> None:
        self.explore_gallery.click()
