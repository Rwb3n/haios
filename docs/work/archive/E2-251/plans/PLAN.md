---
template: implementation_plan
status: ready
date: 2026-01-03
backlog_id: E2-251
title: Complete WorkEngine Module - Cascade Spawn Backfill
author: Hephaestus
lifecycle_phase: plan
session: 163
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-03T23:39:27'
---
# Implementation Plan: Complete WorkEngine Module - Cascade Spawn Backfill

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

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

WorkEngine will absorb cascade/spawn/backfill functionality from `.claude/lib/`, making it the single owner of all work item operations per INV-052 Section 17.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | work_engine.py, cli.py, justfile |
| Lines of code affected | ~250 | Port logic from cascade.py(596), spawn.py(188), backfill.py(271) |
| New files to create | 0 | All additions to existing files |
| Tests to write | 10 | 7 unit + 3 integration |
| Dependencies | 2 | status.py (cascade), backlog.md (backfill) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | justfile, haios-status.json, backlog.md |
| Risk of regression | Low | New methods, existing WorkEngine tests stable |
| External dependencies | Low | Only internal files |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests (RED) | 30 min | High |
| cascade() | 45 min | High |
| spawn_tree() | 20 min | High |
| backfill() | 30 min | High |
| CLI + justfile | 15 min | High |
| **Total** | ~2.5 hr | High |

---

## Current State vs Desired State

### Current State

**Files:**
- `.claude/lib/cascade.py` - 596 lines, standalone module
- `.claude/lib/spawn.py` - 188 lines, standalone module
- `.claude/lib/backfill.py` - 271 lines, standalone module

**Justfile recipes call legacy code:**
```just
# justfile:93-94
cascade id status:
    python -c "import sys; sys.path.insert(0, '.claude/lib'); from cascade import run_cascade; ..."

# justfile:240-241
spawns id:
    python -c "import sys; sys.path.insert(0, '.claude/lib'); from spawn import build_spawn_tree; ..."
```

**Behavior:** Split ownership - WorkEngine owns CRUD, legacy lib owns cascade/spawn/backfill.

**Result:** INV-052 mandate violated - WorkEngine should be single owner of work operations.

### Desired State

**WorkEngine methods:**
```python
# .claude/haios/modules/work_engine.py
class WorkEngine:
    def cascade(self, id: str, new_status: str) -> CascadeResult: ...
    def spawn_tree(self, root_id: str) -> Dict[str, Any]: ...
    def backfill(self, id: str, force: bool = False) -> bool: ...
```

**Justfile recipes use CLI:**
```just
cascade id status:
    python .claude/haios/modules/cli.py cascade {{id}} {{status}}

spawns id:
    python .claude/haios/modules/cli.py spawn-tree {{id}}
```

**Behavior:** Single ownership - WorkEngine owns ALL work item operations.

**Result:** INV-052 compliance; legacy `.claude/lib/` can be deprecated.

---

## Tests First (TDD)

### Test 1: cascade_unblocks_items
```python
def test_cascade_unblocks_items(tmp_path):
    """When E2-100 completes, E2-101 (blocked_by: [E2-100]) becomes READY."""
    # Setup: Create E2-100 and E2-101 where E2-101 blocked_by E2-100
    # Action: engine.cascade("E2-100", "complete")
    # Assert: result.unblocked contains "E2-101"
```

### Test 2: cascade_partial_unblock
```python
def test_cascade_partial_unblock(tmp_path):
    """E2-101 blocked_by [E2-100, E2-102] - completing E2-100 leaves still blocked."""
    # Setup: E2-101 blocked by two items
    # Action: cascade("E2-100", "complete")
    # Assert: result.still_blocked contains "E2-101", result.unblocked is empty
```

### Test 3: cascade_finds_related
```python
def test_cascade_finds_related(tmp_path):
    """Both inbound and outbound related items are discovered."""
    # Setup: E2-100 related: [E2-102], E2-101 related: [E2-100]
    # Action: cascade("E2-100", "complete")
    # Assert: result.related contains both "E2-101" (inbound) and "E2-102" (outbound)
```

