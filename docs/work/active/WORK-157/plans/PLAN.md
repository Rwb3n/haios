---
template: implementation_plan
status: approved
date: 2026-02-17
backlog_id: WORK-157
title: "Hierarchy Query Engine"
author: Hephaestus
lifecycle_phase: plan
session: 393
version: "1.5"
generated: 2026-02-17
last_updated: 2026-02-17T18:51:06
---
# Implementation Plan: Hierarchy Query Engine

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | DONE | Memory queried: 84811 (flat storage decision), 84212 (no epoch-status command), 84230 (chapters as immutable docs), StatusPropagator reviewed |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

Provide callable engine functions (`get_arcs()`, `get_chapters()`, `get_work()`, `get_hierarchy()`) in a new `HierarchyQueryEngine` module that parse the existing markdown hierarchy (EPOCH.md, ARC.md, WORK.md) into typed dataclass results, eliminating manual path resolution for hierarchy navigation.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 2 | `.claude/haios/lib/hierarchy_engine.py`, `tests/test_hierarchy_engine.py` |
| Files to modify | 1 | `.claude/haios/lib/status_propagator.py` (replace hardcoded scan with engine calls) |
| Lines of code (new) | ~200 | Based on StatusPropagator (273 lines) as reference for similar parsing |
| Tests to write | 10 | 4 functions x 2 cases + 2 edge cases |
| Dependencies | 2 | ConfigLoader (lib/config.py), yaml |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | New module, StatusPropagator is only immediate consumer |
| Risk of regression | Low | New code, no existing functions modified (except StatusPropagator refactor) |
| External dependencies | Low | Only reads markdown files + haios.yaml via ConfigLoader |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests (RED) | 30 min | High |
| Implementation (GREEN) | 45 min | High |
| StatusPropagator integration | 15 min | High |
| Verification | 15 min | High |
| **Total** | ~2 hr | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/lib/status_propagator.py:110-132
# Hierarchy context extracted by reading individual WORK.md files manually
def get_hierarchy_context(self, work_id: str) -> Optional[Dict]:
    work_file = self._base_path / "docs" / "work" / "active" / work_id / "WORK.md"
    # ... hardcoded path, reads single file
    return {"chapter": chapter, "arc": arc}

# .claude/haios/lib/status_propagator.py:134-167
# Chapter completion check scans ALL active work items
def is_chapter_complete(self, chapter_id: str) -> bool:
    active_dir = self._base_path / "docs" / "work" / "active"
    # ... iterates all dirs, parses all WORK.md files
```

**Behavior:** Each caller independently discovers and parses hierarchy files. No reusable functions for "which arcs exist?" or "which chapters are in this arc?"

**Result:** Hierarchy navigation is fragile, duplicated across modules, and non-composable.

### Desired State

```python
# .claude/haios/lib/hierarchy_engine.py (NEW)
engine = HierarchyQueryEngine(base_path=tmp_path)

arcs = engine.get_arcs()
# [ArcInfo(name="engine-functions", theme="Functions over file reads", status="Active", chapters=["CH-044","CH-045"])]

chapters = engine.get_chapters("engine-functions")
# [ChapterInfo(id="CH-044", title="HierarchyQueryEngine", work_items=["WORK-157"], status="Planning")]

work_items = engine.get_work("CH-044")
# [WorkInfo(id="WORK-157", title="Hierarchy Query Engine", status="active", type="feature")]

chain = engine.get_hierarchy("WORK-157")
# HierarchyChain(work_id="WORK-157", chapter="CH-044", arc="engine-functions", epoch="E2.7")
```

**Behavior:** Single module provides all hierarchy queries. Callers import and call functions.

**Result:** No manual path resolution. StatusPropagator TODO(CH-044) resolved.

---

## Tests First (TDD)

### Test 1: get_arcs returns arc metadata from haios.yaml + ARC.md files
```python
def test_get_arcs_returns_arc_list(tmp_path):
    _setup_hierarchy(tmp_path)  # Creates haios.yaml, ARC.md files
    engine = HierarchyQueryEngine(base_path=tmp_path)
    arcs = engine.get_arcs()
    assert len(arcs) == 2  # engine-functions, composability
    assert arcs[0].name == "composability"  # or sorted order
    assert isinstance(arcs[0].chapters, list)
