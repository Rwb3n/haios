---
template: implementation_plan
status: complete
date: 2025-12-23
backlog_id: E2-155
title: "Node-Exit-Gates"
author: Hephaestus
lifecycle_phase: plan
session: 105
version: "1.5"
generated: 2025-12-21
last_updated: 2025-12-23T20:14:34
---
# Implementation Plan: Node-Exit-Gates

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

When an agent attempts to change a work file's `current_node` field, the PreToolUse hook warns (soft gate) if exit criteria for the current node are not met, preventing premature phase transitions.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `pre_tool_use.py`, `node-cycle-bindings.yaml` |
| Lines of code affected | ~100 | New exit gate handler + config extensions |
| New files to create | 1 | `tests/test_exit_gates.py` |
| Tests to write | 8 | Exit criteria detection, warnings, edge cases |
| Dependencies | 1 | `node_cycle.py` (E2-154) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | PreToolUse hook, work files, node_cycle.py |
| Risk of regression | Low | Adding new check, existing checks unchanged |
| External dependencies | Low | File system only |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Config + Library | 20 min | High |
| Hook Integration | 20 min | High |
| Tests | 20 min | High |
| Verification | 15 min | High |
| **Total** | ~1.5 hours | High |

---

## Current State vs Desired State

### Current State

```markdown
# Agent edits work file to change node
current_node: discovery → plan

# No validation occurs
# Agent can skip directly from discovery to close
# Exit criteria not enforced
```

**Behavior:** Node transitions are unrestricted. Agent can change `current_node` to any value.

**Result:** Phases can be skipped. Incomplete work can progress. No enforcement of workflow.

### Desired State

```markdown
# Agent attempts to change node
current_node: discovery → plan

# PreToolUse hook checks:
# 1. Detects edit touches current_node field
# 2. Reads current node from work file
# 3. Looks up exit criteria for "discovery" node
# 4. Checks: investigation status = complete?
# 5. Checks: findings section has content?
# 6. Checks: spawned items exist?
# 7. If ANY fails: WARN (soft gate) with guidance
# 8. If ALL pass: ALLOW silently
```

**Behavior:** Node transitions are soft-gated. Agent receives warning if exit criteria not met.

**Result:** Agent is reminded of incomplete work. Phases are channeled properly. Workflow integrity maintained (soft enforcement per memory concept 76855).

---

## Tests First (TDD)

**Test file:** `tests/test_exit_gates.py`

### Test 1: Load Exit Criteria from Config
```python
def test_load_exit_criteria_returns_list():
    """Config file has exit_criteria for discovery node."""
    from node_cycle import get_exit_criteria
    criteria = get_exit_criteria("discovery")
    assert isinstance(criteria, list)
    assert len(criteria) > 0
```

### Test 2: Get Exit Criteria for Node Without Criteria
```python
def test_get_exit_criteria_returns_empty_for_backlog():
    """Backlog node has no exit criteria."""
    from node_cycle import get_exit_criteria
    criteria = get_exit_criteria("backlog")
    assert criteria == []
```

### Test 3: Detect Node Exit Attempt
```python
def test_detect_node_exit_from_edit():
    """Detects when Edit changes current_node field."""
    from node_cycle import detect_node_exit_attempt
    old_string = "current_node: discovery"
    new_string = "current_node: plan"
    result = detect_node_exit_attempt(old_string, new_string)
    assert result == ("discovery", "plan")
```

### Test 4: Detect No Exit Attempt
```python
def test_detect_node_exit_returns_none_for_other_edits():
    """Returns None if edit doesn't touch current_node."""
    from node_cycle import detect_node_exit_attempt
    old_string = "title: Old Title"
    new_string = "title: New Title"
    result = detect_node_exit_attempt(old_string, new_string)
    assert result is None
```

### Test 5: Check Exit Criteria - All Pass
```python
def test_check_exit_criteria_passes_when_all_met(tmp_path):
    """Returns empty list when all criteria met."""
    from node_cycle import check_exit_criteria
    # Setup: Create investigation file with complete content
    inv_file = tmp_path / "docs" / "investigations" / "INVESTIGATION-E2-999-test.md"
    inv_file.parent.mkdir(parents=True)
    inv_file.write_text("---\nstatus: complete\n---\n## Findings\nReal content here")

    failures = check_exit_criteria("discovery", "E2-999", tmp_path)
    assert failures == []
```

