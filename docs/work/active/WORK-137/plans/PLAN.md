---
template: implementation_plan
status: complete
date: 2026-02-12
backlog_id: WORK-137
title: "Implement Spawn Ceremony (CH-017)"
author: Hephaestus
lifecycle_phase: plan
session: 357
version: "1.5"
generated: 2026-02-12
last_updated: 2026-02-12T21:33:36
---
# Implementation Plan: Implement Spawn Ceremony (CH-017)

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

A working spawn-work ceremony that creates new work items with bidirectional parent-child lineage, governed by ceremony contracts, with events logged for audit. This is the last chapter (CH-017) in the ceremonies arc, completing E2.5.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | SKILL.md, work_item.md template, work_engine.py |
| New files to create | 1 | tests/test_spawn_ceremony.py |
| New lib module | 1 | .claude/haios/lib/spawn_ceremonies.py |
| Tests to write | ~8 | Contract validation, lineage, event logging, edge cases |
| Dependencies | 4 | queue_ceremonies.py (pattern), ceremony_contracts.py, governance_events.py, spawn_tree.py |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Med | WorkEngine, PortalManager, governance events, ceremony contracts |
| Risk of regression | Low | New code, existing tests for WorkEngine/PortalManager untouched |
| External dependencies | Low | All internal modules |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 20 min | High |
| spawn_ceremonies.py | 20 min | High |
| Template + WorkEngine | 15 min | High |
| SKILL.md de-stub | 10 min | High |
| **Total** | ~65 min | High |

---

## Current State vs Desired State

### Current State

**spawn-work-ceremony SKILL.md** is a stub (`stub: true`). No runtime logic.

**Work item template** has `spawned_by: {{SPAWNED_BY}}` but no `spawned_from` (parent work item) or `spawned_children` fields.

**PortalManager.link_spawned_items()** can set `spawned_by` in frontmatter and `spawned_from` in REFS.md portal, but:
- Only called manually, not via ceremony
- No event logging
- No contract validation
- Sets `spawned_by` on the child but does NOT update parent with children list

**SpawnTree._find_children()** scans all work items for `spawned_by == parent_id` — works but is O(n) scan, no cached `spawned_children` field.

**Behavior:** Work creation can be linked via PortalManager but has no ceremony boundary, no event logging, no governed contract.

**Result:** Spawn relationships are ad-hoc, ungoverned, and not auditable.

### Desired State

**spawn_ceremonies.py** (new lib module) provides `execute_spawn()`:
```python
def execute_spawn(
    work_engine, parent_work_id, title, work_type="implementation",
    traces_to=None, rationale=None, agent=None,
) -> dict:
    # 1. Validate parent exists
    # 2. Get next work ID
    # 3. Scaffold child work item (with spawned_by=parent_work_id)
    # 4. Update parent frontmatter with spawned_children
    # 5. Log SpawnWork event
    # Returns: {success, new_work_id, parent_work_id} or {success, error}
```

**Work item template** gains `spawned_children: []` field for denormalized parent->child tracking.

**WorkEngine** gains `get_work_lineage(id)` method returning `{parent, children}`.

**Behavior:** Spawn ceremony creates child work items inside ceremony boundary with contract validation and event logging.

**Result:** Spawn relationships are governed, auditable, and bidirectional.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Spawn creates child with spawned_by linking
```python
def test_spawn_creates_child_with_lineage(tmp_path):
    # Setup: parent work item exists
    # Action: execute_spawn(engine, "WORK-001", "Child task")
    # Assert: child WORK.md has spawned_by: WORK-001
    assert child_fm["spawned_by"] == "WORK-001"
```

### Test 2: Spawn updates parent spawned_children
```python
def test_spawn_updates_parent_children(tmp_path):
    # Setup: parent work item exists
    # Action: execute_spawn(engine, "WORK-001", "Child task")
    # Assert: parent WORK.md has new_work_id in spawned_children
    assert new_work_id in parent_fm["spawned_children"]
```

### Test 3: Spawn logs SpawnWork event
```python
def test_spawn_logs_event(tmp_path):
    # Action: execute_spawn(engine, "WORK-001", "Child task")
    # Assert: governance-events.jsonl has SpawnWork event
    assert event["type"] == "SpawnWork"
    assert event["parent_work_id"] == "WORK-001"
    assert event["new_work_id"] == new_work_id
```

