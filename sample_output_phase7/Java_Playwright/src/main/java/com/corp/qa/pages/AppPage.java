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
    public Locator getSearchInput() {
        // Locator for input [id]: Search Input
        return this.page.locator("#search-input");
    }
    public Locator getDashboardTab() {
        // Locator for button [data-testid]: Dashboard Tab
        return this.page.getByTestId("dashboard-tab");
    }

    // -----------------------------------------------------------------------
    // Business Flow Actions
    // -----------------------------------------------------------------------
    public void searchAndSubmit(String query) {
        getSearchInput().fill(query);
        page.keyboard().press("Enter");
    }

    public void clickDashboardTab() {
        getDashboardTab().click();
    }
}