### Test 6: Check Exit Criteria - Some Fail
```python
def test_check_exit_criteria_returns_failures(tmp_path):
    """Returns list of unmet criteria."""
    from node_cycle import check_exit_criteria
    # Setup: No investigation file exists
    failures = check_exit_criteria("discovery", "E2-999", tmp_path)
    assert len(failures) > 0
    assert any("investigation" in f.lower() for f in failures)
```

### Test 7: Build Warning Message
```python
def test_build_exit_gate_warning():
    """Builds user-friendly warning message."""
    from node_cycle import build_exit_gate_warning
    failures = ["Investigation status not complete", "Findings section empty"]
    warning = build_exit_gate_warning("discovery", "plan", failures)
    assert "discovery" in warning
    assert "plan" in warning
    assert "Investigation status" in warning
```

### Test 8: Plan Exit Criteria Check
```python
def test_plan_exit_criteria_checks_status(tmp_path):
    """Plan node checks for approved status."""
    from node_cycle import check_exit_criteria
    # Setup: Create plan file with draft status
    plan_file = tmp_path / "docs" / "plans" / "PLAN-E2-999-test.md"
    plan_file.parent.mkdir(parents=True)
    plan_file.write_text("---\nstatus: draft\n---\n## Tests First\ntest content")

    failures = check_exit_criteria("plan", "E2-999", tmp_path)
    assert any("approved" in f.lower() for f in failures)
```

---

## Detailed Design

### Architecture Overview (from INV-022)

Two changes:
1. **Extend node-cycle-bindings.yaml** with `exit_criteria` per node
2. **Add PreToolUse handler** for exit gate checking

### Config Extension: Exit Criteria

**File:** `.claude/config/node-cycle-bindings.yaml`

Add `exit_criteria` to each node:

```yaml
nodes:
  backlog:
    cycle: null
    scaffold: []
    exit_criteria: []  # Manual decision only

  discovery:
    cycle: investigation-cycle
    scaffold:
      - type: investigation
        command: '/new-investigation {id} "{title}"'
        pattern: "docs/investigations/INVESTIGATION-{id}-*.md"
    exit_criteria:
      - type: file_status
        pattern: "docs/investigations/INVESTIGATION-{id}-*.md"
        field: status
        value: complete
        message: "Investigation status not complete"
      - type: section_content
        pattern: "docs/investigations/INVESTIGATION-{id}-*.md"
        section: "## Findings"
        min_length: 50
        message: "Findings section is empty or placeholder"

  plan:
    cycle: plan-cycle
    scaffold:
      - type: plan
        command: '/new-plan {id} "{title}"'
        pattern: "docs/plans/PLAN-{id}-*.md"
    exit_criteria:
      - type: file_status
        pattern: "docs/plans/PLAN-{id}-*.md"
        field: status
        value: approved
        message: "Plan status not approved (still draft)"

  implement:
    cycle: implementation-cycle
    scaffold: []
    exit_criteria: []  # Tests verified via /close command

  close:
    cycle: closure-cycle
    scaffold: []
    exit_criteria: []  # DoD verified via /close command
```

### New Functions in node_cycle.py

**File:** `.claude/lib/node_cycle.py`

