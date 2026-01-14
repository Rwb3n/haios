---
template: implementation_plan
status: complete
date: 2026-01-05
backlog_id: E2-271
title: Skill Module Reference Cleanup
author: Hephaestus
lifecycle_phase: plan
session: 175
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-07T23:20:23'
---
# Implementation Plan: Skill Module Reference Cleanup

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

Skills will contain only executable or prose-based instructions, with no misleading Python import examples that cannot be run.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 7 | Skills with module references (list below) |
| Lines of code affected | ~30 | Code block replacements across 7 files |
| New files to create | 0 | Documentation cleanup only |
| Tests to write | 0 | No code changes, grep verification only |
| Dependencies | 0 | Skills are documentation, not code |

**Files to modify:**
1. `.claude/skills/implementation-cycle/SKILL.md`
2. `.claude/skills/investigation-cycle/SKILL.md`
3. `.claude/skills/close-work-cycle/SKILL.md`
4. `.claude/skills/observation-triage-cycle/SKILL.md`
5. `.claude/skills/routing-gate/SKILL.md`
6. `.claude/skills/extract-content/SKILL.md`
7. `.claude/skills/dod-validation-cycle/SKILL.md` (clarification only)

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Skills are read by LLM, no code execution |
| Risk of regression | Low | Documentation changes, no functional code |
| External dependencies | Low | None |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Edit 7 skill files | 30 min | High |
| Verification (grep) | 10 min | High |
| **Total** | 40 min | High |

---

## Current State vs Desired State

### Current State

Skills contain Python code examples with bare module imports:

```python
# implementation-cycle/SKILL.md:229
from routing import determine_route
result = determine_route(next_work_id=id, has_plan=bool(plans))

# close-work-cycle/SKILL.md:114
from observations import get_pending_observation_count, should_trigger_triage
count = get_pending_observation_count()

# extract-content/SKILL.md:41
from haios_etl.extraction import ExtractionManager
```

**Behavior:** LLM reads these examples but cannot execute them because:
1. Python path is not configured for `.claude/lib/`
2. `haios_etl` is deprecated
3. Claude Code CLI doesn't execute Python imports from skills

**Result:** Confusion about how to actually use the functionality. INV-057 identified this as a portability issue.

### Desired State

Skills contain either:
1. **Prose instructions** referencing decision tables the LLM follows directly
2. **just recipes** for programmatic access (`just triage-observations`)
3. **Clarified paths** where lib module references are intentional

```markdown
# implementation-cycle/SKILL.md:227-231 (CHAIN Phase)
4. **Apply routing decision table** (see routing-gate skill):
   - If `next_work_id` is None → `await_operator`
   - If ID starts with `INV-` → `invoke_investigation`
   - If `has_plan` is True → `invoke_implementation`
   - Else → `invoke_work_creation`
```

**Behavior:** LLM reads prose and decision tables, which it can follow directly without Python execution.

**Result:** Skills accurately describe what agents can do. No misleading code examples.

---

## Tests First (TDD)

**SKIPPED:** This is a documentation-only task. Skills are markdown files read by LLMs, not executed Python code. Verification is via grep patterns, not pytest.

### Verification Strategy (Grep-based)

After edits, these grep patterns should return **no matches** in `.claude/skills/`:

| Pattern | Expected Result |
|---------|-----------------|
| `from routing import` | 0 matches |
| `from observations import` | 0 matches |
| `from governance_events import` | 0 matches |
| `haios_etl.extraction` | 0 matches |

These patterns should **exist** (clarifications added):
| Pattern | Expected |
|---------|----------|
| `routing-gate skill` | References to skill name (not imports) |
| `just triage-observations` | Recipe references |
| `.claude/lib/validate.py` | Intentional path reference in dod-validation |

---

## Detailed Design

### Change Summary by File

#### 1. implementation-cycle/SKILL.md

**Lines 227-231 (CHAIN Phase):** Remove Python import, replace with prose

```diff
-4. **Invoke routing-gate logic** (see `routing-gate` skill for decision table):
-   ```python
-   from routing import determine_route
-   result = determine_route(next_work_id=id, has_plan=bool(plans))
-   ```
+4. **Apply routing decision table** (see `routing-gate` skill):
+   - If `next_work_id` is None → `await_operator`
+   - If ID starts with `INV-` → `invoke_investigation`
+   - If `has_plan` is True → `invoke_implementation`
+   - Else → `invoke_work_creation`
```

**Lines 309-325 (Governance Event Logging):** Remove Python imports, replace with note

