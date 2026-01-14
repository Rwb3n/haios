---
template: implementation_plan
status: complete
date: 2025-12-24
backlog_id: E2-172
title: Fix YAML Timestamp Injection
author: Hephaestus
lifecycle_phase: plan
session: 113
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-24T20:26:22'
---
# Implementation Plan: Fix YAML Timestamp Injection

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

PostToolUse hook's `_add_yaml_timestamp()` will use proper YAML parsing to preserve nested structures like `node_history` arrays.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/hooks/hooks/post_tool_use.py` |
| Lines of code affected | ~40 | Lines 207-267 |
| New files to create | 0 | - |
| Tests to write | 2 | Test nested YAML preservation |
| Dependencies | 0 | No downstream consumers to update |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single function change |
| Risk of regression | Med | All YAML files flow through this |
| External dependencies | Low | Only PyYAML (already used) |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 10 min | High |
| Implementation | 15 min | High |
| **Total** | 25 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/hooks/hooks/post_tool_use.py:225-229
for line in yaml_lines:
    if ":" in line and not line.strip().startswith("#"):
        key = line.split(":")[0].strip()
        yaml_order.append(key)
        yaml_dict[key] = line
```

**Behavior:** Parses each line with `:` as a separate key-value pair.

**Result:** Nested YAML structures like `node_history:` arrays get corrupted - each nested line becomes a top-level entry.

### Desired State

```python
# .claude/hooks/hooks/post_tool_use.py:220-240 (new)
import yaml

yaml_content = "\n".join(lines[1:yaml_end])
fm = yaml.safe_load(yaml_content) or {}

# Update timestamps
if "generated" not in fm:
    fm["generated"] = current_date
fm["last_updated"] = timestamp

# Rebuild with proper YAML serialization
new_fm = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True)
```

**Behavior:** Uses proper YAML parsing that understands nested structures.

**Result:** `node_history` and other nested structures preserved correctly.

---

## Tests First (TDD)

### Test 1: Nested YAML preserved
```python
def test_yaml_timestamp_preserves_nested_structures(tmp_path):
    """Verify node_history arrays survive timestamp injection."""
    from hooks.post_tool_use import _add_yaml_timestamp

    test_file = tmp_path / "test.md"
    content = """---
current_node: plan
node_history:
  - node: backlog
    entered: 2025-12-24T10:00:00
    exited: 2025-12-24T11:00:00
  - node: plan
    entered: 2025-12-24T11:00:00
    exited: null
---
# Content"""
    test_file.write_text(content)
    lines = content.split("\n")

    _add_yaml_timestamp(test_file, lines, 10, "2025-12-24", "2025-12-24T12:00:00")

    result = test_file.read_text()
    assert "node: backlog" in result
    assert "node: plan" in result
    assert result.count("- node:") == 2  # Both entries preserved
```

### Test 2: Flat YAML still works
```python
def test_yaml_timestamp_flat_fields(tmp_path):
    """Verify simple flat YAML still works."""
    from hooks.post_tool_use import _add_yaml_timestamp

    test_file = tmp_path / "test.md"
    content = """---
template: checkpoint
status: active
---
# Content"""
    test_file.write_text(content)
    lines = content.split("\n")

    _add_yaml_timestamp(test_file, lines, 3, "2025-12-24", "2025-12-24T12:00:00")

    result = test_file.read_text()
    assert "template: checkpoint" in result
    assert "status: active" in result
    assert "generated: 2025-12-24" in result
    assert "last_updated: 2025-12-24T12:00:00" in result
```

---

## Detailed Design

<!-- REQUIRED: Document HOW the implementation works, not just WHAT it does.
     Future agents should be able to implement from this section alone.
     This section bridges the gap between tests (WHAT) and steps (HOW).

     MUST INCLUDE (per Session 88 enhancement):
     1. Actual current code that will be changed (copy from source)
     2. Exact diff/change to be made
     3. Function signature details with context
     4. Input/output examples with REAL data from the system -->

### Exact Code Change

<!-- REQUIRED: Show the actual code, not pseudocode -->

**File:** `[path/to/file.py]`
**Location:** Lines X-Y in `function_name()`

**Current Code:**
```python
# [file:line-range] - Copy exact current implementation
        existing_code = """
            SELECT ...
        """
