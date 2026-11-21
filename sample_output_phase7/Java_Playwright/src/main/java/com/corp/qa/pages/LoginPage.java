package com.corp.qa.pages;

import com.microsoft.playwright.Locator;
import com.microsoft.playwright.Page;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class LoginPage extends BasePage {

    public LoginPage(Page page, String baseUrl) {
        super(page, (baseUrl != null && !baseUrl.isEmpty()) ? baseUrl : getEnv("BASE_URL", ""));
    }

    public static String getEnv(String key, String defaultValue) {
        String sysVal = System.getenv(key);
        if (sysVal != null && !sysVal.isEmpty()) {
            return sysVal;
        }
        Map<String, String> envMap = loadDotEnv();
        return envMap.getOrDefault(key, defaultValue);
    }

    private static Map<String, String> loadDotEnv() {
        Map<String, String> map = new HashMap<>();
        Path[] candidates = new Path[] { Paths.get("..", ".env"), Paths.get(".env") };
        for (Path p : candidates) {
            if (Files.exists(p)) {
                try {
                    List<String> lines = Files.readAllLines(p);
                    for (String line : lines) {
                        String trimmed = line.trim();
                        if (trimmed.isEmpty() || trimmed.startsWith("#") || !trimmed.contains("=")) {
                            continue;
                        }
                        int idx = trimmed.indexOf('=');
                        String k = trimmed.substring(0, idx).trim();
                        String v = trimmed.substring(idx + 1).trim();
                        map.put(k, v);
                    }
                    break;
                } catch (IOException ignored) {
                }
            }
        }
        return map;
    }

    public void loginWithProfile(String profileName) {
        String role = (profileName != null && !profileName.isEmpty())
            ? profileName.trim().toUpperCase()
            : getEnv("TEST_ACCESS_PROFILE", "").trim().toUpperCase();
        if (role.isEmpty() || role.equals("NONE") || role.equals("PUBLIC") || role.equals("NONE (PUBLIC URL)")) {
            return;
        }
        String username = getEnv(role + "_USERNAME", "");
        String password = getEnv(role + "_PASSWORD", "");
        if (username.isEmpty() && password.isEmpty()) {
            return;
        }

        Locator pwdInput = page.locator("input[type=\"password\"]").first();
        try {
            pwdInput.waitFor(new Locator.WaitForOptions().setTimeout(3000));
        } catch (Exception e) {
            return;
        }

        Locator userInput = page.locator("input[type=\"email\"], input[name*=\"user\" i], input[type=\"text\"]").first();
        if (!username.isEmpty()) {
            userInput.fill(username);
        }
        if (!password.isEmpty()) {
            pwdInput.fill(password);
        }
        Locator submitBtn = page.locator("button[type=\"submit\"], input[type=\"submit\"]").first();
        if (submitBtn.isVisible()) {
            submitBtn.click();
        } else {
            pwdInput.press("Enter");
        }
        page.waitForLoadState();
    }
}