### Test 4: Spawn validates parent exists
```python
def test_spawn_fails_for_nonexistent_parent(tmp_path):
    # Action: execute_spawn(engine, "WORK-999", "Child task")
    # Assert: returns error, no child created
    assert result["success"] is False
    assert "not found" in result["error"]
```

### Test 5: Spawn contract validation
```python
def test_spawn_contract_validates_inputs():
    # Action: validate_ceremony_input(contract, {missing required fields})
    # Assert: validation fails with specific errors
    assert not result.valid
```

### Test 6: get_work_lineage returns parent and children
```python
def test_get_work_lineage(tmp_path):
    # Setup: parent WORK-001 spawns WORK-002
    # Action: lineage = engine.get_work_lineage("WORK-002")
    # Assert: lineage has parent and empty children
    assert lineage["parent"] == "WORK-001"
    assert lineage["children"] == []
```

### Test 7: Multiple spawns accumulate in parent
```python
def test_multiple_spawns_accumulate(tmp_path):
    # Setup: spawn twice from same parent
    # Assert: parent has both children
    assert len(parent_fm["spawned_children"]) == 2
```

### Test 8: Spawn returns correct output contract
```python
def test_spawn_output_contract(tmp_path):
    # Action: result = execute_spawn(...)
    # Assert: has success, new_work_id, parent_work_id
    assert result["success"] is True
    assert result["new_work_id"].startswith("WORK-")
    assert result["parent_work_id"] == "WORK-001"
```

---

## Detailed Design

<!-- REQUIRED: Document HOW the implementation works, not just WHAT it does.
     Future agents should be able to implement from this section alone.
     This section bridges the gap between tests (WHAT) and steps (HOW).

     MUST INCLUDE (per Session 88 enhancement):
     1. Actual current code that will be changed (copy from source)
     2. Exact diff/change to be made
     3. Function signature details with context
     4. Input/output examples with REAL data from the system

     PATTERN VERIFICATION (E2-255 Learning):
     IF creating a new module that imports from siblings:
       - MUST read at least one sibling module for import/error patterns
       - Verify: try/except conditional imports? sys.path manipulation? error types?
       - Use the SAME patterns as existing siblings (consistency > preference)

     IF modifying existing module:
       - Follow existing patterns in that file

     IF creating module with no siblings (new directory):
       - Document chosen patterns in Key Design Decisions with rationale -->

### Component 1: spawn_ceremonies.py (NEW)

**File:** `.claude/haios/lib/spawn_ceremonies.py`

Follows the pattern established by `queue_ceremonies.py` — ceremony wrapper around engine operations.

