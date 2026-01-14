---
template: implementation_plan
status: complete
date: 2025-12-28
backlog_id: E2-086
title: Template RFC 2119 Normalization
author: Hephaestus
lifecycle_phase: plan
session: 141
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-28T22:03:37'
---
# Implementation Plan: Template RFC 2119 Normalization

@docs/README.md
@docs/epistemic_state.md

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

## Goal

All HAIOS document templates will include RFC 2119 governance sections that guide agents with explicit MUST/SHOULD/MAY requirements for document creation.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 5 | `.claude/templates/{checkpoint,implementation_plan,investigation,report,architecture_decision_record}.md` |
| Lines affected | ~989 total | `wc -l` on 5 template files |
| Lines to add | ~50-75 | ~10-15 lines per template for RFC 2119 section |
| New files to create | 0 | Modifying existing templates only |
| Tests to write | 5 | One validation test per template |
| Dependencies | 0 | Templates have no code dependencies |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Templates are standalone markdown |
| Risk of regression | Low | Additive changes, no existing behavior changed |
| External dependencies | Low | No APIs or services, pure documentation |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Template updates | 30 min | High |
| Validation tests | 15 min | High |
| **Total** | 45 min | High |

---

## Current State vs Desired State

### Current State

Templates have placeholder sections and comments but no explicit RFC 2119 governance sections.

**Example (checkpoint.md):**
```markdown
## Session Summary

[Summary of work completed this session]

## WHY Captured (ADR-033)

| Decision/Learning | Memory ID | Source |
```

**Behavior:** Templates guide through structure but don't specify MUST/SHOULD/MAY requirements for each section.

**Result:** Agents may skip important steps (e.g., memory query, observation capture) because there's no explicit governance signal.

### Desired State

Each template has a dedicated RFC 2119 governance section near the top with explicit requirements.

**Example (checkpoint.md with RFC 2119 section):**
```markdown
## Session Hygiene (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Review unblocked plans | SHOULD | Run `just ready` before starting work |
| Capture observations | SHOULD | Document unexpected behaviors, gaps noticed |
| Store WHY to memory | MUST | Use `ingester_ingest` for key decisions |
| Update memory_refs | MUST | Add concept IDs to frontmatter |
```

**Behavior:** Templates provide explicit governance signals that Claude understands semantically.

**Result:** Agents follow MUST requirements and consider SHOULD/MAY items, improving governance compliance.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Checkpoint Template Has RFC 2119 Section
```python
def test_checkpoint_template_has_rfc2119_section():
    content = Path(".claude/templates/checkpoint.md").read_text()
    assert "RFC 2119" in content or "Session Hygiene" in content
    assert "MUST" in content or "SHOULD" in content
```

### Test 2: Implementation Plan Template Has RFC 2119 Section
```python
def test_implementation_plan_template_has_rfc2119_section():
    content = Path(".claude/templates/implementation_plan.md").read_text()
    assert "Pre-Implementation Checklist" in content or "RFC 2119" in content
    assert "MUST" in content
```

### Test 3: Investigation Template Has RFC 2119 Section
```python
def test_investigation_template_has_rfc2119_section():
    content = Path(".claude/templates/investigation.md").read_text()
    assert "Discovery Protocol" in content or "RFC 2119" in content
    assert "SHOULD" in content
```

### Test 4: Report Template Has RFC 2119 Section
```python
def test_report_template_has_rfc2119_section():
    content = Path(".claude/templates/report.md").read_text()
    assert "Verification Requirements" in content or "RFC 2119" in content
    assert "MUST" in content
```

### Test 5: ADR Template Has RFC 2119 Section
```python
def test_adr_template_has_rfc2119_section():
    content = Path(".claude/templates/architecture_decision_record.md").read_text()
    assert "Decision Criteria" in content or "RFC 2119" in content
    assert "MUST" in content
```

---

## Detailed Design

**SKIPPED (partial):** Pure documentation task - no code changes, only markdown template additions.

### RFC 2119 Section Format

Each template will have a governance section added after the frontmatter and before the first content section. The format is consistent:

```markdown
## [Context-Specific Name] (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| [Requirement 1] | MUST/SHOULD/MAY | [What to do] |
| [Requirement 2] | MUST/SHOULD/MAY | [What to do] |
```

### Template-Specific Sections

#### 1. checkpoint.md - "Session Hygiene"
| Requirement | Level | Action |
|-------------|-------|--------|
| Review unblocked work | SHOULD | Run `just ready` to see available items |
| Capture observations | SHOULD | Note unexpected behaviors, gaps |
| Store WHY to memory | MUST | Use `ingester_ingest` for key decisions |
| Update memory_refs | MUST | Add concept IDs after storing |

