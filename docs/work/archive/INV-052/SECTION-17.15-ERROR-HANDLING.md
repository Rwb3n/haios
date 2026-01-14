# generated: 2026-01-02
# System Auto: last updated on: 2026-01-02T20:13:36
# Section 17.15: Error Handling

Generated: 2026-01-02 (Session 156)
Purpose: Define error types, propagation, and recovery strategies per module
Status: DESIGN
Resolves: G3 (Error Handling)

---

## Overview

This section specifies what happens when modules fail. Each module has defined:
- Error types it can produce
- Error propagation strategy (fail fast vs graceful degradation)
- Recovery mechanisms
- Error event schema

---

## Design Principles

### 1. Fail Fast for Critical Paths
Operations that could corrupt state should fail immediately with clear error messages.

### 2. Graceful Degradation for Non-Critical
Optional features should degrade gracefully (e.g., memory query timeout → continue without strategies).

### 3. Explicit Error Events
All errors emit events for observability and debugging.

### 4. Idempotent Recovery
Recovery operations should be safe to retry.

---

## Error Types Taxonomy

```yaml
# .claude/haios/config/error-types.yaml
version: "1.0"

error_categories:
  - critical     # Stops execution, requires operator intervention
  - blocking     # Blocks current operation, may retry
  - degraded     # Operation continues with reduced functionality
  - warning      # Logged but no impact on execution

error_codes:
  # ContextLoader errors (CL-xxx)
  CL-001:
    message: "Required context file not found"
    category: critical
    details: "L0-L3 manifesto files must exist"
  CL-002:
    message: "Session number computation failed"
    category: blocking
    details: "Could not determine session from checkpoints"
  CL-003:
    message: "Memory query timeout"
    category: degraded
    details: "Continue without strategy injection"

  # WorkEngine errors (WE-xxx)
  WE-001:
    message: "Work file not found"
    category: critical
    details: "WORK.md does not exist for specified work_id"
  WE-002:
    message: "Invalid node transition"
    category: blocking
    details: "DAG does not allow transition from A to B"
  WE-003:
    message: "YAML parse error"
    category: blocking
    details: "Frontmatter is malformed"
  WE-004:
    message: "Work ID already exists"
    category: blocking
    details: "Cannot create duplicate work item"

  # CycleRunner errors (CR-xxx)
  CR-001:
    message: "Cycle definition not found"
    category: critical
    details: "cycle-definitions.yaml missing or invalid"
  CR-002:
    message: "Gate check failed"
    category: blocking
    details: "Blocking gate returned failure"
  CR-003:
    message: "Subagent invocation failed"
    category: blocking
    details: "Task tool returned error"
  CR-004:
    message: "Chain routing failed"
    category: degraded
    details: "Fallback to await_operator"

  # MemoryBridge errors (MB-xxx)
  MB-001:
    message: "MCP server unavailable"
    category: critical
    details: "haios-memory MCP not responding"
  MB-002:
    message: "Query timeout"
    category: degraded
    details: "Memory query exceeded timeout"
  MB-003:
    message: "Ingestion failed"
    category: blocking
    details: "Content could not be stored"
  MB-004:
    message: "Auto-link failed"
    category: warning
    details: "Memory refs not updated in work file"

  # GovernanceLayer errors (GL-xxx)
  GL-001:
    message: "Handler not found"
    category: warning
    details: "No handler registered for event type"
  GL-002:
    message: "Handler execution failed"
    category: warning
    details: "Handler raised exception"
  GL-003:
    message: "Gate definition not found"
    category: blocking
    details: "gates.yaml missing gate_id"
```

---

## Module-Specific Error Handling

### 17.15.1 ContextLoader

**Responsibility:** Bootstrap context loading

| Error Code | Condition | Propagation | Recovery |
|------------|-----------|-------------|----------|
| CL-001 | L0-L3 file missing | CRITICAL - stop | Operator must create file |
| CL-002 | Checkpoint parse fails | BLOCKING - retry | Re-scan checkpoints, use 1 if none |
| CL-003 | Memory query timeout | DEGRADED | Continue without strategies, log warning |

**Error Flow:**
```
ContextLoader.initialize()
    │
    ├── L0 missing? → emit ErrorOccurred(CL-001) → HALT
    │
    ├── Session calc fails? → emit ErrorOccurred(CL-002) → default to session=1
    │
    └── Memory timeout? → emit ErrorOccurred(CL-003) → continue with empty strategies
```

**Critical Path:** L0-L3 files must exist. No degradation possible.

---

### 17.15.2 WorkEngine

**Responsibility:** Work item state management

| Error Code | Condition | Propagation | Recovery |
|------------|-----------|-------------|----------|
| WE-001 | WORK.md not found | CRITICAL | Operator must create via /new-work |
| WE-002 | Invalid transition | BLOCKING | Return error, stay in current node |
| WE-003 | YAML parse error | BLOCKING | Return error with parse details |
| WE-004 | Duplicate work ID | BLOCKING | Return error, suggest alternate ID |

**Error Flow:**
```
WorkEngine.transition_node(work_id, target_node)
    │
    ├── Work file missing? → emit ErrorOccurred(WE-001) → return Error
    │
    ├── Parse YAML fails? → emit ErrorOccurred(WE-003) → return Error
    │
    ├── Transition invalid? → emit ErrorOccurred(WE-002) → return Error
    │
    └── GovernanceLayer.validate fails? → return Error (from GL)
```

**Single Writer Principle:** All writes go through WorkEngine. Errors here are authoritative.

---

### 17.15.3 CycleRunner

**Responsibility:** Phase execution orchestration

