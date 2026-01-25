---
template: implementation_plan
status: ready
date: 2026-01-25
backlog_id: WORK-014
title: Type-Based Routing Migration
author: Hephaestus
lifecycle_phase: plan
session: 239
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-25T21:07:53'
---
# Implementation Plan: Type-Based Routing Migration

@docs/work/active/WORK-013/WORK.md
@docs/specs/TRD-WORK-ITEM-UNIVERSAL.md

---

<!-- TEMPLATE GOVERNANCE (v1.4) - Sections marked SKIPPED have rationale -->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing test for routing.determine_route() |
| Query prior work | SHOULD | WORK-013 investigation provides all context |
| Document design decisions | MUST | Filled below |
| Ground truth metrics | MUST | 4 Python files, 7 prose files = 11 total |

---

## Goal

Routing decisions will use the work item `type` field instead of ID prefix, enabling WORK-XXX items with `type: investigation` to route correctly to investigation-cycle.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Python files to modify | 4 | WORK-013 findings |
| Prose files to modify | 7 | WORK-013 findings (6 skills + 1 command) |
| Lines of code affected | ~15 | Small targeted changes |
| New files to create | 0 | Modifying existing |
| Tests to write | 2 | Test type-based routing |
| Dependencies | 1 | routing.py used by skills |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | One function signature change |
| Risk of regression | Low | Adding parameter, backward compat |
| External dependencies | Low | No external APIs |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests + routing.py | 15 min | High |
| Other Python files | 10 min | High |
| Prose files | 15 min | High |
| **Total** | 40 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/lib/routing.py:62-67
# Investigation routing (INV-* prefix)
if next_work_id.startswith("INV-"):
    return {
        "action": "invoke_investigation",
        "reason": f"ID prefix INV-* routes to investigation-cycle: {next_work_id}"
    }
```

**Behavior:** Routes based on ID prefix. WORK-123 with `type: investigation` routes to work-creation, not investigation.

**Result:** Inconsistent routing for universal work items.

### Desired State

```python
# .claude/lib/routing.py - Updated
def determine_route(
    next_work_id: Optional[str],
    has_plan: bool,
    work_type: Optional[str] = None  # NEW parameter
) -> dict:
    # Investigation routing (type field OR legacy INV-* prefix)
    if work_type == "investigation" or (next_work_id and next_work_id.startswith("INV-")):
        return {
            "action": "invoke_investigation",
            "reason": f"Type 'investigation' routes to investigation-cycle: {next_work_id}"
        }
```

**Behavior:** Routes based on `type` field. Legacy INV-* prefix still works for backward compatibility.

**Result:** WORK-XXX items with `type: investigation` route correctly.

---

## Tests First (TDD)

### Test 1: Type-based investigation routing
```python
def test_determine_route_type_investigation():
    """WORK-XXX with type: investigation routes to investigation-cycle."""
    result = determine_route(
        next_work_id="WORK-014",
        has_plan=False,
        work_type="investigation"
    )
    assert result["action"] == "invoke_investigation"
```

### Test 2: Legacy INV-* prefix still works
```python
def test_determine_route_legacy_inv_prefix():
    """INV-XXX still routes to investigation-cycle (backward compat)."""
    result = determine_route(
        next_work_id="INV-017",
        has_plan=False,
        work_type=None  # Legacy items may not have type
    )
    assert result["action"] == "invoke_investigation"
```

### Test 3: Type takes precedence over no-plan default
```python
def test_determine_route_type_over_default():
    """Type field routes correctly even without plan."""
    result = determine_route(
        next_work_id="WORK-015",
        has_plan=False,
        work_type="feature"
    )
    # Feature without plan goes to work-creation
    assert result["action"] == "invoke_work_creation"
```

---

## Detailed Design

### Change 1: routing.py - Add work_type parameter

**File:** `.claude/lib/routing.py`
**Location:** Lines 28-80

**Current Signature:**
```python
def determine_route(
    next_work_id: Optional[str],
    has_plan: bool
) -> dict:
```

**New Signature:**
```python
def determine_route(
    next_work_id: Optional[str],
    has_plan: bool,
    work_type: Optional[str] = None
) -> dict:
```

**Current Logic (line 62-67):**
```python
# Investigation routing (INV-* prefix)
if next_work_id.startswith("INV-"):
    return {
        "action": "invoke_investigation",
        "reason": f"ID prefix INV-* routes to investigation-cycle: {next_work_id}"
    }
```

**New Logic:**
```python
# Investigation routing (type field OR legacy INV-* prefix)
if work_type == "investigation" or (next_work_id and next_work_id.startswith("INV-")):
    return {
        "action": "invoke_investigation",
        "reason": f"Type 'investigation' routes to investigation-cycle: {next_work_id}"
    }
```

### Change 2: status.py - Use type field

**File:** `.claude/lib/status.py`
**Location:** Lines 818-820

**Current:**
```python
# Check for associated investigation (INV-* items)
if item_id.startswith("INV-"):
    cycle_type = "investigation"
```

**New:**
```python
# Check for investigation type (field or legacy prefix)
work_type = metadata.get("type", "")
if work_type == "investigation" or item_id.startswith("INV-"):
    cycle_type = "investigation"
