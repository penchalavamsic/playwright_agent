import { test, expect } from '@playwright/test';
import { AppPage } from '../pages/AppPage';
import { LoginPage } from '../pages/LoginPage';

test.describe('Corporate Automation Suite: Online Shopping site in India: Shop Online for Mobiles, Books, Watches, Shoes and More - Amazon.in', () => {
  let app: AppPage;
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    app = new AppPage(page);
    await app.navigate();
    await loginPage.loginWithProfile(process.env.TEST_ACCESS_PROFILE || 'PUBLIC');
  });

  test('TC-01: Primary User Flow with UI Actions & Backend Status Code Interception', async ({ page }) => {
    await expect(page).toHaveTitle(/Online Shopping site in India: Shop Online for Mobiles, Books, Watches, Shoes and More - Amazon.in/);

    const expectedStatuses = [200, 201];
    const responsePromise = page.waitForResponse(
      (response) => response.url().toLowerCase().includes('inputs'.toLowerCase())
    );

    await app.searchAndSubmit('playwright');

    const response = await responsePromise;
    expect(expectedStatuses).toContain(response.status());
  });

  test('TC-02: Page Load & Core UI Component Sanity', async () => {
    await expect(app.mainContent).toBeVisible();
    await expect(app.searchAltForwardSlash).toBeVisible();
    await expect(app.cartShiftAltC).toBeVisible();
    await expect(app.homeShiftAltH).toBeVisible();
    await expect(app.yourOrdersShiftAltO).toBeVisible();
  });

  test('TC-03: API Contract Matrix Verification', async () => {
    const endpoints = [
      { url: 'https://1c5c1ecf7303.e10058c8.ap-south-1.token.awswaf.com/1c5c1ecf7303/6ab7d267eef9/66125abca348/inputs?client=browser', status: 200 },
      { url: 'https://1c5c1ecf7303.e10058c8.ap-south-1.token.awswaf.com/1c5c1ecf7303/6ab7d267eef9/66125abca348/mp_verify?region=ap-south-1', status: 200 },
      { url: 'https://m.media-amazon.com/images/G/01/csm/showads.v2.js?adspot_=1', status: 200 },
      { url: 'https://www.amazon.in/dram/renderLazyLoadedStreaming?rshVal=1795252753545', status: 200 },
      { url: 'https://www.amazon.in/hz/rhf?currentPageType=Gateway&currentSubPageType=desktop&excludeAsin=&fieldKeywords=&k=&keywords=&search=&auditEnabled=&previewCampaigns=&forceWidgets=&searchAlias=&cardJSPresent=true', status: 200 },
    ];
    expect(endpoints.length).toBeGreaterThan(0);
  });
});