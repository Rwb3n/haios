# generated: 2026-01-02
# System Auto: last updated on: 2026-01-02T20:11:33
# Section 17.14: Event Schemas

Generated: 2026-01-02 (Session 156)
Purpose: Define JSON schemas for all inter-module events
Status: DESIGN
Resolves: G2 (Event Schema)

---

## Overview

This section defines formal JSON schemas for the 7 inter-module events identified in Section 17.9. Events enable loose coupling between modules while maintaining well-defined contracts.

---

## Event System Design

### Event Envelope

All events share a common envelope structure:

```json
{
  "type": "EVENT_TYPE",
  "timestamp": "2026-01-02T20:25:00.000Z",
  "session": 156,
  "payload": { ... }
}
```

### Event Storage

Events are persisted to `.claude/haios-events.jsonl` (one JSON object per line).

### Event Versioning

Each event type has a `version` field for schema evolution:
- Version 1.x: Backward-compatible additions
- Version 2.x: Breaking changes (new required fields, type changes)

---

## Event Catalog

| Event | Producer | Consumers | Description |
|-------|----------|-----------|-------------|
| SessionStarted | ContextLoader | GovernanceLayer | New session initialized |
| WorkCreated | WorkEngine | GovernanceLayer | New work item created |
| NodeTransitioned | WorkEngine | MemoryBridge, GovernanceLayer | Work item changed DAG node |
| WorkClosed | WorkEngine | MemoryBridge | Work item archived |
| PhaseEntered | CycleRunner | GovernanceLayer | Cycle entered new phase |
| GatePassed | CycleRunner | GovernanceLayer | Gate check completed |
| CycleCompleted | CycleRunner | WorkEngine | Cycle finished execution |

---

## 17.14.1 SessionStarted

**Producer:** ContextLoader
**Consumers:** GovernanceLayer

**Description:** Emitted when a new session is initialized via coldstart or session recovery.

### Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "type": { "const": "SessionStarted" },
    "version": { "type": "string", "pattern": "^1\\." },
    "timestamp": { "type": "string", "format": "date-time" },
    "session": { "type": "integer", "minimum": 1 },
    "payload": {
      "type": "object",
      "properties": {
        "session_number": {
          "type": "integer",
          "minimum": 1,
          "description": "Current session number"
        },
        "prior_session": {
          "type": ["integer", "null"],
          "minimum": 1,
          "description": "Previous session number (null if first session)"
        },
        "trigger": {
          "type": "string",
          "enum": ["coldstart", "session_recovery"],
          "description": "How the session was initialized"
        },
        "context_loaded": {
          "type": "array",
          "items": { "type": "string" },
          "description": "List of context files loaded (L0-L3)"
        }
      },
      "required": ["session_number", "prior_session", "trigger"],
      "additionalProperties": false
    }
  },
  "required": ["type", "version", "timestamp", "session", "payload"]
}
```

### Example

```json
{
  "type": "SessionStarted",
  "version": "1.0",
  "timestamp": "2026-01-02T20:25:00.000Z",
  "session": 156,
  "payload": {
    "session_number": 156,
    "prior_session": 155,
    "trigger": "coldstart",
    "context_loaded": [
      ".claude/haios/manifesto/L0-telos.md",
      ".claude/haios/manifesto/L1-principal.md",
      ".claude/haios/manifesto/L2-intent.md",
      ".claude/haios/manifesto/L3-requirements.md"
    ]
  }
}
```

---

## 17.14.2 WorkCreated

**Producer:** WorkEngine
**Consumers:** GovernanceLayer

**Description:** Emitted when a new work item is created via `/new-work` or work-creation-cycle.

### Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "type": { "const": "WorkCreated" },
    "version": { "type": "string", "pattern": "^1\\." },
    "timestamp": { "type": "string", "format": "date-time" },
    "session": { "type": "integer", "minimum": 1 },
    "payload": {
      "type": "object",
      "properties": {
        "work_id": {
          "type": "string",
          "pattern": "^(E2-\\d{3}|INV-\\d{3})$",
          "description": "Work item identifier"
        },
        "title": {
          "type": "string",
          "minLength": 1,
          "description": "Work item title"
        },
        "category": {
          "type": "string",
          "enum": ["implementation", "investigation", "fix", "refactor"],
          "description": "Work item category"
        },
        "initial_node": {
          "type": "string",
          "enum": ["backlog"],
          "description": "Starting DAG node (always backlog)"
        },
        "spawned_by": {
          "type": ["string", "null"],
          "description": "Parent work item ID if spawned"
        },
        "file_path": {
          "type": "string",
          "description": "Path to WORK.md file"
        }
      },
      "required": ["work_id", "title", "category", "initial_node", "file_path"],
      "additionalProperties": false
    }
  },
  "required": ["type", "version", "timestamp", "session", "payload"]
}
```

