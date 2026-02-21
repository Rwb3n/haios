---
template: implementation_plan
plan_version: "2.0"
status: draft
date: {{DATE}}
backlog_id: {{BACKLOG_ID}}
title: "{{TITLE}}"
author: Hephaestus
lifecycle_phase: plan
session: {{SESSION}}
generated: {{DATE}}
last_updated: {{TIMESTAMP}}

input_contract:
  - field: work_item
    path: "docs/work/active/{{BACKLOG_ID}}/WORK.md"
    required: true
  - field: source_files_exist
    verify: "all paths in WORK.md source_files exist on disk"
    required: true

output_contract:
  - field: layer_0_complete
    verify: "Layer 0 tables have no placeholder rows"
  - field: layer_1_complete
    verify: "Layer 1 has concrete code blocks, not pseudocode"
  - field: layer_2_complete
    verify: "every step has input/action/output/verify fields"
  - field: layer_3_complete
    verify: "every verification line has a command and expected output"
---
# Implementation Plan: {{TITLE}}

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification.

     SKIP RATIONALE: If ANY section is omitted, provide one-line rationale:
     **SKIPPED:** [reason] -->

---

## Goal

[One sentence: What capability will exist after this plan is complete?]

---

## Open Decisions

<!-- If ANY row has [BLOCKED] in Chosen column, plan-validation-cycle will BLOCK.
     POPULATE FROM: Work item frontmatter operator_decisions field. -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| [From work item] | [A, B] | [BLOCKED] | [Why — filled when resolved] |

---

## Layer 0: Inventory

<!-- MUST complete before any design work. Map the blast radius.
     Producer: plan-author agent
     Consumer: all downstream agents (DO, CHECK, critique) -->

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `[path/to/new_file.py]` | CREATE | 2 |
| `[path/to/existing.py]` | MODIFY | 2 |

### Consumer Files

<!-- Files that reference primary files and need updating.
     Use: Grep(pattern="module_name|function_name", glob="**/*.{py,md}") -->

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `[path/to/consumer.py]` | [imports X / calls Y / references Z] | [N] | UPDATE |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `[tests/test_new.py]` | CREATE | New test file for primary module |
| `[tests/test_existing.py]` | UPDATE | Consumer test — assertion changes |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | [N] | Primary Files table (CREATE rows) |
| Files to modify | [N] | Primary + Consumer + Test tables (MODIFY/UPDATE rows) |
| Tests to write | [N] | Test Files table |
| Total blast radius | [N] | Sum of all unique files above |

---

## Layer 1: Specification

<!-- The contract that the DO agent implements.
     Producer: plan-author agent
     Consumer: DO agent

     MUST INCLUDE:
     1. Actual current code that will be changed (copy from source)
     2. Exact target code (not pseudocode)
     3. Function signatures with types
     4. Input/output examples with REAL system data

     PATTERN VERIFICATION (E2-255):
     IF creating new module with sibling imports:
       - MUST read one sibling for import/error patterns
       - Use SAME patterns (consistency > preference)
     IF modifying existing module:
       - Follow existing patterns in that file -->

### Current State

```python
# [file:line] — what exists now
```

**Behavior:** [What the system does now]
**Problem:** [Why this needs to change]

### Desired State

```python
# [file:line] — target implementation
```

**Behavior:** [What the system will do]
**Result:** [What this enables]

### Tests

<!-- Write test specs BEFORE implementation code.
     Each test: name, file, setup, assertion. -->

#### Test 1: [Descriptive Name]
- **file:** `tests/test_[module].py`
- **function:** `test_[descriptive_name]()`
- **setup:** [concrete setup — tmp_path, fixtures, mocks]
- **assertion:** [concrete assertion — what is checked]

#### Test 2: [Descriptive Name]
- **file:** `tests/test_[module].py`
- **function:** `test_[descriptive_name]()`
- **setup:** [setup]
- **assertion:** [assertion]

