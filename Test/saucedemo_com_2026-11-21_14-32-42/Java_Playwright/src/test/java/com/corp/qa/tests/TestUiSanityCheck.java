package com.corp.qa.tests;

import com.corp.qa.pages.AppPage;
import com.microsoft.playwright.*;
import org.testng.Assert;
import org.testng.annotations.*;

public class Test002PageLoadAndCoreUiSanity {
    private Playwright playwright;
    private Browser browser;
    private BrowserContext context;
    private Page page;
    private AppPage app;
    private static final String TARGET_URL = "https://www.saucedemo.com";

    @BeforeClass
    public void setupClass() {
        playwright = Playwright.create();
        browser = playwright.chromium().launch(new BrowserType.LaunchOptions().setChannel("chrome").setHeadless(true));
    }

    @BeforeMethod
    public void setupTest() {
        context = browser.newContext(new Browser.NewContextOptions().setIgnoreHTTPSErrors(true));
        page = context.newPage();
        app = new AppPage(page, TARGET_URL);
        app.navigate();
    }

    @AfterMethod
    public void tearDownTest() {
        if (context != null) context.close();
    }

    @AfterClass
    public void tearDownClass() {
        if (browser != null) browser.close();
        if (playwright != null) playwright.close();
    }

    @Test(description = "TC-02: Page Load & Core UI Component Sanity")
    public void testTc02CoreUiComponentSanity() {
        Assert.assertTrue(app.getOpenMenu().isVisible(), "Element Open Menu is visible");
        Assert.assertTrue(app.getAllItems().isVisible(), "Element All Items is visible");
        Assert.assertTrue(app.getDynamicCatalog().isVisible(), "Element Dynamic Catalog is visible");
        Assert.assertTrue(app.getAbout().isVisible(), "Element About is visible");
        Assert.assertTrue(app.getLogout().isVisible(), "Element Logout is visible");
    }
}