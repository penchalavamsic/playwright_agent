"""Phase 5 Smoke Test Verification Script.

Asserts that dist/PlaywrightEnterpriseQAStudio/PlaywrightEnterpriseQAStudio.exe exists,
validates its CLI argument handling (--help), and outputs corporate deployment guidance.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TARGET_EXE = ROOT / "dist" / "PlaywrightEnterpriseQAStudio" / "PlaywrightEnterpriseQAStudio.exe"
TARGET_RELEASE_EXE = ROOT / "dist_release" / "PlaywrightEnterpriseQAStudio" / "PlaywrightEnterpriseQAStudio.exe"


def test_phase5_smoke() -> int:
    print("=" * 80)
    print("PHASE 5 STANDALONE WINDOWS EXECUTABLE SMOKE TEST")
    print("=" * 80)

    exe_target = TARGET_RELEASE_EXE if TARGET_RELEASE_EXE.exists() else TARGET_EXE

    passed = 0
    failed = 0

    def check(condition: bool, desc: str) -> None:
        nonlocal passed, failed
        if condition:
            passed += 1
            print(f"  [PASS] {desc}")
        else:
            failed += 1
            print(f"  [FAIL] {desc}")

    # 1. Assert Executable File Existence
    check(exe_target.exists(), f"PlaywrightEnterpriseQAStudio.exe exists at {exe_target}")

    if not exe_target.exists():
        print(f"\n[FAIL] Executable not found. Please run build_exe.py first.")
        return 1

    # 2. Assert Valid Binary Size
    size_mb = exe_target.stat().st_size / (1024 * 1024)
    check(size_mb > 0.05, f"Executable binary size is valid ({size_mb:.2f} MB)")

    # 3. Assert Directory Structure inside dist/
    dist_dir = exe_target.parent
    check((dist_dir / "_internal").exists() or (dist_dir / "base_library.zip").exists(), "PyInstaller internal dependency bundles exist")

    # 4. Smoke test: Run executable with --help in CLI mode
    print("\nExecuting Smoke Test: PlaywrightEnterpriseQAStudio.exe --help ...")
    try:
        proc = subprocess.run(
            [str(exe_target), "--help"],
            capture_output=True,
            text=True,
            timeout=15,
        )
        check(proc.returncode == 0, f"Executable executed successfully (Exit Code: {proc.returncode})")
        check(
            "Playwright Enterprise QA Agent Studio" in proc.stdout
            or "Offline Zero-API" in proc.stdout
            or "--url" in proc.stdout,
            "Executable CLI output contains expected help text",
        )
    except Exception as exc:
        check(False, f"Executable execution failed with error: {exc}")

    # 5. Output Deployment Instructions
    print("\n" + "=" * 80)
    print(f"PHASE 5 VERIFICATION RESULTS: {passed} passed, {failed} failed")
    print("=" * 80)

    if failed == 0:
        print("\nCORPORATE DEPLOYMENT GUIDANCE:")
        print("  1. The entire folder 'dist/PlaywrightEnterpriseQAStudio/' is standalone.")
        print("  2. It can be zipped or distributed to any Windows 10/11 / Windows Server workstation.")
        print("  3. No Python installation, cloud keys, or external browser downloads are needed.")
        print("  4. It automatically detects and uses corporate Chrome or Edge.")
        print("PHASE 5 STANDALONE EXECUTABLE VERIFICATION PASSED")
        return 0

    return 1


if __name__ == "__main__":
    sys.exit(test_phase5_smoke())

