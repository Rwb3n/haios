---
template: implementation_plan
status: complete
date: 2025-12-23
backlog_id: E2-117
title: "Milestone-Auto-Discovery"
author: Hephaestus
lifecycle_phase: plan
session: 105
version: "1.5"
generated: 2025-12-21
last_updated: 2025-12-23T20:23:54
---
# Implementation Plan: Milestone-Auto-Discovery

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

Milestone discovery in status.py will auto-discover milestone names from `**Milestone:**` fields in backlog.md instead of requiring hardcoded `milestone_names` dict.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/lib/status.py` |
| Lines of code affected | ~20 | Lines 899-912 |
| New files to create | 0 | - |
| Tests to write | 2 | Add to existing test_lib_status.py |
| Dependencies | 0 | No new imports |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single function change |
| Risk of regression | Low | Existing tests cover milestones |
| External dependencies | Low | File system only |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Implementation | 15 min | High |
| Testing | 10 min | High |
| **Total** | 25 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/lib/status.py:899-912
    # Default milestone names (only names, items discovered)
    # TODO: E2-117 should make this fully dynamic
    milestone_names = {
        "M2-Governance": "Governance Suite",
        "M3-Cycles": "Implementation Cycles",
        "M4-Research": "Investigation Infrastructure",
        "M5-Plugin": "Plugin Architecture",
        "M6-WorkCycle": "Work File Architecture",
    }

    milestones = {
        key: {"name": name, "items": [], "complete": [], "progress": 0}
        for key, name in milestone_names.items()
    }
```

**Behavior:** Milestones are hardcoded. Adding M7 requires editing status.py.

**Result:** Manual maintenance burden, risk of forgetting to update.

### Desired State

```python
# .claude/lib/status.py - auto-discover milestone names
    # Pass 1: Discover all unique milestone keys from backlog
    milestone_pattern = r'\*\*Milestone:\*\*\s*(M\d+-[A-Za-z]+)'
    discovered_keys = set(re.findall(milestone_pattern, content))

    # Build milestones dict from discovered keys
    milestones = {
        key: {"name": _format_milestone_name(key), "items": [], "complete": [], "progress": 0}
        for key in discovered_keys
    }
```

**Behavior:** Milestones are discovered from backlog.md. Adding M7 just requires using `**Milestone:** M7-NewName` in backlog.

**Result:** Zero maintenance - system adapts automatically.

---

## Tests First (TDD)

**Test file:** `tests/test_lib_status.py`

### Test 1: Auto-Discover Milestone Keys
```python
def test_discover_milestones_finds_unique_keys(tmp_path, monkeypatch):
    """Discovers all unique milestone keys from backlog."""
    backlog = tmp_path / "docs" / "pm" / "backlog.md"
    backlog.parent.mkdir(parents=True)
    backlog.write_text("""
### [HIGH] E2-001: Item One
- **Milestone:** M7-NewMilestone

### [MEDIUM] E2-002: Item Two
- **Milestone:** M7-NewMilestone

### [LOW] E2-003: Item Three
- **Milestone:** M8-AnotherOne
""")
    monkeypatch.setattr('status.PROJECT_ROOT', tmp_path)

    from status import _discover_milestones_from_backlog
    milestones = _discover_milestones_from_backlog()

    assert "M7-NewMilestone" in milestones
    assert "M8-AnotherOne" in milestones
```

### Test 2: Format Milestone Name from Key
```python
def test_format_milestone_name():
    """Converts M6-WorkCycle to 'WorkCycle' for display."""
    from status import _format_milestone_name

    assert _format_milestone_name("M6-WorkCycle") == "WorkCycle"
    assert _format_milestone_name("M7-NewFeature") == "NewFeature"
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/lib/status.py`
**Location:** Lines 899-912 in `_discover_milestones_from_backlog()`

**Current Code (to remove):**
```python
    # Default milestone names (only names, items discovered)
    # TODO: E2-117 should make this fully dynamic
    milestone_names = {
        "M2-Governance": "Governance Suite",
        "M3-Cycles": "Implementation Cycles",
        "M4-Research": "Investigation Infrastructure",
        "M5-Plugin": "Plugin Architecture",
        "M6-WorkCycle": "Work File Architecture",
    }

    milestones = {
        key: {"name": name, "items": [], "complete": [], "progress": 0}
        for key, name in milestone_names.items()
    }
```

**New Code (replacement):**
```python
    # Auto-discover milestone keys from backlog content
    # Pattern matches: **Milestone:** M6-WorkCycle
    milestone_pattern = r'\*\*Milestone:\*\*\s*(M\d+-[A-Za-z]+)'
    discovered_keys = set(re.findall(milestone_pattern, content))

    # Build milestones dict from discovered keys
    milestones = {
        key: {"name": _format_milestone_name(key), "items": [], "complete": [], "progress": 0}
        for key in sorted(discovered_keys)  # Sort for deterministic order
    }
```

**New Helper Function:**
```python
def _format_milestone_name(key: str) -> str:
    """Convert milestone key to display name.

    Args:
        key: Milestone key like "M6-WorkCycle"

    Returns:
        Display name like "WorkCycle"
    """
    # Extract part after "M#-"
    if "-" in key:
        return key.split("-", 1)[1]
    return key
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Extract name from key | Split on `-` | `M6-WorkCycle` → `WorkCycle` is clear enough |
| Sort discovered keys | `sorted()` | Deterministic order for testing/display |
| Empty backlog handling | Empty dict | Already handled by existing code |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No milestones in backlog | Empty dict returned | Existing tests |
| Malformed milestone key | Regex won't match | Implicit |
| Duplicate milestone refs | Set deduplication | Test 1 |

---

## Implementation Steps

### Step 1: Add Helper Function
- [ ] Add `_format_milestone_name()` to status.py
- [ ] Add test for helper function

### Step 2: Replace Hardcoded Dict
- [ ] Remove hardcoded `milestone_names` dict
- [ ] Add auto-discovery logic
- [ ] Run tests

### Step 3: Verify Real Backlog Works
- [ ] Run `just update-status-slim`
- [ ] Verify M6-WorkCycle still appears in output

---

## Verification

- [ ] Tests pass
- [ ] Real backlog produces same milestones as before
- [ ] No README changes needed (internal function only)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Regex doesn't match all patterns | Medium | Pattern tested on real backlog |
| Empty milestones on empty backlog | Low | Already handled |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/status.py` | No hardcoded milestone_names | [ ] | |
| `tests/test_lib_status.py` | Tests for auto-discovery | [ ] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] WHY captured (reasoning stored to memory)
- [ ] Real backlog still works

---

## References

- **Memory 77171:** "Discover items dynamically from backlog.md's **Milestone:** field"

---
