package com.corp.qa.tests;

import com.corp.qa.pages.LoginPage;
import com.microsoft.playwright.*;
import org.testng.ITestResult;
import org.testng.annotations.*;
import java.nio.file.*;
import java.util.*;
import com.google.gson.JsonObject;
import com.google.gson.JsonParser;

public class BaseTest {
    public static final Path REPORT_ROOT = Paths.get("execution-reports", System.currentTimeMillis() + "-" + UUID.randomUUID().toString().substring(0, 8));
    protected Playwright playwright;
    protected Browser browser;
    protected BrowserContext context;
    protected Page page;
    protected LoginPage loginPage;
    protected static final String TARGET_URL = LoginPage.getEnv("BASE_URL", "");
    private Path evidence;
    private static final JsonObject SETTINGS = readSettings();
    private static JsonObject readSettings() {
        try { return JsonParser.parseString(Files.readString(Paths.get("..", "browser-settings.json"))).getAsJsonObject(); }
        catch (java.io.IOException ex) { return new JsonObject(); }
    }
    public static String setting(String key, String fallback) { return SETTINGS.has(key) ? SETTINGS.get(key).getAsString() : fallback; }
    protected String accessProfile() { return LoginPage.getEnv("TEST_ACCESS_PROFILE", "PUBLIC"); }
    private boolean persistent() { return setting("session_mode", "fresh").equals("persistent"); }
    private BrowserContext openContext(boolean video) throws Exception {
        if (persistent()) {
            String channel = LoginPage.getEnv("BROWSER_CHANNEL", "msedge");
            java.net.URI url = java.net.URI.create(TARGET_URL);
            String identity = url.getScheme() + "://" + url.getAuthority() + "|" + accessProfile() + "|" + channel;
            String key = HexFormat.of().formatHex(java.security.MessageDigest.getInstance("SHA-256").digest(identity.getBytes(java.nio.charset.StandardCharsets.UTF_8))).substring(0,24);
            BrowserType.LaunchPersistentContextOptions options = new BrowserType.LaunchPersistentContextOptions().setChannel(channel).setHeadless(true).setTimeout(30000).setIgnoreHTTPSErrors(true).setViewportSize(1280,720);
            if (video) options.setRecordVideoDir(evidence.resolve("raw-video"));
            return playwright.chromium().launchPersistentContext(Paths.get(".browser_profiles", key).toAbsolutePath(), options);
        }
        Browser.NewContextOptions options = new Browser.NewContextOptions().setIgnoreHTTPSErrors(true).setViewportSize(1280,720);
        if (video) options.setRecordVideoDir(evidence.resolve("raw-video"));
        return browser.newContext(options);
    }

    @BeforeClass public void startBrowser() {
        playwright = Playwright.create();
        String channel = LoginPage.getEnv("BROWSER_CHANNEL", "msedge");
        if (!persistent()) browser = playwright.chromium().launch(new BrowserType.LaunchOptions().setChannel(channel).setHeadless(true));
    }

    @BeforeMethod public void startTest(java.lang.reflect.Method method) throws Exception {
        evidence = REPORT_ROOT.resolve("Evidence").resolve(getClass().getSimpleName() + "-" + method.getName());
        Files.createDirectories(evidence);
        try {
            context = openContext(true);
            page = context.pages().isEmpty() ? context.newPage() : context.pages().get(0);
        } catch (PlaywrightException ex) {
            if (context != null) context.close();
            if (!ex.getMessage().toLowerCase().contains("ffmpeg")) throw ex;
            context = openContext(false);
            page = context.pages().isEmpty() ? context.newPage() : context.pages().get(0);
        }
        context.tracing().start(new Tracing.StartOptions().setScreenshots(true).setSnapshots(true).setSources(true));
        loginPage = new LoginPage(page, TARGET_URL);
    }

    @AfterMethod(alwaysRun = true) public void finishTest(ITestResult result) {
        if (context == null) return;
        Video video = page == null ? null : page.video();
        try {
            if (page != null && !page.isClosed()) {
                result.setAttribute("final_route", page.url());
                page.screenshot(new Page.ScreenshotOptions().setPath(evidence.resolve("final-screenshot.png")));
                result.setAttribute("final_screenshot", relative("final-screenshot.png"));
            }
            context.tracing().stop(new Tracing.StopOptions().setPath(evidence.resolve("trace.zip")));
            result.setAttribute("trace_rel_path", relative("trace.zip"));
        } catch (Exception ex) {
            result.setAttribute("media_note", ex.toString());
        } finally {
            context.close();
        }
        try {
            if (video != null && Files.isRegularFile(video.path())) {
                Files.copy(video.path(), evidence.resolve("video.webm"), StandardCopyOption.REPLACE_EXISTING);
                result.setAttribute("video_rel_path", relative("video.webm"));
            }
        } catch (Exception ex) { result.setAttribute("media_note", ex.toString()); }
    }
    private String relative(String file) { return REPORT_ROOT.relativize(evidence.resolve(file)).toString().replace('\\', '/'); }

    @AfterClass(alwaysRun = true) public void stopBrowser() {
        if (browser != null) browser.close();
        if (playwright != null) playwright.close();
    }
}
