package com.corp.qa.tests;

import com.corp.qa.pages.AppPage;
import com.corp.qa.pages.LoginPage;
import com.microsoft.playwright.*;
import org.testng.ITestResult;
import org.testng.annotations.*;

import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Base TestNG harness with native Playwright screenshot & .webm video capture.
 */
public class BaseTest {
    protected Playwright playwright;
    protected Browser browser;
    protected BrowserContext context;
    protected Page page;
    protected AppPage app;
    protected LoginPage loginPage;
    protected static final String TARGET_URL = LoginPage.getEnv("BASE_URL", "");
    private static final AtomicInteger TEST_COUNTER = new AtomicInteger(0);
    private String currentTestId = "JAVA-001";

    @BeforeClass
    public void setupClass() {
        playwright = Playwright.create();
        browser = playwright.chromium().launch(new BrowserType.LaunchOptions().setChannel("chrome").setHeadless(true));
    }

    @BeforeMethod
    public void setupTest() throws Exception {
        currentTestId = String.format("JAVA-%03d", TEST_COUNTER.incrementAndGet());
        Path videoDir = Paths.get("target", "videos");
        Files.createDirectories(videoDir);
        context = browser.newContext(new Browser.NewContextOptions()
                .setIgnoreHTTPSErrors(true)
                .setViewportSize(1280, 720)
                .setRecordVideoDir(videoDir)
                .setRecordVideoSize(1280, 720));
        page = context.newPage();
        loginPage = new LoginPage(page, TARGET_URL);
        app = new AppPage(page, TARGET_URL);
        app.navigate();
        loginPage.loginWithProfile(LoginPage.getEnv("TEST_ACCESS_PROFILE", "STANDARD_USER"));
    }

    @AfterMethod
    public void tearDownTest(ITestResult result) {
        Video video = (page != null) ? page.video() : null;
        try {
            if (page != null) {
                Path ssDir = Paths.get("..", "Complete-Suite-Test-Report", "Evidence", "Screenshots", currentTestId);
                Files.createDirectories(ssDir);
                page.screenshot(new Page.ScreenshotOptions().setPath(ssDir.resolve("final-screenshot.png")));
                page.close();
            }
        } catch (Exception ignored) {
        }
        try {
            if (context != null) {
                context.close();
            }
            if (video != null) {
                Path srcVideo = video.path();
                if (srcVideo != null && Files.exists(srcVideo) && Files.size(srcVideo) > 0) {
                    Path recDir = Paths.get("..", "Complete-Suite-Test-Report", "Evidence", "Recording", currentTestId);
                    Files.createDirectories(recDir);
                    Files.copy(srcVideo, recDir.resolve("video.webm"), StandardCopyOption.REPLACE_EXISTING);
                }
            }
        } catch (Exception ignored) {
        }
    }

    @AfterClass
    public void tearDownClass() {
        if (browser != null) browser.close();
        if (playwright != null) playwright.close();
    }
}