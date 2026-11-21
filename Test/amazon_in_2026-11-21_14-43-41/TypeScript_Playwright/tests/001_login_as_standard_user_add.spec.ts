import { test, expect } from '@playwright/test';
import { AppPage } from '../pages/AppPage';
import { LoginPage } from '../pages/LoginPage';

test.describe('Scenario 001: LoginAsStandardUserAdd (PUBLIC)', () => {
  let app: AppPage;
  let loginPage: LoginPage;

  test.beforeEach(async ({ page }) => {
    loginPage = new LoginPage(page);
    app = new AppPage(page);
    await app.navigate();
    await loginPage.loginWithProfile(process.env.TEST_ACCESS_PROFILE || 'PUBLIC');
  });

  test('001 - Execute Primary Flow & Intercept Network Status Codes', async ({ page }) => {
    await expect(page).toHaveTitle(/Online Shopping site in India: Shop Online for Mobiles, Books, Watches, Shoes and More - Amazon.in/);

    const expectedStatuses = [200, 201];
    const responsePromise = page.waitForResponse(
      (response) => response.url().toLowerCase().includes('inputs'.toLowerCase())
    );

    await app.searchAndSubmit('playwright');

    const response = await responsePromise;
    expect(expectedStatuses).toContain(response.status());
  });
});