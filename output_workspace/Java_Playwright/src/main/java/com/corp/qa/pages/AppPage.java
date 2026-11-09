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
    public Locator getElement() {
        // Locator for a [css]: 
        return this.page.locator("a[href=\"https://news.ycombinator.com\"]");
    }
    public Locator getHackerNews() {
        // Locator for a [role]: Hacker News
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("Hacker News").setExact(true));
    }
    public Locator getNew() {
        // Locator for a [role]: new
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("new").setExact(true));
    }
    public Locator getPast() {
        // Locator for a [role]: past
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("past").setExact(true));
    }
    public Locator getComments() {
        // Locator for a [role]: comments
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("comments").setExact(true));
    }
    public Locator getAsk() {
        // Locator for a [role]: ask
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("ask").setExact(true));
    }
    public Locator getShow() {
        // Locator for a [role]: show
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("show").setExact(true));
    }
    public Locator getJobs() {
        // Locator for a [role]: jobs
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("jobs").setExact(true));
    }
    public Locator getSubmit() {
        // Locator for a [role]: submit
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("submit").setExact(true));
    }
    public Locator getLogin() {
        // Locator for a [role]: login
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("login").setExact(true));
    }
    public Locator getElement() {
        // Locator for a [css]: 
        return this.page.locator("a[href=\"vote?id=50427362&how=up&goto=news\"]");
    }
    public Locator getPaymentsCanadaAnnouncesLaunchOfCanadaSRealTimeRail() {
        // Locator for a [role]: Payments Canada announces launch of Canada\'s Real-Time Rail (RTR) payment system
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("Payments Canada announces launch of Canada's Real-Time Rail (RTR) payment system").setExact(true));
    }
    public Locator getPaymentsCa() {
        // Locator for a [role]: payments.ca
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("payments.ca").setExact(true));
    }
    public Locator getOcd() {
        // Locator for a [role]: ocd
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("ocd").setExact(true));
    }
    public Locator getEl1HourAgo() {
        // Locator for a [css]: 1 hour ago
        return this.page.locator("tr:nth-of-type(2) > td:nth-of-type(2) > span > span:nth-of-type(2) > a");
    }
    public Locator getHide() {
        // Locator for a [css]: hide
        return this.page.locator("a[href=\"hide?id=50427362&goto=news\"]");
    }
    public Locator getEl99Comments() {
        // Locator for a [role]: 99 comments
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("99 comments").setExact(true));
    }
    public Locator getElement() {
        // Locator for a [css]: 
        return this.page.locator("a[href=\"vote?id=50424581&how=up&goto=news\"]");
    }
    public Locator getFoldEpicPaperAirplanes() {
        // Locator for a [role]: Fold Epic Paper Airplanes
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("Fold Epic Paper Airplanes").setExact(true));
    }
    public Locator getFoldableflightCom() {
        // Locator for a [role]: foldableflight.com
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("foldableflight.com").setExact(true));
    }
    public Locator getVismit2000() {
        // Locator for a [role]: vismit2000
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("vismit2000").setExact(true));
    }
    public Locator getEl5HoursAgo() {
        // Locator for a [role]: 5 hours ago
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("5 hours ago").setExact(true));
    }
    public Locator getHide() {
        // Locator for a [css]: hide
        return this.page.locator("a[href=\"hide?id=50424581&goto=news\"]");
    }
    public Locator getEl86Comments() {
        // Locator for a [role]: 86 comments
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("86 comments").setExact(true));
    }
    public Locator getElement() {
        // Locator for a [css]: 
        return this.page.locator("a[href=\"vote?id=50426175&how=up&goto=news\"]");
    }
    public Locator getMagentaSolarPanelsMayBeAgrivoltaicsCleverestTrickY() {
        // Locator for a [role]: Magenta solar panels may be agrivoltaics\' cleverest trick yet
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("Magenta solar panels may be agrivoltaics' cleverest trick yet").setExact(true));
    }
    public Locator getAnthropocenemagazineOrg() {
        // Locator for a [role]: anthropocenemagazine.org
        return this.page.getByRole(AriaRole.LINK, new Page.GetByRoleOptions().setName("anthropocenemagazine.org").setExact(true));
    }
    public Locator getSpeckx() {
        // Locator for a [css]: speckx
        return this.page.locator("tr:nth-of-type(8) > td:nth-of-type(2) > span > a:nth-of-type(1)");
    }
    public Locator getEl3HoursAgo() {
        // Locator for a [css]: 3 hours ago
        return this.page.locator("tr:nth-of-type(8) > td:nth-of-type(2) > span > span:nth-of-type(2) > a");
    }
    public Locator getHide() {
        // Locator for a [css]: hide
        return this.page.locator("a[href=\"hide?id=50426175&goto=news\"]");
    }

    // -----------------------------------------------------------------------
    // Business Flow Actions
    // -----------------------------------------------------------------------
    public void searchAndSubmit(String query) {
        getElement().fill(query);
        page.keyboard().press("Enter");
    }

    public void clickDashboardTab() {
        page.getByRole(AriaRole.TAB, new Page.GetByRoleOptions().setName("Dashboard").setExact(true)).click();
    }
}