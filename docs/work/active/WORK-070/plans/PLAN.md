---
template: implementation_plan
status: approved
date: 2026-02-02
backlog_id: WORK-070
title: Multi-Level DoD Cascade Design
author: Hephaestus
lifecycle_phase: plan
session: 284
version: '1.5'
generated: 2025-12-21
last_updated: '2026-02-02T11:25:00'
---
# Implementation Plan: Multi-Level DoD Cascade Design

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

HAIOS will have multi-level DoD ceremonies (close-chapter, close-arc, close-epoch) that verify completeness at each hierarchy level with formal L4 requirements (REQ-DOD-001, REQ-DOD-002) backing the governance.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `functional_requirements.md`, `EPOCH.md` |
| Lines of code affected | ~30 | New requirements + decision assigned_to |
| New files to create | 4 | 3 skill files + 1 chapter file |
| Tests to write | 6 | 2 per ceremony level (chapter, arc, epoch) |
| Dependencies | 2 | close-work-cycle pattern, audit_decision_coverage.py |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Med | Skills integrate with `just` recipes, audit workflow |
| Risk of regression | Low | New ceremonies, no existing code modified |
| External dependencies | Low | Uses existing HAIOS patterns only |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| L4 Requirements | 15 min | High |
| Chapter DoD Ceremony | 30 min | High |
| Arc DoD Ceremony | 30 min | High |
| Epoch DoD Ceremony | 30 min | High |
| CH-010 Chapter File | 15 min | High |
| Tests | 30 min | Med |
| **Total** | ~2.5 hr | Med |

---

## Current State vs Desired State

### Current State

**DoD exists only at work item level (ADR-033):**

```markdown
# close-work-cycle:53-68 - Current DoD validation
### 1. VALIDATE Phase
**Guardrails (MUST follow):**
1. **Tests MUST pass** - Prompt user to confirm
2. **WHY MUST be captured** - Check for memory_refs
3. **Docs MUST be current** - CLAUDE.md, READMEs updated
4. **Traced files MUST be complete** - Associated plans have status: complete
5. **Traced requirement MUST be addressed** (REQ-TRACE-003)
```

**Behavior:** Only work items have DoD validation. Chapters, arcs, and epochs have no formal closure ceremonies.

**Result:** Work completes but chapter/arc/epoch objectives may not be achieved. "Sum of parts ≠ whole."

### Desired State

**DoD cascade from Work → Chapter → Arc → Epoch:**

```markdown
# Multi-Level DoD Cascade
| Level | DoD Criteria | Ceremony |
|-------|--------------|----------|
| Work Item | Tests pass, runtime consumer, WHY captured | close-work-cycle |
| Chapter | All work complete + exit criteria + implements_decisions | close-chapter-ceremony |
| Arc | All chapters complete + no unassigned decisions | close-arc-ceremony |
| Epoch | All arcs complete + all decisions implemented | close-epoch-ceremony |
```

**Behavior:** Each hierarchy level has formal DoD validation before closure.

**Result:** Guarantees that completing all work items actually achieves chapter/arc/epoch objectives.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: L4 Requirements Exist
```python
def test_req_dod_001_exists():
    """REQ-DOD-001 should exist in functional_requirements.md"""
    content = Path(".claude/haios/manifesto/L4/functional_requirements.md").read_text()
    assert "REQ-DOD-001" in content
    assert "chapter closure" in content.lower()

def test_req_dod_002_exists():
    """REQ-DOD-002 should exist in functional_requirements.md"""
    content = Path(".claude/haios/manifesto/L4/functional_requirements.md").read_text()
    assert "REQ-DOD-002" in content
    assert "arc closure" in content.lower()
```

