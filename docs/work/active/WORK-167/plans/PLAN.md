---
template: implementation_plan
status: complete
date: 2026-02-19
backlog_id: WORK-167
title: "Governance Tier Detection"
author: Hephaestus
lifecycle_phase: plan
session: 400
version: "1.5"
generated: 2026-02-19
last_updated: 2026-02-19T00:52:00
---
# Implementation Plan: Governance Tier Detection

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | 12 tests defined below covering all 4 tiers + edge cases + boundaries |
| Query prior work | SHOULD | Queried memory — mem:86670 confirms downstream importance |
| Document design decisions | MUST | 4 decisions documented below |
| Ground truth metrics | MUST | File counts from Glob, pattern from session_end_actions.py |

---

## Goal

A pure function `detect_tier(work_id, project_root=None) -> str` in `lib/tier_detector.py` that computes the governance tier (trivial/small/standard/architectural) from WORK.md frontmatter, following the `session_end_actions.py` fail-permissive pattern.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 0 | No existing files modified |
| New files to create | 2 | `lib/tier_detector.py`, `tests/test_tier_detector.py` |
| Tests to write | 12 | 4 tiers + 5 edge cases + 3 boundary tests |
| Dependencies | 1 | `governance_events.py` (for TierDetected event logging) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Pure lib/ function, no hook changes |
| Risk of regression | Low | New file, no existing code modified |
| External dependencies | Low | Only reads WORK.md files + yaml stdlib |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 15 min | High |
| Implement detect_tier | 20 min | High |
| Event logging integration | 10 min | High |
| Verification | 5 min | High |
| **Total** | **~50 min** | High |

---

## Current State vs Desired State

### Current State

No `detect_tier()` function exists. Agents determine governance tier manually by reading WORK.md frontmatter and applying predicates from REQ-LIFECYCLE-005 documentation. This costs agent tokens and is inconsistent.

**Behavior:** Agent reads WORK.md, reads REQ-LIFECYCLE-005, mentally evaluates 4 predicates, decides tier.

**Result:** Token-expensive, error-prone, no audit trail of tier decisions.

### Desired State

```python
# .claude/haios/lib/tier_detector.py
from tier_detector import detect_tier

tier = detect_tier("WORK-167")  # Returns "small"
tier = detect_tier("WORK-101")  # Returns "architectural"
```

**Behavior:** Pure function reads WORK.md frontmatter, evaluates computable predicates, returns tier string, logs TierDetected governance event.

**Result:** Zero agent tokens for tier determination, consistent results, full audit trail.

---

## Tests First (TDD)

### Test 1: Trivial Tier Detection
```python
def test_detect_tier_trivial(tmp_path):
    """effort=small, source_files<=2, no plan, no ADR, no type=design -> trivial"""
    _write_work_md(tmp_path, "WORK-001", effort="small", source_files=["a.py", "b.py"],
                   traces_to=["REQ-CEREMONY-005"], work_type="implementation")
    result = detect_tier("WORK-001", project_root=tmp_path)
    assert result == "trivial"
```

### Test 2: Small Tier Detection
```python
def test_detect_tier_small(tmp_path):
    """effort=small, source_files<=3, no ADR, no type=design -> small"""
    _write_work_md(tmp_path, "WORK-002", effort="small",
                   source_files=["a.py", "b.py", "c.py"],
                   traces_to=["REQ-CEREMONY-005"], work_type="implementation")
    # Create a plan file to differentiate from trivial
    _write_plan(tmp_path, "WORK-002")
    result = detect_tier("WORK-002", project_root=tmp_path)
    assert result == "small"
```

### Test 3: Standard Tier Detection (Default)
```python
def test_detect_tier_standard(tmp_path):
    """effort=medium -> standard (default)"""
    _write_work_md(tmp_path, "WORK-003", effort="medium",
                   source_files=["a.py", "b.py"], traces_to=[], work_type="implementation")
    result = detect_tier("WORK-003", project_root=tmp_path)
    assert result == "standard"
```

### Test 4: Architectural Tier Detection (type=design)
```python
def test_detect_tier_architectural_design(tmp_path):
    """type=design -> architectural"""
    _write_work_md(tmp_path, "WORK-004", effort="small",
                   source_files=["a.py"], traces_to=[], work_type="design")
    result = detect_tier("WORK-004", project_root=tmp_path)
    assert result == "architectural"
```

