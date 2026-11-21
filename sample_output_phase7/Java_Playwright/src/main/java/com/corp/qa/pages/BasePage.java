package com.corp.qa.pages;

import com.microsoft.playwright.Page;
import com.microsoft.playwright.Response;
import java.util.List;

public class BasePage {
    protected final Page page;
    protected final String baseUrl;

    public BasePage(Page page, String baseUrl) {
        this.page = page;
        this.baseUrl = baseUrl;
    }

    public void navigate() {
        this.page.navigate(this.baseUrl);
    }

    public Response waitForApiResponse(String urlPredicate, Runnable action, List<Integer> expectedStatuses) {
        Response response = page.waitForResponse(
            r -> r.url().toLowerCase().contains(urlPredicate.toLowerCase()),
            action
        );
        if (expectedStatuses != null && !expectedStatuses.isEmpty()) {
            if (!expectedStatuses.contains(response.status())) {
                throw new AssertionError("API " + response.url() + " returned status " + response.status() 
                    + ", expected one of: " + expectedStatuses);
            }
        }
        return response;
    }
}