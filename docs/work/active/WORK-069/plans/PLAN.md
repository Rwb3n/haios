---
template: implementation_plan
status: complete
date: 2026-02-02
backlog_id: WORK-069
title: Decision Traceability Schema Design
author: Hephaestus
lifecycle_phase: plan
session: 283
version: '1.5'
generated: 2025-12-21
last_updated: '2026-02-02T09:08:49'
---
# Implementation Plan: Decision Traceability Schema Design

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: New feature, no existing code to show current state"
     - "SKIPPED: Pure documentation task, no code changes"
     - "SKIPPED: Trivial fix, single line change doesn't warrant detailed design"

     This prevents silent section deletion and ensures conscious decisions.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

Epoch decisions will have structured `assigned_to` fields linking to arcs/chapters, and chapter files will have `implements_decisions` fields, enabling automated verification that all decisions have chapter ownership.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | EPOCH.md, 1+ chapter files (CH-009) |
| Lines of code affected | ~50 | Schema additions to EPOCH.md decisions section |
| New files to create | 2 | CH-009-DecisionTraceability.md, audit-decision-coverage.py |
| Tests to write | 3 | Validation rule tests |
| Dependencies | 2 | audit skill, work-creation-cycle |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Schema is documentation, validation is additive |
| Risk of regression | Low | New fields, no existing behavior changed |
| External dependencies | Low | Pure YAML/markdown changes |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Schema design (EPOCH.md) | 15 min | High |
| Chapter file creation | 15 min | High |
| Validation script | 30 min | Medium |
| Integration wiring | 20 min | Medium |
| **Total** | ~80 min | |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/haios/epochs/E2_4/EPOCH.md:52-110 - Decisions as prose sections

## Core Decisions (Session 265)

### Decision 1: Five-Layer Hierarchy
[prose description]

### Decision 2: Work Classification (Two-Axis)
[prose description]
```

**Behavior:** Decisions are unstructured prose. No field links decisions to arcs/chapters.

**Result:** 8 epoch decisions exist but none trace to implementing chapters. Decisions can be forgotten during decomposition.

### Desired State

```markdown
# .claude/haios/epochs/E2_4/EPOCH.md - Decisions with assigned_to field

## Core Decisions (Session 265)

### Decision 1: Five-Layer Hierarchy
assigned_to:
  - arc: activities
    chapters: [CH-001, CH-002]
  - arc: flow
    chapters: [CH-001]
[prose description]

### Decision 2: Work Classification (Two-Axis)
assigned_to:
  - arc: workuniversal
    chapters: [CH-007]
[prose description]
```

```markdown
# .claude/haios/epochs/E2_4/arcs/flow/CH-009-DecisionTraceability.md

## Definition
**Chapter ID:** CH-009
**Arc:** flow
**implements_decisions:** [D8]  # <-- NEW FIELD
```

**Behavior:** Decisions have structured `assigned_to` linking to arcs/chapters. Chapters have `implements_decisions` back-reference.

**Result:** Bidirectional traceability enables validation that all decisions have chapter ownership.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Decision Without assigned_to Triggers Warning
```python
def test_decision_without_assigned_to_warns():
    """Validation warns when decision lacks assigned_to field."""
    epoch_content = """
### Decision 1: Test Decision
[prose only, no assigned_to]
"""
    result = validate_decision_coverage(epoch_content)
    assert result.warnings == ["Decision 1 has no assigned_to field"]
```

### Test 2: Chapter Without implements_decisions Field Detected
```python
def test_chapter_missing_implements_decisions():
    """Validation detects chapters without implements_decisions."""
    chapter_content = """
**Chapter ID:** CH-001
**Arc:** activities
**Status:** Draft
# No implements_decisions field
"""
    result = validate_chapter_traceability(chapter_content)
    assert result.warnings == ["CH-001 missing implements_decisions field"]
```

### Test 3: Bidirectional Consistency Check
```python
def test_bidirectional_traceability():
    """Decision assigned_to matches chapter implements_decisions."""
    epoch_decisions = {
        "D1": {"assigned_to": [{"arc": "flow", "chapters": ["CH-009"]}]}
    }
    chapter_refs = {
        "flow/CH-009": {"implements_decisions": ["D1"]}
    }
    result = validate_bidirectional(epoch_decisions, chapter_refs)
    assert result.is_consistent
    assert result.orphan_decisions == []
    assert result.orphan_chapters == []