### Test 2: Ceremony Skill Files Exist
```python
def test_close_chapter_ceremony_exists():
    """close-chapter-ceremony skill should exist with required sections"""
    skill_path = Path(".claude/skills/close-chapter-ceremony/SKILL.md")
    assert skill_path.exists()
    content = skill_path.read_text()
    assert "## The Cycle" in content
    assert "implements_decisions" in content

def test_close_arc_ceremony_exists():
    """close-arc-ceremony skill should exist"""
    skill_path = Path(".claude/skills/close-arc-ceremony/SKILL.md")
    assert skill_path.exists()
    content = skill_path.read_text()
    assert "## The Cycle" in content
    assert "unassigned decisions" in content.lower()

def test_close_epoch_ceremony_exists():
    """close-epoch-ceremony skill should exist"""
    skill_path = Path(".claude/skills/close-epoch-ceremony/SKILL.md")
    assert skill_path.exists()
    content = skill_path.read_text()
    assert "## The Cycle" in content
```

### Test 3: CH-010 Chapter File
```python
def test_ch010_chapter_file_exists():
    """CH-010 chapter file should exist with implements_decisions"""
    ch_path = Path(".claude/haios/epochs/E2_4/arcs/flow/CH-010-MultiLevelDoD.md")
    assert ch_path.exists()
    content = ch_path.read_text()
    assert "implements_decisions" in content
    assert "D8" in content  # From WORK-055: Multi-Level Governance
```

---

## Detailed Design

### Deliverable 1: L4 Requirements (REQ-DOD-001, REQ-DOD-002)

**File:** `.claude/haios/manifesto/L4/functional_requirements.md`
**Location:** After line 41 (after REQ-TEMPLATE-002)

**New Requirements:**
```markdown
| REQ-DOD-001 | DoD | Chapter closure MUST verify all work complete + implements_decisions | L3.7, L3.18 | close-chapter-ceremony |
| REQ-DOD-002 | DoD | Arc closure MUST verify all chapters complete + no orphan decisions | L3.7, L3.18 | close-arc-ceremony |
```

**Full Section to Add (after Template Requirements):**
```markdown
---

## DoD Requirements (E2.4 - Session 284)

*Derived from L3.7 (Traceability) + L3.18 (DoD requirement)*

| ID | Requirement | Derives From | Acceptance Test |
|----|-------------|--------------|-----------------|
| **REQ-DOD-001** | Chapter closure MUST verify all work items complete + implements_decisions match claimed decisions | L3.7, L3.18 | close-chapter-ceremony blocks on incomplete work or unimplemented decisions |
| **REQ-DOD-002** | Arc closure MUST verify all chapters complete + no epoch decisions unassigned to arc | L3.7, L3.18 | close-arc-ceremony blocks on incomplete chapters or orphan decisions |

**Invariants:**
- DoD cascade: Work → Chapter → Arc → Epoch
- Lower level must complete before higher level can close
- Orphan decisions (assigned but not implemented) block closure
```

### Deliverable 2: close-chapter-ceremony Skill

**File:** `.claude/skills/close-chapter-ceremony/SKILL.md`
**Pattern:** Follow close-work-cycle structure (VALIDATE->ARCHIVE->MEMORY)

**Skill Structure:**
```markdown
---
name: close-chapter-ceremony
description: HAIOS Close Chapter Ceremony for verifying chapter DoD. Use when all work items
  in a chapter are complete. Guides VALIDATE->MARK workflow with decision verification.
recipes:
- audit-decision-coverage
generated: 2026-02-02
---
# Close Chapter Ceremony

## When to Use
When all work items assigned to a chapter are complete and you want to verify the chapter
achieved its objectives.

## The Cycle

```
VALIDATE --> MARK --> REPORT
```

### 1. VALIDATE Phase

**DoD Criteria (REQ-DOD-001):**
- [ ] All work items with `chapter: {arc}/{chapter_id}` have `status: complete`
- [ ] Chapter exit criteria (in chapter file) all checked
- [ ] `implements_decisions` all verified via `just audit-decision-coverage`

**Actions:**
1. Read chapter file: `.claude/haios/epochs/{epoch}/arcs/{arc}/{chapter_id}.md`
2. Query work items: `Grep(pattern="chapter: {arc}/{chapter_id}")`
3. Verify each work item has `status: complete`
4. Run `just audit-decision-coverage` - verify no errors for this chapter
5. Check chapter Exit Criteria section - all must be checked

### 2. MARK Phase

**Actions:**
1. Update chapter file `**Status:**` from `Active` to `Complete`
2. Add completion timestamp to chapter file

### 3. REPORT Phase

**Actions:**
1. Report chapter closure summary
2. List any observations from completed work
```

