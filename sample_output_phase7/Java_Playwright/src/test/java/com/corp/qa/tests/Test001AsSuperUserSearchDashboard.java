package com.corp.qa.tests;

import com.corp.qa.pages.AppPage;
import com.corp.qa.pages.LoginPage;
import com.microsoft.playwright.*;
import org.testng.Assert;
import org.testng.annotations.*;
import java.util.Arrays;
import java.util.List;

public class Test001AsSuperUserSearchDashboard {
    private Playwright playwright;
    private Browser browser;
    private BrowserContext context;
    private Page page;
    private AppPage app;
    private LoginPage loginPage;
    private static final String TARGET_URL = LoginPage.getEnv("BASE_URL", "");

    @BeforeClass
    public void setupClass() {
        playwright = Playwright.create();
        browser = playwright.chromium().launch(new BrowserType.LaunchOptions().setChannel("chrome").setHeadless(true));
    }

    @BeforeMethod
    public void setupTest() {
        context = browser.newContext(new Browser.NewContextOptions().setIgnoreHTTPSErrors(true));
        page = context.newPage();
        loginPage = new LoginPage(page, TARGET_URL);
        app = new AppPage(page, TARGET_URL);
        app.navigate();
        loginPage.loginWithProfile(LoginPage.getEnv("TEST_ACCESS_PROFILE", "SUPER_USER"));
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
        Assert.assertTrue(page.title().contains("Shutterstock — Stock Images, Photos, Vectors, Video, and Music"), "Page title matches");

        List<Integer> expectedStatuses = Arrays.asList(200, 201);
        Response response = app.waitForApiResponse(
            "search",
            () -> {
                app.searchAndSubmit("playwright");
            },
            expectedStatuses
        );
        Assert.assertTrue(expectedStatuses.contains(response.status()), 
            "API returned expected status code: " + response.status());
    }
}