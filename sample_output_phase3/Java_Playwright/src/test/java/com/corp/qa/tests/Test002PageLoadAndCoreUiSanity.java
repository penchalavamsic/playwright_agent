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
    private static final String TARGET_URL = "http://127.0.0.1:50751/";

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
        Assert.assertTrue(app.getHome().isVisible(), "Element Home is visible");
        Assert.assertTrue(app.getDocs().isVisible(), "Element Docs is visible");
        Assert.assertTrue(app.getExternal().isVisible(), "Element External is visible");
        Assert.assertTrue(app.getSearch().isVisible(), "Element Search is visible");
        Assert.assertTrue(app.getGo().isVisible(), "Element Go is visible");
    }
}