### Test 4: spawn_tree_simple
```python
def test_spawn_tree_simple(tmp_path):
    """INV-X spawns E2-A, E2-B -> tree shows both as children."""
    # Setup: E2-A and E2-B both have spawned_by: INV-017
    # Action: tree = engine.spawn_tree("INV-017")
    # Assert: tree == {"INV-017": {"E2-A": {}, "E2-B": {}}}
```

### Test 5: spawn_tree_nested
```python
def test_spawn_tree_nested(tmp_path):
    """INV-X spawns E2-A, E2-A spawns E2-B -> nested tree."""
    # Setup: E2-A spawned_by INV-017, E2-B spawned_by E2-A
    # Action: tree = engine.spawn_tree("INV-017")
    # Assert: tree == {"INV-017": {"E2-A": {"E2-B": {}}}}
```

### Test 6: backfill_updates_context
```python
def test_backfill_updates_context(tmp_path):
    """Placeholder [Problem and root cause] is replaced with backlog context."""
    # Setup: Work file with placeholder, backlog with context
    # Action: engine.backfill("E2-021")
    # Assert: Work file now contains actual context from backlog
```

### Test 7: backfill_updates_deliverables
```python
def test_backfill_updates_deliverables(tmp_path):
    """Placeholder deliverables are replaced with backlog checklist."""
    # Setup: Work file with [Deliverable 1], backlog with real checklist
    # Action: engine.backfill("E2-021")
    # Assert: Work file has actual deliverables
```

### Test 8: cli_cascade (Integration)
```python
def test_cli_cascade():
    """just cascade E2-100 complete -> outputs cascade report."""
    # Run: python cli.py cascade E2-100 complete
    # Assert: Output contains "--- Cascade ---"
```

### Test 9: cli_spawn_tree (Integration)
```python
def test_cli_spawn_tree():
    """just spawns INV-017 -> outputs ASCII tree."""
    # Run: python cli.py spawn-tree INV-017
    # Assert: Output contains tree structure
```

### Test 10: cli_backfill (Integration)
```python
def test_cli_backfill():
    """just backfill E2-021 -> updates work file."""
    # Run: python cli.py backfill E2-021
    # Assert: Output contains "Backfilled" or "Not found"
```

---

## Detailed Design

### 1. CascadeResult Dataclass

**File:** `.claude/haios/modules/work_engine.py`
**Add after WorkState class:**

```python
@dataclass
class CascadeResult:
    """Result of cascade operation."""
    unblocked: List[str]       # IDs now READY (all blockers complete)
    still_blocked: List[str]   # IDs with remaining blockers
    related: List[str]         # IDs to review (bidirectional)
    milestone_delta: Optional[int]  # Progress change (+N%)
    substantive_refs: List[str]     # Files referencing completed ID
    message: str               # Formatted cascade report
```

### 2. WorkEngine.cascade()

**Signature:**
```python
def cascade(self, id: str, new_status: str, dry_run: bool = False) -> CascadeResult:
    """
    Run cascade for completed item.

    Checks:
    1. UNBLOCK - Items blocked by this item
    2. RELATED - Bidirectional related items
    3. MILESTONE - Progress delta
    4. SUBSTANTIVE - CLAUDE.md/README references

    Args:
        id: Work item ID (e.g., "E2-100")
        new_status: New status (must be in TRIGGER_STATUSES)
        dry_run: If True, don't write events or refresh status

    Returns:
        CascadeResult with all cascade effects
    """
```

**Implementation approach:**
- Port helper functions from cascade.py:
  - `_get_unblocked_items()` - Scan work files for blocked_by
  - `_get_related_items()` - Bidirectional related scan
  - `_get_milestone_delta()` - Read haios-status.json
  - `_get_substantive_refs()` - Scan CLAUDE.md, READMEs
- Use `self.active_dir` instead of hardcoded paths
- Write cascade event to `.claude/haios-events.jsonl`

**Trigger statuses:** `{"complete", "completed", "done", "closed", "accepted"}`

