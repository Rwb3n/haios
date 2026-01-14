---
template: implementation_plan
status: complete
date: 2025-12-23
backlog_id: E2-150
title: "Work-Item-Infrastructure"
author: Hephaestus
lifecycle_phase: plan
session: 105
version: "1.5"
generated: 2025-12-21
last_updated: 2025-12-23T18:13:44
---
# Implementation Plan: Work-Item-Infrastructure

@docs/README.md
@docs/epistemic_state.md
@docs/investigations/INVESTIGATION-INV-022-work-cycle-dag-unified-architecture.md
@docs/investigations/INVESTIGATION-INV-024-work-item-as-file-architecture.md

---

## Goal

Create infrastructure for work-item files: template, /new-work command, and status.py scanning - enabling work items to be tracked as individual files instead of backlog.md entries.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | validate.py, scaffold.py, status.py |
| Lines of code affected | ~150 | Additions only |
| New files to create | 2 | work_item.md template, new-work.md command |
| Tests to write | 6 | 2 per module |
| Dependencies | 0 | No new imports needed |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Med | validate.py, scaffold.py, status.py |
| Risk of regression | Low | Adding new template, not changing existing |
| External dependencies | Low | No APIs, just file system |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Template + Registry | 15 min | High |
| /new-work command | 10 min | High |
| status.py scanning | 20 min | High |
| Tests | 15 min | High |
| **Total** | 60 min | |

---

## Current State vs Desired State

### Current State

**No work_item template exists.** Work items are tracked in `docs/pm/backlog.md` (1,224 lines, 62 items).

Status.py scans:
```python
# .claude/lib/status.py:502-508
governed_paths = [
    PROJECT_ROOT / "docs" / "checkpoints",
    PROJECT_ROOT / "docs" / "plans",
    PROJECT_ROOT / "docs" / "investigations",
    PROJECT_ROOT / "docs" / "ADR",
    PROJECT_ROOT / "docs" / "reports",
]
```

**Behavior:** Work items scattered across backlog.md, plans, investigations.

**Result:** Status staleness - backlog.md says "pending" while plan says "complete".

### Desired State

**work_item template + governed path + command:**

```python
# .claude/lib/status.py - ADD to governed_paths
governed_paths = [
    ...existing paths...,
    PROJECT_ROOT / "docs" / "work" / "active",
    PROJECT_ROOT / "docs" / "work" / "blocked",
    PROJECT_ROOT / "docs" / "work" / "archive",
]
```

**Behavior:** Work items as individual files with status in frontmatter.

**Result:** Single source of truth for work item status.

---

## Tests First (TDD)

### Test 1: work_item in template registry
```python
def test_work_item_template_in_registry():
    from validate import get_template_registry
    registry = get_template_registry()
    assert "work_item" in registry
    assert "id" in registry["work_item"]["required_fields"]
    assert "current_node" in registry["work_item"]["required_fields"]
```

### Test 2: work_item validation passes for prototype
```python
def test_work_item_validation_passes():
    from validate import validate_template
    from pathlib import Path
    work_file = Path("docs/work/active/WORK-E2-143.md")
    result = validate_template(str(work_file))
    assert result["valid"] is True
```

### Test 3: scaffold generates work_item path
```python
def test_scaffold_work_item_path():
    from scaffold import generate_output_path
    path = generate_output_path("work_item", backlog_id="E2-999", title="Test Item")
    assert "docs/work/active/WORK-E2-999-test-item.md" in path
```

### Test 4: scaffold creates work_item file
```python
def test_scaffold_work_item_creates_file(tmp_path, monkeypatch):
    from scaffold import scaffold_template
    # Uses temp directory
    result = scaffold_template("work_item", backlog_id="E2-999", title="Test")
    assert "WORK-E2-999" in result
```

### Test 5: status.py scans docs/work/active
```python
def test_get_live_files_includes_work_items():
    from status import get_live_files
    files = get_live_files()
    work_files = [f for f in files if "docs/work/" in f["path"]]
    # Prototype WORK-E2-143.md should be found
    assert any("WORK-E2-143" in f["path"] for f in work_files)
```

### Test 6: get_work_items returns active work
```python
def test_get_work_items_returns_active():
    from status import get_work_items
    items = get_work_items()
    assert isinstance(items, list)
    # Should find prototype
    active = [i for i in items if i.get("status") == "active"]
    assert len(active) >= 1
```

---

## Detailed Design

### Component 1: work_item.md Template

**File:** `.claude/templates/work_item.md` (NEW)

