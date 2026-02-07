---
template: implementation_plan
status: complete
date: 2025-12-28
backlog_id: E2-224
title: OBSERVE Phase Threshold-Triggered Triage
author: Hephaestus
lifecycle_phase: plan
session: 138
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-28T18:20:14'
---
# Implementation Plan: OBSERVE Phase Threshold-Triggered Triage

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

The close-work-cycle OBSERVE phase will check pending observation count across all archived work items and trigger inline triage when threshold is exceeded, completing the observation feedback loop while maintaining cognitive continuity.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `.claude/lib/observations.py`, `.claude/skills/close-work-cycle/SKILL.md` |
| Lines of code affected | ~30 | Add 2 functions (~15 lines each) to observations.py |
| New files to create | 0 | Adding to existing files |
| Tests to write | 4 | 2 for get_pending_observation_count, 2 for should_trigger_triage |
| Dependencies | 1 | scan_archived_observations (already exists) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only touches observations.py and SKILL.md |
| Risk of regression | Low | Existing tests cover scan_archived_observations |
| External dependencies | Low | No external APIs or services |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 10 min | High |
| Implementation | 15 min | High |
| SKILL.md update | 10 min | High |
| **Total** | 35 min | High |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/skills/close-work-cycle/SKILL.md:68-115
### 2. OBSERVE Phase (INV-047)

**Actions:**
#### 2a. Scaffold Observations
#### 2b. Populate Observations
#### 2c. Validate Gate (Hard)
# NO step 2d for threshold check - observations accumulate untriaged
```

**Behavior:** OBSERVE phase captures observations but doesn't check if pending observations have accumulated across archived work items.

**Result:** Observations with `triage_status: pending` accumulate indefinitely with no feedback loop.

### Desired State

```markdown
# .claude/skills/close-work-cycle/SKILL.md - OBSERVE Phase
### 2. OBSERVE Phase (INV-047, E2-224)

**Actions:**
#### 2a. Scaffold Observations
#### 2b. Populate Observations
#### 2c. Validate Gate (Hard)
#### 2d. Threshold Check (E2-224) - NEW
```

```python
# .claude/lib/observations.py - NEW functions
DEFAULT_OBSERVATION_THRESHOLD = 10  # From memory 79956

def get_pending_observation_count(base_path: Optional[Path] = None) -> int:
    """Count total pending observations across archived work items."""
    pending_items = scan_archived_observations(base_path)
    return sum(len(item["observations"]) for item in pending_items)

def should_trigger_triage(count: int, threshold: int = DEFAULT_OBSERVATION_THRESHOLD) -> bool:
    """Check if pending observation count exceeds threshold."""
    return count > threshold
```

**Behavior:** OBSERVE phase checks pending count after validation gate, triggers inline triage when threshold exceeded.

**Result:** Observations are triaged while agent is in reflection mode, maintaining cognitive continuity.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: get_pending_observation_count with empty archive
```python
def test_get_pending_observation_count_empty(tmp_path):
    """No archived observations returns 0."""
    # Setup: Create empty archive structure
    archive_dir = tmp_path / "docs" / "work" / "archive"
    archive_dir.mkdir(parents=True)

    # Action
    count = get_pending_observation_count(base_path=tmp_path)

    # Assert
    assert count == 0
```

### Test 2: get_pending_observation_count with pending observations
```python
def test_get_pending_observation_count_with_pending(tmp_path):
    """Correctly counts pending observations across archived items."""
    # Setup: Create 2 archived items with 3 and 2 observations
    for item, obs_count in [("E2-A", 3), ("E2-B", 2)]:
        work_dir = tmp_path / "docs" / "work" / "archive" / item
        work_dir.mkdir(parents=True)
        obs_file = work_dir / "observations.md"
        obs_lines = "\n".join([f"- [x] Obs {i}" for i in range(obs_count)])
        obs_file.write_text(f"---\ntriage_status: pending\n---\n## Gaps\n{obs_lines}")

    # Action
    count = get_pending_observation_count(base_path=tmp_path)

    # Assert
    assert count == 5
