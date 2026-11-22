"""Self-Contained Offline Enterprise Test Evidence Report Generator (Phase 7).

Models the exact visual layout, CSS styling, directory hierarchy, and evidence structure
of `./Complete-Suite-Test-Report/`:
  - Complete-Suite-Test-Report/index.html
  - Complete-Suite-Test-Report/README.txt
  - Complete-Suite-Test-Report/report-summary.json
  - Complete-Suite-Test-Report/Evidence/Plans/<TEST_ID>/<TEST_ID>-<slug>.md
  - Complete-Suite-Test-Report/Evidence/Screenshots/<TEST_ID>/<NN>-<step>.png & final-screenshot.png
  - Complete-Suite-Test-Report/Evidence/Recording/<TEST_ID>/video.webm
  - Complete-Suite-Test-Report/Evidence/Trace/<TEST_ID>/trace.zip

100% offline: zero external CDN links, fonts, scripts, or internet dependencies.
100% dynamic application naming: zero hardcoded application names or URLs.
"""

from __future__ import annotations

import datetime
import html
import json
import re
import shutil
import struct
import zipfile
import zlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urlparse


def _slugify(text: str, max_len: int = 48) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", (text or "").strip().lower()).strip("-")
    return (cleaned[:max_len].strip("-") or "step")


def _title_case_slug(slug: str) -> str:
    return " ".join(w.capitalize() for w in slug.replace("_", "-").split("-") if w)


def derive_app_display_name(target_url: str, page_title: str = "") -> Tuple[str, str]:
    """Derive dynamic `(app_display_name, domain_label)` from target_url and page_title."""
    parsed = urlparse((target_url or "").strip())
    hostname = (parsed.hostname or "").lower()
    netloc = parsed.netloc or hostname or "localhost"
    domain_label = re.sub(r"^www\.", "", hostname) if hostname else "application"

    clean_title = (page_title or "").strip()
    title_first_segment = re.split(r"\s+[\-—|:]\s+", clean_title)[0].strip() if clean_title else ""

    if hostname in ("localhost", "127.0.0.1", "::1", ""):
        domain_label = netloc or "localhost"
        app_name = title_first_segment or "Localhost Application"
    else:
        parts = [p for p in domain_label.split(".") if p and p not in ("com", "org", "net", "io", "co", "gov", "edu", "local", "internal")]
        domain_brand = parts[0].capitalize() if parts else domain_label.capitalize()
        app_name = domain_brand if len(title_first_segment) > 28 or not title_first_segment else title_first_segment

    return app_name, domain_label


def generate_offline_png(width: int = 640, height: int = 360, rgb: tuple[int, int, int] = (26, 26, 46)) -> bytes:
    """Create a valid self-contained PNG image in pure Python (fallback when no browser screenshot exists)."""
    r, g, b = rgb
    raw_rows = []
    for y in range(height):
        if y < 44:
            row_rgb = bytes((r, g, b)) * width
        elif 44 <= y < 48:
            row_rgb = bytes((76, 175, 80)) * width
        else:
            row_rgb = bytes((245, 247, 250)) * width
        raw_rows.append(b"\x00" + row_rgb)
    raw_data = b"".join(raw_rows)

    def _chunk(chunk_type: bytes, data: bytes) -> bytes:
        crc = zlib.crc32(chunk_type + data) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + chunk_type + data + struct.pack(">I", crc)

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    idat = zlib.compress(raw_data, level=6)
    return b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr) + _chunk(b"IDAT", idat) + _chunk(b"IEND", b"")


def build_readme_txt(app_display_name: str) -> str:
    return f"""{app_display_name} Complete Suite Test Evidence Report

1. Extract the complete ZIP before opening the report.
2. Keep index.html and the Evidence folder together.
3. Open the extracted index.html.
4. Do not open index.html directly inside the ZIP.
5. Individual test reports are linked from the header section.
"""


