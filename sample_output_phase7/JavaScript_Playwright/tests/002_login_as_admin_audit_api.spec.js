const { test, expect } = require('@playwright/test');
const { AppPage } = require('../pages/AppPage');
const { LoginPage } = require('../pages/LoginPage');

test.describe('Scenario 002: LoginAsAdminAuditApi (ADMIN)', () => {
  let app;
  let loginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    app = new AppPage(page);
    await app.navigate();
    await loginPage.loginWithProfile(process.env.TEST_ACCESS_PROFILE || 'ADMIN');
  });

  test('002 - Execute Primary Flow & Intercept Network Status Codes', async ({ page }) => {
    await expect(page).toHaveTitle(/Shutterstock — Stock Images, Photos, Vectors, Video, and Music/);

    const expectedStatuses = [200, 201];
    const responsePromise = page.waitForResponse(
      (response) => response.url().toLowerCase().includes('search'.toLowerCase())
    );

    await app.searchAndSubmit('playwright');

    const response = await responsePromise;
    expect(expectedStatuses).toContain(response.status());
  });
});