---
template: implementation_plan
status: complete
date: 2026-02-11
backlog_id: WORK-122
title: "Closure Ceremony Contracts (CH-015)"
author: Hephaestus
lifecycle_phase: plan
session: 345
version: "1.5"
generated: 2026-02-11
last_updated: 2026-02-11T20:52:54
---
# Implementation Plan: Closure Ceremony Contracts (CH-015)

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | CH-011/WORK-112 already done contracts; this adds validation functions |
| Document design decisions | MUST | Filled below |
| Ground truth metrics | MUST | Based on actual file analysis |

---

## Goal

Programmatic DoD validation functions that closure ceremony skills can invoke to reduce manual agent bookkeeping, plus fix the pre-existing encoding bug in test_multilevel_dod.py.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `tests/test_multilevel_dod.py` (encoding fix) |
| Lines of code affected | ~3 | Fixture encoding parameter |
| New files to create | 2 | `lib/dod_validation.py`, `tests/test_dod_validation.py` |
| Tests to write | ~8 | 4 validation functions x 2 cases each |
| Dependencies | 1 | `work_item.py` (find_work_file) or direct Path/yaml |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | New module, no callers yet (runtime consumer = closure skills) |
| Risk of regression | Low | New module, existing tests untouched except encoding fix |
| External dependencies | Low | Only filesystem (read YAML frontmatter) |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests + encoding fix | 15 min | High |
| Implementation | 20 min | High |
| Verification | 10 min | High |
| **Total** | **45 min** | |

---

## Current State vs Desired State

### Current State

Each closure ceremony skill describes DoD validation as prose steps the agent follows manually:
- close-chapter-ceremony: Agent must grep for work items, check each status, read exit criteria checkboxes
- close-arc-ceremony: Agent must glob chapter files, check each status, run audit
- This costs ~200-500 tokens per closure ceremony VALIDATE phase

**Behavior:** Agent manually reads files, greps for statuses, interprets results.

**Result:** High ceremony overhead for closing entities. Inconsistent validation (agent may miss checks).

### Desired State

```python
# lib/dod_validation.py
from dod_validation import validate_work_dod, validate_chapter_dod

result = validate_chapter_dod("CH-015", "ceremonies")
# DoDResult(passed=True, checks=[...], failures=[])
```

**Behavior:** Agent calls one function, gets structured result.

**Result:** Consistent validation, lower ceremony overhead, machine-parseable results.

---

## Tests First (TDD)

### Test 1: validate_work_dod returns DoDResult

```python
def test_validate_work_dod_returns_result(tmp_path):
    """validate_work_dod returns DoDResult with passed and checks fields."""
    # Setup: create minimal work dir with WORK.md status: complete
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-001"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text("---\nstatus: complete\nclosed: 2026-02-11\ntraces_to: [REQ-TEST-001]\n---\n# WORK-001\n", encoding="utf-8")
    result = validate_work_dod("WORK-001", base_path=tmp_path)
    assert hasattr(result, "passed")
    assert hasattr(result, "checks")
    assert hasattr(result, "failures")
```

### Test 2: validate_work_dod fails on incomplete work

```python
def test_validate_work_dod_fails_incomplete(tmp_path):
    """validate_work_dod fails when status is not complete."""
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-001"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text("---\nstatus: active\nclosed: null\ntraces_to: []\n---\n# WORK-001\n", encoding="utf-8")
    result = validate_work_dod("WORK-001", base_path=tmp_path)
    assert result.passed is False
    assert len(result.failures) > 0
```

### Test 3: validate_chapter_dod checks all work items (bold markdown format)

```python
def test_validate_chapter_dod_checks_work_items(tmp_path):
    """validate_chapter_dod verifies all chapter work items are complete."""
    # Setup: chapter file in BOLD MARKDOWN format (not YAML frontmatter)
    epoch_dir = tmp_path / ".claude" / "haios" / "epochs" / "E2_5"
    ch_dir = epoch_dir / "arcs" / "ceremonies"
    ch_dir.mkdir(parents=True)
    (ch_dir / "CH-015-ClosureCeremonies.md").write_text(
        "# Chapter: Closure Ceremonies\n\n"
        "**Chapter ID:** CH-015\n**Arc:** ceremonies\n**Status:** Complete\n\n"
        "## Exit Criteria\n\n- [x] 4 closure skills\n- [x] Contracts added\n",
        encoding="utf-8"
    )
    # Setup: 2 work items with chapter: CH-015, both complete
    for wid in ["WORK-111", "WORK-112"]:
        wd = tmp_path / "docs" / "work" / "active" / wid
        wd.mkdir(parents=True)
        (wd / "WORK.md").write_text(
            f"---\nid: {wid}\nstatus: complete\nchapter: CH-015\nclosed: 2026-02-11\n---\n",
            encoding="utf-8"
        )
    result = validate_chapter_dod("CH-015", "ceremonies", base_path=tmp_path)
    assert result.passed is True
```

