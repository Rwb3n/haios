---
template: implementation_plan
status: complete
date: 2026-02-20
backlog_id: WORK-174
title: "WorkState Dataclass Expansion"
author: Hephaestus
lifecycle_phase: plan
session: 411
version: "1.5"
generated: 2026-02-20
last_updated: 2026-02-20T22:38:37
---
# Implementation Plan: WorkState Dataclass Expansion

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

WorkState dataclass parses all 5 missing governance-relevant frontmatter fields (effort, chapter, arc, traces_to, spawned_children) enabling downstream consumers like tier_detector.py to use typed WorkState instead of raw YAML parsing.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `work_engine.py`, `tier_detector.py` |
| Lines of code affected | ~25 | 5 fields in dataclass + 5 lines in parser + ~10 lines in tier_detector |
| New files to create | 0 | Tests added to existing test files |
| Tests to write | 8 | 5 field parsing + 1 backward compat + 1 default values + 1 tier_detector WorkState |
| Dependencies | 3 | coldstart_orchestrator.py, queue_ceremonies.py, spawn_ceremonies.py (import WorkEngine/WorkState) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Adding fields to dataclass, not changing interfaces |
| Risk of regression | Low | Existing tests cover current fields; new fields use same parsing pattern |
| External dependencies | Low | No APIs, services, or config changes |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 15 min | High |
| WorkState + parser | 10 min | High |
| tier_detector update | 10 min | High |
| CHECK phase | 10 min | High |
| **Total** | 45 min | High |

---

## Current State vs Desired State

### Current State

```python
# work_engine.py:90-116 — WorkState dataclass (missing 5 fields)
@dataclass
class WorkState:
    id: str
    title: str
    status: str
    current_node: str
    type: str = "feature"
    queue_position: str = "backlog"
    cycle_phase: str = "backlog"
    blocked_by: List[str] = field(default_factory=list)
    node_history: List[Dict[str, Any]] = field(default_factory=list)
    queue_history: List[Dict[str, Any]] = field(default_factory=list)
    memory_refs: List[int] = field(default_factory=list)
    requirement_refs: List[str] = field(default_factory=list)
    source_files: List[str] = field(default_factory=list)
    acceptance_criteria: List[str] = field(default_factory=list)
    artifacts: List[str] = field(default_factory=list)
    extensions: Dict[str, Any] = field(default_factory=dict)
    path: Optional[Path] = None
    priority: str = "medium"
```

```python
# tier_detector.py:139-143 — raw YAML parsing workaround
work_type = fm.get("type")
effort = fm.get("effort")
source_files = fm.get("source_files")
traces_to = fm.get("traces_to") or []
```

**Behavior:** `w.chapter` raises `AttributeError`. Tier detector must parse YAML itself.

**Result:** Downstream consumers cannot use WorkState for governance-relevant fields.

### Desired State

```python
# work_engine.py:90-121 — WorkState dataclass (5 new fields added)
@dataclass
class WorkState:
    # ... existing fields unchanged ...
    priority: str = "medium"
    # WORK-174: Governance-relevant fields (read-only, not round-tripped by _write_work_file)
    effort: str = ""
    chapter: str = ""
    arc: str = ""
    traces_to: List[str] = field(default_factory=list)
    spawned_children: List[str] = field(default_factory=list)
```

```python
# tier_detector.py:104+ — detect_tier can accept optional WorkState
def detect_tier(work_id: str, project_root: Optional[Path] = None,
                work_state: Optional['WorkState'] = None) -> str:
    # If work_state provided, use it instead of parsing YAML
```

**Behavior:** `w.chapter` returns `"CH-059"`. Tier detector can use WorkState directly.

**Result:** All governance-relevant fields available through typed WorkState interface.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Parse effort field
```python
def test_workstate_parses_effort(tmp_path, engine, setup_work_item):
    setup_work_item("WORK-TEST", SAMPLE_WORK_MD_WITH_NEW_FIELDS)
    result = engine.get_work("WORK-TEST")
    assert result.effort == "small"
```

### Test 2: Parse chapter field
```python
def test_workstate_parses_chapter(tmp_path, engine, setup_work_item):
    setup_work_item("WORK-TEST", SAMPLE_WORK_MD_WITH_NEW_FIELDS)
    result = engine.get_work("WORK-TEST")
    assert result.chapter == "CH-059"
```

