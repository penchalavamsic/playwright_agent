"""Deterministic Rule-Based NLP / Regex Intent Parser Node for LangGraph.

Decomposes free-form user automation requirements into structured `ParsedFlowStep`
objects with zero LLM dependencies.
"""

from __future__ import annotations

import inspect
import re
from typing import Any, Dict, List, Optional

from agents.state import AgentState, ParsedFlowStep
from core.workspace_manager import WorkspaceManager

# Keywords & Regex patterns
STATUS_CODE_REGEX = re.compile(r"\b([2-5]\d{2})\b")
QUOTED_TEXT_REGEX = re.compile(r"[\"\u201c]([^\"\u201d]{1,100})[\"\u201d]|'([^']{1,100})'")

SEARCH_FILL_KEYWORDS = ["search", "type", "enter", "input", "fill", "filter", "login", "query", "lookup"]
CLICK_KEYWORDS = ["click", "press", "submit", "open", "select", "button", "tab", "link", "tap", "trigger", "launch"]
VERIFY_API_KEYWORDS = ["api", "status", "response", "endpoint", "network", "succeeded", "success", "code", "200", "201"]
VERIFY_UI_KEYWORDS = ["verify", "check", "see", "visible", "dashboard", "display", "validate", "assert", "ensure", "present"]


def _clean_str(val: str) -> str:
    return re.sub(r"\s+", " ", val or "").strip()


def _emit_progress(state: AgentState, node_name: str, percent: float, message: str) -> None:
    cb = state.get("progress_callback")
    if not cb:
        return
    try:
        res = cb(node_name, percent, message)
        if inspect.isawaitable(res):
            # In sync node, if callback is async, fire task or run
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(res)
            except RuntimeError:
                asyncio.run(res)
    except Exception:
        pass


def detect_access_profile_from_flow(
    user_flow_text: str,
    active_access_profile: str = "",
    account_credentials: Optional[Dict[str, Any]] = None,
) -> str:
    """Resolve active access profile from explicit user flow mentions or fallback to GUI selection."""
    text = user_flow_text or ""
    candidates: List[str] = []
    for k in (account_credentials or {}).keys():
        norm = WorkspaceManager.normalize_role(k)
        if norm and norm not in candidates:
            candidates.append(norm)
    for default_role in ("SUPER_USER_ADMIN_USER", "SUPER_USER", "ADMIN"):
        if default_role not in candidates:
            candidates.append(default_role)

    # Sort longest-first so SUPER_USER_ADMIN_USER matches before SUPER_USER or ADMIN
    candidates.sort(key=len, reverse=True)

    for role in candidates:
        parts = [re.escape(p) for p in role.split("_") if p]
        if not parts:
            continue
        role_pat = r"[\s_\-]+".join(parts)
        contextual_re = re.compile(
            rf"\b(?:as|with|using|login\s+as|log\s+in\s+as|for|role|profile)\s+(?:a\s+|an\s+|the\s+)?{role_pat}\b",
            re.IGNORECASE,
        )
        exact_token_re = re.compile(rf"\b{re.escape(role)}\b")
        if contextual_re.search(text) or exact_token_re.search(text):
            return role

    return active_access_profile or "None (Public URL)"


def intent_parser_node(state: AgentState) -> Dict[str, Any]:
    """Parse user_flow_text into deterministic structured ParsedFlowStep items."""
    _emit_progress(
        state,
        "IntentParserNode",
        0.15,
        "Parsing user flow and extracting automation rules & status codes...",
    )

    user_flow = state.get("user_flow_text", "")
    from core.browser_inspector import BrowserInspector
    target_url = BrowserInspector._normalize_url(state.get("target_url", "")) if state.get("target_url") else ""
    raw_output_dir = state.get("output_dir", "")
    resolved_output_dir = (
        str(WorkspaceManager.resolve_run_output_dir(raw_output_dir, target_url))
        if raw_output_dir
        else ""
    )
    resolved_profile = detect_access_profile_from_flow(
        user_flow_text=user_flow,
        active_access_profile=state.get("active_access_profile", ""),
        account_credentials=state.get("account_credentials", {}),
    )

    from core.flow_parser import parse_flow
    parsed_steps = [ParsedFlowStep(**step) for step in parse_flow(user_flow, target_url, resolved_profile)]

    result_payload: Dict[str, Any] = {
        "target_url": target_url,
        "parsed_flow_steps": [s.model_dump() for s in parsed_steps],
        "active_access_profile": resolved_profile,
    }
    if resolved_output_dir:
        result_payload["output_dir"] = resolved_output_dir
    return result_payload