### Test 4: validate_chapter_dod fails with incomplete work

```python
def test_validate_chapter_dod_fails_incomplete_work(tmp_path):
    """validate_chapter_dod fails when any work item is not complete."""
    # Setup: chapter file + 1 complete + 1 active work item
    epoch_dir = tmp_path / ".claude" / "haios" / "epochs" / "E2_5"
    ch_dir = epoch_dir / "arcs" / "ceremonies"
    ch_dir.mkdir(parents=True)
    (ch_dir / "CH-015-ClosureCeremonies.md").write_text(
        "**Chapter ID:** CH-015\n**Status:** Planned\n\n"
        "## Exit Criteria\n\n- [ ] Not done yet\n",
        encoding="utf-8"
    )
    wd1 = tmp_path / "docs" / "work" / "active" / "WORK-111"
    wd1.mkdir(parents=True)
    (wd1 / "WORK.md").write_text("---\nid: WORK-111\nstatus: complete\nchapter: CH-015\n---\n", encoding="utf-8")
    wd2 = tmp_path / "docs" / "work" / "active" / "WORK-122"
    wd2.mkdir(parents=True)
    (wd2 / "WORK.md").write_text("---\nid: WORK-122\nstatus: active\nchapter: CH-015\n---\n", encoding="utf-8")
    result = validate_chapter_dod("CH-015", "ceremonies", base_path=tmp_path)
    assert result.passed is False
    assert any("WORK-122" in f for f in result.failures)
```

### Test 5: validate_arc_dod checks all chapters (bold markdown format)

```python
def test_validate_arc_dod_checks_chapters(tmp_path):
    """validate_arc_dod verifies all arc chapters are Complete via bold markdown."""
    arc_dir = tmp_path / ".claude" / "haios" / "epochs" / "E2_5" / "arcs" / "ceremonies"
    arc_dir.mkdir(parents=True)
    (arc_dir / "ARC.md").write_text("**Status:** Complete\n", encoding="utf-8")
    (arc_dir / "CH-011-CeremonyContracts.md").write_text("**Status:** Complete\n", encoding="utf-8")
    (arc_dir / "CH-012-SideEffectBoundaries.md").write_text("**Status:** Complete\n", encoding="utf-8")
    result = validate_arc_dod("ceremonies", base_path=tmp_path)
    assert result.passed is True
```

### Test 6: validate_epoch_dod checks all arcs (bold markdown format)

```python
def test_validate_epoch_dod_checks_arcs(tmp_path):
    """validate_epoch_dod verifies all arcs are Complete via bold markdown."""
    epoch_dir = tmp_path / ".claude" / "haios" / "epochs" / "E2_5"
    epoch_dir.mkdir(parents=True)
    (epoch_dir / "EPOCH.md").write_text("**Status:** Active\n", encoding="utf-8")
    arcs_dir = epoch_dir / "arcs"
    for arc in ["lifecycles", "ceremonies"]:
        (arcs_dir / arc).mkdir(parents=True)
        (arcs_dir / arc / "ARC.md").write_text("**Status:** Complete\n", encoding="utf-8")
    result = validate_epoch_dod("E2_5", base_path=tmp_path)
    assert result.passed is True
```

### Test 7: Encoding fix in test_multilevel_dod

```python
def test_multilevel_dod_encoding_fix():
    """test_multilevel_dod.py fixture should use encoding='utf-8'."""
    content = Path("tests/test_multilevel_dod.py").read_text()
    assert "encoding" in content  # fixture uses explicit encoding
```

### Test 8: Backward compatibility

```python
def test_existing_ceremony_retrofit_tests_still_pass():
    """Existing ceremony tests should not regress."""
    # Run via pytest - verified in CHECK phase
```

---

## Detailed Design

### New File: `.claude/haios/lib/dod_validation.py`

**Pattern Reference:** Follows `ceremony_contracts.py` patterns (dataclass results, Path-based, yaml parsing).

**Critique Revision (A1):** Chapter, arc, and epoch files use **bold markdown** (`**Status:** Complete`), NOT YAML frontmatter. Only WORK.md files have YAML frontmatter. Two parsing functions needed.

**Critique Revision (A2):** Work-item-to-chapter discovery uses `chapter:` field in WORK.md frontmatter (format: `chapter: CH-015`, no arc prefix). Scans all `docs/work/active/*/WORK.md`.