### Test 3: Parse arc field
```python
def test_workstate_parses_arc(tmp_path, engine, setup_work_item):
    setup_work_item("WORK-TEST", SAMPLE_WORK_MD_WITH_NEW_FIELDS)
    result = engine.get_work("WORK-TEST")
    assert result.arc == "call"
```

### Test 4: Parse traces_to field
```python
def test_workstate_parses_traces_to(tmp_path, engine, setup_work_item):
    setup_work_item("WORK-TEST", SAMPLE_WORK_MD_WITH_NEW_FIELDS)
    result = engine.get_work("WORK-TEST")
    assert result.traces_to == ["REQ-CEREMONY-005"]
```

### Test 5: Parse spawned_children field
```python
def test_workstate_parses_spawned_children(tmp_path, engine, setup_work_item):
    setup_work_item("WORK-TEST", SAMPLE_WORK_MD_WITH_NEW_FIELDS)
    result = engine.get_work("WORK-TEST")
    assert result.spawned_children == ["WORK-168", "WORK-169"]
```

### Test 6: Default values for missing fields (backward compat)
```python
def test_workstate_defaults_for_missing_new_fields(tmp_path, engine, setup_work_item):
    # Uses legacy SAMPLE_WORK_MD without new fields
    setup_work_item("E2-TEST")
    result = engine.get_work("E2-TEST")
    assert result.effort == ""
    assert result.chapter == ""
    assert result.arc == ""
    assert result.traces_to == []
    assert result.spawned_children == []
```

### Test 7: Existing WorkState fields unchanged
```python
def test_existing_workstate_fields_still_work(tmp_path, engine, setup_work_item):
    setup_work_item("E2-TEST")
    result = engine.get_work("E2-TEST")
    assert result.id == "E2-TEST"
    assert result.title == "Test Work Item"
    assert result.status == "active"
    assert result.source_files == []  # Already parsed (pre-existing)
```

### Test 8: tier_detector uses WorkState when provided
```python
def test_detect_tier_with_workstate(tmp_path):
    # Create WORK.md in tmp_path so detect_tier doesn't short-circuit on missing file
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-TEST"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text("---\nid: WORK-TEST\n---\n# WORK-TEST\n")
    # Do NOT create plans/PLAN.md (trivial requires no plan)

    work_state = WorkState(
        id="WORK-TEST", title="Test", status="active",
        current_node="backlog", effort="small",
        source_files=["a.py"], traces_to=[]
    )
    result = detect_tier("WORK-TEST", project_root=tmp_path, work_state=work_state)
    assert result == "trivial"
```

### Test Fixture: SAMPLE_WORK_MD_WITH_NEW_FIELDS
```python
SAMPLE_WORK_MD_WITH_NEW_FIELDS = """---
template: work_item
id: WORK-TEST
title: Test Work Item
status: active
current_node: backlog
effort: small
chapter: CH-059
arc: call
traces_to:
  - REQ-CEREMONY-005
spawned_children:
  - WORK-168
  - WORK-169
blocked_by: []
node_history:
- node: backlog
  entered: '2026-01-03T10:00:00'
  exited: null
memory_refs: []
---
# WORK-TEST: Test Work Item
"""
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

### Change 1: WorkState Dataclass — 5 New Fields

**File:** `.claude/haios/modules/work_engine.py`
**Location:** Lines 114-116, after `priority` field

**Diff:**
```diff
     priority: str = "medium"  # E2-290: For queue ordering
+    # WORK-174: Governance-relevant fields (read-only, not round-tripped by _write_work_file)
+    effort: str = ""
+    chapter: str = ""
+    arc: str = ""
+    traces_to: List[str] = field(default_factory=list)
+    spawned_children: List[str] = field(default_factory=list)
```

### Change 2: _parse_work_file — Parse New Fields

**File:** `.claude/haios/modules/work_engine.py`
**Location:** Lines 993-995, after `priority` parsing

**Diff:**
```diff
             priority=fm.get("priority", "medium"),  # E2-290: Queue ordering
+            # WORK-174: Governance-relevant fields
+            effort=fm.get("effort", ""),
+            chapter=fm.get("chapter", ""),
+            arc=fm.get("arc", ""),
+            traces_to=fm.get("traces_to", []) or [],
+            spawned_children=fm.get("spawned_children", []) or [],
         )
