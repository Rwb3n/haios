# generated: 2025-12-01
# System Auto: last updated on: 2025-12-02 21:56:56
"""
HAIOS Agent Submodules

This package contains the subagent implementations for the HAIOS Agent Ecosystem.
See docs/plans/PLAN-AGENT-ECOSYSTEM-001.md for architecture.

Agents:
    - Interpreter: Translates operator intent to system directives (DD-012 to DD-014)
    - Ingester: Classifies and stores content in memory (DD-015 to DD-019)
    - Collaborator: Manages agent-to-agent handoffs (DD-018)

Design Decisions:
    - DD-018: Synchronous handoff for MVP
    - DD-020: Hybrid architecture (Python modules + MCP wrappers)
"""
from .interpreter import Interpreter, InterpreterConfig, InterpretationResult
from .ingester import Ingester, IngesterConfig, IngestionResult
from .collaboration import (
    Collaborator,
    CollaborationHandoff,
    CollaborationResult,
    HandoffPayload,
    HandoffStatus,
    ResultStatus,
    CollaborationError,
    register_handler,
    get_handler,
)

__all__ = [
    # Interpreter
    "Interpreter",
    "InterpreterConfig",
    "InterpretationResult",
    # Ingester
    "Ingester",
    "IngesterConfig",
    "IngestionResult",
    # Collaboration
    "Collaborator",
    "CollaborationHandoff",
    "CollaborationResult",
    "HandoffPayload",
    "HandoffStatus",
    "ResultStatus",
    "CollaborationError",
    "register_handler",
    "get_handler",
]
