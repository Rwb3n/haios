# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:32:13
# Chapter: Ceremony Lifecycle Distinction

## Definition

**Chapter ID:** CH-013
**Arc:** ceremonies
**Status:** Planned
**Implementation Type:** CREATE NEW (CeremonyRunner doesn't exist)
**Depends:** CH-011, Lifecycles:CH-001
**Work Items:** None

---

## Current State (Verified)

**Source:** `.claude/haios/modules/cycle_runner.py`, `.claude/skills/`

Only CycleRunner exists, no CeremonyRunner:

```python
# cycle_runner.py - handles both lifecycles AND ceremony-like skills
class CycleRunner:
    """Stateless phase gate validator for cycle skills."""
```

**Naming analysis:**
- `close-work-cycle` - ceremony (state change), misnamed as cycle
- `work-creation-cycle` - ceremony (creates work), misnamed as cycle
- `implementation-cycle` - true lifecycle (produces artifacts)
- `investigation-cycle` - true lifecycle (produces findings)
- `checkpoint-cycle` - ceremony (state change)
- `observation-capture-cycle` - ceremony (captures observations)

**What exists:**
- CycleRunner handles everything
- "-cycle" suffix used for both lifecycles and ceremonies
- No separate CeremonyRunner class

**What doesn't exist:**
- CeremonyRunner class
- `type: lifecycle|ceremony` in skill frontmatter
- Clear naming convention enforcement

---

## Problem

CycleRunner handles both lifecycles (artifact production) and ceremonies (state changes). No code distinction exists.

---

## Agent Need

> "I need ceremonies and lifecycles to be clearly distinct so I know: lifecycles produce artifacts (WHAT), ceremonies produce state changes (WHEN)."

---

## Requirements

### R1: Clear Distinction (REQ-CEREMONY-003)

| Concept | Purpose | Produces | Examples |
|---------|---------|----------|----------|
| Lifecycle | Transform work | Artifacts | Findings, Spec, Code |
| Ceremony | Govern transitions | State changes | Status update, Event log |

### R2: Naming Convention

- Lifecycles: `{type}-lifecycle` or just `{type}` (investigation, design, implementation)
- Ceremonies: `{action}-ceremony` (close-work-ceremony, session-start-ceremony)

Rename existing conflated names:
- `close-work-cycle` → `close-work-ceremony`
- `work-creation-cycle` → `intake-ceremony`

### R3: Invocation Separation

Lifecycles and ceremonies have different invocation patterns:

```python
# Lifecycle - returns artifact
output = cycle_runner.run(work_id, lifecycle="design")

# Ceremony - performs state change
ceremony_runner.invoke("close-work", work_id=work_id)
```

---

## Interface

### CeremonyRunner (New)

```python
class CeremonyRunner:
    """Execute ceremonies with boundary enforcement."""

    def invoke(self, ceremony: str, **inputs) -> CeremonyResult:
        """
        Invoke ceremony with inputs.
        Validates contract, executes within boundary, logs events.
        """
        with ceremony_context(ceremony):
            # Validate input contract
            # Execute ceremony
            # Validate output contract
            return result
```

### Separation in Code

```python
# Clear module separation
from cycles import CycleRunner      # For lifecycles
from ceremonies import CeremonyRunner  # For ceremonies

# Usage
cycle_runner = CycleRunner()
ceremony_runner = CeremonyRunner()

# Lifecycle produces artifact
spec = cycle_runner.run(work_id, "design")

# Ceremony produces state change
ceremony_runner.invoke("close-work", work_id=work_id)
```

### Documentation Pattern

Each skill/cycle file must declare:
```yaml
---
type: lifecycle  # or ceremony
---
```

---

## Success Criteria

- [ ] CeremonyRunner class separate from CycleRunner
- [ ] Naming convention applied (ceremony vs lifecycle)
- [ ] Existing "-cycle" ceremonies renamed to "-ceremony"
- [ ] Each skill declares type: lifecycle or ceremony
- [ ] No artifact production in ceremonies
- [ ] No state changes in lifecycles (only via ceremony calls)
- [ ] Unit tests verify separation
- [ ] Documentation updated with distinction

---

## Non-Goals

- Changing what ceremonies/lifecycles do (just clarifying separation)
- Preventing ceremonies from being called within lifecycles (they can be)
- Automated refactoring of all names (manual review needed)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-003)
- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-001-LifecycleSignature.md (lifecycle definition)