### Test 5: Architectural Tier Detection (ADR in traces_to)
```python
def test_detect_tier_architectural_adr(tmp_path):
    """ADR in traces_to -> architectural"""
    _write_work_md(tmp_path, "WORK-005", effort="small",
                   source_files=["a.py"], traces_to=["ADR-045"], work_type="implementation")
    result = detect_tier("WORK-005", project_root=tmp_path)
    assert result == "architectural"
```

### Test 6: Missing Effort Field Defaults to Standard
```python
def test_detect_tier_missing_effort_defaults_standard(tmp_path):
    """Absent effort field -> standard (conservative safe default)"""
    _write_work_md(tmp_path, "WORK-006", effort=None,
                   source_files=["a.py"], traces_to=[], work_type="implementation")
    result = detect_tier("WORK-006", project_root=tmp_path)
    assert result == "standard"
```

### Test 7: Missing source_files Defaults to Standard
```python
def test_detect_tier_missing_source_files_defaults_standard(tmp_path):
    """Absent source_files -> standard (conservative safe default)"""
    _write_work_md(tmp_path, "WORK-007", effort="small",
                   source_files=None, traces_to=[], work_type="implementation")
    result = detect_tier("WORK-007", project_root=tmp_path)
    assert result == "standard"
```

### Test 8: Absent traces_to with All Fields Absent Defaults to Standard
```python
def test_detect_tier_all_absent_defaults_standard(tmp_path):
    """All fields absent/empty -> standard (conservative, not trivial or architectural)"""
    _write_work_md(tmp_path, "WORK-008", effort=None,
                   source_files=None, traces_to=None, work_type=None)
    result = detect_tier("WORK-008", project_root=tmp_path)
    assert result == "standard"
```

### Test 9: Nonexistent Work Item Returns Standard
```python
def test_detect_tier_nonexistent_work_returns_standard(tmp_path):
    """Missing WORK.md -> standard (fail-permissive)"""
    result = detect_tier("WORK-999", project_root=tmp_path)
    assert result == "standard"
```

### Test 10: Boundary — source_files=2 with Plan Exists Returns Small
```python
def test_detect_tier_two_files_with_plan_returns_small(tmp_path):
    """effort=small, source_files=2, plan exists -> small (plan disqualifies trivial)"""
    _write_work_md(tmp_path, "WORK-010", effort="small", source_files=["a.py", "b.py"],
                   traces_to=["REQ-CEREMONY-005"], work_type="implementation")
    _write_plan(tmp_path, "WORK-010")
    result = detect_tier("WORK-010", project_root=tmp_path)
    assert result == "small"
```

### Test 11: Malformed YAML Frontmatter Returns Standard
```python
def test_detect_tier_malformed_yaml_returns_standard(tmp_path):
    """Malformed YAML frontmatter -> standard (fail-permissive)"""
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-011"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text("---\neffort: : bad yaml\n---\n")
    result = detect_tier("WORK-011", project_root=tmp_path)
    assert result == "standard"
```

### Test 12: Empty source_files List Returns Standard
```python
def test_detect_tier_empty_source_files_returns_standard(tmp_path):
    """source_files=[] (empty list) -> standard (conservative, per REQ-LIFECYCLE-005 invariant)"""
    _write_work_md(tmp_path, "WORK-012", effort="small", source_files=[],
                   traces_to=[], work_type="implementation")
    result = detect_tier("WORK-012", project_root=tmp_path)
    assert result == "standard"
```

---

## Detailed Design

### Function/Component Signatures

```python
# .claude/haios/lib/tier_detector.py

def detect_tier(work_id: str, project_root: Optional[Path] = None) -> str:
    """Compute governance tier from work item frontmatter.

    Evaluates computable predicates from REQ-LIFECYCLE-005 to classify
    work items into governance tiers: trivial, small, standard, architectural.

    Args:
        work_id: Work item ID (e.g., "WORK-167").
        project_root: Project root path. Defaults to derived path
                      (same pattern as session_end_actions.py).

    Returns:
        One of: "trivial", "small", "standard", "architectural".
        Returns "standard" on any error (conservative safe default).
    """
```