| Error Code | Condition | Propagation | Recovery |
|------------|-----------|-------------|----------|
| CR-001 | Cycle not defined | CRITICAL | Cannot continue cycle |
| CR-002 | Blocking gate failed | BLOCKING | Stay in current phase |
| CR-003 | Subagent failed | BLOCKING | Retry or abort phase |
| CR-004 | Chain routing failed | DEGRADED | Fall back to await_operator |

**Error Flow:**
```
CycleRunner.execute_phase(phase)
    │
    ├── Gate check fails (blocking)?
    │   └── emit GatePassed(outcome="failed") → stay in phase, return BlockedResult
    │
    ├── Subagent invocation fails?
    │   └── emit ErrorOccurred(CR-003) → retry once, then abort
    │
    └── Phase completes → move to next
```

**Gate Failure Behavior:**
- `blocking: true` → Phase cannot proceed, emit error, await resolution
- `blocking: false` → Log warning, continue to next phase

---

### 17.15.4 MemoryBridge

**Responsibility:** MCP wrapper with auto-linking

| Error Code | Condition | Propagation | Recovery |
|------------|-----------|-------------|----------|
| MB-001 | MCP unavailable | CRITICAL | System cannot function |
| MB-002 | Query timeout | DEGRADED | Return empty results |
| MB-003 | Ingestion failed | BLOCKING | Retry, then report failure |
| MB-004 | Auto-link failed | WARNING | Log, continue without linking |

**Error Flow:**
```
MemoryBridge.query(query, mode)
    │
    ├── MCP unavailable? → emit ErrorOccurred(MB-001) → CRITICAL
    │
    └── Timeout? → emit ErrorOccurred(MB-002) → return QueryResult(concepts=[], strategies=[])
```

**Degradation Pattern:** Memory operations should degrade gracefully. Missing strategies is preferable to system halt.

---

### 17.15.5 GovernanceLayer

**Responsibility:** Policy enforcement

| Error Code | Condition | Propagation | Recovery |
|------------|-----------|-------------|----------|
| GL-001 | Handler not found | WARNING | Skip event, log |
| GL-002 | Handler exception | WARNING | Skip handler, continue |
| GL-003 | Gate not defined | BLOCKING | Cannot evaluate gate |

**Error Flow:**
```
GovernanceLayer.on_event(event)
    │
    ├── No handler? → emit ErrorOccurred(GL-001) → log, continue
    │
    └── Handler throws? → emit ErrorOccurred(GL-002) → log, continue
```

**Passive Resilience:** GovernanceLayer is passive and should never block the system. Log errors but continue.

---

## Error Event Schema

All errors emit an `ErrorOccurred` event:

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "properties": {
    "type": { "const": "ErrorOccurred" },
    "version": { "type": "string", "pattern": "^1\\." },
    "timestamp": { "type": "string", "format": "date-time" },
    "session": { "type": "integer", "minimum": 1 },
    "payload": {
      "type": "object",
      "properties": {
        "error_code": {
          "type": "string",
          "pattern": "^(CL|WE|CR|MB|GL)-\\d{3}$",
          "description": "Error code from error-types.yaml"
        },
        "message": {
          "type": "string",
          "description": "Human-readable error message"
        },
        "category": {
          "type": "string",
          "enum": ["critical", "blocking", "degraded", "warning"],
          "description": "Error severity"
        },
        "module": {
          "type": "string",
          "enum": ["ContextLoader", "WorkEngine", "CycleRunner", "MemoryBridge", "GovernanceLayer"],
          "description": "Module that produced the error"
        },
        "context": {
          "type": "object",
          "description": "Additional context (work_id, phase, etc.)"
        },
        "stack_trace": {
          "type": ["string", "null"],
          "description": "Stack trace if available"
        },
        "recoverable": {
          "type": "boolean",
          "description": "Whether automatic recovery is possible"
        }
      },
      "required": ["error_code", "message", "category", "module", "recoverable"]
    }
  },
  "required": ["type", "version", "timestamp", "session", "payload"]
}
```

---

## Recovery Strategies

### Strategy 1: Retry with Backoff
For transient failures (MB-002, CR-003):
```python
for attempt in range(3):
    try:
        result = operation()
        break
    except TransientError:
        sleep(2 ** attempt)
else:
    emit_error_and_abort()
```

### Strategy 2: Fallback Default
For degraded operations (CL-003, MB-002):
```python
try:
    strategies = memory_bridge.query(query)
except Timeout:
    strategies = []  # Continue without strategies
```

### Strategy 3: Operator Escalation
For critical failures (CL-001, WE-001, MB-001):
```python
emit_error_event(critical=True)
# System halts, awaits operator intervention
```

---

## Error Handling in Cycle Phases

Each cycle phase has defined error behavior:

| Phase | On Error | Recovery |
|-------|----------|----------|
| PLAN | Blocking gate fail | Stay in PLAN, await fix |
| DO | Implementation error | Abort DO, remain in phase |
| CHECK | Validation fail | Return to DO for fixes |
| DONE | Memory store fail | Warn, proceed to CHAIN |
| CHAIN | Routing fail | Fallback to await_operator |

---

## Gap Resolution

**G3 Status:** DESIGNED

Error handling specified:
- [x] Error types taxonomy (error-types.yaml)
- [x] Per-module error codes (CL, WE, CR, MB, GL prefixes)
- [x] Error categories (critical, blocking, degraded, warning)
- [x] Propagation strategies per error
- [x] Recovery mechanisms (retry, fallback, escalation)
- [x] ErrorOccurred event schema

---

*Created Session 156*
