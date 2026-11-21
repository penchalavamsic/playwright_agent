const { expect } = require('@playwright/test');

class AppPage {
  /**
   * @param {import('@playwright/test').Page} page
   * @param {string} baseUrl
   */
  constructor(page, baseUrl = process.env.BASE_URL || '') {
    this.page = page;
    this.baseUrl = baseUrl;
  }

  async navigate() {
    await this.page.goto(this.baseUrl, { waitUntil: 'domcontentloaded' });
  }

  // -----------------------------------------------------------------------
  // Interactive Element Locators
  // -----------------------------------------------------------------------
  get searchInput() {
    // input [id]: Search Input
    return this.page.locator("#search-input");
  }
  get dashboardTab() {
    // button [data-testid]: Dashboard Tab
    return this.page.getByTestId("dashboard-tab");
  }

  // -----------------------------------------------------------------------
  // Flow Actions
  // -----------------------------------------------------------------------
  async searchAndSubmit(query) {
    await this.searchInput.fill(query);
    await this.page.keyboard.press('Enter');
  }

  async clickDashboardTab() {
    await this.dashboardTab.click();
  }
}

module.exports = { AppPage };