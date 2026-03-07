---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-03-07
backlog_id: WORK-251
title: "Coldstart Crash Recovery — Fix False-Positive Incomplete Work Detection"
author: Hephaestus
lifecycle_phase: plan
session: 475
generated: 2026-03-07
last_updated: 2026-03-07T18:05:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-251/WORK.md"
    required: true
  - field: source_files_exist
    verify: "all paths in WORK.md source_files exist on disk"
    required: true

output_contract:
  - field: layer_0_complete
    verify: "Layer 0 tables have no placeholder rows"
  - field: layer_1_complete
    verify: "Layer 1 has concrete code blocks, not pseudocode"
  - field: layer_2_complete
    verify: "every step has input/action/output/verify fields"
  - field: layer_3_complete
    verify: "every verification line has a command and expected output"
---
# Implementation Plan: Coldstart Crash Recovery — Fix False-Positive Incomplete Work Detection

---

## Goal

Fix `scan_incomplete_work()` to only flag work items in active lifecycle phases (PLAN/DO/CHECK/DONE/CHAIN), eliminating false-positive noise from backlog/ready/working items that are not actually stuck.

---

## Open Decisions

None. Approach approved by operator: filter by `cycle_phase` to distinguish "actively being worked in a lifecycle" from "sitting in queue".

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/haios/lib/governance_events.py` | MODIFY | 2 |

### Consumer Files

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `.claude/haios/lib/coldstart_orchestrator.py` | calls `scan_incomplete_work()` | 111 | NO CHANGE (signature unchanged) |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_governance_events.py` | UPDATE | Add tests for filtered incomplete work detection |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | No new files |
| Files to modify | 2 | governance_events.py + test file |
| Tests to write | 4 | See Layer 1 Tests |
| Total blast radius | 2 | governance_events.py, test file |

---

## Layer 1: Specification

### Current State

```python
# governance_events.py:307-368 — scan_incomplete_work()
def scan_incomplete_work(project_root: Path) -> list[dict]:
    # ...
    for dir_path in work_dirs:
        for subdir in dir_path.iterdir():
            work_file = subdir / "WORK.md"
            # ...
            # Check for exited: null in node_history
            if "exited: null" in yaml_content or "exited: ~" in yaml_content:
                # Extract id
                id_match = re.search(r"id:\s*(\S+)", yaml_content)
                # Extract current node
                node_match = re.search(r"node:\s*(\S+)", yaml_content)
                if id_match:
                    incomplete.append({
                        "id": id_match.group(1).strip(),
                        "incomplete_node": node_match.group(1).strip() if node_match else "unknown",
                        "path": str(work_file.relative_to(project_root)),
                    })
    return incomplete
```

**Behavior:** Flags ALL work items with `exited: null` in node_history as "incomplete/stuck".
**Problem:** `exited: null` is the normal state for any work item's current node. All 28 backlog items show as "stuck in 'backlog'" because their current node_history entry naturally has `exited: null`. This drowns real crash signals in noise.

### Desired State

```python
# governance_events.py:307-368 — scan_incomplete_work()
# Add lifecycle phase filter: only flag items in active lifecycle phases
LIFECYCLE_PHASES = {"PLAN", "DO", "CHECK", "DONE", "CHAIN"}

def scan_incomplete_work(project_root: Path) -> list[dict]:
    # ...
    for dir_path in work_dirs:
        for subdir in dir_path.iterdir():
            work_file = subdir / "WORK.md"
            # ...
            # Extract cycle_phase
            phase_match = re.search(r"cycle_phase:\s*(\S+)", yaml_content)
            cycle_phase = phase_match.group(1).strip() if phase_match else ""

            # Only flag items in active lifecycle phases
            # Items in backlog/ready/working are in queue, not stuck in a lifecycle
            if cycle_phase not in LIFECYCLE_PHASES:
                continue

            # Check for exited: null in node_history
            if "exited: null" in yaml_content or "exited: ~" in yaml_content:
                id_match = re.search(r"id:\s*(\S+)", yaml_content)
                node_match = re.search(r"node:\s*(\S+)", yaml_content)
                if id_match:
                    incomplete.append({
                        "id": id_match.group(1).strip(),
                        "incomplete_node": node_match.group(1).strip() if node_match else "unknown",
                        "path": str(work_file.relative_to(project_root)),
                    })
    return incomplete
```

