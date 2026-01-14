---
template: implementation_plan
status: complete
date: 2025-12-22
backlog_id: E2-113
title: "Investigation Events"
author: Hephaestus
lifecycle_phase: plan
session: 98
spawned_by: M4-Research
related: [E2-097, E2-111, E2-084]
milestone: M4-Research
enables: []
version: "1.5"
generated: 2025-12-22
last_updated: 2025-12-22T18:18:05
---
# Implementation Plan: Investigation Events

@docs/README.md
@docs/epistemic_state.md
@.claude/hooks/hooks/post_tool_use.py

---

## Goal

Log investigation phase transitions (HYPOTHESIZE/EXPLORE/CONCLUDE) to haios-events.jsonl, mirroring the existing plan cycle transition logging (E2-097).

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/hooks/hooks/post_tool_use.py` |
| Lines of code affected | ~5 | Extend existing `_log_cycle_transition` function |
| New files to create | 0 | Using existing event infrastructure |
| Tests to write | 1 | Add test for investigation event logging |
| Dependencies | 0 | Uses existing event log pattern |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single function modification |
| Risk of regression | Low | Additive change to path detection |
| External dependencies | Low | Same haios-events.jsonl format |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Implement change | 15 min | High |
| Test | 10 min | High |
| **Total** | ~25 min | High |

---

## Current State vs Desired State

### Current State

**File:** `.claude/hooks/hooks/post_tool_use.py:534-535`

```python
# Only handles plans
def _log_cycle_transition(path: Path) -> Optional[str]:
    path_str = str(path).replace("\\", "/")
    if "plans" not in path_str or "PLAN-" not in path_str:
        return None
```

**Behavior:** Only logs cycle transitions for plan files (PLAN-*.md).

**Result:** Investigation phase transitions are not logged to haios-events.jsonl.

### Desired State

```python
# Handles both plans and investigations
def _log_cycle_transition(path: Path) -> Optional[str]:
    path_str = str(path).replace("\\", "/")
    is_plan = "plans" in path_str and "PLAN-" in path_str
    is_investigation = "investigations" in path_str and "INVESTIGATION-" in path_str
    if not is_plan and not is_investigation:
        return None
```

**Behavior:** Logs cycle transitions for both plan files AND investigation files.

**Result:** Investigation phase changes appear in haios-events.jsonl with same structure.

---

## Tests First (TDD)

### Test 1: Investigation Cycle Transition Logged
```python
def test_investigation_cycle_transition_logged(tmp_path, monkeypatch):
    """Test that investigation phase changes are logged to events."""
    # Setup: Create investigation file with lifecycle_phase
    inv_dir = tmp_path / "docs" / "investigations"
    inv_dir.mkdir(parents=True)
    inv_file = inv_dir / "INVESTIGATION-INV-001-test.md"
    inv_file.write_text("""---
template: investigation
backlog_id: INV-001
lifecycle_phase: explore
---
# Test Investigation
""")

    # Create events file
    events_dir = tmp_path / ".claude"
    events_dir.mkdir()
    events_file = events_dir / "haios-events.jsonl"
    events_file.write_text("")

    # Monkeypatch paths and call
    monkeypatch.chdir(tmp_path)

    from hooks.post_tool_use import _log_cycle_transition
    result = _log_cycle_transition(inv_file)

    # Assert event was logged
    assert result is not None
    assert "INV-001" in result
    events_content = events_file.read_text()
    assert '"type": "cycle_transition"' in events_content
    assert '"backlog_id": "INV-001"' in events_content
```

### Test 2: Plan Events Still Work (Backward Compatibility)
```python
def test_plan_cycle_transition_still_works(tmp_path, monkeypatch):
    """Ensure plan events still work after change."""
    # Same pattern as existing E2-097 tests
    # Verify PLAN-* files still trigger events
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/hooks/hooks/post_tool_use.py`
**Location:** Lines 534-539 in `_log_cycle_transition()`

**Current Code:**
```python
# post_tool_use.py:534-539
def _log_cycle_transition(path: Path) -> Optional[str]:
    """
    Log events when cycle_phase changes in plan files (E2-097).

    Returns cycle message or None.
    """
    path_str = str(path).replace("\\", "/")
    if "plans" not in path_str or "PLAN-" not in path_str:
        return None
