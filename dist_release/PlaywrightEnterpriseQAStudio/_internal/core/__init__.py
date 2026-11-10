"""Core engine of the offline Playwright framework generator agent.

Everything in this package runs 100% deterministically and offline:
no LLM APIs, no cloud keys, no model weights.
"""

from core.models import CapturedAPI, DOMElement, InspectionReport
from core.browser_inspector import BrowserInspector

__all__ = ["BrowserInspector", "CapturedAPI", "DOMElement", "InspectionReport"]
__version__ = "0.1.0"