**Behavior:** Only flags work items whose `cycle_phase` is a lifecycle phase (PLAN/DO/CHECK/DONE/CHAIN). Queue positions (backlog/ready/working) are filtered out.
**Result:** Coldstart RECOVERY phase only shows genuinely stuck items (e.g., crashed mid-DO), not normal backlog noise.

### Tests

#### Test 1: Backlog items not flagged as incomplete
- **file:** `tests/test_governance_events.py`
- **function:** `test_scan_incomplete_work_ignores_backlog_items()`
- **setup:** Create tmp_path with WORK.md containing `cycle_phase: backlog`, `node_history` with `exited: null`
- **assertion:** `scan_incomplete_work(tmp_path)` returns empty list

#### Test 2: PLAN phase item flagged as incomplete
- **file:** `tests/test_governance_events.py`
- **function:** `test_scan_incomplete_work_flags_lifecycle_phase_items()`
- **setup:** Create tmp_path with WORK.md containing `cycle_phase: DO`, `node_history` with `exited: null`
- **assertion:** `scan_incomplete_work(tmp_path)` returns 1 item with `incomplete_node` set

#### Test 3: Mixed items — only lifecycle ones flagged
- **file:** `tests/test_governance_events.py`
- **function:** `test_scan_incomplete_work_mixed_items()`
- **setup:** Create tmp_path with 3 WORK.md files: one backlog, one DO, one ready
- **assertion:** `scan_incomplete_work(tmp_path)` returns exactly 1 item (the DO one)

#### Test 4: Missing cycle_phase defaults to not-flagged
- **file:** `tests/test_governance_events.py`
- **function:** `test_scan_incomplete_work_missing_cycle_phase_not_flagged()`
- **setup:** Create tmp_path with WORK.md containing no `cycle_phase` field, `node_history` with `exited: null`
- **assertion:** `scan_incomplete_work(tmp_path)` returns empty list (conservative: missing data = not flagged, prevents false positives)

### Design

#### File 1 (MODIFY): `.claude/haios/lib/governance_events.py`

**Location:** Lines 307-368 in `scan_incomplete_work()`

**Current Code:**
```python
def scan_incomplete_work(project_root: Path) -> list[dict]:
    """
    Scan WORK.md files for incomplete transitions (exited: null).

    Per INV-052 Section 2A: Scan for `exited: null` entries in node_history.

    Args:
        project_root: Project root path (accepts str or Path)

    Returns:
        List of dicts with id, incomplete_node, path
    """
    import re

    project_root = Path(project_root)  # WORK-129: Coerce string to Path

    work_dirs = [
        project_root / "docs" / "work" / "active",
        project_root / "docs" / "work" / "blocked",
    ]
    incomplete = []

    for dir_path in work_dirs:
        if not dir_path.exists():
            continue
        for subdir in dir_path.iterdir():
            if not subdir.is_dir():
                continue
            work_file = subdir / "WORK.md"
            if not work_file.exists():
                continue

            content = work_file.read_text(encoding="utf-8", errors="ignore")
            # Parse YAML frontmatter
            match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
            if not match:
                continue

            yaml_content = match.group(1)

            # Extract status field and skip terminal statuses
            # Uses same terminal set as WorkEngine.get_ready() (Session 211)
            status_match = re.search(r"status:\s*(\S+)", yaml_content)
            status = status_match.group(1).strip() if status_match else ""
            terminal_statuses = {"complete", "archived", "dismissed", "invalid", "deferred"}
            if status in terminal_statuses:
                continue

            # Check for exited: null in node_history
            if "exited: null" in yaml_content or "exited: ~" in yaml_content:
                # Extract id
                id_match = re.search(r"id:\s*(\S+)", yaml_content)
                # Extract current node
                node_match = re.search(r"node:\s*(\S+)", yaml_content)
                if id_match:
                    incomplete.append({
                        "id": id_match.group(1).strip(),
                        "incomplete_node": node_match.group(1).strip() if node_match else "unknown",
                        "path": str(work_file.relative_to(project_root)),
                    })

    return incomplete
```

