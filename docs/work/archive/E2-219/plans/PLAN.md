---
template: implementation_plan
status: complete
date: 2025-12-28
backlog_id: E2-219
title: Ground Truth Verification Parser
author: Hephaestus
lifecycle_phase: plan
session: 136
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-28T17:00:08'
---
# Implementation Plan: Ground Truth Verification Parser

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

A parser function will extract verification items from Ground Truth Verification tables in implementation plans, classifying each by type (file-check, grep-check, test-run, json-verify, human-judgment) to enable automated DoD validation.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/lib/validate.py` |
| Lines of code affected | ~80 | New function additions |
| New files to create | 0 | Adding to existing module |
| Tests to write | 6 | Based on verification types |
| Dependencies | 0 | Self-contained parser |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | New functions, no existing callers yet |
| Risk of regression | Low | Adding functions, not modifying |
| External dependencies | Low | Regex-based parsing only |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 15 min | High |
| Implementation | 20 min | High |
| **Total** | 35 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/lib/validate.py - No Ground Truth Verification parsing exists
# validate_template() validates YAML frontmatter and section structure
# but doesn't parse the Ground Truth Verification table
```

**Behavior:** Ground Truth Verification tables exist in plans but are not machine-parsed.

**Result:** DoD validation can't automate verification of plan-specific criteria.

### Desired State

```python
# .claude/lib/validate.py - New functions
def parse_ground_truth_table(content: str) -> list[dict]:
    """Extract verification items from Ground Truth Verification table."""

def classify_verification_type(file_path: str, expected_state: str) -> str:
    """Classify verification type based on patterns."""
```

**Behavior:** Parser extracts verification items and classifies them by type.

**Result:** E2-220 can use parsed items to execute automated verification.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Parse simple Ground Truth table
```python
def test_parse_ground_truth_table_basic():
    content = '''
## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/validate.py` | Function exists | [ ] | |
'''
    items = parse_ground_truth_table(content)
    assert len(items) == 1
    assert items[0]['file_path'] == '.claude/lib/validate.py'
    assert items[0]['expected_state'] == 'Function exists'
    assert items[0]['is_checked'] == False
```

### Test 2: Parse multiple items with checked/unchecked
```python
def test_parse_ground_truth_table_multiple():
    content = '''
| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `path/a.py` | A exists | [x] | Done |
| `path/b.py` | B exists | [ ] | |
'''
    items = parse_ground_truth_table(content)
    assert len(items) == 2
    assert items[0]['is_checked'] == True
    assert items[1]['is_checked'] == False
```

### Test 3: Classify file-check type
```python
def test_classify_verification_type_file_check():
    result = classify_verification_type('`.claude/lib/test.py`', 'Function X exists')
    assert result == 'file-check'
```

### Test 4: Classify grep-check type
```python
def test_classify_verification_type_grep_check():
    result = classify_verification_type('`Grep: old_pattern`', 'Zero matches')
    assert result == 'grep-check'
```

### Test 5: Classify test-run type
```python
def test_classify_verification_type_test_run():
    # Content contains pytest reference
    result = classify_verification_type('`tests/test_file.py`', '5 tests pass')
    assert result == 'test-run'
```

### Test 6: Classify json-verify type
```python
def test_classify_verification_type_json_verify():
    result = classify_verification_type('`.claude/haios-status.json`', 'Field X contains Y')
    assert result == 'json-verify'
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

**File:** `.claude/lib/validate.py`
**Location:** After `validate_template()` function (line ~515)

**New Code to Add:**
```python
def parse_ground_truth_table(content: str) -> list[dict]:
    """Parse Ground Truth Verification table from plan content.

    Extracts rows from the markdown table in the Ground Truth Verification section.

    Args:
        content: Full markdown content of implementation plan

    Returns:
        List of dicts with keys: file_path, expected_state, is_checked, notes, verification_type
    """
    items = []

    # Find the Ground Truth Verification section
    section_pattern = r"## Ground Truth Verification.*?\n(.*?)(?=\n##|\Z)"
    section_match = re.search(section_pattern, content, re.DOTALL | re.IGNORECASE)
    if not section_match:
        return items

    section_content = section_match.group(1)

    # Parse markdown table rows: | File | Expected State | Verified | Notes |
    # Skip header row (contains "File") and separator row (contains ---)
    row_pattern = r"\|\s*`([^`]+)`\s*\|\s*([^|]+)\s*\|\s*\[([x ])\]\s*\|\s*([^|]*)\|"

    for match in re.finditer(row_pattern, section_content, re.IGNORECASE):
        file_path = match.group(1).strip()
        expected_state = match.group(2).strip()
        is_checked = match.group(3).lower() == 'x'
        notes = match.group(4).strip()

        verification_type = classify_verification_type(file_path, expected_state)

        items.append({
            'file_path': file_path,
            'expected_state': expected_state,
            'is_checked': is_checked,
            'notes': notes,
            'verification_type': verification_type,
        })

    return items


def classify_verification_type(file_path: str, expected_state: str) -> str:
    """Classify verification type based on file path and expected state patterns.

    Types (from INV-042):
    - file-check: Path to file, verify existence/content
    - grep-check: Grep: pattern prefix
    - test-run: tests/ path or pytest reference
    - json-verify: .json file reference
    - human-judgment: Semantic description only

    Args:
        file_path: File path from table (may include backticks)
        expected_state: Expected state description

    Returns:
        One of: 'file-check', 'grep-check', 'test-run', 'json-verify', 'human-judgment'
    """
    # Clean file_path (remove backticks if present)
    clean_path = file_path.strip('`')

    # Grep check: starts with Grep:
    if clean_path.lower().startswith('grep:'):
        return 'grep-check'

    # JSON verify: .json file
    if clean_path.endswith('.json'):
        return 'json-verify'

    # Test run: tests/ path or pytest in expected state
    if 'tests/' in clean_path or 'test_' in clean_path:
        return 'test-run'
    if 'pytest' in expected_state.lower() or 'tests pass' in expected_state.lower():
        return 'test-run'

    # File check: has file extension (indicates actual file)
    if '.' in clean_path and not clean_path.startswith('.'):
        return 'file-check'

    # Default: human judgment for semantic descriptions
    return 'human-judgment'
```

### Call Chain Context

```
dod-validation-cycle (E2-220)
    |
    +-> read_plan_file()
    |
    +-> parse_ground_truth_table(content)  # <-- NEW
    |       Returns: list[dict] of verification items
    |
    +-> execute_verification_item(item)    # <-- E2-220
```

### Function/Component Signatures

```python
def parse_ground_truth_table(content: str) -> list[dict]:
    """Parse Ground Truth Verification table from plan content.

    Args:
        content: Full markdown content of implementation plan

    Returns:
        List of dicts with keys:
        - file_path: str - path from File column
        - expected_state: str - description from Expected State column
        - is_checked: bool - whether [x] or [ ]
        - notes: str - notes column content
        - verification_type: str - classified type
    """

def classify_verification_type(file_path: str, expected_state: str) -> str:
    """Classify verification type based on patterns.

    Args:
        file_path: File path from table
        expected_state: Expected state description

    Returns:
        One of: 'file-check', 'grep-check', 'test-run', 'json-verify', 'human-judgment'
    """
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Regex-based parsing | Use regex not YAML parser | Ground Truth is markdown table, not YAML |
| Verification type enum | 5 types from INV-042 | Based on investigation of 36 real items across 5 plans |
| Default to human-judgment | When patterns don't match | Safer to require confirmation than auto-pass |
| Return dict not dataclass | Simple dict structure | Easy to serialize, no new dependencies |

### Input/Output Examples

**Real Example (from E2-212 plan):**
```python
content = '''
## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/scaffold.py` | TEMPLATE_CONFIG has directory patterns | [ ] | |
| `Grep: WORK-.*-\*\.md` | **MUST:** Zero stale references | [ ] | |
| `tests/test_work_item.py` | 5+ tests passed | [ ] | |
'''

result = parse_ground_truth_table(content)
# Returns:
[
    {'file_path': '.claude/lib/scaffold.py', 'expected_state': 'TEMPLATE_CONFIG has directory patterns', 'is_checked': False, 'notes': '', 'verification_type': 'file-check'},
    {'file_path': 'Grep: WORK-.*-\\*\\.md', 'expected_state': '**MUST:** Zero stale references', 'is_checked': False, 'notes': '', 'verification_type': 'grep-check'},
    {'file_path': 'tests/test_work_item.py', 'expected_state': '5+ tests passed', 'is_checked': False, 'notes': '', 'verification_type': 'test-run'},
]
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No Ground Truth section | Return empty list | Implicit |
| Empty table | Return empty list | Implicit |
| Malformed row | Skip (regex won't match) | N/A |
| Checked items [x] | Set is_checked=True | Test 2 |
| Multiple tables | Only parse first (in section) | Implicit |

### Open Questions

**Q: Should we handle Verification Commands section?**

Not in this PR. E2-220 will handle command extraction and execution separately. This parser focuses on the table structure only.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_ground_truth_parser.py`
- [ ] Add 6 tests from Tests First section
- [ ] Verify all tests fail (red) - functions don't exist yet

### Step 2: Implement classify_verification_type
- [ ] Add `classify_verification_type()` to `validate.py`
- [ ] Tests 3-6 pass (green)

### Step 3: Implement parse_ground_truth_table
- [ ] Add `parse_ground_truth_table()` to `validate.py`
- [ ] Tests 1-2 pass (green)

### Step 4: Integration Verification
- [ ] All 6 tests pass
- [ ] Run full test suite (no regressions)

### Step 5: README Sync (MUST)
- [ ] **SKIPPED:** No README changes needed - adding functions to existing module

### Step 6: Consumer Verification (MUST for migrations/refactors)
- [ ] **SKIPPED:** New functions, no consumers to update yet (E2-220 will be first consumer)

---

## Verification

- [ ] Tests pass
- [ ] **SKIPPED:** READMEs - no new files, adding to existing module
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Regex misses edge cases | Low | Test with real plan data from E2-212 |
| Table format varies | Low | 5 sampled plans all had identical format |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 136 | 2025-12-28 | - | PLAN | Initial plan created |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/validate.py` | `parse_ground_truth_table()` function exists | [x] | Lines 565-606 |
| `.claude/lib/validate.py` | `classify_verification_type()` function exists | [x] | Lines 518-562 |
| `tests/test_ground_truth_parser.py` | 6 tests exist and pass | [x] | 11 tests (6 planned + 5 additional) |

**Verification Commands:**
```bash
# Actual output:
pytest tests/test_ground_truth_parser.py -v
# Result: 11 passed in 0.14s
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | |
| Test output pasted above? | Yes | |
| Any deviations from plan? | Yes | Added 5 extra tests for edge cases, added handling for .claude/ paths |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (11 passed in 0.14s)
- [x] WHY captured (memory concept 79942)
- [x] **SKIPPED:** READMEs - no new files created
- [x] **SKIPPED:** Consumer verification - new functions, no consumers yet
- [x] All traced files complete
- [x] Ground Truth Verification completed above

---

## References

- Spawned by: INV-042 (Machine-Checked DoD Gates)
- Design source: `docs/work/archive/INV-042/investigations/001-machine-checked-dod-gates.md`
- Template: `.claude/templates/implementation_plan.md:347-393`
- Blocked by: Nothing
- Blocks: E2-220 (dod-validation-cycle integration)

---
