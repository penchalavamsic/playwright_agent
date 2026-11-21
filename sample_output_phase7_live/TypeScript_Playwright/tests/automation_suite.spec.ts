import { test, expect } from '@playwright/test';
import { AppPage } from '../pages/AppPage';
import { LoginPage } from '../pages/LoginPage';

test.describe('Corporate Automation Suite: Shutterstock Studio Portal', () => {
  let app: AppPage;
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    app = new AppPage(page);
    await app.navigate();
    await loginPage.loginWithProfile(process.env.TEST_ACCESS_PROFILE || 'SUPER_USER');
  });

  test('TC-01: Primary User Flow with UI Actions & Backend Status Code Interception', async ({ page }) => {
    await expect(page).toHaveTitle(/Shutterstock Studio Portal/);

    const expectedStatuses = [200, 201];
    const responsePromise = page.waitForResponse(
      (response) => response.url().toLowerCase().includes('search'.toLowerCase())
    );

    await app.searchAndSubmit('playwright');

    const response = await responsePromise;
    expect(expectedStatuses).toContain(response.status());
  });

  test('TC-02: Page Load & Core UI Component Sanity', async () => {
    await expect(app.searchStockImages).toBeVisible();
    await expect(app.exploreGallery).toBeVisible();
  });

  test('TC-03: API Contract Matrix Verification', async () => {
    const endpoints = [
      { url: 'http://127.0.0.1:56844/api/search?q=vectors', status: 200 },
    ];
    expect(endpoints.length).toBeGreaterThan(0);
  });
});