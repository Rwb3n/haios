---
template: implementation_plan
status: complete
date: 2026-02-03
backlog_id: WORK-066
title: Queue Position Field Implementation
author: Hephaestus
lifecycle_phase: plan
session: 305
version: '1.5'
generated: 2026-02-03
last_updated: '2026-02-04T21:15:56'
---
# Implementation Plan: Queue Position Field Implementation

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
| Query prior work | SHOULD | DONE: memory_search returned 10 relevant concepts (82953, 82958, 82968, etc.) |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

Add `queue_position` field to work items and rename `current_node` to `cycle_phase`, enabling orthogonal tracking of work selection state per the four-dimensional model from WORK-065.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | work_engine.py, TRD-WORK-ITEM-UNIVERSAL.md, work_item.md template |
| Lines of code affected | ~70 | WorkEngine (~40), TRD (~20), template (~10) |
| New files to create | 1 | test_queue_position.py |
| Tests to write | 6 | See Tests First section |
| Dependencies | 2 | GovernanceLayer (reads), cycle_runner (reads) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | WorkEngine + template + TRD |
| Risk of regression | Low | Adding new field with backward compat defaults |
| External dependencies | Low | No external APIs |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Phase 1: Schema Changes (WorkState, _parse_work_file) | 20 min | High |
| Phase 2: New Methods (set_queue_position, get_in_progress) | 20 min | High |
| Phase 3: TRD + Template Updates | 15 min | High |
| Phase 4: Tests | 25 min | High |
| **Total** | ~1.5 hr | High |

---

## Current State vs Desired State

### Current State

```yaml
# docs/work/active/WORK-066/WORK.md frontmatter (current)
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-02-01 20:56:18
    exited: null
```

```python
# .claude/haios/modules/work_engine.py:90-100 - WorkState dataclass
@dataclass
class WorkState:
    id: str
    title: str
    status: str
    current_node: str  # Conflates queue position and cycle phase
    type: str = "feature"
```

**Behavior:** `current_node` conflates queue position and cycle phase. 94% of work items stuck at `backlog` regardless of actual status (WORK-065 finding).

**Result:** No visibility into work selection pipeline state.

### Desired State

```yaml
# docs/work/active/WORK-066/WORK.md frontmatter (target)
queue_position: in_progress     # NEW: work selection state
cycle_phase: implement          # RENAMED from current_node
cycle_phase_history:
  - phase: backlog
    entered: 2026-02-01 20:56:18
    exited: 2026-02-03T23:54:00
  - phase: implement
    entered: 2026-02-03T23:54:00
    exited: null
```

```python
# .claude/haios/modules/work_engine.py - WorkState dataclass (target)
@dataclass
class WorkState:
    id: str
    title: str
    status: str
    queue_position: str = "backlog"  # NEW: backlog|in_progress|done
    cycle_phase: str = "backlog"     # RENAMED from current_node
    current_node: str = "backlog"    # DEPRECATED: kept for backward compat
    type: str = "feature"
```

**Behavior:** Two separate fields track orthogonal concerns:
- `queue_position`: backlog -> in_progress -> done (work selection pipeline)
- `cycle_phase`: discovery -> plan -> implement -> close (lifecycle phase)

**Result:** Clear visibility into where work is in selection pipeline and what phase it's in.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Queue Position Field Parsing
```python
def test_parse_queue_position():
    """WorkEngine._parse_work_file reads queue_position field."""
    # Setup: Create temp WORK.md with queue_position: in_progress
    work_content = """---
id: TEST-001
title: Test
status: active
queue_position: in_progress
---
# TEST-001
"""
    # Action: engine._parse_work_file(path)
    work = engine._parse_work_file(path)
    # Assert
    assert work.queue_position == "in_progress"
```

### Test 2: Queue Position Default Value
```python
def test_queue_position_defaults_to_backlog():
    """Work items without queue_position field default to 'backlog'."""
    # Setup: Create temp WORK.md WITHOUT queue_position field
    work_content = """---
id: TEST-002
title: Test
status: active
current_node: backlog
---
# TEST-002
"""
    work = engine._parse_work_file(path)
    assert work.queue_position == "backlog"
```

