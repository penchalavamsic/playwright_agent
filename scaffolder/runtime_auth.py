"""Copied into generated Python suites; no dependency on the Studio installation."""
import json
import time
from pathlib import Path
from urllib.parse import urlsplit
from playwright.sync_api import Error as PlaywrightError


def settings():
    path = Path(__file__).resolve().parent.parent / 'browser-settings.json'
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else {}


class SessionGuard:
    def __init__(self, page):
        self.page, self.config, self.authenticated = page, settings(), False

    def check(self):
        if self.authenticated and self.password_visible():
            raise AssertionError('Session lost: returned to login. No automatic retry attempted.')

    def password_visible(self):
        try:
            return self.page.locator('input[type="password"]:visible').count() > 0
        except PlaywrightError as exc:
            if 'Execution context was destroyed' in str(exc):
                return False
            raise

    def success_visible(self):
        try:
            return self._success_visible()
        except PlaywrightError as exc:
            if 'Execution context was destroyed' in str(exc):
                return False
            raise

    def _success_visible(self):
        path = self.config.get('auth_success_path', '')
        actual, wanted = urlsplit(self.page.url), urlsplit(path)
        expected = wanted.path.rstrip('/') or '/'
        good = not self.password_visible()
        good = good and (not path or ((not wanted.netloc or (actual.scheme,actual.netloc)==(wanted.scheme,wanted.netloc)) and (actual.path==expected or (expected!='/' and actual.path.startswith(expected+'/')))))
        selector = self.config.get('auth_success_selector', '')
        if selector:
            good = good and self.page.locator(selector).first.is_visible()
        return good and self.page.locator('body').is_visible() and bool(self.page.locator('body').inner_text())

    def login(self, action):
        timeout = max(3000, min(120000, int(self.config.get('auth_timeout_ms', 15000))))
        entry_deadline = time.monotonic() + timeout/1000
        marker = self.config.get('auth_success_path') or self.config.get('auth_success_selector')
        while not self.password_visible() and time.monotonic() < entry_deadline:
            if marker and self.success_visible():
                break
            self.page.wait_for_timeout(100)
        form = self.password_visible()
        if form:
            action()
        elif not (self.config.get('auth_success_path') or self.config.get('auth_success_selector')):
            raise AssertionError('No login form found. Configure an authenticated path or selector for saved sessions.')
        settle = max(500, min(timeout-500, int(self.config.get('auth_settle_ms', 2500))))
        deadline, since, seen = time.monotonic() + timeout/1000, None, False
        while time.monotonic() < deadline:
            visible = self.password_visible()
            if seen and visible:
                raise AssertionError('Login loop detected: dashboard returned to login. No automatic retry attempted.')
            good = self.success_visible()
            if good:
                seen = True
                since = since or time.monotonic()
                if time.monotonic()-since >= settle/1000:
                    self.authenticated = True
                    return
            else:
                since = None
            self.page.wait_for_timeout(100)
        raise AssertionError('Authentication did not remain valid before timeout. Check session/SSO settings.')
