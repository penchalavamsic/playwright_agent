"""Enterprise QA Agent Studio Desktop GUI Window (Phase 4).

100% Offline, Zero-API CustomTkinter Desktop Interface with thread-safe queue polling,
5-Node visual pipeline state badges, live telemetry counters, clean non-overlapping layout,
and multi-tab output inspector.
"""

from __future__ import annotations

import asyncio
import datetime
import os
import queue
import sys
import threading
from pathlib import Path
from tkinter import filedialog, messagebox
from typing import Any, Dict, List, Optional

import customtkinter as ctk

from agents.state import AgentState
from agents.workflow_graph import run_agent_pipeline
from core.browser_inspector import BrowserInspector

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
    """Playwright Enterprise QA Agent Studio (Zero-API Offline Edition)."""

    def __init__(self, is_test_mode: bool = False) -> None:
        super().__init__()

        self.is_test_mode = is_test_mode
        self.title("Playwright Enterprise QA Agent Studio (Zero-API Offline Edition)")
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

        self._build_ui()
        self._start_queue_poller()
        self.protocol("WM_DELETE_WINDOW", self._on_window_close)

    def _on_window_close(self) -> None:
        """Ensure persistent browser is closed when app window terminates."""
        try:
            BrowserInspector.close_persistent_browser_sync()
        except Exception:
            pass
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
        sidebar = ctk.CTkFrame(self, width=440, corner_radius=12)
        sidebar.grid(row=0, column=0, padx=(15, 8), pady=15, sticky="nsew")
        sidebar.grid_propagate(False)

        # Header Title
        title_box = ctk.CTkFrame(sidebar, fg_color="transparent")
        title_box.pack(fill="x", padx=16, pady=(16, 8))

        title_lbl = ctk.CTkLabel(
            title_box,
            text="Autonomous QA Studio",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title_lbl.pack(anchor="w")

        sub_lbl = ctk.CTkLabel(
            title_box,
            text="100% Offline Zero-API Playwright Synthesizer",
            font=ctk.CTkFont(size=12),
            text_color="#94A3B8",
        )
        sub_lbl.pack(anchor="w")

        # Scrollable form container for clean vertical pacing
        form = ctk.CTkScrollableFrame(sidebar, fg_color="transparent")
        form.pack(fill="both", expand=True, padx=8, pady=(0, 6))

        # -------------------------------------------------------------------
        # SECTION 1: Target & Flow
        # -------------------------------------------------------------------
        sec1_header = ctk.CTkFrame(form, fg_color="transparent")
        sec1_header.pack(fill="x", pady=(4, 6))
        ctk.CTkLabel(
            sec1_header,
            text="1. Target Application & Flow",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLOR_ACCENT,
        ).pack(side="left")

        demo_btn = ctk.CTkButton(
            sec1_header,
            text="⚡ Load Demo Portal",
            width=135,
            height=24,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#334155",
            hover_color="#475569",
            command=self._load_demo_portal,
        )
        demo_btn.pack(side="right")

        sec1_card = ctk.CTkFrame(form, fg_color=COLOR_CARD_BG, corner_radius=8, border_color=COLOR_BORDER, border_width=1)
        sec1_card.pack(fill="x", pady=(0, 14), padx=2, ipady=8)

        ctk.CTkLabel(sec1_card, text="Target URL:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=14, pady=(8, 2))
        self.url_entry = ctk.CTkEntry(
            sec1_card,
            placeholder_text="http://localhost:3000 or https://example.com",
            height=34,
        )
        self.url_entry.pack(fill="x", padx=14, pady=(0, 10))
        self.url_entry.insert(0, "http://localhost:3000")

        ctk.CTkLabel(sec1_card, text="Flow / Scenario Description:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=14, pady=(0, 2))
        self.flow_text = ctk.CTkTextbox(sec1_card, height=100, font=ctk.CTkFont(size=12))
        self.flow_text.pack(fill="x", padx=14, pady=(0, 6))
        self.flow_text.insert(
            "0.0",
            "Create automation script for the dashboard, search API, click button and verify whether it succeeded with 200 or 201 status code",
        )

        # -------------------------------------------------------------------
        # SECTION 2: Languages & Scope
        # -------------------------------------------------------------------
        sec2_header = ctk.CTkFrame(form, fg_color="transparent")
        sec2_header.pack(fill="x", pady=(4, 6))
        ctk.CTkLabel(
            sec2_header,
            text="2. Languages & Deliverables Scope",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLOR_ACCENT,
        ).pack(side="left")

        toggle_all_btn = ctk.CTkButton(
            sec2_header,
            text="Toggle All",
            width=80,
            height=24,
            font=ctk.CTkFont(size=11),
            fg_color="#334155",
            hover_color="#475569",
            command=self._toggle_all_languages,
        )
        toggle_all_btn.pack(side="right")

        sec2_card = ctk.CTkFrame(form, fg_color=COLOR_CARD_BG, corner_radius=8, border_color=COLOR_BORDER, border_width=1)
        sec2_card.pack(fill="x", pady=(0, 14), padx=2, ipady=8)

        ctk.CTkLabel(sec2_card, text="Target Playwright Frameworks:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=14, pady=(8, 4))

        # Well-spaced 2-column grid container for language checkboxes
        lang_grid = ctk.CTkFrame(sec2_card, fg_color="transparent")
        lang_grid.pack(fill="x", padx=14, pady=(0, 8))
        lang_grid.grid_columnconfigure(0, weight=1, uniform="languages")
        lang_grid.grid_columnconfigure(1, weight=1, uniform="languages")

        self.chk_py = ctk.CTkCheckBox(lang_grid, text="Python (pytest)", font=ctk.CTkFont(size=12))
        self.chk_py.grid(row=0, column=0, padx=(0, 6), pady=6, sticky="w")
        self.chk_py.select()

        self.chk_java = ctk.CTkCheckBox(lang_grid, text="Java (TestNG)", font=ctk.CTkFont(size=12))
        self.chk_java.grid(row=0, column=1, padx=(6, 0), pady=6, sticky="w")
        self.chk_java.select()

        self.chk_ts = ctk.CTkCheckBox(lang_grid, text="TypeScript (@playwright)", font=ctk.CTkFont(size=12))
        self.chk_ts.grid(row=1, column=0, padx=(0, 6), pady=6, sticky="w")
        self.chk_ts.select()

        self.chk_js = ctk.CTkCheckBox(lang_grid, text="JavaScript (@playwright)", font=ctk.CTkFont(size=12))
        self.chk_js.grid(row=1, column=1, padx=(6, 0), pady=6, sticky="w")
        self.chk_js.select()

        ctk.CTkFrame(sec2_card, height=1, fg_color=COLOR_BORDER).pack(fill="x", padx=14, pady=6)

        ctk.CTkLabel(sec2_card, text="Automation Artifact Scope:", font=ctk.CTkFont(size=12, weight="bold")).pack(anchor="w", padx=14, pady=(4, 4))

        scope_box = ctk.CTkFrame(sec2_card, fg_color="transparent")
        scope_box.pack(fill="x", padx=14, pady=(0, 6))

        self.chk_plan = ctk.CTkCheckBox(scope_box, text="Generate IEEE 829 Test Plan (PLAN_TEMPLATE.md)", font=ctk.CTkFont(size=12))
        self.chk_plan.pack(anchor="w", pady=4)
        self.chk_plan.select()

        self.chk_scripts = ctk.CTkCheckBox(scope_box, text="Synthesize Multi-Language POM Frameworks", font=ctk.CTkFont(size=12))
        self.chk_scripts.pack(anchor="w", pady=4)
        self.chk_scripts.select()

        self.switch_headless = ctk.CTkSwitch(scope_box, text="Headless Browser Inspection", font=ctk.CTkFont(size=12))
        self.switch_headless.pack(anchor="w", pady=6)
        self.switch_headless.select()

        self.switch_interactive = ctk.CTkSwitch(
            scope_box,
            text="Interactive Session (Keep Browser Open)",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#F59E0B",
            command=self._on_interactive_toggled,
        )
        self.switch_interactive.pack(anchor="w", pady=(2, 6))

        # -------------------------------------------------------------------
        # SECTION 3: Output Workspace Directory
        # -------------------------------------------------------------------
        sec3_header = ctk.CTkFrame(form, fg_color="transparent")
        sec3_header.pack(fill="x", pady=(4, 6))
        ctk.CTkLabel(
            sec3_header,
            text="3. Output Workspace Directory",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color=COLOR_ACCENT,
        ).pack(side="left")

        sec3_card = ctk.CTkFrame(form, fg_color=COLOR_CARD_BG, corner_radius=8, border_color=COLOR_BORDER, border_width=1)
        sec3_card.pack(fill="x", pady=(0, 10), padx=2, ipady=8)

        out_box = ctk.CTkFrame(sec3_card, fg_color="transparent")
        out_box.pack(fill="x", padx=14, pady=(8, 6))
        out_box.grid_columnconfigure(0, weight=1)

        default_out = str(Path("./output_workspace").resolve())
        self.out_entry = ctk.CTkEntry(out_box, height=34, font=ctk.CTkFont(size=11))
        self.out_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.out_entry.insert(0, default_out)

        browse_btn = ctk.CTkButton(
            out_box,
            text="Browse...",
            width=85,
            height=34,
            command=self._browse_output_dir,
        )
        browse_btn.grid(row=0, column=1)

        # -------------------------------------------------------------------
        # SECTION 4: Action Buttons
        # -------------------------------------------------------------------
        action_box = ctk.CTkFrame(sidebar, fg_color="transparent")
        action_box.pack(fill="x", padx=16, pady=(4, 16))

        self.run_btn = ctk.CTkButton(
            action_box,
            text="🚀 Generate Test Plan & Automation Suite",
            height=46,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self._on_start_clicked,
        )
        self.run_btn.pack(fill="x", pady=(0, 8))

        # Interactive Step B Button (Revealed during Interactive Session Mode)
        self.capture_btn = ctk.CTkButton(
            action_box,
            text="📸 Capture State & Generate Suite",
            height=42,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#059669",
            hover_color="#047857",
            command=self._on_capture_clicked,
        )
        # Hidden by default until Step A is running
        self.capture_btn.pack_forget()

        self.open_folder_btn = ctk.CTkButton(
            action_box,
            text="📂 Open Output Folder",
            height=36,
            font=ctk.CTkFont(size=13),
            fg_color="#334155",
            hover_color="#475569",
            state="disabled",
            command=self._open_output_folder,
        )
        self.open_folder_btn.pack(fill="x", pady=(0, 6))

        self.close_browser_btn = ctk.CTkButton(
            action_box,
            text="🛑 Close Persistent Browser",
            height=32,
            font=ctk.CTkFont(size=12),
            fg_color="#475569",
            hover_color="#DC2626",
            command=self._on_close_browser_clicked,
        )
        self.close_browser_btn.pack(fill="x")

    # -----------------------------------------------------------------------
    # RIGHT MAIN WORKSPACE: Visual Pipeline Tracker & Multi-Tab Inspector
    # -----------------------------------------------------------------------
    def _build_right_workspace(self) -> None:
        workspace = ctk.CTkFrame(self, corner_radius=12)
        workspace.grid(row=0, column=1, padx=(8, 15), pady=15, sticky="nsew")
        workspace.grid_columnconfigure(0, weight=1)
        workspace.grid_rowconfigure(2, weight=1)

        # TOP PANEL: 5-Node Visual Pipeline Step Cards
        top_tracker_box = ctk.CTkFrame(workspace, fg_color="transparent")
        top_tracker_box.grid(row=0, column=0, sticky="ew", padx=16, pady=(16, 8))
        top_tracker_box.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        self.node_cards: Dict[str, Dict[str, Any]] = {}
        nodes_config = [
            ("intent_parser", "1. Intent Parser", "IntentParserNode"),
            ("browser_inspector", "2. UI & API Inspector", "BrowserInspector"),
            ("test_planner", "3. IEEE 829 Planner", "TestPlannerNode"),
            ("code_synthesizer", "4. Code Synthesizer", "CodeSynthesizerNode"),
            ("project_scaffolder", "5. Project Scaffolder", "ProjectScaffolderNode"),
        ]

        for idx, (node_id, title, subtitle) in enumerate(nodes_config):
            card = ctk.CTkFrame(
                top_tracker_box,
                fg_color=COLOR_PENDING,
                border_color=COLOR_BORDER,
                border_width=1,
                corner_radius=8,
                height=68,
            )
            card.grid(row=0, column=idx, padx=4, sticky="nsew")
            card.grid_propagate(False)

            title_l = ctk.CTkLabel(card, text=title, font=ctk.CTkFont(size=12, weight="bold"))
            title_l.pack(anchor="w", padx=10, pady=(8, 2))

            status_l = ctk.CTkLabel(card, text="○ Pending", font=ctk.CTkFont(size=10), text_color="#94A3B8")
            status_l.pack(anchor="w", padx=10, pady=(0, 6))

            self.node_cards[node_id] = {
                "card": card,
                "title_label": title_l,
                "status_label": status_l,
                "state": "pending",
            }

        # Progress Bar & Telemetry Banner
        telemetry_box = ctk.CTkFrame(workspace, fg_color="#0F172A", corner_radius=8)
        telemetry_box.grid(row=1, column=0, sticky="ew", padx=16, pady=(0, 10))
        telemetry_box.grid_columnconfigure(0, weight=1)

        # Header with Status + Percent
        t_header = ctk.CTkFrame(telemetry_box, fg_color="transparent")
        t_header.pack(fill="x", padx=12, pady=(10, 4))

        self.status_banner_lbl = ctk.CTkLabel(
            t_header,
            text="Ready. Enter a URL and click Generate to start the pipeline.",
            font=ctk.CTkFont(size=13, weight="bold"),
        )
        self.status_banner_lbl.pack(side="left")

        self.pct_display_lbl = ctk.CTkLabel(
            t_header,
            text="0%",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#38BDF8",
        )
        self.pct_display_lbl.pack(side="right")

        # Smooth Progress Bar
        self.progress_bar = ctk.CTkProgressBar(telemetry_box, height=12)
        self.progress_bar.pack(fill="x", padx=12, pady=(0, 8))
        self.progress_bar.set(0.0)

        # Live Counter Badges
        counter_box = ctk.CTkFrame(telemetry_box, fg_color="transparent")
        counter_box.pack(fill="x", padx=12, pady=(0, 10))

        self.counter_dom_lbl = ctk.CTkLabel(
            counter_box,
            text="DOM Locators: 0",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94A3B8",
        )
        self.counter_dom_lbl.pack(side="left", padx=(0, 16))

        self.counter_api_lbl = ctk.CTkLabel(
            counter_box,
            text="APIs Intercepted: 0",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94A3B8",
        )
        self.counter_api_lbl.pack(side="left", padx=(0, 16))

        self.counter_files_lbl = ctk.CTkLabel(
            counter_box,
            text="Files Generated: 0",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#94A3B8",
        )
        self.counter_files_lbl.pack(side="left")

        # BOTTOM PANEL: CTkTabview with 3 Tabs
        self.tabs = ctk.CTkTabview(workspace, corner_radius=8)
        self.tabs.grid(row=2, column=0, sticky="nsew", padx=16, pady=(0, 16))

        tab_console = self.tabs.add("🖥 Live Execution Console")
        tab_plan = self.tabs.add("📋 Corporate Test Plan (IEEE 829)")
        tab_files = self.tabs.add("🗂 Generated Project Files")

        # --- TAB 1: Live Execution Console ---
        tab_console.grid_columnconfigure(0, weight=1)
        tab_console.grid_rowconfigure(0, weight=1)

        self.console_textbox = ctk.CTkTextbox(
            tab_console,
            wrap="word",
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self.console_textbox.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)

        # --- TAB 2: Corporate Test Plan Markdown ---
        tab_plan.grid_columnconfigure(0, weight=1)
        tab_plan.grid_rowconfigure(0, weight=1)

        self.plan_textbox = ctk.CTkTextbox(
            tab_plan,
            wrap="word",
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self.plan_textbox.grid(row=0, column=0, sticky="nsew", padx=4, pady=4)
        self.plan_textbox.insert(
            "0.0",
            "IEEE 829 Corporate Test Plan (PLAN_TEMPLATE.md format) will be generated here automatically after TestPlannerNode completes.\n",
        )

        # --- TAB 3: Generated Project Files Previewer ---
        tab_files.grid_columnconfigure(0, weight=1)
        tab_files.grid_rowconfigure(1, weight=1)

        file_nav_bar = ctk.CTkFrame(tab_files, fg_color="transparent")
        file_nav_bar.grid(row=0, column=0, sticky="ew", padx=4, pady=(4, 6))

        ctk.CTkLabel(file_nav_bar, text="Select File to Inspect:", font=ctk.CTkFont(size=12, weight="bold")).pack(side="left", padx=(0, 8))

        self.file_selector = ctk.CTkOptionMenu(
            file_nav_bar,
            values=["(No files generated yet)"],
            width=380,
            command=self._on_file_selected,
        )
        self.file_selector.pack(side="left")

        self.code_preview_textbox = ctk.CTkTextbox(
            tab_files,
            wrap="none",
            font=ctk.CTkFont(family="Consolas", size=12),
        )
        self.code_preview_textbox.grid(row=1, column=0, sticky="nsew", padx=4, pady=4)
        self.code_preview_textbox.insert("0.0", "// Select a generated file above to preview its synthesized source code.\n")

    # -----------------------------------------------------------------------
    # Interactive Session Mode Helpers
    # -----------------------------------------------------------------------
    def _on_interactive_toggled(self) -> None:
        """Adjust UI button labels when interactive mode is switched."""
        is_interactive = bool(self.switch_interactive.get())
        if is_interactive:
            self.switch_headless.deselect()  # Browser must be visible
            if not self._is_running:
                self.run_btn.configure(text="🌐 Step A: Launch & Keep Browser Open", fg_color="#D97706", hover_color="#B45309")
        else:
            if not self._is_running:
                self.run_btn.configure(text="🚀 Generate Test Plan & Automation Suite", fg_color="#2563EB", hover_color="#1D4ED8")
            self.capture_btn.pack_forget()

    def _on_capture_clicked(self) -> None:
        """Triggered by user in Step B to capture live state and generate suites."""
        if self._interactive_trigger_event:
            self._interactive_trigger_event.set()
            self.capture_btn.configure(state="disabled", text="⏳ Analyzing & Generating Suites...")
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
        self.status_banner_lbl.configure(text=f"[{node_name}] {message}")

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
        self.status_banner_lbl.configure(text="Pipeline Complete! Multi-Language Suites & Test Plan Ready.")
        
        # Reset Action Buttons
        is_interactive = bool(self.switch_interactive.get())
        if is_interactive:
            self.run_btn.configure(state="normal", text="🌐 Step A: Launch & Keep Browser Open", fg_color="#D97706", hover_color="#B45309")
        else:
            self.run_btn.configure(state="normal", text="🚀 Generate Test Plan & Automation Suite", fg_color="#2563EB", hover_color="#1D4ED8")
        self.capture_btn.pack_forget()

        self.open_folder_btn.configure(state="normal", fg_color=COLOR_COMPLETED, hover_color="#15803D")

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

        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.console_textbox.insert(
            "end",
            f"\n[{timestamp}] [100%] [PIPELINE SUCCESS] Successfully generated {file_count} assets.\n",
        )
        self.console_textbox.see("end")

        if not self.is_test_mode:
            messagebox.showinfo(
                "Framework Generation Complete",
                f"Successfully synthesized {file_count} automation assets!\n\n"
                f"- DOM Locators Cataloged: {dom_count}\n"
                f"- API Contracts Intercepted: {api_count}\n\n"
                f"Output Folder: {self.out_entry.get().strip()}",
            )

    def _handle_error_event(self, msg: Dict[str, Any]) -> None:
        err = msg.get("error", "Unknown error")
        self._is_running = False

        # Mark active card as error
        for node_id, card_info in self.node_cards.items():
            if card_info["state"] == "running":
                self._set_node_state(node_id, "error")

        is_interactive = bool(self.switch_interactive.get())
        if is_interactive:
            self.run_btn.configure(state="normal", text="🌐 Step A: Launch & Keep Browser Open", fg_color="#D97706", hover_color="#B45309")
        else:
            self.run_btn.configure(state="normal", text="🚀 Generate Test Plan & Automation Suite", fg_color="#2563EB", hover_color="#1D4ED8")
        self.capture_btn.pack_forget()
        self.status_banner_lbl.configure(text=f"Pipeline Error: {err[:60]}")
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
        """Autofills offline fixture demo portal URL."""
        self.url_entry.delete(0, "end")
        self.url_entry.insert(0, "http://127.0.0.1:49790/")

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
            self.out_entry.delete(0, "end")
            self.out_entry.insert(0, os.path.normpath(chosen))

    def _on_close_browser_clicked(self) -> None:
        """User clicked close persistent browser."""
        BrowserInspector.close_persistent_browser_sync()
        self.console_textbox.insert("end", "[INFO] Persistent browser session closed.\n")
        self.console_textbox.see("end")

    def _open_output_folder(self) -> None:
        target = self.out_entry.get().strip()
        if os.path.exists(target):
            os.startfile(target)
        else:
            messagebox.showwarning("Directory Not Found", f"Output folder does not exist yet:\n{target}")

    def _on_start_clicked(self) -> None:
        if self._is_running:
            return

        target_url = self.url_entry.get().strip()
        flow_prompt = self.flow_text.get("0.0", "end").strip()
        output_dir = self.out_entry.get().strip()

        if not target_url:
            messagebox.showerror("Validation Error", "Please provide a valid Target URL.")
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

        if not selected_langs:
            messagebox.showerror("Validation Error", "Please select at least one Target Language.")
            return

        # Prepare UI
        self._is_running = True
        is_interactive = bool(self.switch_interactive.get())

        if is_interactive:
            self._interactive_trigger_event = threading.Event()
            self.run_btn.configure(state="disabled", text="🌐 Browser Running (Interactive Mode)...")
            # Reveal Step B capture button prominently
            self.capture_btn.pack(fill="x", pady=(0, 8), before=self.open_folder_btn)
            self.capture_btn.configure(state="normal", text="📸 Step B: Capture State & Generate Suite")
        else:
            self._interactive_trigger_event = None
            self.run_btn.configure(state="disabled", text="⏳ Synthesizing Automation Suites...")
            self.capture_btn.pack_forget()

        self.open_folder_btn.configure(state="disabled", fg_color="#334155")
        self.console_textbox.delete("0.0", "end")
        self.progress_bar.set(0.0)
        self.pct_display_lbl.configure(text="0%")
        self.status_banner_lbl.configure(
            text="Launching Interactive Browser Session..." if is_interactive else "Launching 5-Node Zero-API LangGraph Pipeline..."
        )
        self._reset_pipeline_cards()

        initial_state: AgentState = {
            "target_url": target_url,
            "user_flow_text": flow_prompt,
            "target_languages": selected_langs,
            "output_dir": output_dir,
            "headless": False if is_interactive else bool(self.switch_headless.get()),
            "generate_test_plan": bool(self.chk_plan.get()),
            "generate_scripts": bool(self.chk_scripts.get()),
            "interactive_mode": is_interactive,
            "capture_trigger_event": self._interactive_trigger_event,
            "progress_callback": self._enqueue_progress,
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