Based on INV-022 Work File Schema v2 and prototype WORK-E2-143.md:

```yaml
---
template: work_item
id: {{BACKLOG_ID}}
title: "{{TITLE}}"
status: active
owner: Hephaestus
created: {{DATE}}
closed: null
milestone: null
priority: medium
effort: medium
category: implementation
spawned_by: null
spawned_by_investigation: null
blocked_by: []
blocks: []
enables: []
related: []
current_node: backlog
node_history:
  - node: backlog
    entered: {{TIMESTAMP}}
    exited: null
cycle_docs: {}
memory_refs: []
documents:
  investigations: []
  plans: []
  checkpoints: []
version: "1.0"
generated: {{DATE}}
last_updated: {{TIMESTAMP}}
---
# WORK-{{BACKLOG_ID}}: {{TITLE}}

@docs/README.md
@docs/epistemic_state.md

---

## Context

[Problem and root cause]

---

## Current State

Work item in BACKLOG node. Awaiting prioritization.

---

## Deliverables

- [ ] [Deliverable 1]
- [ ] [Deliverable 2]

---

## History

### {{DATE}} - Created (Session {{SESSION}})
- Initial creation

---

## References

- [Related documents]
```

### Component 2: validate.py Registry Entry

**File:** `.claude/lib/validate.py`
**Location:** Add to `get_template_registry()` after line 131

**Add:**
```python
        "work_item": {
            "required_fields": ["template", "status", "id", "title", "current_node"],
            "optional_fields": [
                "owner", "created", "closed", "milestone", "priority", "effort",
                "category", "spawned_by", "spawned_by_investigation", "blocked_by",
                "blocks", "enables", "related", "node_history", "cycle_docs",
                "memory_refs", "documents", "version",
            ],
            "allowed_status": ["active", "blocked", "complete", "archived"],
            "expected_sections": ["Context", "Current State", "Deliverables"],
        },
```

### Component 3: scaffold.py Configuration

**File:** `.claude/lib/scaffold.py`
**Location:** Add to `TEMPLATE_CONFIG` dict after line 59

**Add:**
```python
    "work_item": {
        "dir": "docs/work/active",
        "prefix": "WORK",
        "pattern": "{dir}/{prefix}-{backlog_id}-{slug}.md",
    },
```

### Component 4: status.py Work Item Scanning

**File:** `.claude/lib/status.py`
**Location 1:** Add work paths to `get_live_files()` governed_paths (line 502-508)

**Change:**
```python
governed_paths = [
    PROJECT_ROOT / "docs" / "checkpoints",
    PROJECT_ROOT / "docs" / "plans",
    PROJECT_ROOT / "docs" / "investigations",
    PROJECT_ROOT / "docs" / "ADR",
    PROJECT_ROOT / "docs" / "reports",
    PROJECT_ROOT / "docs" / "work" / "active",      # NEW
    PROJECT_ROOT / "docs" / "work" / "blocked",     # NEW
    PROJECT_ROOT / "docs" / "work" / "archive",     # NEW
]
```

**Location 2:** Add new function `get_work_items()` after `get_spawn_map()`

```python
def get_work_items() -> list[dict[str, Any]]:
    """Scan docs/work/ for work item files.

    Returns:
        List of work item dicts with id, title, status, current_node, priority.
    """
    work_dirs = [
        PROJECT_ROOT / "docs" / "work" / "active",
        PROJECT_ROOT / "docs" / "work" / "blocked",
        PROJECT_ROOT / "docs" / "work" / "archive",
    ]

    items = []
    for dir_path in work_dirs:
        if not dir_path.exists():
            continue

        for file_path in dir_path.glob("WORK-*.md"):
            try:
                content = file_path.read_text(encoding="utf-8-sig")
                metadata = _parse_yaml_frontmatter(content)

                items.append({
                    "id": metadata.get("id"),
                    "title": metadata.get("title"),
                    "status": metadata.get("status"),
                    "current_node": metadata.get("current_node"),
                    "priority": metadata.get("priority"),
                    "path": str(file_path.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                })
            except Exception:
                continue

    return items
```

### Component 5: /new-work Command

**File:** `.claude/commands/new-work.md` (NEW)