```

### Test 2: get_chapters returns chapter list for given arc
```python
def test_get_chapters_returns_chapter_list(tmp_path):
    _setup_hierarchy(tmp_path)
    engine = HierarchyQueryEngine(base_path=tmp_path)
    chapters = engine.get_chapters("engine-functions")
    assert len(chapters) == 2  # CH-044, CH-045
    assert chapters[0].id == "CH-044"
    assert chapters[0].work_items == ["WORK-157"]
```

### Test 3: get_chapters returns empty list for unknown arc
```python
def test_get_chapters_unknown_arc(tmp_path):
    _setup_hierarchy(tmp_path)
    engine = HierarchyQueryEngine(base_path=tmp_path)
    chapters = engine.get_chapters("nonexistent")
    assert chapters == []
```

### Test 4: get_work returns work items for given chapter
```python
def test_get_work_returns_work_items(tmp_path):
    _setup_hierarchy(tmp_path)
    engine = HierarchyQueryEngine(base_path=tmp_path)
    items = engine.get_work("CH-044")
    assert len(items) == 1
    assert items[0].id == "WORK-157"
    assert items[0].status == "active"
```

### Test 5: get_work returns empty for chapter with no items
```python
def test_get_work_empty_chapter(tmp_path):
    _setup_hierarchy(tmp_path)
    engine = HierarchyQueryEngine(base_path=tmp_path)
    items = engine.get_work("CH-999")
    assert items == []
```

### Test 6: get_hierarchy returns full chain for work item
```python
def test_get_hierarchy_full_chain(tmp_path):
    _setup_hierarchy(tmp_path)
    engine = HierarchyQueryEngine(base_path=tmp_path)
    chain = engine.get_hierarchy("WORK-157")
    assert chain is not None
    assert chain.work_id == "WORK-157"
    assert chain.chapter == "CH-044"
    assert chain.arc == "engine-functions"
    assert chain.epoch == "E2.7"
```

### Test 7: get_hierarchy returns None for unknown work item
```python
def test_get_hierarchy_unknown_work(tmp_path):
    _setup_hierarchy(tmp_path)
    engine = HierarchyQueryEngine(base_path=tmp_path)
    chain = engine.get_hierarchy("WORK-999")
    assert chain is None
```

### Test 8: get_arcs with no arcs_dir returns empty list
```python
def test_get_arcs_no_arcs_dir(tmp_path):
    _setup_minimal_config(tmp_path)  # haios.yaml but no arcs dir
    engine = HierarchyQueryEngine(base_path=tmp_path)
    arcs = engine.get_arcs()
    assert arcs == []
```

### Test 9: get_work filters completed work items
```python
def test_get_work_includes_completed_items(tmp_path):
    _setup_hierarchy(tmp_path)
    engine = HierarchyQueryEngine(base_path=tmp_path)
    items = engine.get_work("CH-045")
    assert len(items) == 1
    assert items[0].id == "WORK-034"
    assert items[0].status == "complete"
```

### Test 10: Integration - StatusPropagator uses HierarchyQueryEngine
```python
def test_status_propagator_uses_hierarchy_engine(tmp_path):
    """Verify StatusPropagator delegates to HierarchyQueryEngine."""
    # This validates the TODO(CH-044) consumer integration
    _setup_hierarchy(tmp_path)
    propagator = StatusPropagator(base_path=tmp_path)
    ctx = propagator.get_hierarchy_context("WORK-034")
    assert ctx is not None
    assert ctx["chapter"] == "CH-045"
