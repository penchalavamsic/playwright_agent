import { test, expect } from '@playwright/test';
import { AppPage } from '../pages/AppPage';

test.describe('Scenario TC-02: Page Load & Core UI Component Sanity', () => {
  let app: AppPage;

  test.beforeEach(async ({ page }) => {
    app = new AppPage(page);
    await app.navigate();
  });

  test('002 - Verify Visibility of Discovered Interactive Controls', async () => {
    await expect(app.home).toBeVisible();
    await expect(app.docs).toBeVisible();
    await expect(app.external).toBeVisible();
    await expect(app.search).toBeVisible();
    await expect(app.go).toBeVisible();
  });
});