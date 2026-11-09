"""Phase 1 end-to-end verification CLI.

Default mode (100% offline): spins up a local fixture web app on 127.0.0.1 that
exposes a realistic SPA (search box, tabs, data-testid elements, duplicate links)
plus JSON APIs returning 200/201/204/400/401/403/404/500. The BrowserInspector is
run against it and the report is asserted strictly.

Custom mode:  python test_phase1.py --url https://your.app --flow "Search for 'x' then open Dashboard"
(only generic structural checks are applied to arbitrary URLs).
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Dict, List, Tuple
from urllib.parse import parse_qs, urlparse

from core.browser_inspector import BrowserInspector
from core.models import SUPPORTED_LANGUAGES, InspectionReport

ROOT = Path(__file__).resolve().parent
DEFAULT_FLOW = (
    'Search for "playwright", open the "Dashboard" tab, then check the Reports tab. '
    'Verify the "Delete Account" button is visible but never click it.'
)

# ---------------------------------------------------------------------------
# Offline fixture application
# ---------------------------------------------------------------------------
FIXTURE_HTML = """<!doctype html>
<html lang="en">
<head><meta charset="utf-8"><title>Acme QA Portal</title>
<style>
  body { font-family: Segoe UI, sans-serif; margin: 24px; }
  [role=tabpanel] { border: 1px solid #ccc; padding: 12px; margin-top: 8px; }
  .hidden { display: none; }
</style></head>
<body>
  <header>
    <nav aria-label="Main">
      <a href="#home">Home</a>
      <a href="#docs">Docs</a>
      <a href="https://example.org/external" target="_blank">External</a>
    </nav>
    <form role="search" id="search-form" onsubmit="event.preventDefault(); runSearch(true);">
      <input type="search" id="global-search" placeholder="Search products" aria-label="Search">
      <button type="submit" data-testid="search-submit">Go</button>
    </form>
  </header>

  <main>
    <h1>Welcome back</h1>
    <div role="tablist" aria-label="Sections">
      <button role="tab" aria-selected="true" onclick="showTab('overview')">Overview</button>
      <button role="tab" onclick="showTab('dashboard')">Dashboard</button>
      <button role="tab" onclick="showTab('reports')">Reports</button>
    </div>
    <section role="tabpanel" id="panel">Overview content</section>

    <form id="profile" method="post" action="/profile" onsubmit="event.preventDefault();">
      <label>Email <input type="email" name="email"></label>
      <input name="coupon" placeholder="Coupon code">
      <select name="country"><option>India</option><option>USA</option></select>
      <textarea name="notes"></textarea>
      <button type="submit">Save profile</button>
    </form>

    <div class="cards">
      <div class="card"><p>Card A</p><a href="#a">Learn more</a></div>
      <div class="card"><p>Card B</p><a href="#b">Learn more</a></div>
    </div>

    <div role="button" tabindex="0" data-testid="help-widget">Help</div>
    <span id="react-12345">dynamic</span>
    <button class="hidden">Hidden button</button>
    <button data-testid="delete-account" class="danger" onclick="deleteAccount()">Delete Account</button>
  </main>

<script>
  const api = (url, opts) => fetch(url, opts).catch(() => null);
  const json = (method, body) => ({ method, headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) });

  // ---- page-load traffic covering many status codes ----
  api('/api/user');
  api('/api/feature-flags');
  api('/api/legacy-endpoint');
  api('/api/admin/settings');
  api('/api/validate', json('POST', { email: 'not-an-email', terms: false }));
  api('/api/preferences', json('PUT', { theme: 'dark', locale: 'en-IN' }));
  const xhr = new XMLHttpRequest(); xhr.open('GET', '/api/config'); xhr.send();

  // ---- search (debounced type-ahead + submit) ----
  let t = null;
  document.getElementById('global-search').addEventListener('input', () => {
    clearTimeout(t); t = setTimeout(() => runSearch(false), 250);
  });
  function runSearch(submitted) {
    const q = document.getElementById('global-search').value;
    api('/api/search?q=' + encodeURIComponent(q) + (submitted ? '&submit=1' : ''));
  }

  // ---- tabs ----
  function showTab(name) {
    document.getElementById('panel').textContent = name + ' content';
    if (name === 'dashboard') {
      api('/api/dashboard');
      api('/api/events', json('POST', { event: 'tab_view', tab: 'dashboard', ts: Date.now() }));
    }
    if (name === 'reports') api('/api/reports');
  }

  // ---- destructive action (must NEVER be triggered by probes) ----
  function deleteAccount() {
    if (confirm('Really delete?')) api('/api/account', { method: 'DELETE' });
    else api('/api/account', { method: 'DELETE' });  // fires even if dialog dismissed
  }