```

---

## Detailed Design

### Component 1: EPOCH.md Decision Schema Extension

**File:** `.claude/haios/epochs/E2_4/EPOCH.md`
**Location:** Lines 52-163 (Core Decisions section)

**Schema Format:**
```markdown
### Decision N: Title

assigned_to:
  - arc: {arc_name}
    chapters: [{chapter_ids}]

[existing prose description]
```

**Field Definition:**
- `assigned_to`: List of arc/chapter mappings (optional - absence triggers warning)
- `arc`: Arc ID (must match directory name in `arcs/`)
- `chapters`: List of chapter IDs that implement this decision

### Component 2: Chapter File Schema Extension

**File:** `.claude/haios/epochs/E2_4/arcs/{arc}/CH-XXX-*.md`
**Location:** Definition section (after Chapter ID, Arc, Status)

**Schema Format:**
```markdown
## Definition

**Chapter ID:** CH-XXX
**Arc:** {arc_name}
**Status:** {status}
**implements_decisions:** [D1, D3, D8]  # <-- NEW FIELD
**Depends:** {dependencies}
```

**Field Definition:**
- `implements_decisions`: List of decision IDs this chapter implements
- Format: `D{N}` where N is the decision number from EPOCH.md

### Component 3: Validation Script

**File:** `.claude/haios/lib/audit_decision_coverage.py`

```python
def validate_decision_coverage(epoch_path: str, arcs_dir: str) -> ValidationResult:
    """
    Validate decision-to-chapter traceability.

    Args:
        epoch_path: Path to EPOCH.md
        arcs_dir: Path to arcs directory

    Returns:
        ValidationResult with warnings and errors
    """
    # 1. Parse decisions from EPOCH.md
    # 2. Extract assigned_to fields
    # 3. Parse chapter files for implements_decisions
    # 4. Check bidirectional consistency
    # 5. Return warnings for gaps
```

**Integration Point:** Add to `just audit-decision-coverage` recipe.

### Component 4: CH-009 Chapter File

**File:** `.claude/haios/epochs/E2_4/arcs/flow/CH-009-DecisionTraceability.md`

Documents the decision traceability ceremony:
- When to assign decisions to chapters (during arc decomposition)
- How to verify coverage (run audit)
- What to do when gaps found

### Call Chain Context

```
/audit skill
    |
    +-> just audit-decision-coverage
    |       |
    |       +-> audit_decision_coverage.py
    |               |
    |               +-> parse_epoch_decisions()
    |               +-> parse_chapter_refs()
    |               +-> validate_bidirectional()
    |
    +-> Report warnings/errors
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Inline `assigned_to` in prose | YAML-like block after header | Keeps decisions readable, doesn't require full YAML frontmatter |
| Warning not error for missing | Soft enforcement | Existing decisions lack field - hard error would block all work |
| Bidirectional validation | Check both directions | Catches orphan decisions AND orphan chapter claims |
| Separate validation script | New file in lib/ | Follows Module-First principle, reusable |

### Input/Output Examples

**Current State (real data from EPOCH.md):**
```
8 decisions defined (D1-D8)
0 decisions have assigned_to field
0 chapters have implements_decisions field
Result: 100% orphan decisions
```

**After Implementation:**
```
8 decisions defined
8 decisions have assigned_to (once populated)
~11 chapters have implements_decisions
Result: Bidirectional traceability verified
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Decision with empty assigned_to | Warning: "D1 has empty assigned_to" | Test 1 variant |
| Chapter claims decision not in EPOCH | Error: "CH-009 claims D99 which doesn't exist" | Test 3 |
| Multiple chapters for one decision | Valid: Many chapters can implement one decision | Test 3 |
| Decision spans multiple arcs | Valid: assigned_to is a list | By design |

### Open Questions

**Q: Should we migrate existing decisions to have assigned_to now?**

Answer: Yes, but as separate follow-up. This work establishes the schema. Populating existing decisions is a data migration task that should be done incrementally.

---

## Open Decisions (MUST resolve before implementation)

**SKIPPED:** No operator_decisions in work item frontmatter. All design choices documented in Key Design Decisions above.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_decision_traceability.py`
- [ ] Add Test 1: `test_decision_without_assigned_to_warns`
- [ ] Add Test 2: `test_chapter_missing_implements_decisions`
- [ ] Add Test 3: `test_bidirectional_traceability`
- [ ] Verify all tests fail (red)

