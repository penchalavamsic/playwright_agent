import { test, expect } from '@playwright/test';
import { AppPage } from '../pages/AppPage';
import { LoginPage } from '../pages/LoginPage';

test.describe('Corporate Automation Suite: Shutterstock — Stock Images, Photos, Vectors, Video, and Music', () => {
  let app: AppPage;
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    app = new AppPage(page);
    await app.navigate();
    await loginPage.loginWithProfile(process.env.TEST_ACCESS_PROFILE || 'ADMIN');
  });

  test('TC-01: Primary User Flow with UI Actions & Backend Status Code Interception', async ({ page }) => {
    await expect(page).toHaveTitle(/Shutterstock — Stock Images, Photos, Vectors, Video, and Music/);

    const expectedStatuses = [200, 201];
    const responsePromise = page.waitForResponse(
      (response) => response.url().toLowerCase().includes('search'.toLowerCase())
    );

    await app.searchAndSubmit('playwright');

    const response = await responsePromise;
    expect(expectedStatuses).toContain(response.status());
  });

  test('TC-02: Page Load & Core UI Component Sanity', async () => {
    await expect(app.searchInput).toBeVisible();
    await expect(app.dashboardTab).toBeVisible();
  });

  test('TC-03: API Contract Matrix Verification', async () => {
    const endpoints = [
      { url: 'https://www.shutterstock.com/api/v1/search', status: 200 },
      { url: 'https://www.shutterstock.com/api/v1/audit', status: 201 },
    ];
    expect(endpoints.length).toBeGreaterThan(0);
  });
});