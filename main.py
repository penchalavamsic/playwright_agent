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
        }

        print(f"Starting Offline Playwright Agent for URL: {args.url}")
        res = asyncio.run(run_agent_pipeline(initial_state))
        print(f"\n[DONE] Generated {len(res.get('generated_files', []))} files under {args.output}")
        return 0

    # Desktop GUI Execution Path
    from gui.app_window import launch_desktop_gui
    launch_desktop_gui()
    return 0


if __name__ == "__main__":
    sys.exit(main())