class EnterpriseReportGenerator:
    """Generates self-contained Complete-Suite-Test-Report directory and HTML/JSON evidence."""

    REPORT_DIR_NAME = "Complete-Suite-Test-Report"

    def __init__(self, project_root: str | Path) -> None:
        self.project_root = Path(project_root).resolve()
        self.report_dir = self.project_root / self.REPORT_DIR_NAME
        self.evidence_dir = self.report_dir / "Evidence"
        self.plans_dir = self.evidence_dir / "Plans"
        self.screenshots_dir = self.evidence_dir / "Screenshots"
        self.recording_dir = self.evidence_dir / "Recording"
        self.trace_dir = self.evidence_dir / "Trace"

    def _ensure_dirs(self) -> None:
        for d in (
            self.report_dir,
            self.evidence_dir,
            self.plans_dir,
            self.screenshots_dir,
            self.recording_dir,
            self.trace_dir,
        ):
            d.mkdir(parents=True, exist_ok=True)

    def generate_from_agent_state(self, state: Dict[str, Any]) -> List[str]:
        """Generate or update Complete-Suite-Test-Report from an AgentState pipeline run."""
        self._ensure_dirs()
        created_files: List[str] = []

        report = state.get("inspection_report") or {}
        target_url = state.get("target_url", "") or report.get("target_url", "")
        page_title = report.get("page_title", "") or ""
        app_display_name, domain_label = derive_app_display_name(target_url, page_title)
        clean_page = page_title.strip() if page_title.strip() else app_display_name
        module_name = (app_display_name.split()[0] if app_display_name else "Core").strip(" -—|") or "Core"
        browser_channel = (report.get("browser_channel") or "Edge").capitalize()
        raw_profile = state.get("active_access_profile", "") or "PUBLIC"
        profile = (
            "PUBLIC"
            if raw_profile.strip() in ("", "None (Public URL)", "NONE", "PUBLIC")
            else raw_profile.strip().upper().replace(" ", "_")
        )
        seq_num = int(state.get("sequence_number") or 1)
        apis = report.get("captured_apis") or []
        scenarios = state.get("test_scenarios") or []

        # Real captured evidence paths from BrowserInspector
        real_step_screenshots: List[Dict[str, str]] = report.get("step_screenshots") or []
        real_final_screenshot: str = report.get("final_screenshot_path") or ""
        real_video_path: str = report.get("video_path") or ""
        real_trace_path: str = report.get("trace_path") or ""

        primary_api = apis[0] if apis else {
            "method": "GET",
            "url": target_url or "/api",
            "status_code": "Not observed",
            "triggered_by_action": "No API response captured",
        }
        parsed_path = urlparse(primary_api.get("url", "")).path or "/"

        # Build test case records for this run
        new_cases: List[Dict[str, Any]] = []
        id_prefix = re.sub(r"[^A-Z0-9]", "", module_name.upper())[:6] or "APP"
        for idx, sc in enumerate(scenarios, start=1):
            sc_title = sc.get("title", f"Scenario {idx}")
            test_id = f"{id_prefix}-{seq_num:03d}-{idx:02d}"
            slug = _slugify(sc_title)
            steps_raw = sc.get("steps") or []
            step_descriptions = [
                s.get("description") or f"{s.get('action', 'VERIFY')} {s.get('element_name', '')}".strip()
                for s in steps_raw
            ]
            if not step_descriptions:
                step_descriptions = [
                    "Navigate to application entry point",
                    "Verify core interactive components and API contract",
                ]

            executed = idx == 1 and bool(report.get("execution_steps"))
            status = report.get("execution_status", "not_run") if executed else "not_run"
            duration_s = report.get("duration_s", 0.0) if executed else 0.0
            execution_steps = report.get("execution_steps", []) if executed else []
            if executed:
                step_descriptions = [f"{r['action_type']} {r['target_keyword']} - {r['status'].upper()}" for r in execution_steps]
            error = "\n".join(r.get("error", "") for r in execution_steps if r.get("status") == "failed")
            if not executed:
                error = "Planned scenario only; not executed. Inspection evidence is not proof that this scenario passed."
            jira_heading = f'"{module_name}" → "{clean_page}" → "{sc_title}"'

            # Write per-test Evidence files (copying real Playwright screenshots, video.webm, trace.zip)
            case_evidence = self._write_case_evidence(
                test_id=test_id,
                slug=slug,
                title=jira_heading,
                module=module_name,
                page_title=clean_page,
                profile=profile,
                steps=step_descriptions,
                primary_api=primary_api,
                all_apis=apis,
                real_step_screenshots=real_step_screenshots if executed else [],
                real_final_screenshot=real_final_screenshot if executed else "",
                real_video_path=real_video_path if executed else "",
                real_trace_path=real_trace_path if executed else "",
                created_files=created_files,
            )

            new_cases.append(
                {
                    "test_id": test_id,
                    "slug": slug,
                    "title": jira_heading,
                    "raw_title": sc_title,
                    "module": module_name,
                    "page": clean_page,
                    "profile": profile,
                    "status": status,
                    "duration_s": duration_s,
                    "actual_duration_s": duration_s,
                    "execution_steps": execution_steps,
                    "auth_diagnostics": report.get('auth_diagnostics', {}) if executed else {},
                    "final_route": report.get("final_url", "") if executed else "",
                    "spec_path": "See numbered flow test in the selected language folder" if idx == 1 else "Not generated (advisory plan)",
                    "plan_rel_path": case_evidence["plan_rel_path"],
                    "plan_filename": case_evidence["plan_filename"],
                    "plan_markdown": case_evidence["plan_markdown"],
                    "purpose": f"Verify {sc_title} for {app_display_name} ({clean_page}) under access profile {profile}.",
                    "expected_result": "All explicitly requested actions and assertions complete in order.",
                    "steps": step_descriptions,
                    "step_screenshots": case_evidence["step_screenshots"],
                    "final_screenshot": case_evidence["final_screenshot"],
                    "video_rel_path": case_evidence["video_rel_path"],
                    "trace_rel_path": case_evidence["trace_rel_path"],
                    "api_method": primary_api.get("method", "GET"),
                    "api_pathname": parsed_path,
                    "api_status": primary_api.get("status_code", 200),
                    "api_trigger": primary_api.get("triggered_by_action", "Page navigation"),
                    "captured_apis": apis if executed else [],
                    "error_message": error,
                }
            )

        # Merge with any existing report-summary.json cases across multi-day runs
        summary_json_path = self.report_dir / "report-summary.json"
        existing_cases: List[Dict[str, Any]] = []
        if summary_json_path.exists():
            try:
                old_data = json.loads(summary_json_path.read_text(encoding="utf-8"))
                existing_cases = list(old_data.get("test_cases", []))
                if old_data.get('schema_version', 0) < 2:
                    for case in existing_cases:
                        case['legacy_reported_status'] = case.get('status', 'unknown')
                        case['status'] = 'not_run'
                        case['duration_s'] = 0.0
                        case['actual_duration_s'] = 0.0
                        case['error_message'] = 'Legacy report: execution provenance unavailable. Regenerate this flow to verify its result.'
                        case['step_screenshots'] = []
                        for key in ('final_screenshot', 'video_rel_path', 'trace_rel_path'):
                            case[key] = ''
            except Exception:
                existing_cases = []

        merged_by_id: Dict[str, Dict[str, Any]] = {c["test_id"]: c for c in existing_cases if "test_id" in c}
        for c in new_cases:
            merged_by_id[c["test_id"]] = c
        all_cases = list(merged_by_id.values())

        total_count = len(all_cases)
        passed_count = sum(1 for c in all_cases if c.get("status") == "passed")
        failed_count = sum(1 for c in all_cases if c.get("status") == "failed")
        flaky_count = sum(1 for c in all_cases if c.get("status") == "flaky")
        skipped_count = sum(1 for c in all_cases if c.get("status") in ("skipped", "not_run"))
        total_duration = round(sum(float(c.get("duration_s", 0.0)) for c in all_cases), 2)
        executed_count = passed_count + failed_count
        pass_rate = round((passed_count / executed_count) * 100.0, 1) if executed_count else 0.0
        date_str = datetime.datetime.now().strftime("%Y-%m-%d")

        summary_payload = {
            "schema_version": 2,
            "report_title": f"{app_display_name} Detailed Test Evidence Report — {domain_label} — {profile}",
            "app_display_name": app_display_name,
            "domain_label": domain_label,
            "module": module_name,
            "profile": profile,
            "target_url": "${BASE_URL}",
            "browser": browser_channel,
            "date": date_str,
            "total": total_count,
            "passed": passed_count,
            "failed": failed_count,
            "flaky": flaky_count,
            "skipped": skipped_count,
            "pass_rate_pct": pass_rate,
            "duration_s": total_duration,
            "test_cases": all_cases,
        }

        summary_json_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")
        created_files.append(str(summary_json_path))

        readme_txt_path = self.report_dir / "README.txt"
        readme_txt_path.write_text(build_readme_txt(app_display_name), encoding="utf-8")
        created_files.append(str(readme_txt_path))

        index_html_path = self.report_dir / "index.html"
        index_html_path.write_text(self.render_html_report(summary_payload), encoding="utf-8")
        created_files.append(str(index_html_path))

        return created_files

    def _write_case_evidence(
        self,
        test_id: str,
        slug: str,
        title: str,
        module: str,
        page_title: str,
        profile: str,
        steps: List[str],
        primary_api: Dict[str, Any],
        all_apis: List[Dict[str, Any]],
        real_step_screenshots: List[Dict[str, str]],
        real_final_screenshot: str,
        real_video_path: str,
        real_trace_path: str,
        created_files: List[str],
    ) -> Dict[str, Any]:
        """Write Evidence/Plans, Evidence/Screenshots, Evidence/Recording, and Evidence/Trace for a test case."""
        # 1. Plan markdown file
        case_plan_dir = self.plans_dir / test_id
        case_plan_dir.mkdir(parents=True, exist_ok=True)
        plan_filename = f"{test_id}-{slug}.md"
        plan_path = case_plan_dir / plan_filename
        plan_rel_path = f"Plans/{test_id}/{plan_filename}"

        api_path = urlparse(primary_api.get("url", "")).path or "/"
        api_method = primary_api.get("method", "GET")
        api_status = primary_api.get("status_code", 200)

        steps_md_lines = []
        for i, st in enumerate(steps, start=1):
            steps_md_lines.append(
                f"{i}. Action: {st}.\n   Expected Result: Step completes deterministically without UI or network errors."
            )
        steps_md = "\n\n".join(steps_md_lines)

        plan_md = f"""---
test_id: "{test_id}"
title: "To verify the functionality of {title.replace('"', '\\"')}"
module: "{module}"
page: "{page_title}"
section: "Primary Flow"
control: "Interactive Controls"
action: "Execution & Verification"
access_profile: "{profile}"
priority: "High"
classification: "Read-only"
test_type: "Positive"
automation_candidate: true
plan_status: "generated"
script_status: "generated"
environment_variables:
  - BASE_URL
  - TEST_ACCESS_PROFILE
test_data: {{}}
related_script: "tests/{slug}.spec.ts"
---

# Purpose

Verify the functionality of {title} under access profile `{profile}`.

# Preconditions

- `${{BASE_URL}}` is reachable.
- Credentials for `${{TEST_ACCESS_PROFILE}}` (`{profile}`) are configured in `.env`.

# Test Data

Use environment variables and runtime fixtures.

# Steps and Expected Results

{steps_md}

# Network Verification

- Request URL: `${{BASE_URL}}{api_path}`
- HTTP Method: {api_method}
- Expected Status: {api_status}
- Payload Presence: See observed telemetry; not independently asserted
- Visible UI Result: Interactive controls visible and responsive

# Expected Final Result

All steps and network status assertions succeed for {test_id}.

# Classification

- Read-only
- Positive

# Restrictions

- Do not include credentials, tokens, cookies, authorization codes, or sensitive payloads.
- Do not use static environment-specific data.

# Generation Status

- Generated plan; execution status is recorded separately in the report.
"""
        plan_path.write_text(plan_md, encoding="utf-8")
        created_files.append(str(plan_path))

        # 2. Step Screenshots + Final Screenshot (Copy real Playwright PNGs when available)
        case_ss_dir = self.screenshots_dir / test_id
        case_ss_dir.mkdir(parents=True, exist_ok=True)
        step_screenshots: List[Dict[str, str]] = []

        valid_real_steps = [
            s for s in real_step_screenshots
            if s.get("file_path") and Path(s["file_path"]).exists() and Path(s["file_path"]).stat().st_size > 0
        ]
        valid_real_final = (
            Path(real_final_screenshot)
            if real_final_screenshot and Path(real_final_screenshot).exists() and Path(real_final_screenshot).stat().st_size > 0
            else (Path(valid_real_steps[-1]["file_path"]) if valid_real_steps else None)
        )
        # Preserve capture labels and order; never relabel one image as several steps.
        for i, shot in enumerate(valid_real_steps, start=1):
            name = f"{i:02d}-step.png"
            dest = case_ss_dir / name
            shutil.copy2(shot['file_path'], dest)
            created_files.append(str(dest))
            step_screenshots.append({"rel_path": f"Evidence/Screenshots/{test_id}/{name}",
                                     "caption": shot.get('step_name', f'Step {i}')})

        def copy_real(source, folder, filename):
            if not source or not Path(source).is_file() or Path(source).stat().st_size == 0:
                return ""
            dest = self.report_dir / "Evidence" / folder / test_id / filename
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, dest)
            created_files.append(str(dest))
            return dest.relative_to(self.report_dir).as_posix()

        final_ss_rel = copy_real(str(valid_real_final) if valid_real_final else '', 'Screenshots', 'final-screenshot.png')
        video_rel = copy_real(real_video_path, 'Recording', 'video.webm')
        trace_rel = copy_real(real_trace_path, 'Trace', 'trace.zip')

        return {
            "plan_rel_path": plan_rel_path,
            "plan_filename": plan_filename,
            "plan_markdown": plan_md,
            "step_screenshots": step_screenshots,
            "final_screenshot": final_ss_rel,
            "video_rel_path": video_rel,
            "trace_rel_path": trace_rel,
        }

    @staticmethod
    def render_html_report(summary: Dict[str, Any]) -> str:
        """Render 100% self-contained index.html matching Complete-Suite-Test-Report layout."""
        report_title = html.escape(summary.get("report_title", "Detailed Test Evidence Report"))
        total = summary.get("total", 0)
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        flaky = summary.get("flaky", 0)
        skipped = summary.get("skipped", 0)
        pass_rate = summary.get("pass_rate_pct", 100.0)
        duration_s = summary.get("duration_s", 0.0)
        date_str = html.escape(str(summary.get("date", "")))
        browser = html.escape(str(summary.get("browser", "Edge")))
        profile = html.escape(str(summary.get("profile", "PUBLIC")))
        test_cases: List[Dict[str, Any]] = summary.get("test_cases", [])

        cards_html: List[str] = []
        for idx, tc in enumerate(test_cases):
            card_id = f"test-{idx}"
            status = (tc.get("status") or "not_run").lower()
            status_cls = status if status in ("passed", "failed", "skipped", "not_run", "flaky") else "not_run"
            status_badge = status.upper()
            tc_id = html.escape(str(tc.get("test_id", f"TC-{idx+1:03d}")))
            tc_title = html.escape(str(tc.get("title", "")))
            tc_dur = f"{float(tc.get('duration_s', 1.5)):.2f}s"
            tc_profile = html.escape(str(tc.get("profile", profile)))
            tc_module = html.escape(str(tc.get("module", "Core")))
            tc_plan_rel = html.escape(str(tc.get("plan_rel_path", "")))
            tc_plan_name = html.escape(str(tc.get("plan_filename", "")))
            tc_spec = html.escape(str(tc.get("spec_path", "")))
            tc_purpose = html.escape(str(tc.get("purpose", "")))
            tc_expected = html.escape(str(tc.get("expected_result", "")))

            steps_li = "".join(f"<li>{html.escape(str(s))}</li>" for s in (tc.get("steps") or []))

            raw_plan_md = str(tc.get("plan_markdown", ""))
            plan_html_lines = "<br>".join(html.escape(line) for line in raw_plan_md.splitlines())

            ss_items_html = []
            for ss in tc.get("step_screenshots") or []:
                rel = html.escape(str(ss.get("rel_path", "")))
                cap = html.escape(str(ss.get("caption", "")))
                ss_items_html.append(
                    f"""<div class="ss-item">
        <a href="{rel}" target="_blank" rel="noopener">
          <img src="{rel}" alt="{cap}" loading="lazy">
        </a>
        <span>{cap}</span>
      </div>"""
                )
            ss_grid_block = (
                f'<div class="screenshots"><h4>Step Screenshots</h4><div class="ss-grid">{"".join(ss_items_html)}</div></div>'
                if ss_items_html
                else ""
            )

            final_ss_rel = html.escape(str(tc.get("final_screenshot", "")))
            final_ss_block = (
                f'<div class="final-ss"><h4>Final Screenshot</h4><a href="{final_ss_rel}" target="_blank" rel="noopener"><img src="{final_ss_rel}" alt="Final state" loading="lazy" style="max-width:640px"></a></div>'
                if final_ss_rel
                else ""
            )

            video_rel = html.escape(str(tc.get("video_rel_path", "")))
            video_block = (
                f"""<div class="video-container">
      <h4>Screen Recording</h4>
      <video controls preload="metadata" style="width:100%;max-width:640px">
        <source src="{video_rel}" type="video/webm">
        Video playback is not supported by this browser.
      </video>
      <p><a href="{video_rel}" download>Download video</a></p>
    </div>"""
                if video_rel
                else ""
            )

            api_method = html.escape(str(tc.get("api_method", "GET")))
            api_pathname = html.escape(str(tc.get("api_pathname", "/")))
            api_status = html.escape(str(tc.get("api_status", 200)))
            api_trigger = html.escape(str(tc.get("api_trigger", "Page navigation")))

            extra_apis_rows = []
            for a in (tc.get("captured_apis") or [])[:8]:
                m = html.escape(str(a.get("method", "GET")))
                u = html.escape(urlparse(str(a.get("url", ""))).path or str(a.get("url", "")))
                st_code = html.escape(str(a.get("status_code", 200)))
                trig = html.escape(str(a.get("triggered_by_action", "page_load")))
                extra_apis_rows.append(
                    f"<tr><td><code>{m}</code></td><td><code>{u}</code></td><td><strong>{st_code}</strong></td><td>{trig}</td></tr>"
                )
            api_table_html = (
                f'<table class="api-table"><thead><tr><th>Method</th><th>Endpoint</th><th>Status</th><th>Trigger</th></tr></thead><tbody>{"".join(extra_apis_rows)}</tbody></table>'
                if extra_apis_rows
                else ""
            )

            trace_rel = html.escape(str(tc.get("trace_rel_path", "")))
            trace_block = (
                f"""<div class="trace-section">
      <h4>Trace</h4>
      <p>Raw trace available for download: <a href="{trace_rel}" download>trace.zip</a></p>
    </div>"""
                if trace_rel
                else ""
            )

            actual_dur = f"{float(tc.get('actual_duration_s', tc.get('duration_s', 1.2))):.2f}s"
            final_route = html.escape(str(tc.get("final_route", "/")))
            err_msg = str(tc.get("error_message", "")).strip()
            err_block = f'<div class="errors"><h4>Failure Details</h4><pre>{html.escape(err_msg)}</pre></div>' if err_msg else ""
            auth = tc.get('auth_diagnostics', {})
            auth_block = ('<div class="auth-diagnostics"><h4>Authentication and session diagnostics</h4><pre>' + html.escape(json.dumps(auth, indent=2)) + '</pre></div>') if auth else ''

            cards_html.append(
                f"""  <div class="test-card {status_cls}" id="{card_id}" data-status="{status_cls}">
    <div class="test-header" onclick="toggleExpand('{card_id}')">
      <div class="test-card-heading">
        <span class="test-id-col">{tc_id}</span>
        <span class="test-title-col">{tc_title}</span>
      </div>
      <span class="test-status {status_cls}">{status_badge}</span>
      <span class="test-duration">{tc_dur}</span>
      <span class="expand-icon">▼</span>
    </div>
    <div class="test-body">
      <div class="test-meta">
        <span><strong>Profile:</strong> {tc_profile}</span>
        <span><strong>Module:</strong> {tc_module}</span>
        <span><strong>Plan:</strong> {tc_plan_rel}</span>
      </div>
      <div class="steps"><h4>Test Steps</h4><ol>{steps_li}</ol></div>
      <div class="test-summary"><h2>Test: {tc_id}</h2><p><strong>Module:</strong> {tc_module}<br><strong>Access Profile:</strong> {tc_profile}<br><strong>Spec:</strong> {tc_spec}<br><strong>Plan:</strong> {tc_plan_name}</p><p><h3>Purpose</h3><br>{tc_purpose}</p><p><h3>Preconditions</h3><br><li><code>${{BASE_URL}}</code> is reachable.</li><li>Credentials for <code>${{TEST_ACCESS_PROFILE}}</code> are configured.</li></p><p><h3>Expected Result</h3><br>{tc_expected}</p></div>
      <div class="test-plan">
        <h4>Test Plan</h4>
        <p>{plan_html_lines}</p>
      </div>
      {ss_grid_block or "<p>No step screenshots captured for this scenario.</p>"}
      {final_ss_block}
      {video_block or "<p>No recording available for this scenario.</p>"}
      <div class="api-summary"><h4>API / Navigation Summary</h4><h2>API / Navigation Summary</h2><p><strong>Method:</strong> {api_method}<br><strong>Pathname:</strong> {api_pathname}<br><strong>Status:</strong> {api_status}<br><strong>Trigger:</strong> {api_trigger}</p>{api_table_html}</div>
      {trace_block or "<p>No trace captured for this scenario.</p>"}
      <div class="actual-result"><h4>Actual Result</h4><h2>Actual Result</h2><p><strong>Status:</strong> {status}<br><strong>Duration:</strong> {actual_dur}<br><strong>Final Route:</strong> {final_route}</p><p>{"All assertions completed successfully." if status == "passed" else ("One or more steps failed; remaining steps were skipped." if status == "failed" else "This scenario has not been executed.")}</p></div>
      {err_block}
      {auth_block}
    </div>
  </div>"""
            )

        cards_joined = "\n\n".join(cards_html)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{report_title}</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{ width: 100%; max-width: 100%; margin: 0; overflow-x: hidden; }}
