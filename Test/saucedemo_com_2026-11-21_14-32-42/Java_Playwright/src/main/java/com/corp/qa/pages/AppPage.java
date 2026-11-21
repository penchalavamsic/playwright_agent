package com.corp.qa.pages;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.options.AriaRole;

public class AppPage extends BasePage {

    public AppPage(Page page, String baseUrl) {
        super(page, baseUrl);
    }

    // -----------------------------------------------------------------------
    // Interactive Element Locators
    // -----------------------------------------------------------------------
    public Locator getOpenMenu() {
        // Locator for button [role]: Open Menu
        return this.page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Open Menu").setExact(true));
    }
    public Locator getAllItems() {
        // Locator for a [id]: All Items
        return this.page.locator("#inventory_sidebar_link");
    }
    public Locator getDynamicCatalog() {
        // Locator for a [id]: Dynamic Catalog
        return this.page.locator("#dynamic_catalog_sidebar_link");
    }
    public Locator getAbout() {
        // Locator for a [id]: About
        return this.page.locator("#about_sidebar_link");
    }
    public Locator getLogout() {
        // Locator for a [id]: Logout
        return this.page.locator("#logout_sidebar_link");
    }
    public Locator getResetAppState() {
        // Locator for a [id]: Reset App State
        return this.page.locator("#reset_sidebar_link");
    }
    public Locator getCloseMenu() {
        // Locator for button [text]: Close Menu
        return this.page.getByText("Close Menu", new Page.GetByTextOptions().setExact(true));
    }
    public Locator getCartEmpty() {
        // Locator for a [role]: Cart, empty
        return this.page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Cart, empty").setExact(true));
    }
    public Locator getSortProducts() {
        // Locator for select [role]: Sort products
        return this.page.getByRole(AriaRole.COMBOBOX, new Page.GetByRoleOptions().setName("Sort products").setExact(true));
    }
    public Locator getViewDetailsForSauceLabsBackpack() {
        // Locator for a [id]: View details for Sauce Labs Backpack
        return this.page.locator("#item_4_img_link");
    }
    public Locator getViewDetailsForSauceLabsBackpack() {
        // Locator for a [id]: View details for Sauce Labs Backpack
        return this.page.locator("#item_4_title_link");
    }
    public Locator getAddToCart() {
        // Locator for button [id]: Add to cart
        return this.page.locator("#add-to-cart-sauce-labs-backpack");
    }
    public Locator getViewDetailsForSauceLabsBikeLight() {
        // Locator for a [id]: View details for Sauce Labs Bike Light
        return this.page.locator("#item_0_img_link");
    }
    public Locator getViewDetailsForSauceLabsBikeLight() {
        // Locator for a [id]: View details for Sauce Labs Bike Light
        return this.page.locator("#item_0_title_link");
    }
    public Locator getAddToCart() {
        // Locator for button [id]: Add to cart
        return this.page.locator("#add-to-cart-sauce-labs-bike-light");
    }
    public Locator getViewDetailsForSauceLabsBoltTShirt() {
        // Locator for a [id]: View details for Sauce Labs Bolt T-Shirt
        return this.page.locator("#item_1_img_link");
    }
    public Locator getViewDetailsForSauceLabsBoltTShirt() {
        // Locator for a [id]: View details for Sauce Labs Bolt T-Shirt
        return this.page.locator("#item_1_title_link");
    }
    public Locator getAddToCart() {
        // Locator for button [id]: Add to cart
        return this.page.locator("#add-to-cart-sauce-labs-bolt-t-shirt");
    }
    public Locator getViewDetailsForSauceLabsFleeceJacket() {
        // Locator for a [id]: View details for Sauce Labs Fleece Jacket
        return this.page.locator("#item_5_img_link");
    }
    public Locator getViewDetailsForSauceLabsFleeceJacket() {
        // Locator for a [id]: View details for Sauce Labs Fleece Jacket
        return this.page.locator("#item_5_title_link");
    }
    public Locator getAddToCart() {
        // Locator for button [id]: Add to cart
        return this.page.locator("#add-to-cart-sauce-labs-fleece-jacket");
    }
    public Locator getViewDetailsForSauceLabsOnesie() {
        // Locator for a [id]: View details for Sauce Labs Onesie
        return this.page.locator("#item_2_img_link");
    }
    public Locator getViewDetailsForSauceLabsOnesie() {
        // Locator for a [id]: View details for Sauce Labs Onesie
        return this.page.locator("#item_2_title_link");
    }
    public Locator getAddToCart() {
        // Locator for button [id]: Add to cart
        return this.page.locator("#add-to-cart-sauce-labs-onesie");
    }
    public Locator getViewDetailsForTestAllTheThingsTShirtRed() {
        // Locator for a [id]: View details for Test.allTheThings() T-Shirt (Red)
        return this.page.locator("#item_3_img_link");
    }
    public Locator getViewDetailsForTestAllTheThingsTShirtRed() {
        // Locator for a [id]: View details for Test.allTheThings() T-Shirt (Red)
        return this.page.locator("#item_3_title_link");
    }
    public Locator getAddToCart() {
        // Locator for button [id]: Add to cart
        return this.page.locator("[id=\"add-to-cart-test.allthethings()-t-shirt-(red)\"]");
    }
    public Locator getX() {
        // Locator for a [role]: X
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("X").setExact(true));
    }
    public Locator getFacebook() {
        // Locator for a [role]: Facebook
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("Facebook").setExact(true));
    }
    public Locator getLinkedIn() {
        // Locator for a [role]: LinkedIn
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("LinkedIn").setExact(true));
    }

    // -----------------------------------------------------------------------
    // Business Flow Actions
    // -----------------------------------------------------------------------
    public void searchAndSubmit(String query) {
        page.keyboard().type(query);
        page.keyboard().press("Enter");
    }

    public void clickDashboardTab() {
        page.getByRole(AriaRole.TAB, new Page.GetByRoleOptions().setName("Dashboard").setExact(true)).click();
    }
}