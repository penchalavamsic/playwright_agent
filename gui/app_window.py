"""Desktop test setup and results, with optional session settings and diagnostics."""

from __future__ import annotations

import asyncio
import datetime
import os
import queue
import sys
import threading
import webbrowser
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any, Dict, List, Optional

import customtkinter as ctk

from agents.state import AgentState
from agents.workflow_graph import run_agent_pipeline
from core.browser_inspector import BrowserInspector
from core.workspace_manager import DEFAULT_PROFILE_CHOICES, WorkspaceManager

# Configure CustomTkinter Theme & Styling
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")


def get_asset_path(relative_path: str) -> Path:
    """Resolve asset paths supporting standalone PyInstaller bundles."""
    base = getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent)
    return Path(base) / relative_path


# Visual Node Badge Color Constants
COLOR_PENDING = "#1E293B"       # Slate 800
COLOR_ACTIVE = "#2563EB"        # Blue 600
COLOR_COMPLETED = "#16A34A"     # Emerald 600
COLOR_ERROR = "#DC2626"         # Red 600
COLOR_BORDER = "#334155"        # Slate 700
COLOR_CARD_BG = "#0F172A"       # Slate 900
COLOR_ACCENT = "#38BDF8"        # Sky 400


class EnterpriseQAStudioApp(ctk.CTk):
    """Playwright Studio."""

    def __init__(self, is_test_mode: bool = False) -> None:
        super().__init__()

        self.is_test_mode = is_test_mode
        self.title("Playwright Studio")
        self.geometry("1320x860")
        self.minsize(1100, 720)

        # Thread-safe queue for UI streaming
        self.msg_queue: queue.Queue = queue.Queue()
        self._is_running: bool = False
        self._poll_job: Optional[str] = None
        self._cached_final_state: Optional[Dict[str, Any]] = None
        self._generated_files_map: Dict[str, str] = {}
        # Interactive Persistent Session state
        self._interactive_trigger_event: Optional[threading.Event] = None
        # Phase 6: Persistent Multi-Day Workspace & Credential Manager
        default_ws = Path("./output_workspace").resolve()
        self.workspace_manager: WorkspaceManager = WorkspaceManager(default_ws)

        self._build_ui()
        self._refresh_workspace_ui()
        self._start_queue_poller()
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

    def _on_window_close(self) -> None:
        """Ensure persistent browser is closed when app window terminates."""
        try:
            BrowserInspector.close_persistent_browser_sync()
        except Exception:
            pass
        if getattr(self, '_demo_server', None):
            self._demo_server.shutdown()
            self._demo_server.server_close()
        self.destroy()

    def _build_ui(self) -> None:
        # Split layout: 2 Columns (Sidebar 440px wide, Workspace flexible)
        self.grid_columnconfigure(0, weight=0, minsize=440)  # Left Sidebar
        self.grid_columnconfigure(1, weight=1)               # Right Main Workspace
        self.grid_rowconfigure(0, weight=1)

        self._build_left_sidebar()
        self._build_right_workspace()

    # -----------------------------------------------------------------------
    # LEFT SIDEBAR: User Inputs & Controls
    # -----------------------------------------------------------------------
    def _build_left_sidebar(self) -> None:
        sidebar = ctk.CTkFrame(self, width=440, corner_radius=16, fg_color="#111C30")
        sidebar.grid(row=0, column=0, padx=(18, 8), pady=18, sticky="nsew")
        sidebar.grid_propagate(False)
        header = ctk.CTkFrame(sidebar, fg_color="transparent")
        header.pack(fill="x", padx=22, pady=(20, 12))
        ctk.CTkLabel(header, text="Playwright Studio", font=ctk.CTkFont(size=24, weight="bold")).pack(anchor="w")
        ctk.CTkLabel(header, text="Set up a flow. Run it. Review the result.", text_color="#94A3B8").pack(anchor="w")
        links = ctk.CTkFrame(header, fg_color="transparent")
        links.pack(fill="x", pady=(12, 0))
        self.open_project_btn = ctk.CTkButton(links, text="Open project", width=130, height=30,
            fg_color="#26364F", command=self._open_existing_project)
        self.open_project_btn.pack(side="left")
        ctk.CTkButton(links, text="Try demo", width=110, height=30, fg_color="#26364F",
            command=self._load_demo_portal).pack(side="right")
        # Kept for workspace state; the internal sequence is not a main-screen input.
        self.seq_badge_lbl = ctk.CTkLabel(header, text="")
        form = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=16, pady=0)

        def label(parent, text):
            ctk.CTkLabel(parent, text=text, font=ctk.CTkFont(size=13, weight="bold")).pack(anchor="w", pady=(12, 4))

        label(form, "Application URL")
        self.url_entry = ctk.CTkEntry(form, height=38, placeholder_text="https://your-application.com")
        self.url_entry.pack(fill="x")
        label(form, "Login profile")
        profile_row = ctk.CTkFrame(form, fg_color="transparent")
        profile_row.pack(fill="x")
        self.profile_dropdown = ctk.CTkOptionMenu(profile_row, values=list(DEFAULT_PROFILE_CHOICES), height=34)
        self.profile_dropdown.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self.profile_dropdown.set("None (Public URL)")
        self.account_toggle = ctk.CTkButton(profile_row, text="Edit", width=60, height=34,
            fg_color="#26364F", command=self._toggle_account_editor)
        self.account_toggle.pack(side="right")
        account_slot = ctk.CTkFrame(form, fg_color="transparent", height=1)
        account_slot.pack(fill="x")
        self.account_editor = ctk.CTkFrame(account_slot, fg_color=COLOR_CARD_BG)
        label(self.account_editor, "Save a login profile")
        self.role_combo = ctk.CTkComboBox(self.account_editor, values=["QA", "ADMIN", "SUPER_USER"], height=32)
        self.role_combo.pack(fill="x", padx=10, pady=5)
        self.role_combo.set("QA")
        self.username_entry = ctk.CTkEntry(self.account_editor, placeholder_text="Username or email", height=32)
        self.username_entry.pack(fill="x", padx=10, pady=5)
        self.password_entry = ctk.CTkEntry(self.account_editor, placeholder_text="Password", show="*", height=32)
        self.password_entry.pack(fill="x", padx=10, pady=5)
        self.save_account_btn = ctk.CTkButton(self.account_editor, text="Save profile", command=self._on_save_role_account)
        self.save_account_btn.pack(fill="x", padx=10, pady=8)
        self.saved_roles_lbl = ctk.CTkLabel(self.account_editor, text="", wraplength=320)
        self.saved_roles_lbl.pack(fill="x", padx=10, pady=(0, 8))
        label(form, "Test flow")
        self.flow_text = ctk.CTkTextbox(form, height=132, font=ctk.CTkFont(size=13), wrap="word")
        self.flow_text.pack(fill="x")
        self.flow_text.insert("0.0", 'click "Reports"; verify "Reports"')
        ctk.CTkLabel(form, text='Use steps such as click "Save"; verify "Saved".', text_color="#94A3B8", font=ctk.CTkFont(size=11)).pack(anchor="w", pady=(4, 12))
        self.advanced_toggle = ctk.CTkButton(form, text="Advanced settings  +", anchor="w", height=34,
            fg_color="#26364F", command=self._toggle_advanced_settings)
        self.advanced_toggle.pack(fill="x", pady=(0, 8))
        self.advanced_panel = ctk.CTkFrame(form, fg_color="transparent")
        advanced = self.advanced_panel
        label(advanced, "Browser session")
        self.session_mode = ctk.CTkOptionMenu(advanced, values=['Fresh (incognito-like)', 'Saved profile (normal)'])
        self.session_mode.pack(fill="x", pady=4)
        ctk.CTkLabel(advanced, text="Fresh starts clean. Saved keeps this project's login.", text_color="#94A3B8", wraplength=340, justify="left").pack(anchor="w")
        label(advanced, "Confirm login with (optional)")
        self.auth_success_path = ctk.CTkEntry(advanced, placeholder_text="Authenticated path, e.g. /dashboard")
        self.auth_success_path.pack(fill="x", pady=4)
        self.auth_success_selector = ctk.CTkEntry(advanced, placeholder_text="Logged-in CSS selector")
        self.auth_success_selector.pack(fill="x", pady=4)
        self.switch_headless = ctk.CTkSwitch(advanced, text="Run browser in background")
        self.switch_headless.pack(anchor="w", pady=10)
        self.switch_headless.select()
        self.switch_interactive = ctk.CTkSwitch(advanced, text="Manual browser session", command=self._on_interactive_toggled)
        self.switch_interactive.pack(anchor="w", pady=6)
        label(advanced, "Generate scripts")
        languages = ctk.CTkFrame(advanced, fg_color="transparent")
        languages.pack(fill="x")
        for i, (attr, title) in enumerate((("chk_py", "Python"), ("chk_java", "Java"), ("chk_ts", "TypeScript"), ("chk_js", "JavaScript"))):
            checkbox = ctk.CTkCheckBox(languages, text=title, width=160)
            checkbox.grid(row=i//2, column=i%2, sticky="w", pady=7)
            setattr(self, attr, checkbox)
        self.chk_py.select()
        self.chk_scripts = ctk.CTkCheckBox(advanced, text="Include automation scripts")
        self.chk_scripts.pack(anchor="w", pady=(10, 6))
        self.chk_scripts.select()
        self.chk_plan = ctk.CTkCheckBox(advanced, text="Include test plan")
        self.chk_plan.pack(anchor="w", pady=6)
        self.chk_plan.select()
        label(advanced, "Save results to")
        self.out_entry = ctk.CTkEntry(advanced, height=32)
        self.out_entry.pack(fill="x", pady=4)
        self.out_entry.insert(0, str(Path("./output_workspace").resolve()))
        ctk.CTkButton(advanced, text="Choose folder", fg_color="#26364F", command=self._browse_output_dir).pack(anchor="w", pady=(4, 12))

        actions = ctk.CTkFrame(sidebar, fg_color="transparent")
        actions.pack(fill="x", padx=22, pady=(12, 20))
        self.run_btn = ctk.CTkButton(actions, text="Run test", height=44, font=ctk.CTkFont(size=15, weight="bold"), command=self._on_start_clicked)
        self.run_btn.pack(fill="x", pady=(0, 8))
        self.capture_btn = ctk.CTkButton(actions, text="Capture and generate", height=38, command=self._on_capture_clicked)
        self.close_browser_btn = ctk.CTkButton(actions, text="Close browser", fg_color="#26364F", command=self._on_close_browser_clicked)
        self.open_folder_btn = ctk.CTkButton(actions, text="Open results folder", height=32, fg_color="#26364F", state="disabled", command=self._open_output_folder)
        self.open_folder_btn.pack(fill="x")

    def _toggle_advanced_settings(self) -> None:
        if self.advanced_panel.winfo_manager():
            self.advanced_panel.pack_forget()
            self.advanced_toggle.configure(text="Advanced settings  +")
        else:
            self.advanced_panel.pack(fill="x", pady=(0, 12))
            self.advanced_toggle.configure(text="Advanced settings  −")

    def _toggle_account_editor(self) -> None:
        if self.account_editor.winfo_manager():
            self.account_editor.pack_forget()
            self.account_editor.master.configure(height=1)
            self.account_toggle.configure(text="Edit")
        else:
            self.account_editor.pack(fill="x", pady=(8, 0))
            self.account_toggle.configure(text="Done")

    def _build_right_workspace(self) -> None:
        workspace = ctk.CTkFrame(self, corner_radius=16, fg_color="#111C30")
        workspace.grid(row=0, column=1, padx=(8, 18), pady=18, sticky="nsew")
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_rowconfigure(2, weight=1)
        heading = ctk.CTkFrame(workspace, fg_color="transparent")
        heading.grid(row=0, column=0, sticky="ew", padx=24, pady=(22, 12))
        ctk.CTkLabel(heading, text="Test results", font=ctk.CTkFont(size=23, weight="bold")).pack(side="left")
        self.open_report_btn = ctk.CTkButton(heading, text="Open full report", width=140, height=32,
            state="disabled", command=self._open_test_report)
        self.open_report_btn.pack(side="right")
        progress = ctk.CTkFrame(workspace, fg_color="transparent")
        progress.grid(row=1, column=0, sticky="ew", padx=24, pady=(0, 12))
        progress.grid_columnconfigure(0, weight=1)
        self.status_banner_lbl = ctk.CTkLabel(progress, text="Ready to run", anchor="w", font=ctk.CTkFont(size=14, weight="bold"))
        self.status_banner_lbl.grid(row=0, column=0, sticky="ew", pady=(0, 8))
        self.pct_display_lbl = ctk.CTkLabel(progress, text="0%", width=44, text_color=COLOR_ACCENT)
        self.pct_display_lbl.grid(row=0, column=1)
        self.progress_bar = ctk.CTkProgressBar(progress, height=6)
        self.progress_bar.grid(row=1, column=0, columnspan=2, sticky="ew")
        self.progress_bar.set(0)
        self.tabs = ctk.CTkTabview(workspace, corner_radius=10)
        self.tabs.grid(row=2, column=0, sticky="nsew", padx=20, pady=(0, 20))
        result_tab = self.tabs.add("Results")
        tab_console = self.tabs.add("Details")
        tab_plan = self.tabs.add("Test plan")
        tab_files = self.tabs.add("Files")
        for tab in (result_tab, tab_console, tab_plan, tab_files):
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(1, weight=1)
        self.results_textbox = ctk.CTkTextbox(result_tab, wrap="word", font=ctk.CTkFont(size=15), fg_color=COLOR_CARD_BG)
        self.results_textbox.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        self._show_result_text("Your next test starts here.\n\nEnter the application URL, choose a login profile if needed, and describe the steps to check.\n\nAfter the run, you'll see which steps passed and where the flow stopped.")
        counters = ctk.CTkFrame(tab_console, fg_color="transparent")
        counters.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        for attr, text in (("counter_dom_lbl", "Locators: 0"), ("counter_api_lbl", "APIs: 0"), ("counter_files_lbl", "Files: 0")):
            widget = ctk.CTkLabel(counters, text=text, font=ctk.CTkFont(size=11), text_color="#94A3B8")
            widget.pack(side="left", padx=(0, 20))
            setattr(self, attr, widget)
        self.node_cards = {}
        self.console_textbox = ctk.CTkTextbox(tab_console, wrap="word", font=ctk.CTkFont(family="Consolas", size=12))
        self.console_textbox.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        self.plan_textbox = ctk.CTkTextbox(tab_plan, wrap="word", font=ctk.CTkFont(size=13))
        self.plan_textbox.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)
        self.plan_textbox.insert("0.0", "Your test plan will appear after the run.")
        self.file_selector = ctk.CTkOptionMenu(tab_files, values=["No files generated yet"], command=self._on_file_selected)
        self.file_selector.grid(row=0, column=0, sticky="ew", padx=6, pady=6)
        self.code_preview_textbox = ctk.CTkTextbox(tab_files, wrap="none", font=ctk.CTkFont(family="Consolas", size=12))
        self.code_preview_textbox.grid(row=1, column=0, sticky="nsew", padx=6, pady=6)

    def _show_result_text(self, text: str) -> None:
        self.results_textbox.configure(state="normal")
        self.results_textbox.delete("0.0", "end")
        self.results_textbox.insert("0.0", text)
        self.results_textbox.configure(state="disabled")

    # -----------------------------------------------------------------------
    # Interactive Session Mode Helpers
    # -----------------------------------------------------------------------
    def _on_interactive_toggled(self) -> None:
        """Adjust UI button labels when interactive mode is switched."""
        is_interactive = bool(self.switch_interactive.get())
        if is_interactive:
            self.close_browser_btn.pack(fill="x", pady=6)
            self.switch_headless.deselect()  # Browser must be visible
            if not self._is_running:
                self.run_btn.configure(text="Open browser", fg_color="#D97706", hover_color="#B45309")
        else:
            self.close_browser_btn.pack_forget()
            if not self._is_running:
                self.run_btn.configure(text="Run test", fg_color="#2563EB", hover_color="#1D4ED8")
            self.capture_btn.pack_forget()

    def _on_capture_clicked(self) -> None:
        """Triggered by user in Step B to capture live state and generate suites."""
        if self._interactive_trigger_event:
            self._interactive_trigger_event.set()
            self.capture_btn.configure(state="disabled", text="Capturing…")
            self.status_banner_lbl.configure(text="Capture trigger received. Capturing active page DOM and generating suite...")
    def _set_node_state(self, node_id: str, state: str) -> None:
        """Update visual badge state: pending | running | completed | error."""
        card_info = self.node_cards.get(node_id)
        if not card_info:
            return

        card_info["state"] = state
        card: ctk.CTkFrame = card_info["card"]
        status_l: ctk.CTkLabel = card_info["status_label"]

        if state == "running":
            card.configure(fg_color=COLOR_ACTIVE, border_color="#60A5FA")
            status_l.configure(text="⏳ Running...", text_color="#FFFFFF")
        elif state == "completed":
            card.configure(fg_color=COLOR_COMPLETED, border_color="#4ADE80")
            status_l.configure(text="✔ Done", text_color="#FFFFFF")
        elif state == "error":
            card.configure(fg_color=COLOR_ERROR, border_color="#F87171")
            status_l.configure(text="✖ Error", text_color="#FFFFFF")
        else:
            card.configure(fg_color=COLOR_PENDING, border_color=COLOR_BORDER)
            status_l.configure(text="○ Pending", text_color="#94A3B8")

    def _reset_pipeline_cards(self) -> None:
        for node_id in self.node_cards:
            self._set_node_state(node_id, "pending")

    # -----------------------------------------------------------------------
    # Thread-Safe Queue Polling
    # -----------------------------------------------------------------------
    def _start_queue_poller(self) -> None:
        self._poll_queue()

    def _poll_queue(self) -> None:
        try:
            while True:
                msg = self.msg_queue.get_nowait()
                msg_type = msg.get("type")

                if msg_type == "progress":
                    self._handle_progress_event(msg)
                elif msg_type == "complete":
                    self._handle_complete_event(msg)
                elif msg_type == "error":
                    self._handle_error_event(msg)

                self.msg_queue.task_done()
        except queue.Empty:
            pass
        finally:
            self._poll_job = self.after(80, self._poll_queue)

    def _handle_progress_event(self, msg: Dict[str, Any]) -> None:
        node_name = msg.get("node_name", "")
        percent = float(msg.get("percent", 0.0))
        message = msg.get("message", "")
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")

        # Normalize progress (0.0 to 1.0)
        norm_val = percent if percent <= 1.0 else (percent / 100.0)
        norm_val = max(0.0, min(1.0, norm_val))
        pct_int = int(norm_val * 100)

        self.progress_bar.set(norm_val)
        self.pct_display_lbl.configure(text=f"{pct_int}%")
        stage = {"intentparser": "Preparing the flow", "browserinspector": "Running your flow", "testplanner": "Preparing the test plan", "codesynthesizer": "Generating scripts", "projectscaffolder": "Saving results"}
        self.status_banner_lbl.configure(text=next((value for key, value in stage.items() if key in node_name.lower()), "Working…"))

        # Stream into Console Log
        log_entry = f"[{timestamp}] [{pct_int:3d}%] [{node_name:<24}] {message}\n"
        self.console_textbox.insert("end", log_entry)
        self.console_textbox.see("end")

        # Map active node highlighting
        lower_node = node_name.lower()
        if "intentparser" in lower_node:
            self._set_node_state("intent_parser", "running")
        elif "browserinspector" in lower_node:
            self._set_node_state("intent_parser", "completed")
            self._set_node_state("browser_inspector", "running")
        elif "testplanner" in lower_node:
            self._set_node_state("browser_inspector", "completed")
            self._set_node_state("test_planner", "running")
        elif "codesynthesizer" in lower_node:
            self._set_node_state("test_planner", "completed")
            self._set_node_state("code_synthesizer", "running")
        elif "projectscaffolder" in lower_node:
            self._set_node_state("code_synthesizer", "completed")
            self._set_node_state("project_scaffolder", "running")

    def _handle_complete_event(self, msg: Dict[str, Any]) -> None:
        final_state = msg.get("state", {})
        self._cached_final_state = final_state
        self._is_running = False

        # Mark all node cards as completed
        for node_id in self.node_cards:
            self._set_node_state(node_id, "completed")

        self.progress_bar.set(1.0)
        self.pct_display_lbl.configure(text="100%")
        execution_status = final_state.get('inspection_report', {}).get('execution_status', 'not_run')
        self.status_banner_lbl.configure(text=f"Flow {execution_status.upper().replace('_', ' ')}", text_color="#F87171" if execution_status == "failed" else "#E2E8F0")
        report = final_state.get("inspection_report", {})
        lines = [f"Flow {execution_status.upper().replace('_', ' ')}", ""]
        for index, step in enumerate(report.get("execution_steps", []), 1):
            label = step.get('description') or f"{step.get('action_type', 'Step').replace('_', ' ').title()} {step.get('target_keyword', '')}"
            lines.append(f"{index}. {label.strip()}  —  {step.get('status', 'not_run').upper()}")
            if step.get("error"):
                lines.append(f"   {step['error']}")
            lines.append("")
        if not report.get("execution_steps"):
            lines.append("No automated steps were executed.")
        self._show_result_text("\n".join(lines))
        self.tabs.set("Results")
        if execution_status == 'failed':
            self._set_node_state('browser_inspector', 'error')
        
        # Reset Action Buttons
        is_interactive = bool(self.switch_interactive.get())
        if is_interactive:
            self.run_btn.configure(state="normal", text="Open browser", fg_color="#D97706", hover_color="#B45309")
        else:
            self.run_btn.configure(state="normal", text="Run test", fg_color="#2563EB", hover_color="#1D4ED8")
        self.capture_btn.pack_forget()

        self.open_folder_btn.configure(state="normal", fg_color=COLOR_COMPLETED, hover_color="#15803D")
        self.open_report_btn.configure(state="normal", fg_color="#0284C7", hover_color="#0369A1")

        # Update Live Counters
        report = final_state.get("inspection_report", {})
        dom_count = len(report.get("elements", []))
        api_count = len(report.get("captured_apis", []))
        file_count = len(final_state.get("generated_files", []))

        self.counter_dom_lbl.configure(text=f"DOM Locators: {dom_count}", text_color="#38BDF8")
        self.counter_api_lbl.configure(text=f"APIs Intercepted: {api_count}", text_color="#38BDF8")
        self.counter_files_lbl.configure(text=f"Files Generated: {file_count}", text_color="#4ADE80")

        # Populate Tab 2: Test Plan Markdown
        plan_md = final_state.get("test_plan_markdown", "")
        if plan_md:
            self.plan_textbox.delete("0.0", "end")
            self.plan_textbox.insert("0.0", plan_md)

        # Populate Tab 3: Generated Files Previewer
        created_files = final_state.get("generated_files", [])
        if created_files:
            self._populate_file_previewer(created_files)

        # Refresh workspace state & Next Test ID badge after run
        out_dir = final_state.get("output_dir") or self.out_entry.get().strip()
        if out_dir:
            self._last_run_output_dir = out_dir
            self.out_entry.delete(0, 'end')
            self.out_entry.insert(0, out_dir)
            self.workspace_manager = WorkspaceManager.load_project_state(out_dir)
            self._refresh_workspace_ui()

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.console_textbox.insert(
            "end",
            f"\n[{timestamp}] [100%] Generated {file_count} assets. Flow: {execution_status.upper()}.\n" + '\n'.join(final_state.get('errors', [])) + '\n',
        )
        self.console_textbox.see("end")


    def _handle_error_event(self, msg: Dict[str, Any]) -> None:
        err = msg.get("error", "Unknown error")
        self._is_running = False

        # Mark active card as error
        for node_id, card_info in self.node_cards.items():
            if card_info["state"] == "running":
                self._set_node_state(node_id, "error")

        is_interactive = bool(self.switch_interactive.get())
        if is_interactive:
            self.run_btn.configure(state="normal", text="Open browser", fg_color="#D97706", hover_color="#B45309")
        else:
            self.run_btn.configure(state="normal", text="Run test", fg_color="#2563EB", hover_color="#1D4ED8")
        self.capture_btn.pack_forget()
        self.status_banner_lbl.configure(text="Run failed", text_color="#F87171")
        self._show_result_text("Run failed\n\n" + err)
        self.tabs.set("Results")
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.console_textbox.insert("end", f"\n[{timestamp}] [ERROR] Pipeline failed: {err}\n")
        self.console_textbox.see("end")

        if not self.is_test_mode:
            messagebox.showerror("Pipeline Execution Failure", f"An error occurred during execution:\n\n{err}")

    # -----------------------------------------------------------------------
    # File Previewer Helper
    # -----------------------------------------------------------------------
    def _populate_file_previewer(self, files: List[str]) -> None:
        self._generated_files_map.clear()
        options: List[str] = []

        out_root = Path(self.out_entry.get().strip()).resolve()

        for f in files:
            p = Path(f).resolve()
            if p.exists() and p.is_file():
                try:
                    rel_name = str(p.relative_to(out_root))
                except ValueError:
                    rel_name = p.name
                options.append(rel_name)
                self._generated_files_map[rel_name] = str(p)

        if options:
            options.sort()
            self.file_selector.configure(values=options)
            self.file_selector.set(options[0])
            self._on_file_selected(options[0])

    def _on_file_selected(self, chosen_label: str) -> None:
        full_path = self._generated_files_map.get(chosen_label)
        if full_path and os.path.exists(full_path):
            try:
                content = Path(full_path).read_text(encoding="utf-8")
                self.code_preview_textbox.delete("0.0", "end")
                self.code_preview_textbox.insert("0.0", content)
            except Exception as e:
                self.code_preview_textbox.delete("0.0", "end")
                self.code_preview_textbox.insert("0.0", f"// Error reading file: {e}\n")

    # -----------------------------------------------------------------------
    # UI Control Callbacks
    # -----------------------------------------------------------------------
    def _load_demo_portal(self) -> None:
        """Start a real disposable localhost portal and configure a reproducible flow."""
        from core.demo_portal import make_server, DEMO_FLOW
        if not getattr(self, '_demo_server', None):
            self._demo_server = make_server()
            threading.Thread(target=self._demo_server.serve_forever, daemon=True).start()
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, f"http://127.0.0.1:{self._demo_server.server_port}")
        self.flow_text.delete('0.0', 'end')
        self.flow_text.insert('0.0', DEMO_FLOW)
        self.workspace_manager.add_or_update_account('QA', 'qa@example.test', 'local-demo-only')
        self._refresh_workspace_ui()
        self.profile_dropdown.set('QA')
        self.session_mode.set('Fresh (incognito-like)')
        self.auth_success_path.delete(0, 'end')
        self.auth_success_selector.delete(0, 'end')

    def _toggle_all_languages(self) -> None:
        all_selected = (
            self.chk_py.get() == 1
            and self.chk_java.get() == 1
            and self.chk_ts.get() == 1
            and self.chk_js.get() == 1
        )
        if all_selected:
            self.chk_py.deselect()
            self.chk_java.deselect()
            self.chk_ts.deselect()
            self.chk_js.deselect()
        else:
            self.chk_py.select()
            self.chk_java.select()
            self.chk_ts.select()
            self.chk_js.select()

    def _browse_output_dir(self) -> None:
        chosen = filedialog.askdirectory(initialdir=self.out_entry.get().strip() or ".")
        if chosen:
            norm_path = os.path.normpath(chosen)
            self.out_entry.delete(0, "end")
            self.out_entry.insert(0, norm_path)
            # Load existing workspace if present, otherwise point workspace_manager to new dir
            if (Path(norm_path) / WorkspaceManager.PROJECT_FILE).exists():
                self.load_workspace(norm_path)
            else:
                old_accounts = dict(self.workspace_manager.state.get("accounts", {}))
                self.workspace_manager = WorkspaceManager(norm_path)
                if old_accounts and not self.workspace_manager.state.get("accounts"):
                    self.workspace_manager.state["accounts"] = old_accounts
                self._refresh_workspace_ui()

    def _open_existing_project(self) -> None:
        chosen = filedialog.askdirectory(initialdir=self.out_entry.get().strip() or ".")
        if chosen:
            self.load_workspace(chosen)

    def load_workspace(self, folder_path: str | Path) -> None:
        """Load an existing multi-day project workspace into the GUI."""
        norm_path = os.path.normpath(str(folder_path))
        self._last_run_output_dir = norm_path
        self.workspace_manager = WorkspaceManager.load_project_state(norm_path)

        self.out_entry.delete(0, "end")
        self.out_entry.insert(0, norm_path)

        saved_url = self.workspace_manager.state.get("target_url", "")
        settings = self.workspace_manager.state.get('browser_settings', {})
        self.session_mode.set('Saved profile (normal)' if settings.get('session_mode') == 'persistent' else 'Fresh (incognito-like)')
        for field in ('auth_success_path', 'auth_success_selector'):
            widget = getattr(self, field)
            widget.delete(0, 'end')
            widget.insert(0, settings.get(field, ''))
        if saved_url:
            self.url_entry.delete(0, "end")
            self.url_entry.insert(0, saved_url)

        saved_langs = self.workspace_manager.state.get("target_languages", [])
        if saved_langs:
            for chk, lang in [
                (self.chk_py, "Python"),
                (self.chk_java, "Java"),
                (self.chk_ts, "TypeScript"),
                (self.chk_js, "JavaScript"),
            ]:
                if lang in saved_langs:
                    chk.select()
                else:
                    chk.deselect()

        self._refresh_workspace_ui()
        if hasattr(self, "console_textbox"):
            self.console_textbox.insert(
                "end",
                f"[WORKSPACE LOADED] {norm_path} | Next Test ID: {self.workspace_manager.next_sequence_number():03d}\n",
            )
            self.console_textbox.see("end")

    def _on_save_role_account(self) -> None:
        """Save or update a role account in the local workspace vault & .env."""
        role = self.role_combo.get().strip()
        username = self.username_entry.get().strip()
        password = self.password_entry.get()

        if not role:
            if not self.is_test_mode:
                messagebox.showerror("Validation Error", "Please enter or select a Role name.")
            return
        if not username or not password:
            if not self.is_test_mode:
                messagebox.showerror("Validation Error", "Please provide both Username and Password.")
            return

        out_dir = self.out_entry.get().strip() or "./output_workspace"
        if Path(out_dir).resolve() != self.workspace_manager.project_root:
            old_accounts = dict(self.workspace_manager.state.get("accounts", {}))
            self.workspace_manager = WorkspaceManager(out_dir)
            for k, v in old_accounts.items():
                self.workspace_manager.state.setdefault("accounts", {})[k] = v

        norm_role = self.workspace_manager.add_or_update_account(role, username, password)
        # Only persist immediately to disk if an existing project workspace is loaded;
        # new runs create `<output_dir>/<domain>_<timestamp>/` on execution.
        if self.workspace_manager.exists():
            self.workspace_manager.write_env_and_profiles(
                active_role=norm_role,
                target_url=self.url_entry.get().strip(),
            )
            self.workspace_manager.save_project_state()

        self.password_entry.delete(0, "end")
        self._refresh_workspace_ui()
        self.profile_dropdown.set(norm_role)

        if hasattr(self, "console_textbox"):
            self.console_textbox.insert("end", f"[VAULT] Saved role account '{norm_role}' to .env & workspace.\n")
            self.console_textbox.see("end")

    def _refresh_workspace_ui(self) -> None:
        """Update Next Test ID badge, saved roles status, and profile dropdown options."""
        next_seq = self.workspace_manager.next_sequence_number()
        self.seq_badge_lbl.configure(text=f"Next Test ID: {next_seq:03d}")

        saved_roles = self.workspace_manager.get_saved_roles()
        if saved_roles:
            self.saved_roles_lbl.configure(text=f"Saved Roles: {', '.join(saved_roles)}", text_color="#4ADE80")
        else:
            self.saved_roles_lbl.configure(text="Saved Roles: None", text_color="#94A3B8")

        options = list(DEFAULT_PROFILE_CHOICES)
        for r in saved_roles:
            if r not in options:
                options.append(r)
        current = self.profile_dropdown.get()
        self.profile_dropdown.configure(values=options)
        if current in options:
            self.profile_dropdown.set(current)
        else:
            self.profile_dropdown.set(options[0])

    def _on_close_browser_clicked(self) -> None:
        """User clicked close persistent browser."""
        BrowserInspector.close_persistent_browser_sync()
        self.console_textbox.insert("end", "[INFO] Persistent browser session closed.\n")
        self.console_textbox.see("end")

    def _open_output_folder(self) -> None:
        target = getattr(self, "_last_run_output_dir", "") or self.out_entry.get().strip()
        if os.path.exists(target):
            os.startfile(target)
        else:
            messagebox.showwarning("Directory Not Found", f"Output folder does not exist yet:\n{target}")

    def _open_test_report(self) -> None:
        """Launch <project_root>/Complete-Suite-Test-Report/index.html in the default browser."""
        base_target = getattr(self, "_last_run_output_dir", "") or self.out_entry.get().strip() or "./output_workspace"
        target = Path(base_target).resolve()
        report_html = target / "Complete-Suite-Test-Report" / "index.html"
        if not report_html.exists():
            if not self.is_test_mode:
                messagebox.showwarning("Report Not Found", f"No report for this project yet:\n{report_html}")
            return
        try:
            os.startfile(str(report_html))
        except Exception:
            webbrowser.open(report_html.as_uri())

    def _on_start_clicked(self) -> None:
        if self._is_running:
            return

        target_url = self.url_entry.get().strip()
        flow_prompt = self.flow_text.get("0.0", "end").strip()
        output_dir = self.out_entry.get().strip()

        if not target_url:
            messagebox.showerror("Validation Error", "Please provide a valid Target URL.")
            return

        if not flow_prompt:
            messagebox.showerror("Test flow required", "Enter the steps you want to check.")
            return

        selected_langs: List[str] = []
        if self.chk_py.get():
            selected_langs.append("Python")
        if self.chk_java.get():
            selected_langs.append("Java")
        if self.chk_ts.get():
            selected_langs.append("TypeScript")
        if self.chk_js.get():
            selected_langs.append("JavaScript")

        if not selected_langs and self.chk_scripts.get():
            messagebox.showerror("Validation Error", "Please select at least one Target Language.")
            return

        # Prepare UI
        self._is_running = True
        is_interactive = bool(self.switch_interactive.get())

        if is_interactive:
            self._interactive_trigger_event = threading.Event()
            self.run_btn.configure(state="disabled", text="Browser is open…")
            # Reveal Step B capture button prominently
            self.capture_btn.pack(fill="x", pady=(0, 8), before=self.open_folder_btn)
            self.capture_btn.configure(state="normal", text="Capture and generate")
        else:
            self._interactive_trigger_event = None
            self.run_btn.configure(state="disabled", text="Running test…")
            self.capture_btn.pack_forget()

        self.open_folder_btn.configure(state="disabled", fg_color="#334155")
        self.open_report_btn.configure(state="disabled")
        self.console_textbox.delete("0.0", "end")
        self.progress_bar.set(0.0)
        self.pct_display_lbl.configure(text="0%")
        self.status_banner_lbl.configure(text_color="#E2E8F0")
        self._show_result_text("Running your flow…\n\nStep results will appear here when the run finishes.")
        self.tabs.set("Results")
        self.status_banner_lbl.configure(
            text="Opening browser…" if is_interactive else "Starting test…"
        )
        self._reset_pipeline_cards()

        # Sync workspace manager with selected output_dir while preserving unsaved in-memory accounts
        if Path(output_dir).resolve() != self.workspace_manager.project_root:
            in_mem_accounts = dict(self.workspace_manager.state.get("accounts", {}))
            self.workspace_manager = WorkspaceManager(output_dir)
            for k, v in in_mem_accounts.items():
                self.workspace_manager.state.setdefault("accounts", {})[k] = v

        active_profile = self.profile_dropdown.get()
        decrypted_accounts = self.workspace_manager.get_all_decrypted_accounts()
        next_seq = self.workspace_manager.next_sequence_number()

        initial_state: AgentState = {
            "target_url": target_url,
            "user_flow_text": flow_prompt,
            "target_languages": selected_langs,
            "output_dir": output_dir,
            "headless": False if is_interactive else bool(self.switch_headless.get()),
            "generate_test_plan": bool(self.chk_plan.get()),
            "generate_scripts": bool(self.chk_scripts.get()),
            "interactive_mode": is_interactive,
            "browser_settings": dict(self.workspace_manager.state.get('browser_settings', {}),
                                     session_mode='persistent' if self.session_mode.get().startswith('Saved') else 'fresh',
                                     auth_success_path=self.auth_success_path.get().strip(),
                                     auth_success_selector=self.auth_success_selector.get().strip()),
            "capture_trigger_event": self._interactive_trigger_event,
            "progress_callback": self._enqueue_progress,
            "active_access_profile": active_profile,
            "account_credentials": decrypted_accounts,
            "sequence_number": next_seq,
            "parsed_flow_steps": [],
            "inspection_report": {},
            "test_plan_markdown": "",
            "test_scenarios": [],
            "generated_files": [],
            "errors": [],
        }

        # Background thread execution
        worker = threading.Thread(
            target=self._run_background_pipeline,
            args=(initial_state,),
            daemon=True,
        )
        worker.start()

    def _enqueue_progress(self, node_name: str, percent: float, message: str) -> None:
        """Called by LangGraph nodes; thread-safe queue insertion."""
        self.msg_queue.put({
            "type": "progress",
            "node_name": node_name,
            "percent": percent,
            "message": message,
        })

    def _run_background_pipeline(self, initial_state: AgentState) -> None:
        """Executes within background daemon thread."""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            final_state = loop.run_until_complete(run_agent_pipeline(initial_state))
            loop.close()

            self.msg_queue.put({
                "type": "complete",
                "state": final_state,
            })
        except Exception as exc:
            self.msg_queue.put({
                "type": "error",
                "error": str(exc),
            })


def launch_desktop_gui() -> None:
    """Launch the Enterprise QA Agent Studio desktop application."""
    app = EnterpriseQAStudioApp()
    app.mainloop()


if __name__ == "__main__":
    launch_desktop_gui()