```

---

## Detailed Design

### Module Location

**File:** `.claude/haios/lib/hierarchy_engine.py` (NEW)

**Rationale:** lib/ not modules/ because:
- StatusPropagator (the primary consumer) is in lib/
- No WorkEngine or GovernanceLayer dependency needed
- Pure data-reading module (reads YAML/markdown, returns dataclasses)
- Follows ConfigLoader pattern (lib/config.py) — infrastructure utility

### Data Types

```python
@dataclass
class ArcInfo:
    """Arc metadata parsed from haios.yaml active_arcs + ARC.md."""
    name: str           # e.g., "engine-functions"
    theme: str          # From ARC.md ## Definition
    status: str         # From ARC.md ## Definition
    chapters: List[str] # Chapter IDs from Chapters table

@dataclass
class ChapterInfo:
    """Chapter metadata parsed from ARC.md chapter table row."""
    id: str             # e.g., "CH-044"
    title: str          # e.g., "HierarchyQueryEngine"
    work_items: List[str]  # Work item IDs from table cell
    status: str         # e.g., "Planning", "Complete"
    arc: str            # Parent arc name

@dataclass
class WorkInfo:
    """Lightweight work item metadata for hierarchy queries."""
    id: str             # e.g., "WORK-157"
    title: str
    status: str
    type: str
    chapter: str        # From frontmatter
    arc: str            # From frontmatter

@dataclass
class HierarchyChain:
    """Full hierarchy chain from work item up to epoch."""
    work_id: str
    chapter: str        # CH-XXX
    arc: str            # Arc name
    epoch: str          # e.g., "E2.7"
```

### Function Signatures

```python
class HierarchyQueryEngine:
    """
    Stateless hierarchy query engine for epoch/arc/chapter/work navigation.

    Reads hierarchy from existing markdown files (EPOCH.md, ARC.md, WORK.md)
    via ConfigLoader path resolution. All I/O injectable via base_path for testing.

    Usage:
        engine = HierarchyQueryEngine()  # production
        engine = HierarchyQueryEngine(base_path=tmp_path)  # testing
    """

    def __init__(self, base_path: Optional[Path] = None):
        """
        Args:
            base_path: Project root (default: auto-detect from __file__)
        """

    def get_arcs(self) -> List[ArcInfo]:
        """
        Get all active arcs from haios.yaml epoch.active_arcs + ARC.md files.

        Reads haios.yaml for active_arcs list and arcs_dir path.
        For each arc, parses ARC.md for theme, status, and chapter list.

        Returns:
            List of ArcInfo, sorted by name. Empty list if no arcs_dir.
        """

    def get_chapters(self, arc_name: str) -> List[ChapterInfo]:
        """
        Get chapters for a given arc from its ARC.md chapter table.

        Parses the markdown table under ## Chapters in ARC.md.
        Table format: | CH-ID | Title | Work Items | Requirements | Dependencies | Status |

        Args:
            arc_name: Arc directory name (e.g., "engine-functions")

        Returns:
            List of ChapterInfo. Empty list if arc not found.
        """

    def get_work(self, chapter_id: str) -> List[WorkInfo]:
        """
        Get work items assigned to a chapter by scanning active work items.

        Reads each WORK.md in docs/work/active/ and filters by chapter field.
        Includes ALL statuses (active, complete, etc.) for completeness queries.

        Args:
            chapter_id: Chapter ID (e.g., "CH-044")

        Returns:
            List of WorkInfo. Empty list if no items found.
        """

    def get_hierarchy(self, work_id: str) -> Optional[HierarchyChain]:
        """
        Get full hierarchy chain for a work item (work -> chapter -> arc -> epoch).

        Reads work item frontmatter for chapter/arc fields.
        Resolves epoch from haios.yaml epoch.current.

        Args:
            work_id: Work item ID (e.g., "WORK-157")

        Returns:
            HierarchyChain if work item has chapter/arc fields, None otherwise.
        """
