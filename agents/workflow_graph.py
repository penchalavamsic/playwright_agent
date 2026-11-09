"""LangGraph StateGraph workflow pipeline for Phase 2 & Phase 3.

Orchestrates full 5-node pipeline:
START -> intent_parser -> browser_inspector -> test_planner -> code_synthesizer -> project_scaffolder -> END

100% deterministic, offline, and zero-API.
"""

from __future__ import annotations

import inspect
from typing import Any, Dict

from langgraph.graph import END, START, StateGraph

from agents.code_synthesizer_node import code_synthesizer_node, project_scaffolder_node
from agents.intent_parser import intent_parser_node
from agents.planner_node import test_planner_node
from agents.state import AgentState
from core.browser_inspector import BrowserInspector


async def browser_inspector_node(state: AgentState) -> Dict[str, Any]:
    """Async LangGraph node wrapping BrowserInspector from Phase 1."""
    target_url = state.get("target_url", "")
    user_flow_text = state.get("user_flow_text", "")
    headless = state.get("headless", True)
    parent_progress_cb = state.get("progress_callback")

    async def scaled_progress(node_name: str, percent: float, message: str) -> None:
        """Map Phase 1 progress (5% - 50%) to Phase 2 workflow scale (0.20 - 0.55)."""
        if not parent_progress_cb:
            return
        norm = max(0.0, min(1.0, (percent - 5.0) / 45.0))
        scaled_pct = 0.20 + (norm * 0.35)
        try:
            res = parent_progress_cb(f"BrowserInspector:{node_name}", round(scaled_pct, 2), message)
            if inspect.isawaitable(res):
                await res
        except Exception:
            pass

    inspector = BrowserInspector()
    report = await inspector.inspect_url(
        target_url=target_url,
        user_flow_text=user_flow_text,
        headless=headless,
        progress_callback=scaled_progress,
    )

    return {"inspection_report": report.model_dump()}


def build_workflow_graph() -> Any:
    """Build and compile the complete 5-node LangGraph StateGraph workflow."""
    workflow = StateGraph(AgentState)

    workflow.add_node("intent_parser", intent_parser_node)
    workflow.add_node("browser_inspector", browser_inspector_node)
    workflow.add_node("test_planner", test_planner_node)
    workflow.add_node("code_synthesizer", code_synthesizer_node)
    workflow.add_node("project_scaffolder", project_scaffolder_node)

    workflow.add_edge(START, "intent_parser")
    workflow.add_edge("intent_parser", "browser_inspector")
    workflow.add_edge("browser_inspector", "test_planner")
    workflow.add_edge("test_planner", "code_synthesizer")
    workflow.add_edge("code_synthesizer", "project_scaffolder")
    workflow.add_edge("project_scaffolder", END)

    return workflow.compile()


async def run_agent_pipeline(initial_state: AgentState) -> AgentState:
    """Compile and execute the LangGraph pipeline with the provided initial state."""
    app = build_workflow_graph()
    result = await app.ainvoke(initial_state)
    return result
