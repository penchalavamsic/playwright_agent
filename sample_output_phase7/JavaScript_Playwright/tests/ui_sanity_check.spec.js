const { test, expect } = require('@playwright/test');
const { AppPage } = require('../pages/AppPage');

test.describe('Scenario TC-02: Page Load & Core UI Component Sanity', () => {
  let app;

  test.beforeEach(async ({ page }) => {
    app = new AppPage(page);
    await app.navigate();
  });

  test('002 - Verify Visibility of Discovered Interactive Controls', async () => {
    await expect(app.searchInput).toBeVisible();
    await expect(app.dashboardTab).toBeVisible();
  });
});