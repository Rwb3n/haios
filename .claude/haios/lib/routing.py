# generated: 2025-12-28
# System Auto: last updated on: 2026-01-28T22:42:24
"""Routing-gate module for HAIOS (E2-221).

Provides pure work-type routing logic for cycle skill CHAIN phases.
Extracts duplicated routing from implementation-cycle, investigation-cycle,
and close-work-cycle into a single reusable component.

Note: Threshold checks are NOT here - they live in OBSERVE phase (E2-224).
This module does pure routing based on work-type signals only.

Functions:
1. determine_route() - Determine routing action based on work-type signals
"""

from typing import Optional


# Valid routing actions
VALID_ACTIONS = {
    "invoke_investigation",
    "invoke_implementation",
    "invoke_work_creation",
    "await_operator",
}


def determine_route(
    next_work_id: Optional[str],
    has_plan: bool,
    work_type: Optional[str] = None
) -> dict:
    """
    Determine routing action based on work-type signals.

    Pure routing logic - no threshold checks (those live in OBSERVE phase per E2-224).

    Routing Decision Table (WORK-030: type field takes precedence):
    | Signal | Action |
    |--------|--------|
    | next_work_id is None | await_operator |
    | type == "investigation" | invoke_investigation |
    | has_plan is True | invoke_implementation |
    | Otherwise | invoke_work_creation |

    Args:
        next_work_id: ID of next work item (None if no work available)
        has_plan: Whether work item has documents.plans populated
        work_type: The `type` field from WORK.md (e.g., "investigation", "implementation")

    Returns:
        dict with keys:
            action: str - One of: invoke_investigation, invoke_implementation,
                          invoke_work_creation, await_operator
            reason: str - Why this action was chosen
    """
    # No work available
    if next_work_id is None:
        return {
            "action": "await_operator",
            "reason": "No unblocked work items. Awaiting operator direction."
        }

    # Investigation routing (type field - WORK-030)
    if work_type == "investigation":
        return {
            "action": "invoke_investigation",
            "reason": f"type: investigation routes to investigation-cycle: {next_work_id}"
        }

    # Implementation routing (has plan)
    if has_plan:
        return {
            "action": "invoke_implementation",
            "reason": f"Work item has plan, routes to implementation-cycle: {next_work_id}"
        }

    # Work creation routing (no plan)
    return {
        "action": "invoke_work_creation",
        "reason": f"Work item has no plan, routes to work-creation-cycle: {next_work_id}"
    }
