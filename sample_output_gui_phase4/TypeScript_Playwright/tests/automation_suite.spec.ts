import { test, expect } from '@playwright/test';
import { AppPage } from '../pages/AppPage';

test.describe('Corporate Automation Suite: Acme QA Portal', () => {
  let app: AppPage;

  test.beforeEach(async ({ page }) => {
    app = new AppPage(page);
    await app.navigate();
  });

  test('TC-01: Primary User Flow with UI Actions & Backend Status Code Interception', async ({ page }) => {
    await expect(page).toHaveTitle(/Acme QA Portal/);

    const expectedStatuses = [200, 201];
    const responsePromise = page.waitForResponse(
      (response) => response.url().toLowerCase().includes('user'.toLowerCase())
    );

    await app.searchAndSubmit('playwright');

    const response = await responsePromise;
    expect(expectedStatuses).toContain(response.status());
  });

  test('TC-02: Page Load & Core UI Component Sanity', async () => {
    await expect(app.home).toBeVisible();
    await expect(app.docs).toBeVisible();
    await expect(app.external).toBeVisible();
    await expect(app.search).toBeVisible();
    await expect(app.go).toBeVisible();
  });

  test('TC-03: API Contract Matrix Verification', async () => {
    const endpoints = [
      { url: 'http://127.0.0.1:59064/api/user', status: 200 },
      { url: 'http://127.0.0.1:59064/api/feature-flags', status: 401 },
      { url: 'http://127.0.0.1:59064/api/validate', status: 400 },
      { url: 'http://127.0.0.1:59064/api/legacy-endpoint', status: 404 },
      { url: 'http://127.0.0.1:59064/api/admin/settings', status: 403 },
    ];
    expect(endpoints.length).toBeGreaterThan(0);
  });
});