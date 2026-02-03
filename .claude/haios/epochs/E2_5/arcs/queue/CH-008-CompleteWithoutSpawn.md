# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:29:46
# Chapter: Complete Without Spawn

## Definition

**Chapter ID:** CH-008
**Arc:** queue
**Status:** Planned
**Implementation Type:** REFACTOR
**Depends:** CH-007, Lifecycles:CH-004
**Work Items:** None

---

## Current State (Verified)

**Source:** `.claude/skills/close-work-cycle/SKILL.md` (lines 191-200)

close-work-cycle CHAIN phase already has "no spawn" path:

```markdown
# From SKILL.md:191-195
6. **Apply routing decision table** (WORK-030):
   - If `next_work_id` is None → `await_operator`  # THIS IS THE NO-SPAWN PATH
   - If `type` == "investigation" → `invoke_investigation`
   ...
7. Execute the action:
   - `await_operator` -> Report "No unblocked work. Awaiting operator direction."
```

**What exists:**
- `await_operator` path accepts no spawn
- CHAIN phase prompts but doesn't force spawn
- Routing decision table supports `next_work_id = None`

**What doesn't exist:**
- Explicit "store output" option in the prompt
- Output storage mechanism when not spawning (output just exists in work dir)
- Clear UX for "complete without spawn" choice

---

## Problem

The mechanism exists but UX is unclear. `await_operator` happens when no unblocked work exists, not as explicit "I choose not to spawn" option.

Gap: Need explicit "Store output, no spawn" choice, not just fallback to await_operator.

---

## Agent Need

> "I need to close work items that are genuinely complete without being forced to spawn follow-on work. Research can end with findings, design can end with spec."

---

## Requirements

### R1: Valid Terminal State (REQ-QUEUE-002)

"Complete without spawn" is valid terminal state:

```yaml
# Valid final state
status: complete
queue_position: done
spawn_next: null   # Explicitly nothing
```

### R2: close-work-cycle Acceptance

close-work-cycle must accept closure without spawn_next:

```
Work complete. Options:
1. Store output (no spawn) ← VALID CHOICE
2. Chain to next lifecycle
3. Spawn new work item

Choice: 1
→ Work closed. No spawn. Output stored.
```

### R3: No Warnings for No-Spawn

System should not warn when spawn_next is empty. It's a valid choice, not an oversight.

---

## Interface

### close-work-cycle Changes

```python
def close_work(work_id: str, spawn_next: str = None) -> CloseResult:
    """
    Close work item.

    Args:
        work_id: Work to close
        spawn_next: Optional next work ID. None = complete without spawn.
    """
    # Validate DoD
    dod_result = validate_dod(work_id)
    if not dod_result.passed:
        return CloseResult(blocked=True, reason=dod_result.failures)

    # Close work - spawn_next=None is valid
    work_engine.update_work(work_id,
        status="complete",
        queue_position="done",
        spawn_next=spawn_next  # Can be None
    )

    return CloseResult(success=True, spawned=spawn_next)
```

### WORK.md Template

```yaml
---
# spawn_next is optional, empty means "complete standalone"
spawn_next: ~  # YAML null, explicitly no spawn
---
```

### Governance Changes

Remove any rules that:
- Require spawn_next field
- Warn on empty spawn_next
- Treat no-spawn as incomplete

---

## Success Criteria

- [ ] close-work-cycle accepts spawn_next=None
- [ ] No warnings when closing without spawn
- [ ] WORK.md supports null spawn_next
- [ ] Governance doesn't block no-spawn closure
- [ ] Unit tests: close without spawn → success
- [ ] Integration test: Investigation → CONCLUDE → close → no spawn → verify complete

---

## Relationship to Release Ceremony (CH-010)

**DECISION:** close_work() IS the Release ceremony implementation.

| Operation | What it is | Relationship |
|-----------|------------|--------------|
| close_work() | Function in WorkEngine | Implementation |
| Release ceremony | Queue transition working→done | Conceptual model |
| close-work-cycle | Skill that orchestrates closure | Orchestration layer |

```
close-work-cycle skill
    └── calls close_work() function
          └── which IS the Release ceremony
```

**They are NOT separate operations.** The Release ceremony is implemented by close_work().

---

## Output Storage

When closing without spawn, output is stored in work directory:

```
docs/work/active/WORK-XXX/
├── WORK.md           # status: complete
├── plans/PLAN.md     # status: complete
└── output/           # Lifecycle output stored here
    └── specification.md   # Or findings.md, artifact/, etc.
```

No separate "store output" action needed - output is already in work directory.

---

## Non-Goals

- Determining when spawn is appropriate (that's operator judgment)
- Auto-suggesting spawn options (that's ceremony behavior)
- Tracking spawn lineage (that's CH-017 Spawn Ceremony)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-QUEUE-002)
- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-004-CallerChaining.md (caller decides)
