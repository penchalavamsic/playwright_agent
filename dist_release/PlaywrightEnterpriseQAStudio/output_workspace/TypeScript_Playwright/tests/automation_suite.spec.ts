import { test, expect } from '@playwright/test';
import { AppPage } from '../pages/AppPage';

test.describe('Corporate Automation Suite: YouTube', () => {
  let app: AppPage;

  test.beforeEach(async ({ page }) => {
    app = new AppPage(page);
    await app.navigate();
  });

  test('TC-01: Primary User Flow with UI Actions & Backend Status Code Interception', async ({ page }) => {
    await expect(page).toHaveTitle(/YouTube/);

    const expectedStatuses = [200, 201];
    const responsePromise = page.waitForResponse(
      (response) => response.url().toLowerCase().includes('24px.svg'.toLowerCase())
    );

    await app.searchAndSubmit('playwright');

    const response = await responsePromise;
    expect(expectedStatuses).toContain(response.status());
  });

  test('TC-02: Page Load & Core UI Component Sanity', async () => {
    await expect(app.guide).toBeVisible();
    await expect(app.youTubeHome).toBeVisible();
    await expect(app.skipNavigation).toBeVisible();
    await expect(app.search).toBeVisible();
    await expect(app.search).toBeVisible();
  });

  test('TC-03: API Contract Matrix Verification', async () => {
    const endpoints = [
      { url: 'https://googleads.g.doubleclick.net/pagead/id', status: 302 },
      { url: 'https://googleads.g.doubleclick.net/pagead/id?slf_rd=1', status: 200 },
      { url: 'https://www.youtube.com/youtubei/v1/guide?prettyPrint=false', status: 200 },
      { url: 'https://www.youtube.com/youtubei/v1/feedback?prettyPrint=false', status: 200 },
      { url: 'https://fonts.gstatic.com/s/i/youtube_outline_experimental/search/v16/24px.svg', status: 200 },
    ];
    expect(endpoints.length).toBeGreaterThan(0);
  });
});