### Test 3: Set Queue Position
```python
def test_set_queue_position():
    """WorkEngine.set_queue_position updates field in file."""
    # Setup: Create work item
    engine.create_work("TEST-003", "Test Item")
    # Action
    engine.set_queue_position("TEST-003", "in_progress")
    # Assert: re-read shows queue_position: in_progress
    work = engine.get_work("TEST-003")
    assert work.queue_position == "in_progress"
```

### Test 4: Get In Progress Items
```python
def test_get_in_progress_items():
    """WorkEngine.get_in_progress returns items with queue_position: in_progress."""
    # Setup: Create 3 items, set one to in_progress
    engine.create_work("TEST-004A", "Item A")
    engine.create_work("TEST-004B", "Item B")
    engine.create_work("TEST-004C", "Item C")
    engine.set_queue_position("TEST-004B", "in_progress")
    # Action
    in_progress = engine.get_in_progress()
    # Assert
    assert len(in_progress) == 1
    assert in_progress[0].id == "TEST-004B"
```

### Test 5: Cycle Phase Backward Compat
```python
def test_cycle_phase_falls_back_to_current_node():
    """cycle_phase falls back to current_node for legacy items."""
    # Setup: Create WORK.md with current_node but NO cycle_phase
    work_content = """---
id: TEST-005
title: Test
status: active
current_node: implement
---
# TEST-005
"""
    work = engine._parse_work_file(path)
    assert work.cycle_phase == "implement"  # Falls back to current_node
```

### Test 6: Invalid Queue Position Rejected
```python
def test_invalid_queue_position_raises():
    """set_queue_position rejects invalid values."""
    engine.create_work("TEST-006", "Test Item")
    with pytest.raises(ValueError):
        engine.set_queue_position("TEST-006", "invalid_value")
```

---

## Detailed Design

<!-- Pattern verified: work_engine.py uses try/except conditional imports (lines 51-62) -->

### Change 1: WorkState Dataclass

**File:** `.claude/haios/modules/work_engine.py`
**Location:** Lines 90-112 in `WorkState` dataclass

**Current Code:**
```python
# work_engine.py:90-112
@dataclass
class WorkState:
    """Typed work item state from parsed WORK.md.

    WORK-001: Extended with universal work item fields for pipeline portability.
    """

    id: str
    title: str
    status: str
    current_node: str
    type: str = "feature"
    # ... remaining fields
```

**Changed Code:**
```python
@dataclass
class WorkState:
    """Typed work item state from parsed WORK.md.

    WORK-001: Extended with universal work item fields for pipeline portability.
    WORK-066: Added queue_position and cycle_phase per four-dimensional model.
    """

    id: str
    title: str
    status: str
    queue_position: str = "backlog"  # WORK-066: backlog|in_progress|done
    cycle_phase: str = "backlog"     # WORK-066: renamed from current_node
    current_node: str = "backlog"    # DEPRECATED: use cycle_phase (backward compat)
    type: str = "feature"
    # ... remaining fields
```

### Change 2: _parse_work_file Method

**File:** `.claude/haios/modules/work_engine.py`
**Location:** Lines 688-707 in `_parse_work_file()`

**Current Code:**
```python
# work_engine.py:688-707
def _parse_work_file(self, path: Path) -> Optional[WorkState]:
    # ...
    fm = yaml.safe_load(parts[1]) or {}
    return WorkState(
        id=fm.get("id", ""),
        title=fm.get("title", ""),
        status=fm.get("status", ""),
        current_node=fm.get("current_node", "backlog"),
        type=fm.get("type", fm.get("category", "feature")),
        # ...
    )
```

**Changed Code:**
```python
def _parse_work_file(self, path: Path) -> Optional[WorkState]:
    # ...
    fm = yaml.safe_load(parts[1]) or {}
    # WORK-066: Parse queue_position and cycle_phase with backward compat
    current_node_val = fm.get("current_node", "backlog")
    return WorkState(
        id=fm.get("id", ""),
        title=fm.get("title", ""),
        status=fm.get("status", ""),
        queue_position=fm.get("queue_position", "backlog"),  # WORK-066: new field
        cycle_phase=fm.get("cycle_phase", current_node_val), # WORK-066: fallback
        current_node=current_node_val,  # DEPRECATED: kept for backward compat
        type=fm.get("type", fm.get("category", "feature")),
        # ...
    )
```