### Deliverable 3: close-arc-ceremony Skill

**File:** `.claude/skills/close-arc-ceremony/SKILL.md`

**Skill Structure:**
```markdown
---
name: close-arc-ceremony
description: HAIOS Close Arc Ceremony for verifying arc DoD. Use when all chapters
  in an arc are complete. Guides VALIDATE->MARK workflow with orphan decision check.
recipes:
- audit-decision-coverage
generated: 2026-02-02
---
# Close Arc Ceremony

## When to Use
When all chapters in an arc are complete and you want to verify the arc achieved its theme.

## The Cycle

```
VALIDATE --> MARK --> REPORT
```

### 1. VALIDATE Phase

**DoD Criteria (REQ-DOD-002):**
- [ ] All chapters in arc have `**Status:** Complete`
- [ ] No epoch decisions assigned to arc are unimplemented (orphan check)
- [ ] Arc exit criteria all checked

**Actions:**
1. Read arc file: `.claude/haios/epochs/{epoch}/arcs/{arc}/ARC.md`
2. Glob chapter files: `.claude/haios/epochs/{epoch}/arcs/{arc}/CH-*.md`
3. Verify each chapter `**Status:**` is `Complete`
4. Run `just audit-decision-coverage` - verify no orphan decisions for this arc
5. Check arc Exit Criteria section - all must be checked

### 2. MARK Phase

**Actions:**
1. Update ARC.md `**Status:**` from `Active`/`Planned` to `Complete`
2. Add completion timestamp

### 3. REPORT Phase

**Actions:**
1. Report arc closure summary
2. List completed chapters
```

### Deliverable 4: close-epoch-ceremony Skill

**File:** `.claude/skills/close-epoch-ceremony/SKILL.md`

