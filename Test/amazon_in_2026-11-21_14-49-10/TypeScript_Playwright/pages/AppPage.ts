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
  get mainContent(): Locator {
    // a [id]: main content
    return this.page.locator('#nav-assist-skip-to-main-content');
  }
  get searchAltForwardSlash(): Locator {
    // a [id]: Search, alt, forward slash
    return this.page.locator('#nav-assist-search');
  }
  get cartShiftAltC(): Locator {
    // a [id]: Cart, shift, alt, c
    return this.page.locator('#nav-assist-cart');
  }
  get homeShiftAltH(): Locator {
    // a [id]: Home, shift, alt, h
    return this.page.locator('#nav-assist-home');
  }
  get yourOrdersShiftAltO(): Locator {
    // a [id]: Your orders, shift, alt, o
    return this.page.locator('#nav-assist-your-orders');
  }
  get showHideShortcutsShiftAltZ(): Locator {
    // button [id]: Show/hide shortcuts, shift, alt, z
    return this.page.locator('#nav-assist-show-shortcuts');
  }
  get amazonIn(): Locator {
    // a [id]: Amazon.in
    return this.page.locator('#nav-logo-sprites');
  }
  get deliveringToBengaluru560087UpdateLocation(): Locator {
    // a [id]: Delivering to Bengaluru 560087 Update location
    return this.page.locator('#nav-global-location-popover-link');
  }
  get selectTheDepartmentYouWantToSearchIn(): Locator {
    // select [id]: Select the department you want to search in
    return this.page.locator('#searchDropdownBox');
  }
  get searchAmazonIn(): Locator {
    // input [id]: Search Amazon.in
    return this.page.locator('#twotabsearchtextbox');
  }
  get go(): Locator {
    // input [id]: Go
    return this.page.locator('#nav-search-submit-button');
  }
  get chooseALanguageForShoppingInAmazonIndiaTheCurrentS(): Locator {
    // a [role]: Choose a language for shopping in Amazon India. The current selection is English (EN).
    return this.page.getByRole('link', { name: 'Choose a language for shopping in Amazon India. The current selection is English (EN).', exact: true });
  }
  get expandToChangeLanguageOrCountry(): Locator {
    // button [css]: Expand to Change Language or Country
    return this.page.locator('#icp-nav-flyout > button');
  }
  get helloSignInAccountLists(): Locator {
    // a [role]: Hello, sign in Account & Lists
    return this.page.getByRole('link', { name: 'Hello, sign in Account & Lists', exact: true });
  }
  get expandAccountAndLists(): Locator {
    // button [role]: Expand Account and Lists
    return this.page.getByRole('button', { name: 'Expand Account and Lists', exact: true });
  }
  get returnsOrders(): Locator {
    // a [id]: Returns & Orders
    return this.page.locator('#nav-orders');
  }
  get el0itemsincart(): Locator {
    // a [id]: 0 items in cart
    return this.page.locator('#nav-cart');
  }
  get openAllCategoriesMenu(): Locator {
    // a [id]: Open All Categories Menu
    return this.page.locator('#nav-hamburger-menu');
  }
  get amazonPay(): Locator {
    // a [role]: Amazon Pay
    return this.page.getByRole('link', { name: 'Amazon Pay', exact: true });
  }
  get mobiles(): Locator {
    // a [role]: Mobiles
    return this.page.getByRole('link', { name: 'Mobiles', exact: true });
  }
  get flights(): Locator {
    // a [role]: Flights
    return this.page.getByRole('link', { name: 'Flights', exact: true });
  }
  get todaySDeals(): Locator {
    // a [role]: Today\'s Deals
    return this.page.getByRole('link', { name: 'Today\'s Deals', exact: true });
  }
  get coupons(): Locator {
    // a [role]: Coupons
    return this.page.getByRole('link', { name: 'Coupons', exact: true });
  }
  get newReleases(): Locator {
    // a [role]: New Releases
    return this.page.getByRole('link', { name: 'New Releases', exact: true });
  }
  get electronics(): Locator {
    // a [css]: Electronics
    return this.page.locator('a[href="/electronics/b/?ie=UTF8&node=976419031&ref_=nav_cs_electronics"]');
  }
  get bestsellers(): Locator {
    // a [role]: Bestsellers
    return this.page.getByRole('link', { name: 'Bestsellers', exact: true });
  }
  get fashion(): Locator {
    // a [role]: Fashion
    return this.page.getByRole('link', { name: 'Fashion', exact: true });
  }
  get computers(): Locator {
    // a [role]: Computers
    return this.page.getByRole('link', { name: 'Computers', exact: true });
  }
  get petSupplies(): Locator {
    // a [role]: Pet Supplies
    return this.page.getByRole('link', { name: 'Pet Supplies', exact: true });
  }
  get sportsFitnessOutdoors(): Locator {
    // a [role]: Sports, Fitness & Outdoors
    return this.page.getByRole('link', { name: 'Sports, Fitness & Outdoors', exact: true });
  }

  // -----------------------------------------------------------------------
  // Flow Actions
  // -----------------------------------------------------------------------
  async searchAndSubmit(query: string): Promise<void> {
    await this.searchAltForwardSlash.fill(query);
    await this.page.keyboard.press('Enter');
  }

  async clickDashboardTab(): Promise<void> {
    await this.page.getByRole('tab', { name: 'Dashboard', exact: true }).click();
  }
}