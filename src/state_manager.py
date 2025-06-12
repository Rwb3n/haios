from __future__ import annotations

"""Compatibility shim for legacy imports.

Historically, some test suites imported ``StateManager`` directly from ``src.state_manager``.
The actual implementation was moved to ``src.utils.state_manager`` during the
Phase-1 refactor (ADR-006 / ADR-013).  To preserve backward-compatibility and
avoid widespread import churn, this thin wrapper simply re-exports the real
``StateManager`` class.  No new logic is added and all public symbols remain
unchanged.
"""

from src.utils.state_manager import (  # type: ignore[F401]
    StateManager,
)

__all__ = ["StateManager"]