### Example

```json
{
  "type": "WorkCreated",
  "version": "1.0",
  "timestamp": "2026-01-02T20:26:00.000Z",
  "session": 156,
  "payload": {
    "work_id": "E2-240",
    "title": "Implement Event Bus",
    "category": "implementation",
    "initial_node": "backlog",
    "spawned_by": "INV-052",
    "file_path": "docs/work/active/E2-240/WORK.md"
  }
}
```

---

## 17.14.3 NodeTransitioned

**Producer:** WorkEngine
**Consumers:** MemoryBridge, GovernanceLayer

**Description:** Emitted when a work item moves from one DAG node to another.

### Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "type": { "const": "NodeTransitioned" },
    "version": { "type": "string", "pattern": "^1\\." },
    "timestamp": { "type": "string", "format": "date-time" },
    "session": { "type": "integer", "minimum": 1 },
    "payload": {
      "type": "object",
      "properties": {
        "work_id": {
          "type": "string",
          "pattern": "^(E2-\\d{3}|INV-\\d{3})$",
          "description": "Work item identifier"
        },
        "from_node": {
          "type": "string",
          "enum": ["backlog", "discovery", "plan", "implement", "close"],
          "description": "Previous DAG node"
        },
        "to_node": {
          "type": "string",
          "enum": ["backlog", "discovery", "plan", "implement", "close"],
          "description": "New DAG node"
        },
        "transition_reason": {
          "type": "string",
          "description": "Why the transition occurred"
        },
        "session_number": {
          "type": "integer",
          "minimum": 1,
          "description": "Session in which transition occurred"
        }
      },
      "required": ["work_id", "from_node", "to_node", "session_number"],
      "additionalProperties": false
    }
  },
  "required": ["type", "version", "timestamp", "session", "payload"]
}
```

### Example

```json
{
  "type": "NodeTransitioned",
  "version": "1.0",
  "timestamp": "2026-01-02T20:27:00.000Z",
  "session": 156,
  "payload": {
    "work_id": "E2-240",
    "from_node": "backlog",
    "to_node": "plan",
    "transition_reason": "Investigation complete, ready for planning",
    "session_number": 156
  }
}
```

---

## 17.14.4 WorkClosed

**Producer:** WorkEngine
**Consumers:** MemoryBridge

**Description:** Emitted when a work item is closed and archived.

### Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "type": { "const": "WorkClosed" },
    "version": { "type": "string", "pattern": "^1\\." },
    "timestamp": { "type": "string", "format": "date-time" },
    "session": { "type": "integer", "minimum": 1 },
    "payload": {
      "type": "object",
      "properties": {
        "work_id": {
          "type": "string",
          "pattern": "^(E2-\\d{3}|INV-\\d{3})$",
          "description": "Work item identifier"
        },
        "outcome": {
          "type": "string",
          "enum": ["completed", "abandoned", "merged"],
          "description": "How the work item was closed"
        },
        "memory_refs": {
          "type": "array",
          "items": { "type": "integer" },
          "description": "Memory concept IDs linked to this work"
        },
        "archive_path": {
          "type": "string",
          "description": "Path where work item was archived"
        },
        "spawned_work": {
          "type": "array",
          "items": { "type": "string" },
          "description": "Work items spawned from this work"
        }
      },
      "required": ["work_id", "outcome", "memory_refs", "archive_path"],
      "additionalProperties": false
    }
  },
  "required": ["type", "version", "timestamp", "session", "payload"]
}
```

### Example

