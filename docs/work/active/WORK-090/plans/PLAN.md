---
template: implementation_plan
status: approved
date: 2026-02-04
backlog_id: WORK-090
title: Fracture Implementation Lifecycle Templates
author: Hephaestus
lifecycle_phase: plan
session: 311
version: '1.5'
generated: 2026-02-04
last_updated: '2026-02-04T23:17:30'
---
# Implementation Plan: Fracture Implementation Lifecycle Templates

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

Implementation lifecycle will have four fractured phase templates (PLAN, DO, CHECK, DONE) with input/output contracts, matching the investigation and design template patterns.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 0 | No existing files modified |
| Lines of code affected | 0 | New templates only |
| New files to create | 5 | PLAN.md, DO.md, CHECK.md, DONE.md, README.md |
| Tests to write | 4 | Directory exists, files exist, contracts present, size constraint |
| Dependencies | 0 | Templates are passive markdown, no code imports |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Templates read by skills, no code changes |
| Risk of regression | Low | New directory, no existing code affected |
| External dependencies | Low | None - pure markdown creation |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Create templates | 30 min | High |
| Write tests | 15 min | High |
| Archive legacy | 5 min | High |
| **Total** | ~50 min | High |

---

## Current State vs Desired State

### Current State

```
.claude/templates/
├── investigation/           # FRACTURED (reference pattern)
│   └── ... (4 phase templates)
├── design/                  # FRACTURED (WORK-089)
│   └── ... (4 phase templates)
├── implementation/          # DOES NOT EXIST
└── implementation_plan.md   # MONOLITHIC (needs archiving)
```

**Behavior:** Implementation lifecycle has no fractured templates. The monolithic `implementation_plan.md` is used for plans but not for phase-specific context loading.

**Result:** Skills cannot load phase-specific context for implementation phases.

### Desired State

```
.claude/templates/
├── investigation/           # EXISTS (reference)
├── design/                  # EXISTS (WORK-089)
├── implementation/          # NEW
│   ├── PLAN.md             (~50 lines)
│   ├── DO.md               (~50 lines)
│   ├── CHECK.md            (~50 lines)
│   ├── DONE.md             (~40 lines)
│   └── README.md
├── _legacy/                 # NEW (archive)
│   └── implementation_plan.md
└── ...
```

**Behavior:** Implementation lifecycle has fractured templates with input/output contracts per phase.

**Result:** Skills can load ~50-line phase-specific templates instead of monolithic content.

---

## Tests First (TDD)

### Test 1: Implementation templates directory exists
```python
def test_implementation_templates_directory_exists():
    """templates/implementation/ directory must exist."""
    impl_dir = Path(".claude/templates/implementation")
    assert impl_dir.is_dir(), "templates/implementation/ directory does not exist"
```

### Test 2: All phase templates exist
```python
def test_implementation_phase_templates_exist():
    """All four implementation phase templates must exist."""
    impl_dir = Path(".claude/templates/implementation")
    for phase in ["PLAN", "DO", "CHECK", "DONE"]:
        template = impl_dir / f"{phase}.md"
        assert template.exists(), f"{phase}.md does not exist"
```

### Test 3: Templates have required frontmatter contracts
```python
def test_implementation_templates_have_contracts():
    """Each template must have input_contract and output_contract in frontmatter."""
    impl_dir = Path(".claude/templates/implementation")
    for phase in ["PLAN", "DO", "CHECK", "DONE"]:
        content = (impl_dir / f"{phase}.md").read_text()
        frontmatter = yaml.safe_load(content.split("---")[1])
        assert "input_contract" in frontmatter, f"{phase}.md missing input_contract"
        assert "output_contract" in frontmatter, f"{phase}.md missing output_contract"
        assert frontmatter["phase"] == phase, f"{phase}.md has wrong phase field"
```

### Test 4: Templates under 100 lines
```python
def test_implementation_templates_size_constraint():
    """Each template must be ≤100 lines per REQ-TEMPLATE-002."""
    impl_dir = Path(".claude/templates/implementation")
    for phase in ["PLAN", "DO", "CHECK", "DONE"]:
        lines = len((impl_dir / f"{phase}.md").read_text().splitlines())
        assert lines <= 100, f"{phase}.md has {lines} lines, exceeds 100"
```

---

## Detailed Design

**No code changes** - this is pure markdown template creation.

### Template Frontmatter Schema

Each template follows the established pattern:

```yaml
---
template: implementation_phase
phase: {PLAN|DO|CHECK|DONE}
maps_to_state: {PLAN|DO|CHECK|DONE}  # For activity_matrix lookup
version: '1.0'
input_contract:
- field: <name>
  type: <markdown|boolean|table>
  required: true|false
  description: <description>
output_contract:
- field: <name>
  type: <markdown|boolean|table>
  required: true|false
  description: <description>
generated: '<date>'
last_updated: '<timestamp>'
---
```

### Phase-to-State Mapping

| Implementation Phase | Maps to State | Purpose |
|---------------------|---------------|---------|
| PLAN | PLAN | Verify plan exists and is ready |
| DO | DO | Implement design from plan |
| CHECK | CHECK | Verify implementation quality |
| DONE | DONE | Complete and prepare for closure |

### Template Content Structure

Each template has these sections (per investigation/design pattern):
1. `# {PHASE} Phase` - Header with brief description
2. `## Input Contract` - Checklist of prerequisites
3. `## Governed Activities` - Table from activity_matrix.yaml
4. `## Output Contract` - Checklist of required outputs
5. `## Template` - Markdown scaffold for artifacts

### PLAN.md Specification (~50 lines)

**Purpose:** Verify plan exists and is ready for implementation.