```python
"""
DoD validation functions for closure ceremonies (CH-015, WORK-122).

Two file format parsers:
- _parse_frontmatter(): For WORK.md files (YAML between --- markers)
- _parse_markdown_field(): For chapter/arc/epoch files (bold markdown **Field:** Value)

Four validation functions:
- validate_work_dod: Work item status, traces_to, closed date
- validate_chapter_dod: All chapter work items complete + exit criteria
- validate_arc_dod: All arc chapters Complete
- validate_epoch_dod: All epoch arcs Complete

Usage:
    from dod_validation import validate_work_dod, validate_chapter_dod
    result = validate_chapter_dod("CH-015", "ceremonies")
    if not result.passed:
        print(result.failures)
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

import yaml


@dataclass
class DoDCheck:
    """Single DoD check result."""
    name: str
    passed: bool
    detail: str = ""


@dataclass
class DoDResult:
    """Result of DoD validation at any level."""
    level: str  # "work", "chapter", "arc", "epoch"
    entity_id: str
    passed: bool
    checks: List[DoDCheck] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)


def _parse_frontmatter(path: Path) -> dict:
    """Parse YAML frontmatter from a WORK.md file (--- delimited)."""
    content = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    return yaml.safe_load(match.group(1)) or {}


def _parse_markdown_field(content: str, field_name: str) -> Optional[str]:
    """Extract value from bold markdown field: **Field:** Value.

    Used for chapter, arc, epoch files which do NOT use YAML frontmatter.
    Example: _parse_markdown_field(content, "Status") -> "Complete"
    """
    pattern = rf"\*\*{re.escape(field_name)}:\*\*\s*(.+)"
    match = re.search(pattern, content)
    return match.group(1).strip() if match else None


def _count_exit_criteria(content: str) -> tuple:
    """Count checked vs total exit criteria checkboxes.

    Returns: (checked_count, total_count)
    """
    total = len(re.findall(r"- \[[ x]\]", content))
    checked = len(re.findall(r"- \[x\]", content))
    return checked, total


def _find_work_items_for_chapter(chapter_id: str, base_path: Path) -> list:
    """Find all work items assigned to a chapter via frontmatter chapter: field.

    Scans docs/work/active/*/WORK.md, returns list of (work_id, frontmatter_dict).
    """
    active_dir = base_path / "docs" / "work" / "active"
    results = []
    if not active_dir.exists():
        return results
    for work_dir in sorted(active_dir.iterdir()):
        work_file = work_dir / "WORK.md"
        if not work_file.exists():
            continue
        fm = _parse_frontmatter(work_file)
        if fm.get("chapter") == chapter_id:
            results.append((fm.get("id", work_dir.name), fm))
    return results


def validate_work_dod(
    work_id: str,
    base_path: Optional[Path] = None,
) -> DoDResult:
    """Validate work item meets Definition of Done.

    Checks: status == complete, closed date set, traces_to non-empty.
    """
    ...


def validate_chapter_dod(
    chapter_id: str,
    arc: str,
    base_path: Optional[Path] = None,
    epoch_dir: str = ".claude/haios/epochs/E2_5",
) -> DoDResult:
    """Validate chapter meets DoD.

    Checks: all work items with chapter: {chapter_id} are complete,
    exit criteria checkboxes all checked.
    Uses _parse_markdown_field for chapter status (bold markdown format).
    Uses _find_work_items_for_chapter for work item discovery.
    """
    ...


def validate_arc_dod(
    arc: str,
    base_path: Optional[Path] = None,
    epoch_dir: str = ".claude/haios/epochs/E2_5",
) -> DoDResult:
    """Validate arc meets DoD (all chapters Complete).

    Globs CH-*.md files in arc directory.
    Uses _parse_markdown_field to check **Status:** of each chapter.
    Skips chapters with Status containing "Deferred".
    """
    ...


def validate_epoch_dod(
    epoch_id: str,
    base_path: Optional[Path] = None,
) -> DoDResult:
    """Validate epoch meets DoD (all arcs Complete).

    Globs arcs/*/ARC.md files in epoch directory.
    Uses _parse_markdown_field to check **Status:** of each arc.
    Skips arcs with Status containing "Deferred".
    """
    ...
```

### Call Chain Context

