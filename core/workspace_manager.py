"""Local Multi-Day Workspace & Role-Based Credential Manager (Phase 6).

100% offline, zero external API calls.
Persists project state in `<project_root>/.qa_studio_project.json`,
manages local `.env`, `.env.example`, `access-profiles.json`, and `.gitignore`,
and tracks sequential test numbering across multi-day sessions.
"""

from __future__ import annotations

import base64
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse


DEFAULT_PROFILE_CHOICES: List[str] = [
    "None (Public URL)",
    "SUPER_USER",
    "ADMIN",
    "SUPER_USER_ADMIN_USER",
]


class WorkspaceManager:
    """Manages persistent project state, role-based accounts, and .env files."""

    PROJECT_FILE = ".qa_studio_project.json"
    ENV_FILE = ".env"
    ENV_EXAMPLE_FILE = ".env.example"
    PROFILES_FILE = "access-profiles.json"
    GITIGNORE_FILE = ".gitignore"

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.state: Dict[str, Any] = {
            "project_name": self.project_root.name or "qa_automation_project",
            "target_url": "",
            "target_languages": ["Python", "Java", "TypeScript", "JavaScript"],
            "last_sequence_number": 0,
            "history": [],
            "accounts": {},
            "browser_settings": {},
        }
        self._load_if_exists()

    # ------------------------------------------------------------------
    # Credential Encoding Helpers (100% Local)
    # ------------------------------------------------------------------
    @staticmethod
    def encode_password(password: str) -> str:
        """Encode a password with Base64 for local workspace storage."""
        if not password:
            return ""
        return base64.b64encode(password.encode("utf-8")).decode("ascii")

    @staticmethod
    def decode_password(password_b64: str) -> str:
        """Decode a Base64-encoded password from local workspace storage."""
        if not password_b64:
            return ""
        try:
            return base64.b64decode(password_b64.encode("ascii")).decode("utf-8")
        except Exception:
            return ""

    @staticmethod
    def normalize_role(role: str) -> str:
        """Normalize a role name to UPPER_SNAKE_CASE (e.g. 'super user' -> 'SUPER_USER')."""
        cleaned = (role or "").strip().upper()
        for ch in (" ", "-", "."):
            cleaned = cleaned.replace(ch, "_")
        while "__" in cleaned:
            cleaned = cleaned.replace("__", "_")
        return cleaned.strip("_")

    @staticmethod
    def sanitize_domain_for_folder(target_url: str) -> str:
        """Extract sanitized website domain from target_url (e.g., https://www.saucedemo.com -> saucedemo_com)."""
        raw = (target_url or "").strip()
        if raw and not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", raw):
            raw = "https://" + raw
        parsed = urlparse(raw)
        host = (parsed.hostname or "").lower()
        host = re.sub(r"^www\.", "", host)
        sanitized = re.sub(r"[^a-z0-9]+", "_", host).strip("_")
        return sanitized or "web_app"

    @classmethod
    def resolve_run_output_dir(
        cls,
        base_output_dir: str | Path,
        target_url: str,
        timestamp: Optional[str] = None,
    ) -> Path:
        """Resolve `<base_output_dir>/<sanitized_domain>_<YYYY-MM-DD_HH-MM-SS>` for new runs,
        or preserve `base_output_dir` when reopening an existing project workspace."""
        base = Path(base_output_dir).resolve()
        if (base / cls.PROJECT_FILE).exists():
            return base
        if re.search(r"_\d{4}-\d{2}-\d{2}_\d{2}-\d{2}-\d{2}$", base.name):
            return base
        domain_slug = cls.sanitize_domain_for_folder(target_url)
        ts = timestamp or datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return base / f"{domain_slug}_{ts}"

    # ------------------------------------------------------------------
    # Persistence: Load & Save
    # ------------------------------------------------------------------
    def _load_if_exists(self) -> bool:
        proj_path = self.project_root / self.PROJECT_FILE
        if not proj_path.exists():
            return False
        try:
            data = json.loads(proj_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                self.state["project_name"] = data.get("project_name", self.state["project_name"])
                self.state["target_url"] = data.get("target_url", "")
                self.state["target_languages"] = data.get(
                    "target_languages", self.state["target_languages"]
                )
                self.state["last_sequence_number"] = int(data.get("last_sequence_number", 0))
                self.state["history"] = list(data.get("history", []))
                self.state["accounts"] = dict(data.get("accounts", {}))
                self.state["browser_settings"] = dict(data.get("browser_settings", {}))
                return True
        except Exception:
            pass
        return False

    @classmethod
    def load_project_state(cls, folder_path: str | Path) -> "WorkspaceManager":
        """Load an existing project workspace from `folder_path`."""
        return cls(folder_path)

    def save_project_state(self) -> Path:
        """Persist current workspace state to `<project_root>/.qa_studio_project.json`."""
        self.project_root.mkdir(parents=True, exist_ok=True)
        proj_path = self.project_root / self.PROJECT_FILE
        proj_path.write_text(json.dumps(self.state, indent=2), encoding="utf-8")
        return proj_path

    def exists(self) -> bool:
        """Return True if `.qa_studio_project.json` exists in `project_root`."""
        return (self.project_root / self.PROJECT_FILE).exists()

    # ------------------------------------------------------------------
    # Account / Role Management
    # ------------------------------------------------------------------
    def add_or_update_account(self, role: str, username: str, password: str) -> str:
        """Save or update credentials for a role in local state."""
        norm_role = self.normalize_role(role)
        if not norm_role:
            raise ValueError("Role name cannot be empty.")
        accounts = self.state.setdefault("accounts", {})
        accounts[norm_role] = {
            "username": username.strip(),
            "password_b64": self.encode_password(password),
        }
        return norm_role

    def get_credentials_for_role(self, role: str) -> Optional[Dict[str, str]]:
        """Return decoded `{'username': ..., 'password': ...}` for `role`, or None."""
        norm_role = self.normalize_role(role)
        entry = self.state.get("accounts", {}).get(norm_role)
        if not entry:
            return None
        return {
            "username": entry.get("username", ""),
            "password": self.decode_password(entry.get("password_b64", "")),
        }

    def get_all_decrypted_accounts(self) -> Dict[str, Dict[str, str]]:
        """Return all saved accounts with decoded passwords for runtime execution."""
        result: Dict[str, Dict[str, str]] = {}
        for role, entry in self.state.get("accounts", {}).items():
            result[role] = {
                "username": entry.get("username", ""),
                "password": self.decode_password(entry.get("password_b64", "")),
            }
        return result

    def get_saved_roles(self) -> List[str]:
        """Return list of role names configured in this workspace."""
        return list(self.state.get("accounts", {}).keys())

    # ------------------------------------------------------------------
    # Multi-Day Sequence Tracking
    # ------------------------------------------------------------------
    def next_sequence_number(self) -> int:
        """Return the next 1-based sequence number (e.g. 1, 2, 3...)."""
        return int(self.state.get("last_sequence_number", 0)) + 1

    def record_run(
        self,
        sequence_number: int,
        test_id: str,
        title: str,
        access_profile: str,
        target_url: str = "",
        target_languages: Optional[List[str]] = None,
        files: Optional[List[str]] = None,
    ) -> None:
        """Record a completed generation run and advance `last_sequence_number`."""
        current_last = int(self.state.get("last_sequence_number", 0))
        if sequence_number > current_last:
            self.state["last_sequence_number"] = sequence_number
        if target_url:
            self.state["target_url"] = target_url
        if target_languages:
            self.state["target_languages"] = list(target_languages)

        history = self.state.setdefault("history", [])
        history.append(
            {
                "sequence_number": sequence_number,
                "test_id": test_id,
                "title": title,
                "access_profile": access_profile,
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "files": files or [],
            }
        )

    # ------------------------------------------------------------------
    # .env, .env.example, access-profiles.json, .gitignore Writers
    # ------------------------------------------------------------------
    def write_env_and_profiles(
        self,
        active_role: str = "",
        target_url: str = "",
    ) -> List[str]:
        """Generate/update `.env`, `.env.example`, `access-profiles.json`, and `.gitignore`."""
        self.project_root.mkdir(parents=True, exist_ok=True)
        written: List[str] = []
        settings_path = self.project_root / 'browser-settings.json'
        settings_path.write_text(json.dumps(self.state.get('browser_settings', {}), indent=2), encoding='utf-8')
        written.append(str(settings_path))

        url = (target_url or self.state.get("target_url", "")).strip()
        if url:
            self.state["target_url"] = url

        norm_active = ""
        if active_role and active_role.strip() not in ("None (Public URL)", "NONE", "PUBLIC"):
            norm_active = self.normalize_role(active_role)

        accounts = self.state.get("accounts", {})

        # 1. Write .env
        env_lines = [
            "# Auto-generated by Playwright Enterprise QA Agent Studio (100% Local)",
            f"BASE_URL={url}",
            f"TEST_ACCESS_PROFILE={norm_active}",
            "",
            "# Role-Based Credentials",
        ]
        example_lines = [
            "# Example environment configuration (safe to commit to Git)",
            "BASE_URL=https://example.com",
            f"TEST_ACCESS_PROFILE={norm_active or 'ADMIN'}",
            "",
            "# Role-Based Credentials (fill in locally in .env)",
        ]

        profiles_map: Dict[str, Dict[str, str]] = {}
        for role, entry in accounts.items():
            u_key = f"{role}_USERNAME"
            p_key = f"{role}_PASSWORD"
            username = entry.get("username", "")
            password = self.decode_password(entry.get("password_b64", ""))
            env_lines.append(f"{u_key}={username}")
            env_lines.append(f"{p_key}={password}")
            example_lines.append(f"{u_key}=your_{role.lower()}_username")
            example_lines.append(f"{p_key}=your_{role.lower()}_password")
            profiles_map[role] = {
                "username_env": u_key,
                "password_env": p_key,
            }

        # Ensure active role is represented in access-profiles.json even if added ad-hoc
        if norm_active and norm_active not in profiles_map:
            u_key = f"{norm_active}_USERNAME"
            p_key = f"{norm_active}_PASSWORD"
            profiles_map[norm_active] = {
                "username_env": u_key,
                "password_env": p_key,
            }
            example_lines.append(f"{u_key}=your_{norm_active.lower()}_username")
            example_lines.append(f"{p_key}=your_{norm_active.lower()}_password")

        env_path = self.project_root / self.ENV_FILE
        env_path.write_text("\n".join(env_lines) + "\n", encoding="utf-8")
        written.append(str(env_path))

        env_ex_path = self.project_root / self.ENV_EXAMPLE_FILE
        env_ex_path.write_text("\n".join(example_lines) + "\n", encoding="utf-8")
        written.append(str(env_ex_path))

        # 2. Write access-profiles.json
        profiles_path = self.project_root / self.PROFILES_FILE
        profiles_path.write_text(json.dumps(profiles_map, indent=2) + "\n", encoding="utf-8")
        written.append(str(profiles_path))

        # 3. Write / update .gitignore
        gitignore_path = self.project_root / self.GITIGNORE_FILE
        required_ignores = [
            ".browser_profiles/",
            ".env",
            ".qa_studio_project.json",
            "__pycache__/",
            ".venv/",
            "node_modules/",
            "target/",
            "test-results/",
            "playwright-report/",
        ]
        existing_lines: List[str] = []
        if gitignore_path.exists():
            existing_lines = gitignore_path.read_text(encoding="utf-8").splitlines()
        existing_set = {line.strip() for line in existing_lines}
        for item in required_ignores:
            if item not in existing_set:
                existing_lines.append(item)
        gitignore_path.write_text("\n".join(existing_lines) + "\n", encoding="utf-8")
        written.append(str(gitignore_path))

        return written