**Input Contract:**
- work_context: Work item exists with approved plan
- plan_exists: Plan file present in plans/ directory

**Output Contract:**
- specs_verified: Referenced specifications read
- tests_defined: Tests First section has concrete tests
- design_documented: Detailed Design section complete

### DO.md Specification (~50 lines)

**Purpose:** Implement design from the plan.

**Input Contract:**
- plan_validated: PLAN phase complete
- file_manifest: Files to modify listed

**Output Contract:**
- tests_written: Failing tests written first
- implementation_done: All planned changes made
- design_matched: Implementation matches Detailed Design

### CHECK.md Specification (~50 lines)

**Purpose:** Verify implementation meets quality bar.

**Input Contract:**
- do_complete: DO phase complete
- tests_exist: Tests written during DO

**Output Contract:**
- tests_pass: All tests pass
- deliverables_verified: All WORK.md deliverables complete
- ground_truth_verified: Ground Truth Verification complete

### DONE.md Specification (~40 lines)

**Purpose:** Complete implementation and prepare for closure.

**Input Contract:**
- check_complete: CHECK phase complete
- dod_passed: DoD criteria verified

**Output Contract:**
- why_captured: Learnings stored to memory
- plan_complete: Plan status set to complete
- docs_updated: READMEs updated

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Template type | `implementation_phase` | Distinguish from investigation_phase and design_phase |
| Phase names | PLAN/DO/CHECK/DONE | Matches implementation-cycle skill phases |
| State mapping | 1:1 (PLAN→PLAN, DO→DO, etc.) | Implementation phases map directly to activity_matrix states |
| Contract structure | Same as investigation/design templates | Consistency across all lifecycles |
| Archive legacy | Move to _legacy/ | Preserve for reference, not delete |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Template >100 lines | Reject - REQ-TEMPLATE-002 violation | Test 4 |
| Missing frontmatter field | Fail contract validation | Test 3 |
| Wrong phase value | Fail contract validation | Test 3 |

---

## Open Decisions (MUST resolve before implementation)

**No operator decisions required.** This follows the established pattern from WORK-088 (investigation) and WORK-089 (design).

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_implementation_templates.py` with 4 tests
- [ ] Verify all tests fail (red) - directory doesn't exist yet

### Step 2: Create Directory Structure
- [ ] Create `.claude/templates/implementation/` directory
- [ ] Create `.claude/templates/_legacy/` directory (if not exists)
- [ ] Test 1 passes (green)

### Step 3: Create PLAN.md
- [ ] Write PLAN.md with frontmatter and content (~50 lines)
- [ ] Partial Test 2 passes

### Step 4: Create DO.md
- [ ] Write DO.md with frontmatter and content (~50 lines)
- [ ] Partial Test 2 passes

### Step 5: Create CHECK.md
- [ ] Write CHECK.md with frontmatter and content (~50 lines)
- [ ] Partial Test 2 passes

### Step 6: Create DONE.md
- [ ] Write DONE.md with frontmatter and content (~40 lines)
- [ ] Tests 2, 3, 4 pass (green)

### Step 7: Archive Legacy Template
- [ ] Move `implementation_plan.md` to `_legacy/implementation_plan.md`
- [ ] Verify no critical references broken (grep for direct imports)

### Step 8: Integration Verification
- [ ] All 4 tests pass
- [ ] Run full test suite (no regressions)

### Step 9: README Sync
- [ ] Create `.claude/templates/implementation/README.md` documenting the templates

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment - templates don't match activity_matrix states | Medium | Verified phase-to-state mapping matches activity_matrix.yaml |
| Integration - skills don't find templates | Low | Templates are passive markdown; skills read by path |
| Regression - none, new directory | None | No existing code modified |
| Scope creep - adding features beyond templates | Low | Plan strictly follows investigation/design template pattern |
| Legacy breakage - something depends on implementation_plan.md | Low | Archive to _legacy/, don't delete; grep for references first |

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

**MUST** read `docs/work/active/WORK-090/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Create templates/implementation/ directory | [ ] | `ls .claude/templates/implementation/` |
| Create PLAN.md with contracts | [ ] | File exists, has input/output_contract |
| Create DO.md with contracts | [ ] | File exists, has input/output_contract |
| Create CHECK.md with contracts | [ ] | File exists, has input/output_contract |
| Create DONE.md with contracts | [ ] | File exists, has input/output_contract |
| Move implementation_plan.md to _legacy/ | [ ] | File in _legacy/, not in templates/ |
| Each template ≤100 lines | [ ] | `wc -l` output |
| Unit test passes | [ ] | pytest output |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/templates/implementation/PLAN.md` | Has frontmatter with contracts | [ ] | |
| `.claude/templates/implementation/DO.md` | Has frontmatter with contracts | [ ] | |
| `.claude/templates/implementation/CHECK.md` | Has frontmatter with contracts | [ ] | |
| `.claude/templates/implementation/DONE.md` | Has frontmatter with contracts | [ ] | |
| `tests/test_implementation_templates.py` | 4 tests exist and pass | [ ] | |
| `.claude/templates/implementation/README.md` | Documents the templates | [ ] | |
| `.claude/templates/_legacy/implementation_plan.md` | Archived | [ ] | |

**Verification Commands:**
```bash
# Line counts (all ≤100)
wc -l .claude/templates/implementation/*.md

# Tests pass
pytest tests/test_implementation_templates.py -v
# Expected: 4 tests passed
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

- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-006-TemplateFracturing.md
- @.claude/templates/investigation/ (reference pattern)
- @.claude/templates/design/ (WORK-089 pattern)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-TEMPLATE-002)
- @.claude/haios/config/activity_matrix.yaml (governed activities)

---
