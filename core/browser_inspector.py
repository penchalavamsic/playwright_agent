"""Async Playwright DOM & Network Telemetry Engine (Phase 1).

100% offline and deterministic:
  * No LLM / cloud APIs - flow understanding is keyword based.
  * Uses the corporate machine's pre-installed Chrome (``channel="chrome"``) or
    Edge (``channel="msedge"``), falling back to Playwright's bundled Chromium
    only if neither is available. This keeps a PyInstaller ``.exe`` working
    without downloading browser binaries.
"""

from __future__ import annotations

import asyncio
import inspect
import itertools
import json
import logging
import re
from typing import Any, Awaitable, Callable, Dict, List, Optional, Sequence, Tuple, Union
from urllib.parse import urldefrag, urlparse

from playwright.async_api import (
    Browser,
    BrowserContext,
    Locator,
    Page,
    Playwright,
    Request,
    Response,
    async_playwright,
)

from core.models import CapturedAPI, DOMElement, InspectionReport

logger = logging.getLogger(__name__)

ProgressCallback = Callable[[str, float, str], Union[None, Awaitable[None]]]

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Browser channels tried in order. ``None`` == Playwright's bundled Chromium.
DEFAULT_CHANNELS: Tuple[Optional[str], ...] = ("chrome", "msedge", None)

INTERACTIVE_SELECTOR = ", ".join(
    [
        "button",
        "input",
        "select",
        "textarea",
        "a",
        '[role="button"]',
        '[role="tab"]',
        "[data-testid]",
    ]
)

#: Temporary attribute used to prove a candidate locator resolves to *exactly* our element.
MARKER_ATTR = "data-pw-agent-eid"

#: Auto-generated / unstable ids that must never be used as locators.
DYNAMIC_ID_PATTERN = (
    r"^(?::r[0-9a-z]*:|react-|ember\d+|mui-\d+|radix-|headlessui-|ext-gen|yui_|gwt-uid|j_idt)"
    r"|\d{4,}|[0-9a-f]{8}-[0-9a-f]{4}"
)

#: ARIA roles that ``get_by_role`` can meaningfully target with an accessible name.
NAMEABLE_ROLES = frozenset(
    {
        "button", "checkbox", "combobox", "link", "listbox", "menuitem", "menuitemcheckbox",
        "menuitemradio", "option", "radio", "searchbox", "slider", "spinbutton", "switch",
        "tab", "textbox", "treeitem", "gridcell", "cell", "row", "heading", "img", "dialog",
        "navigation", "region", "tabpanel", "progressbar", "scrollbar", "separator",
    }
)

FORM_CONTROL_TAGS = frozenset({"input", "select", "textarea"})
CLICKABLE_ROLES = frozenset({"button", "tab", "link", "menuitem", "treeitem", "option", "switch"})

#: Anything matching this is NEVER clicked by a probe (non-destructive guarantee).
DESTRUCTIVE_PATTERN = re.compile(
    r"\b(delete|remove|destroy|drop|erase|purge|wipe|trash|log\s?out|sign\s?out|log\s?off|"
    r"unsubscribe|deactivate|disable|terminate|cancel|reset|pay|payment|purchase|buy|checkout|"
    r"check\s?out|order|transfer|send|submit|confirm|approve|reject|publish|deploy|archive|"
    r"revoke|ban|block|kill|shutdown|restart|format|uninstall|save|update|create|upload|"
    r"import|sync|merge|close\s+account)\b",
    re.IGNORECASE,
)

SEARCH_INTENT_PATTERN = re.compile(r"\b(search|find|look\s?up|filter|query)\b", re.IGNORECASE)
SEARCH_FIELD_HINT = re.compile(r"search|query|find|filter|keyword|\bq\b", re.IGNORECASE)

STOPWORDS = frozenset(
    """a an the and or then than to of on in into onto at by for from with without as is are be
    been was were it its this that these those there here i we you user users should must can
    will would could click clicks clicking tap press open opens opening go goes navigate
    navigates visit visits load loads view views see sees check checks verify verifies validate
    ensure assert make sure page pages screen button buttons tab tabs link links field fields
    input inputs enter enters type types select selects choose fill fills value text after
    before when while until wait waits shown visible display displayed appears appear exists
    present also next first last some any all each every new search searches find filter query
    look lookup results result not dont don't do does""".split()
)

