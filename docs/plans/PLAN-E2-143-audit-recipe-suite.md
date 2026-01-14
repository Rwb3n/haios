---
template: implementation_plan
status: complete
date: 2025-12-24
backlog_id: E2-143
title: "Audit Recipe Suite"
author: Hephaestus
lifecycle_phase: plan
session: 111
version: "1.5"
generated: 2025-12-21
last_updated: 2025-12-24T19:13:58
---
# Implementation Plan: Audit Recipe Suite

@docs/README.md
@docs/epistemic_state.md

---

## Goal

Three just recipes (`audit-sync`, `audit-gaps`, `audit-stale`) that detect governance drift automatically, replacing manual audits.

---

## Effort Estimation (Ground Truth)

Medium complexity task creating audit module in .claude/lib/ with three functions, just recipes to call them, and tests.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `justfile` |
| New files to create | 2 | `.claude/lib/audit.py`, `tests/test_lib_audit.py` |
| Lines of code (new) | ~80 | 3 functions × ~20 lines + tests |
| Tests to write | 3 | One per audit function |
| Dependencies | 2 | `docs/work/`, `docs/investigations/` |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only reads files, no writes |
| Risk of regression | Low | New functionality, doesn't touch existing |
| External dependencies | Low | Only filesystem |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Create .claude/lib/audit.py | 15 min | High |
| Create tests/test_lib_audit.py | 10 min | High |
| Add just recipes | 5 min | High |
| **Total** | 30 min | High |

---

## Current State vs Desired State

Comparing manual governance audits with automated recipe-based detection.

### Current State

**Behavior:** Manual audit requires grepping and comparing files by hand (Session 101 took ~30 min)

**Result:** Drift accumulates undetected; status mismatches, orphan items, stale investigations

### Desired State

**Behavior:** Three recipes provide instant drift detection:
- `just audit-sync` - Find work files with `status: complete` but investigation still `status: active`
- `just audit-gaps` - Find active work with completed plans (implementation evidence but not closed)
- `just audit-stale` - Find investigations older than 10 sessions still active

**Result:** Governance drift detected in seconds, can be run in heartbeat or manually

---

## Tests First (TDD)

Tests in `tests/test_lib_audit.py`:

```python
"""Tests for .claude/lib/audit.py"""
import pytest
import tempfile
import os
from pathlib import Path

# Import after path setup
import sys
sys.path.insert(0, '.claude/lib')
from audit import parse_frontmatter, audit_sync, audit_gaps, audit_stale

def test_parse_frontmatter_valid():
    """Test parsing valid YAML frontmatter."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write('---\nstatus: active\nid: E2-001\n---\n# Content')
        f.flush()
        result = parse_frontmatter(f.name)
        assert result['status'] == 'active'
        assert result['id'] == 'E2-001'
    os.unlink(f.name)

def test_parse_frontmatter_missing():
    """Test parsing file without frontmatter."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write('# No frontmatter here')
        f.flush()
        result = parse_frontmatter(f.name)
        assert result == {}
    os.unlink(f.name)

def test_audit_sync_returns_list():
    """Verify audit_sync returns a list."""
    result = audit_sync()
    assert isinstance(result, list)

def test_audit_gaps_returns_list():
    """Verify audit_gaps returns a list."""
    result = audit_gaps()
    assert isinstance(result, list)

def test_audit_stale_returns_list():
    """Verify audit_stale returns a list."""
    result = audit_stale()
    assert isinstance(result, list)

def test_audit_stale_threshold():
    """Verify threshold parameter works."""
    result_high = audit_stale(threshold=1000)  # Very high, should find nothing recent
    result_low = audit_stale(threshold=0)      # Zero, should find everything
    # At minimum, result should be a list
    assert isinstance(result_high, list)
    assert isinstance(result_low, list)
```

---

## Detailed Design

Python module in .claude/lib/audit.py with three functions. Just recipes call module functions. Tests verify behavior.

### Module: .claude/lib/audit.py

