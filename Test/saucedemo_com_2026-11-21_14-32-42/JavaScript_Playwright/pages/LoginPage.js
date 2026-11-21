const fs = require('fs');
const path = require('path');

class LoginPage {
  /**
   * @param {import('@playwright/test').Page} page
   */
  constructor(page) {
    this.page = page;
  }

  _resolveCredentials(profileName) {
    const profilesPath = path.resolve(__dirname, '../../access-profiles.json');
    let usernameEnv = `${profileName}_USERNAME`;
    let passwordEnv = `${profileName}_PASSWORD`;
    if (fs.existsSync(profilesPath)) {
      try {
        const profiles = JSON.parse(fs.readFileSync(profilesPath, 'utf-8'));
        if (profiles[profileName]) {
          usernameEnv = profiles[profileName].username_env || usernameEnv;
          passwordEnv = profiles[profileName].password_env || passwordEnv;
        }
      } catch {
        // Fallback to standard naming
      }
    }
    return {
      username: process.env[usernameEnv] || '',
      password: process.env[passwordEnv] || '',
    };
  }

  async loginWithProfile(profileName) {
    const role = (profileName || process.env.TEST_ACCESS_PROFILE || '').trim().toUpperCase();
    if (!role || ['NONE', 'PUBLIC', 'NONE (PUBLIC URL)'].includes(role)) {
      return;
    }
    const { username, password } = this._resolveCredentials(role);
    if (!username && !password) return;

    const pwdInput = this.page.locator('input[type="password"]').first();
    try {
      await pwdInput.waitFor({ state: 'visible', timeout: 3000 });
    } catch {
      return;
    }

    const userInput = this.page.locator('input[type="email"], input[name*="user" i], input[type="text"]').first();
    if (username) await userInput.fill(username);
    if (password) await pwdInput.fill(password);

    const submitBtn = this.page.locator('button[type="submit"], input[type="submit"]').first();
    if (await submitBtn.isVisible()) {
      await submitBtn.click();
    } else {
      await pwdInput.press('Enter');
    }
    await this.page.waitForLoadState('networkidle').catch(() => {});
  }
}

module.exports = { LoginPage };