```

### Parsing Logic

**ARC.md chapter table parsing** (reuse StatusPropagator pattern from `status_propagator.py:199-245`):

```python
def _parse_arc_chapters(self, arc_file: Path, arc_name: str) -> List[ChapterInfo]:
    """Parse chapter table rows from ARC.md."""
    content = arc_file.read_text(encoding="utf-8")
    chapters = []
    for line in content.split("\n"):
        # Match: | CH-XXX | Title | Work Items | ... | Status |
        if re.match(r"\s*\|\s*CH-\d+", line):
            cells = [c.strip() for c in line.split("|") if c.strip()]
            if len(cells) >= 4:
                ch_id = cells[0]       # CH-044
                title = cells[1]       # HierarchyQueryEngine
                work_str = cells[2]    # "WORK-157" or "WORK-152, WORK-155"
                status = cells[-1]     # Planning, Complete
                # Parse work item IDs from cell
                work_items = [w.strip() for w in re.findall(r"WORK-\d+", work_str)]
                chapters.append(ChapterInfo(
                    id=ch_id, title=title, work_items=work_items,
                    status=status, arc=arc_name
                ))
    return chapters
```

**ARC.md theme/status extraction:**

```python
def _parse_arc_metadata(self, arc_file: Path) -> dict:
    """Extract theme and status from ARC.md frontmatter-like structure."""
    content = arc_file.read_text(encoding="utf-8")
    theme = ""
    status = ""
    for line in content.split("\n"):
        if line.startswith("**Theme:**"):
            theme = line.split("**Theme:**")[1].strip()
        elif line.startswith("**Status:**"):
            status = line.split("**Status:**")[1].strip()
    return {"theme": theme, "status": status}
```

**Work item chapter lookup:**

```python
def _get_work_chapter_arc(self, work_id: str) -> Optional[tuple]:
    """Read chapter/arc from work item WORK.md frontmatter."""
    work_file = self._active_dir / work_id / "WORK.md"
    if not work_file.exists():
        return None
    content = work_file.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        return None
    fm = yaml.safe_load(parts[1]) or {}
    chapter = fm.get("chapter")
    arc = fm.get("arc")
    if not chapter or not arc:
        return None
    return (chapter, arc)
```

### Path Resolution

All paths via haios.yaml config:
```python
# haios.yaml paths used:
config = self._load_haios_config()
arcs_dir = config.get("epoch", {}).get("arcs_dir", "")    # ".claude/haios/epochs/E2_7/arcs"
active_arcs = config.get("epoch", {}).get("active_arcs", [])  # ["engine-functions", "composability", "infrastructure"]
current_epoch = config.get("epoch", {}).get("current", "")     # "E2.7"

# Resolved paths:
arc_file = self._base_path / arcs_dir / arc_name / "ARC.md"
active_dir = self._base_path / "docs" / "work" / "active"     # Via ConfigLoader.get_path("work_active")
```

### Call Chain Context

```
StatusPropagator.propagate()
    |
    +-> HierarchyQueryEngine.get_hierarchy()  # <-- replaces get_hierarchy_context()
    |       Returns: HierarchyChain
    |
    +-> HierarchyQueryEngine.get_work()       # <-- replaces is_chapter_complete() scan
    |       Returns: List[WorkInfo]
    |
    +-> StatusPropagator.update_arc_chapter_status()  # Unchanged
```

### Consumer Integration (StatusPropagator)

The `TODO(CH-044)` in `status_propagator.py:47` will be resolved:

```python
# BEFORE (status_propagator.py:134-167):
def is_chapter_complete(self, chapter_id: str) -> bool:
    active_dir = self._base_path / "docs" / "work" / "active"
    # Full directory scan...

# AFTER:
def is_chapter_complete(self, chapter_id: str) -> bool:
    items = self._hierarchy.get_work(chapter_id)
    if not items:
        return False
    return all(s.status.lower() in COMPLETE_STATUSES for s in items)
