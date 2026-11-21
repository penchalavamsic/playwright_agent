"""Role-Based Login Page Object Model (reads .env and access-profiles.json)."""

import json
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv
from playwright.sync_api import Page
from pages.base_page import BasePage


_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(_PROJECT_ROOT / ".env", override=True)


class LoginPage(BasePage):
    """Handles dynamic role-based authentication without hardcoded credentials."""

    def __init__(self, page: Page, base_url: str = ""):
        resolved_url = base_url or os.getenv("BASE_URL", "")
        super().__init__(page, resolved_url)

    def _resolve_profile_credentials(self, profile_name: str) -> tuple[str, str]:
        profiles_path = _PROJECT_ROOT / "access-profiles.json"
        username_env = f"{profile_name}_USERNAME"
        password_env = f"{profile_name}_PASSWORD"
        if profiles_path.exists():
            try:
                profiles = json.loads(profiles_path.read_text(encoding="utf-8"))
                if profile_name in profiles:
                    username_env = profiles[profile_name].get("username_env", username_env)
                    password_env = profiles[profile_name].get("password_env", password_env)
            except Exception:
                pass
        return os.getenv(username_env, ""), os.getenv(password_env, "")

    def login_with_profile(self, profile_name: Optional[str] = None) -> None:
        """Authenticate using credentials for `profile_name` from .env & access-profiles.json."""
        load_dotenv(_PROJECT_ROOT / ".env", override=True)
        role = (profile_name or os.getenv("TEST_ACCESS_PROFILE", "")).strip()
        if not role or role.upper() in ("NONE", "PUBLIC", "NONE (PUBLIC URL)"):
            return

        username, password = self._resolve_profile_credentials(role.upper())
        if not username and not password:
            return

        pwd_input = self.page.page.locator("input[type=\"password\"]").first
        try:
            pwd_input.wait_for(state="visible", timeout=3000)
        except Exception:
            return

        user_input = self.page.page.locator("input[name*=\"user\" i]").first
        if username:
            user_input.fill(username)
        if password:
            pwd_input.fill(password)

        submit_btn = self.page.page.locator("input[type=\"submit\"]").first
        if submit_btn.is_visible():
            submit_btn.click()
        else:
            pwd_input.press("Enter")
        self.page.wait_for_load_state("networkidle")

    def login_as_profile(self, profile_name: Optional[str] = None) -> None:
        """Alias for login_with_profile."""
        self.login_with_profile(profile_name)