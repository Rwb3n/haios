# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:31:48
# Chapter: Side Effect Boundaries

## Definition

**Chapter ID:** CH-012
**Arc:** ceremonies
**Status:** Planned
**Implementation Type:** CREATE NEW
**Depends:** CH-011
**Work Items:** None

---

## Current State (Verified)

**Source:** `.claude/haios/modules/work_engine.py`, `.claude/haios/modules/governance_layer.py`

State changes happen directly via WorkEngine methods:

```python
# WorkEngine.close() - line ~320
def close(self, work_id: str) -> WorkState:
    """Close a work item (set status=complete, stays in active/)."""
    # Directly updates file, no ceremony context check
```

**What exists:**
- GovernanceLayer with gate checks (dod, preflight, observation)
- governance-events.jsonl for event logging
- PreToolUse/PostToolUse hooks for some enforcement

**What doesn't exist:**
- `ceremony_context()` context manager
- `in_ceremony_context()` check function
- State change blocking outside ceremony context
- `ceremony_enforcement` config toggle

---

## Problem

State-changing methods (WorkEngine.close(), update_work(), etc.) don't check for ceremony context. Any code can mutate state without governance.

---

## Agent Need

> "I need all state changes to occur within ceremony boundaries so I can trust that every mutation is governed, logged, and accountable."

---

## Requirements

### R1: Ceremony-Only State Changes (REQ-CEREMONY-001)

State changes MUST occur within ceremony context:

```python
# BLOCKED - direct state change
work_engine.update_work(work_id, status="complete")

# ALLOWED - within ceremony
with ceremony_context("close-work"):
    work_engine.update_work(work_id, status="complete")
```

### R2: Ceremony Context Manager

All state-changing operations require ceremony context:

```python
@contextmanager
def ceremony_context(ceremony_name: str):
    """
    Context manager for ceremony boundaries.
    All state changes within this context are logged.
    """
    log_event("CeremonyStart", ceremony=ceremony_name)
    try:
        yield CeremonyContext(ceremony_name)
    finally:
        log_event("CeremonyEnd", ceremony=ceremony_name)
```

### R3: Enforcement Modes

Two enforcement levels:
- **warn**: Log warning on out-of-ceremony state change (migration period)
- **block**: Raise error on out-of-ceremony state change (production)

Configurable in haios.yaml:
```yaml
governance:
  ceremony_enforcement: block  # or warn
```

---

## Interface

### Ceremony Context Manager

```python
from governance import ceremony_context

# Usage
with ceremony_context("close-work") as ctx:
    work_engine.update_work(work_id, status="complete")
    ctx.log_side_effect("status_changed", {"from": "active", "to": "complete"})
```

### State Change Functions

All state-changing functions check ceremony context:

```python
def update_work(work_id: str, **fields):
    if not in_ceremony_context():
        if config.ceremony_enforcement == "block":
            raise CeremonyRequiredError("update_work requires ceremony context")
        else:
            log_warning("State change outside ceremony", work_id=work_id)

    # ... actual update
```

### Protected Operations

Operations requiring ceremony context:
- WorkEngine.update_work()
- WorkEngine.create_work()
- WorkEngine.archive()
- log_governance_event()
- Memory commit operations

---

## Success Criteria

- [ ] ceremony_context() manager implemented
- [ ] WorkEngine methods check ceremony context
- [ ] Config toggle for warn/block mode
- [ ] Out-of-ceremony changes logged (warn mode)
- [ ] Out-of-ceremony changes blocked (block mode)
- [ ] All ceremony skills use ceremony_context()
- [ ] Unit tests for boundary enforcement
- [ ] Integration test: state change without ceremony → appropriate response

---

## Ceremony Composition Model

**RESOLUTION:** Ceremonies can COMPOSE but not NEST.

| Pattern | Allowed | Example |
|---------|---------|---------|
| **Composition** | YES | close-work has steps that include observation-capture |
| **Nesting** | NO | ceremony_context("A") containing ceremony_context("B") |

**How composition works:**

```python
# COMPOSITION (allowed) - sequential steps within single ceremony
with ceremony_context("close-work") as ctx:
    # Step 1: Validate DoD
    validate_dod(work_id)

    # Step 2: Capture observations (ceremony step, not nested ceremony)
    ctx.execute_step("observation-capture", work_id=work_id)

    # Step 3: Commit memory
    ctx.execute_step("memory-commit", learnings=learnings)

    # Step 4: Archive
    archive_work(work_id)
```

```python
# NESTING (forbidden) - would create nested contexts
with ceremony_context("close-work"):
    with ceremony_context("observation-capture"):  # BLOCKED
        ...
```

**Key distinction:**
- Composition: Ceremony has steps that reference other ceremony patterns
- Nesting: Ceremony context inside another ceremony context

This resolves the CH-015/CH-016 apparent contradiction - close-work-ceremony COMPOSES observation-capture and memory-commit as steps, it doesn't NEST them.

---

## Non-Goals

- Read operations (reads don't need ceremony context)
- External system calls (only internal state changes)
- True ceremony nesting (contexts within contexts)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-001)
- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-011-CeremonyContracts.md (contract definition)