### Change 3: Update _write_work_file (REVISED per critique A1)

**File:** `.claude/haios/modules/work_engine.py`
**Location:** Lines 709-732 in `_write_work_file()`

**Current Code:**
```python
# work_engine.py:709-732
def _write_work_file(self, work: WorkState) -> None:
    # ...
    fm = yaml.safe_load(parts[1]) or {}
    fm["current_node"] = work.current_node
    fm["node_history"] = work.node_history
    fm["memory_refs"] = work.memory_refs
    fm["status"] = work.status

    new_fm = yaml.dump(...)
```

**Changed Code:**
```python
def _write_work_file(self, work: WorkState) -> None:
    # ...
    fm = yaml.safe_load(parts[1]) or {}
    fm["current_node"] = work.current_node
    fm["node_history"] = work.node_history
    fm["memory_refs"] = work.memory_refs
    fm["status"] = work.status
    # WORK-066: Persist queue_position and cycle_phase (unified write path)
    fm["queue_position"] = work.queue_position
    fm["cycle_phase"] = work.cycle_phase
    fm["last_updated"] = datetime.now().isoformat()

    new_fm = yaml.dump(...)
```

**Rationale (A1 mitigation):** Unifies write path - all WorkState persistence goes through `_write_work_file()`. Prevents data loss from dual write paths.

### Change 4: New Methods (after add_memory_refs, ~line 617)

**File:** `.claude/haios/modules/work_engine.py`
**Location:** After line 617 (add_memory_refs method)

**New Code:**
```python
# ========== Queue Position Methods (WORK-066) ==========

def set_queue_position(self, id: str, position: str) -> Optional[WorkState]:
    """
    Set queue_position for work item (WORK-066).

    Uses unified write path via _write_work_file() per critique A1.

    Args:
        id: Work item ID
        position: New position (backlog, in_progress, done)

    Returns:
        Updated WorkState, or None if not found

    Raises:
        ValueError: If position is not valid
    """
    VALID_POSITIONS = {"backlog", "in_progress", "done"}
    if position not in VALID_POSITIONS:
        raise ValueError(f"Invalid queue_position: {position}. Must be one of {VALID_POSITIONS}")

    work = self.get_work(id)
    if work is None:
        return None

    # Update in-memory state
    work.queue_position = position

    # Persist via unified write path (A1 mitigation)
    self._write_work_file(work)

    return work

def get_in_progress(self) -> List[WorkState]:
    """
    Get all work items with queue_position: in_progress (WORK-066).

    Used by survey-cycle to enforce single in_progress constraint.

    Returns:
        List of WorkState with queue_position == "in_progress"
    """
    result = []
    if not self.active_dir.exists():
        return result

    for subdir in self.active_dir.iterdir():
        if subdir.is_dir():
            work_md = subdir / "WORK.md"
            if work_md.exists():
                work = self._parse_work_file(work_md)
                if work and work.queue_position == "in_progress":
                    result.append(work)
    return result
```

### Call Chain Context

```
survey-cycle (future wiring)
    |
    +-> WorkEngine.get_in_progress()    # Check constraint
    |       Returns: List[WorkState]
    |
    +-> WorkEngine.set_queue_position(id, "in_progress")  # Set on selection
            Returns: WorkState

close-work-cycle (future wiring)
    |
    +-> WorkEngine.set_queue_position(id, "done")  # Set on closure
            Returns: WorkState
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Add new field vs overload current_node | Add `queue_position` field | Clean separation per WORK-065; current_node conflates 3 vocabularies |
| Rename current_node | Rename to `cycle_phase` | Operator decision (Session 305); better semantic clarity |
| Keep current_node for compat | Yes, as deprecated alias | Existing code references current_node; avoid breaking changes |
| queue_position values | backlog, in_progress, done | Simplified from L5 (removed "todo" - survey-cycle handles selection) |
| Default queue_position | "backlog" | All existing items are unselected by definition |
| Enforcement location | get_in_progress() method | survey-cycle calls this; WorkEngine doesn't enforce (separation) |
| **Unified write path (A1)** | `set_queue_position` uses `_write_work_file` | Critique A1: Prevents data loss from dual write paths |

### Input/Output Examples

**Before (current WORK-066):**
```yaml
# just ready returns 32+ items
# No way to know which is "being worked on"
current_node: backlog  # Stuck despite being actively worked
```

**After (expected):**
```yaml
# WORK-066 after survey-cycle selection
queue_position: in_progress  # Shows this is THE active work item
cycle_phase: plan            # Shows lifecycle phase
```

**Real Data Example:**
```
Current: WorkEngine.get_work("WORK-066")
  - current_node: "backlog"
  - (no queue_position field)

