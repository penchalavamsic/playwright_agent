"""Base Page Object wrapper for corporate Playwright automation."""

from typing import Any, Callable, List, Optional
from playwright.sync_api import Page, Response, expect


class BasePage:
    def __init__(self, page: Page, base_url: str = ""):
        self.page = page
        self.base_url = base_url

    def navigate(self, path: str = "") -> None:
        target = f"{self.base_url}{path}" if path.startswith("/") and self.base_url else (path or self.base_url)
        self.page.goto(target, wait_until="domcontentloaded")

    def wait_for_api_response(
        self,
        url_predicate: str,
        trigger_action: Callable[[], Any],
        expected_statuses: Optional[List[int]] = None,
        timeout: float = 10000,
    ) -> Response:
        """Trigger an action while intercepting and validating an expected API response status."""
        expected = expected_statuses or [200, 201]
        with self.page.expect_response(
            lambda r: url_predicate.lower() in r.url.lower(),
            timeout=timeout,
        ) as response_info:
            trigger_action()
        response = response_info.value
        assert response.status in expected, (
            f"API {response.url} returned status {response.status}, expected {expected}"
        )
        return response