### Behavior Logic

```
Input (work_id) → Read WORK.md frontmatter
                    ├─ File missing/parse error → "standard" (fail-permissive)
                    ├─ type=design OR ADR in traces_to → "architectural"
                    ├─ effort absent OR effort != "small" → "standard"
                    ├─ source_files absent OR empty ([]) → "standard" (REQ-LIFECYCLE-005 invariant)
                    ├─ source_files > 3 → "standard"
                    ├─ source_files <= 2 AND no plan (filesystem: docs/work/active/{id}/plans/PLAN.md absent) AND no ADR AND type != design → "trivial"
                    ├─ source_files <= 3 AND no ADR → "small"
                    └─ else → "standard"
```

**Evaluation order matters:** Architectural is checked first (escalation always wins). Then conservative defaults for missing/empty fields. Then trivial/small predicates. The trivial branch includes an explicit `type != design` guard (A1 critique: self-contained predicate, not reliant on evaluation order).

### Call Chain Context

```
[Future: PreToolUse hook] OR [Agent manual call]
    |
    +-> detect_tier(work_id)             # <-- This function
    |       Returns: "trivial" | "small" | "standard" | "architectural"
    |       Side-effect: logs TierDetected to governance-events.jsonl
    |
    +-> [Future: WORK-169 critique_injector uses tier to select critique level]
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Location | `lib/tier_detector.py` | Follows session_end_actions.py pattern: pure lib/ function, testable without hooks |
| Path derivation | `_default_project_root()` from `__file__` | Same pattern as session_end_actions.py. Not `Path.cwd()` — hook subprocess cwd not guaranteed. |
| Error handling | Return "standard" on any error | Conservative safe default per REQ-LIFECYCLE-005 invariant. Absent data MUST NOT produce more permissive classification. |
| Event logging | Import `governance_events.log_governance_event()` with try/except | Fail-permissive: logging failure must not break tier detection. New event type `TierDetected`. |
| YAML parsing | `content.split("---", 2)` + `yaml.safe_load(parts[1])` | Established frontmatter parsing pattern in lib/ (epoch_validator.py:128). No external dependency. |
| Plan existence check | `Glob docs/work/active/{id}/plans/PLAN.md` | Filesystem check, not frontmatter field. Matches REQ-LIFECYCLE-005 predicate spec. |

### Input/Output Examples (Real Data)

```
detect_tier("WORK-167", project_root=D:\PROJECTS\haios)
  Frontmatter: effort=small, source_files=[session_end_actions.py, tier_detector.py],
               traces_to=[REQ-CEREMONY-005, REQ-LIFECYCLE-005], type=implementation
  Plan exists: Yes (PLAN.md just created)
  ADR in traces_to: No
  type=design: No
  → Predicate path: effort=small, source_files=2, has plan, no ADR → "small"
  Returns: "small"

detect_tier("WORK-101", project_root=D:\PROJECTS\haios)
  Frontmatter: effort=large, type=design
  → Predicate path: type=design → "architectural"
  Returns: "architectural"

detect_tier("WORK-166", project_root=D:\PROJECTS\haios)
  Frontmatter: effort=small, source_files=[5 files], type=implementation
  → Predicate path: effort=small but source_files=5 (>3) → "standard"
  Returns: "standard"
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| WORK.md missing | Return "standard" | Test 9 |
| Frontmatter parse error (malformed YAML) | Return "standard" | Test 11 |
| effort field absent | Return "standard" | Test 6 |
| source_files field absent (None) | Return "standard" | Test 7 |
| source_files field empty (`[]`) | Return "standard" (conservative — REQ-LIFECYCLE-005 invariant) | Test 12 |
| traces_to field absent | Return "standard" (not architectural, not trivial/small) | Test 8 |
| source_files=2 + plan exists | Return "small" (plan disqualifies trivial) | Test 10 |
| ADR-xxx in traces_to | Triggers architectural | Test 5 |

### Open Questions

**Q: Should detect_tier also log to governance-events.jsonl?**

Yes. AC specifies: "Tier determination logged to governance-events.jsonl as TierDetected event." Implementation: append a new event type via a simple JSONL append (same pattern as `governance_events.py`). Fail-permissive — logging failure must not affect tier return value.