After: WorkEngine.get_work("WORK-066")
  - queue_position: "backlog" (default until survey-cycle selects)
  - cycle_phase: "backlog" (falls back to current_node)
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Legacy items without queue_position | Default to "backlog" | Test 2 |
| Legacy items without cycle_phase | Fall back to current_node | Test 5 |
| Invalid queue_position value | Raise ValueError | Test 6 |
| Work item not found | Return None | (guard clause) |

### Open Questions

**Q: Should we migrate existing work items to add queue_position?**

No - backward compatibility defaults handle this. Items without the field get `queue_position: backlog` on read. This is correct since they haven't been selected.

---

## Open Decisions (MUST resolve before implementation)

<!-- Decisions from work item's operator_decisions field.
     If ANY row has [BLOCKED] in Chosen column, plan-validation-cycle will BLOCK.

     POPULATE FROM: Work item frontmatter `operator_decisions` field -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Rename current_node to cycle_phase? | [rename, keep] | rename to cycle_phase | Operator decision (Session 305): Better semantic clarity, aligns with four-dimensional model terminology |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [x] Create `tests/test_work_engine.py` (added to existing file)
- [x] Add 6 tests from "Tests First" section
- [x] Verify all tests fail (red) - Session 307

### Step 2: Update WorkState Dataclass
- [x] Add `queue_position: str = "backlog"` field
- [x] Add `cycle_phase: str = "backlog"` field
- [x] Keep `current_node` as deprecated alias
- [x] Tests 1, 2, 5 pass (green)

### Step 3: Update _parse_work_file
- [x] Parse `queue_position` with default "backlog"
- [x] Parse `cycle_phase` with fallback to `current_node`
- [x] Tests 1, 2, 5 pass (green)

### Step 4: Update _write_work_file (A1 mitigation)
- [x] Add `fm["queue_position"] = work.queue_position`
- [x] Add `fm["cycle_phase"] = work.cycle_phase`
- [x] Add `fm["last_updated"] = datetime.now().isoformat()`

### Step 5: Add New WorkEngine Methods
- [x] Add `set_queue_position(id, position)` method (uses unified write path)
- [x] Add `get_in_progress()` method
- [x] Tests 3, 4, 6 pass (green)

### Step 6: Update TRD-WORK-ITEM-UNIVERSAL.md
- [x] Add `queue_position` field to schema
- [x] Add `cycle_phase` field (note current_node as deprecated)
- [x] Update Lifecycle Nodes section

### Step 7: Update work_item.md Template
- [x] Add `queue_position: backlog` to frontmatter
- [x] Add `cycle_phase: backlog` to frontmatter
- [ ] Add `cycle_phase_history` section - SKIPPED (node_history handles this)

### Step 8: Integration Verification
- [x] All 6 tests pass
- [x] Run full test suite: `pytest tests/test_work_engine.py -v`
- [x] No regressions (41 tests pass)

### Step 9: README Sync (MUST)
- [x] **MUST:** Update `.claude/haios/modules/README.md` with new methods
- [x] **MUST:** Verify README content matches actual file state

### Step 10: Consumer Verification (MUST for renames)
- [x] **MUST:** Grep for references to `current_node` in modules
- [x] **MUST:** Document consumers (cli.py, work_engine.py, work-creation-cycle SKILL.md)
- [x] **MUST:** Verify cycle_phase fallback works for all existing items (demo verified)

