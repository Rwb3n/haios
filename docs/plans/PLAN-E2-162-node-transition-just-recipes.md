---
template: implementation_plan
status: complete
date: 2025-12-24
backlog_id: E2-162
title: "Node Transition Just Recipes"
author: Hephaestus
lifecycle_phase: plan
session: 111
version: "1.5"
generated: 2025-12-21
last_updated: 2025-12-24T19:51:02
---
# Implementation Plan: Node Transition Just Recipes

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

## Goal

Just recipes `node` and `link` that update work file frontmatter (current_node, node_history, cycle_docs, documents) without manual Read+Edit dance.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `.claude/lib/work_item.py`, `justfile` |
| Lines of code affected | ~84 + ~10 | `wc -l` on work_item.py (84), justfile additions |
| New files to create | 0 | Extending existing module |
| Tests to write | 4 | 2 for update_node, 2 for add_document_link |
| Dependencies | 1 | `tests/test_work_item.py` will import new functions |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only work_item.py and justfile |
| Risk of regression | Low | Adding new functions, not modifying existing |
| External dependencies | Low | No external APIs, just file operations |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 10 min | High |
| Python functions | 15 min | High |
| Just recipes | 5 min | High |
| **Total** | 30 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/lib/work_item.py:19-84 - Existing functions
def find_work_file(backlog_id: str) -> Optional[Path]
def update_work_file_status(path: Path, new_status: str) -> None
def update_work_file_closed_date(path: Path, date: str) -> None
def move_work_file_to_archive(path: Path) -> Path
```

**Behavior:** No functions for node transitions or document linking. Agent must manually Read+Edit work files.

**Result:** Error-prone, verbose, inconsistent frontmatter updates.

### Desired State

```python
# .claude/lib/work_item.py - New functions
def update_node(path: Path, new_node: str) -> None:
    """Update current_node and append to node_history."""

def add_document_link(path: Path, doc_type: str, doc_path: str) -> None:
    """Add document to cycle_docs and documents section."""
```

**Behavior:** `just node E2-162 plan` and `just link E2-162 plan docs/plans/PLAN-E2-162.md` update frontmatter atomically.

**Result:** One-command node transitions, proper history tracking.

---

## Tests First (TDD)

### Test 1: update_node updates current_node
```python
def test_update_node_changes_current_node(tmp_path):
    work_file = tmp_path / "WORK-TEST-001.md"
    work_file.write_text("""---
current_node: backlog
node_history:
  - node: backlog
    entered: 2025-12-24T10:00:00
    exited: null
---""")
    update_node(work_file, "plan")
    content = work_file.read_text()
    assert "current_node: plan" in content
```

### Test 2: update_node appends to history
```python
def test_update_node_appends_history(tmp_path):
    work_file = tmp_path / "WORK-TEST-001.md"
    work_file.write_text("""---
current_node: backlog
node_history:
  - node: backlog
    entered: 2025-12-24T10:00:00
    exited: null
---""")
    update_node(work_file, "plan")
    content = work_file.read_text()
    assert "node: plan" in content
    assert content.count("- node:") == 2
```

### Test 3: add_document_link adds to documents
```python
def test_add_document_link_adds_plan(tmp_path):
    work_file = tmp_path / "WORK-TEST-001.md"
    work_file.write_text("""---
documents:
  plans: []
---""")
    add_document_link(work_file, "plan", "docs/plans/PLAN-TEST.md")
    content = work_file.read_text()
    assert "PLAN-TEST.md" in content
```

### Test 4: add_document_link updates cycle_docs
```python
def test_add_document_link_updates_cycle_docs(tmp_path):
    work_file = tmp_path / "WORK-TEST-001.md"
    work_file.write_text("""---
current_node: plan
cycle_docs: {}
---""")
    add_document_link(work_file, "plan", "docs/plans/PLAN-TEST.md")
    content = work_file.read_text()
    assert "plan:" in content.split("cycle_docs:")[1].split("---")[0]
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/lib/work_item.py`
**Location:** Append after line 84 (end of existing module)

**New Code:**
```python
def update_node(path: Path, new_node: str) -> None:
    """
    Update work file to new DAG node with history tracking.

    Updates current_node field and appends new entry to node_history,
    marking the previous entry's exited timestamp.

    Args:
        path: Path to work file
        new_node: Target node (backlog, plan, implement, check, done)
    """
    import yaml
    from datetime import datetime

    content = path.read_text(encoding="utf-8")
    # Split frontmatter
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid frontmatter in {path}")

    fm = yaml.safe_load(parts[1])
    now = datetime.now().isoformat()

    # Mark previous node as exited
    if fm.get("node_history"):
        fm["node_history"][-1]["exited"] = now

    # Update current node
    fm["current_node"] = new_node

    # Append new history entry
    fm.setdefault("node_history", []).append({
        "node": new_node,
        "entered": now,
        "exited": None
    })

    # Rebuild content
    new_fm = yaml.dump(fm, default_flow_style=False, sort_keys=False)
    path.write_text(f"---\n{new_fm}---{parts[2]}", encoding="utf-8")


