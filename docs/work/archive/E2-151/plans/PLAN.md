---
template: implementation_plan
status: complete
date: 2025-12-23
backlog_id: E2-151
title: "Backlog-Migration-Script"
author: Hephaestus
lifecycle_phase: plan
session: 105
version: "1.5"
generated: 2025-12-21
last_updated: 2025-12-23T19:08:23
---
# Implementation Plan: Backlog-Migration-Script

@docs/README.md
@docs/epistemic_state.md
@docs/pm/backlog.md

---

## Goal

Create a Python script to migrate active backlog.md entries to individual WORK-{id}.md files in docs/work/active/.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 0 | New script only |
| Lines of code affected | ~150 | New script |
| New files to create | 1 + 58 | Script + work files |
| Tests to write | 3 | Parser, mapper, integration |
| Dependencies | 0 | Uses .claude/lib/scaffold.py |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only scaffold.py |
| Risk of regression | Low | New script, no existing code |
| External dependencies | Low | Just file system |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Script development | 30 min | High |
| Testing | 15 min | High |
| Migration run | 10 min | High |
| **Total** | ~55 min | |

---

## Current State vs Desired State

### Current State

**58 active items** in docs/pm/backlog.md (38 pending, 20 proposed).

```markdown
### [MEDIUM] E2-004: Documentation Sync
- **Status:** pending
- **Owner:** Hephaestus
- **Created:** 2025-12-07
- **Context:** Update epistemic_state.md...
```

**Behavior:** Items tracked in monolithic markdown file

**Result:** Status drift - backlog.md stale when work progresses

### Desired State

**Individual work files** in docs/work/active/:

```yaml
# docs/work/active/WORK-E2-004-documentation-sync.md
---
template: work_item
id: E2-004
title: "Documentation Sync"
status: active
priority: medium
current_node: backlog
...
---
# WORK-E2-004: Documentation Sync

## Context
Update epistemic_state.md...
```

**Behavior:** Each item is self-contained file with status in frontmatter

**Result:** Single source of truth (directory = status)

---

## Tests First (TDD)

### Test 1: Parse single backlog entry
```python
def test_parse_backlog_entry():
    entry = '''### [MEDIUM] E2-004: Documentation Sync
- **Status:** pending
- **Owner:** Hephaestus
- **Created:** 2025-12-07
- **Context:** Update docs'''

    result = parse_backlog_entry(entry)
    assert result["id"] == "E2-004"
    assert result["title"] == "Documentation Sync"
    assert result["priority"] == "medium"
    assert result["status"] == "pending"
```

### Test 2: Map fields to work file schema
```python
def test_map_to_work_schema():
    entry = {"id": "E2-004", "title": "Docs", "priority": "high", "status": "pending"}
    work = map_to_work_schema(entry)
    assert work["current_node"] == "backlog"
    assert work["priority"] == "high"
```

### Test 3: Full migration creates files
```python
def test_migrate_creates_work_files(tmp_path):
    # Run migration to temp directory
    result = migrate_backlog(dry_run=True)
    assert result["total_items"] >= 50
    assert result["errors"] == []
```

---

## Detailed Design

### Script: scripts/migrate_backlog.py (NEW)

**Location:** `scripts/migrate_backlog.py`

```python
"""Migrate backlog.md entries to WORK-{id}.md files.

E2-151: Phase A.2 of M6-WorkCycle migration.

Usage:
    python scripts/migrate_backlog.py --dry-run  # Preview
    python scripts/migrate_backlog.py            # Execute
"""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "lib"))
from scaffold import scaffold_template

PROJECT_ROOT = Path(__file__).parent.parent


def parse_backlog_entry(text: str) -> dict:
    """Parse a single backlog entry from markdown."""
    result = {}

    # Header: ### [PRIORITY] ID: Title
    header_match = re.match(r"### \[(\w+)\] ([\w-]+): (.+)", text)
    if header_match:
        result["priority"] = header_match.group(1).lower()
        result["id"] = header_match.group(2)
        result["title"] = header_match.group(3).strip()

    # Fields: - **Field:** value
    for line in text.split("\n"):
        if line.startswith("- **"):
            match = re.match(r"- \*\*(\w+):\*\* (.+)", line)
            if match:
                field = match.group(1).lower()
                value = match.group(2).strip()
                result[field] = value

    return result


def map_to_work_schema(entry: dict) -> dict:
    """Map backlog entry to work file schema."""
    return {
        "id": entry.get("id"),
        "title": entry.get("title", "Untitled"),
        "status": "active",  # All migrated items start active
        "priority": entry.get("priority", "medium"),
        "current_node": "backlog",  # Start in backlog node
        "spawned_by": entry.get("spawned_by"),
        "milestone": entry.get("milestone"),
        "context": entry.get("context", ""),
    }


def migrate_backlog(dry_run: bool = False) -> dict:
    """Run migration from backlog.md to work files."""
    backlog_path = PROJECT_ROOT / "docs" / "pm" / "backlog.md"
    content = backlog_path.read_text(encoding="utf-8-sig")

    # Split into entries (### [...)
    entries = re.split(r"(?=### \[\w+\])", content)

    results = {"migrated": [], "skipped": [], "errors": [], "total_items": 0}

    for entry_text in entries:
        if not entry_text.strip().startswith("### ["):
            continue

        # Skip complete/closed items
        if "status:** complete" in entry_text.lower():
            continue

        entry = parse_backlog_entry(entry_text)
        if not entry.get("id"):
            continue

        results["total_items"] += 1
        work = map_to_work_schema(entry)

        if dry_run:
            results["migrated"].append(work["id"])
            continue

        try:
            scaffold_template("work_item", backlog_id=work["id"], title=work["title"])
            results["migrated"].append(work["id"])
        except Exception as e:
            results["errors"].append(f"{work['id']}: {e}")

    return results
```

