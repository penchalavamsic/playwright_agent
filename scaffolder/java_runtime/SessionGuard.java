package com.corp.qa.tests;
import com.microsoft.playwright.Page;
import com.microsoft.playwright.PlaywrightException;
import java.net.URI;

public class SessionGuard {
    private final Page page;
    private boolean authenticated;
    public SessionGuard(Page page) { this.page = page; }
    private boolean passwordVisible() {
        try { return page.locator("input[type=\"password\"]:visible").count() > 0; }
        catch (PlaywrightException ex) {
            if (ex.getMessage().contains("Execution context was destroyed")) return false;
            throw ex;
        }
    }
    public void check() {
        if (authenticated && passwordVisible()) throw new AssertionError("Session lost: returned to login. No automatic retry attempted.");
    }
    private boolean successVisible(String path, String selector) {
        try { return stablePageVisible(path, selector); }
        catch (PlaywrightException ex) {
            if (ex.getMessage().contains("Execution context was destroyed")) return false;
            throw ex;
        }
    }
    private boolean stablePageVisible(String path, String selector) {
        boolean good = !passwordVisible();
        if (!path.isEmpty()) {
            URI actual = URI.create(page.url()), wanted = URI.create(path);
            String expected = wanted.getPath().replaceAll("/$", "");
            if (expected.isEmpty()) expected = "/";
            good = good && (wanted.getHost() == null || (java.util.Objects.equals(actual.getScheme(),wanted.getScheme()) && java.util.Objects.equals(actual.getAuthority(),wanted.getAuthority())))
                && (actual.getPath().equals(expected) || (!expected.equals("/") && actual.getPath().startsWith(expected + "/")));
        }
        if (!selector.isEmpty()) good = good && page.locator(selector).first().isVisible();
        return good && page.locator("body").isVisible() && !page.locator("body").innerText().isBlank();
    }
    public void login(Runnable action) {
        String path = BaseTest.setting("auth_success_path", "");
        String selector = BaseTest.setting("auth_success_selector", "");
        long timeout = Math.max(3000, Math.min(120000, Long.parseLong(BaseTest.setting("auth_timeout_ms", "15000"))));
        long entryDeadline = System.nanoTime() + timeout * 1000000;
        while (!passwordVisible() && System.nanoTime() < entryDeadline) {
            if ((!path.isEmpty() || !selector.isEmpty()) && successVisible(path, selector)) break;
            page.waitForTimeout(100);
        }
        if (passwordVisible()) action.run();
        else if (path.isEmpty() && selector.isEmpty()) throw new AssertionError("Configure an authenticated path or selector to verify the saved session.");
        long settle = Math.max(500, Math.min(timeout-500, Long.parseLong(BaseTest.setting("auth_settle_ms", "2500"))));
        long deadline = System.nanoTime() + timeout * 1000000;
        long since = 0;
        boolean seen = false;
        while (System.nanoTime() < deadline) {
            boolean visible = passwordVisible();
            if (seen && visible) throw new AssertionError("Login loop detected: dashboard returned to login. No automatic retry attempted.");
            boolean good = successVisible(path, selector);
            if (good) {
                seen = true;
                if (since == 0) since = System.nanoTime();
                if (System.nanoTime()-since >= settle*1000000) { authenticated = true; return; }
            } else since = 0;
            page.waitForTimeout(100);
        }
        throw new AssertionError("Authentication did not remain valid before timeout. Check session/SSO settings.");
    }
}
