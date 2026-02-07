---
template: implementation_plan
status: complete
date: 2026-01-04
backlog_id: E2-263
title: CycleRunner Scaffold Commands
author: Hephaestus
lifecycle_phase: plan
session: 170
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-04T20:54:25'
---
# Implementation Plan: CycleRunner Scaffold Commands

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

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

CycleRunner module will provide `build_scaffold_command(template, work_id, title)` method that delegates to existing node_cycle.py functionality, enabling post_tool_use.py hook to import from modules instead of lib/ directory.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | cycle_runner.py, test_cycle_runner.py |
| Lines of code affected | ~20 | Add method (~15) + tests (~5) |
| New files to create | 0 | Adding to existing module |
| Tests to write | 2 | Basic call, placeholder replacement |
| Dependencies | 1 | node_cycle.py (lib/) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single delegation to existing module |
| Risk of regression | Low | Adding new method, not modifying existing |
| External dependencies | Low | Uses existing node_cycle infrastructure |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 5 min | High |
| Implement method | 10 min | High |
| Update docs | 5 min | High |
| **Total** | 20 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/hooks/hooks/post_tool_use.py:766-768
from node_cycle import (
    get_node_binding, check_doc_exists, build_scaffold_command,
    extract_work_id, extract_title
)
```

**Behavior:** post_tool_use.py imports build_scaffold_command directly from lib/node_cycle.py

**Result:** Hook bypasses module architecture, violating Strangler Fig migration pattern

### Desired State

```python
# .claude/haios/modules/cycle_runner.py (new method)
def build_scaffold_command(self, template: str, work_id: str, title: str) -> str:
    """Build scaffold command from template."""
    # Delegates to node_cycle.build_scaffold_command()
```

**Behavior:** CycleRunner exposes build_scaffold_command() method that delegates to existing implementation

**Result:** E2-264 can rewire post_tool_use.py to import from CycleRunner instead of lib/

---

## Tests First (TDD)

### Test 1: Returns correctly formatted command
```python
def test_build_scaffold_command_replaces_placeholders():
    """build_scaffold_command replaces {id} and {title} placeholders."""
    from cycle_runner import CycleRunner
    from governance_layer import GovernanceLayer

    runner = CycleRunner(governance=GovernanceLayer())
    result = runner.build_scaffold_command(
        template="/new-plan {id} {title}",
        work_id="E2-263",
        title="Test Title"
    )
    assert result == "/new-plan E2-263 Test Title"
```

### Test 2: Handles template without placeholders
```python
def test_build_scaffold_command_passthrough():
    """build_scaffold_command passes through template without placeholders."""
    from cycle_runner import CycleRunner
    from governance_layer import GovernanceLayer

    runner = CycleRunner(governance=GovernanceLayer())
    result = runner.build_scaffold_command(
        template="just validate",
        work_id="E2-263",
        title="Test"
    )
    assert result == "just validate"
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/haios/modules/cycle_runner.py`
**Location:** After `_emit_phase_entered` method (end of file, line 197)

**New Method:**
```python
    def build_scaffold_command(
        self, template: str, work_id: str, title: str
    ) -> str:
        """
        Build scaffold command from template.

        Delegates to node_cycle.build_scaffold_command().

        Args:
            template: Command template with {id} and {title} placeholders
            work_id: Work item ID (e.g., "E2-263")
            title: Work item title

        Returns:
            Complete command string with placeholders replaced.
        """
        from node_cycle import build_scaffold_command as _build_scaffold_command
        return _build_scaffold_command(template, work_id, title)
```

### Call Chain Context

```
post_tool_use.py:handle_work_file_node_change()
    |
    +-> CycleRunner.build_scaffold_command()  # <-- NEW METHOD
    |       Returns: str (command)
    |
    +-> node_cycle.build_scaffold_command()   # <-- Delegated
            Returns: str (same)
```

### Function/Component Signatures

```python
def build_scaffold_command(
    self, template: str, work_id: str, title: str
) -> str:
    """
    Build scaffold command from template.

    Args:
        template: Command template (e.g., "/new-plan {id} {title}")
        work_id: Work item ID (e.g., "E2-263")
        title: Work item title

    Returns:
        Command string with {id} and {title} replaced.
    """
```

### Behavior Logic

```
template, work_id, title
    |
    +-> node_cycle.build_scaffold_command(template, work_id, title)
          |
          +-> template.replace("{id}", work_id).replace("{title}", title)
                |
                +-> Return formatted command string
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Delegation pattern | Import and call node_cycle function | Matches E2-262 pattern; single source of truth |
| No dataclass result | Return string directly | Matches existing node_cycle interface exactly |
| Lazy import | Import inside method | Matches CycleRunner pattern (check_phase_exit does same) |

### Input/Output Examples

**Example 1: Full placeholder replacement**
```
Input: template="/new-plan {id} {title}", work_id="E2-263", title="Scaffold Commands"
Output: "/new-plan E2-263 Scaffold Commands"
```

**Example 2: No placeholders**
```
Input: template="just validate", work_id="E2-263", title="Test"
Output: "just validate"
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Template without placeholders | Pass through unchanged | Test 2 |
| Empty title | Replaces with empty string | Covered by node_cycle |

### Open Questions

**Q: Should we also expose get_node_binding, check_doc_exists, extract_work_id, extract_title?**

Not in this work item. E2-264 will determine which functions need exposure. For now, build_scaffold_command is the only one explicitly mapped in INV-056.

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add test_build_scaffold_command_replaces_placeholders to test_cycle_runner.py
- [ ] Add test_build_scaffold_command_passthrough to test_cycle_runner.py
- [ ] Verify both tests fail (red)

### Step 2: Implement build_scaffold_command Method
- [ ] Add build_scaffold_command method after _emit_phase_entered (line 197)
- [ ] Delegate to node_cycle.build_scaffold_command
- [ ] Tests 1, 2 pass (green)

### Step 3: Integration Verification
- [ ] All tests pass: `pytest tests/test_cycle_runner.py -v`
- [ ] Run full test suite: `pytest tests/ -v` (no regressions)

### Step 4: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/modules/README.md` with new method

---

## Verification

- [ ] Tests pass: `pytest tests/test_cycle_runner.py -v`
- [ ] **MUST:** `.claude/haios/modules/README.md` updated
- [ ] Demo: Import and call build_scaffold_command with test data

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| node_cycle import path differs | Low | sys.path already set up in CycleRunner |
| E2-264 not yet rewired | Low | This work item adds method; E2-264 does the rewiring |

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

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/cycle_runner.py` | build_scaffold_command method exists | [ ] | |
| `tests/test_cycle_runner.py` | 2 new tests for build_scaffold_command | [ ] | |
| `.claude/haios/modules/README.md` | **MUST:** Documents build_scaffold_command method | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_cycle_runner.py -v
# Expected: Tests pass
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
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.

---

## References

- INV-056: Hook-to-Module Migration Investigation
- E2-262: MemoryBridge Learning Extraction (pattern to follow)
- `.claude/lib/node_cycle.py`: Source implementation
- `.claude/haios/modules/cycle_runner.py`: Target module
- Memory 80685: Original mapping finding

---