```diff
-### Phase Transition Logging
-
-At each phase exit, agent **SHOULD** call:
-```python
-from governance_events import log_phase_transition
-log_phase_transition("PLAN", "{backlog_id}", "Hephaestus")  # PLAN phase exit
-...
-```
-
-### Validation Outcome Logging
-
-Bridge skills (plan-validation, dod-validation, preflight-checker) **SHOULD** log outcomes:
-```python
-from governance_events import log_validation_outcome
-log_validation_outcome("preflight", "{backlog_id}", "pass", "All checks passed")
-...
-```
+### Phase Transition Logging
+
+Phase transitions are logged automatically via governance hooks. View with:
+```bash
+just governance-metrics
+```
+
+### Validation Outcome Logging
+
+Validation outcomes are logged automatically. Check audit trail via:
+```bash
+just events
+```
```

#### 2. investigation-cycle/SKILL.md

**Lines 128-132 (CHAIN Phase):** Remove Python import, replace with prose

```diff
-4. **Invoke routing-gate logic** (see `routing-gate` skill for decision table):
-   ```python
-   from routing import determine_route
-   result = determine_route(next_work_id=id, has_plan=bool(plans))
-   ```
+4. **Apply routing decision table** (see `routing-gate` skill):
+   - If `next_work_id` is None → `await_operator`
+   - If ID starts with `INV-` → `invoke_investigation`
+   - If `has_plan` is True → `invoke_implementation`
+   - Else → `invoke_work_creation`
```

#### 3. close-work-cycle/SKILL.md

**Lines 113-125 (OBSERVE Phase threshold check):** Remove Python imports

```diff
-5. **Check pending observation count:**
-   ```python
-   from observations import get_pending_observation_count, should_trigger_triage
-   count = get_pending_observation_count()
-   ```
+5. **Check pending observation count:**
+   ```bash
+   just triage-observations
+   ```
+   This reports count and lists pending items.
```

**Lines 174-180 (MEMORY Phase governance check):** Remove Python import

```diff
-1. **Check for cycle events** (soft gate - warns but does not block):
-   ```python
-   from governance_events import check_work_item_events
-   result = check_work_item_events("{id}")
-   if not result["has_events"]:
-       print(f"WARNING: {result['warning']}")
-   ```
+1. **Check for cycle events** (soft gate - warns but does not block):
+   ```bash
+   just events | grep "{id}"
+   ```
+   If no events found for the work ID, warn that governance may have been bypassed.
```

**Lines 214-218 (CHAIN Phase):** Remove Python import, replace with prose (same as implementation-cycle)

#### 4. observation-triage-cycle/SKILL.md

**Lines 47-51 (SCAN Phase):** Remove Python import

```diff
-   Or in Python:
-   ```python
-   from observations import scan_archived_observations
-   pending = scan_archived_observations()
-   ```
+(Python API available in `.claude/lib/observations.py` for programmatic access)
```

#### 5. routing-gate/SKILL.md

**Lines 56-76 (Usage from Python) and Lines 85-95 (From Skill CHAIN Phase):** Remove Python imports