```
close-chapter-ceremony (SKILL.md)
    |
    +-> Agent reads skill, follows VALIDATE phase
    |       Currently: manual grep + read
    |       After: validate_chapter_dod("CH-015", "ceremonies")
    |
    +-> DoDResult returned → agent reports to operator
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| New module vs extend ceremony_contracts | New `dod_validation.py` | Separation of concerns — contracts define schema, validation checks state |
| `base_path` parameter | Optional, defaults to cwd | Enables testing with tmp_path without mocking filesystem |
| DoDResult dataclass | Structured result, not bool | Agent needs to report what failed, not just pass/fail |
| Read frontmatter directly | Not via WorkEngine | WorkEngine requires governance init; validation should be lightweight |
| `epoch_dir` parameter | Configurable, defaults to E2_5 | Avoids hardcoded epoch (portability arc concern) |
| Exit criteria parsing | Regex for `- [x]` vs `- [ ]` | Chapter files use markdown checkboxes for exit criteria |
| Two parsers (A1 critique) | `_parse_frontmatter` for WORK.md, `_parse_markdown_field` for chapter/arc/epoch | Chapter/arc/epoch files use `**Field:** Value` bold markdown, NOT YAML frontmatter. Critique caught this — would have caused silent failure in 3/4 functions |
| Work-item discovery (A2 critique) | Scan `docs/work/active/*/WORK.md`, filter by `chapter == chapter_id` | Real data uses `chapter: CH-015` (no arc prefix). Close-chapter-ceremony SKILL.md grep pattern `chapter: {arc}/{chapter_id}` is wrong for actual data |
| Signature deviates from CH-015 spec (A3) | Take `(chapter_id, arc)` instead of `(chapter_path: Path)` | Logical IDs are better API than raw paths; CH-015 spec predates this implementation. Chapter file will be updated at closure |
| Deferred items (A7) | Skip items with Status containing "Deferred" | S339 operator decision — deferred items are out of scope, not failures |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Work item not found | DoDResult(passed=False, failures=["Work item not found"]) | Test 2 variant |
| Chapter has no work items | DoDResult(passed=True) with note | Test 3 variant |
| Arc has deferred chapters | Skip chapters with `**Status:** Deferred` | Test 5 variant |
| Epoch has deferred arcs | Skip arcs with `Deferred` status | Test 6 variant |

### Open Questions

**Q: Should deferred arcs/chapters be skipped or fail validation?**

Skip. Deferred items are explicitly out of scope (S339 operator decision). Validation should only check non-deferred entities. This matches the epoch exit criteria where deferred items are struck through.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| None | N/A | N/A | All design decisions resolved above |

---

## Implementation Steps

### Step 1: Write Failing Tests

- [ ] Create `tests/test_dod_validation.py` with all 6 DoD tests (Tests 1-6)
- [ ] Verify all tests fail (red) — module doesn't exist yet

### Step 2: Fix Encoding Bug

- [ ] Edit `tests/test_multilevel_dod.py` fixture to use `encoding="utf-8"`
- [ ] Verify 3 previously erroring tests now pass

### Step 3: Implement dod_validation.py

- [ ] Create `.claude/haios/lib/dod_validation.py`
- [ ] Implement `DoDCheck`, `DoDResult` dataclasses
- [ ] Implement `_parse_frontmatter` utility
- [ ] Implement `validate_work_dod`
- [ ] Implement `validate_chapter_dod`
- [ ] Implement `validate_arc_dod`
- [ ] Implement `validate_epoch_dod`
- [ ] Tests 1-6 pass (green)

### Step 4: Integration Verification

- [ ] All new tests pass
- [ ] Run full test suite (no regressions): `pytest tests/test_dod_validation.py tests/test_multilevel_dod.py tests/test_ceremony_retrofit.py tests/test_ceremony_contracts.py -v`

### Step 5: README Sync (MUST)

- [ ] **MUST:** Update `.claude/haios/lib/` README if exists

### Step 6: Consumer Verification (MUST for migrations/refactors)

**SKIPPED:** New module, no migrations. Consumers will be the closure ceremony skills (runtime consumer exists: skills reference lib functions).

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Frontmatter parsing inconsistency across files | Low | Use same `_parse_frontmatter` as test_ceremony_retrofit.py |
| Exit criteria checkbox format varies | Low | Test with real chapter files |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 345 | 2026-02-11 | - | Plan | Plan created |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-122/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Ceremony contracts in 4 closure skills | [x] | Already done CH-011/WORK-112, test_ceremony_retrofit.py 105/105 |
| Contract frontmatter parses | [x] | test_ceremony_contracts.py 15/15 |
| Cascading DoD documented | [x] | Each skill VALIDATE phase describes checks |
| DoD validation functions in lib/ | [ ] | dod_validation.py created |
| Fix encoding in test_multilevel_dod | [ ] | 3 tests now pass |
| Tests for DoD validation | [ ] | test_dod_validation.py all pass |
| CH-015 status Complete | [ ] | Chapter file updated |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/dod_validation.py` | 4 validation functions | [ ] | |
| `tests/test_dod_validation.py` | ~8 tests, all pass | [ ] | |
| `tests/test_multilevel_dod.py` | encoding fix, 0 errors | [ ] | |

---

## References

- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-015-ClosureCeremonies.md
- @.claude/haios/lib/ceremony_contracts.py (pattern reference)
- @tests/test_ceremony_retrofit.py (existing contract tests)
- @tests/test_multilevel_dod.py (encoding bug)

---
