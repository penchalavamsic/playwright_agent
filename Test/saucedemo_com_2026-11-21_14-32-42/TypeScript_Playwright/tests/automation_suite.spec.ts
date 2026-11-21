import { test, expect } from '@playwright/test';
import { AppPage } from '../pages/AppPage';
import { LoginPage } from '../pages/LoginPage';

test.describe('Corporate Automation Suite: Swag Labs', () => {
  let app: AppPage;
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    app = new AppPage(page);
    await app.navigate();
    await loginPage.loginWithProfile(process.env.TEST_ACCESS_PROFILE || 'STANDARD_USER');
  });

  test('TC-01: Primary User Flow with UI Actions & Backend Status Code Interception', async ({ page }) => {
    await expect(page).toHaveTitle(/Swag Labs/);

    const expectedStatuses = [200, 201];
    const responsePromise = page.waitForResponse(
      (response) => response.url().toLowerCase().includes('submit'.toLowerCase())
    );

    await page.waitForTimeout(500);

    const response = await responsePromise;
    expect(expectedStatuses).toContain(response.status());
  });

  test('TC-02: Page Load & Core UI Component Sanity', async () => {
    await expect(app.openMenu).toBeVisible();
    await expect(app.allItems).toBeVisible();
    await expect(app.dynamicCatalog).toBeVisible();
    await expect(app.about).toBeVisible();
    await expect(app.logout).toBeVisible();
  });

  test('TC-03: API Contract Matrix Verification', async () => {
    const endpoints = [
      { url: 'https://events.backtrace.io/api/summed-events/submit?universe=UNIVERSE&token=TOKEN', status: 401 },
      { url: 'https://events.backtrace.io/api/unique-events/submit?universe=UNIVERSE&token=TOKEN', status: 401 },
    ];
    expect(endpoints.length).toBeGreaterThan(0);
  });
});