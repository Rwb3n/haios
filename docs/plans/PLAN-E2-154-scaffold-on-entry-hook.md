---
template: implementation_plan
status: complete
date: 2025-12-23
backlog_id: E2-154
title: "Scaffold-on-Entry-Hook"
author: Hephaestus
lifecycle_phase: plan
session: 107
version: "1.5"
generated: 2025-12-21
last_updated: 2025-12-23T19:59:53
---
# Implementation Plan: Scaffold-on-Entry-Hook

@docs/README.md
@docs/epistemic_state.md
@docs/investigations/INVESTIGATION-INV-022-work-cycle-dag-unified-architecture.md
@docs/work/active/WORK-E2-154-scaffold-on-entry-hook-inv-022-phase-2.md

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

When a work file's `current_node` field changes, the PostToolUse hook automatically scaffolds all cycle documents for that node based on a configurable node-cycle binding, ensuring no workflow steps can be skipped.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `post_tool_use.py`, work file template |
| Lines of code affected | ~150 | New scaffold detection function + config loader |
| New files to create | 3 | `node_cycle.py`, `node-cycle-bindings.yaml`, test file |
| Tests to write | 8 | Detection, config loading, scaffold logic, edge cases |
| Dependencies | 2 | scaffold.py (for command execution), work_item.py |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | High | PostToolUse hook, scaffold commands, work files |
| Risk of regression | Medium | Adding new hook handler, existing flow unchanged |
| External dependencies | Low | File system only, uses existing /new-* commands |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Config + Library | 30 min | High |
| Hook Integration | 30 min | Medium |
| Tests | 30 min | High |
| Verification | 15 min | High |
| **Total** | ~2 hours | Medium |

---

## Current State vs Desired State

### Current State

```markdown
# Work file current_node changes
current_node: backlog → plan

# Agent must manually:
1. Remember to run /new-plan
2. Create plan file
3. Update work file cycle_docs field
```

**Behavior:** Node transitions require manual document scaffolding.

**Result:** Steps can be skipped. Agent may forget to create cycle documents. No enforcement of workflow.

### Desired State

```markdown
# Work file current_node changes
current_node: backlog → plan

# PostToolUse hook automatically:
1. Detects current_node field changed in work file
2. Looks up node-cycle binding for "plan" node
3. Checks if plan file exists (Glob)
4. If not exists: Executes /new-plan {id} "{title}"
5. Updates work file cycle_docs field with path
6. Updates node_history with entry timestamp
```

**Behavior:** Node transitions automatically scaffold all required cycle documents.

**Result:** Steps cannot be skipped. Agent is channeled through complete workflow. Cycle documents always exist.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

**Test file:** `tests/test_node_cycle.py`

### Test 1: Load Node-Cycle Bindings
```python
def test_load_bindings_returns_dict():
    """Config file loads and returns node bindings."""
    bindings = load_node_cycle_bindings()
    assert isinstance(bindings, dict)
    assert "plan" in bindings
    assert "discovery" in bindings
```

### Test 2: Get Binding for Node
```python
def test_get_binding_for_plan_node():
    """Plan node has correct scaffold config."""
    binding = get_node_binding("plan")
    assert binding["scaffold"][0]["type"] == "plan"
    assert binding["scaffold"][0]["command"].startswith("/new-plan")
```

### Test 3: Detect Node Change
```python
def test_detect_node_change_returns_new_node():
    """Detects current_node field changed in work file."""
    # Mock: old content had current_node: backlog
    # Mock: new content has current_node: plan
    result = detect_node_change(old_content, new_content)
    assert result == "plan"
```

### Test 4: Detect Node Change No Change
```python
def test_detect_node_change_returns_none_if_same():
    """Returns None if node unchanged."""
    result = detect_node_change(content, content)
    assert result is None
```

### Test 5: Check Doc Exists
```python
def test_check_doc_exists_returns_path(tmp_path):
    """Returns path if doc exists matching pattern."""
    plan = tmp_path / "docs" / "plans" / "PLAN-E2-154-test.md"
    plan.parent.mkdir(parents=True)
    plan.write_text("test")
    result = check_doc_exists("docs/plans/PLAN-E2-154-*.md", tmp_path)
    assert result is not None
```