```diff
-### From Python
-
-```python
-from routing import determine_route
-...
-```
-
-### From Skill CHAIN Phase
-
-```markdown
-### CHAIN Phase
-
-1. Query next work: `just ready`
-2. Read work file to check `documents.plans`
-3. Call routing-gate:
-   ```python
-   from routing import determine_route
-   result = determine_route(next_work_id=id, has_plan=bool(plans))
-   ```
+### Usage
+
+**From cycle skill CHAIN phase:**
+
+1. Query next work: `just ready`
+2. Read first work file, check `documents.plans` field
+3. Apply the decision table above:
+   - `next_work_id` is None → `await_operator`
+   - ID starts with `INV-` → `invoke_investigation`
+   - `has_plan` is True → `invoke_implementation`
+   - Otherwise → `invoke_work_creation`
+4. Execute the corresponding skill invocation
+
+**Programmatic access:** `.claude/lib/routing.py` contains `determine_route()` function.
```

#### 6. extract-content/SKILL.md

**Lines 39-52 (Via Python Direct):** Replace deprecated haios_etl reference

```diff
-### Via Python (Direct)
-
-```python
-from haios_etl.extraction import ExtractionManager
-
-extractor = ExtractionManager(api_key="your_google_api_key")
-result = extractor.extract_from_file("path/to/file.md", content)
-...
-```
+### Via Python (Direct)
+
+**Note:** `haios_etl` is deprecated. Use `.claude/lib/extraction.py` for direct Python access:
+
+```python
+# From .claude/lib/ directory
+from extraction import ExtractionManager
+```
+
+For most use cases, the MCP tool `extract_content` is recommended.
```

#### 7. dod-validation-cycle/SKILL.md

**Lines 73-74:** No change needed - reference to `.claude/lib/validate.py` is intentional and correct. Add clarifying comment if desired.

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Remove Python imports | Replace with prose/decision tables | Skills are LLM documentation, not executable code |
| Keep decision tables | LLM follows directly | Decision logic is clear without Python |
| Reference just recipes | For programmatic access | Recipes wrap lib modules with correct paths |
| Keep lib path references | Where intentional | dod-validation intentionally references validate.py |
| Note programmatic access | Brief mention of lib path | Advanced users can find lib modules if needed |

### Edge Cases

| Case | Handling |
|------|----------|
| Agent wants to call Python function | Reference lib path or just recipe |
| New skill needs routing | Copy prose decision table, not Python import |
| Hooks need module access | Hooks are Python, they import from lib correctly |

---

## Implementation Steps

### Step 1: Update routing-gate/SKILL.md
- [ ] Replace Python import section with prose usage instructions
- [ ] Keep decision table (unchanged)

### Step 2: Update implementation-cycle/SKILL.md
- [ ] Replace CHAIN Phase Python import with prose decision table
- [ ] Replace Governance Event Logging Python imports with just recipe references

### Step 3: Update investigation-cycle/SKILL.md
- [ ] Replace CHAIN Phase Python import with prose decision table

### Step 4: Update close-work-cycle/SKILL.md
- [ ] Replace OBSERVE Phase Python imports with just recipe
- [ ] Replace MEMORY Phase Python import with just recipe
- [ ] Replace CHAIN Phase Python import with prose decision table

### Step 5: Update observation-triage-cycle/SKILL.md
- [ ] Remove Python import example, add note about lib path

### Step 6: Update extract-content/SKILL.md
- [ ] Replace deprecated haios_etl reference with .claude/lib/ path

### Step 7: Verify dod-validation-cycle/SKILL.md
- [ ] Confirm .claude/lib/validate.py reference is appropriate (no change needed)

### Step 8: Verification (Grep)
- [ ] Grep for `from routing import` - expect 0 matches in skills
- [ ] Grep for `from observations import` - expect 0 matches in skills
- [ ] Grep for `from governance_events import` - expect 0 matches in skills
- [ ] Grep for `haios_etl.extraction` - expect 0 matches

### Step 9: README Sync
- [ ] Update `.claude/skills/README.md` if needed (document pattern change)

---

## Verification

- [ ] Grep verification passes (0 matches for bad patterns)
- [ ] Skills still readable and coherent
- [ ] Decision tables preserved and clear

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Skill becomes less clear | Low | Decision tables remain, prose is equally clear |
| Lost information | Low | Lib paths noted for programmatic access |
| Agent confusion on new pattern | Low | Pattern is simpler: follow prose, not fake code |

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
| `.claude/skills/routing-gate/SKILL.md` | No `from routing import` | [ ] | |
| `.claude/skills/implementation-cycle/SKILL.md` | No `from routing/governance_events import` | [ ] | |
| `.claude/skills/investigation-cycle/SKILL.md` | No `from routing import` | [ ] | |
| `.claude/skills/close-work-cycle/SKILL.md` | No `from routing/observations/governance_events import` | [ ] | |
| `.claude/skills/observation-triage-cycle/SKILL.md` | No `from observations import` | [ ] | |
| `.claude/skills/extract-content/SKILL.md` | No `haios_etl.extraction` | [ ] | |
| `Grep: from routing import` | 0 matches in skills | [ ] | |
| `Grep: from observations import` | 0 matches in skills | [ ] | |
| `Grep: from governance_events import` | 0 matches in skills | [ ] | |
| `Grep: haios_etl.extraction` | 0 matches anywhere | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
Grep(pattern="from routing import", path=".claude/skills")
Grep(pattern="from observations import", path=".claude/skills")
Grep(pattern="from governance_events import", path=".claude/skills")
Grep(pattern="haios_etl.extraction", path=".claude")
# Expected: 0 matches each
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Grep outputs show 0 matches? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Grep verification passes (no bad patterns)
- [ ] **Runtime consumer exists** - Skills are consumed by LLM at skill invocation time
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated if needed
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **Note:** No pytest tests for this task - skills are markdown documentation, not Python code.

---

## References

- INV-057: Commands Skills Templates Portability (source investigation)
- E2-270: Command PowerShell Elimination (sibling task, completed S174)
- E2-269: manifest.yaml Creation (sibling task from INV-057)
- `.claude/lib/routing.py` - Actual routing module
- `.claude/lib/observations.py` - Actual observations module
- `.claude/lib/governance_events.py` - Actual governance events module

---
