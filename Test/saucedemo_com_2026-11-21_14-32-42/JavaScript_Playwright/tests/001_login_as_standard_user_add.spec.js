const { test, expect } = require('@playwright/test');
const { AppPage } = require('../pages/AppPage');
const { LoginPage } = require('../pages/LoginPage');

test.describe('Scenario 001: LoginAsStandardUserAdd (STANDARD_USER)', () => {
  let app;
  let loginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    app = new AppPage(page);
    await app.navigate();
    await loginPage.loginWithProfile(process.env.TEST_ACCESS_PROFILE || 'STANDARD_USER');
  });

  test('001 - Execute Primary Flow & Intercept Network Status Codes', async ({ page }) => {
    await expect(page).toHaveTitle(/Swag Labs/);

    const expectedStatuses = [200, 201];
    const responsePromise = page.waitForResponse(
      (response) => response.url().toLowerCase().includes('submit'.toLowerCase())
    );

    await page.waitForTimeout(500);

    const response = await responsePromise;
    expect(expectedStatuses).toContain(response.status());
  });
});