EXTRACT_ELEMENTS_JS = r"""
(args) => {
  const { selector, maxElements, marker, dynamicIdPattern } = args;
  const dynId = new RegExp(dynamicIdPattern, 'i');
  const norm = (s) => (s || '').replace(/\s+/g, ' ').trim();
  const q = (v) => String(v).replace(/\\/g, '\\\\').replace(/"/g, '\\"');
  const unique = (sel) => { try { return document.querySelectorAll(sel).length === 1; } catch (e) { return false; } };

  const visible = (el) => {
    if (typeof el.checkVisibility === 'function' &&
        !el.checkVisibility({ checkOpacity: false, checkVisibilityCSS: true })) return false;
    const st = getComputedStyle(el);
    if (st.display === 'none' || st.visibility === 'hidden' || st.visibility === 'collapse') return false;
    const r = el.getBoundingClientRect();
    return r.width > 0 && r.height > 0;
  };

  const implicitRole = (el) => {
    const tag = el.tagName.toLowerCase();
    const type = (el.getAttribute('type') || '').toLowerCase();
    switch (tag) {
      case 'a': case 'area': return el.hasAttribute('href') ? 'link' : '';
      case 'button': return 'button';
      case 'select': return (el.multiple || el.size > 1) ? 'listbox' : 'combobox';
      case 'textarea': return 'textbox';
      case 'input':
        if (['button', 'submit', 'reset', 'image'].includes(type)) return 'button';
        if (type === 'checkbox') return 'checkbox';
        if (type === 'radio') return 'radio';
        if (type === 'range') return 'slider';
        if (type === 'number') return 'spinbutton';
        if (type === 'search') return el.hasAttribute('list') ? 'combobox' : 'searchbox';
        if (['', 'text', 'email', 'tel', 'url'].includes(type)) return el.hasAttribute('list') ? 'combobox' : 'textbox';
        return '';
      default: return '';
    }
  };

  const textOfId = (id) => { const n = document.getElementById(id); return n ? norm(n.innerText || n.textContent) : ''; };
  const labelText = (el) => {
    const lb = el.getAttribute('aria-labelledby');
    if (lb) { const t = norm(lb.split(/\s+/).map(textOfId).join(' ')); if (t) return t; }
    const al = norm(el.getAttribute('aria-label')); if (al) return al;
    if (el.labels && el.labels.length) {
      const t = norm([...el.labels].map((l) => l.innerText || l.textContent).join(' '));
      if (t) return t;
    }
    return '';
  };
  const accName = (el, tag, type) => {
    const lt = labelText(el); if (lt) return lt;
    if (tag === 'input') {
      if (['button', 'submit', 'reset'].includes(type)) return norm(el.value) || ({ submit: 'Submit', reset: 'Reset' }[type] || '');
      if (type === 'image') return norm(el.getAttribute('alt')) || 'Submit';
    }
    if (!['input', 'select', 'textarea'].includes(tag)) {
      let t = norm(el.innerText);
      if (!t) { const img = el.querySelector('img[alt]'); if (img) t = norm(img.getAttribute('alt')); }
      if (t) return t;
    }
    return norm(el.getAttribute('title')) || norm(el.getAttribute('placeholder'));
  };

  const cssFor = (el) => {
    const tag = el.tagName.toLowerCase();
    if (el.id && !dynId.test(el.id)) { const s = '#' + CSS.escape(el.id); if (unique(s)) return s; }
    for (const attr of ['data-testid', 'name', 'aria-label', 'placeholder', 'title', 'href', 'type']) {
      const v = el.getAttribute(attr);
      if (v) { const s = `${tag}[${attr}="${q(v)}"]`; if (unique(s)) return s; }
    }
    const parts = []; let node = el;
    while (node && node.nodeType === 1 && node !== document.documentElement) {
      if (node !== el && node.id && !dynId.test(node.id) && unique('#' + CSS.escape(node.id))) {
        parts.unshift('#' + CSS.escape(node.id));
      } else {
        let part = node.tagName.toLowerCase();
        const parent = node.parentElement;
        if (parent) {
          const sibs = [...parent.children].filter((c) => c.tagName === node.tagName);
          if (sibs.length > 1) part += `:nth-of-type(${sibs.indexOf(node) + 1})`;
        }
        parts.unshift(part);
      }
      const sel = parts.join(' > ');
      if (unique(sel)) return sel;
      if (parts[0].startsWith('#')) break;
      node = node.parentElement;
    }
    return parts.join(' > ');
  };

  const nodes = []; const seen = new Set();
  for (const el of document.querySelectorAll(selector)) {
    if (seen.has(el)) continue;
    seen.add(el);
    if (el.tagName.toLowerCase() === 'input' && (el.getAttribute('type') || '').toLowerCase() === 'hidden') continue;
    if (!visible(el)) continue;
    nodes.push(el);
    if (nodes.length >= maxElements) break;
  }

  const infos = nodes.map((el, i) => {
    const tag = el.tagName.toLowerCase();
    const type = tag === 'input' ? (el.getAttribute('type') || 'text').toLowerCase() : '';
    const explicitRole = norm(el.getAttribute('role')).split(' ')[0] || '';
    const attributes = {};
    for (const a of el.attributes) {
      if (a.name === 'style' || a.name === marker) continue;
      if (a.name === 'value' && type === 'password') continue;
      attributes[a.name] = String(a.value).slice(0, 300);
    }
    const testid = el.getAttribute('data-testid') || '';
    const id = el.id || '';
    const isControl = ['input', 'select', 'textarea'].includes(tag);
    return {
      eid: 'e' + (i + 1),
      tag, type,
      role: explicitRole || implicitRole(el),
      attributes,
      name: accName(el, tag, type),
      text: isControl ? '' : norm(el.innerText).slice(0, 200),
      placeholder: norm(el.getAttribute('placeholder')),
      label: labelText(el),
      testid,
      testid_unique: !!testid && unique(`[data-testid="${q(testid)}"]`),
      id,
      id_unique: !!id && !dynId.test(id) && unique(`[id="${q(id)}"]`),
      css: cssFor(el),
      abs_href: typeof el.href === 'string' ? el.href : '',
      target: el.getAttribute('target') || '',
      download: el.hasAttribute('download'),
      form_method: ((el.closest('form') && el.closest('form').getAttribute('method')) || '').toLowerCase(),
    };
  });
  nodes.forEach((el, i) => el.setAttribute(marker, 'e' + (i + 1)));
  return infos;
}
"""