### 3. WorkEngine.spawn_tree()

**Signature:**
```python
def spawn_tree(self, root_id: str, max_depth: int = 5) -> Dict[str, Any]:
    """
    Build spawn tree from root_id.

    Traverses spawned_by relationships across work files.

    Args:
        root_id: ID to start tree from
        max_depth: Maximum recursion depth

    Returns:
        Nested dict: {root_id: {child_id: {grandchild_id: {}}}}
    """
```

**Static helper:**
```python
@staticmethod
def format_tree(tree: Dict[str, Any], use_ascii: bool = False) -> str:
    """Format tree as ASCII art."""
```

### 4. WorkEngine.backfill()

**Signatures:**
```python
def backfill(self, id: str, force: bool = False) -> bool:
    """
    Backfill work file from backlog.md/backlog_archive.md.

    Args:
        id: Work item ID
        force: Re-process even if placeholders not found

    Returns:
        True if updated, False if not found or no changes
    """

def backfill_all(self, force: bool = False) -> Dict[str, List[str]]:
    """Backfill all active work items."""
```

**Implementation:**
- Parse backlog sources with regex (port from backfill.py)
- Update Context section (replace `[Problem and root cause]`)
- Update Deliverables (replace placeholder checklist)
- Update frontmatter (milestone, spawned_by, memory_refs)

### 5. CLI Commands

**File:** `.claude/haios/modules/cli.py`
**Add to command dispatch:**

```python
elif cmd == "cascade":
    id, status = args[1], args[2]
    result = engine.cascade(id, status)
    print(result.message)

elif cmd == "spawn-tree":
    tree = engine.spawn_tree(args[1])
    print(WorkEngine.format_tree(tree, use_ascii=True))

elif cmd == "backfill":
    success = engine.backfill(args[1])
    print("Backfilled" if success else "Not found or no changes")

elif cmd == "backfill-all":
    force = "--force" in args
    results = engine.backfill_all(force=force)
    print(f"Success: {len(results['success'])} | Not found: {len(results['not_found'])}")
```

### 6. Justfile Updates