**Target Code:**
```python
# Module-level constant (add near top of file, after imports)
LIFECYCLE_PHASES = {"PLAN", "DO", "CHECK", "DONE", "CHAIN"}

def scan_incomplete_work(project_root: Path) -> list[dict]:
    """
    Scan WORK.md files for incomplete transitions (exited: null).

    Per INV-052 Section 2A: Scan for `exited: null` entries in node_history.
    WORK-251: Only flags items in active lifecycle phases (PLAN/DO/CHECK/DONE/CHAIN).
    Items in queue positions (backlog/ready/working) are normal — not stuck.

    Args:
        project_root: Project root path (accepts str or Path)

    Returns:
        List of dicts with id, incomplete_node, path
    """
    import re

    project_root = Path(project_root)  # WORK-129: Coerce string to Path

    work_dirs = [
        project_root / "docs" / "work" / "active",
        project_root / "docs" / "work" / "blocked",
    ]
    incomplete = []

    for dir_path in work_dirs:
        if not dir_path.exists():
            continue
        for subdir in dir_path.iterdir():
            if not subdir.is_dir():
                continue
            work_file = subdir / "WORK.md"
            if not work_file.exists():
                continue

            content = work_file.read_text(encoding="utf-8", errors="ignore")
            # Parse YAML frontmatter
            match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
            if not match:
                continue

            yaml_content = match.group(1)

            # Extract status field and skip terminal statuses
            # Uses same terminal set as WorkEngine.get_ready() (Session 211)
            status_match = re.search(r"status:\s*(\S+)", yaml_content)
            status = status_match.group(1).strip() if status_match else ""
            terminal_statuses = {"complete", "archived", "dismissed", "invalid", "deferred"}
            if status in terminal_statuses:
                continue

            # WORK-251: Only flag items in active lifecycle phases
            # Items in queue positions (backlog/ready/working) have exited:null
            # on their current node as normal state — not stuck
            phase_match = re.search(r"cycle_phase:\s*(\S+)", yaml_content)
            cycle_phase = phase_match.group(1).strip() if phase_match else ""
            if cycle_phase not in LIFECYCLE_PHASES:
                continue

            # Check for exited: null in node_history
            if "exited: null" in yaml_content or "exited: ~" in yaml_content:
                # Extract id
                id_match = re.search(r"id:\s*(\S+)", yaml_content)
                # Extract current node
                node_match = re.search(r"node:\s*(\S+)", yaml_content)
                if id_match:
                    incomplete.append({
                        "id": id_match.group(1).strip(),
                        "incomplete_node": node_match.group(1).strip() if node_match else "unknown",
                        "path": str(work_file.relative_to(project_root)),
                    })

    return incomplete
```

**Diff:**
```diff
+# Module-level constant
+LIFECYCLE_PHASES = {"PLAN", "DO", "CHECK", "DONE", "CHAIN"}
+
 def scan_incomplete_work(project_root: Path) -> list[dict]:
     """
     Scan WORK.md files for incomplete transitions (exited: null).

     Per INV-052 Section 2A: Scan for `exited: null` entries in node_history.
+    WORK-251: Only flags items in active lifecycle phases (PLAN/DO/CHECK/DONE/CHAIN).
+    Items in queue positions (backlog/ready/working) are normal — not stuck.
     ...
             if status in terminal_statuses:
                 continue

+            # WORK-251: Only flag items in active lifecycle phases
+            phase_match = re.search(r"cycle_phase:\s*(\S+)", yaml_content)
+            cycle_phase = phase_match.group(1).strip() if phase_match else ""
+            if cycle_phase not in LIFECYCLE_PHASES:
+                continue
+
             # Check for exited: null in node_history
```

