"""Corporate Page Object for Acme QA Portal."""

from typing import List, Optional
from playwright.sync_api import Locator, Page, expect
from pages.base_page import BasePage


class AppPage(BasePage):
    def __init__(self, page: Page, base_url: str = "http://127.0.0.1:54697/"):
        super().__init__(page, base_url)

    # -----------------------------------------------------------------------
    # Interactive Element Locators
    # -----------------------------------------------------------------------
    @property
    def home(self) -> Locator:
        """Locator for a [role]: Home"""
        return self.page.get_by_role("link", name="Home", exact=True)
    @property
    def docs(self) -> Locator:
        """Locator for a [role]: Docs"""
        return self.page.get_by_role("link", name="Docs", exact=True)
    @property
    def external(self) -> Locator:
        """Locator for a [role]: External"""
        return self.page.get_by_role("link", name="External", exact=True)
    @property
    def search(self) -> Locator:
        """Locator for input [id]: Search"""
        return self.page.locator("#global-search")
    @property
    def go(self) -> Locator:
        """Locator for button [data-testid]: Go"""
        return self.page.get_by_test_id("search-submit")
    @property
    def overview(self) -> Locator:
        """Locator for button [role]: Overview"""
        return self.page.get_by_role("tab", name="Overview", exact=True)
    @property
    def dashboard(self) -> Locator:
        """Locator for button [role]: Dashboard"""
        return self.page.get_by_role("tab", name="Dashboard", exact=True)
    @property
    def reports(self) -> Locator:
        """Locator for button [role]: Reports"""
        return self.page.get_by_role("tab", name="Reports", exact=True)
    @property
    def email(self) -> Locator:
        """Locator for input [role]: Email"""
        return self.page.get_by_role("textbox", name="Email", exact=True)
    @property
    def coupon_code(self) -> Locator:
        """Locator for input [role]: Coupon code"""
        return self.page.get_by_role("textbox", name="Coupon code", exact=True)
    @property
    def element(self) -> Locator:
        """Locator for select [css]: """
        return self.page.locator("select[name=\"country\"]")
    @property
    def element(self) -> Locator:
        """Locator for textarea [css]: """
        return self.page.locator("textarea[name=\"notes\"]")
    @property
    def save_profile(self) -> Locator:
        """Locator for button [role]: Save profile"""
        return self.page.get_by_role("button", name="Save profile", exact=True)
    @property
    def learn_more(self) -> Locator:
        """Locator for a [css]: Learn more"""
        return self.page.locator("a[href=\"#a\"]")
    @property
    def learn_more(self) -> Locator:
        """Locator for a [css]: Learn more"""
        return self.page.locator("a[href=\"#b\"]")
    @property
    def help(self) -> Locator:
        """Locator for div [data-testid]: Help"""
        return self.page.get_by_test_id("help-widget")
    @property
    def delete_account(self) -> Locator:
        """Locator for button [data-testid]: Delete Account"""
        return self.page.get_by_test_id("delete-account")

    # -----------------------------------------------------------------------
    # Flow Action Methods
    # -----------------------------------------------------------------------
    def search_and_submit(self, query: str) -> None:
        self.search.fill(query)
        self.page.keyboard.press("Enter")

    def click_dashboard_tab(self) -> None:
        self.overview.click()
