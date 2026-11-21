"""Corporate Page Object for Swag Labs."""

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
    def open_menu(self) -> Locator:
        """Locator for button [role]: Open Menu"""
        return self.page.get_by_role("button", name="Open Menu", exact=True)
    @property
    def all_items(self) -> Locator:
        """Locator for a [id]: All Items"""
        return self.page.locator("#inventory_sidebar_link")
    @property
    def dynamic_catalog(self) -> Locator:
        """Locator for a [id]: Dynamic Catalog"""
        return self.page.locator("#dynamic_catalog_sidebar_link")
    @property
    def about(self) -> Locator:
        """Locator for a [id]: About"""
        return self.page.locator("#about_sidebar_link")
    @property
    def logout(self) -> Locator:
        """Locator for a [id]: Logout"""
        return self.page.locator("#logout_sidebar_link")
    @property
    def reset_app_state(self) -> Locator:
        """Locator for a [id]: Reset App State"""
        return self.page.locator("#reset_sidebar_link")
    @property
    def close_menu(self) -> Locator:
        """Locator for button [text]: Close Menu"""
        return self.page.get_by_text("Close Menu", exact=True)
    @property
    def cart_empty(self) -> Locator:
        """Locator for a [role]: Cart, empty"""
        return self.page.get_by_role("button", name="Cart, empty", exact=True)
    @property
    def sort_products(self) -> Locator:
        """Locator for select [role]: Sort products"""
        return self.page.get_by_role("combobox", name="Sort products", exact=True)
    @property
    def view_details_for_sauce_labs_backpack(self) -> Locator:
        """Locator for a [id]: View details for Sauce Labs Backpack"""
        return self.page.locator("#item_4_img_link")
    @property
    def view_details_for_sauce_labs_backpack(self) -> Locator:
        """Locator for a [id]: View details for Sauce Labs Backpack"""
        return self.page.locator("#item_4_title_link")
    @property
    def add_to_cart(self) -> Locator:
        """Locator for button [id]: Add to cart"""
        return self.page.locator("#add-to-cart-sauce-labs-backpack")
    @property
    def view_details_for_sauce_labs_bike_light(self) -> Locator:
        """Locator for a [id]: View details for Sauce Labs Bike Light"""
        return self.page.locator("#item_0_img_link")
    @property
    def view_details_for_sauce_labs_bike_light(self) -> Locator:
        """Locator for a [id]: View details for Sauce Labs Bike Light"""
        return self.page.locator("#item_0_title_link")
    @property
    def add_to_cart(self) -> Locator:
        """Locator for button [id]: Add to cart"""
        return self.page.locator("#add-to-cart-sauce-labs-bike-light")
    @property
    def view_details_for_sauce_labs_bolt_t_shirt(self) -> Locator:
        """Locator for a [id]: View details for Sauce Labs Bolt T-Shirt"""
        return self.page.locator("#item_1_img_link")
    @property
    def view_details_for_sauce_labs_bolt_t_shirt(self) -> Locator:
        """Locator for a [id]: View details for Sauce Labs Bolt T-Shirt"""
        return self.page.locator("#item_1_title_link")
    @property
    def add_to_cart(self) -> Locator:
        """Locator for button [id]: Add to cart"""
        return self.page.locator("#add-to-cart-sauce-labs-bolt-t-shirt")
    @property
    def view_details_for_sauce_labs_fleece_jacket(self) -> Locator:
        """Locator for a [id]: View details for Sauce Labs Fleece Jacket"""
        return self.page.locator("#item_5_img_link")
    @property
    def view_details_for_sauce_labs_fleece_jacket(self) -> Locator:
        """Locator for a [id]: View details for Sauce Labs Fleece Jacket"""
        return self.page.locator("#item_5_title_link")
    @property
    def add_to_cart(self) -> Locator:
        """Locator for button [id]: Add to cart"""
        return self.page.locator("#add-to-cart-sauce-labs-fleece-jacket")
    @property
    def view_details_for_sauce_labs_onesie(self) -> Locator:
        """Locator for a [id]: View details for Sauce Labs Onesie"""
        return self.page.locator("#item_2_img_link")
    @property
    def view_details_for_sauce_labs_onesie(self) -> Locator:
        """Locator for a [id]: View details for Sauce Labs Onesie"""
        return self.page.locator("#item_2_title_link")
    @property
    def add_to_cart(self) -> Locator:
        """Locator for button [id]: Add to cart"""
        return self.page.locator("#add-to-cart-sauce-labs-onesie")
    @property
    def view_details_for_test_all_the_things_t_shirt_red(self) -> Locator:
        """Locator for a [id]: View details for Test.allTheThings() T-Shirt (Red)"""
        return self.page.locator("#item_3_img_link")
    @property
    def view_details_for_test_all_the_things_t_shirt_red(self) -> Locator:
        """Locator for a [id]: View details for Test.allTheThings() T-Shirt (Red)"""
        return self.page.locator("#item_3_title_link")
    @property
    def add_to_cart(self) -> Locator:
        """Locator for button [id]: Add to cart"""
        return self.page.locator("[id=\"add-to-cart-test.allthethings()-t-shirt-(red)\"]")
    @property
    def x(self) -> Locator:
        """Locator for a [role]: X"""
        return self.page.get_by_role("link", name="X", exact=True)
    @property
    def facebook(self) -> Locator:
        """Locator for a [role]: Facebook"""
        return self.page.get_by_role("link", name="Facebook", exact=True)
    @property
    def linked_in(self) -> Locator:
        """Locator for a [role]: LinkedIn"""
        return self.page.get_by_role("link", name="LinkedIn", exact=True)

    # -----------------------------------------------------------------------
    # Flow Action Methods
    # -----------------------------------------------------------------------
    def search_and_submit(self, query: str) -> None:
        self.page.keyboard.type(query)
        self.page.keyboard.press("Enter")

    def click_dashboard_tab(self) -> None:
        self.page.get_by_role("tab", name="Dashboard").click()