```

### Import Pattern (E2-255 verified from cascade_engine.py)

```python
# hierarchy_engine.py - lib/ module
# Follows ConfigLoader pattern (lib/config.py): no try/except needed
# lib/ modules use direct imports since they don't run as packages
import yaml
import re
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Optional
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Module location | lib/ not modules/ | No GovernanceLayer/WorkEngine dependency; pure data reader like ConfigLoader. StatusPropagator (primary consumer) is in lib/. |
| Typed dataclasses | ArcInfo, ChapterInfo, WorkInfo, HierarchyChain | Type safety, IDE support, match WorkState pattern in work_engine.py |
| Parse markdown tables | Regex line-by-line | Matches StatusPropagator pattern (proven in WORK-034). No new parser dependency. |
| get_work includes all statuses | Yes (active + complete) | StatusPropagator.is_chapter_complete needs to see both. Caller filters if needed. |
| haios.yaml direct read | Yes, not via ConfigLoader | ConfigLoader doesn't expose epoch.active_arcs. Direct yaml.safe_load follows StatusPropagator pattern. |
| Injectable base_path | Yes (default auto-detect) | Matches StatusPropagator, CascadeEngine testing patterns. |
| No caching | Stateless reads on each call | Matches WorkEngine/StatusPropagator pattern. Files may change between calls. |

### Input/Output Examples

**Real data from current system:**

```
# get_arcs() with current E2.7 config
haios.yaml active_arcs: ["engine-functions", "composability", "infrastructure"]
arcs_dir: ".claude/haios/epochs/E2_7/arcs"

Returns:
[
  ArcInfo(name="composability", theme="Compose, don't concatenate...", status="Active", chapters=["CH-046","CH-047","CH-048"]),
  ArcInfo(name="engine-functions", theme="Functions over file reads...", status="Active", chapters=["CH-044","CH-045"]),
  ArcInfo(name="infrastructure", theme="Clean the house first...", status="Active", chapters=["CH-049","CH-050","CH-051"]),
]

# get_chapters("engine-functions")
Parses ARC.md table:
| CH-044 | HierarchyQueryEngine | WORK-157 | REQ-TRACE-005 | None | Planning |
| CH-045 | StatusCascade | WORK-034 | REQ-QUEUE-001 | CH-044 | Complete |

Returns:
[
  ChapterInfo(id="CH-044", title="HierarchyQueryEngine", work_items=["WORK-157"], status="Planning", arc="engine-functions"),
  ChapterInfo(id="CH-045", title="StatusCascade", work_items=["WORK-034"], status="Complete", arc="engine-functions"),
]

# get_hierarchy("WORK-157")
Reads WORK.md: chapter=CH-044, arc=engine-functions
Reads haios.yaml: epoch.current="E2.7"

Returns:
HierarchyChain(work_id="WORK-157", chapter="CH-044", arc="engine-functions", epoch="E2.7")
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| ARC.md missing | get_chapters returns [] | Test 3 |
| Work item missing chapter/arc | get_hierarchy returns None | Test 7 |
| No active work dir | get_work returns [] | Test 5 |
| Chapter with multiple work items | Parse comma-separated IDs from table cell | Test 2, 9 |
| haios.yaml missing | get_arcs returns [] | Test 8 |
| Work item in archive (not active) | Not included in get_work() (scans active only) | By design — matches StatusPropagator |

### Open Questions

**Q: Should get_work() also scan archive directory?**

No. StatusPropagator only scans active, and completed items remain in active per ADR-041 ("status over location"). Archive is only for epoch cleanup.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| No unresolved operator decisions | N/A | N/A | Work item has no operator_decisions field |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_hierarchy_engine.py` with all 10 tests
- [ ] Create `_setup_hierarchy()` helper fixture (haios.yaml + ARC.md + WORK.md files)
- [ ] Verify all tests fail (red) — ImportError from missing module