```

### Test 3: should_trigger_triage threshold exceeded
```python
def test_should_trigger_triage_exceeded():
    """Returns True when count exceeds threshold."""
    assert should_trigger_triage(count=11, threshold=10) is True
    assert should_trigger_triage(count=15, threshold=10) is True
```

### Test 4: should_trigger_triage threshold not exceeded
```python
def test_should_trigger_triage_not_exceeded():
    """Returns False when count at or below threshold."""
    assert should_trigger_triage(count=10, threshold=10) is False
    assert should_trigger_triage(count=5, threshold=10) is False
    assert should_trigger_triage(count=0, threshold=10) is False
```

---

## Detailed Design

<!-- REQUIRED: Document HOW the implementation works, not just WHAT it does. -->

### Exact Code Change

**File 1:** `.claude/lib/observations.py`
**Location:** After line 332 (after `scan_archived_observations` function)

**New Code to Add:**
```python
# =============================================================================
# THRESHOLD FUNCTIONS (E2-224)
# =============================================================================

# Default threshold - configurable via E2-222 later
DEFAULT_OBSERVATION_THRESHOLD = 10


def get_pending_observation_count(base_path: Optional[Path] = None) -> int:
    """Count total pending observations across all archived work items.

    Args:
        base_path: Override project root (for testing)

    Returns:
        Total count of pending observations across all archived items.
    """
    pending_items = scan_archived_observations(base_path)
    return sum(len(item["observations"]) for item in pending_items)


def should_trigger_triage(count: int, threshold: int = DEFAULT_OBSERVATION_THRESHOLD) -> bool:
    """Check if pending observation count exceeds threshold.

    Args:
        count: Current pending observation count
        threshold: Threshold to trigger triage (default: 10)

    Returns:
        True if count > threshold, False otherwise.
    """
    return count > threshold
```

**File 2:** `.claude/skills/close-work-cycle/SKILL.md`
**Location:** After line 115 (after step 2c "Validate Gate")

**New Section to Add:**
```markdown
#### 2d. Threshold Check (E2-224)

5. **Check pending observation count:**
   ```python
   from observations import get_pending_observation_count, should_trigger_triage
   count = get_pending_observation_count()
   ```
6. **Report count to user:**
   > "Pending observations across archive: {count}"
7. **If threshold exceeded, invoke triage:**
   ```
   if should_trigger_triage(count):
       > "Threshold exceeded ({count} > 10). Invoking inline triage."
       Skill(skill="observation-triage-cycle")
   ```
8. Continue to ARCHIVE phase after triage completes (or if threshold not exceeded)
```

### Call Chain Context

```
close-work-cycle OBSERVE phase
    |
    +-> 2a. scaffold_observations()
    +-> 2b. (agent populates)
    +-> 2c. validate_observations()
    +-> 2d. get_pending_observation_count()  # <-- NEW
    |       Returns: int
    |
    +-> should_trigger_triage(count)         # <-- NEW
            Returns: bool
            |
            +-> IF True: observation-triage-cycle
    |
    +-> 3. ARCHIVE phase continues
```

### Function/Component Signatures

```python
def get_pending_observation_count(base_path: Optional[Path] = None) -> int:
    """Count total pending observations across all archived work items.

    Args:
        base_path: Override project root (for testing). If None, uses PROJECT_ROOT.

    Returns:
        Total count of pending observations. 0 if no archived items or no observations.
    """

def should_trigger_triage(count: int, threshold: int = DEFAULT_OBSERVATION_THRESHOLD) -> bool:
    """Check if pending observation count exceeds threshold.

    Uses strict greater-than (not >=) to avoid triggering at exactly threshold.

    Args:
        count: Current pending observation count
        threshold: Threshold to trigger triage (default: 10 per memory 79956)

    Returns:
        True if count > threshold (triage needed), False otherwise.
    """
```

### Behavior Logic

**Current Flow:**
```
OBSERVE phase → 2a,2b,2c → ARCHIVE phase
                           (no threshold check - observations accumulate)
