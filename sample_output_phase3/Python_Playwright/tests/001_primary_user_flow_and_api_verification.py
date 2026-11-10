"""Corporate Playwright Test Case: TC-01 Primary User Flow & API Verification.

Adheres strictly to IEEE 829 Test Plan.
"""

import pytest
from playwright.sync_api import Page, expect
from pages.app_page import AppPage


class Test001PrimaryUserFlowAndApiVerification:
    """TC-01: Primary User Flow with UI Actions & Backend Status Code Interception."""

    @pytest.fixture(autouse=True)
    def setup(self, page: Page, base_url: str):
        self.page = page
        self.app = AppPage(page, base_url=base_url or "http://127.0.0.1:50751/")
        self.app.navigate()

    def test_tc01_primary_user_flow_and_api_verification(self):
        """Execute primary user flow and intercept expected backend API status codes."""
        # Step 1: Verify Page Title
        expect(self.page).to_have_title("Acme QA Portal")

        # Step 2: Trigger action with network API status code interception
        def perform_action():
            self.app.search_and_submit("playwright")

        response = self.app.wait_for_api_response(
            url_predicate="user",
            trigger_action=perform_action,
            expected_statuses=[200, 201],
        )
        assert response.status in [200, 201], (
            f"Expected status [200, 201] from {response.url}, got {response.status}"
        )