### Step 2: Implement HierarchyQueryEngine
- [ ] Create `.claude/haios/lib/hierarchy_engine.py`
- [ ] Implement dataclasses: ArcInfo, ChapterInfo, WorkInfo, HierarchyChain
- [ ] Implement `get_arcs()` — reads haios.yaml + ARC.md files
- [ ] Implement `get_chapters()` — parses ARC.md chapter table
- [ ] Implement `get_work()` — scans active dir, filters by chapter
- [ ] Implement `get_hierarchy()` — reads WORK.md frontmatter + haios.yaml
- [ ] Tests 1-9 pass (green)

### Step 3: Integrate with StatusPropagator
- [ ] Add HierarchyQueryEngine import to status_propagator.py
- [ ] Refactor `is_chapter_complete()` to use `engine.get_work()`
- [ ] Remove TODO(CH-044) comment
- [ ] Test 10 passes (green)
- [ ] Existing status_propagator tests still pass (no regression)

### Step 4: Integration Verification
- [ ] All hierarchy engine tests pass
- [ ] All status_propagator tests pass
- [ ] Run full test suite (no regressions)

### Step 5: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/lib/README.md` with hierarchy_engine.py entry
- [ ] **MUST:** Verify README content matches actual file state

### Step 6: Consumer Verification
- [ ] **MUST:** Grep for `TODO(CH-044)` — should be zero remaining
- [ ] **MUST:** Grep for hardcoded hierarchy path patterns that should use engine

---

## Verification

- [ ] Tests pass (`pytest tests/test_hierarchy_engine.py tests/test_status_propagator.py -v`)
- [ ] **MUST:** All READMEs current
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| ARC.md table format varies across arcs | Medium | Regex tested against all 3 current ARC.md files. Table format is consistent. |
| StatusPropagator refactor breaks existing tests | Medium | Run existing test_status_propagator.py after refactor. Tests are comprehensive (8 tests). |
| haios.yaml epoch structure changes | Low | Read config defensively with `.get()` chains and empty defaults. |
| New module not discovered by consumers | Low | Explicit import in status_propagator.py. Document in lib/ README. |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 393 | 2026-02-17 | - | Plan authored | Plan authoring cycle complete |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-157/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| `get_arcs()` function returning arc metadata | [ ] | Read hierarchy_engine.py, verify function exists |
| `get_chapters(arc_id)` function returning chapter list | [ ] | Read hierarchy_engine.py, verify function exists |
| `get_work(chapter_id)` function returning work items | [ ] | Read hierarchy_engine.py, verify function exists |
| `get_hierarchy(work_id)` function returning full chain | [ ] | Read hierarchy_engine.py, verify function exists |
| Unit tests for all query functions | [ ] | Read test_hierarchy_engine.py, count test cases |
| Integration test with real epoch/arc/chapter files | [ ] | Verify test uses representative fixture data |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/hierarchy_engine.py` | 4 query functions + 4 dataclasses | [ ] | |
| `tests/test_hierarchy_engine.py` | 10+ tests covering all functions + edge cases | [ ] | |
| `.claude/haios/lib/status_propagator.py` | Uses HierarchyQueryEngine, TODO removed | [ ] | |
| `.claude/haios/lib/README.md` | **MUST:** Lists hierarchy_engine.py | [ ] | |
| `Grep: TODO(CH-044)` | **MUST:** Zero remaining references | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_hierarchy_engine.py tests/test_status_propagator.py -v
# Expected: 18+ tests passed (10 new + 8 existing)
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
- [ ] **Runtime consumer exists** (StatusPropagator imports and calls HierarchyQueryEngine)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories
- [ ] **MUST:** Consumer verification complete (zero TODO(CH-044) references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- @.claude/haios/epochs/E2_7/arcs/engine-functions/ARC.md
- @.claude/haios/epochs/E2_7/EPOCH.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-TRACE-005)
- @.claude/haios/lib/status_propagator.py (TODO(CH-044) consumer)
- @.claude/haios/lib/config.py (ConfigLoader pattern)
- @.claude/haios/modules/cascade_engine.py (sibling pattern reference)
- Memory: 84811 (flat storage architecture), 84212 (no epoch-status command), 84230 (chapters as immutable docs)

---