```

Note: `or []` pattern handles YAML `null` → Python `None` for list fields (same as `blocked_by` at line 983).

### Change 3: tier_detector.py — Accept Optional WorkState

**File:** `.claude/haios/lib/tier_detector.py`
**Location:** Lines 104-143, `detect_tier()` function

**Current signature:**
```python
def detect_tier(work_id: str, project_root: Optional[Path] = None) -> str:
```

**New signature:**
```python
def detect_tier(work_id: str, project_root: Optional[Path] = None,
                work_state: Optional[object] = None) -> str:
```

**Logic change:** When `work_state` is provided, extract fields from it instead of raw YAML:
```python
        if work_state is not None:
            work_type = work_state.type
            effort = work_state.effort or None  # "" -> None for existing predicate compat
            source_files = work_state.source_files or None
            traces_to = work_state.traces_to or []
        else:
            # Existing raw YAML path unchanged
            fm = _parse_frontmatter(work_file)
            ...
            work_type = fm.get("type")
            effort = fm.get("effort")
            source_files = fm.get("source_files")
            traces_to = fm.get("traces_to") or []
```

Note: `Optional[object]` used instead of `Optional[WorkState]` to avoid circular import (lib/ -> modules/). Type annotation is structural, not nominal.

### Change 4: _write_work_file — NO CHANGES

**File:** `.claude/haios/modules/work_engine.py`
**Location:** Lines 997-1029

**Explicitly no changes.** New fields are read-only: parsed from WORK.md but never written back. These are creation-time metadata (effort, chapter, arc set at work item creation and never mutated by WorkEngine). The `_write_work_file` hardcoded field list (lines 1016-1023) is intentionally NOT extended.

### Call Chain Context

```
WorkEngine.get_work(work_id)
    |
    +-> _parse_work_file(path)   # <-- Change 2: parse 5 new fields
    |       Returns: WorkState   # <-- Change 1: 5 new fields on dataclass
    |
    +-> Consumers:
        +-> get_ready() — filters by status/blocked_by (unchanged)
        +-> tier_detector.detect_tier() — Change 3: can use WorkState
        +-> coldstart_orchestrator — reads .chapter, .arc (currently fails)
        +-> critique entry gate — reads .traces_to (currently raw YAML)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Read-only fields | New fields NOT in _write_work_file | effort/chapter/arc are creation-time metadata, never mutated by WorkEngine. Extending _write_work_file risks silent overwrites. |
| Default "" for string fields | Empty string, not None | Consistent with `type` field pattern (line 102). Enables truthiness check: `if w.effort:` |
| Default [] for list fields | Empty list with `or []` | Same pattern as `blocked_by` (line 983). Handles YAML null -> None. |
| `Optional[object]` for WorkState param | Not `Optional[WorkState]` | Avoids circular import (lib/ cannot import modules/). Structural typing is sufficient. |
| Keep raw YAML path in tier_detector | Dual path (WorkState or raw YAML) | Backward compatible. Hook callers may not have WorkEngine available. |
| `spawned_by` excluded | Only 5 fields, not 6 | `spawned_by` is a single string, used only by `get_work_lineage()` which reads raw YAML. Different access pattern than governance fields. |

### Input/Output Examples