```python
"""
Spawn ceremony execution and event logging (CH-017, WORK-137).

Events stored in .claude/haios/governance-events.jsonl (append-only).

Event Types:
- SpawnWork: Logged when spawn ceremony creates a child work item

Usage:
    from spawn_ceremonies import execute_spawn
    result = execute_spawn(engine, "WORK-001", "Follow-on task")
"""
import json
import sys
import yaml
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, List, Optional

# Module-level sys.path for sibling imports (A6 revision)
sys.path.insert(0, str(Path(__file__).parent))

EVENTS_FILE = Path(__file__).parent.parent / "governance-events.jsonl"


def log_spawn_ceremony(
    parent_work_id: str,
    new_work_id: str,
    title: str,
    work_type: str = "implementation",
    rationale: Optional[str] = None,
    agent: Optional[str] = None,
) -> dict:
    """Log spawn ceremony event to governance-events.jsonl."""
    event = {
        "type": "SpawnWork",
        "ceremony": "spawn-work",
        "parent_work_id": parent_work_id,
        "new_work_id": new_work_id,
        "title": title,
        "work_type": work_type,
        "timestamp": datetime.now().isoformat(),
    }
    if rationale:
        event["rationale"] = rationale
    if agent:
        event["agent"] = agent
    _append_event(event)
    return event


def execute_spawn(
    work_engine: Any,
    parent_work_id: str,
    title: str,
    work_type: str = "implementation",
    traces_to: Optional[List[str]] = None,
    rationale: Optional[str] = None,
    agent: Optional[str] = None,
) -> dict:
    """Execute spawn ceremony: create child work item linked to parent.

    Steps:
    1. Validate parent exists
    2. Get next work ID
    3. Scaffold child via scaffold_template (with spawned_by=parent)
    4. Create REFS.md portal for child (A8 revision)
    5. Update parent frontmatter with spawned_children
    6. Log SpawnWork event with side effects on ceremony context (A5 revision)

    Returns:
        {success: True, new_work_id, parent_work_id} or
        {success: False, error, parent_work_id}
    """
    from scaffold import get_next_work_id, scaffold_template

    # 1. Validate parent
    parent = work_engine.get_work(parent_work_id)
    if parent is None:
        return {"success": False, "error": f"Parent {parent_work_id} not found",
                "parent_work_id": parent_work_id}

    # 2. Get next ID
    new_work_id = get_next_work_id()

    try:
        with _ceremony_context_safe("spawn-work") as ctx:
            # 3. Scaffold child
            output_path = f"docs/work/active/{new_work_id}/WORK.md"
            scaffold_template(
                "work_item",
                output_path=output_path,
                backlog_id=new_work_id,
                title=title,
                variables={"SPAWNED_BY": parent_work_id, "TYPE": work_type},
            )
            if ctx:
                ctx.log_side_effect("scaffold_child", {
                    "new_work_id": new_work_id, "parent": parent_work_id,
                })

            # 4. Create REFS.md portal for child (A8: match WorkEngine.create_work structure)
            refs_dir = Path("docs/work/active") / new_work_id / "references"
            refs_dir.mkdir(parents=True, exist_ok=True)
            work_engine._create_portal(new_work_id, refs_dir / "REFS.md")

            # 5. Update parent spawned_children
            _update_parent_children(work_engine, parent_work_id, new_work_id)
            if ctx:
                ctx.log_side_effect("update_parent_children", {
                    "parent": parent_work_id, "child": new_work_id,
                })

            # 6. Log event
            log_spawn_ceremony(
                parent_work_id=parent_work_id,
                new_work_id=new_work_id,
                title=title,
                work_type=work_type,
                rationale=rationale,
                agent=agent,
            )
            if ctx:
                ctx.log_side_effect("spawn_event_logged", {
                    "event_type": "SpawnWork",
                })

        return {
            "success": True,
            "new_work_id": new_work_id,
            "parent_work_id": parent_work_id,
        }
    except Exception as e:
        return {"success": False, "error": str(e), "parent_work_id": parent_work_id}


def _update_parent_children(work_engine: Any, parent_id: str, child_id: str) -> None:
    """Append child_id to parent's spawned_children field in frontmatter.

    Note: Writes directly to WORK.md (bypasses WorkEngine._write_work_file).
    This follows the precedent set by PortalManager.link_spawned_items() and
    WorkEngine._set_closed_date() for field-specific updates. The spawned_children
    field survives subsequent _write_work_file calls because that method reads
    existing frontmatter and only overwrites specific keys.
    """
    parent = work_engine.get_work(parent_id)
    path = parent.path
    content = path.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid frontmatter in {parent_id}")
    fm = yaml.safe_load(parts[1]) or {}
    children = fm.get("spawned_children", []) or []
    if child_id not in children:
        children.append(child_id)
    fm["spawned_children"] = children
    fm["last_updated"] = datetime.now().isoformat()
    new_fm = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True)
    path.write_text(f"---\n{new_fm}---{parts[2]}", encoding="utf-8")


@contextmanager
def _ceremony_context_safe(name: str):
    """Ceremony context wrapper matching queue_ceremonies.py pattern (A5 revision)."""
    try:
        from governance_layer import ceremony_context, in_ceremony_context
        if in_ceremony_context():
            yield None  # Already inside ceremony — no-op (avoid nesting)
        else:
            with ceremony_context(name) as ctx:
                yield ctx
    except ImportError:
        yield None


def _append_event(event: dict) -> None:
    """Append event to JSONL file."""
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")
```

### Component 2: Template Changes

**File:** `.claude/templates/work_item.md`

Add `spawned_children: []` after `spawned_by`:

```diff
 spawned_by: {{SPAWNED_BY}}
+spawned_children: []
 chapter: null
```