def add_document_link(path: Path, doc_type: str, doc_path: str) -> None:
    """
    Link a document to the work file.

    Updates both cycle_docs (current node's doc) and documents section.

    Args:
        path: Path to work file
        doc_type: Document type (plan, investigation, checkpoint)
        doc_path: Path to the document being linked
    """
    import yaml

    content = path.read_text(encoding="utf-8")
    parts = content.split("---", 2)
    if len(parts) < 3:
        raise ValueError(f"Invalid frontmatter in {path}")

    fm = yaml.safe_load(parts[1])

    # Map doc_type to documents key (plural)
    type_map = {"plan": "plans", "investigation": "investigations", "checkpoint": "checkpoints"}
    docs_key = type_map.get(doc_type, f"{doc_type}s")

    # Update documents section
    fm.setdefault("documents", {}).setdefault(docs_key, [])
    if doc_path not in fm["documents"][docs_key]:
        fm["documents"][docs_key].append(doc_path)

    # Update cycle_docs for current node
    current_node = fm.get("current_node", "unknown")
    fm.setdefault("cycle_docs", {})[current_node] = doc_path

    new_fm = yaml.dump(fm, default_flow_style=False, sort_keys=False)
    path.write_text(f"---\n{new_fm}---{parts[2]}", encoding="utf-8")
```

### Call Chain Context

```
just node E2-162 plan
    |
    +-> python -c "...update_node(path, 'plan')"
    |       Modifies: work file frontmatter
    |
    +-> Triggers PostToolUse hook (last_updated timestamp)
```

### Function Signatures

```python
def update_node(path: Path, new_node: str) -> None:
    """Update current_node and append to node_history with timestamps."""

def add_document_link(path: Path, doc_type: str, doc_path: str) -> None:
    """Add document to cycle_docs and documents section."""
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| YAML parsing | PyYAML | Already a dependency, handles nested structures |
| History tracking | Append-only | Preserves full audit trail, matches work_item template spec |
| cycle_docs overwrite | Yes | Each node has one primary document |
| documents append | Yes | Multiple documents per type allowed |

### Input/Output Examples

**Real Example - E2-162 Work File:**
```yaml
# BEFORE: just node E2-162 plan
current_node: backlog
node_history:
  - node: backlog
    entered: 2025-12-24T09:41:53
    exited: null

# AFTER: just node E2-162 plan
current_node: plan
node_history:
  - node: backlog
    entered: 2025-12-24T09:41:53
    exited: 2025-12-24T19:30:00
  - node: plan
    entered: 2025-12-24T19:30:00
    exited: null
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Empty node_history | Create new list | Test 2 |
| Duplicate doc_path | Skip if already exists | Test 3 |
| Unknown doc_type | Use pluralized form | Test 4 |

### Justfile Recipes

```just
# Move work item to node
node id node:
    python -c "import sys; sys.path.insert(0, '.claude/lib'); from work_item import find_work_file, update_node; p = find_work_file('{{id}}'); update_node(p, '{{node}}') if p else print(f'Not found: {{id}}')"

# Link document to work item
link id type path:
    python -c "import sys; sys.path.insert(0, '.claude/lib'); from work_item import find_work_file, add_document_link; p = find_work_file('{{id}}'); add_document_link(p, '{{type}}', '{{path}}') if p else print(f'Not found: {{id}}')"
```

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add 4 tests to `tests/test_work_item.py`
- [ ] Verify all tests fail (red)

### Step 2: Implement update_node
- [ ] Add `update_node()` function to `.claude/lib/work_item.py`
- [ ] Tests 1, 2 pass (green)

### Step 3: Implement add_document_link
- [ ] Add `add_document_link()` function to `.claude/lib/work_item.py`
- [ ] Tests 3, 4 pass (green)

### Step 4: Add Just Recipes
- [ ] Add `node` recipe to `justfile`
- [ ] Add `link` recipe to `justfile`
- [ ] Manual test: `just node E2-162 plan`

### Step 5: Integration Verification
- [ ] All tests pass
- [ ] Run full test suite (no regressions)

### Step 6: README Sync (MUST)
- [ ] **MUST:** Update `.claude/lib/README.md` with new functions
- [ ] Verify README content matches actual file state

### Step 7: Use the tools (dogfood)
- [ ] Use `just node E2-162 plan` to move this work item
- [ ] Use `just link E2-162 plan docs/plans/PLAN-E2-162-node-transition-just-recipes.md`

---

## Verification

- [ ] Tests pass (`pytest tests/test_work_item.py -v`)
- [ ] **MUST:** `.claude/lib/README.md` updated
- [ ] Just recipes work: `just node`, `just link`

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| YAML reordering | Low | Use sort_keys=False in yaml.dump |
| Invalid frontmatter | Low | Validate 3-part split before parsing |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 114 | 2025-12-24 | - | In Progress | Plan created |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/work_item.py` | `update_node` and `add_document_link` exist | [ ] | |
| `tests/test_work_item.py` | 4 new tests exist and pass | [ ] | |
| `.claude/lib/README.md` | Documents new functions | [ ] | |
| `justfile` | `node` and `link` recipes exist | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_work_item.py -v
# Expected: 4+ tests passed
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [ ] | |
| Test output pasted above? | [ ] | |
| Any deviations from plan? | [ ] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- E2-162 Work File: `docs/work/active/WORK-E2-162-just-recipes-for-node-transitions.md`
- Session 113: Governance workflow enforcement
- ADR-039: Work-Item-as-File Architecture

---