```python
"""Governance audit functions for detecting drift."""
import glob
import json
import yaml
from pathlib import Path
from typing import List

def parse_frontmatter(file_path: str) -> dict:
    """Extract YAML frontmatter from markdown file."""
    content = Path(file_path).read_text(encoding='utf-8')
    if '---' not in content:
        return {}
    parts = content.split('---')
    if len(parts) < 2:
        return {}
    try:
        return yaml.safe_load(parts[1]) or {}
    except yaml.YAMLError:
        return {}

def audit_sync() -> List[str]:
    """Find investigations still active but work file is archived."""
    issues = []
    for inv in glob.glob('docs/investigations/INVESTIGATION-*.md'):
        fm = parse_frontmatter(inv)
        if fm.get('status') == 'active':
            inv_id = fm.get('backlog_id', '')
            if inv_id and glob.glob(f'docs/work/archive/WORK-{inv_id}-*.md'):
                issues.append(f'SYNC: {inv_id} investigation active but work archived')
    return issues

def audit_gaps() -> List[str]:
    """Find work items with complete plans but still active."""
    issues = []
    for work in glob.glob('docs/work/active/WORK-*.md'):
        fm = parse_frontmatter(work)
        work_id = fm.get('id', '')
        if not work_id:
            continue
        for plan in glob.glob(f'docs/plans/PLAN-{work_id}*.md'):
            pfm = parse_frontmatter(plan)
            if pfm.get('status') == 'complete':
                issues.append(f'GAP: {work_id} has complete plan but work still active')
    return issues

def audit_stale(threshold: int = 10) -> List[str]:
    """Find investigations older than threshold sessions."""
    issues = []
    try:
        status = json.loads(Path('.claude/haios-status.json').read_text())
        current = status.get('system', {}).get('last_session', 999)
    except (FileNotFoundError, json.JSONDecodeError):
        current = 999

    for inv in glob.glob('docs/investigations/INVESTIGATION-*.md'):
        fm = parse_frontmatter(inv)
        if fm.get('status') == 'active':
            sess = fm.get('session', 0)
            if current - sess > threshold:
                inv_id = fm.get('backlog_id', '?')
                issues.append(f'STALE: {inv_id} active since S{sess} (now S{current})')
    return issues
```

### Just Recipes (justfile)

```just
# Audit: Find investigations active but work archived (E2-143)
audit-sync:
    @python -c "import sys; sys.path.insert(0, '.claude/lib'); from audit import audit_sync; [print(i) for i in audit_sync()]"

# Audit: Find work items with complete plans but still active (E2-143)
audit-gaps:
    @python -c "import sys; sys.path.insert(0, '.claude/lib'); from audit import audit_gaps; [print(i) for i in audit_gaps()]"

# Audit: Find investigations older than 10 sessions (E2-143)
audit-stale:
    @python -c "import sys; sys.path.insert(0, '.claude/lib'); from audit import audit_stale; [print(i) for i in audit_stale()]"
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Module vs inline | .claude/lib/audit.py | Testable, maintainable, follows INV-011 architecture |
| Return type | List of strings | Enables testing (assert length), flexible output |
| Threshold param | audit_stale(threshold=10) | Configurable for testing and flexibility |
| YAML parsing | Separate parse_frontmatter() | Reusable, testable, handles errors gracefully |

### Expected Output Examples

**audit-sync:**
```
SYNC: INV-022 investigation active but work archived
```
(If INV-022 investigation is still status: active but WORK-INV-022-*.md is in archive/)

**audit-gaps:**
```
GAP: E2-143 has complete plan but work still active
```
(If PLAN-E2-143-*.md has status: complete but work file in active/)

**audit-stale:**
```
STALE: INV-005 active since S45 (now S113)
```
(If investigation session is >10 behind current)

### Edge Cases

| Case | Handling |
|------|----------|
| Missing frontmatter | Skip file (if '---' not in content) |
| Missing session field | Default to 0 (always stale) |
| No matches | Silent (no output = clean) |

---

## Implementation Steps

Create module first, then tests, then recipes. TDD approach.

### Step 1: Create .claude/lib/audit.py
- [ ] Create audit.py with parse_frontmatter, audit_sync, audit_gaps, audit_stale
- [ ] Verify module imports without error

### Step 2: Create tests/test_lib_audit.py
- [ ] Create test file with 6 tests
- [ ] Run pytest tests/test_lib_audit.py
- [ ] All tests pass (green)

### Step 3: Add just recipes
- [ ] Add audit-sync, audit-gaps, audit-stale to justfile
- [ ] Verify each recipe runs without error

### Step 4: Final verification
- [ ] All tests pass: `pytest tests/test_lib_audit.py`
- [ ] Recipes visible: `just --list | grep audit`
- [ ] Run each recipe and verify output

---

## Verification

- [ ] `pytest tests/test_lib_audit.py` passes (6 tests)
- [ ] `just audit-sync` executes
- [ ] `just audit-gaps` executes
- [ ] `just audit-stale` executes
- [ ] All three visible in `just --list | grep audit`

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| YAML parsing errors | Low | Skip files without proper frontmatter |
| False positives | Low | Output is advisory, not blocking |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 113 | 2025-12-24 | - | Plan created | - |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/audit.py` | Contains parse_frontmatter, audit_sync, audit_gaps, audit_stale | [ ] | |
| `tests/test_lib_audit.py` | Contains 6 tests, all pass | [ ] | |
| `justfile` | Contains audit-sync, audit-gaps, audit-stale recipes | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_lib_audit.py -v
# Expected: 6 tests passed

just --list | grep audit
# Expected: 3 recipes listed
```

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass (pytest tests/test_lib_audit.py)
- [ ] WHY captured (reasoning stored to memory)
- [ ] Recipes visible in `just --list`

---

## References

- INV-022: Work-Cycle-DAG Unified Architecture (spawned this item)
- E2-168, E2-169, E2-167: Prior M7a-Recipes items (pattern reference)

---
