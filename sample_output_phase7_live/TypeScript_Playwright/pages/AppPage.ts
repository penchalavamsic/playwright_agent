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
  get searchStockImages(): Locator {
    // input [id]: Search stock images...
    return this.page.locator('#search-input');
  }
  get exploreGallery(): Locator {
    // button [id]: Explore Gallery
    return this.page.locator('#dashboard-tab');
  }

  // -----------------------------------------------------------------------
  // Flow Actions
  // -----------------------------------------------------------------------
  async searchAndSubmit(query: string): Promise<void> {
    await this.searchStockImages.fill(query);
    await this.page.keyboard.press('Enter');
  }

  async clickDashboardTab(): Promise<void> {
    await this.exploreGallery.click();
  }
}