# generated: 2026-01-03
# System Auto: last updated on: 2026-01-09T21:58:50
"""
HAIOS Modules Package.

Contains the core modules for HAIOS Chariot Architecture:
- GovernanceLayer (E2-240): Policy enforcement, gate checks, transition validation
- MemoryBridge (E2-241, E2-253): MCP wrapper, query modes, auto-link
- WorkEngine (E2-242, E2-251): Work file ownership, lifecycle management
- CascadeEngine (E2-279): Completion cascade, unblock, milestone tracking
- PortalManager (E2-279): Portal REFS.md management
- SpawnTree (E2-279): Spawn tree traversal and formatting
- BackfillEngine (E2-279): Backlog content backfill
- ContextLoader (E2-254): L0-L4 context loading, session tracking
- CycleRunner (E2-255): Phase gate validation, cycle phase lookup
"""
from .governance_layer import GovernanceLayer, GateResult
from .memory_bridge import MemoryBridge, QueryResult, StoreResult
from .work_engine import WorkEngine, WorkState, InvalidTransitionError, WorkNotFoundError
from .cascade_engine import CascadeEngine, CascadeResult  # E2-279
from .portal_manager import PortalManager  # E2-279
from .spawn_tree import SpawnTree  # E2-279
from .backfill_engine import BackfillEngine  # E2-279
from .context_loader import ContextLoader, GroundedContext
from .cycle_runner import CycleRunner, CycleResult

__all__ = [
    "GovernanceLayer",
    "GateResult",
    "MemoryBridge",
    "QueryResult",
    "StoreResult",
    "WorkEngine",
    "WorkState",
    "InvalidTransitionError",
    "WorkNotFoundError",
    "CascadeEngine",  # E2-279
    "CascadeResult",  # E2-279
    "PortalManager",  # E2-279
    "SpawnTree",  # E2-279
    "BackfillEngine",  # E2-279
    "ContextLoader",
    "GroundedContext",
    "CycleRunner",
    "CycleResult",
]
