const { test: base, expect, chromium } = require('@playwright/test');
const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const settingsFile = path.resolve(__dirname, '../browser-settings.json');
const settings = fs.existsSync(settingsFile) ? JSON.parse(fs.readFileSync(settingsFile, 'utf8')) : {};

class SessionGuard {
  constructor(page) { this.page = page; this.authenticated = false; }
  async passwordVisible() {
    try { return (await this.page.locator('input[type="password"]:visible').count()) > 0; }
    catch (error) {
      if (String(error).includes('Execution context was destroyed')) return false;
      throw error;
    }
  }
  async check() {
    if (this.authenticated && await this.passwordVisible()) throw new Error('Session lost: returned to login. No automatic retry attempted.');
  }
  async successVisible() {
    try { return await this.stablePageVisible(); }
    catch (error) {
      if (String(error).includes('Execution context was destroyed')) return false;
      throw error;
    }
  }
  async stablePageVisible() {
    let good = !(await this.passwordVisible());
    if (settings.auth_success_path) {
      const actual = new URL(this.page.url());
      const wanted = new URL(settings.auth_success_path, actual.origin);
      const pathname = wanted.pathname.replace(/\/$/, '') || '/';
      good = good && actual.origin === wanted.origin && (actual.pathname === pathname || (pathname !== '/' && actual.pathname.startsWith(pathname + '/')));
    }
    if (settings.auth_success_selector) good = good && await this.page.locator(settings.auth_success_selector).first().isVisible();
    return good && await this.page.locator('body').isVisible() && !!(await this.page.locator('body').innerText());
  }
  async login(action) {
    const timeout = Math.max(3000, Math.min(120000, settings.auth_timeout_ms || 15000));
    const entryDeadline = Date.now() + timeout;
    while (!(await this.passwordVisible()) && Date.now() < entryDeadline) {
      if ((settings.auth_success_path || settings.auth_success_selector) && await this.successVisible()) break;
      await this.page.waitForTimeout(100);
    }
    const hasForm = await this.passwordVisible();
    if (hasForm) await action();
    else if (!settings.auth_success_path && !settings.auth_success_selector) throw new Error('Configure an authenticated path or selector to verify the saved session.');
    const settle = Math.max(500, Math.min(timeout-500, settings.auth_settle_ms || 2500));
    const deadline = Date.now() + timeout;
    let since = 0, seen = false;
    while (Date.now() < deadline) {
      const visible = await this.passwordVisible();
      if (seen && visible) throw new Error('Login loop detected: dashboard returned to login. No automatic retry attempted.');
      const good = await this.successVisible();
      if (good) {
        seen = true; since ||= Date.now();
        if (Date.now()-since >= settle) { this.authenticated = true; return; }
      } else since = 0;
      await this.page.waitForTimeout(100);
    }
    throw new Error('Authentication did not remain valid before timeout. Check session/SSO settings.');
  }
}

const test = base.extend({
  qaRole: [process.env.TEST_ACCESS_PROFILE || 'PUBLIC', { option: true }],
  page: async ({ browser, baseURL, qaRole }, use, testInfo) => {
    const persistent = settings.session_mode === 'persistent';
    const identity = new URL(baseURL).origin + '|' + qaRole + '|' + (process.env.BROWSER_CHANNEL || 'msedge');
    const profile = path.resolve(__dirname, '.browser_profiles', crypto.createHash('sha256').update(identity).digest('hex').slice(0,24));
    const options = {ignoreHTTPSErrors:true, viewport:{width:1280,height:720}, recordVideo:{dir:testInfo.outputPath('videos')}};
    const context = persistent
      ? await chromium.launchPersistentContext(profile, { ...options, channel:process.env.BROWSER_CHANNEL || 'msedge', headless:!process.env.QA_HEADED })
      : await browser.newContext(options);
    const page = context.pages()[0] || await context.newPage();
    await context.tracing.start({screenshots:true, snapshots:true, sources:true});
    try { await use(page); }
    finally {
      const video = page.video();
      try {
        const screenshot = testInfo.outputPath('session-final.png');
        await page.screenshot({path:screenshot});
        await testInfo.attach('screenshot', {path:screenshot, contentType:'image/png'});
        const trace = testInfo.outputPath('session-trace.zip');
        await context.tracing.stop({path:trace});
        await testInfo.attach('trace', {path:trace, contentType:'application/zip'});
      } finally { await context.close(); }
      if (video) await testInfo.attach('video', {path:await video.path(), contentType:'video/webm'});
    }
  }
});
module.exports = {test, expect, SessionGuard};
