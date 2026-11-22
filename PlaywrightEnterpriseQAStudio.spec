# -*- mode: python ; coding: utf-8 -*-
"""PyInstaller Specification for Playwright Enterprise QA Agent Studio.

Phase 5: 100% Offline Standalone Windows Executable Build.
Bundles CustomTkinter assets, Jinja2 template registries, project source packages,
and Playwright driver binaries (node.exe + driver package).
Runs deterministically against the corporate workstation's pre-installed Chrome/Edge.
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_all, collect_data_files, collect_submodules

block_cipher = None

ROOT = Path.cwd()

# 1. CustomTkinter assets (themes, json, fonts)
datas = collect_data_files("customtkinter")

# 2. Project source packages
datas += [
    (str(ROOT / "core"), "core"),
    (str(ROOT / "agents"), "agents"),
    (str(ROOT / "scaffolder"), "scaffolder"),
    (str(ROOT / "gui"), "gui"),
]

# 3. Include templates directory or PLAN_TEMPLATE.md if present
templates_dir = ROOT / "templates"
if templates_dir.exists():
    datas.append((str(templates_dir), "templates"))
plan_template_file = ROOT / "PLAN_TEMPLATE.md"
if plan_template_file.exists():
    datas.append((str(plan_template_file), "."))

# 4. Playwright Driver (node.exe + driver package) & FFmpeg for Offline Video Recording
import os
import playwright
pw_dir = Path(playwright.__file__).parent
driver_dir = pw_dir / "driver"
if driver_dir.exists():
    datas.append((str(driver_dir), "playwright/driver"))

# Desktop sandboxes can redirect LOCALAPPDATA while installed browser media lives
# in the user's real cache. Copy only FFmpeg, not the browser installations.
media_caches = [
    Path(os.environ.get("LOCALAPPDATA", "")) / "ms-playwright",
    Path.home() / "AppData" / "Local" / "ms-playwright",
    ROOT / "dist_release" / "PlaywrightEnterpriseQAStudio" / "_internal" / "ms-playwright",
]
bundled_ffmpeg = set()
for cache in media_caches:
    for ff_dir in sorted(cache.glob("ffmpeg-*")):
        if ff_dir.is_dir() and ff_dir.name not in bundled_ffmpeg:
            datas.append((str(ff_dir), f"ms-playwright/{ff_dir.name}"))
            bundled_ffmpeg.add(ff_dir.name)
if not bundled_ffmpeg:
    print("WARNING: FFmpeg not found; this package will capture screenshots and traces without video.")

# 5. Collect Hidden Imports & Dependencies
hiddenimports = [
    "customtkinter",
    "playwright",
    "playwright.async_api",
    "playwright.sync_api",
    "langgraph",
    "langgraph.graph",
    "jinja2",
    "pydantic",
    "pydantic_core",
    "pyee",
    "pyee.asyncio",
    "core.workspace_manager",
    "core.report_generator",
    "core.browser_inspector",
    "core.models",
    "agents.state",
    "agents.intent_parser",
    "agents.planner_node",
    "agents.code_synthesizer_node",
    "agents.workflow_graph",
    "scaffolder.project_builder",
    "scaffolder.template_registry",
    "gui.app_window",
]

# Add all submodules for key packages
for pkg in ["langgraph", "jinja2", "pydantic"]:
    try:
        hiddenimports.extend(collect_submodules(pkg))
    except Exception:
        pass

hiddenimports = list(dict.fromkeys(hiddenimports))

a = Analysis(
    ["main.py"],
    pathex=[str(ROOT)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=["tkinter.test", "unittest", "pydoc"],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="PlaywrightEnterpriseQAStudio",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,  # Console enabled for troubleshooting corporate runtime logs
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="PlaywrightEnterpriseQAStudio",
)