```python
def get_exit_criteria(node: str) -> list:
    """Get exit criteria for a node.

    Returns list of criterion dicts, or empty list if none.
    """
    binding = get_node_binding(node)
    if not binding:
        return []
    return binding.get("exit_criteria", [])


def detect_node_exit_attempt(old_string: str, new_string: str) -> Optional[tuple]:
    """Detect if edit is changing current_node field.

    Returns (from_node, to_node) tuple if changing, None otherwise.
    """
    old_match = re.search(r'current_node:\s*(\w+)', old_string)
    new_match = re.search(r'current_node:\s*(\w+)', new_string)

    if not old_match or not new_match:
        return None

    old_node = old_match.group(1)
    new_node = new_match.group(1)

    if old_node != new_node:
        return (old_node, new_node)
    return None


def check_exit_criteria(node: str, work_id: str, base_path: Path = Path(".")) -> list:
    """Check all exit criteria for a node.

    Returns list of failure messages (empty if all pass).
    """
    criteria = get_exit_criteria(node)
    failures = []

    for criterion in criteria:
        result = _check_single_criterion(criterion, work_id, base_path)
        if result:
            failures.append(result)

    return failures


def _check_single_criterion(criterion: dict, work_id: str, base_path: Path) -> Optional[str]:
    """Check a single exit criterion.

    Returns failure message or None if passed.
    """
    criterion_type = criterion.get("type")
    pattern = criterion.get("pattern", "").replace("{id}", work_id)
    message = criterion.get("message", "Exit criterion not met")

    # Find file matching pattern
    matches = list(base_path.glob(pattern))
    if not matches:
        return f"Required file not found: {pattern}"

    file_path = matches[0]
    content = file_path.read_text(encoding="utf-8")

    if criterion_type == "file_status":
        field = criterion.get("field", "status")
        expected = criterion.get("value")
        match = re.search(rf'^{field}:\s*(\w+)', content, re.MULTILINE)
        if not match or match.group(1) != expected:
            return message

    elif criterion_type == "section_content":
        section = criterion.get("section", "")
        min_length = criterion.get("min_length", 1)
        # Find section content
        section_match = re.search(rf'{re.escape(section)}\n+(.*?)(?=\n## |\Z)',
                                  content, re.DOTALL)
        if not section_match:
            return message
        section_content = section_match.group(1).strip()
        if len(section_content) < min_length:
            return message

    return None


def build_exit_gate_warning(from_node: str, to_node: str, failures: list) -> str:
    """Build user-friendly warning message."""
    lines = [
        f"[EXIT GATE] Transitioning from '{from_node}' to '{to_node}' with unmet criteria:",
    ]
    for failure in failures:
        lines.append(f"  - {failure}")
    lines.append("Consider completing these before proceeding.")
    return "\n".join(lines)
```

### PreToolUse Integration

**File:** `.claude/hooks/hooks/pre_tool_use.py`

Add new check in `handle()` function after `_check_backlog_id_uniqueness`:

```python
# Check Write/Edit for governance
if tool_name in ("Write", "Edit"):
    # ... existing checks ...

    # Exit gate check (E2-155)
    result = _check_exit_gate(file_path, old_string, new_string)
    if result:
        return result

    # Path governance - only for new files
    result = _check_path_governance(file_path)
    # ...
```

**New Function:**

```python
def _check_exit_gate(file_path: str, old_string: str, new_string: str) -> Optional[dict]:
    """
    Check exit criteria when changing work file current_node (E2-155).

    Soft gate: warns but allows operation if criteria unmet.
    """
    if not file_path or not old_string or not new_string:
        return None

    # Only check work files
    normalized = file_path.replace("\\", "/")
    if "docs/work/" not in normalized or not Path(file_path).name.startswith("WORK-"):
        return None

    # Only check if current_node is being changed
    if "current_node:" not in old_string and "current_node:" not in new_string:
        return None

    try:
        # Import node_cycle library
        lib_dir = Path(__file__).parent.parent.parent / "lib"
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))

        from node_cycle import (
            detect_node_exit_attempt, check_exit_criteria,
            build_exit_gate_warning, extract_work_id
        )

        # Detect if this is a node transition
        transition = detect_node_exit_attempt(old_string, new_string)
        if not transition:
            return None

        from_node, to_node = transition

        # Get work ID from file path
        work_id = extract_work_id(Path(file_path))
        if not work_id:
            return None

        # Check exit criteria for current node
        failures = check_exit_criteria(from_node, work_id)
        if not failures:
            return None  # All criteria met, allow silently

        # Build warning message (soft gate - allow with warning)
        warning = build_exit_gate_warning(from_node, to_node, failures)
        return _allow_with_warning(warning)

    except Exception:
        pass  # On error, allow operation

    return None
```

### Behavior Logic

