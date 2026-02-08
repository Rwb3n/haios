# generated: 2026-02-03
# System Auto: last updated on: 2026-02-05T22:33:47
# Chapter: Template Fracturing

## Definition

**Chapter ID:** CH-006
**Arc:** lifecycles
**Status:** Complete
**Completed:** 2026-02-05 (Session 316)
**Implementation Type:** PARTIAL (investigation done, others need fracturing)
**Depends:** CH-005
**Work Items:** WORK-089, WORK-090, WORK-091, WORK-092

---

## Current State (Verified)

**Source:** `.claude/templates/`

Template structure:
```
.claude/templates/
├── investigation/           # FRACTURED
│   ├── EXPLORE.md          (~53 lines)
│   ├── HYPOTHESIZE.md
│   ├── VALIDATE.md
│   ├── CONCLUDE.md
│   └── README.md
├── implementation_plan.md   # MONOLITHIC (needs fracturing)
├── investigation.md         # LEGACY (fractured version exists)
├── checkpoint.md            # NOT lifecycle (keep as-is)
├── work_item.md             # NOT lifecycle (keep as-is)
└── ... other non-lifecycle templates
```

**What exists:**
- Investigation lifecycle: fully fractured into 4 phase templates
- Each investigation phase template ~50 lines with contracts
- Legacy `investigation.md` still exists (should archive)

**What doesn't exist:**
- Fractured templates for: design, implementation, validation, triage
- ConfigLoader.get_phase_template() method
- Migration of implementation_plan.md to phase-based structure

---

## Problem

Only investigation lifecycle is fractured. Implementation, design, validation, and triage still need fracturing (or don't have templates at all).

---

## Agent Need

> "I need templates fractured by phase so I only load the relevant 30-50 lines for my current phase, not the entire 200+ line lifecycle template."

---

## Requirements

### R1: One Template Per Phase (REQ-TEMPLATE-002)

Fracture existing templates:

```
# Before
templates/
  implementation.md  (200+ lines)

# After
templates/
  implementation/
    PLAN.md      (~40 lines)
    DO.md        (~50 lines)
    CHECK.md     (~40 lines)
    DONE.md      (~30 lines)
```

### R2: Size Constraint

No single template exceeds 100 lines. Target: 30-50 lines per phase.

### R3: Template Discovery

ConfigLoader must support fractured templates:

```python
def get_phase_template(lifecycle: str, phase: str) -> Path:
    """Get path to specific phase template."""
    return Path(f"templates/{lifecycle}/{phase}.md")
```

---

## Interface

### Directory Structure

```
.claude/templates/
├── investigation/
│   ├── EXPLORE.md
│   ├── HYPOTHESIZE.md
│   ├── VALIDATE.md
│   └── CONCLUDE.md
├── design/
│   ├── EXPLORE.md
│   ├── SPECIFY.md
│   ├── CRITIQUE.md
│   └── COMPLETE.md
├── implementation/
│   ├── PLAN.md
│   ├── DO.md
│   ├── CHECK.md
│   └── DONE.md
├── validation/
│   ├── VERIFY.md
│   ├── JUDGE.md
│   └── REPORT.md
└── triage/
    ├── SCAN.md
    ├── ASSESS.md
    ├── RANK.md
    └── COMMIT.md
```

### ConfigLoader Changes

```python
# New methods
def get_phase_template(lifecycle: str, phase: str) -> Path:
    """Get fractured phase template."""

def get_lifecycle_templates(lifecycle: str) -> List[Path]:
    """Get all phase templates for lifecycle."""
```

### Migration

Existing monolithic templates preserved as `_legacy/` for reference during migration.

---

## Success Criteria

- [x] Investigation templates fractured into per-phase files (DONE)
- [x] Investigation phase templates ≤ 100 lines (DONE - ~53 lines each)
- [ ] ConfigLoader.get_phase_template() works
- [ ] Remaining lifecycles fractured:
  - [ ] design/ (EXPLORE, SPECIFY, CRITIQUE, COMPLETE)
  - [ ] implementation/ (PLAN, DO, CHECK, DONE)
  - [ ] validation/ (VERIFY, JUDGE, REPORT)
  - [ ] triage/ (SCAN, ASSESS, RANK, COMMIT)
- [ ] Legacy investigation.md archived to _legacy/
- [ ] Skill loaders updated to use fractured templates
- [ ] Integration test: load PLAN.md → contains only PLAN phase

---

## Non-Goals

- Changing template content (just restructuring)
- Template versioning (that's future work)
- Dynamic template composition (each phase is standalone)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-TEMPLATE-002)
- @.claude/templates/ (current monolithic templates)
