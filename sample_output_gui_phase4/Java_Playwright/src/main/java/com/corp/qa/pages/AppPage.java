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
    public Locator getHome() {
        // Locator for a [role]: Home
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("Home").setExact(true));
    }
    public Locator getDocs() {
        // Locator for a [role]: Docs
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("Docs").setExact(true));
    }
    public Locator getExternal() {
        // Locator for a [role]: External
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("External").setExact(true));
    }
    public Locator getSearch() {
        // Locator for input [id]: Search
        return this.page.locator("#global-search");
    }
    public Locator getGo() {
        // Locator for button [data-testid]: Go
        return this.page.getByTestId("search-submit");
    }
    public Locator getOverview() {
        // Locator for button [role]: Overview
        return this.page.getByRole(AriaRole.TAB, new Page.GetByRoleOptions().setName("Overview").setExact(true));
    }
    public Locator getDashboard() {
        // Locator for button [role]: Dashboard
        return this.page.getByRole(AriaRole.TAB, new Page.GetByRoleOptions().setName("Dashboard").setExact(true));
    }
    public Locator getReports() {
        // Locator for button [role]: Reports
        return this.page.getByRole(AriaRole.TAB, new Page.GetByRoleOptions().setName("Reports").setExact(true));
    }
    public Locator getEmail() {
        // Locator for input [role]: Email
        return this.page.getByRole(AriaRole.TEXTBOX, new Page.GetByRoleOptions().setName("Email").setExact(true));
    }
    public Locator getCouponCode() {
        // Locator for input [role]: Coupon code
        return this.page.getByRole(AriaRole.TEXTBOX, new Page.GetByRoleOptions().setName("Coupon code").setExact(true));
    }
    public Locator getElement() {
        // Locator for select [css]: 
        return this.page.locator("select[name=\"country\"]");
    }
    public Locator getElement() {
        // Locator for textarea [css]: 
        return this.page.locator("textarea[name=\"notes\"]");
    }
    public Locator getSaveProfile() {
        // Locator for button [role]: Save profile
        return this.page.getByRole(AriaRole.BUTTON, new Page.GetByRoleOptions().setName("Save profile").setExact(true));
    }
    public Locator getLearnMore() {
        // Locator for a [css]: Learn more
        return this.page.locator("a[href=\"#a\"]");
    }
    public Locator getLearnMore() {
        // Locator for a [css]: Learn more
        return this.page.locator("a[href=\"#b\"]");
    }
    public Locator getHelp() {
        // Locator for div [data-testid]: Help
        return this.page.getByTestId("help-widget");
    }
    public Locator getDeleteAccount() {
        // Locator for button [data-testid]: Delete Account
        return this.page.getByTestId("delete-account");
    }

    // -----------------------------------------------------------------------
    // Business Flow Actions
    // -----------------------------------------------------------------------
    public void searchAndSubmit(String query) {
        getSearch().fill(query);
        page.keyboard().press("Enter");
    }

    public void clickDashboardTab() {
        getOverview().click();
    }
}