```

**Changed Code:**
```python
# post_tool_use.py:534-545
def _log_cycle_transition(path: Path) -> Optional[str]:
    """
    Log events when lifecycle_phase changes in plan or investigation files.

    E2-097: Plans (PLAN-*.md in plans/)
    E2-113: Investigations (INVESTIGATION-*.md in investigations/)

    Returns cycle message or None.
    """
    path_str = str(path).replace("\\", "/")
    is_plan = "plans" in path_str and "PLAN-" in path_str
    is_investigation = "investigations" in path_str and "INVESTIGATION-" in path_str
    if not is_plan and not is_investigation:
        return None
```

**Diff:**
```diff
 def _log_cycle_transition(path: Path) -> Optional[str]:
     """
-    Log events when cycle_phase changes in plan files (E2-097).
+    Log events when lifecycle_phase changes in plan or investigation files.
+
+    E2-097: Plans (PLAN-*.md in plans/)
+    E2-113: Investigations (INVESTIGATION-*.md in investigations/)

     Returns cycle message or None.
     """
     path_str = str(path).replace("\\", "/")
-    if "plans" not in path_str or "PLAN-" not in path_str:
+    is_plan = "plans" in path_str and "PLAN-" in path_str
+    is_investigation = "investigations" in path_str and "INVESTIGATION-" in path_str
+    if not is_plan and not is_investigation:
         return None
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Extend existing function | Yes | Same logic, different path patterns |
| Same event type | `cycle_transition` | Unified event schema for both |
| Same lifecycle_phase field | Yes | Investigations use same field as plans |

### Event Schema (unchanged)

```json
{
  "ts": "2025-12-22T18:00:00",
  "type": "cycle_transition",
  "backlog_id": "INV-023",
  "from_phase": "HYPOTHESIZE",
  "to_phase": "EXPLORE",
  "session": 98,
  "source": "PostToolUse"
}
```

---

## Implementation Steps

### Step 1: Write Failing Test
- [ ] Add test to `tests/test_post_tool_use.py` (or create if needed)
- [ ] Verify test fails (investigation events not logged)

### Step 2: Modify _log_cycle_transition
- [ ] Update path detection logic (lines 534-539)
- [ ] Update docstring
- [ ] Test passes

### Step 3: Integration Verification
- [ ] Run full test suite
- [ ] Manually verify: edit an investigation file, check haios-events.jsonl

### Step 4: README Sync (MUST)
- [ ] **MUST:** Update `.claude/hooks/README.md` if it exists

### Step 5: Consumer Verification

**SKIPPED:** Not a migration - extending existing function.

---

## Verification

- [ ] Test passes
- [ ] Investigation phase changes appear in haios-events.jsonl
- [ ] Plan phase changes still work (no regression)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Break plan events | Medium | Test backward compatibility |
| Wrong path detection | Low | Use same pattern as plans |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 98 | 2025-12-22 | - | Plan drafted | Design from E2-097 pattern |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/hooks/hooks/post_tool_use.py` | `is_investigation` check added | [ ] | |
| `tests/test_post_tool_use.py` | Investigation event test exists | [ ] | |
| `.claude/haios-events.jsonl` | Shows investigation events | [ ] | |

**Verification Commands:**
```bash
# Test the change
pytest tests/test_post_tool_use.py -v -k investigation
# Expected: 1 test passed

# Manual verification: edit an investigation, check events
cat .claude/haios-events.jsonl | tail -5
# Expected: cycle_transition event with INV-* backlog_id
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
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- **E2-097:** Cycle State Frontmatter (plan events - pattern to follow)
- **E2-084:** Event Log Foundation (haios-events.jsonl)
- **E2-111:** Investigation Cycle Skill (defines phases)
- **Memory:** Concept 76839 (E2-097 key decisions)

---