**Consumer Discovery Pattern:**
```bash
Grep(pattern="current_node", path=".claude/haios/modules", glob="**/*.py")
Grep(pattern="current_node", path=".claude/skills", glob="**/*.md")
```

> **Note:** current_node kept for backward compat - consumers don't need immediate updates

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing code that uses current_node | Medium | Keep current_node as deprecated alias; all existing consumers continue working |
| Spec misalignment (queue_position values) | Low | Values (backlog, in_progress, done) explicitly match simplified L5 model |
| Integration regression | Low | Full test suite run after each step; 6 new tests cover all new functionality |
| Scope creep (wiring survey/close cycles) | Medium | Scope limited to WorkEngine + schema; skill wiring tracked as future work |
| Knowledge gap: how scaffold.py handles new fields | Low | Read scaffold.py before implementation; follow existing patterns |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 305 | 2026-02-03 | (pending) | Plan authored | Ready for validation |
| 307 | 2026-02-04 | (pending) | Implementation complete | All steps done, 41 tests pass |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-066/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| TRD Update - Add queue_position field | [x] | TRD-WORK-ITEM-UNIVERSAL.md:110 has queue_position field |
| Template Update - Add queue_position | [x] | work_item.md:22 has queue_position field |
| Survey-cycle Wiring | N/A | **OUT OF SCOPE** - separate work item |
| Close-work-cycle Wiring | N/A | **OUT OF SCOPE** - separate work item |
| Single In_Progress Constraint | [x] | get_in_progress() method at work_engine.py:662 |
| Vocabulary Alignment (rename to cycle_phase) | [x] | WorkState.cycle_phase at work_engine.py:104 |

> **Scope Note:** This plan covers schema changes only. Skill wiring (survey-cycle, close-work-cycle) will be tracked as follow-up work items per WORK-066 deliverables.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/work_engine.py` | WorkState has queue_position, cycle_phase; set_queue_position(), get_in_progress() exist | [x] | Lines 103-104, 626-678 |
| `tests/test_work_engine.py` | 6 WORK-066 tests exist and pass | [x] | Tests added to existing file, all 41 tests pass |
| `docs/specs/TRD-WORK-ITEM-UNIVERSAL.md` | queue_position field documented | [x] | Lines 110-112, 230-270 |
| `.claude/templates/work_item.md` | queue_position, cycle_phase in frontmatter | [x] | Lines 22-24 |
| `.claude/haios/modules/README.md` | **MUST:** Reflects new methods | [x] | WorkState and Functions tables updated |

**Verification Commands:**
```bash
pytest tests/test_work_engine.py -v
# Result: 41 tests passed (including 6 WORK-066 tests)
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | All files read and verified in Session 307 |
| Test output pasted above? | Yes | 41 passed in 0.86s |
| Any deviations from plan? | Yes | Tests added to existing test_work_engine.py instead of separate file |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (41 tests including 6 WORK-066 tests)
- [x] **MUST:** All WORK.md deliverables verified complete (4/4 in-scope, 2 out-of-scope)
- [ ] **Runtime consumer exists** - Pending: survey-cycle and close-work-cycle wiring (separate work items)
- [x] WHY captured (memory concepts 83938-83949)
- [x] **MUST:** READMEs updated in all modified directories (.claude/haios/modules/README.md)
- [x] **MUST:** Consumer verification complete (current_node kept for backward compat)
- [x] All traced files complete
- [x] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.
> **E2-290 Learning (Session 192):** "Tests pass" ≠ "Deliverables complete". Agent declared victory after tests passed but skipped 2 of 7 deliverables.

---

## References

- @docs/work/active/WORK-016/WORK.md (investigation decision - wire transitions)
- @docs/work/active/WORK-065/WORK.md (four-dimensional model design)
- @docs/specs/TRD-WORK-ITEM-UNIVERSAL.md (target spec)
- @.claude/haios/modules/governance_layer.py:59-68 (VALID_TRANSITIONS)
- @.claude/haios/modules/work_engine.py (target implementation)
- Memory refs: 82952, 82953, 82954, 82958, 82968, 83051, 83054

---
