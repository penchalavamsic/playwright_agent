"""Session policy and bounded authentication checks for deployed applications."""
import asyncio
import hashlib
import time
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from playwright.async_api import Error as PlaywrightError


def safe_url(url):
    parsed = urlsplit(url)
    host = parsed.hostname or ''
    if ':' in host:
        host = '[' + host + ']'
    if parsed.port:
        host += ':' + str(parsed.port)
    return urlunsplit((parsed.scheme, host, parsed.path, '', ''))


def profile_directory(root, url, role, channel):
    origin = urlsplit(url)
    identity = f'{origin.scheme}://{origin.netloc}|{role.upper()}|{channel}'
    return Path(root).resolve() / '.browser_profiles' / hashlib.sha256(identity.encode()).hexdigest()[:24]


def matches_path(url, expected):
    actual = urlsplit(url)
    wanted = urlsplit(expected)
    if wanted.netloc and (actual.scheme, actual.netloc) != (wanted.scheme, wanted.netloc):
        return False
    path = wanted.path.rstrip('/') or '/'
    return actual.path == path or (path != '/' and actual.path.startswith(path + '/'))


class AuthenticationGuard:
    def __init__(self, page, settings=None):
        self.page = page
        self.settings = settings or {}
        self.authenticated = False
        self.routes = []
        self.denied = []
        self.error = ''
        self.login_url = ''
        page.on('framenavigated', self._navigation)
        page.on('response', self._response)

    def _navigation(self, frame):
        if frame == self.page.main_frame:
            route = safe_url(frame.url)
            if not self.routes or self.routes[-1] != route:
                self.routes.append(route)
                self.routes[:] = self.routes[-30:]

    def _response(self, response):
        if response.status in (401, 403):
            self.denied.append({'url': safe_url(response.url), 'status': response.status})
            self.denied[:] = self.denied[-30:]

    async def password_visible(self):
        try:
            return await self.page.locator('input[type="password"]:visible').count() > 0
        except PlaywrightError as exc:
            if 'Execution context was destroyed' in str(exc):
                return False
            raise

    async def success_visible(self):
        try:
            return await self._success_visible()
        except PlaywrightError as exc:
            if 'Execution context was destroyed' in str(exc):
                return False
            raise

    async def _success_visible(self):
        if await self.password_visible():
            return False
        path = self.settings.get('auth_success_path', '')
        selector = self.settings.get('auth_success_selector', '')
        if path and not matches_path(self.page.url, path):
            return False
        if selector and not await self.page.locator(selector).first.is_visible():
            return False
        return await self.page.locator('body').is_visible() and bool(await self.page.locator('body').inner_text())

    async def wait_for_login(self, reused=False):
        if reused and not (self.settings.get('auth_success_path') or self.settings.get('auth_success_selector')):
            self.error = 'No login form found. Set an authenticated path or selector to verify a saved/SSO session.'
            raise AssertionError(self.error)
        timeout = max(3000, min(120000, int(self.settings.get('auth_timeout_ms', 15000))))
        settle = max(500, min(timeout - 500, int(self.settings.get('auth_settle_ms', 2500))))
        deadline = time.monotonic() + timeout / 1000
        since = None
        seen_success = False
        while time.monotonic() < deadline:
            visible_password = await self.password_visible()
            if seen_success and visible_password:
                self.error = 'Login loop detected: the application returned to its login form after reaching the authenticated page. No automatic login retry was attempted.'
                raise AssertionError(self.error)
            if await self.success_visible():
                seen_success = True
                since = since or time.monotonic()
                if time.monotonic() - since >= settle / 1000:
                    self.authenticated = True
                    return
            else:
                since = None
            await asyncio.sleep(.1)
        self.error = 'Authentication did not remain valid before the timeout. Check credentials, the authenticated path/selector, session cookies, or complete SSO/MFA in Interactive mode.'
        raise AssertionError(self.error)

    async def wait_for_entry(self):
        """Let SPA login forms mount before deciding whether to reuse a session."""
        timeout = max(3000, min(120000, int(self.settings.get('auth_timeout_ms', 15000))))
        deadline = time.monotonic() + timeout / 1000
        marker = self.settings.get('auth_success_path') or self.settings.get('auth_success_selector')
        while time.monotonic() < deadline:
            if await self.password_visible():
                return
            if marker and await self.success_visible():
                return
            await asyncio.sleep(.1)

    async def check_session(self):
        if self.authenticated and await self.password_visible():
            self.error = 'Session lost: the application returned to login during the flow. Remaining actions were stopped; no automatic login retry was attempted.'
            raise AssertionError(self.error)

    def diagnostics(self):
        return {'session_mode': self.settings.get('session_mode', 'fresh'), 'authenticated': self.authenticated,
                'navigation_routes': self.routes, 'unauthorized_responses': self.denied, 'error': self.error}