REMOVE_MARKERS_JS = (
    "(m) => document.querySelectorAll('[' + m + ']').forEach((el) => el.removeAttribute(m))"
)

_SIMPLE_ID = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


# ---------------------------------------------------------------------------
# Locator code rendering (pure functions - deterministic)
# ---------------------------------------------------------------------------


def _dq(value: str) -> str:
    """Double-quoted literal valid in Python and Java."""
    return json.dumps(value, ensure_ascii=False)


def _sq(value: str) -> str:
    """Single-quoted literal for TypeScript / JavaScript."""
    escaped = (
        value.replace("\\", "\\\\").replace("'", "\\'").replace("\n", "\\n").replace("\r", "\\r").replace("\t", "\\t")
    )
    return f"'{escaped}'"


def _id_selector(element_id: str) -> str:
    return f"#{element_id}" if _SIMPLE_ID.match(element_id) else f'[id="{element_id}"]'


def render_locator(strategy: str, value: str, role: str = "") -> Dict[str, str]:
    """Render one locator strategy into Python / Java / TS / JS Playwright syntax."""
    if strategy == "data-testid":
        return {
            "python": f"page.get_by_test_id({_dq(value)})",
            "java": f"page.getByTestId({_dq(value)})",
            "ts": f"page.getByTestId({_sq(value)})",
            "js": f"page.getByTestId({_sq(value)})",
        }
    if strategy in ("id", "css"):
        selector = _id_selector(value) if strategy == "id" else value
        return {
            "python": f"page.locator({_dq(selector)})",
            "java": f"page.locator({_dq(selector)})",
            "ts": f"page.locator({_sq(selector)})",
            "js": f"page.locator({_sq(selector)})",
        }
    if strategy == "role":
        js = f"page.getByRole({_sq(role)}, {{ name: {_sq(value)}, exact: true }})"
        return {
            "python": f"page.get_by_role({_dq(role)}, name={_dq(value)}, exact=True)",
            "java": (
                f"page.getByRole(AriaRole.{role.upper()}, "
                f"new Page.GetByRoleOptions().setName({_dq(value)}).setExact(true))"
            ),
            "ts": js,
            "js": js,
        }
    method = {"placeholder": ("get_by_placeholder", "getByPlaceholder", "GetByPlaceholderOptions"),
              "label": ("get_by_label", "getByLabel", "GetByLabelOptions"),
              "text": ("get_by_text", "getByText", "GetByTextOptions")}.get(strategy)
    if method is None:
        raise ValueError(f"Unknown locator strategy: {strategy}")
    py_name, camel, java_opts = method
    js = f"page.{camel}({_sq(value)}, {{ exact: true }})"
    return {
        "python": f"page.{py_name}({_dq(value)}, exact=True)",
        "java": f"page.{camel}({_dq(value)}, new Page.{java_opts}().setExact(true))",
        "ts": js,
        "js": js,
    }


# ---------------------------------------------------------------------------
# Inspector
# ---------------------------------------------------------------------------


