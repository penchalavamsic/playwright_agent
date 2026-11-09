"""LangGraph Code Synthesizer and Project Scaffolder Nodes (Phase 3).

Orchestrates multi-language Playwright code synthesis and file writing
within the deterministic LangGraph pipeline.
"""

from __future__ import annotations

import inspect
from pathlib import Path
from typing import Any, Dict, List

from agents.state import AgentState
from scaffolder.project_builder import ProjectScaffolder
from scaffolder.template_registry import TemplateRegistry


def _emit_progress(state: AgentState, node_name: str, percent: float, message: str) -> None:
    cb = state.get("progress_callback")
    if not cb:
        return
    try:
        res = cb(node_name, percent, message)
        if inspect.isawaitable(res):
            import asyncio
            try:
                loop = asyncio.get_running_loop()
                loop.create_task(res)
            except RuntimeError:
                asyncio.run(res)
    except Exception:
        pass


def code_synthesizer_node(state: AgentState) -> Dict[str, Any]:
    """Synthesizes Page Object Models and test suites across selected target languages."""
    generate_scripts = state.get("generate_scripts", True)
    if not generate_scripts:
        _emit_progress(state, "CodeSynthesizerNode", 0.90, "Script generation skipped per configuration.")
        return {}

    target_langs = state.get("target_languages", ["Python", "Java", "TypeScript", "JavaScript"])

    # Progressive milestone reporting
    if "Python" in target_langs:
        _emit_progress(state, "CodeSynthesizerNode", 0.78, "Synthesizing Python Page Object Model & pytest suite...")
    if "Java" in target_langs:
        _emit_progress(state, "CodeSynthesizerNode", 0.82, "Synthesizing Java Maven POM & TestNG suite...")
    if "TypeScript" in target_langs:
        _emit_progress(state, "CodeSynthesizerNode", 0.86, "Synthesizing TypeScript Page Object & Playwright suite...")
    if "JavaScript" in target_langs:
        _emit_progress(state, "CodeSynthesizerNode", 0.90, "Synthesizing JavaScript Page Object & Playwright suite...")

    return {}


def project_scaffolder_node(state: AgentState) -> Dict[str, Any]:
    """Writes all synthesized corporate files and directories to the designated output folder."""
    output_dir = state.get("output_dir", "")
    generate_scripts = state.get("generate_scripts", True)

    existing_files: List[str] = list(state.get("generated_files", []))

    if not output_dir:
        return {"generated_files": existing_files}

    _emit_progress(state, "ProjectScaffolderNode", 0.95, "Writing corporate project structure and configs to disk...")

    created_paths = []
    if generate_scripts:
        scaffolder = ProjectScaffolder()
        created_paths = scaffolder.scaffold_project(output_dir, state)

    _emit_progress(
        state,
        "ProjectScaffolderNode",
        1.00,
        "Corporate Test Plan & Multi-Language Playwright Suites successfully generated!",
    )

    all_files = list(dict.fromkeys(existing_files + created_paths))
    return {"generated_files": all_files}

