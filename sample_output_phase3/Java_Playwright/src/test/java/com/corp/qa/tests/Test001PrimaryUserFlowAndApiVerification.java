package com.corp.qa.tests;

import com.corp.qa.pages.AppPage;
import com.microsoft.playwright.*;
import org.testng.Assert;
import org.testng.annotations.*;
import java.util.Arrays;
import java.util.List;

public class Test001PrimaryUserFlowAndApiVerification {
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

    @Test(description = "TC-01: Primary User Flow with UI Actions & Backend Status Code Interception")
    public void testTc01PrimaryUserFlowAndApiVerification() {
        Assert.assertTrue(page.title().contains("Acme QA Portal"), "Page title matches");

        List<Integer> expectedStatuses = Arrays.asList(200, 201);
        Response response = app.waitForApiResponse(
            "user",
            () -> {
                app.searchAndSubmit("playwright");
            },
            expectedStatuses
        );
        Assert.assertTrue(expectedStatuses.contains(response.status()), 
            "API returned expected status code: " + response.status());
    }
}