### Component 3: WorkEngine.get_work_lineage()

**File:** `.claude/haios/modules/work_engine.py`

New method added to WorkEngine class:

```python
def get_work_lineage(self, id: str) -> Dict[str, Any]:
    """Get parent and children of work item.

    Args:
        id: Work item ID

    Returns:
        {parent: str|None, children: list[str]}
    """
    work = self.get_work(id)
    if work is None:
        return {"parent": None, "children": []}

    # Read frontmatter for spawned_by and spawned_children
    path = work.path
    content = path.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {"parent": None, "children": []}
    fm = yaml.safe_load(parts[1]) or {}

    parent = fm.get("spawned_by")
    if parent in (None, "null", ""):
        parent = None
    children = fm.get("spawned_children", []) or []

    return {"parent": parent, "children": children}
```

### Component 4: SKILL.md De-stub

**File:** `.claude/skills/spawn-work-ceremony/SKILL.md`

Remove `stub: true` from frontmatter. Update ceremony steps to reference `spawn_ceremonies.execute_spawn()`.

### Call Chain Context

```
spawn-work-ceremony (skill, invoked by agent)
    |
    +-> execute_spawn()               # spawn_ceremonies.py (NEW)
    |       |
    |       +-> work_engine.get_work()     # Validate parent
    |       +-> get_next_work_id()         # scaffold.py
    |       +-> scaffold_template()        # scaffold.py — creates child WORK.md
    |       +-> _update_parent_children()  # Updates parent frontmatter
    |       +-> log_spawn_ceremony()       # Appends to governance-events.jsonl
    |
    +-> Returns: {success, new_work_id, parent_work_id}
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| New lib module vs extending queue_ceremonies | New `spawn_ceremonies.py` | Spawn is a different ceremony category. Follows single-responsibility. queue_ceremonies handles queue transitions; spawn handles work creation lineage. |
| `spawned_children` in frontmatter (denormalized) | Yes, add field | SpawnTree._find_children() does O(n) scan. Denormalized field enables O(1) lookup for direct children. SpawnTree remains for deep tree traversal. |
| Use scaffold_template for child creation | Yes | Reuses existing template machinery. Child gets proper frontmatter, subdirs, etc. Passes `SPAWNED_BY` variable. |
| `spawned_by` field semantics change | No change — keep dual use | Currently `spawned_by` can reference chapters or work items. CH-017 spec adds `spawned_from` as alias but existing `spawned_by` already serves this purpose. Keep `spawned_by` as the canonical field, don't add `spawned_from` to avoid redundancy. SpawnTree already uses `spawned_by`. |
| Ceremony context wrapping | Use `_ceremony_context_safe` pattern | Consistent with queue_ceremonies.py. Fail-permissive for import errors, avoids nesting errors. |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Parent doesn't exist | Return `{success: False, error}` | Test 4 |
| Parent already has spawned_children | Append to existing list | Test 7 |
| Parent has no spawned_children field | Initialize as `[child_id]` | Test 2 (implicit) |
| Duplicate spawn (same child twice) | Skip if already in list | _update_parent_children checks |
| Scaffold fails (disk error) | Exception caught, return error | Exception handler in execute_spawn |

### Open Questions

**Q: Should `spawned_from` be added as a separate field per CH-017 spec?**

No. The existing `spawned_by` field already serves this purpose. Adding `spawned_from` as a separate field creates redundancy. SpawnTree, PortalManager, and all consumers use `spawned_by`. The CH-017 spec's `spawned_from` concept maps to the existing `spawned_by` field when it contains a WORK-XXX ID instead of a chapter reference.

---

## Open Decisions (MUST resolve before implementation)

<!-- Decisions from work item's operator_decisions field.
     If ANY row has [BLOCKED] in Chosen column, plan-validation-cycle will BLOCK.

     POPULATE FROM: Work item frontmatter `operator_decisions` field
     - question -> Decision column
     - options -> Options column
     - chosen -> Chosen column (null = [BLOCKED])
     - rationale -> Rationale column (filled when resolved) -->

No open decisions. All design choices resolved in Detailed Design section above.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_spawn_ceremony.py` with all 8 tests
- [ ] Verify all tests fail (red) — module doesn't exist yet