</script>
</body></html>
"""

ROUTES: Dict[Tuple[str, str], Tuple[int, object]] = {
    ("GET", "/api/user"): (200, {"id": 7, "name": "QA Lead", "roles": ["admin"], "email": "qa@acme.test"}),
    ("GET", "/api/feature-flags"): (401, {"error": "unauthorized", "code": 401}),
    ("GET", "/api/legacy-endpoint"): (404, {"error": "not_found", "path": "/api/legacy-endpoint"}),
    ("GET", "/api/admin/settings"): (403, {"error": "forbidden", "requiredRole": "superadmin"}),
    ("POST", "/api/validate"): (400, {"error": "validation_failed", "fields": {"email": "invalid"}}),
    ("PUT", "/api/preferences"): (204, None),
    ("GET", "/api/config"): (200, [{"key": "pageSize", "value": 20}]),
    ("GET", "/api/dashboard"): (200, {"widgets": [{"id": 1}], "updatedAt": "2026-11-09T00:00:00Z", "owner": "qa"}),
    ("POST", "/api/events"): (201, {"eventId": "evt-001", "status": "created"}),
    ("GET", "/api/reports"): (500, {"error": "internal_server_error", "traceId": "abc123"}),
    ("DELETE", "/api/account"): (204, None),
}


class FixtureHandler(BaseHTTPRequestHandler):
    hits: List[Tuple[str, str]] = []

    def log_message(self, *args) -> None:  # keep terminal clean
        pass

    def _send(self, status: int, body: object, content_type: str = "application/json") -> None:
        payload = b"" if body is None else (body if isinstance(body, bytes) else json.dumps(body).encode())
        self.send_response(status)
        if body is not None:
            self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        if payload:
            self.wfile.write(payload)

    def _handle(self) -> None:
        parsed = urlparse(self.path)
        length = int(self.headers.get("Content-Length") or 0)
        if length:
            self.rfile.read(length)
        FixtureHandler.hits.append((self.command, parsed.path))
        if self.command == "GET" and parsed.path in ("/", "/index.html"):
            return self._send(200, FIXTURE_HTML.encode("utf-8"), "text/html; charset=utf-8")
        if self.command == "GET" and parsed.path == "/api/search":
            q = parse_qs(parsed.query).get("q", [""])[0]
            return self._send(200, {"query": q, "results": [{"sku": "PW-1", "title": f"{q} handbook"}], "total": 1})
        status, body = ROUTES.get((self.command, parsed.path), (404, {"error": "no_route"}))
        self._send(status, body)

    do_GET = do_POST = do_PUT = do_DELETE = do_PATCH = _handle


def start_fixture_server() -> Tuple[ThreadingHTTPServer, str]:
    server = ThreadingHTTPServer(("127.0.0.1", 0), FixtureHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    return server, f"http://127.0.0.1:{server.server_address[1]}/"


# ---------------------------------------------------------------------------
# Progress printing
# ---------------------------------------------------------------------------
_seen_milestones: List[float] = []


def print_progress(node_name: str, percent: float, message: str) -> None:
    _seen_milestones.append(percent)
    filled = int(percent / 2.5)  # 40-char bar for 0..100
    bar = "#" * filled + "-" * (40 - filled)
    print(f"  [{bar}] {percent:5.1f}%  {node_name:<20} {message}", flush=True)


# ---------------------------------------------------------------------------
# Verification
# ---------------------------------------------------------------------------
class Checker:
    def __init__(self) -> None:
        self.failures: List[str] = []
        self.passed = 0

    def check(self, condition: bool, description: str) -> None:
        if condition:
            self.passed += 1
            print(f"  [PASS] {description}")
        else:
            self.failures.append(description)
            print(f"  [FAIL] {description}")


def generic_checks(c: Checker, report: InspectionReport) -> None:
    c.check(report.browser_channel in ("chrome", "msedge", "chromium"), f"Browser launched (channel={report.browser_channel})")
    c.check(bool(report.page_title), f"Page title captured: {report.page_title!r}")
    c.check(len(report.elements) > 0, f"{len(report.elements)} interactive elements extracted")
    c.check(
        all(set(e.recommended_locator) == set(SUPPORTED_LANGUAGES) and all(e.recommended_locator.values()) for e in report.elements),
        "Every element has python/java/ts/js locators",
    )
    c.check(len({e.element_id for e in report.elements}) == len(report.elements), "Element ids are unique")
    c.check(bool(report.aria_snapshot.strip()), f"ARIA snapshot captured ({len(report.aria_snapshot)} chars)")
    c.check(all(a.resource_type in ("xhr", "fetch") for a in report.captured_apis), "Only xhr/fetch traffic captured")
    for pct in (5, 15, 25, 35, 45):
        c.check(pct in _seen_milestones, f"Progress milestone {pct}% reported")


def fixture_checks(c: Checker, report: InspectionReport) -> None:
    by_name = {e.text_or_label: e for e in report.elements}
    apis = report.captured_apis

    # --- locator priority ---
    go = next((e for e in report.elements if e.attributes.get("data-testid") == "search-submit"), None)
    c.check(go is not None and go.locator_strategy == "data-testid", "data-testid wins over role/text (search-submit)")
    if go:
        c.check(go.recommended_locator["python"] == 'page.get_by_test_id("search-submit")', "Python testid syntax")
        c.check(go.recommended_locator["java"] == 'page.getByTestId("search-submit")', "Java testid syntax")
        c.check(go.recommended_locator["ts"] == "page.getByTestId('search-submit')", "TS testid syntax")
        c.check(go.recommended_locator["js"] == "page.getByTestId('search-submit')", "JS testid syntax")
    search = next((e for e in report.elements if e.attributes.get("id") == "global-search"), None)
    c.check(search is not None and search.locator_strategy == "id"
            and search.recommended_locator["python"] == 'page.locator("#global-search")', "id strategy for search input")
    dash = by_name.get("Dashboard")
    c.check(dash is not None and dash.locator_strategy == "role", "role+name strategy for Dashboard tab")
    if dash:
        c.check(dash.recommended_locator["python"] == 'page.get_by_role("tab", name="Dashboard", exact=True)', "Python role syntax")
        c.check(dash.recommended_locator["java"]
                == 'page.getByRole(AriaRole.TAB, new Page.GetByRoleOptions().setName("Dashboard").setExact(true))', "Java role syntax")
        c.check(dash.recommended_locator["ts"] == "page.getByRole('tab', { name: 'Dashboard', exact: true })", "TS role syntax")
    learn = [e for e in report.elements if e.text_or_label == "Learn more"]
    c.check(len(learn) == 2 and all(e.locator_strategy == "css" for e in learn)
            and learn[0].recommended_locator["python"] != learn[1].recommended_locator["python"],
            "Duplicate 'Learn more' links fall back to distinct CSS locators")
    c.check("Hidden button" not in by_name, "Hidden elements are excluded")
    c.check(all("data-pw-agent-eid" not in e.attributes for e in report.elements), "Internal marker attribute not leaked")
    strategies = {e.locator_strategy for e in report.elements}
    c.check({"data-testid", "id", "role", "css"} <= strategies, f"Multiple strategies in use: {sorted(strategies)}")

    # --- network telemetry ---
    statuses = {a.status_code for a in apis}
    expected = {200, 201, 204, 400, 401, 403, 404, 500}
    c.check(expected <= statuses, f"Status codes captured {sorted(statuses)} include {sorted(expected)}")
    user = next((a for a in apis if a.url.endswith("/api/user")), None)
    c.check(user is not None and user.response_keys == ["id", "name", "roles", "email"] and user.triggered_by_action == "page_load",
            "GET /api/user -> 200 with top-level JSON keys, tagged page_load")
    val = next((a for a in apis if a.url.endswith("/api/validate")), None)
    c.check(val is not None and val.method == "POST" and val.status_code == 400 and val.request_payload_keys == ["email", "terms"],
            "POST /api/validate -> 400 with request payload keys")
    c.check(any(a.url.endswith("/api/config") and a.resource_type == "xhr" for a in apis), "XMLHttpRequest traffic captured")

    search_calls = [a for a in apis if "/api/search" in a.url]
    c.check(bool(search_calls) and all("probe:search" in a.triggered_by_action for a in search_calls)
            and any("q=playwright" in a.url for a in search_calls), "Search probe typed 'playwright' and captured /api/search")
    events = next((a for a in apis if a.url.endswith("/api/events")), None)
    c.check(events is not None and events.status_code == 201 and "Dashboard" in events.triggered_by_action
            and events.request_payload_keys == ["event", "tab", "ts"] and events.response_keys == ["eventId", "status"],
            "Dashboard tab probe -> POST /api/events 201 tagged with action")
    reports = next((a for a in apis if a.url.endswith("/api/reports")), None)
    c.check(reports is not None and reports.status_code == 500 and "Reports" in reports.triggered_by_action,
            "Reports tab probe (unquoted keyword) -> 500 captured")
    c.check(("DELETE", "/api/account") not in FixtureHandler.hits and not any(a.method == "DELETE" for a in apis),
            "Destructive 'Delete Account' was NEVER clicked")
    c.check(not any(("POST", "/profile") == h for h in FixtureHandler.hits), "POST form was never submitted")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
async def run(args: argparse.Namespace) -> int:
    server = None
    url = args.url
    if not url:
        server, url = start_fixture_server()
        print(f"Offline fixture app running at {url}")

    print(f"\nInspecting: {url}\nFlow     : {args.flow}\n")
    started = time.perf_counter()
    try:
        report = await BrowserInspector().inspect_url(url, args.flow, headless=not args.headed, progress_callback=print_progress)
    finally:
        if server:
            server.shutdown()
    elapsed = time.perf_counter() - started

    output = Path(args.output)
    output.write_text(report.model_dump_json(indent=2), encoding="utf-8")

    print(f"\nInspection finished in {elapsed:.1f}s  ->  {output}")
    print(f"Browser: {report.browser_channel} | Elements: {len(report.elements)} | APIs: {len(report.captured_apis)}")
    print("\nProbes executed:")
    for p in report.probes_executed or ["(none)"]:
        print(f"  - {p}")
    print("\nCaptured APIs:")
    for a in report.captured_apis:
        print(f"  {a.status_code:>3} {a.method:<6} {urlparse(a.url).path:<26} keys={a.response_keys} <- {a.triggered_by_action}")
    print("\nSample locators:")
    for e in report.elements[:6]:
        print(f"  {e.element_id:<4} {e.tag:<8} [{e.locator_strategy}] {e.text_or_label[:30]!r}")
        for lang in SUPPORTED_LANGUAGES:
            print(f"        {lang:<6} {e.recommended_locator[lang]}")

    print("\nVerification:")
    checker = Checker()
    generic_checks(checker, report)
    if not args.url:
        fixture_checks(checker, report)
    print(f"\nRESULT: {checker.passed} passed, {len(checker.failures)} failed")
    if checker.failures:
        print("FAILED CHECKS:\n  - " + "\n  - ".join(checker.failures))
        return 1
    print("PHASE 1 VERIFICATION PASSED")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Phase 1 BrowserInspector verification")
    parser.add_argument("--url", help="Inspect this URL instead of the built-in offline fixture app")
    parser.add_argument("--flow", default=DEFAULT_FLOW, help="Free-text user flow used for safe probing")
    parser.add_argument("--headed", action="store_true", help="Show the browser window")
    parser.add_argument("--output", default=str(ROOT / "phase1_output.json"), help="Report output path")
    return asyncio.run(run(parser.parse_args()))


if __name__ == "__main__":
    sys.exit(main())

