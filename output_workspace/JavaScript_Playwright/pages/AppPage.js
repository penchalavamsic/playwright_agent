const { expect } = require('@playwright/test');

class AppPage {
  /**
   * @param {import('@playwright/test').Page} page
   * @param {string} baseUrl
   */
  constructor(page, baseUrl = 'https://news.ycombinator.com') {
    this.page = page;
    this.baseUrl = baseUrl;
  }

  async navigate() {
    await this.page.goto(this.baseUrl, { waitUntil: 'domcontentloaded' });
  }

  // -----------------------------------------------------------------------
  // Interactive Element Locators
  // -----------------------------------------------------------------------
  get element() {
    // a [css]: 
    return this.page.locator('a[href="https://news.ycombinator.com"]');
  }
  get hackerNews() {
    // a [role]: Hacker News
    return this.page.getByRole('link', { name: 'Hacker News', exact: true });
  }
  get newElem() {
    // a [role]: new
    return this.page.getByRole('link', { name: 'new', exact: true });
  }
  get past() {
    // a [role]: past
    return this.page.getByRole('link', { name: 'past', exact: true });
  }
  get comments() {
    // a [role]: comments
    return this.page.getByRole('link', { name: 'comments', exact: true });
  }
  get ask() {
    // a [role]: ask
    return this.page.getByRole('link', { name: 'ask', exact: true });
  }
  get show() {
    // a [role]: show
    return this.page.getByRole('link', { name: 'show', exact: true });
  }
  get jobs() {
    // a [role]: jobs
    return this.page.getByRole('link', { name: 'jobs', exact: true });
  }
  get submit() {
    // a [role]: submit
    return this.page.getByRole('link', { name: 'submit', exact: true });
  }
  get login() {
    // a [role]: login
    return this.page.getByRole('link', { name: 'login', exact: true });
  }
  get element() {
    // a [css]: 
    return this.page.locator('a[href="vote?id=50427362&how=up&goto=news"]');
  }
  get paymentsCanadaAnnouncesLaunchOfCanadaSRealTimeRail() {
    // a [role]: Payments Canada announces launch of Canada\'s Real-Time Rail (RTR) payment system
    return this.page.getByRole('link', { name: 'Payments Canada announces launch of Canada\'s Real-Time Rail (RTR) payment system', exact: true });
  }
  get paymentsCa() {
    // a [role]: payments.ca
    return this.page.getByRole('link', { name: 'payments.ca', exact: true });
  }
  get ocd() {
    // a [role]: ocd
    return this.page.getByRole('link', { name: 'ocd', exact: true });
  }
  get el1hourago() {
    // a [css]: 1 hour ago
    return this.page.locator('tr:nth-of-type(2) > td:nth-of-type(2) > span > span:nth-of-type(2) > a');
  }
  get hide() {
    // a [css]: hide
    return this.page.locator('a[href="hide?id=50427362&goto=news"]');
  }
  get el99comments() {
    // a [role]: 99 comments
    return this.page.getByRole('link', { name: '99 comments', exact: true });
  }
  get element() {
    // a [css]: 
    return this.page.locator('a[href="vote?id=50424581&how=up&goto=news"]');
  }
  get foldEpicPaperAirplanes() {
    // a [role]: Fold Epic Paper Airplanes
    return this.page.getByRole('link', { name: 'Fold Epic Paper Airplanes', exact: true });
  }
  get foldableflightCom() {
    // a [role]: foldableflight.com
    return this.page.getByRole('link', { name: 'foldableflight.com', exact: true });
  }
  get vismit2000() {
    // a [role]: vismit2000
    return this.page.getByRole('link', { name: 'vismit2000', exact: true });
  }
  get el5hoursago() {
    // a [role]: 5 hours ago
    return this.page.getByRole('link', { name: '5 hours ago', exact: true });
  }
  get hide() {
    // a [css]: hide
    return this.page.locator('a[href="hide?id=50424581&goto=news"]');
  }
  get el86comments() {
    // a [role]: 86 comments
    return this.page.getByRole('link', { name: '86 comments', exact: true });
  }
  get element() {
    // a [css]: 
    return this.page.locator('a[href="vote?id=50426175&how=up&goto=news"]');
  }
  get magentaSolarPanelsMayBeAgrivoltaicsCleverestTrickY() {
    // a [role]: Magenta solar panels may be agrivoltaics\' cleverest trick yet
    return this.page.getByRole('link', { name: 'Magenta solar panels may be agrivoltaics\' cleverest trick yet', exact: true });
  }
  get anthropocenemagazineOrg() {
    // a [role]: anthropocenemagazine.org
    return this.page.getByRole('link', { name: 'anthropocenemagazine.org', exact: true });
  }
  get speckx() {
    // a [css]: speckx
    return this.page.locator('tr:nth-of-type(8) > td:nth-of-type(2) > span > a:nth-of-type(1)');
  }
  get el3hoursago() {
    // a [css]: 3 hours ago
    return this.page.locator('tr:nth-of-type(8) > td:nth-of-type(2) > span > span:nth-of-type(2) > a');
  }
  get hide() {
    // a [css]: hide
    return this.page.locator('a[href="hide?id=50426175&goto=news"]');
  }

  // -----------------------------------------------------------------------
  // Flow Actions
  // -----------------------------------------------------------------------
  async searchAndSubmit(query) {
    await this.element.fill(query);
    await this.page.keyboard.press('Enter');
  }

  async clickDashboardTab() {
    await this.page.getByRole('tab', { name: 'Dashboard', exact: true }).click();
  }
}

module.exports = { AppPage };