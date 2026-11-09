"""Corporate Page Object for Hacker News."""

from typing import List, Optional
from playwright.sync_api import Locator, Page, expect
from pages.base_page import BasePage


class AppPage(BasePage):
    def __init__(self, page: Page, base_url: str = "https://news.ycombinator.com"):
        super().__init__(page, base_url)

    # -----------------------------------------------------------------------
    # Interactive Element Locators
    # -----------------------------------------------------------------------
    @property
    def element(self) -> Locator:
        """Locator for a [css]: """
        return self.page.locator("a[href=\"https://news.ycombinator.com\"]")
    @property
    def hacker_news(self) -> Locator:
        """Locator for a [role]: Hacker News"""
        return self.page.get_by_role("link", name="Hacker News", exact=True)
    @property
    def new(self) -> Locator:
        """Locator for a [role]: new"""
        return self.page.get_by_role("link", name="new", exact=True)
    @property
    def past(self) -> Locator:
        """Locator for a [role]: past"""
        return self.page.get_by_role("link", name="past", exact=True)
    @property
    def comments(self) -> Locator:
        """Locator for a [role]: comments"""
        return self.page.get_by_role("link", name="comments", exact=True)
    @property
    def ask(self) -> Locator:
        """Locator for a [role]: ask"""
        return self.page.get_by_role("link", name="ask", exact=True)
    @property
    def show(self) -> Locator:
        """Locator for a [role]: show"""
        return self.page.get_by_role("link", name="show", exact=True)
    @property
    def jobs(self) -> Locator:
        """Locator for a [role]: jobs"""
        return self.page.get_by_role("link", name="jobs", exact=True)
    @property
    def submit(self) -> Locator:
        """Locator for a [role]: submit"""
        return self.page.get_by_role("link", name="submit", exact=True)
    @property
    def login(self) -> Locator:
        """Locator for a [role]: login"""
        return self.page.get_by_role("link", name="login", exact=True)
    @property
    def element(self) -> Locator:
        """Locator for a [css]: """
        return self.page.locator("a[href=\"vote?id=50427362&how=up&goto=news\"]")
    @property
    def payments_canada_announces_launch_of_canada_s_real_(self) -> Locator:
        """Locator for a [role]: Payments Canada announces launch of Canada\'s Real-Time Rail (RTR) payment system"""
        return self.page.get_by_role("link", name="Payments Canada announces launch of Canada's Real-Time Rail (RTR) payment system", exact=True)
    @property
    def payments_ca(self) -> Locator:
        """Locator for a [role]: payments.ca"""
        return self.page.get_by_role("link", name="payments.ca", exact=True)
    @property
    def ocd(self) -> Locator:
        """Locator for a [role]: ocd"""
        return self.page.get_by_role("link", name="ocd", exact=True)
    @property
    def el_1_hour_ago(self) -> Locator:
        """Locator for a [css]: 1 hour ago"""
        return self.page.locator("tr:nth-of-type(2) > td:nth-of-type(2) > span > span:nth-of-type(2) > a")
    @property
    def hide(self) -> Locator:
        """Locator for a [css]: hide"""
        return self.page.locator("a[href=\"hide?id=50427362&goto=news\"]")
    @property
    def el_99_comments(self) -> Locator:
        """Locator for a [role]: 99 comments"""
        return self.page.get_by_role("link", name="99 comments", exact=True)
    @property
    def element(self) -> Locator:
        """Locator for a [css]: """
        return self.page.locator("a[href=\"vote?id=50424581&how=up&goto=news\"]")
    @property
    def fold_epic_paper_airplanes(self) -> Locator:
        """Locator for a [role]: Fold Epic Paper Airplanes"""
        return self.page.get_by_role("link", name="Fold Epic Paper Airplanes", exact=True)
    @property
    def foldableflight_com(self) -> Locator:
        """Locator for a [role]: foldableflight.com"""
        return self.page.get_by_role("link", name="foldableflight.com", exact=True)
    @property
    def vismit2000(self) -> Locator:
        """Locator for a [role]: vismit2000"""
        return self.page.get_by_role("link", name="vismit2000", exact=True)
    @property
    def el_5_hours_ago(self) -> Locator:
        """Locator for a [role]: 5 hours ago"""
        return self.page.get_by_role("link", name="5 hours ago", exact=True)
    @property
    def hide(self) -> Locator:
        """Locator for a [css]: hide"""
        return self.page.locator("a[href=\"hide?id=50424581&goto=news\"]")
    @property
    def el_86_comments(self) -> Locator:
        """Locator for a [role]: 86 comments"""
        return self.page.get_by_role("link", name="86 comments", exact=True)
    @property
    def element(self) -> Locator:
        """Locator for a [css]: """
        return self.page.locator("a[href=\"vote?id=50426175&how=up&goto=news\"]")
    @property
    def magenta_solar_panels_may_be_agrivoltaics_cleverest(self) -> Locator:
        """Locator for a [role]: Magenta solar panels may be agrivoltaics\' cleverest trick yet"""
        return self.page.get_by_role("link", name="Magenta solar panels may be agrivoltaics' cleverest trick yet", exact=True)
    @property
    def anthropocenemagazine_org(self) -> Locator:
        """Locator for a [role]: anthropocenemagazine.org"""
        return self.page.get_by_role("link", name="anthropocenemagazine.org", exact=True)
    @property
    def speckx(self) -> Locator:
        """Locator for a [css]: speckx"""
        return self.page.locator("tr:nth-of-type(8) > td:nth-of-type(2) > span > a:nth-of-type(1)")
    @property
    def el_3_hours_ago(self) -> Locator:
        """Locator for a [css]: 3 hours ago"""
        return self.page.locator("tr:nth-of-type(8) > td:nth-of-type(2) > span > span:nth-of-type(2) > a")
    @property
    def hide(self) -> Locator:
        """Locator for a [css]: hide"""
        return self.page.locator("a[href=\"hide?id=50426175&goto=news\"]")
    @property
    def el_31_comments(self) -> Locator:
        """Locator for a [css]: 31 comments"""
        return self.page.locator("tr:nth-of-type(8) > td:nth-of-type(2) > span > a:nth-of-type(3)")
    @property
    def element(self) -> Locator:
        """Locator for a [css]: """
        return self.page.locator("a[href=\"vote?id=50427934&how=up&goto=news\"]")
    @property
    def show_hn_db_delve_open_source_db_client_made_with_r(self) -> Locator:
        """Locator for a [role]: Show HN: DBDelve – Open-Source DB Client Made with Rust and GPUI"""
        return self.page.get_by_role("link", name="Show HN: DBDelve – Open-Source DB Client Made with Rust and GPUI", exact=True)
    @property
    def shayan_abbas(self) -> Locator:
        """Locator for a [role]: shayan_abbas"""
        return self.page.get_by_role("link", name="shayan_abbas", exact=True)
    @property
    def el_1_hour_ago(self) -> Locator:
        """Locator for a [css]: 1 hour ago"""
        return self.page.locator("tr:nth-of-type(11) > td:nth-of-type(2) > span > span:nth-of-type(2) > a")
    @property
    def hide(self) -> Locator:
        """Locator for a [css]: hide"""
        return self.page.locator("a[href=\"hide?id=50427934&goto=news\"]")
    @property
    def el_1_comment(self) -> Locator:
        """Locator for a [role]: 1 comment"""
        return self.page.get_by_role("link", name="1 comment", exact=True)
    @property
    def element(self) -> Locator:
        """Locator for a [css]: """
        return self.page.locator("a[href=\"vote?id=50426207&how=up&goto=news\"]")
    @property
    def zebkit_chromium_as_an_embeddable_library(self) -> Locator:
        """Locator for a [role]: Zebkit – Chromium as an embeddable library"""
        return self.page.get_by_role("link", name="Zebkit – Chromium as an embeddable library", exact=True)
    @property
    def github_com_ikey4u(self) -> Locator:
        """Locator for a [role]: github.com/ikey4u"""
        return self.page.get_by_role("link", name="github.com/ikey4u", exact=True)

    # -----------------------------------------------------------------------
    # Flow Action Methods
    # -----------------------------------------------------------------------
    def search_and_submit(self, query: str) -> None:
        self.element.fill(query)
        self.page.keyboard.press("Enter")

    def click_dashboard_tab(self) -> None:
        self.page.get_by_role("tab", name="Dashboard").click()
