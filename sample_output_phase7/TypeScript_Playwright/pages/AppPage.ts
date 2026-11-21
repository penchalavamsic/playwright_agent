import { Page, Locator, expect } from '@playwright/test';

export class AppPage {
  readonly page: Page;
  readonly baseUrl: string;

  constructor(page: Page, baseUrl: string = process.env.BASE_URL || '') {
    this.page = page;
    this.baseUrl = baseUrl;
  }

  async navigate(): Promise<void> {
    await this.page.goto(this.baseUrl, { waitUntil: 'domcontentloaded' });
  }

  // -----------------------------------------------------------------------
  // Interactive Element Locators
  // -----------------------------------------------------------------------
  get searchInput(): Locator {
    // input [id]: Search Input
    return this.page.locator("#search-input");
  }
  get dashboardTab(): Locator {
    // button [data-testid]: Dashboard Tab
    return this.page.getByTestId("dashboard-tab");
  }

  // -----------------------------------------------------------------------
  // Flow Actions
  // -----------------------------------------------------------------------
  async searchAndSubmit(query: string): Promise<void> {
    await this.searchInput.fill(query);
    await this.page.keyboard.press('Enter');
  }

  async clickDashboardTab(): Promise<void> {
    await this.dashboardTab.click();
  }
}