```
PreToolUse(Edit on WORK-*.md)
    |
    +-> _check_exit_gate(path, old_string, new_string)
            |
            ├─ Is work file? (WORK-*.md in docs/work/)
            |       NO → return None (allow)
            |
            ├─ Edit touches current_node?
            |       NO → return None (allow)
            |
            ├─ Detect transition (from_node, to_node)
            |       NO change → return None (allow)
            |
            ├─ Check exit criteria for from_node
            |       ALL PASS → return None (allow silently)
            |
            └─ Build warning, return _allow_with_warning()
                    (soft gate: allows but shows warning)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Soft gate vs hard gate | Soft (warn) | Memory concept 76855: soft gates preferred over hard blocks |
| PreToolUse not PostToolUse | Check before edit | Gate should happen BEFORE transition, not after |
| Config-based criteria | YAML definitions | Allows criteria to change without code changes |
| Only check from_node | Exit criteria on current | Validates leaving a node, not entering |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| File not found | Return file not found message | Test 6 |
| No exit criteria for node | Return empty list (allow) | Test 2 |
| Edit doesn't touch current_node | Skip check entirely | Test 4 |
| Non-work file | Skip check entirely | Implicit |
| Malformed frontmatter | Return failure message | Implicit |

### Open Questions

**Q: Should we block or warn for exit gate violations?**

ANSWER: Warn only (soft gate). Per memory concept 76855, soft gates are preferred. Agent sees warning but can proceed if needed.

**Q: What about implement → close transition?**

ANSWER: No exit criteria defined. DoD is verified by `/close` command (E2-152), not exit gate.

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_exit_gates.py` with 8 tests from Tests First section
- [ ] Verify all tests fail (red) - functions don't exist yet

### Step 2: Extend Config with Exit Criteria
- [ ] Edit `.claude/config/node-cycle-bindings.yaml`
- [ ] Add `exit_criteria` field to each node
- [ ] Tests 1, 2 can now run (config exists)

### Step 3: Add Exit Gate Functions to node_cycle.py
- [ ] Add `get_exit_criteria()` function
- [ ] Add `detect_node_exit_attempt()` function
- [ ] Add `check_exit_criteria()` and `_check_single_criterion()` functions
- [ ] Add `build_exit_gate_warning()` function
- [ ] Tests 1-8 pass (green)

### Step 4: Integrate PreToolUse Hook
- [ ] Add `_check_exit_gate()` function to `pre_tool_use.py`
- [ ] Add call to `_check_exit_gate()` in `handle()` function
- [ ] Update module docstring to list Part 6

### Step 5: README Sync (MUST)
- [ ] **MUST:** Update `.claude/lib/README.md` - note exit gate functions added
- [ ] **MUST:** Update `.claude/hooks/README.md` - list Part 6
- [ ] **MUST:** Update `.claude/config/README.md` - document exit_criteria schema

### Step 6: Demo Verification
- [ ] Edit a work file's current_node from discovery → plan
- [ ] Verify warning appears if criteria not met
- [ ] Verify no warning if criteria all met

---

## Verification

- [ ] 8 tests pass in `tests/test_exit_gates.py`
- [ ] Full test suite passes (no regressions)
- [ ] **MUST:** All READMEs current (lib, hooks, config)
- [ ] Demo: Edit work file current_node → soft gate warning appears

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hook breaks existing PreToolUse | High | Only check work files, others pass through |
| Config parsing error | Medium | Return empty list on error (allow operation) |
| Performance overhead | Low | Only runs for Edit on work files |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 108 | 2025-12-23 | - | Planning | Full design created |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/config/node-cycle-bindings.yaml` | `exit_criteria` on discovery, plan nodes | [ ] | |
| `.claude/lib/node_cycle.py` | 4 new functions for exit gates | [ ] | |
| `.claude/hooks/hooks/pre_tool_use.py` | `_check_exit_gate()` function | [ ] | |
| `tests/test_exit_gates.py` | 8 tests exist and pass | [ ] | |
| `.claude/lib/README.md` | Lists exit gate functions | [ ] | |
| `.claude/hooks/README.md` | Lists Part 6 exit gates | [ ] | |
| `.claude/config/README.md` | Documents exit_criteria schema | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_exit_gates.py -v
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
- [ ] **MUST:** READMEs updated (lib, hooks, config)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- **INV-022:** Work-Cycle-DAG Unified Architecture (design source)
- **E2-154:** Scaffold-on-Entry Hook (sister implementation)
- **Memory 76855:** Soft gates preferred over hard blocks

---
