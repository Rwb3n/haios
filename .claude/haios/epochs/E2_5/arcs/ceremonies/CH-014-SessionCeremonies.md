# generated: 2026-02-03
# System Auto: last updated on: 2026-02-11T20:00:00
# Chapter: Session Ceremonies

## Definition

**Chapter ID:** CH-014
**Arc:** ceremonies
**Status:** Complete
**Completed:** 2026-02-11 (Session 343)
**Implementation Type:** PARTIAL (skills exist, ceremony wrapper doesn't)
**Depends:** CH-011
**Work Items:** WORK-120

---

## Current State (Verified)

**Source:** `.claude/skills/`, `.claude/commands/`

Session-related skills exist:
- `/coldstart` command → invokes `coldstart` skill
- `checkpoint-cycle` skill exists with SCAFFOLD→FILL→VERIFY→CAPTURE→COMMIT phases
- `survey-cycle` for work selection after coldstart

**What exists:**
- `coldstart` skill loads context, increments session number
- `checkpoint-cycle` creates checkpoint documents
- `just session-start N` / `just session-end N` bash commands
- governance-events.jsonl logs some events

**What doesn't exist:**
- Formal `session-start-ceremony` with contract
- `session-end-ceremony` (sessions end when context window exhausts)
- `SessionState` type definition
- Orphan work detection on session end

**Session state tracking:**
- `.claude/session` contains session number (integer)
- No structured SessionState object

---

## Problem

Coldstart and checkpoint work but aren't formal ceremonies. No session end ceremony exists. SessionState type needs definition.

---

## Agent Need

> "I need formal session ceremonies so session boundaries are governed, context is properly loaded/saved, and session state is traceable."

---

## Requirements

### R1: Three Session Ceremonies

| Ceremony | Signature | When |
|----------|-----------|------|
| Session Start | `Config → SessionState` | Beginning of session |
| Session End | `SessionState → Log` | End of session |
| Checkpoint | `SessionState → CheckpointDoc` | Mid-session save |

### R2: Session Start Ceremony

```yaml
input_contract:
  - field: config_path
    type: path
    required: false
    default: ".claude/haios/config/haios.yaml"
output_contract:
  - field: session_id
    type: integer
  - field: session_state
    type: SessionState
side_effects:
  - "Log SessionStarted event"
  - "Load context files"
  - "Set current_session in status"
```

### R3: Session End Ceremony

```yaml
input_contract:
  - field: session_state
    type: SessionState
    required: true
output_contract:
  - field: session_log
    type: path
side_effects:
  - "Log SessionEnded event"
  - "Check for orphan work (active items not closed)"
  - "Update session count in status"
```

### R4: Checkpoint Ceremony

```yaml
input_contract:
  - field: session_state
    type: SessionState
    required: true
  - field: summary
    type: string
    required: true
output_contract:
  - field: checkpoint_path
    type: path
side_effects:
  - "Write checkpoint document"
  - "Git commit checkpoint"
  - "Log CheckpointCreated event"
```

### R5: SessionState Type Definition

**NOTE:** This type must be defined as prerequisite.

```python
@dataclass
class SessionState:
    """Session state for ceremony contracts."""
    session_id: int
    started_at: datetime
    epoch: str                    # E2.5
    active_work: List[str]        # Work IDs currently in working queue
    completed_work: List[str]     # Work IDs completed this session
    checkpoints: List[str]        # Checkpoint paths created
    pending: List[str]            # Items to carry forward
    memory_refs: List[int]        # Concept IDs relevant to session
```

---

## Interface

### Session Start

```python
# Invocation (replaces /coldstart)
result = ceremony_runner.invoke("session-start")
session_id = result.session_id
```

### Session End

```python
# Invocation
result = ceremony_runner.invoke("session-end", session_state=current_state)
if result.orphan_work:
    warn(f"Orphan work items: {result.orphan_work}")
```

### Checkpoint

```python
# Invocation (replaces /new-checkpoint)
result = ceremony_runner.invoke("checkpoint",
    session_state=current_state,
    summary="E2.5 chapters created"
)
checkpoint_path = result.checkpoint_path
```

### Skill Files

```
skills/
  session-start-ceremony.md
  session-end-ceremony.md
  checkpoint-ceremony.md
```

---

## Success Criteria

- [x] Session Start ceremony implemented with contract
- [x] Session End ceremony implemented with contract
- [x] Checkpoint ceremony implemented with contract
- [x] /coldstart uses session-start-ceremony
- [x] /new-checkpoint uses checkpoint-ceremony
- [x] SessionStarted/SessionEnded events logged
- [x] Orphan work detected on session end
- [x] Unit tests for each ceremony (10 tests in test_session_ceremonies.py)
- [ ] ~~Integration test: start → work → checkpoint → end~~ DEFERRED (requires full session lifecycle mock; unit tests provide coverage)

---

## Non-Goals

- Automatic session end detection (manual invocation required)
- Session recovery from crash (that's future work)
- Multi-session support (one session at a time)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-001)
- @.claude/skills/coldstart.md (existing implementation to wrap)