### Test 6: Check Doc Not Exists
```python
def test_check_doc_exists_returns_none_if_missing(tmp_path):
    """Returns None if no doc matches pattern."""
    result = check_doc_exists("docs/plans/PLAN-E2-999-*.md", tmp_path)
    assert result is None
```

### Test 7: Build Scaffold Command
```python
def test_build_scaffold_command():
    """Builds correct /new-plan command."""
    cmd = build_scaffold_command("/new-plan {id} \"{title}\"", "E2-154", "Test Title")
    assert cmd == '/new-plan E2-154 "Test Title"'
```

### Test 8: Update Work File Cycle Docs
```python
def test_update_cycle_docs_field(tmp_path):
    """Updates work file cycle_docs field."""
    work_file = tmp_path / "WORK-E2-154.md"
    work_file.write_text("---\ncycle_docs: {}\n---\n# Test")
    update_cycle_docs(work_file, "plan", "docs/plans/PLAN-E2-154-test.md")
    content = work_file.read_text()
    assert "plan: docs/plans/PLAN-E2-154-test.md" in content
```

---

## Detailed Design

### Architecture Overview (from INV-022)

Three new components:

1. **Node-Cycle Binding Config** (`.claude/config/node-cycle-bindings.yaml`)
2. **Node-Cycle Library** (`.claude/lib/node_cycle.py`)
3. **PostToolUse Integration** (add Part 7 to `hooks/post_tool_use.py`)

### New File 1: Node-Cycle Bindings Config

**File:** `.claude/config/node-cycle-bindings.yaml`

```yaml
# Node-Cycle Bindings (INV-022)
# Maps lifecycle nodes to their cycle skills and scaffold requirements

nodes:
  backlog:
    cycle: null
    scaffold: []

  discovery:
    cycle: investigation-cycle
    scaffold:
      - type: investigation
        command: "/new-investigation {id} \"{title}\""
        pattern: "docs/investigations/INVESTIGATION-{id}-*.md"

  plan:
    cycle: plan-cycle
    scaffold:
      - type: plan
        command: "/new-plan {id} \"{title}\""
        pattern: "docs/plans/PLAN-{id}-*.md"

  implement:
    cycle: implementation-cycle
    scaffold: []  # Plan already exists, tests created during DO phase

  close:
    cycle: closure-cycle
    scaffold: []  # Inline in work file
```

### New File 2: Node-Cycle Library

**File:** `.claude/lib/node_cycle.py`

```python
"""Node-Cycle binding operations for scaffold-on-entry (E2-154)."""
from pathlib import Path
from typing import Optional, Dict, Any
import re
import yaml

CONFIG_PATH = Path(".claude/config/node-cycle-bindings.yaml")


def load_node_cycle_bindings() -> Dict[str, Any]:
    """Load node-cycle bindings from config file."""
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    return config.get("nodes", {})


def get_node_binding(node: str) -> Optional[Dict[str, Any]]:
    """Get binding config for a specific node."""
    bindings = load_node_cycle_bindings()
    return bindings.get(node)


def detect_node_change(old_content: str, new_content: str) -> Optional[str]:
    """
    Detect if current_node field changed in work file.

    Returns new node name if changed, None otherwise.
    """
    old_match = re.search(r'^current_node:\s*(\w+)', old_content, re.MULTILINE)
    new_match = re.search(r'^current_node:\s*(\w+)', new_content, re.MULTILINE)

    if not new_match:
        return None

    old_node = old_match.group(1) if old_match else None
    new_node = new_match.group(1)

    if old_node != new_node:
        return new_node
    return None


def check_doc_exists(pattern: str, base_path: Path = Path(".")) -> Optional[Path]:
    """Check if a document matching pattern exists."""
    matches = list(base_path.glob(pattern))
    return matches[0] if matches else None


def build_scaffold_command(template: str, work_id: str, title: str) -> str:
    """Build scaffold command from template."""
    return template.replace("{id}", work_id).replace("{title}", title)


def extract_work_id(path: Path) -> Optional[str]:
    """Extract work ID from work file path."""
    match = re.search(r'WORK-((?:E2|INV|TD|V)-\d+)', path.name)
    return match.group(1) if match else None


def extract_title(content: str) -> str:
    """Extract title from work file frontmatter."""
    match = re.search(r'^title:\s*["\']?([^"\']+)["\']?', content, re.MULTILINE)
    return match.group(1).strip() if match else "Untitled"


def update_cycle_docs(path: Path, doc_type: str, doc_path: str) -> None:
    """Update cycle_docs field in work file frontmatter."""
    content = path.read_text(encoding="utf-8")
    # Find cycle_docs section and add/update entry
    if "cycle_docs: {}" in content:
        content = content.replace(
            "cycle_docs: {}",
            f"cycle_docs:\n  {doc_type}: {doc_path}"
        )
    else:
        # Append to existing cycle_docs
        content = re.sub(
            r'(cycle_docs:\n)',
            f'\\1  {doc_type}: {doc_path}\n',
            content
        )
    path.write_text(content, encoding="utf-8")
```