#### 2. implementation_plan.md - "Pre-Implementation Checklist"
| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in Tests First section |
| Query prior work | SHOULD | Search memory for similar implementations |
| Document design decisions | MUST | Fill Key Design Decisions table |
| Ground truth metrics | MUST | Real file counts, not guesses |

#### 3. investigation.md - "Discovery Protocol"
| Requirement | Level | Action |
|-------------|-------|--------|
| Query memory first | SHOULD | Search for prior investigations on topic |
| Document hypotheses | SHOULD | State what you expect to find |
| Use investigation-agent | MUST | Delegate EXPLORE to subagent (L3) |
| Capture findings | MUST | Fill Findings section with evidence |

#### 4. report.md - "Verification Requirements"
| Requirement | Level | Action |
|-------------|-------|--------|
| Include evidence | MUST | Link to files, screenshots, test output |
| Document methodology | SHOULD | Explain how conclusions were reached |
| List artifacts | MUST | Reference all relevant files |

#### 5. architecture_decision_record.md - "Decision Criteria"
| Requirement | Level | Action |
|-------------|-------|--------|
| Document alternatives | MUST | List at least 2 options considered |
| Explain WHY | MUST | Rationale for chosen option |
| Link to memory | SHOULD | Store decision reasoning via `ingester_ingest` |
| Get operator approval | MUST | Update decision field after approval |

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Section name per template | Context-specific names (Session Hygiene, Discovery Protocol, etc.) | More meaningful than generic "RFC 2119 Section" |
| Table format | Requirement/Level/Action columns | Clear structure, scannable for agents |
| MUST vs SHOULD balance | 2-3 MUSTs per template | Avoid over-constraining, focus on critical items |
| Placement | After frontmatter, before first content | Early visibility, not buried |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_template_rfc2119.py`
- [ ] Add 5 test functions (one per template)
- [ ] Verify all tests fail (red) - templates don't have sections yet

### Step 2: Update checkpoint.md
- [ ] Add "Session Hygiene (RFC 2119)" section after line 19 (after frontmatter comment)
- [ ] Include 4 requirements from design
- [ ] Test 1 passes (green)

### Step 3: Update implementation_plan.md
- [ ] Add "Pre-Implementation Checklist (RFC 2119)" section after Template Governance comment
- [ ] Include 4 requirements from design
- [ ] Test 2 passes (green)

### Step 4: Update investigation.md
- [ ] Add "Discovery Protocol (RFC 2119)" section after Template Governance comment
- [ ] Include 4 requirements from design
- [ ] Test 3 passes (green)

### Step 5: Update report.md
- [ ] Add "Verification Requirements (RFC 2119)" section after frontmatter
- [ ] Include 3 requirements from design
- [ ] Test 4 passes (green)

### Step 6: Update architecture_decision_record.md
- [ ] Add "Decision Criteria (RFC 2119)" section after frontmatter
- [ ] Include 4 requirements from design
- [ ] Test 5 passes (green)

### Step 7: Full Verification
- [ ] All 5 tests pass
- [ ] Run `just validate` on each template
- [ ] No regressions

### Step 8: README Sync (MUST)
- [ ] **MUST:** Update `.claude/templates/README.md` documenting RFC 2119 sections

---

## Verification

- [ ] All 5 template tests pass
- [ ] `just validate` passes for each template
- [ ] **MUST:** `.claude/templates/README.md` updated

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agents ignore new sections | Medium | MUST requirements are semantic signals Claude understands |
| Section becomes stale | Low | Review during E2-037 Phase 3 compliance tracking |
| Template validation breaks | Low | Run `just validate` after each edit |

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

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/templates/checkpoint.md` | Has "Session Hygiene (RFC 2119)" section | [ ] | |
| `.claude/templates/implementation_plan.md` | Has "Pre-Implementation Checklist (RFC 2119)" section | [ ] | |
| `.claude/templates/investigation.md` | Has "Discovery Protocol (RFC 2119)" section | [ ] | |
| `.claude/templates/report.md` | Has "Verification Requirements (RFC 2119)" section | [ ] | |
| `.claude/templates/architecture_decision_record.md` | Has "Decision Criteria (RFC 2119)" section | [ ] | |
| `tests/test_template_rfc2119.py` | 5 tests exist and pass | [ ] | |
| `.claude/templates/README.md` | Documents RFC 2119 sections | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_template_rfc2119.py -v
# Expected: 5 tests passed
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
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- ADR-035: RFC 2119 Governance Signaling
- E2-037: RFC 2119 Governance Signaling System (completed - provides pattern)
- CLAUDE.md: RFC 2119 Keywords section (reference for MUST/SHOULD/MAY usage)
- `.claude/templates/`: Target templates directory

---