**Q: Should we add a `log_tier_detected()` function to governance_events.py or keep logging inline?**

Add a `log_tier_detected()` function to `governance_events.py` for consistency. All event logging goes through that module. This is a minor addition (single function, follows existing pattern).

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Runtime consumer DoD criterion | (A) Add minimal consumer, (B) Foundation-item exception, (C) Defer closure | Foundation-item exception (B) | Operator decision S400: foundation/library items without consumers at creation time are exempt from ADR-033 "runtime consumer exists" criterion. First consumer will be WORK-169 (Critique-as-Hook). Exception logged as governance precedent. |
| ConfigLoader for plan path check | (A) Use ConfigLoader with fallback, (B) Hardcode convention | Hardcode convention (B) | tier_detector.py is a standalone lib/ function that must work without the full HAIOS config stack. Uses same path derivation pattern as session_end_actions.py. Follows convention: `docs/work/active/{id}/plans/PLAN.md`. |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_tier_detector.py` with 12 test cases + helper functions
- [ ] Verify all tests fail (red) — module doesn't exist yet

### Step 2: Implement detect_tier
- [ ] Create `lib/tier_detector.py` with `_default_project_root()`, `_parse_frontmatter()`, `detect_tier()`
- [ ] Tests 1-12 pass (green)

### Step 3: Add TierDetected Event Logging
- [ ] Add `log_tier_detected()` to `governance_events.py`
- [ ] Call from `detect_tier()` with try/except wrapper
- [ ] Verify event appears in governance-events.jsonl

### Step 4: Integration Verification
- [ ] All tests pass
- [ ] Run full test suite (no regressions)

### Step 5: README Sync (MUST)
- [ ] **MUST:** Update `lib/` README if one exists
- [ ] **MUST:** Verify README content matches actual file state

### Step 6: Consumer Verification
- [ ] **SKIPPED:** New file, no migration. No consumers to update yet (WORK-169 will be the first consumer).

---

## Verification

- [ ] Tests pass (`pytest tests/test_tier_detector.py -v`)
- [ ] No regressions in full suite
- [ ] `detect_tier("WORK-167")` returns correct tier when called manually

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| YAML parsing edge cases in WORK.md | Low | Fail-permissive: any parse error returns "standard" |
| Plan existence check path mismatch | Low | Hardcoded convention per Open Decisions choice B — no ConfigLoader dependency. Convention: `docs/work/active/{id}/plans/PLAN.md` |
| governance_events.py import failure | Low | try/except import, logging failure doesn't affect return |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 400 | 2026-02-19 | - | PLAN approved | Plan populated. Critique: 3 passes (all REVISE, all addressed). Validation + preflight: PASS. Status: approved. |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-167/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| New file `lib/tier_detector.py` with `detect_tier(work_id)` function | [ ] | Read file, function exists |
| Implements all 4 tier predicates from REQ-LIFECYCLE-005 | [ ] | Code inspection shows trivial/small/standard/architectural paths |
| Conservative defaults for missing fields (-> Standard) | [ ] | Tests 6, 7, 8 pass |
| Governance event logging for tier determination | [ ] | TierDetected event in governance-events.jsonl |
| Tests in `tests/test_tier_detector.py` covering all tiers + edge cases | [ ] | 12 tests, all pass |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/tier_detector.py` | `detect_tier()` function with 4-tier logic | [ ] | |
| `tests/test_tier_detector.py` | 12 tests covering all tiers + edge cases + boundaries | [ ] | |
| `.claude/haios/lib/governance_events.py` | `log_tier_detected()` function added | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_tier_detector.py -v
# Expected: 12 tests passed
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
- [ ] **Runtime consumer exists** — EXEMPT (foundation-item exception, operator decision S400). First consumer: WORK-169.
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories
- [ ] Ground Truth Verification completed above

---

## References

- @docs/work/active/WORK-167/WORK.md (work item)
- @docs/work/active/WORK-101/plans/PLAN.md (tier predicate specification, lines 145-186)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-LIFECYCLE-005, REQ-CEREMONY-005)
- @.claude/haios/lib/session_end_actions.py (pattern template)
- @.claude/haios/lib/governance_events.py (event logging pattern)
- Memory: 85390 (104% problem), 86670 (downstream automation dependency)

---
