---
template: implementation_plan
status: complete
date: 2026-02-05
backlog_id: WORK-091
title: Fracture Validation Lifecycle Templates
author: Hephaestus
lifecycle_phase: plan
session: 313
version: '1.0'
generated: 2026-02-05
last_updated: '2026-02-05T20:33:14'
---
# Implementation Plan: Fracture Validation Lifecycle Templates

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

Validation lifecycle will have three fractured phase templates (VERIFY, JUDGE, REPORT) with input/output contracts, matching the investigation, design, and implementation template patterns.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 0 | No existing files modified |
| Lines of code affected | 0 | New templates only |
| New files to create | 4 | VERIFY.md, JUDGE.md, REPORT.md, README.md |
| Tests to write | 4 | Directory exists, files exist, contracts present, size constraint |
| Dependencies | 0 | Templates are passive markdown, no code imports |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Templates read by skills, no code changes |
| Risk of regression | Low | New directory, no existing code affected |
| External dependencies | Low | None - pure markdown creation |

---

## Current State vs Desired State

### Current State

```
.claude/templates/
├── investigation/           # FRACTURED (reference pattern)
├── design/                  # FRACTURED (WORK-089)
├── implementation/          # FRACTURED (WORK-090)
└── validation/              # DOES NOT EXIST
```

### Desired State

```
.claude/templates/
├── investigation/           # EXISTS (reference)
├── design/                  # EXISTS (WORK-089)
├── implementation/          # EXISTS (WORK-090)
└── validation/              # NEW
    ├── VERIFY.md           (~40 lines)
    ├── JUDGE.md            (~40 lines)
    ├── REPORT.md           (~30 lines)
    └── README.md
```

---

## Tests First (TDD)

### Test 1: Validation templates directory exists
```python
def test_validation_templates_directory_exists():
    """templates/validation/ directory must exist."""
    val_dir = Path(".claude/templates/validation")
    assert val_dir.is_dir(), "templates/validation/ directory does not exist"
```

### Test 2: All phase templates exist
```python
def test_validation_phase_templates_exist():
    """All three validation phase templates must exist."""
    val_dir = Path(".claude/templates/validation")
    for phase in ["VERIFY", "JUDGE", "REPORT"]:
        template = val_dir / f"{phase}.md"
        assert template.exists(), f"{phase}.md does not exist"
```

### Test 3: Templates have required frontmatter contracts
```python
def test_validation_templates_have_contracts():
    """Each template must have input_contract and output_contract."""
    val_dir = Path(".claude/templates/validation")
    for phase in ["VERIFY", "JUDGE", "REPORT"]:
        content = (val_dir / f"{phase}.md").read_text()
        frontmatter = yaml.safe_load(content.split("---")[1])
        assert "input_contract" in frontmatter
        assert "output_contract" in frontmatter
        assert frontmatter["phase"] == phase
```

### Test 4: Templates under 100 lines
```python
def test_validation_templates_size_constraint():
    """Each template must be ≤100 lines per REQ-TEMPLATE-002."""
    val_dir = Path(".claude/templates/validation")
    for phase in ["VERIFY", "JUDGE", "REPORT"]:
        lines = len((val_dir / f"{phase}.md").read_text().splitlines())
        assert lines <= 100, f"{phase}.md has {lines} lines, exceeds 100"
```

---

## Detailed Design

### Template Frontmatter Schema

```yaml
---
template: validation_phase
phase: {VERIFY|JUDGE|REPORT}
maps_to_state: CHECK  # All validation phases map to CHECK (operator decision Session 313)
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
---
```

### Phase Specifications

**VERIFY.md (~40 lines):** Gather evidence, run tests, check artifacts
- Input: artifact_exists, spec_exists
- Output: evidence_gathered, artifact_inspected, criteria_identified

**JUDGE.md (~40 lines):** Evaluate evidence against criteria
- Input: verify_complete, evidence_exists
- Output: criteria_evaluated, verdict_formed, gaps_identified

**REPORT.md (~30 lines):** Document findings and verdict
- Input: judge_complete, verdict_exists
- Output: report_written, recommendations_made, stakeholders_informed

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Template type | `validation_phase` | Distinguish from other lifecycle types |
| Phase names | VERIFY/JUDGE/REPORT | Matches validation lifecycle phases |
| Three phases | Not four | Validation has 3 phases per L4 spec |
| maps_to_state | All map to CHECK | Validation is fundamentally a CHECK activity (operator decision S313) |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_validation_templates.py` with 4 tests
- [ ] Verify all tests fail (red)

### Step 2: Create Directory
- [ ] Create `.claude/templates/validation/` directory
- [ ] Test 1 passes (green)

### Step 3: Create VERIFY.md
- [ ] Write VERIFY.md with frontmatter and content

### Step 4: Create JUDGE.md
- [ ] Write JUDGE.md with frontmatter and content

### Step 5: Create REPORT.md
- [ ] Write REPORT.md with frontmatter and content
- [ ] Tests 2, 3, 4 pass (green)

### Step 6: Create README.md
- [ ] Create README.md documenting the templates

### Step 7: Verify
- [ ] All 4 tests pass
- [ ] Run full test suite (no regressions)

---

## Ground Truth Verification (Before Closing)

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Create templates/validation/ directory | [ ] | ls output |
| Create VERIFY.md with contracts | [ ] | File exists |
| Create JUDGE.md with contracts | [ ] | File exists |
| Create REPORT.md with contracts | [ ] | File exists |
| Each template ≤100 lines | [ ] | wc -l output |
| Unit test passes | [ ] | pytest output |

---

## References

- @.claude/templates/investigation/ (reference pattern)
- @.claude/templates/design/ (WORK-089 pattern)
- @.claude/templates/implementation/ (WORK-090 pattern)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-TEMPLATE-002)

---
