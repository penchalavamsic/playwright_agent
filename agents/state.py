"""Agent State and Structured Test Case models for Phase 2.

Everything is strictly typed and serializable so that StateGraph
can checkpoint or pass state deterministically between nodes.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, TypedDict
from pydantic import BaseModel, Field


class ParsedFlowStep(BaseModel):
    """Normalized atomic action extracted from free-form user flow text."""

    step_order: int = Field(..., description="1-based sequence order")
    action_type: str = Field(
        ...,
        description="One of: NAVIGATE, CLICK, FILL, SEARCH, VERIFY_UI, VERIFY_API",
    )
    target_keyword: str = Field("", description="Target button, tab, link, or component name")
    input_value: str = Field("", description="Value to type/search if action is FILL/SEARCH")
    expected_status_codes: List[int] = Field(
        default_factory=list,
        description="Target HTTP status codes expected (e.g., [200, 201])",
    )


class TestStepSpec(BaseModel):
    """Detailed automated test execution step with multi-language locators."""

    step_number: int = Field(..., description="1-based sequence number")
    action: str = Field(..., description="Action verb: NAVIGATE, CLICK, FILL, SEARCH, VERIFY_UI, VERIFY_API")
    description: str = Field(..., description="Human-readable test step narrative")
    element_name: str = Field("", description="Human-friendly element identifier")
    locators: Dict[str, str] = Field(
        default_factory=dict,
        description="Map of language ('python', 'java', 'ts', 'js') to exact Playwright locator syntax",
    )
    input_data: str = Field("", description="Input string, keypress, or payload")
    api_url_pattern: str = Field("", description="Matching API URL or endpoint regex")
    expected_status_codes: List[int] = Field(
        default_factory=list,
        description="List of acceptable HTTP status codes",
    )


class TestScenarioSpec(BaseModel):
    """A cohesive test case / scenario adhering to IEEE 829 specification."""

    scenario_id: str = Field(..., description="E.g., 'TC-01', 'TC-02'")
    title: str = Field(..., description="Descriptive scenario title")
    category: str = Field(
        ...,
        description="Category: 'Positive E2E', 'API Verification', 'UI Element Check', 'Negative/Boundary'",
    )
    steps: List[TestStepSpec] = Field(default_factory=list)


class AgentState(TypedDict, total=False):
    """Shared state dictionary passed across the LangGraph pipeline nodes."""

    # Inputs
    target_url: str
    user_flow_text: str
    target_languages: List[str]
    output_dir: str
    headless: bool
    generate_test_plan: bool
    generate_scripts: bool
    progress_callback: Any  # Callable[[str, float, str], None]

    # Node outputs
    parsed_flow_steps: List[Dict[str, Any]]  # Serialized ParsedFlowStep dicts
    inspection_report: Dict[str, Any]       # Serialized InspectionReport dict
    test_plan_markdown: str                 # Full IEEE 829 Markdown document
    test_scenarios: List[Dict[str, Any]]    # Serialized TestScenarioSpec dicts
    generated_files: List[str]              # Paths of created assets
    errors: List[str]                       # Accumulated pipeline errors