### PostToolUse Integration

**File:** `.claude/hooks/hooks/post_tool_use.py`
**Location:** Add Part 7 after existing handlers (~line 105)

```python
# Part 7: Scaffold-on-entry (E2-154)
scaffold_msg = _scaffold_on_node_entry(path, hook_data)
if scaffold_msg:
    messages.append(scaffold_msg)
```

**New Function:**

```python
def _scaffold_on_node_entry(path: Path, hook_data: dict) -> Optional[str]:
    """
    Detect current_node changes in work files and scaffold cycle docs.

    Part of E2-154: Scaffold-on-Entry Hook (INV-022 Phase 2).
    """
    # Only process work files
    if not path.name.startswith("WORK-") or "docs/work/" not in str(path):
        return None

    # Need old content to detect change
    tool_name = hook_data.get("tool_name", "")
    if tool_name == "Edit":
        old_content = hook_data.get("tool_input", {}).get("old_string", "")
        new_content = path.read_text(encoding="utf-8")
    else:
        # Write tool - no old content available for comparison
        return None

    # Import node_cycle library
    import sys
    sys.path.insert(0, str(Path(".claude/lib").resolve()))
    from node_cycle import (
        detect_node_change, get_node_binding, check_doc_exists,
        build_scaffold_command, extract_work_id, extract_title,
        update_cycle_docs
    )

    # Detect node change
    new_node = detect_node_change(old_content, new_content)
    if not new_node:
        return None

    # Get binding for new node
    binding = get_node_binding(new_node)
    if not binding or not binding.get("scaffold"):
        return f"Node changed to {new_node} (no scaffold required)"

    # Extract work ID and title
    work_id = extract_work_id(path)
    title = extract_title(new_content)
    if not work_id:
        return None

    # Scaffold each required doc
    scaffolded = []
    for scaffold_spec in binding["scaffold"]:
        pattern = scaffold_spec["pattern"].replace("{id}", work_id)

        # Check if doc already exists
        if check_doc_exists(pattern):
            continue

        # Build and execute scaffold command
        command = build_scaffold_command(
            scaffold_spec["command"], work_id, title
        )

        # Log the command (actual execution via Skill invocation handled by agent)
        scaffolded.append(f"{scaffold_spec['type']}: {command}")

        # Update work file cycle_docs
        # Pattern includes glob, resolve to actual path after scaffold
        update_cycle_docs(path, scaffold_spec["type"], pattern)

    if scaffolded:
        return f"Scaffold-on-entry ({new_node}): {', '.join(scaffolded)}"
    return None
```

### Behavior Logic

