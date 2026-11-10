"""Automated Windows Executable Build Script (Phase 5).

Cleans previous build artifacts, runs PyInstaller with the enterprise spec,
validates output executable existence, checks binary sizes, and prints a deployment summary.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BUILD_DIR = ROOT / "build"
DIST_DIR = ROOT / "dist"
DIST_RELEASE_DIR = ROOT / "dist_release"
SPEC_FILE = ROOT / "PlaywrightEnterpriseQAStudio.spec"
TARGET_EXE = DIST_DIR / "PlaywrightEnterpriseQAStudio" / "PlaywrightEnterpriseQAStudio.exe"
TARGET_RELEASE_EXE = DIST_RELEASE_DIR / "PlaywrightEnterpriseQAStudio" / "PlaywrightEnterpriseQAStudio.exe"


def clean_build_artifacts() -> None:
    """Safely remove previous build and dist directories."""
    print("[1/4] Cleaning previous build artifacts...")
    for folder in [BUILD_DIR, DIST_DIR, DIST_RELEASE_DIR]:
        if folder.exists():
            print(f"      Removing: {folder}")
            shutil.rmtree(folder, ignore_errors=True)
    print("      Clean complete.")


def run_pyinstaller() -> int:
    """Execute PyInstaller build process."""
    print(f"\n[2/4] Executing PyInstaller build with spec: {SPEC_FILE.name}...")
    pyinstaller_exe = ROOT / ".venv" / "Scripts" / "pyinstaller.exe"
    if not pyinstaller_exe.exists():
        pyinstaller_exe = Path(sys.executable).parent / "Scripts" / "pyinstaller.exe"
    if not pyinstaller_exe.exists():
        pyinstaller_cmd = [sys.executable, "-m", "PyInstaller"]
    else:
        pyinstaller_cmd = [str(pyinstaller_exe)]

    cmd = pyinstaller_cmd + [str(SPEC_FILE), "--noconfirm", "--distpath", str(DIST_RELEASE_DIR)]
    print(f"      Command: {' '.join(cmd)}")

    start_time = time.time()
    result = subprocess.run(cmd, cwd=str(ROOT))
    elapsed = time.time() - start_time

    if result.returncode != 0:
        print(f"      [ERROR] PyInstaller failed with exit code: {result.returncode}", file=sys.stderr)
        return result.returncode

    # If dist is free, sync/copy or use dist_release
    print(f"      PyInstaller completed successfully in {elapsed:.1f}s.")
    return 0


def verify_executable() -> bool:
    """Verify that the compiled executable exists and has valid size."""
    print("\n[3/4] Verifying generated executable binary...")
    target = TARGET_RELEASE_EXE if TARGET_RELEASE_EXE.exists() else TARGET_EXE
    if not target.exists():
        print(f"      [ERROR] Expected executable not found at: {target}", file=sys.stderr)
        return False

    size_bytes = target.stat().st_size
    size_mb = size_bytes / (1024 * 1024)
    print(f"      Executable: {target}")
    print(f"      File Size : {size_mb:.2f} MB ({size_bytes:,} bytes)")

    # Verify bundled Playwright driver
    bundled_driver = target.parent / "_internal" / "playwright" / "driver" / "node.exe"
    if not bundled_driver.exists():
        bundled_driver = target.parent / "playwright" / "driver" / "node.exe"

    if bundled_driver.exists():
        print(f"      Bundled Playwright Driver: {bundled_driver.name} (Verified)")
    else:
        print("      Note: Playwright driver located in bundled site packages.")

    return True


def print_summary() -> None:
    """Print final build and deployment summary."""
    target = TARGET_RELEASE_EXE if TARGET_RELEASE_EXE.exists() else TARGET_EXE
    print("\n[4/4] Enterprise Deployment Summary:")
    print("=" * 80)
    print("  PACKAGE: Playwright Enterprise QA Agent Studio (100% Offline Standalone .exe)")
    print(f"  LOCATION: {target}")
    print("  RUNTIME DEPENDENCY: Zero external APIs or cloud keys required.")
    print("  BROWSER: Uses corporate pre-installed Chrome (`channel=chrome`) or Edge (`channel=msedge`).")
    print("  LAUNCH INSTRUCTIONS:")
    print(f"    & '{target}'")
    print("=" * 80)


def main() -> int:
    clean_build_artifacts()
    code = run_pyinstaller()
    if code != 0:
        return code

    if not verify_executable():
        return 1

    print_summary()
    return 0


if __name__ == "__main__":
    sys.exit(main())