```

**Changed Code:**
```python
# [file:line-range] - Show exact target implementation
        modified_code = """
            SELECT ...
            WHERE new_condition   # <-- NEW
        """
```

**Diff:**
```diff
         existing_line
+        new_line_added
-        old_line_removed
```

### Call Chain Context

<!-- Show where this code fits in the larger system -->

```
caller_function()
    |
    +-> THIS_FUNCTION()     # <-- What we're changing
    |       Returns: [Type]
    |
    +-> downstream_function()
```

### Function/Component Signatures

```python
# Current signature (if changing) or target signature (if new)
def function_name(param: Type) -> ReturnType:
    """
    [One-line description]

    Args:
        param: [Description and constraints]

    Returns:
        [Description of return value]

    Raises:
        [Exceptions and when they occur]
    """
```

### Behavior Logic

<!-- Use flowchart showing CURRENT (buggy) vs FIXED behavior -->

**Current Flow (if buggy):**
```
Input → [Step causing problem] → Wrong Output
```

**Fixed Flow:**
```
Input → [Step 1] → [Decision Point?]
                      ├─ YES → [Path A] → Output
                      └─ NO  → [Path B] → Output
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| [Decision point] | [What was chosen] | [WHY this choice - this is the most important part] |

### Input/Output Examples

<!-- REQUIRED: Use REAL data from the system, not hypothetical examples -->

**Before Fix (with real data):**
```
Run 1: function(param=X)
  Returns: [actual current output from system]
  Problem: [why this is wrong]
```

**After Fix (expected):**
```
Run 1: function(param=X)
  Returns: [expected correct output]
  Improvement: [what's better]
```

**Real Example with Current Data:**
```
Current system state:
  - [Query database or read files to get actual numbers]
  - [Show real IDs, counts, or values]

After fix:
  - [Expected new behavior with same real data]
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| [Edge case] | [How it's handled] | Test N |

### Open Questions

<!-- Surface any uncertainties discovered during design -->

**Q: [Question about behavior or design]**

[Answer based on code analysis, or mark as "TBD - verify during implementation"]

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add tests to appropriate test file
- [ ] Verify all tests fail (red)

### Step 2: [First Implementation Slice]
- [ ] [Specific code change]
- [ ] Tests [N, M] pass (green)

### Step 3: [Second Implementation Slice]
- [ ] [Specific code change]
- [ ] Tests [X, Y] pass (green)

### Step 4: Integration Verification
- [ ] All tests pass
- [ ] Run full test suite (no regressions)

### Step 5: README Sync (MUST)
- [ ] **MUST:** Update README.md in each directory with new/changed files
- [ ] **MUST:** Update parent directory READMEs if structure changed
- [ ] **MUST:** Verify README content matches actual file state

### Step 6: Consumer Verification (MUST for migrations/refactors)
<!-- When migrating, renaming, or moving code, ALL consumers must be updated -->
- [ ] **MUST:** Grep for references to migrated/renamed code
- [ ] **MUST:** Update all consumers (commands, skills, hooks, docs)
- [ ] **MUST:** Verify no stale references remain

**Consumer Discovery Pattern:**
```bash
# Find all references to the old path/name
Grep(pattern="old_path|OldName", path=".", glob="**/*.{md,py,json}")
```

> **Anti-pattern prevented:** "Ceremonial Completion" - code migrated but consumers still reference old location (see epistemic_state.md)

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk 1] | [High/Medium/Low] | [Mitigation strategy] |

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
| `[path/to/implementation.py]` | [Function X exists, does Y] | [ ] | |
| `[tests/test_file.py]` | [Tests exist and cover cases] | [ ] | |
| `[modified_dir/README.md]` | **MUST:** Reflects actual files present | [ ] | |
| `[parent_dir/README.md]` | **MUST:** Updated if structure changed | [ ] | |
| `Grep: old_path\|OldName` | **MUST:** Zero stale references (migrations only) | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest [test_file] -v
# Expected: X tests passed
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

- [Related ADR or spec]
- [Related checkpoint]

---