### Step 2: Add spawned_children to template
- [ ] Add `spawned_children: []` to `.claude/templates/work_item.md` after `spawned_by`
- [ ] No tests turn green yet (template change only)

### Step 3: Create spawn_ceremonies.py
- [ ] Create `.claude/haios/lib/spawn_ceremonies.py` with `execute_spawn()`, `log_spawn_ceremony()`, `_update_parent_children()`
- [ ] Tests 1, 2, 3, 4, 7, 8 pass (green)

### Step 4: Add WorkEngine.get_work_lineage()
- [ ] Add `get_work_lineage()` method to `work_engine.py`
- [ ] Test 6 passes (green)

### Step 5: Contract validation test
- [ ] Test 5 passes (green) — uses existing ceremony_contracts.py with SKILL.md frontmatter

### Step 6: De-stub SKILL.md
- [ ] Remove `stub: true` from spawn-work-ceremony SKILL.md
- [ ] Update ceremony steps to reference `spawn_ceremonies.execute_spawn()`

### Step 7: Integration Verification
- [ ] All 8 tests pass
- [ ] Run full test suite (no regressions)

### Step 8: Consumer Verification
- [ ] Grep for `stub: true` in spawn-work-ceremony — should be zero
- [ ] Verify spawn-work-ceremony appears in `just update-status-slim` output

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Template change breaks existing work items | Low | New field `spawned_children: []` is additive; existing items without it handled via `.get("spawned_children", []) or []` |
| scaffold_template variables not substituted | Medium | Verify `SPAWNED_BY` variable works in scaffold_template; existing pattern used by all work items |
| Ceremony context nesting | Low | Use `_ceremony_context_safe` pattern from queue_ceremonies.py (battle-tested) |

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

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-137/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| De-stub spawn-work-ceremony SKILL.md | [ ] | `stub: true` removed, ceremony steps reference execute_spawn() |
| Verify spawned_by handles parent work item IDs | [ ] | spawned_by already serves spawned_from role; scaffold passes SPAWNED_BY=parent_work_id |
| Add spawned_children field to work_item template and WorkEngine parsing | [ ] | Field in template, _update_parent_children writes it, get_work_lineage reads it |
| Implement parent update | [ ] | _update_parent_children() appends child ID, updates last_updated |
| Log SpawnWork event | [ ] | log_spawn_ceremony() writes to governance-events.jsonl |
| Create REFS.md portal for child | [ ] | work_engine._create_portal() called after scaffold (A8) |
| Add get_work_lineage() to WorkEngine | [ ] | Method returns {parent, children} |
| Unit tests for spawn ceremony | [ ] | 8 tests in test_spawn_ceremony.py |
| Integration test: spawn from parent, verify lineage | [ ] | Test 2 + Test 6 cover bidirectional lineage |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/spawn_ceremonies.py` | execute_spawn(), log_spawn_ceremony(), _update_parent_children() | [ ] | |
| `.claude/haios/modules/work_engine.py` | get_work_lineage() method added | [ ] | |
| `.claude/templates/work_item.md` | spawned_children: [] field present | [ ] | |
| `.claude/skills/spawn-work-ceremony/SKILL.md` | stub: true removed, ceremony steps updated | [ ] | |
| `tests/test_spawn_ceremony.py` | 8 tests, all passing | [ ] | |
| `Grep: stub.*true` in spawn-work-ceremony | Zero matches | [ ] | |
| Child `references/REFS.md` | Portal created by execute_spawn (A8) | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest [test_file] -v
# Expected: X tests passed
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
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.
> **E2-290 Learning (Session 192):** "Tests pass" ≠ "Deliverables complete". Agent declared victory after tests passed but skipped 2 of 7 deliverables.

---

## References

- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-017-SpawnCeremony.md (chapter spec)
- @.claude/skills/spawn-work-ceremony/SKILL.md (stub to de-stub)
- @.claude/haios/lib/queue_ceremonies.py (ceremony pattern to follow)
- @.claude/haios/modules/spawn_tree.py (existing lineage traversal)
- @.claude/haios/modules/portal_manager.py (link_spawned_items pattern)
- @.claude/haios/lib/ceremony_contracts.py (contract validation)

---