body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f5f5; color: #333; line-height: 1.6; }}

.report-header {{ width: 100%; max-width: 100%; min-width: 0; background: #1a1a2e; color: #fff; padding: 24px; }}
.report-header h1 {{ margin: 0; max-width: 100%; white-space: normal; overflow-wrap: anywhere; word-break: normal; font-size: 1.4em; }}

.summary-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(130px, 1fr)); gap: 16px; width: 100%; margin-top: 16px; }}
.summary-card {{ min-width: 0; max-width: 100%; overflow: hidden; background: rgba(255,255,255,0.1); border-radius: 8px; padding: 12px; text-align: center; }}
.summary-card .summary-value {{ max-width: 100%; white-space: normal; overflow-wrap: anywhere; word-break: break-word; text-align: center; line-height: 1.2; font-size: 1.6em; font-weight: bold; }}
.summary-card.profile .summary-value {{ font-size: clamp(15px, 1.8vw, 24px); }}
.summary-card .summary-label {{ font-size: 0.75em; opacity: 0.8; margin-top: 4px; }}
.summary-card.passed .summary-value {{ color: #4caf50; }}
.summary-card.failed .summary-value {{ color: #f44336; }}

.filter-bar {{ display: flex; flex-wrap: wrap; gap: 10px; align-items: center; justify-content: space-between; margin-bottom: 16px; background: #fff; padding: 12px 16px; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.08); }}
.filter-btns {{ display: flex; gap: 8px; }}
.filter-btn {{ border: 1px solid #d0d7de; background: #f6f8fa; color: #24292f; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-size: 0.85em; font-weight: 600; }}
.filter-btn.active {{ background: #1a1a2e; color: #fff; border-color: #1a1a2e; }}
.search-input {{ padding: 6px 12px; border: 1px solid #d0d7de; border-radius: 6px; font-size: 0.85em; min-width: 240px; }}

.container {{ max-width: 1100px; margin: 0 auto; padding: 24px 16px; }}

.test-card {{ background: #fff; border-radius: 8px; margin-bottom: 12px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); overflow: hidden; }}
.test-card.failed {{ border-left: 4px solid #f44336; }}
.test-card.passed {{ border-left: 4px solid #4caf50; }}

.test-card-heading {{ display: grid; grid-template-columns: minmax(150px, auto) minmax(0, 1fr); align-items: start; gap: 16px; flex: 1; }}
.test-id-col {{ font-family: monospace; font-weight: 700; white-space: nowrap; }}
.test-title-col {{ min-width: 0; white-space: normal; overflow-wrap: anywhere; }}

.test-header {{ display: flex; align-items: center; padding: 12px 16px; cursor: pointer; gap: 12px; user-select: none; }}
.test-header:hover {{ background: #f0f0f0; }}
.test-status {{ padding: 2px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold; white-space: nowrap; }}
.test-status.passed {{ background: #e8f5e9; color: #2e7d32; }}
.test-status.not_run, .test-status.skipped {{ background: #fff3cd; color: #856404; }}
.test-status.failed {{ background: #ffebee; color: #c62828; }}
.test-duration {{ color: #666; font-size: 0.85em; min-width: 60px; text-align: right; white-space: nowrap; }}
.expand-icon {{ transition: transform 0.2s; }}
.test-card.expanded .expand-icon {{ transform: rotate(180deg); }}
.test-body {{ display: none; padding: 0 16px 16px; }}
.test-card.expanded .test-body {{ display: block; }}

.test-meta {{ display: flex; flex-wrap: wrap; gap: 24px; margin-bottom: 12px; font-size: 0.9em; color: #555; }}
.steps {{ margin: 12px 0; }}
.steps ol {{ padding-left: 24px; }}
.screenshots {{ margin: 16px 0; }}
.ss-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 12px; }}
.ss-item {{ text-align: center; min-width: 0; }}
.ss-item img {{ width: 100%; border-radius: 4px; border: 1px solid #ddd; cursor: pointer; transition: transform 0.15s; }}
.ss-item img:hover {{ transform: scale(1.02); }}
.ss-item span {{ display: block; font-size: 0.8em; color: #666; margin-top: 4px; overflow-wrap: anywhere; }}
.video-container {{ margin: 16px 0; }}
.trace-section, .api-summary, .test-plan, .actual-result, .test-summary {{ margin: 16px 0; overflow-wrap: anywhere; }}
.final-ss {{ margin: 16px 0; }}
.final-ss img {{ border-radius: 4px; border: 1px solid #ddd; max-width: 100%; }}
.errors {{ background: #fff3e0; border: 1px solid #ff9800; border-radius: 4px; padding: 12px; margin: 16px 0; }}
.errors pre {{ font-size: 0.85em; overflow-x: auto; white-space: pre-wrap; word-break: break-word; }}
.api-table {{ width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 0.88em; }}
.api-table th, .api-table td {{ border: 1px solid #e0e0e0; padding: 6px 10px; text-align: left; }}
.api-table th {{ background: #f4f6f8; }}
h3 {{ font-size: 1.1em; margin: 12px 0 6px; border-bottom: 1px solid #eee; padding-bottom: 4px; }}
h4 {{ font-size: 1em; margin: 10px 0 4px; color: #555; }}
code {{ background: #f4f4f4; padding: 1px 4px; border-radius: 3px; font-size: 0.9em; white-space: pre-wrap; word-break: break-word; }}
pre {{ background: #f4f4f4; padding: 8px; border-radius: 4px; font-size: 0.85em; overflow-x: auto; white-space: pre-wrap; word-break: break-word; }}
p {{ margin: 4px 0; }}
a {{ color: #1976d2; }}

@media (max-width: 700px) {{
  .test-card-heading {{ grid-template-columns: 1fr; gap: 6px; }}
  .test-header {{ flex-wrap: wrap; }}
  .summary-grid {{ grid-template-columns: repeat(3, 1fr); }}
}}
</style>
</head>
<body>
<div class="report-header">
  <h1>{report_title}</h1>
  <div class="summary-grid">
    <div class="summary-card"><div class="summary-value">{total}</div><div class="summary-label">Total</div></div>
    <div class="summary-card passed"><div class="summary-value">{passed}</div><div class="summary-label">Passed</div></div>
    <div class="summary-card failed"><div class="summary-value">{failed}</div><div class="summary-label">Failed</div></div>
    <div class="summary-card"><div class="summary-value">{flaky}</div><div class="summary-label">Flaky</div></div>
    <div class="summary-card"><div class="summary-value">{skipped}</div><div class="summary-label">Not run / Skipped</div></div>
    <div class="summary-card passed"><div class="summary-value">{pass_rate}%</div><div class="summary-label">Pass Rate</div></div>
    <div class="summary-card"><div class="summary-value">{duration_s:.2f}s</div><div class="summary-label">Duration</div></div>
    <div class="summary-card"><div class="summary-value">{date_str}</div><div class="summary-label">Date</div></div>
    <div class="summary-card"><div class="summary-value">{browser}</div><div class="summary-label">Browser</div></div>
    <div class="summary-card profile"><div class="summary-value">{profile}</div><div class="summary-label">Profile</div></div>
  </div>
</div>
<div class="container">
  <div class="filter-bar">
    <div class="filter-btns">
      <button class="filter-btn active" onclick="filterCards('all', this)">All ({total})</button>
      <button class="filter-btn" onclick="filterCards('passed', this)">Passed ({passed})</button>
      <button class="filter-btn" onclick="filterCards('failed', this)">Failed ({failed})</button>
      <button class="filter-btn" onclick="filterCards('not_run', this)">Not run</button>
    </div>
    <input type="text" id="card-search" class="search-input" placeholder="Filter by Test ID or Title..." oninput="searchCards(this.value)">
  </div>

{cards_joined}
</div>
<script>
function toggleExpand(id) {{
  document.getElementById(id).classList.toggle('expanded');
}}
function filterCards(status, btn) {{
  window.reportStatus = status;
  document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
  if (btn) btn.classList.add('active');
  searchCards(document.getElementById('card-search').value);
}}
function searchCards(query) {{
  const q = (query || '').toLowerCase();
  document.querySelectorAll('.test-card').forEach(card => {{
    const text = card.innerText.toLowerCase();
    const status = window.reportStatus || 'all';
    card.style.display = text.includes(q) && (status === 'all' || card.dataset.status === status) ? '' : 'none';
  }});
}}
</script>
</body>
</html>"""