```just
# Update cascade recipe (line 93-94)
cascade id status:
    python .claude/haios/modules/cli.py cascade {{id}} {{status}}

# Update spawns recipe (line 240-241)
spawns id:
    python .claude/haios/modules/cli.py spawn-tree {{id}}

# Update backfill recipes (line 97-106)
backfill id:
    python .claude/haios/modules/cli.py backfill {{id}}

backfill-all:
    python .claude/haios/modules/cli.py backfill-all

backfill-force:
    python .claude/haios/modules/cli.py backfill-all --force
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Port vs rewrite | Port logic wholesale | Logic is correct, just needs new home |
| Keep helpers private | `_get_unblocked_items()` etc | Only `cascade()` is public API |
| TRIGGER_STATUSES constant | Keep same set | Maintains backward compatibility |
| Backlog path | Use PROJECT_ROOT detection | Same as current, works in tests |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Item not found | Return empty CascadeResult | Test implicit |
| Non-trigger status | Return immediately, triggered=False | Test 1 |
| Circular spawn refs | max_depth=5 prevents infinite loop | Test 5 |
| Missing backlog.md | Return False from backfill | Test 6 |

---

## Implementation Steps

### Step 1: Write Failing Tests (RED)
- [ ] Add CascadeResult import and cascade tests to test_work_engine.py
- [ ] Add spawn_tree tests to test_work_engine.py
- [ ] Add backfill tests to test_work_engine.py
- [ ] Add CLI integration tests to test_modules_cli.py
- [ ] Run pytest - verify all new tests fail

### Step 2: CascadeResult + cascade() Method
- [ ] Add CascadeResult dataclass to work_engine.py
- [ ] Add TRIGGER_STATUSES constant
- [ ] Port _get_unblocked_items() helper
- [ ] Port _get_related_items() helper
- [ ] Port _get_milestone_delta() helper
- [ ] Port _get_substantive_refs() helper
- [ ] Add cascade() method
- [ ] Tests 1-3 pass (green)

### Step 3: spawn_tree() Method
- [ ] Port find_children() logic as _find_children()
- [ ] Add spawn_tree() method with recursion
- [ ] Add static format_tree() helper
- [ ] Tests 4-5 pass (green)

### Step 4: backfill() Methods
- [ ] Port parse_backlog_entry() as _parse_backlog_entry()
- [ ] Port update_work_file() as _update_work_file_content()
- [ ] Add backfill() method
- [ ] Add backfill_all() method
- [ ] Tests 6-7 pass (green)

### Step 5: CLI Commands
- [ ] Add cascade, spawn-tree, backfill, backfill-all commands to cli.py
- [ ] Tests 8-10 pass (green)

### Step 6: Justfile Updates
- [ ] Update cascade recipe to use cli.py
- [ ] Update spawns recipe to use cli.py
- [ ] Update backfill/backfill-all/backfill-force recipes

### Step 7: Integration Verification
- [ ] All tests pass
- [ ] Run full test suite (no regressions)
- [ ] Run `just cascade E2-250 complete` - verify uses cli.py
- [ ] Run `just spawns INV-052` - verify uses cli.py

### Step 8: Mark Legacy Code Deprecated
- [ ] Add deprecation header to .claude/lib/cascade.py
- [ ] Add deprecation header to .claude/lib/spawn.py
- [ ] Add deprecation header to .claude/lib/backfill.py

### Step 9: README Sync (MUST)
- [ ] **MUST:** Update .claude/haios/modules/README.md with new methods
- [ ] **MUST:** Verify README content matches actual file state

### Step 10: Consumer Verification
- [ ] **MUST:** Grep for old import patterns: `from cascade import`, `from spawn import`, `from backfill import`
- [ ] **MUST:** Verify justfile recipes are the only remaining consumers (and they now use cli.py)
- [ ] **MUST:** Verify no stale references remain in docs/commands/skills

---

## Verification

- [ ] Tests pass: `pytest tests/test_work_engine.py tests/test_modules_cli.py -v`
- [ ] **MUST:** All READMEs current
- [ ] Runtime verification: `just cascade`, `just spawns`, `just backfill` all work

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| cascade logic complexity | Medium | Port method-by-method, test each |
| backfill depends on backlog.md | Low | backlog.md still exists |
| spawn_tree recursion depth | Low | Keep max_depth=5 limit |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 163 | 2026-01-03 | - | In Progress | Plan created, starting implementation |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/work_engine.py` | cascade(), spawn_tree(), backfill() methods exist | [ ] | |
| `.claude/haios/modules/cli.py` | cascade, spawn-tree, backfill commands | [ ] | |
| `tests/test_work_engine.py` | 7 new tests for cascade/spawn/backfill | [ ] | |
| `tests/test_modules_cli.py` | 3 new CLI tests | [ ] | |
| `justfile` | Recipes use cli.py instead of .claude/lib | [ ] | |
| `.claude/haios/modules/README.md` | Documents new methods | [ ] | |
| `Grep: from cascade import\|from spawn import\|from backfill import` | Only deprecated files | [ ] | |

**Verification Commands:**
```bash
# Run tests
pytest tests/test_work_engine.py tests/test_modules_cli.py -v

# Runtime verification
just cascade E2-250 complete
just spawns INV-052
just backfill E2-021
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [ ] | |
| Test output pasted above? | [ ] | |
| Any deviations from plan? | [ ] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass (10 new tests)
- [ ] **Runtime consumer exists** (justfile recipes use cli.py)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated
- [ ] **MUST:** Consumer verification complete
- [ ] Ground Truth Verification completed above

---

## References

- `docs/work/archive/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md` - Module design
- `docs/work/archive/E2-250/` - Prior WorkEngine integration pattern
- `.claude/lib/cascade.py` - Source to port (596 lines)
- `.claude/lib/spawn.py` - Source to port (188 lines)
- `.claude/lib/backfill.py` - Source to port (271 lines)

---
