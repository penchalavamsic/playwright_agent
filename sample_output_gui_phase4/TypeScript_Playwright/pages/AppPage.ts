import { Page, Locator, expect } from '@playwright/test';

export class AppPage {
  readonly page: Page;
  readonly baseUrl: string;

  constructor(page: Page, baseUrl: string = 'http://127.0.0.1:50992/') {
    this.page = page;
    this.baseUrl = baseUrl;
  }

  async navigate(): Promise<void> {
    await this.page.goto(this.baseUrl, { waitUntil: 'domcontentloaded' });
  }

  // -----------------------------------------------------------------------
  // Interactive Element Locators
  // -----------------------------------------------------------------------
  get home(): Locator {
    // a [role]: Home
    return this.page.getByRole('link', { name: 'Home', exact: true });
  }
  get docs(): Locator {
    // a [role]: Docs
    return this.page.getByRole('link', { name: 'Docs', exact: true });
  }
  get external(): Locator {
    // a [role]: External
    return this.page.getByRole('link', { name: 'External', exact: true });
  }
  get search(): Locator {
    // input [id]: Search
    return this.page.locator('#global-search');
  }
  get go(): Locator {
    // button [data-testid]: Go
    return this.page.getByTestId('search-submit');
  }
  get overview(): Locator {
    // button [role]: Overview
    return this.page.getByRole('tab', { name: 'Overview', exact: true });
  }
  get dashboard(): Locator {
    // button [role]: Dashboard
    return this.page.getByRole('tab', { name: 'Dashboard', exact: true });
  }
  get reports(): Locator {
    // button [role]: Reports
    return this.page.getByRole('tab', { name: 'Reports', exact: true });
  }
  get email(): Locator {
    // input [role]: Email
    return this.page.getByRole('textbox', { name: 'Email', exact: true });
  }
  get couponCode(): Locator {
    // input [role]: Coupon code
    return this.page.getByRole('textbox', { name: 'Coupon code', exact: true });
  }
  get element(): Locator {
    // select [css]: 
    return this.page.locator('select[name="country"]');
  }
  get element(): Locator {
    // textarea [css]: 
    return this.page.locator('textarea[name="notes"]');
  }
  get saveProfile(): Locator {
    // button [role]: Save profile
    return this.page.getByRole('button', { name: 'Save profile', exact: true });
  }
  get learnMore(): Locator {
    // a [css]: Learn more
    return this.page.locator('a[href="#a"]');
  }
  get learnMore(): Locator {
    // a [css]: Learn more
    return this.page.locator('a[href="#b"]');
  }
  get help(): Locator {
    // div [data-testid]: Help
    return this.page.getByTestId('help-widget');
  }
  get deleteAccount(): Locator {
    // button [data-testid]: Delete Account
    return this.page.getByTestId('delete-account');
  }

  // -----------------------------------------------------------------------
  // Flow Actions
  // -----------------------------------------------------------------------
  async searchAndSubmit(query: string): Promise<void> {
    await this.search.fill(query);
    await this.page.keyboard.press('Enter');
  }

  async clickDashboardTab(): Promise<void> {
    await this.overview.click();
  }
}