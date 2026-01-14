---
template: implementation_plan
status: complete
date: 2025-12-22
backlog_id: E2-114
title: "Spawn Tree Query"
author: Hephaestus
lifecycle_phase: done
session: 99
memory_refs: [77147, 77148, 77149, 77150, 77151]
version: "1.5"
generated: 2025-12-21
last_updated: 2025-12-22T19:29:29
---
# Implementation Plan: Spawn Tree Query

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

A `just spawns <id>` recipe that visualizes what work items a given investigation or session spawned (and what that spawned, recursively).

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `justfile`, `.claude/lib/README.md` |
| Lines of code affected | ~20 | Justfile recipe + README update |
| New files to create | 2 | `.claude/lib/spawn.py`, `tests/test_lib_spawn.py` |
| Tests to write | 5-8 | Core traversal + edge cases |
| Dependencies | 0 | No modules import this (new standalone) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only justfile recipe entry point |
| Risk of regression | Low | No existing code modified |
| External dependencies | Low | Just filesystem (docs/*.md) |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests + Module | 30 min | High |
| Justfile + Docs | 10 min | High |
| **Total** | 40 min | High |

---

## Current State vs Desired State

### Current State

**SKIPPED:** New feature - no existing spawn query capability.

Current state: `spawned_by:` field exists in YAML frontmatter of docs (plans, investigations, checkpoints, ADRs) but no tool queries this relationship.

Example from `docs/investigations/INVESTIGATION-INV-011-work-item-as-file-architecture.md`:
```yaml
spawned_by: Session-84
```

### Desired State

```bash
$ just spawns INV-017
INV-017: Observability Gap Analysis
├── E2-099: Vitals Approaching 100% Bug
├── E2-102: Execute Heartbeat Scheduler Setup
└── E2-112: Investigation Agent

$ just spawns Session-84
Session-84
├── INV-011: Work Item as File Architecture
├── E2-099: Vitals Approaching 100% Bug
└── ...
```

**Behavior:** Query `spawned_by:` field across all doc types, build tree, format output.

**Result:** Operators can see what work emerged from investigations/sessions.

---

## Tests First (TDD)

### Test 1: Parse spawned_by from frontmatter
```python
def test_parse_spawned_by_field():
    content = "---\nspawned_by: INV-017\ntitle: Test\n---"
    result = parse_yaml_frontmatter(content)
    assert result.get('spawned_by') == 'INV-017'
```

### Test 2: Find children by spawned_by
```python
def test_find_children_of_parent(tmp_path):
    # Create test files with spawned_by: INV-017
    (tmp_path / "plans" / "PLAN-E2-099.md").write_text("---\nspawned_by: INV-017\nbacklog_id: E2-099\n---")
    (tmp_path / "plans" / "PLAN-E2-102.md").write_text("---\nspawned_by: INV-017\nbacklog_id: E2-102\n---")
    children = find_children("INV-017", docs_path=tmp_path)
    assert set(children) == {"E2-099", "E2-102"}
```

### Test 3: Build spawn tree recursively
```python
def test_build_spawn_tree(tmp_path):
    # INV-017 spawns E2-099, E2-099 spawns nothing
    (tmp_path / "PLAN-E2-099.md").write_text("---\nspawned_by: INV-017\nbacklog_id: E2-099\n---")
    tree = build_spawn_tree("INV-017", docs_path=tmp_path)
    assert tree == {"INV-017": {"E2-099": {}}}
```

### Test 4: No spawns returns empty tree
```python
def test_no_spawns():
    tree = build_spawn_tree("NONEXISTENT")
    assert tree == {"NONEXISTENT": {}}
```

### Test 5: Format tree output
```python
def test_format_tree_output():
    tree = {"INV-017": {"E2-099": {}, "E2-102": {}}}
    output = format_tree(tree)
    assert "INV-017" in output
    assert "E2-099" in output
```

---

## Detailed Design

### New Module: `.claude/lib/spawn.py`

```python
"""Spawn tree query - visualizes what work items spawned from a source.

Traverses spawned_by relationships across plans, investigations, checkpoints.
"""

from pathlib import Path
import re
from typing import Any

PROJECT_ROOT = Path(__file__).parent.parent.parent
DOCS_PATH = PROJECT_ROOT / "docs"

def parse_yaml_frontmatter(content: str) -> dict[str, Any]:
    """Extract YAML frontmatter from markdown content."""
    # Reuse pattern from cascade.py
    match = re.match(r'^---\s*\n([\s\S]*?)\n---', content)
    if not match:
        return {}
    yaml_str = match.group(1)
    result = {}
    for line in yaml_str.split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            result[key.strip()] = value.strip().strip('"\'')
    return result


def find_children(parent_id: str, docs_path: Path = None) -> list[dict]:
    """Find all items that have spawned_by: parent_id."""
    docs_path = docs_path or DOCS_PATH
    children = []

    # Scan all markdown files in docs/
    for md_file in docs_path.rglob("*.md"):
        try:
            content = md_file.read_text(encoding='utf-8')
        except Exception:
            continue

        fm = parse_yaml_frontmatter(content)
        spawned_by = fm.get('spawned_by', '')

        if spawned_by == parent_id:
            # Get ID from backlog_id or filename
            item_id = fm.get('backlog_id') or fm.get('investigation_id') or md_file.stem
            title = fm.get('title', '')
            children.append({'id': item_id, 'title': title, 'file': str(md_file)})

    return children


def build_spawn_tree(root_id: str, docs_path: Path = None, max_depth: int = 5) -> dict:
    """Build recursive spawn tree from root_id."""
    if max_depth <= 0:
        return {root_id: {}}

    children = find_children(root_id, docs_path)
    subtree = {}
    for child in children:
        child_tree = build_spawn_tree(child['id'], docs_path, max_depth - 1)
        subtree.update(child_tree)

    return {root_id: subtree}


def format_tree(tree: dict, prefix: str = "", is_last: bool = True) -> str:
    """Format tree as ASCII art."""
    lines = []
    for root_id, children in tree.items():
        lines.append(f"{root_id}")
        child_items = list(children.items())
        for i, (child_id, grandchildren) in enumerate(child_items):
            is_last_child = (i == len(child_items) - 1)
            connector = "└── " if is_last_child else "├── "
            child_prefix = "    " if is_last_child else "│   "
            lines.append(f"{prefix}{connector}{child_id}")
            if grandchildren:
                subtree = {child_id: grandchildren}
                sublines = format_tree(subtree, prefix + child_prefix, is_last_child)
                # Skip first line (already printed child_id)
                for subline in sublines.split('\n')[1:]:
                    if subline:
                        lines.append(subline)
    return '\n'.join(lines)
```

### Justfile Recipe

```just
# Show spawn tree for an ID (what did it spawn?)
spawns id:
    python -c "import sys; sys.path.insert(0, '.claude/lib'); from spawn import build_spawn_tree, format_tree; print(format_tree(build_spawn_tree('{{id}}')))"
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Reuse frontmatter parsing | Copy pattern from cascade.py | Consistency, tested pattern |
| Scan all doc types | rglob("*.md") in docs/ | spawned_by appears in plans, investigations, checkpoints, ADRs |
| Max depth limit | 5 levels | Prevent infinite recursion, sufficient for realistic hierarchies |
| ASCII tree format | ├── └── style | Standard, readable, terminal-friendly |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No spawns | Return `{id: {}}` | Test 4 |
| Circular reference | max_depth prevents infinite loop | Implicit |
| ID not found | Return empty tree | Test 4 |
| Session-NN format | Works as string match | Part of Test 2 variants |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_lib_spawn.py`
- [ ] Add 5 tests from TDD section
- [ ] Verify all tests fail (red) - module doesn't exist yet

### Step 2: Create spawn.py Module
- [ ] Create `.claude/lib/spawn.py` with functions from Detailed Design
- [ ] Tests 1-5 pass (green)

### Step 3: Add Justfile Recipe
- [ ] Add `spawns` recipe to justfile
- [ ] Manual test: `just spawns INV-017`

### Step 4: Integration Verification
- [ ] All tests pass
- [ ] Run full test suite (no regressions)
- [ ] Test with real data: `just spawns Session-84`

### Step 5: README Sync (MUST)
- [ ] **MUST:** Update `.claude/lib/README.md` - add spawn.py to module list

### Step 6: Consumer Verification
**SKIPPED:** New standalone module, no migrations or renames.

---

## Verification

- [ ] Tests pass (`pytest tests/test_lib_spawn.py -v`)
- [ ] **MUST:** `.claude/lib/README.md` updated
- [ ] Manual verification: `just spawns INV-017`

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Performance on large docs/ | Low | rglob is fast, ~100 files |
| Inconsistent spawned_by format | Low | String match handles Session-84, INV-017, E2-099 |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 99 | 2025-12-22 | - | draft | Plan created |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/spawn.py` | find_children, build_spawn_tree, format_tree exist | [x] | ~180 LOC |
| `tests/test_lib_spawn.py` | 5+ tests covering core functions | [x] | 10 tests |
| `.claude/lib/README.md` | spawn.py listed in module table | [x] | Added to Phase 2 table |
| `justfile` | `spawns` recipe exists | [x] | Line 146-147 |

**Verification Commands:**
```bash
pytest tests/test_lib_spawn.py -v
# Result: 10 passed in 0.17s

just spawns INV-017
# Result:
# INV-017
# +-- E2-102
# +-- E2-103

just spawns Session-84
# Result:
# Session-84
# +-- E2-099
# +-- INV-011
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | All 4 files verified |
| Test output pasted above? | Yes | See above |
| Any deviations from plan? | Yes | Added use_ascii=True for Windows encoding compatibility |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (376 total, 10 new)
- [x] WHY captured (memory refs: 77147-77151)
- [x] **MUST:** `.claude/lib/README.md` updated
- [x] Ground Truth Verification completed above

---

## References

- ADR-033: Work Item Lifecycle
- INV-017: Observability Gap Analysis (spawns example target)
- E2-076: DAG Governance Architecture (related to spawn relationships)

---
