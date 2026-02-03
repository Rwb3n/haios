# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T19:44:18
# Chapter: Pause Semantics

## Definition

**Chapter ID:** CH-002
**Arc:** lifecycles
**Status:** Planned
**Implementation Type:** REFACTOR
**Depends:** CH-001
**Work Items:** WORK-085

---

## Current State (Verified)

**Source:** `.claude/skills/close-work-cycle/SKILL.md`

close-work-cycle exists with VALIDATE->ARCHIVE->MEMORY->CHAIN phases. The CHAIN phase (lines 164-214) prompts for next action but requires a choice:

```markdown
# From SKILL.md:191-195
5. **Apply routing decision table** (WORK-030: type field is authoritative):
   - If `next_work_id` is None → `await_operator`
   - If `type` == "investigation" → `invoke_investigation`
   - If `has_plan` is True → `invoke_implementation`
   - Else → `invoke_work_creation`
```

**What exists:**
- close-work-cycle accepts closure without spawn (`await_operator` path)
- S27 Breath Model documented in `.claude/haios/epochs/E2_4/architecture/S27-breath-model.md`
- CYCLE_PHASES includes CHAIN phases for most cycles

**What doesn't exist:**
- `is_at_pause_point()` method in WorkEngine
- PAUSE_PHASES mapping
- Explicit recognition that CONCLUDE/COMPLETE/DONE are valid stop points

---

## Problem

While close-work-cycle allows `await_operator`, there's no programmatic way to recognize pause points. The breath model (S27) defines pause as valid completion, but code doesn't enforce this.

Gap to address:
- No PAUSE_PHASES constant mapping lifecycles to their pause phases
- WorkEngine lacks `is_at_pause_point()` method
- S27 phase names (INVESTIGATE, EPISTEMY, DESIGN) don't match lifecycle phases (CONCLUDE, COMPLETE, DONE)

---

## Agent Need

> "I need pause points to be recognized as valid completion states so I can safely stop work without the system treating it as incomplete or stuck."

---

## Requirements

### R1: Pause as Valid Completion (REQ-LIFECYCLE-002)

Per S27 Breath Model rhythm:
```
EXPLORE    [inhale] → SYNTHESIZE [exhale] → [pause: safe to stop]
```

Pause points are valid return positions. Work item can close at pause without "incomplete" status.

### R2: Pause Point Recognition

WorkEngine must recognize pause phases in each lifecycle:

| Lifecycle | Pause Phases | S27 Mapping |
|-----------|--------------|-------------|
| Investigation | After CONCLUDE | exhale complete |
| Design | After COMPLETE | exhale complete |
| Implementation | After DONE | exhale complete |
| Validation | After REPORT | exhale complete |
| Triage | After COMMIT | exhale complete |

**S27 Breath Model Mapping:**

| S27 Phase | Lifecycle Equivalent | Breath |
|-----------|---------------------|--------|
| INVESTIGATE/EXPLORE | EXPLORE, HYPOTHESIZE | inhale |
| EPISTEMY/SYNTHESIZE | CONCLUDE, COMPLETE, DONE, REPORT, COMMIT | exhale |
| [pause] | After exhale phases | safe to stop |

### R3: Clean Closure at Pause

close-work-cycle accepts pause point completion without requiring spawn_next.

---

## Interface

### WorkEngine Changes

```python
# New method
def is_at_pause_point(work_id: str) -> bool:
    """Check if work item is at valid pause point."""
    work = self.get_work(work_id)
    return work.cycle_phase in PAUSE_PHASES[work.lifecycle]

# close-work-cycle integration
def close_work(work_id: str) -> CloseResult:
    if not work_engine.is_at_pause_point(work_id):
        return CloseResult(blocked=True, reason="Not at pause point")
    # ... proceed with closure
```

### Status Values

Pause completion should result in `status: complete` (not `status: paused` or similar).

---

## Success Criteria

- [ ] WorkEngine.is_at_pause_point() implemented
- [ ] Pause phases defined for all 5 lifecycles
- [ ] close-work-cycle accepts pause point closure
- [ ] No warnings/errors when closing at pause
- [ ] Unit tests for pause recognition per lifecycle
- [ ] Integration test: Investigation CONCLUDE → close without spawn → success

---

## Non-Goals

- Resume from pause (that's a new lifecycle start, not continuation)
- Pause mid-phase (pause is always between phases)
- Session-level pause (this is work-item level only)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-LIFECYCLE-002)
- @.claude/haios/epochs/E2_4/architecture/S27-breath-model.md (breath model source)