#### Test 3: [Edge Case / Degradation]
- **file:** `tests/test_[module].py`
- **function:** `test_[edge_case]()`
- **setup:** [setup]
- **assertion:** [assertion]

### Design

<!-- Per file in Layer 0 Primary Files table.
     REQUIRED: exact code, not pseudocode. -->

#### File 1 (NEW): `[path/to/new_file.py]`

```python
# Complete implementation — DO agent copies this
```

#### File 2 (MODIFY): `[path/to/existing.py]`

**Location:** Lines X-Y in `function_name()`

**Current Code:**
```python
# [file:line-range] — copy exact current implementation
```

**Target Code:**
```python
# [file:line-range] — exact target implementation
```

**Diff:**
```diff
         existing_line
+        new_line_added
-        old_line_removed
```

### Call Chain

```
caller_function()
    |
    +-> THIS_FUNCTION()     # <-- what we're changing
    |       Returns: [Type]
    |
    +-> downstream_function()
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| [Decision point] | [What was chosen] | [WHY — most important part] |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| [Edge case] | [How handled] | Test N |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| [Risk] | [H/M/L] | [Strategy] |

---

## Layer 2: Implementation Steps

<!-- Ordered steps. Each step is a sub-agent delegation unit.
     Producer: plan-author agent
     Consumer: DO agent + orchestrator

     The orchestrator verifies each step before proceeding to the next. -->

### Step 1: Write Failing Tests (RED)
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Create test file(s) from Layer 1 Tests section
- **output:** Test file(s) exist, all tests fail
- **verify:** `pytest [test_file] -v 2>&1 | grep -c "FAILED\|ERROR"` equals [N]

### Step 2: Implement Primary Module (GREEN)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Create/modify primary file(s) from Layer 1 Design section
- **output:** All tests pass
- **verify:** `pytest [test_file] -v` exits 0, `[N] passed` in output

### Step 3: Integrate
- **input:** Step 2 complete (tests green)
- **action:** Add call-site / wiring per Layer 1 Design (File 2)
- **output:** Runtime consumer calls the new code
- **verify:** `grep "[function_name]" [consumer_file]` returns 1+ match

### Step 4: Update Consumers
- **input:** Step 3 complete
- **action:** Update files from Layer 0 Consumer Files table
- **output:** No stale references
- **verify:** `grep "[old_pattern]" . -r --include="*.py" --include="*.md"` returns 0 matches

### Step 5: Update Documentation
- **input:** Step 4 complete
- **action:** Update README.md in each directory with new/changed files
- **output:** READMEs reflect actual file state
- **verify:** `grep "[new_module]" [dir]/README.md` returns 1 match

---

## Ground Truth Verification

<!-- Computable verification protocol.
     Producer: plan-author agent
     Consumer: CHECK agent + orchestrator

     Every line has a command and expected output.
     The CHECK agent runs these mechanically — no judgment needed. -->

### Tests

| Command | Expected |
|---------|----------|
| `pytest [test_file] -v` | [N] passed, 0 failed |
| `pytest tests/ -v` | 0 new failures vs [baseline] pre-existing |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| [Copy from WORK.md deliverable 1] | `[command]` | [expected output] |
| [Copy from WORK.md deliverable 2] | `[command]` | [expected output] |
| [Copy from WORK.md deliverable N] | `[command]` | [expected output] |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| No stale references | `grep "[old_pattern]" . -r --include="*.py" --include="*.md"` | 0 matches |
| README updated | `grep "[new_module]" [dir]/README.md` | 1+ match |
| Runtime consumer exists | `grep "[function_name]" [consumer_file]` | 1+ match |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 2 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] Runtime consumer exists (Consumer Integrity table above)
- [ ] No stale references (Consumer Integrity table above)
- [ ] READMEs updated (Consumer Integrity table above)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- [Related ADR or spec]
- [Related work items]

---