### Field Mapping

| Backlog Field | Work File Field | Transformation |
|---------------|-----------------|----------------|
| Header `[PRIORITY]` | `priority` | lowercase |
| Header ID | `id` | direct |
| Header Title | `title` | direct |
| `**Status:**` | ignored | always "active" |
| `**Context:**` | `## Context` section | direct |
| `**spawned_by:**` | `spawned_by` | direct |
| `**Milestone:**` | `milestone` | direct |

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| All migrated = active | status: active | Items in backlog.md are by definition not complete |
| current_node = backlog | backlog | New items start at backlog node in DAG |
| Skip complete items | Filter out | Already in archive, don't duplicate |
| Dry-run default | --dry-run flag | Safe preview before execution |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Missing ID in header | Skip entry | Test 1 |
| Complete status | Skip (don't migrate) | Test 3 |
| Special characters in title | scaffold.py handles slug | Existing |
| Duplicate ID | PreToolUse hook blocks (E2-141) | Existing |

---

## Implementation Steps

### Step 1: Write Tests
- [ ] Create `tests/test_backlog_migration.py` with 3 tests from TDD section
- [ ] Run pytest - verify tests fail (RED)

### Step 2: Create Migration Script
- [ ] Create `scripts/migrate_backlog.py` with parse/map/migrate functions
- [ ] Tests 1, 2 pass (GREEN)

### Step 3: Dry-Run Verification
- [ ] Run `python scripts/migrate_backlog.py --dry-run`
- [ ] Verify output shows 58 items to migrate
- [ ] Test 3 passes (GREEN)

### Step 4: Execute Migration (DECISION POINT)
- [ ] Confirm with operator before running full migration
- [ ] Run `python scripts/migrate_backlog.py`
- [ ] Verify 58 WORK-*.md files created in `docs/work/active/`

### Step 5: Post-Migration Verification
- [ ] All tests pass
- [ ] Validate sample work files: `just validate docs/work/active/WORK-E2-004-*.md`
- [ ] Run `just update-status-slim` - verify work items appear

---

## Verification

- [ ] 3 tests pass in `tests/test_backlog_migration.py`
- [ ] Dry-run shows 58 items
- [ ] Work files validate successfully
- [ ] `get_work_items()` returns migrated items

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Duplicate IDs | Low | PreToolUse hook blocks (E2-141) |
| Partial migration failure | Medium | Dry-run first, atomic per-item |
| Work files fail validation | Low | Template tested in E2-150 |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 106 | 2025-12-23 | - | in_progress | Plan created |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `scripts/migrate_backlog.py` | parse_backlog_entry, map_to_work_schema, migrate_backlog | [ ] | |
| `tests/test_backlog_migration.py` | 3 tests pass | [ ] | |
| `docs/work/active/WORK-E2-*.md` | 58+ files created | [ ] | |
| `scripts/README.md` | Documents migration script | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_backlog_migration.py -v
# Expected: 3 passed

ls docs/work/active/ | wc -l
# Expected: ~58 files
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
- [ ] WHY captured
- [ ] Work files created and valid
- [ ] Dry-run verified before execution

---

## References

- **ADR-039:** Work-Item-as-File Architecture
- **E2-150:** Work-Item Infrastructure (prerequisite)
- **INV-024:** Work-Item-as-File Architecture validation
- **Session 105:** M6-WorkCycle milestone definition

---
