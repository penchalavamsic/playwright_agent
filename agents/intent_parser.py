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
    target_url = state.get("target_url", "")
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

    # Extract all explicitly mentioned status codes across the whole text
    global_status_codes = [int(m) for m in STATUS_CODE_REGEX.findall(user_flow)]
    # Filter to valid HTTP status range
    global_status_codes = [c for c in global_status_codes if 200 <= c <= 599]

    # Check if user mentioned API success or status code generically
    lower_full = user_flow.lower()
    has_api_intent = any(k in lower_full for k in ["api", "status code", "status", "endpoint", "succeeded", "success"])
    if not global_status_codes and has_api_intent:
        global_status_codes = [200, 201]

    parsed_steps: List[ParsedFlowStep] = []
    order = 1

    # First synthetic step: Navigate to target URL if given
    if target_url:
        parsed_steps.append(
            ParsedFlowStep(
                step_order=order,
                action_type="NAVIGATE",
                target_keyword=target_url,
                input_value=target_url,
                expected_status_codes=[200],
            )
        )
        order += 1

    # Sentence / clause splitting
    # Split on newlines, semicolons, periods followed by space, or coordinating conjunctions
    clauses = re.split(r"\n+|;+|\.\s+|\s+and\s+then\s+|\s+then\s+|\s+and\s+verify\s+|\s+and\s+check\s+|,", user_flow)

    for raw_clause in clauses:
        clause = _clean_str(raw_clause)
        if not clause or len(clause) < 3:
            continue

        c_lower = clause.lower()

        # Check local status codes
        local_codes = [int(m) for m in STATUS_CODE_REGEX.findall(clause) if 200 <= int(m) <= 599]
        clause_status_codes = local_codes if local_codes else list(global_status_codes)

        # Extract quotes in this clause if any
        quoted_matches = QUOTED_TEXT_REGEX.findall(clause)
        quoted_vals = [m[0] or m[1] for m in quoted_matches if (m[0] or m[1])]
        quoted_target = quoted_vals[0].strip() if quoted_vals else ""

        # Determine action intent using corporate keyword priority
        # 1. VERIFY_API
        if any(k in c_lower for k in ["api", "status code", "status", "200", "201", "endpoint", "response", "succeeded"]):
            # Check if this clause also specifies a preceding click/search action
            has_click = any(k in c_lower for k in CLICK_KEYWORDS)
            has_search = any(k in c_lower for k in SEARCH_FILL_KEYWORDS)
            
            # If compound clause e.g. "click button and verify whether it succeeded with 200 or 201 status code"
            if has_click and ("button" in c_lower or "click" in c_lower):
                target_kw = quoted_target or "button"
                for w in ["button", "tab", "link", "submit", "go"]:
                    if w in c_lower and not quoted_target:
                        target_kw = w
                        break
                parsed_steps.append(
                    ParsedFlowStep(
                        step_order=order,
                        action_type="CLICK",
                        target_keyword=target_kw,
                        input_value="",
                        expected_status_codes=[],
                    )
                )
                order += 1

            if has_search and ("search" in c_lower or "type" in c_lower):
                parsed_steps.append(
                    ParsedFlowStep(
                        step_order=order,
                        action_type="SEARCH",
                        target_keyword="search",
                        input_value=quoted_target or "search",
                        expected_status_codes=[],
                    )
                )
                order += 1

            parsed_steps.append(
                ParsedFlowStep(
                    step_order=order,
                    action_type="VERIFY_API",
                    target_keyword="api",
                    input_value="",
                    expected_status_codes=clause_status_codes if clause_status_codes else [200, 201],
                )
            )
            order += 1
            continue

        # 2. SEARCH / FILL
        if any(k in c_lower for k in SEARCH_FILL_KEYWORDS):
            act = "SEARCH" if ("search" in c_lower or "query" in c_lower or "lookup" in c_lower) else "FILL"
            # Target keyword and input value
            val = quoted_target
            if not val:
                # E.g., "search for playwright" -> search query is playwright
                m_for = re.search(r"(?:search|type|enter|fill)\s+(?:for\s+|in\s+)?([A-Za-z0-9_\-]+)", clause, re.IGNORECASE)
                val = m_for.group(1) if m_for else "search"
            parsed_steps.append(
                ParsedFlowStep(
                    step_order=order,
                    action_type=act,
                    target_keyword="search" if act == "SEARCH" else (quoted_target or "input"),
                    input_value=val,
                    expected_status_codes=[200] if act == "SEARCH" else [],
                )
            )
            order += 1
            continue

        # 3. CLICK
        if any(k in c_lower for k in CLICK_KEYWORDS):
            target_kw = quoted_target
            if not target_kw:
                # E.g. "click dashboard", "open dashboard tab", "click button"
                for word in ["button", "tab", "link", "dashboard", "reports", "overview", "login", "submit", "go"]:
                    if word in c_lower:
                        target_kw = word
                        break
            if not target_kw:
                target_kw = clause
            parsed_steps.append(
                ParsedFlowStep(
                    step_order=order,
                    action_type="CLICK",
                    target_keyword=target_kw,
                    input_value="",
                    expected_status_codes=[],
                )
            )
            order += 1
            continue

        # 4. VERIFY_UI
        if any(k in c_lower for k in VERIFY_UI_KEYWORDS):
            parsed_steps.append(
                ParsedFlowStep(
                    step_order=order,
                    action_type="VERIFY_UI",
                    target_keyword=quoted_target or clause,
                    input_value="",
                    expected_status_codes=[],
                )
            )
            order += 1
            continue

    # Fallback safety: if no steps were parsed from text, create standard baseline steps
    if len(parsed_steps) <= (1 if target_url else 0):
        parsed_steps.append(
            ParsedFlowStep(
                step_order=order,
                action_type="VERIFY_UI",
                target_keyword="dashboard",
                input_value="",
                expected_status_codes=[],
            )
        )
        order += 1
        parsed_steps.append(
            ParsedFlowStep(
                step_order=order,
                action_type="VERIFY_API",
                target_keyword="api",
                input_value="",
                expected_status_codes=global_status_codes or [200, 201],
            )
        )

    result_payload: Dict[str, Any] = {
        "parsed_flow_steps": [s.model_dump() for s in parsed_steps],
        "active_access_profile": resolved_profile,
    }
    if resolved_output_dir:
        result_payload["output_dir"] = resolved_output_dir
    return result_payload