### Step 2: Create Validation Script
- [ ] Create `.claude/haios/lib/audit_decision_coverage.py`
- [ ] Implement `parse_epoch_decisions(epoch_path)` - extract decision IDs and assigned_to
- [ ] Implement `parse_chapter_refs(arcs_dir)` - extract implements_decisions from chapters
- [ ] Implement `validate_bidirectional(decisions, chapters)` - check consistency
- [ ] Tests 1, 2, 3 pass (green)

### Step 3: Add Schema to EPOCH.md (Example)
- [ ] Add `assigned_to` to Decision 8 (Multi-Level Governance) as example
- [ ] Format: `assigned_to:\n  - arc: flow\n    chapters: [CH-009, CH-010, CH-011]`
- [ ] Verify validation script parses it correctly

### Step 4: Create CH-009 Chapter File
- [ ] Create `.claude/haios/epochs/E2_4/arcs/flow/CH-009-DecisionTraceability.md`
- [ ] Add `implements_decisions: [D8]` field
- [ ] Document the decision traceability ceremony

### Step 5: Wire Validation into Audit
- [ ] Add `audit-decision-coverage` recipe to justfile
- [ ] Update `/audit` skill to include decision coverage check
- [ ] Run full audit to verify integration

### Step 6: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/lib/README.md` with new script
- [ ] **MUST:** Update `.claude/haios/epochs/E2_4/arcs/flow/ARC.md` with CH-009
- [ ] **MUST:** Verify README content matches actual file state

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Schema format ambiguity (inline YAML vs frontmatter) | Medium | Document exact format in CH-009, provide examples |
| Parsing complexity for inline YAML blocks | Medium | Use simple regex extraction, not full YAML parser |
| Existing decisions lack assigned_to | Low | Warning not error - gradual adoption |
| Chapter files have inconsistent format | Low | Parse with fallback, warn on parse failure |
| Integration with audit skill incomplete | Medium | Test integration end-to-end before closing |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-069/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| EPOCH.md Decision Schema - Add `assigned_to` field | [ ] | Read EPOCH.md, verify D8 has assigned_to |
| Chapter implements_decisions Field | [ ] | Read CH-009, verify implements_decisions exists |
| Validation Rule - Decision without assigned_to triggers warning | [ ] | Run test, verify warning generated |
| Validation Integration - Wire into audit skill | [ ] | Run `/audit`, verify decision coverage check runs |
| CH-009 Chapter File - Document ceremony | [ ] | Read CH-009, verify ceremony documented |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/audit_decision_coverage.py` | Functions exist: parse_*, validate_* | [ ] | |
| `tests/test_decision_traceability.py` | 3 tests exist and pass | [ ] | |
| `.claude/haios/epochs/E2_4/EPOCH.md` | D8 has assigned_to field | [ ] | |
| `.claude/haios/epochs/E2_4/arcs/flow/CH-009-DecisionTraceability.md` | Chapter file exists, has implements_decisions | [ ] | |
| `.claude/haios/epochs/E2_4/arcs/flow/ARC.md` | CH-009 listed in Chapters table | [ ] | |
| `.claude/haios/lib/README.md` | **MUST:** Lists audit_decision_coverage.py | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest [test_file] -v
# Expected: X tests passed
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.
> **E2-290 Learning (Session 192):** "Tests pass" ≠ "Deliverables complete". Agent declared victory after tests passed but skipped 2 of 7 deliverables.

---

## References

- @docs/work/active/WORK-055/WORK.md (source investigation - Pattern 1)
- @.claude/haios/epochs/E2_4/EPOCH.md (target file for schema)
- @.claude/haios/epochs/E2_4/arcs/flow/ARC.md (parent arc)
- @.claude/haios/epochs/E2_4/arcs/flow/CH-006-chapter-flow.md (chapter format example)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-TRACE-005)

---
