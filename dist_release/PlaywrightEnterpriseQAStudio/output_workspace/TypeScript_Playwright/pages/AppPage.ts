import { Page, Locator, expect } from '@playwright/test';

export class AppPage {
  readonly page: Page;
  readonly baseUrl: string;

  constructor(page: Page, baseUrl: string = 'https://www.youtube.com/') {
    this.page = page;
    this.baseUrl = baseUrl;
  }

  async navigate(): Promise<void> {
    await this.page.goto(this.baseUrl, { waitUntil: 'domcontentloaded' });
  }

  // -----------------------------------------------------------------------
  // Interactive Element Locators
  // -----------------------------------------------------------------------
  get guide(): Locator {
    // button [role]: Guide
    return this.page.getByRole('button', { name: 'Guide', exact: true });
  }
  get youTubeHome(): Locator {
    // a [role]: YouTube Home
    return this.page.getByRole('link', { name: 'YouTube Home', exact: true });
  }
  get skipNavigation(): Locator {
    // button [role]: Skip navigation
    return this.page.getByRole('button', { name: 'Skip navigation', exact: true });
  }
  get search(): Locator {
    // input [role]: Search
    return this.page.getByRole('combobox', { name: 'Search', exact: true });
  }
  get search(): Locator {
    // button [role]: Search
    return this.page.getByRole('button', { name: 'Search', exact: true });
  }
  get searchWithYourVoice(): Locator {
    // button [role]: Search with your voice
    return this.page.getByRole('button', { name: 'Search with your voice', exact: true });
  }
  get element(): Locator {
    // a [css]: 
    return this.page.locator('ytd-topbar-menu-button-renderer > div > a');
  }
  get settings(): Locator {
    // button [role]: Settings
    return this.page.getByRole('button', { name: 'Settings', exact: true });
  }
  get signIn(): Locator {
    // a [css]: Sign in
    return this.page.locator('a[href="https://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en&ec=65620"]');
  }
  get home(): Locator {
    // a [css]: Home
    return this.page.locator('a[title="Home"]');
  }
  get shorts(): Locator {
    // a [css]: Shorts
    return this.page.locator('a[title="Shorts"]');
  }
  get subscriptions(): Locator {
    // a [css]: Subscriptions
    return this.page.locator('a[title="Subscriptions"]');
  }
  get you(): Locator {
    // a [css]: You
    return this.page.locator('a[title="You"]');
  }
  get history(): Locator {
    // a [css]: History
    return this.page.locator('a[title="History"]');
  }
  get signIn(): Locator {
    // a [css]: Sign in
    return this.page.locator('a[href="https://accounts.google.com/ServiceLogin?service=youtube&uilel=3&passive=true&continue=https%3A%2F%2Fwww.youtube.com%2Fsignin%3Faction_handle_signin%3Dtrue%26app%3Ddesktop%26hl%3Den%26next%3Dhttps%253A%252F%252Fwww.youtube.com%252F&hl=en"]');
  }
  get music(): Locator {
    // a [css]: Music
    return this.page.locator('a[title="Music"]');
  }
  get moviesTv(): Locator {
    // a [css]: Movies & TV
    return this.page.locator('a[title="Movies & TV"]');
  }
  get live(): Locator {
    // a [css]: Live
    return this.page.locator('a[title="Live"]');
  }
  get showMore(): Locator {
    // ytd-guide-entry-renderer [id]: Show more
    return this.page.locator('#expander-item');
  }
  get showMore(): Locator {
    // a [css]: Show more
    return this.page.locator('a[title="Show more"]');
  }
  get youTubePremium(): Locator {
    // a [css]: YouTube Premium
    return this.page.locator('a[title="YouTube Premium"]');
  }
  get youTubeMusic(): Locator {
    // a [css]: YouTube Music
    return this.page.locator('a[title="YouTube Music"]');
  }
  get youTubeKids(): Locator {
    // a [css]: YouTube Kids
    return this.page.locator('a[title="YouTube Kids"]');
  }
  get youTubeLabs(): Locator {
    // a [css]: YouTube Labs
    return this.page.locator('a[title="YouTube Labs"]');
  }
  get reportHistory(): Locator {
    // a [css]: Report history
    return this.page.locator('a[title="Report history"]');
  }
  get about(): Locator {
    // a [role]: About
    return this.page.getByRole('link', { name: 'About', exact: true });
  }
  get press(): Locator {
    // a [role]: Press
    return this.page.getByRole('link', { name: 'Press', exact: true });
  }
  get copyright(): Locator {
    // a [role]: Copyright
    return this.page.getByRole('link', { name: 'Copyright', exact: true });
  }
  get contactUs(): Locator {
    // a [role]: Contact us
    return this.page.getByRole('link', { name: 'Contact us', exact: true });
  }
  get creators(): Locator {
    // a [role]: Creators
    return this.page.getByRole('link', { name: 'Creators', exact: true });
  }

  // -----------------------------------------------------------------------
  // Flow Actions
  // -----------------------------------------------------------------------
  async searchAndSubmit(query: string): Promise<void> {
    await this.search.fill(query);
    await this.page.keyboard.press('Enter');
  }

  async clickDashboardTab(): Promise<void> {
    await this.page.getByRole('tab', { name: 'Dashboard', exact: true }).click();
  }
}