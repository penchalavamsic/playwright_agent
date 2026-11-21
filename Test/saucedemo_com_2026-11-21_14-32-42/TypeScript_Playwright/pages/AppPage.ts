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
  get openMenu(): Locator {
    // button [role]: Open Menu
    return this.page.getByRole('button', { name: 'Open Menu', exact: true });
  }
  get allItems(): Locator {
    // a [id]: All Items
    return this.page.locator('#inventory_sidebar_link');
  }
  get dynamicCatalog(): Locator {
    // a [id]: Dynamic Catalog
    return this.page.locator('#dynamic_catalog_sidebar_link');
  }
  get about(): Locator {
    // a [id]: About
    return this.page.locator('#about_sidebar_link');
  }
  get logout(): Locator {
    // a [id]: Logout
    return this.page.locator('#logout_sidebar_link');
  }
  get resetAppState(): Locator {
    // a [id]: Reset App State
    return this.page.locator('#reset_sidebar_link');
  }
  get closeMenu(): Locator {
    // button [text]: Close Menu
    return this.page.getByText('Close Menu', { exact: true });
  }
  get cartEmpty(): Locator {
    // a [role]: Cart, empty
    return this.page.getByRole('button', { name: 'Cart, empty', exact: true });
  }
  get sortProducts(): Locator {
    // select [role]: Sort products
    return this.page.getByRole('combobox', { name: 'Sort products', exact: true });
  }
  get viewDetailsForSauceLabsBackpack(): Locator {
    // a [id]: View details for Sauce Labs Backpack
    return this.page.locator('#item_4_img_link');
  }
  get viewDetailsForSauceLabsBackpack(): Locator {
    // a [id]: View details for Sauce Labs Backpack
    return this.page.locator('#item_4_title_link');
  }
  get addToCart(): Locator {
    // button [id]: Add to cart
    return this.page.locator('#add-to-cart-sauce-labs-backpack');
  }
  get viewDetailsForSauceLabsBikeLight(): Locator {
    // a [id]: View details for Sauce Labs Bike Light
    return this.page.locator('#item_0_img_link');
  }
  get viewDetailsForSauceLabsBikeLight(): Locator {
    // a [id]: View details for Sauce Labs Bike Light
    return this.page.locator('#item_0_title_link');
  }
  get addToCart(): Locator {
    // button [id]: Add to cart
    return this.page.locator('#add-to-cart-sauce-labs-bike-light');
  }
  get viewDetailsForSauceLabsBoltTShirt(): Locator {
    // a [id]: View details for Sauce Labs Bolt T-Shirt
    return this.page.locator('#item_1_img_link');
  }
  get viewDetailsForSauceLabsBoltTShirt(): Locator {
    // a [id]: View details for Sauce Labs Bolt T-Shirt
    return this.page.locator('#item_1_title_link');
  }
  get addToCart(): Locator {
    // button [id]: Add to cart
    return this.page.locator('#add-to-cart-sauce-labs-bolt-t-shirt');
  }
  get viewDetailsForSauceLabsFleeceJacket(): Locator {
    // a [id]: View details for Sauce Labs Fleece Jacket
    return this.page.locator('#item_5_img_link');
  }
  get viewDetailsForSauceLabsFleeceJacket(): Locator {
    // a [id]: View details for Sauce Labs Fleece Jacket
    return this.page.locator('#item_5_title_link');
  }
  get addToCart(): Locator {
    // button [id]: Add to cart
    return this.page.locator('#add-to-cart-sauce-labs-fleece-jacket');
  }
  get viewDetailsForSauceLabsOnesie(): Locator {
    // a [id]: View details for Sauce Labs Onesie
    return this.page.locator('#item_2_img_link');
  }
  get viewDetailsForSauceLabsOnesie(): Locator {
    // a [id]: View details for Sauce Labs Onesie
    return this.page.locator('#item_2_title_link');
  }
  get addToCart(): Locator {
    // button [id]: Add to cart
    return this.page.locator('#add-to-cart-sauce-labs-onesie');
  }
  get viewDetailsForTestAllTheThingsTShirtRed(): Locator {
    // a [id]: View details for Test.allTheThings() T-Shirt (Red)
    return this.page.locator('#item_3_img_link');
  }
  get viewDetailsForTestAllTheThingsTShirtRed(): Locator {
    // a [id]: View details for Test.allTheThings() T-Shirt (Red)
    return this.page.locator('#item_3_title_link');
  }
  get addToCart(): Locator {
    // button [id]: Add to cart
    return this.page.locator('[id="add-to-cart-test.allthethings()-t-shirt-(red)"]');
  }
  get x(): Locator {
    // a [role]: X
    return this.page.getByRole('link', { name: 'X', exact: true });
  }
  get facebook(): Locator {
    // a [role]: Facebook
    return this.page.getByRole('link', { name: 'Facebook', exact: true });
  }
  get linkedIn(): Locator {
    // a [role]: LinkedIn
    return this.page.getByRole('link', { name: 'LinkedIn', exact: true });
  }

  // -----------------------------------------------------------------------
  // Flow Actions
  // -----------------------------------------------------------------------
  async searchAndSubmit(query: string): Promise<void> {
    await this.page.keyboard.type(query);
    await this.page.keyboard.press('Enter');
  }

  async clickDashboardTab(): Promise<void> {
    await this.page.getByRole('tab', { name: 'Dashboard', exact: true }).click();
  }
}