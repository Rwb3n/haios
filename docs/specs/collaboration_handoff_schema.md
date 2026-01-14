# generated: 2025-12-02
# System Auto: last updated on: 2025-12-02 21:55:34
# Collaboration Handoff Schema

**Version:** 1.0.0
**Status:** Active
**Created:** Session 19 (2025-12-02)

---

## Overview

This schema defines the protocol for agent-to-agent collaboration in HAIOS.
It enables structured handoffs between agents (e.g., Interpreter -> Ingester).

## Design Decisions

- **DD-018:** Synchronous handoff for MVP (Interpreter waits for Ingester result)
- **DD-020:** Hybrid architecture (Python modules with MCP wrappers)

---

## Schema Definition

### CollaborationHandoff

```yaml
collaboration_handoff:
  # Unique identifier for this handoff
  handoff_id: string (UUID)

  # Source agent creating the handoff
  from_agent: string

  # Target agent to execute the task
  to_agent: string

  # Timestamp when handoff was created
  created_at: datetime (ISO 8601)

  # Task payload
  payload:
    # The directive or command
    directive: object
    # Optional context from source agent
    context: object (optional)
    # Raw input that triggered this chain
    original_input: string (optional)

  # Expected output schema (for validation)
  expected_output_schema:
    type: string
    properties: object

  # Timeout in milliseconds (default: 30000)
  timeout_ms: integer

  # Current status
  status: enum [pending, accepted, completed, failed, timeout]
```

### CollaborationResult

```yaml
collaboration_result:
  # References the handoff
  handoff_id: string (UUID)

  # Agent that executed the task
  executed_by: string

  # Execution timestamp
  executed_at: datetime (ISO 8601)

  # Result status
  status: enum [success, partial, error]

  # Result payload (matches expected_output_schema)
  result: object

  # Error details if failed
  error: object (optional)
    message: string
    error_type: enum [retryable, permanent, unknown]
```

---

## Python Dataclasses

```python
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from enum import Enum
from datetime import datetime
import uuid

class HandoffStatus(Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"

class ResultStatus(Enum):
    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"

@dataclass
class HandoffPayload:
    directive: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    original_input: Optional[str] = None

@dataclass
class CollaborationHandoff:
    from_agent: str
    to_agent: str
    payload: HandoffPayload
    handoff_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    timeout_ms: int = 30000
    status: HandoffStatus = HandoffStatus.PENDING
    expected_output_schema: Optional[Dict[str, Any]] = None

@dataclass
class CollaborationResult:
    handoff_id: str
    executed_by: str
    status: ResultStatus
    result: Dict[str, Any]
    executed_at: datetime = field(default_factory=datetime.utcnow)
    error: Optional[Dict[str, Any]] = None
```

---

## Usage Examples

### Interpreter creates handoff to Ingester

```python
from haios_etl.agents.collaboration import (
    CollaborationHandoff, HandoffPayload, Collaborator
)

# Interpreter creates handoff after translating intent
handoff = CollaborationHandoff(
    from_agent="interpreter-v1",
    to_agent="ingester-v1",
    payload=HandoffPayload(
        directive={"action": "ingest", "type": "episteme"},
        context={"confidence": 0.85, "grounded": True},
        original_input="Store this ADR as knowledge"
    ),
    timeout_ms=30000
)

# Execute handoff (synchronous for MVP)
collaborator = Collaborator(db_manager=db_manager)
result = collaborator.execute_handoff(handoff)
```

### Ingester handles handoff

```python
# Ingester receives handoff and executes
def handle_handoff(handoff: CollaborationHandoff) -> CollaborationResult:
    ingester = Ingester(db_manager=db_manager)

    # Extract parameters from directive
    content = handoff.payload.directive.get("content", "")
    source_path = handoff.payload.directive.get("source_path", "handoff")
    content_type = handoff.payload.directive.get("type", "unknown")

    # Execute ingestion
    ingestion_result = ingester.ingest(content, source_path, content_type)

    return CollaborationResult(
        handoff_id=handoff.handoff_id,
        executed_by="ingester-v1",
        status=ResultStatus.SUCCESS,
        result=asdict(ingestion_result)
    )
```

---

## Error Handling

| Error Type | Action | Example |
|------------|--------|---------|
| TIMEOUT | Return partial result, log warning | Agent took > 30s |
| RETRYABLE | Retry up to 3 times | Rate limit, connection error |
| PERMANENT | Fail immediately, return error | Invalid payload, auth error |

---

## References

- [GAP-A4 Specification](../handoff/2025-12-01-GAP-CLOSER-remaining-system-gaps.md)
- [DD-018: Synchronous Collaboration](../handoff/2025-12-01-VALIDATION-interpreter-ingester-implementation.md)
- [Agent Ecosystem Plan](../plans/PLAN-AGENT-ECOSYSTEM-001.md)