```
PostToolUse(Edit on WORK-*.md)
    |
    +-> _scaffold_on_node_entry(path, hook_data)
            |
            ├─ Is work file? (WORK-*.md in docs/work/)
            |       NO → return None
            |
            ├─ Detect node change (old vs new current_node)
            |       NO change → return None
            |
            ├─ Get binding for new node
            |       No scaffold → return "no scaffold required"
            |
            └─ For each scaffold spec:
                    ├─ Check if doc exists (Glob pattern)
                    |       EXISTS → skip
                    |
                    ├─ Build scaffold command
                    ├─ Log command for agent execution
                    └─ Update work file cycle_docs field
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| YAML config | External config file | Allows node bindings to be modified without code changes |
| PostToolUse not PreToolUse | Hook after edit | Need to see what node was changed TO, not gate the change |
| Log command, don't execute | Return message with command | Hook can't invoke slash commands; agent reads message and executes |
| Edit only, not Write | Require Edit tool | Need old_string to detect what changed; Write creates new files |
| update_cycle_docs | Frontmatter update | Work file tracks its scaffolded docs for later reference |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Doc already exists | Skip scaffold, no duplicate | Test 5 |
| Node with no binding | Return "no scaffold required" | Implicit |
| Work file not in docs/work/ | Skip processing | Implicit |
| Missing title in frontmatter | Use "Untitled" | extract_title default |
| Malformed current_node | Return None | detect_node_change regex |

### Open Questions

**Q: Should the hook actually execute /new-* commands or just log them?**

Log only. Hooks cannot invoke slash commands directly. The agent reads the message and executes the command. This is consistent with how other hooks provide guidance (E2-007 error capture pattern).

**Q: How to handle node transitions that skip nodes (backlog → implement)?**

Allow it - the binding only scaffolds for the target node. If an intermediate node was skipped, its docs won't be scaffolded. This is intentional: E2-155 (Node Exit Gates) will enforce proper sequencing.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_node_cycle.py` with 8 tests from Tests First section
- [ ] Verify all tests fail (red) - module doesn't exist yet

### Step 2: Create Config Directory and Bindings
- [ ] Create `.claude/config/` directory (if not exists)
- [ ] Create `.claude/config/node-cycle-bindings.yaml` with node definitions
- [ ] Tests 1, 2 setup complete (config can load)

### Step 3: Create Node-Cycle Library
- [ ] Create `.claude/lib/node_cycle.py` with all functions
- [ ] Tests 1-8 pass (green)

### Step 4: Integrate with PostToolUse Hook
- [ ] Add Part 7 call in `post_tool_use.py` handle() function
- [ ] Add `_scaffold_on_node_entry()` function
- [ ] Integration test: Edit work file current_node → hook returns scaffold message

### Step 5: README Sync (MUST)
- [ ] **MUST:** Update `.claude/lib/README.md` to list `node_cycle.py`
- [ ] **MUST:** Create `.claude/config/README.md` (new directory)
- [ ] **MUST:** Update `.claude/hooks/README.md` to document Part 7

### Step 6: Demo Verification
- [ ] Edit a work file: change `current_node: backlog` to `current_node: plan`
- [ ] Verify hook outputs scaffold message
- [ ] Execute the returned `/new-plan` command
- [ ] Verify work file `cycle_docs` field updated

---

## Verification

- [ ] 8 tests pass in `tests/test_node_cycle.py`
- [ ] Full test suite passes (no regressions)
- [ ] **MUST:** `.claude/lib/README.md` lists node_cycle.py
- [ ] **MUST:** `.claude/config/README.md` exists and documents bindings
- [ ] Demo: Edit work file current_node → scaffold message appears

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hook breaks existing PostToolUse | High | Only process WORK-*.md files, others pass through |
| Config file missing | Medium | Return empty dict, no crash |
| YAML parsing error | Medium | Catch exception, return empty |
| Circular import | Medium | Lazy import inside function |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 107 | 2025-12-23 | - | Planning | Full design created |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/config/node-cycle-bindings.yaml` | 5 nodes defined | [ ] | |
| `.claude/lib/node_cycle.py` | 8 functions exist | [ ] | |
| `.claude/hooks/hooks/post_tool_use.py` | Part 7 scaffold handler | [ ] | |
| `tests/test_node_cycle.py` | 8 tests exist and pass | [ ] | |
| `.claude/lib/README.md` | Lists node_cycle.py | [ ] | |
| `.claude/config/README.md` | Documents bindings | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_node_cycle.py -v
# Expected: 8 tests passed
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
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- **INV-022:** Work-Cycle-DAG Unified Architecture (design source)
- **INV-024:** Work-Item-as-File Architecture
- **E2-150:** Work-Item Infrastructure (work file template)
- **E2-152:** Work-Item Tooling Cutover (work_item.py)
- **E2-155:** Node Exit Gates (follow-on work)

---
