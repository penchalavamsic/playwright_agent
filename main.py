"""Main desktop application entry point for Playwright Enterprise QA Agent Studio.

Configures Windows DPI scaling, global exception catching, and starts the CustomTkinter GUI.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

# High-DPI Windows awareness
if sys.platform == "win32":
    try:
        import ctypes
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
    except Exception:
        pass


def global_exception_handler(exctype, value, tb) -> None:
    """Safely log unhandled exceptions without crashing silently."""
    import traceback
    err_str = "".join(traceback.format_exception(exctype, value, tb))
    sys.stderr.write(f"\n[CRITICAL UNHANDLED EXCEPTION]:\n{err_str}\n")


sys.excepthook = global_exception_handler


def main() -> int:
    parser = argparse.ArgumentParser(description="Playwright Enterprise QA Agent Studio (100% Offline Zero-API)")
    parser.add_argument("--cli", action="store_true", help="Run in headless CLI mode instead of GUI")
    parser.add_argument("--url", help="Target URL or web application")
    parser.add_argument("--flow", help="Natural language user flow prompt")
    parser.add_argument("--output", default="./output_workspace", help="Output directory path")
    parser.add_argument("--langs", nargs="+", default=["Python", "Java", "TypeScript", "JavaScript"], help="Target languages")
    parser.add_argument("--headed", action="store_true", help="Run browser in visible mode")
    parser.add_argument("--profile", default="", help="Saved role profile in an existing project")
    parser.add_argument('--session-mode', choices=['fresh', 'persistent'], help='Fresh incognito-like context or a dedicated saved browser profile')
    parser.add_argument('--auth-success-path', help='Authenticated URL path, for example /dashboard')
    parser.add_argument('--auth-success-selector', help='CSS selector visible only when authenticated')
    parser.add_argument('--auth-timeout', type=float, help='Login timeout in seconds (default 15)')
    parser.add_argument('--auth-settle', type=float, help='Stable authenticated window in seconds (default 2.5)')

    args = parser.parse_args()

    # CLI Execution Path
    if args.cli or args.url:
        from agents.state import AgentState
        from agents.workflow_graph import run_agent_pipeline

        if not args.url:
            print("Error: --url is required when running in CLI mode.", file=sys.stderr)
            return 1

        def cli_progress(node: str, pct: float, msg: str) -> None:
            pct_val = pct * 100 if pct <= 1.0 else pct
            print(f"[{pct_val:5.1f}%] [{node:<24}] {msg}", flush=True)

        from core.workspace_manager import WorkspaceManager
        workspace = WorkspaceManager(args.output)
        browser_settings = dict(workspace.state.get('browser_settings', {}))
        for key in ('session_mode', 'auth_success_path', 'auth_success_selector'):
            if getattr(args, key) is not None:
                browser_settings[key] = getattr(args, key)
        for key in ('auth_timeout', 'auth_settle'):
            if getattr(args, key) is not None:
                browser_settings[key + '_ms'] = int(getattr(args, key) * 1000)
        initial_state: AgentState = {
            "target_url": args.url,
            "user_flow_text": args.flow or "Explore application and generate automation suite",
            "target_languages": args.langs,
            "output_dir": str(Path(args.output).resolve()),
            "headless": not args.headed,
            "generate_test_plan": True,
            "generate_scripts": True,
            "progress_callback": cli_progress,
            "parsed_flow_steps": [],
            "inspection_report": {},
            "test_plan_markdown": "",
            "test_scenarios": [],
            "generated_files": [],
            "errors": [],
            "active_access_profile": args.profile,
            "account_credentials": workspace.get_all_decrypted_accounts(),
            "browser_settings": browser_settings,
        }

        print(f"Starting Offline Playwright Agent for URL: {args.url}")
        res = asyncio.run(run_agent_pipeline(initial_state))
        print(f"\n[DONE] Generated {len(res.get('generated_files', []))} files under {res.get('output_dir', args.output)}")
        status = res.get('inspection_report', {}).get('execution_status', 'not_run')
        print(f"Flow execution: {status}")
        for error in res.get('errors', []):
            print(error, file=sys.stderr)
        return 0 if status == 'passed' and not res.get('errors') else 1

    # Desktop GUI Execution Path
    from gui.app_window import launch_desktop_gui
    launch_desktop_gui()
    return 0


if __name__ == "__main__":
    sys.exit(main())