```markdown
# generated: 2025-12-23
# Create Work Item

**MUST** use this command when creating files in `docs/work/`.

Arguments: `<backlog_id> <title>`

## Create Work Item

```bash
just work <backlog_id> "<title>"
```

Example:
```bash
just work E2-160 "New Feature Implementation"
# Creates: docs/work/active/WORK-E2-160-new-feature-implementation.md
```

## Allowed Field Values

| Field | Allowed Values |
|-------|----------------|
| status | `active`, `blocked`, `complete`, `archived` |
| current_node | `backlog`, `discovery`, `design`, `plan`, `implement`, `close` |
| priority | `high`, `medium`, `low` |
```

### Component 6: justfile Recipe

**File:** `justfile`
**Location:** Add recipe near other scaffold recipes

```just
# Create work item file
work backlog_id title:
    just scaffold work_item {{backlog_id}} "{{title}}"
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| status field location | docs/work/{status}/ directory | Directory = status prevents drift (move file = change status) |
| current_node required | Yes | Core DAG tracking field from INV-022 |
| node_history format | List of dicts with node/entered/exited | Enables audit trail of work progression |
| Prefix naming | WORK-{id} | Consistent with PLAN-, INV-, ADR- patterns |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Work file in wrong directory | Validation warns (status vs directory mismatch) | Future: E2-151 |
| Missing node_history | Default to empty list, current_node sufficient | Test 1 |
| Duplicate IDs | scaffold.py doesn't prevent (future: E2-141) | Future: E2-141 |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create tests/test_work_item.py with 6 tests from TDD section
- [ ] Run pytest tests/test_work_item.py - verify all fail (red)

### Step 2: Create work_item Template
- [ ] Create .claude/templates/work_item.md (Component 1)
- [ ] Test 3 (scaffold path) may still fail (scaffold.py not updated)

### Step 3: Update validate.py Registry
- [ ] Add work_item entry to get_template_registry() (Component 2)
- [ ] Test 1, Test 2 pass (green)

### Step 4: Update scaffold.py Configuration
- [ ] Add work_item to TEMPLATE_CONFIG (Component 3)
- [ ] Test 3, Test 4 pass (green)

### Step 5: Update status.py Scanning
- [ ] Add work paths to governed_paths (Component 4, Location 1)
- [ ] Add get_work_items() function (Component 4, Location 2)
- [ ] Test 5, Test 6 pass (green)

### Step 6: Create /new-work Command
- [ ] Create .claude/commands/new-work.md (Component 5)
- [ ] Add justfile recipe (Component 6)
- [ ] Manual test: `just work E2-TEST "Test Work Item"` creates file

### Step 7: Integration Verification
- [ ] All 6 tests pass
- [ ] Run full test suite: `pytest tests/ -v` (no regressions)
- [ ] `just update-status-slim` - verify /new-work appears in commands

### Step 8: README Sync (MUST)
- [ ] **MUST:** Update .claude/templates/README.md - add work_item
- [ ] **MUST:** Update .claude/commands/README.md - add /new-work
- [ ] **MUST:** Update docs/work/README.md or create if needed

---

## Verification

- [ ] Tests pass (6 tests in test_work_item.py)
- [ ] **MUST:** All READMEs current (templates, commands, docs/work)
- [ ] /new-work command discoverable in haios-status-slim.json

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Prototype WORK-E2-143.md fails validation | Low | Update prototype to match final template |
| Node history parsing complex | Low | current_node is required, node_history optional |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 106 | 2025-12-23 | - | in_progress | Plan created, starting implementation |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/templates/work_item.md` | Template with INV-022 schema v2 | [ ] | |
| `.claude/lib/validate.py` | work_item in registry | [ ] | |
| `.claude/lib/scaffold.py` | work_item in TEMPLATE_CONFIG | [ ] | |
| `.claude/lib/status.py` | get_work_items() function, work paths in governed_paths | [ ] | |
| `.claude/commands/new-work.md` | Command file exists | [ ] | |
| `justfile` | `work` recipe exists | [ ] | |
| `tests/test_work_item.py` | 6 tests pass | [ ] | |
| `.claude/templates/README.md` | work_item listed | [ ] | |
| `.claude/commands/README.md` | /new-work listed | [ ] | |
| `docs/work/README.md` | Directory documented | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_work_item.py -v
# Expected: 6 tests passed

just work E2-TEST "Verification Test"
# Expected: File created at docs/work/active/WORK-E2-TEST-verification-test.md
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
- [ ] **MUST:** READMEs updated in all modified directories
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- **ADR-039:** Work-Item-as-File Architecture
- **INV-022:** Work-Cycle-DAG Unified Architecture (schema v2)
- **INV-024:** Work-Item-as-File Architecture (validation)
- **Session 105:** M6-WorkCycle definition

---
