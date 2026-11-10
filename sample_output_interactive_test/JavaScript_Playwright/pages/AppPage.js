const { expect } = require('@playwright/test');

class AppPage {
  /**
   * @param {import('@playwright/test').Page} page
   * @param {string} baseUrl
   */
  constructor(page, baseUrl = 'http://127.0.0.1:63032/') {
    this.page = page;
    this.baseUrl = baseUrl;
  }

  async navigate() {
    await this.page.goto(this.baseUrl, { waitUntil: 'domcontentloaded' });
  }

  // -----------------------------------------------------------------------
  // Interactive Element Locators
  // -----------------------------------------------------------------------
  get home() {
    // a [role]: Home
    return this.page.getByRole('link', { name: 'Home', exact: true });
  }
  get docs() {
    // a [role]: Docs
    return this.page.getByRole('link', { name: 'Docs', exact: true });
  }
  get external() {
    // a [role]: External
    return this.page.getByRole('link', { name: 'External', exact: true });
  }
  get search() {
    // input [id]: Search
    return this.page.locator('#global-search');
  }
  get go() {
    // button [data-testid]: Go
    return this.page.getByTestId('search-submit');
  }
  get overview() {
    // button [role]: Overview
    return this.page.getByRole('tab', { name: 'Overview', exact: true });
  }
  get dashboard() {
    // button [role]: Dashboard
    return this.page.getByRole('tab', { name: 'Dashboard', exact: true });
  }
  get reports() {
    // button [role]: Reports
    return this.page.getByRole('tab', { name: 'Reports', exact: true });
  }
  get email() {
    // input [role]: Email
    return this.page.getByRole('textbox', { name: 'Email', exact: true });
  }
  get couponCode() {
    // input [role]: Coupon code
    return this.page.getByRole('textbox', { name: 'Coupon code', exact: true });
  }
  get element() {
    // select [css]: 
    return this.page.locator('select[name="country"]');
  }
  get element() {
    // textarea [css]: 
    return this.page.locator('textarea[name="notes"]');
  }
  get saveProfile() {
    // button [role]: Save profile
    return this.page.getByRole('button', { name: 'Save profile', exact: true });
  }
  get learnMore() {
    // a [css]: Learn more
    return this.page.locator('a[href="#a"]');
  }
  get learnMore() {
    // a [css]: Learn more
    return this.page.locator('a[href="#b"]');
  }
  get help() {
    // div [data-testid]: Help
    return this.page.getByTestId('help-widget');
  }
  get deleteAccount() {
    // button [data-testid]: Delete Account
    return this.page.getByTestId('delete-account');
  }

  // -----------------------------------------------------------------------
  // Flow Actions
  // -----------------------------------------------------------------------
  async searchAndSubmit(query) {
    await this.search.fill(query);
    await this.page.keyboard.press('Enter');
  }

  async clickDashboardTab() {
    await this.overview.click();
  }
}

module.exports = { AppPage };