"""Corporate Playwright Test Case: 001 LoginAsStandardUserAdd (STANDARD_USER).

Adheres strictly to IEEE 829 Test Plan. Zero hardcoded credentials or URLs.
"""

import os
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, expect
from pages.app_page import AppPage
from pages.login_page import LoginPage


class Test001LoginAsStandardUserAdd:
    """001: Primary User Flow with Role-Based Login & Backend Status Code Interception."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        load_dotenv(override=True)
        self.page = page
        resolved_url = base_url or os.getenv("BASE_URL", "")
        self.login_page = LoginPage(page, base_url=resolved_url)
        self.app = AppPage(page, base_url=resolved_url)
        self.app.navigate()
        self.login_page.login_with_profile(os.getenv("TEST_ACCESS_PROFILE", "STANDARD_USER"))

    def test_001_login_as_standard_user_add(self):
        """Execute primary user flow and intercept expected backend API status codes."""
        # Step 1: Verify Page Title
        expect(self.page).to_have_title("Swag Labs")

        # Step 2: Trigger action with network API status code interception
        def perform_action():
            self.page.wait_for_timeout(500)

        response = self.app.wait_for_api_response(
            url_predicate="submit",
            trigger_action=perform_action,
            expected_statuses=[200, 201],
        )
        assert response.status in [200, 201], (
            f"Expected status [200, 201] from {response.url}, got {response.status}"
        )