```

**New Flow:**
```
OBSERVE phase → 2a,2b,2c → 2d: get_pending_observation_count()
                                |
                          count > 10?
                            ├─ YES → observation-triage-cycle → ARCHIVE
                            └─ NO  → ARCHIVE phase continues
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Threshold value | 10 (not 5) | Memory 79956: "First implementation will use observation pending count > 10" |
| Strict > not >= | count > threshold | At exactly 10, don't trigger - gives breathing room |
| Inline triage | Skill invocation | Agent stays in reflection mode, no context switch |
| Location | After 2c | Threshold check after current item's observations captured |

### Input/Output Examples

**Current System State (run `just triage-observations`):**
```
Found N archived items with untriaged observations:
  E2-215: 3 observations
  E2-216: 2 observations
  ...
```

**After Fix:**
```
During /close E2-224:
  OBSERVE phase step 2d:
    "Pending observations across archive: 12"
    "Threshold exceeded (12 > 10). Invoking inline triage."
    [observation-triage-cycle runs]
  ARCHIVE phase continues...
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Empty archive | Returns 0, no triage | Test 1 |
| Exactly at threshold (10) | No triage (> not >=) | Test 4 |
| All observations already triaged | Returns 0, no triage | Covered by scan_archived_observations logic |

### Open Questions

**Q: Should the threshold be configurable per-project?**

Deferred to E2-222 (Routing Threshold Configuration). Current implementation uses hardcoded default.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add 4 tests to `tests/test_observations.py` (Tests 1-4 from Tests First section)
- [ ] Import `get_pending_observation_count`, `should_trigger_triage` (will fail - not implemented)
- [ ] Run tests - verify they FAIL (ImportError expected)

### Step 2: Implement Threshold Functions
- [ ] Add `DEFAULT_OBSERVATION_THRESHOLD = 10` constant
- [ ] Add `get_pending_observation_count()` function
- [ ] Add `should_trigger_triage()` function
- [ ] Update module exports in docstring
- [ ] Tests 1-4 pass (green)

### Step 3: Update SKILL.md
- [ ] Add step 2d section after step 2c (line ~115)
- [ ] Update Exit Criteria to include threshold check
- [ ] Update Composition Map with new tool reference

### Step 4: Integration Verification
- [ ] Run `pytest tests/test_observations.py -v` - all pass
- [ ] Run full test suite `pytest tests/ -v` - no regressions
- [ ] Demo: Run `python -c "from observations import get_pending_observation_count; print(get_pending_observation_count())"` from .claude/lib

### Step 5: README Sync (MUST)
- [ ] **N/A:** No structural changes to directories
- [ ] **N/A:** observations.py already documented in .claude/lib/README.md

---

## Verification

- [ ] Tests pass (`pytest tests/test_observations.py -v`)
- [ ] **N/A:** No README changes needed (no structural changes)
- [ ] SKILL.md updated with step 2d

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Triage cycle too slow | Low | Triage is interactive, agent controls pace |
| Threshold too high | Low | Start with 10, adjust based on experience |
| scan_archived_observations slow | Low | Already tested, efficient enough |

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
| `.claude/lib/observations.py` | `get_pending_observation_count()` and `should_trigger_triage()` exist | [ ] | |
| `tests/test_observations.py` | 4 new tests for threshold functions | [ ] | |
| `.claude/skills/close-work-cycle/SKILL.md` | Step 2d (Threshold Check) section exists | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_observations.py -v
# Expected: All tests pass including new threshold tests
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
- [ ] **N/A:** No README changes (no structural changes)
- [ ] **N/A:** Not a migration, no consumer verification needed
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- **INV-048:** Routing Gate Architecture (source investigation)
- **E2-217:** Observation Capture Gate (capture mechanism)
- **E2-218:** Observation Triage Skill (triage workflow)
- **Memory 79956:** Threshold value decision (count > 10)
- **Memory 79965:** OBSERVE phase design decision

---
