"""Typed data structures shared across the agent pipeline.

These models are the contract between the browser inspection engine (Phase 1)
and the downstream deterministic code generators (later phases).
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

from pydantic import BaseModel, ConfigDict, Field

#: Languages for which locator syntax is generated.
SUPPORTED_LANGUAGES: tuple[str, ...] = ("python", "java", "ts", "js")

#: Corporate locator priority (highest first).
LOCATOR_PRIORITY: tuple[str, ...] = (
    "data-testid",
    "id",
    "role",
    "placeholder",
    "label",
    "text",
    "css",
)


class DOMElement(BaseModel):
    """A visible, interactive element discovered on the inspected page."""

    model_config = ConfigDict(extra="forbid")

    element_id: str = Field(..., description="Deterministic id within the report, e.g. 'e7'.")
    tag: str = Field(..., description="Lower-case HTML tag name.")
    role: str = Field("", description="Explicit or implicit ARIA role.")
    text_or_label: str = Field("", description="Accessible name / visible text / placeholder.")
    input_type: str = Field("", description="`type` attribute for <input>, else empty.")
    attributes: Dict[str, str] = Field(default_factory=dict)
    recommended_locator: Dict[str, str] = Field(
        default_factory=dict,
        description="Language ('python'|'java'|'ts'|'js') -> exact Playwright locator code.",
    )
    locator_strategy: str = Field(
        "", description="Which priority strategy produced the locator (see LOCATOR_PRIORITY)."
    )


class CapturedAPI(BaseModel):
    """An XHR / fetch call observed while inspecting the page."""

    model_config = ConfigDict(extra="forbid")

    url: str
    method: str
    resource_type: str
    status_code: int = Field(..., description="HTTP status; 0 means the request failed at network level.")
    request_payload_keys: List[str] = Field(default_factory=list)
    response_keys: List[str] = Field(default_factory=list)
    triggered_by_action: str = Field("page_load")


class InspectionReport(BaseModel):
    """Full result of a single URL inspection."""

    model_config = ConfigDict(extra="forbid")

    target_url: str
    page_title: str = ""
    elements: List[DOMElement] = Field(default_factory=list)
    captured_apis: List[CapturedAPI] = Field(default_factory=list)
    aria_snapshot: str = ""
    # --- additional metadata (optional, useful for downstream phases) ---
    browser_channel: str = Field("", description="'chrome', 'msedge' or 'chromium'.")
    probes_executed: List[str] = Field(default_factory=list)
    inspected_at: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat(timespec="seconds")
    )