**Skill Structure:**
```markdown
---
name: close-epoch-ceremony
description: HAIOS Close Epoch Ceremony for verifying epoch DoD. Use when all arcs
  are complete. Guides VALIDATE->ARCHIVE workflow.
recipes:
- audit-decision-coverage
generated: 2026-02-02
---
# Close Epoch Ceremony

## When to Use
When all arcs in an epoch are complete and you want to transition to a new epoch.

## The Cycle

```
VALIDATE --> ARCHIVE --> TRANSITION
```

### 1. VALIDATE Phase

**DoD Criteria:**
- [ ] All arcs have `**Status:** Complete`
- [ ] All epoch decisions have implementations (via audit-decision-coverage)
- [ ] Epoch exit criteria all checked

**Actions:**
1. Read epoch file: `.claude/haios/epochs/{epoch}/EPOCH.md`
2. Glob arc files: `.claude/haios/epochs/{epoch}/arcs/*/ARC.md`
3. Verify each arc `**Status:**` is `Complete`
4. Run `just audit-decision-coverage` - verify all decisions implemented
5. Check epoch Exit Criteria section - all must be checked

### 2. ARCHIVE Phase

**Actions:**
1. Update EPOCH.md `**Status:**` to `Complete`
2. Move work items from `docs/work/active/` to `docs/work/archive/` (epoch-level cleanup per ADR-041)

### 3. TRANSITION Phase

**Note:** `/new-epoch` command (CH-008) is not yet implemented. This phase is manual until CH-008 completes.

**Actions:**
1. (Future) Create new epoch via `/new-epoch` command (CH-008)
2. (Manual) Update `haios.yaml` epoch.current to new epoch
```

### Deliverable 5: CH-010 Chapter File

**File:** `.claude/haios/epochs/E2_4/arcs/flow/CH-010-MultiLevelDoD.md`

**Content:**
```markdown
# generated: 2026-02-02
# Chapter: MultiLevelDoD

## Definition

**Chapter ID:** CH-010
**Arc:** flow
**Status:** Active
**implements_decisions:** [D8]
**Depends:** CH-009

---

## Problem

How do we verify that completing all work items actually achieves chapter/arc/epoch objectives?

Current state: Only work items have DoD (ADR-033). Chapters, arcs, and epochs can be declared
"done" without verification.

---

## Solution: Multi-Level DoD Ceremonies

Three new ceremonies verify completeness at each hierarchy level:

| Level | Ceremony | DoD Criteria |
|-------|----------|--------------|
| Chapter | close-chapter-ceremony | All work complete + implements_decisions verified |
| Arc | close-arc-ceremony | All chapters complete + no orphan decisions |
| Epoch | close-epoch-ceremony | All arcs complete + all decisions implemented |

---

## Exit Criteria

- [ ] REQ-DOD-001 and REQ-DOD-002 created
- [ ] close-chapter-ceremony skill implemented
- [ ] close-arc-ceremony skill implemented
- [ ] close-epoch-ceremony skill implemented
- [ ] Tests pass

---

## Memory Refs

Session 279: 83018-83029 (multi-level governance investigation)
Session 284: [to be added]

---

## References

- @docs/work/active/WORK-055/WORK.md (source investigation)
- @docs/work/active/WORK-070/WORK.md (this implementation)
- @.claude/haios/epochs/E2_4/arcs/flow/CH-009-DecisionTraceability.md (dependency)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Three separate ceremony skills | One skill per level (chapter/arc/epoch) | Matches close-work-cycle pattern; keeps each ceremony focused |
| VALIDATE->MARK pattern | Simpler than VALIDATE->ARCHIVE->MEMORY | Chapters/arcs/epochs don't need memory capture (work items already captured WHY) |
| Leverage audit-decision-coverage | Use existing script for orphan detection | WORK-069 already built this; don't reinvent |
| REQ-DOD prefix | New requirement domain | Distinguishes from REQ-TRACE (traceability) which is about links, not verification |
| Status field in markdown | `**Status:** Complete` | Consistent with work item `status: complete` (ADR-033). Canonical terminal status is `Complete` (not `Closed` or `Done`). |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Work item with no chapter | Skip in chapter ceremony | N/A (not part of any chapter) |
| Chapter with no work items | Warn, allow closure | Test: empty chapter |
| Arc with planned chapters | Block - chapters must be Active or Complete first | Test: planned chapter blocks arc |
| Epoch decisions without assigned_to | Warn (per CH-009 schema) | Uses audit-decision-coverage |

### Open Questions

**Q: Should close-chapter-ceremony chain to close-arc-ceremony automatically?**

No - manual invocation preferred. Closing a chapter doesn't mean the arc is done. Operator decides when all chapters are ready.

**Q: Is D8 already assigned to CH-010?**

Yes - verified. EPOCH.md Decision 8 (lines 148-150) has `assigned_to: [{arc: flow, chapters: [CH-009, CH-010, CH-011]}]`.

---

## Open Decisions (MUST resolve before implementation)

**SKIPPED:** No operator_decisions in WORK-070 frontmatter. Design follows WORK-055 investigation recommendations.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_multilevel_dod.py`
- [ ] Add 6 tests from Tests First section
- [ ] Verify all tests fail (red)

### Step 2: Create L4 Requirements
- [ ] Edit `.claude/haios/manifesto/L4/functional_requirements.md`
- [ ] Add REQ-DOD-001 and REQ-DOD-002 to registry table (line ~42)
- [ ] Add full DoD Requirements section (after Template Requirements)
- [ ] Tests 1a, 1b pass (green)

### Step 3: Create close-chapter-ceremony Skill
- [ ] Create `.claude/skills/close-chapter-ceremony/SKILL.md`
- [ ] Implement VALIDATE->MARK->REPORT cycle per Detailed Design
- [ ] Test 2a passes (green)

### Step 4: Create close-arc-ceremony Skill
- [ ] Create `.claude/skills/close-arc-ceremony/SKILL.md`
- [ ] Implement VALIDATE->MARK->REPORT cycle per Detailed Design
- [ ] Test 2b passes (green)

### Step 5: Create close-epoch-ceremony Skill
- [ ] Create `.claude/skills/close-epoch-ceremony/SKILL.md`
- [ ] Implement VALIDATE->ARCHIVE->TRANSITION cycle per Detailed Design
- [ ] Test 2c passes (green)

### Step 6: Create CH-010 Chapter File
- [ ] Create `.claude/haios/epochs/E2_4/arcs/flow/CH-010-MultiLevelDoD.md`
- [ ] Add `implements_decisions: [D8]` field
- [ ] Link to WORK-070 as implementing work
- [ ] Test 3 passes (green)

### Step 7: Update ARC.md with CH-010
- [ ] Edit `.claude/haios/epochs/E2_4/arcs/flow/ARC.md`
- [ ] Add CH-010 to Chapters table
- [ ] Verify chapter references parent arc

### Step 8: Integration Verification
- [ ] All 6 tests pass
- [ ] Run full test suite: `pytest tests/` (no regressions)
- [ ] Run `just audit-decision-coverage` (verify no new errors)

### Step 9: README Sync (MUST)
- [ ] **MUST:** Update `.claude/skills/README.md` with 3 new ceremony skills
- [ ] **MUST:** Verify skill descriptions match actual skill functionality

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Ceremony skills not discoverable | Med | Add to skills README, document in CLAUDE.md |
| Over-governance slows iteration | Med | Ceremonies are optional until arc/epoch close; work-level DoD unchanged |
| audit-decision-coverage not integrated | Low | WORK-069 already implemented; just verify it runs |
| Skill pattern inconsistency | Low | Follow close-work-cycle structure exactly |
| CH-010 orphan (not linked from ARC.md) | Med | Step 7 explicitly adds to ARC.md Chapters table |

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

**MUST** read `docs/work/active/WORK-070/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| L4 Requirements (REQ-DOD-001, REQ-DOD-002) | [ ] | Grep functional_requirements.md for REQ-DOD |
| Chapter DoD Ceremony | [ ] | File exists: `.claude/skills/close-chapter-ceremony/SKILL.md` |
| Arc DoD Ceremony | [ ] | File exists: `.claude/skills/close-arc-ceremony/SKILL.md` |
| Epoch DoD Ceremony | [ ] | File exists: `.claude/skills/close-epoch-ceremony/SKILL.md` |
| DoD Cascade Schema | [ ] | Documented in CH-010 chapter file |
| CH-010 Chapter File | [ ] | File exists: `.claude/haios/epochs/E2_4/arcs/flow/CH-010-MultiLevelDoD.md` |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/manifesto/L4/functional_requirements.md` | Contains REQ-DOD-001, REQ-DOD-002 | [ ] | |
| `.claude/skills/close-chapter-ceremony/SKILL.md` | VALIDATE->MARK->REPORT cycle | [ ] | |
| `.claude/skills/close-arc-ceremony/SKILL.md` | VALIDATE->MARK->REPORT cycle | [ ] | |
| `.claude/skills/close-epoch-ceremony/SKILL.md` | VALIDATE->ARCHIVE->TRANSITION cycle | [ ] | |
| `.claude/haios/epochs/E2_4/arcs/flow/CH-010-MultiLevelDoD.md` | implements_decisions: [D8] | [ ] | |
| `.claude/haios/epochs/E2_4/arcs/flow/ARC.md` | CH-010 in Chapters table | [ ] | |
| `tests/test_multilevel_dod.py` | 6 tests exist and pass | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_multilevel_dod.py -v
# Expected: 6 tests passed
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

- @docs/ADR/ADR-033-work-item-lifecycle.md (work item DoD definition)
- @docs/work/active/WORK-055/WORK.md (source investigation - multi-level governance)
- @docs/work/active/WORK-069/WORK.md (dependency - decision traceability schema)
- @.claude/haios/epochs/E2_4/arcs/flow/CH-009-DecisionTraceability.md (pattern for chapter files)
- @.claude/skills/close-work-cycle/SKILL.md (pattern for ceremony skills)
- @.claude/haios/manifesto/L4/functional_requirements.md (target for new requirements)

---