class BrowserInspector:
    """Inspects a URL: DOM locators, ARIA snapshot and XHR/fetch API telemetry."""

    # Active persistent session handle shared across runs if interactive/headed mode kept open
    _active_session: Optional[Dict[str, Any]] = None

    @classmethod
    async def close_persistent_browser(cls) -> None:
        """Explicitly terminate any persistent browser session kept open."""
        if cls._active_session:
            session = cls._active_session
            cls._active_session = None
            try:
                if session.get("context"):
                    await session["context"].close()
            except Exception:
                pass
            try:
                if session.get("browser"):
                    await session["browser"].close()
            except Exception:
                pass
            try:
                if session.get("pw"):
                    await session["pw"].stop()
            except Exception:
                pass
            logger.info("Persistent browser session closed successfully.")

    @classmethod
    def close_persistent_browser_sync(cls) -> None:
        """Synchronous wrapper to close persistent browser session."""
        if cls._active_session:
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(cls.close_persistent_browser())
                else:
                    loop.run_until_complete(cls.close_persistent_browser())
            except Exception:
                asyncio.run(cls.close_persistent_browser())

    def __init__(
        self,
        channels: Sequence[Optional[str]] = DEFAULT_CHANNELS,
        navigation_timeout_ms: int = 45_000,
        network_idle_timeout_ms: int = 10_000,
        max_elements: int = 400,
        max_probes: int = 6,
        viewport: Tuple[int, int] = (1440, 900),
    ) -> None:
        self.channels = tuple(channels)
        self.navigation_timeout_ms = navigation_timeout_ms
        self.network_idle_timeout_ms = network_idle_timeout_ms
        self.max_elements = max_elements
        self.max_probes = max_probes
        self.viewport = viewport
        self._reset_state()

    # ------------------------------------------------------------------ state
    def _reset_state(self) -> None:
        self._current_action: str = "page_load"
        self._request_actions: Dict[Request, str] = {}
        self._inflight: set[Request] = set()
        self._pending_tasks: set[asyncio.Task] = set()
        self._api_records: Dict[int, CapturedAPI] = {}
        self._seq = itertools.count()
        self._element_meta: Dict[str, Dict[str, Any]] = {}
        self._progress_cb: Optional[ProgressCallback] = None

    async def _emit(self, node: str, percent: float, message: str) -> None:
        logger.info("[%5.1f%%] %s: %s", percent, node, message)
        if self._progress_cb is None:
            return
        try:
            result = self._progress_cb(node, percent, message)
            if inspect.isawaitable(result):
                await result
        except Exception:  # a UI callback must never break inspection
            logger.exception("progress_callback raised; continuing")

    # ------------------------------------------------------------- public API
    async def inspect_url(
        self,
        target_url: str,
        user_flow_text: str,
        headless: bool = True,
        progress_callback: Optional[ProgressCallback] = None,
        pause_for_user: bool = False,
        capture_trigger: Optional[Any] = None,
    ) -> InspectionReport:
        """Inspect ``target_url`` and return a fully populated :class:`InspectionReport`.

        If ``pause_for_user`` is True, launches a visible browser, navigates to ``target_url``,
        attaches network & event listeners across all context pages, and waits until
        ``capture_trigger`` is set before capturing DOM, ARIA snapshot, and network contracts.
        """
        self._reset_state()
        self._progress_cb = progress_callback
        target_url = self._normalize_url(target_url)

        # In interactive manual session, browser must be visible
        actual_headless = False if pause_for_user else headless
        keep_browser_open = (not actual_headless) or pause_for_user

        # If previous persistent session exists, close it first
        if self._active_session:
            await self.close_persistent_browser()

        pw = await async_playwright().start()
        await self._emit("launch_browser", 5, "Launching Browser (Interactive Session)" if pause_for_user else "Launching Browser")
        browser, channel = await self._launch_browser(pw, actual_headless)
        try:
            context = await browser.new_context(
                viewport={"width": self.viewport[0], "height": self.viewport[1]},
                ignore_https_errors=True,  # corporate / internal certificates
            )
            page = await context.new_page()
            page.set_default_timeout(15_000 if pause_for_user else 10_000)

            await self._emit("attach_network", 15, "Attaching Network Listeners")
            self._attach_listeners(context, page, interactive_mode=pause_for_user)

            await self._emit("navigate", 25, f"Navigating to URL: {target_url}")
            self._current_action = "page_load"
            await self._navigate(page, target_url)

            if pause_for_user:
                await self._emit(
                    "interactive_session",
                    30,
                    "Interactive Browser open. Perform logins, file uploads, or multi-tab actions. Click 'Capture State' when ready.",
                )
                self._current_action = "manual_interaction"
                await self._wait_for_user_capture(capture_trigger, context)
                await self._emit("interactive_session", 33, "Capture trigger received. Analyzing active page state...")

            # Identify active page (last active or first page)
            active_page = context.pages[-1] if context.pages else page
            page_title = await self._safe_title(active_page)

            await self._emit("extract_dom", 35, "Extracting DOM & ARIA Locators")
            elements, live_locators = await self._extract_elements(active_page)
            aria_snapshot = await self._capture_aria_snapshot(active_page)
            await self._emit("extract_dom", 40, f"Extracted {len(elements)} interactive elements from active page")

            probes: List[str] = []
            if not pause_for_user:
                await self._emit("flow_probes", 45, "Executing Safe Flow Probes & Capturing APIs")
                probes = await self._run_flow_probes(active_page, target_url, user_flow_text, elements, live_locators)
            else:
                probes = ["manual:user_session_captured"]

            self._current_action = "background"
            await self._wait_for_network_quiet(quiet_ms=500, timeout_ms=3_000)
            if self._pending_tasks:
                await asyncio.gather(*self._pending_tasks, return_exceptions=True)

            if keep_browser_open:
                # Retain browser context in memory for user inspection or manual interaction
                BrowserInspector._active_session = {
                    "pw": pw,
                    "browser": browser,
                    "context": context,
                    "page": active_page,
                }
                logger.info("Retained persistent browser session open.")
            else:
                await context.close()
                await browser.close()
                await pw.stop()
        except Exception:
            # On unexpected failure, ensure cleanup
            try:
                await context.close()
            except Exception:
                pass
            try:
                await browser.close()
            except Exception:
                pass
            try:
                await pw.stop()
            except Exception:
                pass
            raise

        report = InspectionReport(
            target_url=target_url,
            page_title=page_title,
            elements=elements,
            captured_apis=self._collect_apis(),
            aria_snapshot=aria_snapshot,
            browser_channel=channel,
            probes_executed=probes,
        )
        await self._emit(
            "inspection_complete",
            50,
            f"Inspection complete: {len(report.elements)} elements, {len(report.captured_apis)} API calls",
        )
        return report

    # --------------------------------------------------------------- browser
    async def _launch_browser(self, pw: Playwright, headless: bool) -> Tuple[Browser, str]:
        errors: List[str] = []
        for channel in self.channels:
            kwargs: Dict[str, Any] = {
                "headless": headless,
                "args": ["--no-first-run", "--no-default-browser-check", "--disable-extensions"],
            }
            if channel:
                kwargs["channel"] = channel
            try:
                browser = await pw.chromium.launch(**kwargs)
                name = channel or "chromium"
                logger.info("Launched browser channel=%s version=%s", name, browser.version)
                return browser, name
            except Exception as exc:  # channel not installed -> try next
                errors.append(f"{channel or 'chromium'}: {str(exc).splitlines()[0]}")
        raise RuntimeError(
            "No usable browser found. Install Google Chrome or Microsoft Edge, "
            "or run `playwright install chromium`.\n" + "\n".join(errors)
        )

    @staticmethod
    def _normalize_url(url: str) -> str:
        url = url.strip()
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*://", url):
            local = re.match(r"^(localhost|127\.0\.0\.1|\[::1\])(:\d+)?", url)
            url = ("http://" if local else "https://") + url
        return url

    async def _navigate(self, page: Page, url: str) -> None:
        await page.goto(url, wait_until="domcontentloaded", timeout=self.navigation_timeout_ms)
        try:
            await page.wait_for_load_state("networkidle", timeout=self.network_idle_timeout_ms)
        except Exception:
            # Streaming / long-polling pages never go idle - proceed with what we have.
            logger.info("networkidle not reached within %sms; continuing", self.network_idle_timeout_ms)
            await self._wait_for_network_quiet(quiet_ms=500, timeout_ms=2_000)

    @staticmethod
    async def _safe_title(page: Page) -> str:
        try:
            return await page.title()
        except Exception:
            return ""

    # --------------------------------------------------------------- network
    def _attach_listeners(self, context: BrowserContext, page: Page, interactive_mode: bool = False) -> None:
        self._attach_page_network(page)

        if interactive_mode:
            # In interactive mode, attach network listeners dynamically to any new tab/popup
            def on_new_page(new_p: Page) -> None:
                self._attach_page_network(new_p)
                # Keep new pages open for manual user interactions
            context.on("page", on_new_page)
        else:
            # Automated mode: dismiss confirm/alert dialogs and close auxiliary popups
            page.on("dialog", lambda dialog: self._spawn(dialog.dismiss()))
            context.on("page", lambda new_page: self._spawn(new_page.close()) if new_page is not page else None)

    def _attach_page_network(self, page: Page) -> None:
        page.on("request", self._on_request)
        page.on("requestfinished", self._on_request_done)
        page.on("requestfailed", self._on_request_failed)
        page.on("response", self._on_response)

    async def _wait_for_user_capture(self, capture_trigger: Optional[Any], context: BrowserContext) -> None:
        """Asynchronously wait for the user to trigger state capture from the GUI."""
        if capture_trigger is None:
            # Fallback if no trigger provided: wait 10 seconds
            await asyncio.sleep(10.0)
            return

        # Check if capture_trigger is an asyncio.Event or threading.Event
        if isinstance(capture_trigger, asyncio.Event):
            while not capture_trigger.is_set():
                if not context.pages:
                    break
                await asyncio.sleep(0.2)
        else:
            # Handle threading.Event or custom object with .is_set()
            while not getattr(capture_trigger, "is_set", lambda: False)():
                if not context.pages:
                    break
                await asyncio.sleep(0.2)

    def _spawn(self, coro: Awaitable[Any]) -> None:
        task = asyncio.ensure_future(coro)
        self._pending_tasks.add(task)
        task.add_done_callback(self._pending_tasks.discard)

    @staticmethod
    def _is_api(request: Request) -> bool:
        return request.resource_type in ("xhr", "fetch")

    def _on_request(self, request: Request) -> None:
        if self._is_api(request):
            self._request_actions[request] = self._current_action
            self._inflight.add(request)

    def _on_request_done(self, request: Request) -> None:
        self._inflight.discard(request)

    def _on_request_failed(self, request: Request) -> None:
        self._inflight.discard(request)
        if not self._is_api(request):
            return
        seq = next(self._seq)
        self._api_records[seq] = CapturedAPI(
            url=request.url,
            method=request.method,
            resource_type=request.resource_type,
            status_code=0,
            request_payload_keys=self._payload_keys(request),
            response_keys=[],
            triggered_by_action=self._request_actions.pop(request, self._current_action),
        )

    def _on_response(self, response: Response) -> None:
        request = response.request
        if not self._is_api(request):
            return
        seq = next(self._seq)
        action = self._request_actions.pop(request, self._current_action)
        self._spawn(self._record_response(seq, response, action))

    async def _record_response(self, seq: int, response: Response, action: str) -> None:
        request = response.request
        status = response.status
        response_keys: List[str] = []
        if status not in (204, 205, 304) and not 300 <= status < 400:
            content_type = (response.headers.get("content-type") or "").lower()
            if "json" in content_type or "text/plain" in content_type or not content_type:
                try:
                    body = await response.body()
                    if body and len(body) <= 10 * 1024 * 1024:
                        response_keys = self._top_level_keys(json.loads(body))
                except Exception:
                    pass  # not JSON / body unavailable (e.g. page navigated away)
        self._api_records[seq] = CapturedAPI(
            url=response.url,
            method=request.method,
            resource_type=request.resource_type,
            status_code=status,
            request_payload_keys=self._payload_keys(request),
            response_keys=response_keys,
            triggered_by_action=action,
        )

    @staticmethod
    def _top_level_keys(data: Any) -> List[str]:
        if isinstance(data, dict):
            return [str(k) for k in data.keys()]
        if isinstance(data, list) and data and isinstance(data[0], dict):
            return [str(k) for k in data[0].keys()]
        return []

    def _payload_keys(self, request: Request) -> List[str]:
        try:
            data = request.post_data_json  # parses JSON and form-urlencoded bodies
        except Exception:
            return []
        return self._top_level_keys(data)

    async def _wait_for_network_quiet(self, quiet_ms: int = 600, timeout_ms: int = 6_000) -> None:
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout_ms / 1000
        quiet_since = loop.time()
        while loop.time() < deadline:
            await asyncio.sleep(0.1)
            if self._inflight:
                quiet_since = loop.time()
            elif loop.time() - quiet_since >= quiet_ms / 1000:
                return

    def _collect_apis(self) -> List[CapturedAPI]:
        seen: set[tuple] = set()
        result: List[CapturedAPI] = []
        for seq in sorted(self._api_records):
            api = self._api_records[seq]
            key = (api.method, api.url, api.status_code, api.triggered_by_action)
            if key not in seen:
                seen.add(key)
                result.append(api)
        return result

    # ------------------------------------------------------------------- DOM
    async def _extract_elements(self, page: Page) -> Tuple[List[DOMElement], Dict[str, Locator]]:
        try:
            infos: List[Dict[str, Any]] = await page.evaluate(
                EXTRACT_ELEMENTS_JS,
                {
                    "selector": INTERACTIVE_SELECTOR,
                    "maxElements": self.max_elements,
                    "marker": MARKER_ATTR,
                    "dynamicIdPattern": DYNAMIC_ID_PATTERN,
                },
            )
        except Exception as exc:
            logger.warning("DOM extraction failed: %s", exc)
            return [], {}

        elements: List[DOMElement] = []
        live: Dict[str, Locator] = {}
        for info in infos:
            strategy, value, locator = await self._choose_locator(page, info)
            self._element_meta[info["eid"]] = info
            elements.append(
                DOMElement(
                    element_id=info["eid"],
                    tag=info["tag"],
                    role=info["role"],
                    text_or_label=info["name"] or info["text"] or info["placeholder"],
                    input_type=info["type"],
                    attributes=info["attributes"],
                    recommended_locator=render_locator(strategy, value, info["role"]),
                    locator_strategy=strategy,
                )
            )
            live[info["eid"]] = locator
        try:
            await page.evaluate(REMOVE_MARKERS_JS, MARKER_ATTR)
        except Exception:
            pass
        return elements, live

    async def _choose_locator(self, page: Page, info: Dict[str, Any]) -> Tuple[str, str, Locator]:
        """Apply corporate priority: data-testid -> id -> role+name -> placeholder -> label -> text -> css."""
        eid = info["eid"]
        if info["testid_unique"]:
            return "data-testid", info["testid"], page.get_by_test_id(info["testid"])
        if info["id_unique"]:
            return "id", info["id"], page.locator(_id_selector(info["id"]))

        candidates: List[Tuple[str, str, Callable[[], Locator]]] = []
        role, name = info["role"], info["name"]
        if role in NAMEABLE_ROLES and name and len(name) <= 120:
            candidates.append(("role", name, lambda: page.get_by_role(role, name=name, exact=True)))  # type: ignore[arg-type]
        if info["placeholder"]:
            ph = info["placeholder"]
            candidates.append(("placeholder", ph, lambda: page.get_by_placeholder(ph, exact=True)))
        if info["label"]:
            lb = info["label"]
            candidates.append(("label", lb, lambda: page.get_by_label(lb, exact=True)))
        if info["text"] and info["tag"] not in FORM_CONTROL_TAGS and len(info["text"]) <= 80:
            tx = info["text"]
            candidates.append(("text", tx, lambda: page.get_by_text(tx, exact=True)))

        for strategy, value, factory in candidates:
            locator = factory()
            if await self._resolves_uniquely_to(locator, eid):
                return strategy, value, locator
        return "css", info["css"], page.locator(info["css"])

    @staticmethod
    async def _resolves_uniquely_to(locator: Locator, eid: str) -> bool:
        try:
            if await locator.count() != 1:
                return False
            return await locator.get_attribute(MARKER_ATTR, timeout=2_000) == eid
        except Exception:
            return False

    async def _capture_aria_snapshot(self, page: Page) -> str:
        try:
            return await page.locator("body").aria_snapshot(timeout=15_000)
        except AttributeError:
            logger.info("Locator.aria_snapshot unsupported (Playwright < 1.49); using fallback")
        except Exception as exc:
            logger.info("aria_snapshot failed (%s); using fallback", exc)
        try:  # legacy accessibility tree (removed in recent Playwright versions)
            snapshot = await page.accessibility.snapshot()  # type: ignore[attr-defined]
            return json.dumps(snapshot, indent=2, ensure_ascii=False) if snapshot else ""
        except Exception:
            return ""

    # ---------------------------------------------------------- flow probing
    @staticmethod
    def parse_flow_keywords(user_flow_text: str) -> Tuple[List[str], List[str]]:
        """Deterministically extract (quoted_phrases, keywords) from free-text flow."""
        text = user_flow_text or ""
        quoted = re.findall(r"[\"\u201c]([^\"\u201d]{1,80})[\"\u201d]", text)
        quoted += re.findall(r"(?:^|\s)'([^']{1,80})'(?=\s|$|[.,;:!?])", text)
        quoted = [q.strip().lower() for q in quoted if q.strip()]
        words = re.findall(r"[a-z0-9][a-z0-9_\-]{2,}", text.lower())
        keywords: List[str] = []
        for w in words:
            if w not in STOPWORDS and w not in keywords:
                keywords.append(w)
        return list(dict.fromkeys(quoted)), keywords

    @staticmethod
    def _search_query(user_flow_text: str) -> str:
        m = re.search(
            r"(?:search|find|look\s?up|filter|query)\s+(?:for\s+|by\s+)?[\"\u201c']([^\"\u201d']{1,60})[\"\u201d']",
            user_flow_text or "",
            re.IGNORECASE,
        )
        if m:
            return m.group(1).strip()
        m = re.search(r"(?:search|find|look\s?up)\s+for\s+([A-Za-z0-9_\-]+)", user_flow_text or "", re.IGNORECASE)
        return m.group(1) if m else "test"

    def _is_safe_to_click(self, element: DOMElement, info_origin: str) -> bool:
        name = element.text_or_label
        if not name or DESTRUCTIVE_PATTERN.search(name):
            return False
        attrs = element.attributes
        for attr in ("aria-label", "title", "data-testid", "id", "name", "value"):
            if DESTRUCTIVE_PATTERN.search(attrs.get(attr, "").replace("-", " ").replace("_", " ")):
                return False
        if element.input_type in ("submit", "reset", "image", "file", "password"):
            return False
        if element.attributes.get("disabled") is not None or attrs.get("aria-disabled") == "true":
            return False
        if element.tag == "a" or element.role == "link":
            href = attrs.get("href", "")
            if href.lower().startswith(("mailto:", "tel:", "sms:", "data:")) or "download" in attrs:
                return False
            if attrs.get("target", "") == "_blank":
                return False
            if href and not href.startswith(("#", "/", "?", "javascript:")):
                parsed = urlparse(href)
                if parsed.scheme in ("http", "https") and parsed.netloc and parsed.netloc != info_origin:
                    return False
        return True

    def _match_score(self, element: DOMElement, quoted: List[str], keywords: List[str]) -> Tuple[int, int]:
        """Return (score, position-in-flow). Higher score is better; 0 means no match."""
        name = re.sub(r"\s+", " ", element.text_or_label).strip().lower()
        if not name or len(name) > 60:
            return 0, 0
        name_words = set(re.findall(r"[a-z0-9][a-z0-9_\-]*", name))
        for idx, phrase in enumerate(quoted):
            if phrase == name:
                return 3, idx
            if len(phrase) >= 3 and phrase in name and len(name_words) <= 5:
                return 2, idx
        if len(name_words) <= 4:
            for idx, kw in enumerate(keywords):
                if kw == name or kw in name_words:
                    return 1, len(quoted) + idx
        return 0, 0

    async def _run_flow_probes(
        self,
        page: Page,
        target_url: str,
        user_flow_text: str,
        elements: List[DOMElement],
        live: Dict[str, Locator],
    ) -> List[str]:
        executed: List[str] = []
        if not user_flow_text or not user_flow_text.strip():
            return executed
        origin = urlparse(target_url).netloc
        baseline_url = urldefrag(page.url)[0]
        quoted, keywords = self.parse_flow_keywords(user_flow_text)
        flow_lower = user_flow_text.lower()

        # 1) Search probe: type a sample query into a search box, then press Enter.
        if SEARCH_INTENT_PATTERN.search(flow_lower):
            search_el = self._find_search_input(elements)
            if search_el is not None:
                query = self._search_query(user_flow_text)
                label = f"probe:search -> typed '{query}' into {search_el.role or search_el.tag} '{search_el.text_or_label}'"
                locator = live[search_el.element_id]

                async def do_search() -> None:
                    await locator.fill(query, timeout=5_000)
                    await self._wait_for_network_quiet(quiet_ms=700, timeout_ms=4_000)  # debounced type-ahead
                    await locator.press("Enter", timeout=5_000)

                if await self._probe(page, label, do_search):
                    executed.append(label)
                await self._restore(page, baseline_url, target_url)

        # 2) Click probes: tabs / buttons / links whose names match the flow text.
        ranked: List[Tuple[int, int, int, DOMElement]] = []
        for order, el in enumerate(elements):
            if el.role not in CLICKABLE_ROLES and el.tag not in ("a", "button"):
                continue
            score, pos = self._match_score(el, quoted, keywords)
            if score and self._is_safe_to_click(el, origin):
                if self._submits_post_form(el):
                    continue
                ranked.append((pos, -score, order, el))
        ranked.sort(key=lambda t: (t[0], t[1], t[2]))

        clicked_names: set[str] = set()
        for _, _, _, el in ranked:
            if len(executed) >= self.max_probes:
                break
            key = el.text_or_label.strip().lower()
            if key in clicked_names:
                continue
            clicked_names.add(key)
            label = f"probe:click {el.role or el.tag} '{el.text_or_label}'"
            locator = live[el.element_id]

            async def do_click(loc: Locator = locator) -> None:
                await loc.click(timeout=5_000)

            if await self._probe(page, label, do_click):
                executed.append(label)
            await self._restore(page, baseline_url, target_url)
        return executed

    def _submits_post_form(self, element: DOMElement) -> bool:
        """True if clicking would submit a POST form (state-changing) - never probed."""
        meta = self._element_meta.get(element.element_id, {})
        if meta.get("form_method") != "post":
            return False
        button_type = element.attributes.get("type", "submit" if element.tag == "button" else "").lower()
        return button_type == "submit" or element.input_type in ("submit", "image")

    @staticmethod
    def _find_search_input(elements: List[DOMElement]) -> Optional[DOMElement]:
        best: Optional[Tuple[int, DOMElement]] = None
        for el in elements:
            if el.tag not in ("input", "textarea") and el.role not in ("searchbox", "combobox", "textbox"):
                continue
            if el.input_type in ("password", "checkbox", "radio", "submit", "button", "file", "hidden", "range"):
                continue
            hay = " ".join(
                [el.text_or_label, *(el.attributes.get(a, "") for a in ("name", "id", "placeholder", "aria-label", "class", "data-testid"))]
            )
            score = 0
            if el.input_type == "search" or el.role == "searchbox":
                score += 3
            if SEARCH_FIELD_HINT.search(hay):
                score += 2
            if score and (best is None or score > best[0]):
                best = (score, el)
        return best[1] if best else None

    async def _probe(self, page: Page, label: str, action: Callable[[], Awaitable[None]]) -> bool:
        self._current_action = label
        ok = True
        try:
            await action()
        except Exception as exc:
            ok = False
            logger.info("Probe failed (%s): %s", label, str(exc).splitlines()[0])
        await self._wait_for_network_quiet(quiet_ms=700, timeout_ms=6_000)
        self._current_action = "background"
        return ok

    async def _restore(self, page: Page, baseline_url: str, target_url: str) -> None:
        """Return to the original page if a probe navigated away."""
        try:
            if urldefrag(page.url)[0] != baseline_url:
                self._current_action = "restore_navigation"
                await self._navigate(page, target_url)
                self._current_action = "background"
        except Exception as exc:
            logger.info("Could not restore page after probe: %s", exc)