```

### Change 3: portal_manager.py - Remove prefix check

**File:** `.claude/haios/modules/portal_manager.py`
**Location:** Lines 225-226

**Current:**
```python
if spawned_by.startswith("INV-"):
    fm["spawned_by_investigation"] = spawned_by
```

**New:**
```python
# spawned_by_investigation is DEPRECATED per TRD-WORK-ITEM-UNIVERSAL
# Legacy field preserved for existing items but not set for new items
```

### Change 4: memory_bridge.py - Add WORK-* pattern

**File:** `.claude/haios/modules/memory_bridge.py`
**Location:** Line 211

**Current:**
```python
for pattern in [r"E2-\d+", r"INV-\d+", r"TD-\d+"]:
```

**New:**
```python
for pattern in [r"WORK-\d+", r"E2-\d+", r"INV-\d+", r"TD-\d+"]:
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Add parameter vs replace | Add `work_type` param with default None | Backward compatible - existing callers don't break |
| Check type OR prefix | Both conditions with OR | Legacy INV-* items may not have type field |
| Remove spawned_by_investigation | Comment out, don't set | TRD says field is deprecated, but don't break existing data |
| WORK-* first in regex | Put WORK-* first in pattern list | New canonical format should match first |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Legacy INV-* without type field | Falls back to prefix check | Test 2 |
| WORK-* with type: investigation | Type field takes precedence | Test 1 |
| work_type=None (old callers) | Falls back to prefix check | Test 2 |

---

## Open Decisions (MUST resolve before implementation)

**SKIPPED:** No open decisions - all design choices resolved in WORK-013 investigation and TRD-WORK-ITEM-UNIVERSAL.

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add `test_determine_route_type_investigation` to tests/test_routing.py (or create if needed)
- [ ] Add `test_determine_route_legacy_inv_prefix`
- [ ] Add `test_determine_route_type_over_default`
- [ ] Verify all tests fail (red) - function signature mismatch

### Step 2: Update routing.py
- [ ] Add `work_type: Optional[str] = None` parameter
- [ ] Update investigation check to use `work_type == "investigation" or prefix`
- [ ] Update docstring routing table
- [ ] Tests 1, 2, 3 pass (green)

### Step 3: Update status.py
- [ ] Add type field extraction from metadata
- [ ] Update investigation check to use type OR prefix

### Step 4: Update portal_manager.py
- [ ] Comment out spawned_by_investigation logic (deprecated)

### Step 5: Update memory_bridge.py
- [ ] Add WORK-* to regex pattern list

### Step 6: Update Prose Files (Skills)
- [ ] survey-cycle/SKILL.md - Update routing table
- [ ] routing-gate/SKILL.md - Update decision table
- [ ] implementation-cycle/SKILL.md - Update routing reference
- [ ] investigation-cycle/SKILL.md - Update routing reference
- [ ] close-work-cycle/SKILL.md - Update DoD reference
- [ ] work-creation-cycle/SKILL.md - Update routing reference

### Step 7: Update Command File
- [ ] close.md - Update INV-* handling reference

### Step 8: Integration Verification
- [ ] All tests pass
- [ ] Run full test suite (no regressions)

---

## Verification

- [ ] Tests pass (pytest tests/test_routing.py)
- [ ] Legacy INV-* items still route correctly
- [ ] New WORK-* with type: investigation routes correctly

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Break legacy INV-* routing | High | Keep prefix check as fallback with OR condition |
| Callers don't pass work_type | Medium | Default to None, falls back to prefix check |
| Prose skill files out of sync | Low | Update all 7 files in same session |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| routing.py:62-67 - Route by type field | [ ] | Read file, verify work_type param |
| status.py:819-820 - Determine cycle_type by type field | [ ] | Read file, verify type check |
| portal_manager.py:225-226 - Remove INV- prefix check | [ ] | Read file, verify commented |
| memory_bridge.py:211 - Add WORK-* to regex | [ ] | Read file, verify WORK-* first |
| survey-cycle/SKILL.md - Update routing table | [ ] | Read file, verify type-based |
| routing-gate/SKILL.md - Update decision table | [ ] | Read file, verify type-based |
| implementation-cycle/SKILL.md - Update routing | [ ] | Read file, verify type-based |
| investigation-cycle/SKILL.md - Update routing | [ ] | Read file, verify type-based |
| close-work-cycle/SKILL.md - Update DoD logic | [ ] | Read file, verify type-based |
| work-creation-cycle/SKILL.md - Update routing | [ ] | Read file, verify type-based |
| close.md - Update INV-* handling | [ ] | Read file, verify type-based |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/routing.py` | work_type param, OR condition | [ ] | |
| `tests/test_routing.py` | 3 new tests pass | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_routing.py -v
# Expected: All tests pass including new type-based tests
```

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **MUST:** All WORK.md deliverables verified complete
- [ ] **Runtime consumer exists** (routing.py called by cycle skills)
- [ ] WHY captured (memory stored)

---

## References

- @docs/work/active/WORK-013/WORK.md (investigation findings)
- @docs/specs/TRD-WORK-ITEM-UNIVERSAL.md (type-as-field spec)

---