**Before (WORK-174's own frontmatter):**
```python
w = engine.get_work("WORK-174")
w.effort    # AttributeError: 'WorkState' object has no attribute 'effort'
w.chapter   # AttributeError: 'WorkState' object has no attribute 'chapter'
```

**After:**
```python
w = engine.get_work("WORK-174")
w.effort          # "small"
w.chapter         # "CH-059"
w.arc             # "call"
w.traces_to       # ["REQ-CEREMONY-005"]
w.spawned_children  # []
```

**Tier detector before (raw YAML):**
```python
detect_tier("WORK-174")  # Reads WORK.md, parses YAML internally
```

**Tier detector after (WorkState):**
```python
w = engine.get_work("WORK-174")
detect_tier("WORK-174", work_state=w)  # Uses WorkState directly, no file re-read
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Legacy WORK.md without new fields | Default values: "" for strings, [] for lists | Test 6 |
| YAML null for traces_to | `or []` pattern converts None to [] | Test 4 (implicit) |
| Empty spawned_children `[]` | Parsed as empty list (correct) | Test 5 (modify fixture) |
| tier_detector with work_state=None | Falls back to existing raw YAML path | Existing tests unchanged |
| effort="" in WorkState (from legacy) | tier_detector treats as None for predicate | Handled by `or None` conversion |

### Open Questions

**Q: Should we type-annotate work_state as `Optional['WorkState']` using string forward reference?**

No. tier_detector lives in `lib/` and cannot import from `modules/` without adding sys.path manipulation. `Optional[object]` is cleaner and sufficient — all attribute access is duck-typed anyway.

---

## Open Decisions (MUST resolve before implementation)

<!-- Decisions from work item's operator_decisions field.
     If ANY row has [BLOCKED] in Chosen column, plan-validation-cycle will BLOCK.

     POPULATE FROM: Work item frontmatter `operator_decisions` field
     - question -> Decision column
     - options -> Options column
     - chosen -> Chosen column (null = [BLOCKED])
     - rationale -> Rationale column (filled when resolved) -->

No operator decisions required. All design choices are computable from source code analysis (see Key Design Decisions table above).

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests (RED)
- [ ] Add SAMPLE_WORK_MD_WITH_NEW_FIELDS fixture to test_work_engine.py
- [ ] Add tests 1-7 (5 field parsing + defaults + backward compat) to test_work_engine.py
- [ ] Add test 8 (detect_tier with WorkState) to test_tier_detector.py
- [ ] Verify all 8 new tests fail (red)

### Step 2: WorkState Dataclass + Parser (GREEN for tests 1-7)
- [ ] Add 5 new fields to WorkState dataclass (after `priority`)
- [ ] Add 5 new field extractions to _parse_work_file() (after `priority`)
- [ ] Tests 1-7 pass (green)

### Step 3: tier_detector WorkState Support (GREEN for test 8)
- [ ] Add `work_state` optional parameter to `detect_tier()` signature
- [ ] Add WorkState extraction branch before raw YAML branch
- [ ] Test 8 passes (green)

### Step 4: Integration Verification
- [ ] All 8 new tests pass
- [ ] Run full test suite: `pytest tests/ -v` — no regressions
- [ ] Specifically verify: `pytest tests/test_work_engine.py tests/test_tier_detector.py -v`

### Step 5: Consumer Verification
- [ ] Grep for `fm.get("effort")` / `fm.get("chapter")` patterns outside work_engine.py to find other raw YAML consumers
- [ ] Verify no other files need updating (scope boundary: only tier_detector in this work item)

**SKIPPED: README Sync** — No new files created, no directory structure changes. Existing READMEs unaffected.

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Dataclass field ordering breaks existing unpacking | Medium | New fields added AFTER all existing fields with defaults — no positional args affected |
| _write_work_file accidentally drops new fields on round-trip | Medium | Explicitly NOT extending _write_work_file. New fields are read-only. Documented in deliverables. |
| tier_detector circular import (lib/ -> modules/) | Low | Using `Optional[object]` instead of `Optional[WorkState]`. No import needed. |
| Legacy WORK.md files without new fields cause errors | Medium | All defaults are safe: "" for strings, [] for lists. Same `fm.get(key, default)` pattern as existing fields. |
| effort="" treated differently than effort=None in tier_detector | Low | Explicit `or None` conversion in WorkState path to match existing predicate logic |

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

**MUST** read `docs/work/active/WORK-174/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| WorkState dataclass expanded with 5 new fields | [ ] | Read work_engine.py, verify effort/chapter/arc/traces_to/spawned_children present |
| Parsing logic updated in _parse_work_file() | [ ] | Read work_engine.py, verify fm.get() calls for 5 fields |
| New fields are read-only (not in _write_work_file) | [ ] | Read _write_work_file(), confirm NO new field writes added |
| Tests for each new field | [ ] | pytest output shows 8 new tests passing |
| tier_detector.py updated to use WorkState | [ ] | Read tier_detector.py, verify work_state parameter and extraction logic |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/work_engine.py` | WorkState has 5 new fields, _parse_work_file extracts them | [ ] | |
| `.claude/haios/lib/tier_detector.py` | detect_tier accepts work_state parameter | [ ] | |
| `tests/test_work_engine.py` | 7 new tests for field parsing + defaults | [ ] | |
| `tests/test_tier_detector.py` | 1 new test for WorkState path | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_work_engine.py tests/test_tier_detector.py -v
# Expected: all existing tests + 8 new tests passed
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

- @docs/work/active/WORK-174/WORK.md (work item)
- @.claude/haios/modules/work_engine.py (target: WorkState dataclass + _parse_work_file)
- @.claude/haios/lib/tier_detector.py (consumer: detect_tier)
- @docs/work/active/WORK-167/WORK.md (tier detection, completed)
- Memory: 86606, 86619, 86647, 86668, 86687 (convergent entries)

---