```json
{
  "type": "WorkClosed",
  "version": "1.0",
  "timestamp": "2026-01-02T20:28:00.000Z",
  "session": 156,
  "payload": {
    "work_id": "INV-052",
    "outcome": "completed",
    "memory_refs": [80325, 80326, 80327, 80382, 80383],
    "archive_path": "docs/work/archive/INV-052/",
    "spawned_work": ["E2-240", "E2-241", "E2-242"]
  }
}
```

---

## 17.14.5 PhaseEntered

**Producer:** CycleRunner
**Consumers:** GovernanceLayer

**Description:** Emitted when a cycle enters a new phase.

### Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "type": { "const": "PhaseEntered" },
    "version": { "type": "string", "pattern": "^1\\." },
    "timestamp": { "type": "string", "format": "date-time" },
    "session": { "type": "integer", "minimum": 1 },
    "payload": {
      "type": "object",
      "properties": {
        "cycle_id": {
          "type": "string",
          "description": "Cycle skill identifier"
        },
        "phase": {
          "type": "string",
          "description": "Phase name (e.g., PLAN, DO, CHECK)"
        },
        "work_id": {
          "type": "string",
          "pattern": "^(E2-\\d{3}|INV-\\d{3})$",
          "description": "Work item being processed"
        },
        "phase_index": {
          "type": "integer",
          "minimum": 0,
          "description": "Index of phase in cycle (0-based)"
        },
        "total_phases": {
          "type": "integer",
          "minimum": 1,
          "description": "Total phases in cycle"
        }
      },
      "required": ["cycle_id", "phase", "work_id"],
      "additionalProperties": false
    }
  },
  "required": ["type", "version", "timestamp", "session", "payload"]
}
```

### Example

```json
{
  "type": "PhaseEntered",
  "version": "1.0",
  "timestamp": "2026-01-02T20:29:00.000Z",
  "session": 156,
  "payload": {
    "cycle_id": "implementation-cycle",
    "phase": "DO",
    "work_id": "E2-240",
    "phase_index": 1,
    "total_phases": 5
  }
}
```

---

## 17.14.6 GatePassed

**Producer:** CycleRunner
**Consumers:** GovernanceLayer

**Description:** Emitted when a gate check completes (pass or fail).

### Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "type": { "const": "GatePassed" },
    "version": { "type": "string", "pattern": "^1\\." },
    "timestamp": { "type": "string", "format": "date-time" },
    "session": { "type": "integer", "minimum": 1 },
    "payload": {
      "type": "object",
      "properties": {
        "gate_id": {
          "type": "string",
          "description": "Gate identifier"
        },
        "gate_type": {
          "type": "string",
          "enum": ["skill", "subagent", "gate"],
          "description": "Type of gate check"
        },
        "outcome": {
          "type": "string",
          "enum": ["passed", "failed", "skipped"],
          "description": "Gate check result"
        },
        "blocking": {
          "type": "boolean",
          "description": "Whether gate failure blocks progress"
        },
        "cycle_id": {
          "type": "string",
          "description": "Cycle that invoked the gate"
        },
        "phase": {
          "type": "string",
          "description": "Phase in which gate was checked"
        },
        "work_id": {
          "type": "string",
          "pattern": "^(E2-\\d{3}|INV-\\d{3})$",
          "description": "Work item being processed"
        },
        "failure_reason": {
          "type": ["string", "null"],
          "description": "Reason for failure (null if passed)"
        }
      },
      "required": ["gate_id", "gate_type", "outcome", "blocking", "cycle_id", "phase", "work_id"],
      "additionalProperties": false
    }
  },
  "required": ["type", "version", "timestamp", "session", "payload"]
}
```

### Example

```json
{
  "type": "GatePassed",
  "version": "1.0",
  "timestamp": "2026-01-02T20:30:00.000Z",
  "session": 156,
  "payload": {
    "gate_id": "preflight-checker",
    "gate_type": "subagent",
    "outcome": "passed",
    "blocking": true,
    "cycle_id": "implementation-cycle",
    "phase": "PLAN",
    "work_id": "E2-240",
    "failure_reason": null
  }
}
```

---

## 17.14.7 CycleCompleted

**Producer:** CycleRunner
**Consumers:** WorkEngine

**Description:** Emitted when a cycle finishes execution (all phases completed or terminated early).

### Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "type": { "const": "CycleCompleted" },
    "version": { "type": "string", "pattern": "^1\\." },
    "timestamp": { "type": "string", "format": "date-time" },
    "session": { "type": "integer", "minimum": 1 },
    "payload": {
      "type": "object",
      "properties": {
        "cycle_id": {
          "type": "string",
          "description": "Cycle skill identifier"
        },
        "work_id": {
          "type": "string",
          "pattern": "^(E2-\\d{3}|INV-\\d{3})$",
          "description": "Work item that was processed"
        },
        "outcome": {
          "type": "string",
          "enum": ["completed", "blocked", "chain", "abandoned"],
          "description": "How the cycle ended"
        },
        "final_phase": {
          "type": "string",
          "description": "Last phase executed"
        },
        "phases_completed": {
          "type": "integer",
          "minimum": 0,
          "description": "Number of phases completed"
        },
        "gates_passed": {
          "type": "integer",
          "minimum": 0,
          "description": "Number of gates passed"
        },
        "gates_failed": {
          "type": "integer",
          "minimum": 0,
          "description": "Number of gates failed"
        },
        "next_cycle": {
          "type": ["string", "null"],
          "description": "Chained cycle (null if terminal)"
        },
        "block_reason": {
          "type": ["string", "null"],
          "description": "Reason for blocking (null if not blocked)"
        }
      },
      "required": ["cycle_id", "work_id", "outcome", "final_phase"],
      "additionalProperties": false
    }
  },
  "required": ["type", "version", "timestamp", "session", "payload"]
}
```

### Example

```json
{
  "type": "CycleCompleted",
  "version": "1.0",
  "timestamp": "2026-01-02T20:31:00.000Z",
  "session": 156,
  "payload": {
    "cycle_id": "implementation-cycle",
    "work_id": "E2-240",
    "outcome": "completed",
    "final_phase": "DONE",
    "phases_completed": 4,
    "gates_passed": 3,
    "gates_failed": 0,
    "next_cycle": "close-work-cycle",
    "block_reason": null
  }
}
```

---

## Event File Schema (events.yaml)

All events should be defined in `.claude/haios/config/events.yaml`:

```yaml
# .claude/haios/config/events.yaml
version: "1.0"

events:
  SessionStarted:
    producer: ContextLoader
    consumers: [GovernanceLayer]
    required_fields: [session_number, prior_session, trigger]
    optional_fields: [context_loaded]

  WorkCreated:
    producer: WorkEngine
    consumers: [GovernanceLayer]
    required_fields: [work_id, title, category, initial_node, file_path]
    optional_fields: [spawned_by]

  NodeTransitioned:
    producer: WorkEngine
    consumers: [MemoryBridge, GovernanceLayer]
    required_fields: [work_id, from_node, to_node, session_number]
    optional_fields: [transition_reason]

  WorkClosed:
    producer: WorkEngine
    consumers: [MemoryBridge]
    required_fields: [work_id, outcome, memory_refs, archive_path]
    optional_fields: [spawned_work]

  PhaseEntered:
    producer: CycleRunner
    consumers: [GovernanceLayer]
    required_fields: [cycle_id, phase, work_id]
    optional_fields: [phase_index, total_phases]

  GatePassed:
    producer: CycleRunner
    consumers: [GovernanceLayer]
    required_fields: [gate_id, gate_type, outcome, blocking, cycle_id, phase, work_id]
    optional_fields: [failure_reason]

  CycleCompleted:
    producer: CycleRunner
    consumers: [WorkEngine]
    required_fields: [cycle_id, work_id, outcome, final_phase]
    optional_fields: [phases_completed, gates_passed, gates_failed, next_cycle, block_reason]
```

---

## Gap Resolution

**G2 Status:** DESIGNED

Event schemas defined:
- [x] Common event envelope structure
- [x] SessionStarted - ContextLoader → GovernanceLayer
- [x] WorkCreated - WorkEngine → GovernanceLayer
- [x] NodeTransitioned - WorkEngine → MemoryBridge, GovernanceLayer
- [x] WorkClosed - WorkEngine → MemoryBridge
- [x] PhaseEntered - CycleRunner → GovernanceLayer
- [x] GatePassed - CycleRunner → GovernanceLayer
- [x] CycleCompleted - CycleRunner → WorkEngine
- [x] events.yaml config file schema

---

*Created Session 156*