### Call Chain

```
ColdstartOrchestrator.run()
    |
    +-> _check_for_orphans()
            |
            +-> detect_orphan_session()        # unchanged
            |
            +-> scan_incomplete_work()         # <-- MODIFIED: lifecycle filter
                    Returns: list[dict]        # Now only lifecycle-phase items
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Filter by cycle_phase, not queue_position | cycle_phase | cycle_phase is the lifecycle state. Queue position is orthogonal (WORK-256 addresses sync). Using the lifecycle field is more semantically correct. |
| Missing cycle_phase = not flagged | Conservative against false positives | Older work items may lack cycle_phase. Better to miss a real stuck item than flood with noise. REQ-LIFECYCLE-005: "Absent data MUST NOT produce a more permissive classification" — here applied in reverse: absent data should not produce a more aggressive flagging. |
| LIFECYCLE_PHASES as module constant | Reusability | May be useful for other functions that need to distinguish lifecycle from queue states. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| Work item with no cycle_phase field | Not flagged (empty string not in LIFECYCLE_PHASES) | Test 4 |
| Work item with cycle_phase: backlog | Not flagged | Test 1 |
| Work item with cycle_phase: DO | Flagged if exited:null present | Test 2 |
| Terminal status + lifecycle phase | Already filtered by terminal status check (line before) | Existing tests |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Real stuck items with wrong cycle_phase not detected | L | Items stuck mid-lifecycle will have correct cycle_phase from cycle_set() |
| LIFECYCLE_PHASES set becomes stale | L | Set matches the 5 defined phases from PLAN→DO→CHECK→DONE→CHAIN which are stable |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Add 4 test functions to `tests/test_governance_events.py`
- **output:** Test file updated, 4 new tests fail
- **verify:** `pytest tests/test_governance_events.py -k "scan_incomplete" -v` shows 4 FAILED

### Step 2: Implement Lifecycle Phase Filter (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Add `LIFECYCLE_PHASES` constant and cycle_phase filter to `scan_incomplete_work()`
- **output:** All 4 new tests pass, existing tests still pass
- **verify:** `pytest tests/test_governance_events.py -v` exits 0

### Step 3: Full Suite Regression
- **spec_ref:** Ground Truth Verification
- **input:** Step 2 complete
- **action:** Run full test suite
- **output:** No regressions
- **verify:** `pytest tests/ -v` shows 0 new failures

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_governance_events.py -k "scan_incomplete" -v` | 4+ passed, 0 failed |
| `pytest tests/test_governance_events.py -v` | all passed, 0 failed |
| `pytest tests/ -v` | 0 new failures vs baseline |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| Backlog items not flagged | Run coldstart after fix | RECOVERY phase shows 0 backlog items |
| Lifecycle items flagged | Test 2 passes | Items in PLAN/DO/CHECK/DONE/CHAIN detected |
| Synthetic SessionEnded | Existing implementation | Already works (coldstart_orchestrator.py:107) |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| No stale references | Grep for old scan_incomplete_work signature | Signature unchanged — 0 consumer breaks |
| LIFECYCLE_PHASES accessible | grep "LIFECYCLE_PHASES" governance_events.py | 1+ match |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 2 verify)
- [ ] Coldstart RECOVERY phase no longer shows backlog noise
- [ ] Runtime consumer unchanged (coldstart_orchestrator.py signature stable)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

---

## References

- `.claude/haios/lib/governance_events.py` — primary implementation file
- `.claude/haios/lib/coldstart_orchestrator.py` — consumer (unchanged)
- REQ-CONTEXT-001 — Coldstart MUST inject prior session context
- REQ-CEREMONY-001 — Ceremonies are side-effect boundaries
- INV-052 Section 2A — Original incomplete work detection design

---
