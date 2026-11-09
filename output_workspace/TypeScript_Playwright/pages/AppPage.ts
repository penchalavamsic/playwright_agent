import { Page, Locator, expect } from '@playwright/test';

export class AppPage {
  readonly page: Page;
  readonly baseUrl: string;

  constructor(page: Page, baseUrl: string = 'https://news.ycombinator.com') {
    this.page = page;
    this.baseUrl = baseUrl;
  }

  async navigate(): Promise<void> {
    await this.page.goto(this.baseUrl, { waitUntil: 'domcontentloaded' });
  }

  // -----------------------------------------------------------------------
  // Interactive Element Locators
  // -----------------------------------------------------------------------
  get element(): Locator {
    // a [css]: 
    return this.page.locator('a[href="https://news.ycombinator.com"]');
  }
  get hackerNews(): Locator {
    // a [role]: Hacker News
    return this.page.getByRole('link', { name: 'Hacker News', exact: true });
  }
  get newElem(): Locator {
    // a [role]: new
    return this.page.getByRole('link', { name: 'new', exact: true });
  }
  get past(): Locator {
    // a [role]: past
    return this.page.getByRole('link', { name: 'past', exact: true });
  }
  get comments(): Locator {
    // a [role]: comments
    return this.page.getByRole('link', { name: 'comments', exact: true });
  }
  get ask(): Locator {
    // a [role]: ask
    return this.page.getByRole('link', { name: 'ask', exact: true });
  }
  get show(): Locator {
    // a [role]: show
    return this.page.getByRole('link', { name: 'show', exact: true });
  }
  get jobs(): Locator {
    // a [role]: jobs
    return this.page.getByRole('link', { name: 'jobs', exact: true });
  }
  get submit(): Locator {
    // a [role]: submit
    return this.page.getByRole('link', { name: 'submit', exact: true });
  }
  get login(): Locator {
    // a [role]: login
    return this.page.getByRole('link', { name: 'login', exact: true });
  }
  get element(): Locator {
    // a [css]: 
    return this.page.locator('a[href="vote?id=50427362&how=up&goto=news"]');
  }
  get paymentsCanadaAnnouncesLaunchOfCanadaSRealTimeRail(): Locator {
    // a [role]: Payments Canada announces launch of Canada\'s Real-Time Rail (RTR) payment system
    return this.page.getByRole('link', { name: 'Payments Canada announces launch of Canada\'s Real-Time Rail (RTR) payment system', exact: true });
  }
  get paymentsCa(): Locator {
    // a [role]: payments.ca
    return this.page.getByRole('link', { name: 'payments.ca', exact: true });
  }
  get ocd(): Locator {
    // a [role]: ocd
    return this.page.getByRole('link', { name: 'ocd', exact: true });
  }
  get el1hourago(): Locator {
    // a [css]: 1 hour ago
    return this.page.locator('tr:nth-of-type(2) > td:nth-of-type(2) > span > span:nth-of-type(2) > a');
  }
  get hide(): Locator {
    // a [css]: hide
    return this.page.locator('a[href="hide?id=50427362&goto=news"]');
  }
  get el99comments(): Locator {
    // a [role]: 99 comments
    return this.page.getByRole('link', { name: '99 comments', exact: true });
  }
  get element(): Locator {
    // a [css]: 
    return this.page.locator('a[href="vote?id=50424581&how=up&goto=news"]');
  }
  get foldEpicPaperAirplanes(): Locator {
    // a [role]: Fold Epic Paper Airplanes
    return this.page.getByRole('link', { name: 'Fold Epic Paper Airplanes', exact: true });
  }
  get foldableflightCom(): Locator {
    // a [role]: foldableflight.com
    return this.page.getByRole('link', { name: 'foldableflight.com', exact: true });
  }
  get vismit2000(): Locator {
    // a [role]: vismit2000
    return this.page.getByRole('link', { name: 'vismit2000', exact: true });
  }
  get el5hoursago(): Locator {
    // a [role]: 5 hours ago
    return this.page.getByRole('link', { name: '5 hours ago', exact: true });
  }
  get hide(): Locator {
    // a [css]: hide
    return this.page.locator('a[href="hide?id=50424581&goto=news"]');
  }
  get el86comments(): Locator {
    // a [role]: 86 comments
    return this.page.getByRole('link', { name: '86 comments', exact: true });
  }
  get element(): Locator {
    // a [css]: 
    return this.page.locator('a[href="vote?id=50426175&how=up&goto=news"]');
  }
  get magentaSolarPanelsMayBeAgrivoltaicsCleverestTrickY(): Locator {
    // a [role]: Magenta solar panels may be agrivoltaics\' cleverest trick yet
    return this.page.getByRole('link', { name: 'Magenta solar panels may be agrivoltaics\' cleverest trick yet', exact: true });
  }
  get anthropocenemagazineOrg(): Locator {
    // a [role]: anthropocenemagazine.org
    return this.page.getByRole('link', { name: 'anthropocenemagazine.org', exact: true });
  }
  get speckx(): Locator {
    // a [css]: speckx
    return this.page.locator('tr:nth-of-type(8) > td:nth-of-type(2) > span > a:nth-of-type(1)');
  }
  get el3hoursago(): Locator {
    // a [css]: 3 hours ago
    return this.page.locator('tr:nth-of-type(8) > td:nth-of-type(2) > span > span:nth-of-type(2) > a');
  }
  get hide(): Locator {
    // a [css]: hide
    return this.page.locator('a[href="hide?id=50426175&goto=news"]');
  }

  // -----------------------------------------------------------------------
  // Flow Actions
  // -----------------------------------------------------------------------
  async searchAndSubmit(query: string): Promise<void> {
    await this.element.fill(query);
    await this.page.keyboard.press('Enter');
  }

  async clickDashboardTab(): Promise<void> {
    await this.page.getByRole('tab', { name: 'Dashboard', exact: true }).click();
  }
}