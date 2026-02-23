---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-23
backlog_id: WORK-210
title: "Split Retro-Cycle into Inline Reflect plus Delegated Close"
author: Hephaestus
lifecycle_phase: plan
session: 437
generated: 2026-02-23
last_updated: 2026-02-23T19:30:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-210/WORK.md"
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
# Implementation Plan: Split Retro-Cycle into Inline Reflect plus Delegated Close

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification. -->

---

## Goal

Modify retro-cycle SKILL.md so REFLECT and DERIVE phases are explicitly marked inline-only (main agent context required), and EXTRACT and COMMIT phases delegate to a haiku subagent; also modify close-work-cycle SKILL.md so its ARCHIVE and CHAIN mechanical phases delegate to a haiku subagent.

---

## Open Decisions

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| No unresolved operator decisions | — | — | operator_decisions field is empty in WORK.md |

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/skills/retro-cycle/SKILL.md` | MODIFY | 1 |
| `.claude/skills/close-work-cycle/SKILL.md` | MODIFY | 1 |

### Consumer Files

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `tests/test_retro_cycle.py` | content-asserts retro-cycle phases, provenance tags, escape hatch | 50-79 | UPDATE — add assertions for inline marker and delegation block |
| `tests/test_close_work_cycle.py` | content-asserts CHAIN phase caller-choice | 84-178 | UPDATE — add assertion for haiku subagent delegation in ARCHIVE/CHAIN |
| `.claude/commands/close.md` | references retro-cycle invocation order | whole file | READ-ONLY VERIFY — no change expected |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_retro_cycle.py` | UPDATE | Add 2 content-assertion tests: inline marker present, delegation block present |
| `tests/test_close_work_cycle.py` | UPDATE | Add 1 content-assertion test: haiku delegation present in ARCHIVE/CHAIN |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | No new files |
| Files to modify | 4 | 2 SKILL.md + 2 test files |
| Tests to write | 3 | Test Files table |
| Total blast radius | 4 | Sum of unique files above |

---

## Layer 1: Specification

### Current State

**retro-cycle/SKILL.md — Phase 1 REFLECT header (lines 140-147):**
```markdown
## Phase 1: REFLECT

Capture observations across 5 dimensions, anchored to specific evidence.
```

**retro-cycle/SKILL.md — Phase 4 COMMIT header (lines 287-291):**
```markdown
## Phase 4: COMMIT

Store all outputs to memory with typed provenance tags. No deduplication at write time.
```

**Behavior:** All four retro phases (REFLECT, DERIVE, EXTRACT, COMMIT) are described as inline steps — no distinction between phases that require main-agent context versus phases that are mechanical.

**Problem:** S436 operator directive: REFLECT and DERIVE require full session context held by main agent; delegating them is lossy. EXTRACT and COMMIT are mechanical (classify and persist) and should delegate to haiku to save main-agent context. The SKILL.md gives no guidance on this split, so agents either run everything inline or delegate everything — both wrong.

---

**close-work-cycle/SKILL.md — ARCHIVE Phase header (lines 168-208):**
```markdown
### 2. ARCHIVE Phase
...
**Actions:**
1. Run atomic close-work recipe:
   ```bash
   just close-work {id}
   ```
   ...
2. Update any associated plans to `status: complete` ...
3. **Run upstream status propagation (WORK-034):**
   ...
```

**Behavior:** ARCHIVE (status update, cascade, propagation) and CHAIN (routing, checkpoint) run inline in the main agent's context, consuming substantial tokens over many tool calls.

**Problem:** S436 observed the close-work-cycle-agent ran 68 tool calls over 20 minutes monolithically. ARCHIVE and CHAIN are mechanical (git operations, status writes, file edits, routing query) — they do not need main-agent cognitive context. They can delegate to a haiku subagent that reads the work_id and executes mechanically.

---

### Desired State

**retro-cycle/SKILL.md — Phase 1 REFLECT (add inline marker):**

Add an "Execution Context" note immediately after the Phase 1 header:

```markdown
## Phase 1: REFLECT

> **Execution Context: INLINE (main agent MUST execute this phase directly)**
> REFLECT requires full session context that only the main agent holds — recent tool calls,
> decisions made, surprises encountered. Delegating to a subagent is lossy because the
> subagent reconstructs context from files, not from live session state. S436 operator
> directive: REFLECT stays inline. Never wrap this phase in a Task() call.

Capture observations across 5 dimensions, anchored to specific evidence.
```

**retro-cycle/SKILL.md — Phase 2 DERIVE (add inline marker):**

Add inline marker after Phase 2 header:

```markdown
## Phase 2: DERIVE

> **Execution Context: INLINE (main agent MUST execute this phase directly)**
> DERIVE synthesizes from REFLECT observations. The observations exist in the main agent's
> working context — a subagent would have to read them from a file, losing the cognitive
> chain from observation to directive. S436 operator directive: DERIVE stays inline.

Extract Keep/Stop/Start directives from REFLECT observations.
```

**retro-cycle/SKILL.md — Phase 3 EXTRACT (add delegation block):**

Add delegation instruction at the START of Phase 3 (before Classification table):

```markdown
## Phase 3: EXTRACT

> **Execution Context: DELEGATE to haiku subagent (S436 operator directive)**
> EXTRACT is mechanical classification: takes REFLECT observations and assigns type
> (bug/feature/refactor/upgrade), confidence, priority. No session context required —
> the observations are already written in the main agent's output. Delegate to save
> main-agent tokens.

**Delegation pattern:**
```
Task(
  subagent_type='general-purpose',
  model='haiku',
  prompt='Execute retro-cycle EXTRACT phase for {work_id}.
    REFLECT findings (summary, not full text — chunk if >2000 tokens): {reflect_findings_text}
    Classify each actionable item by type (bug|feature|refactor|upgrade).
    Output format per SKILL.md Phase 3 Classification table.
    Return: extracted_items list in YAML format.'
)
```

Classify actionable items from REFLECT observations...
```

**retro-cycle/SKILL.md — Phase 4 COMMIT (add delegation block):**

Add delegation instruction at the START of Phase 4 (before Provenance Tags):

```markdown
## Phase 4: COMMIT

> **Execution Context: DELEGATE to haiku subagent (S436 operator directive)**
> COMMIT is mechanical persistence: calls ingester_ingest 4 times with structured outputs
> from REFLECT/DERIVE/EXTRACT phases. No cognitive context required. Delegate to save
> main-agent tokens.

**Delegation pattern:**
```
Task(
  subagent_type='general-purpose',
  model='haiku',
  prompt='Execute retro-cycle COMMIT phase for {work_id}.
    reflect_findings: {reflect_findings_json}
    kss_directives: {kss_directives_json}
    extracted_items: {extracted_items_json}
    scaling: {scaling}
    Store each per SKILL.md Phase 4 Provenance Tags. Return: memory_concept_ids list.
    Verify: after each ingester_ingest, confirm concept_ids is non-empty (S407 silent-drop check).'
)
```

Store all outputs to memory with typed provenance tags...
```

---

**close-work-cycle/SKILL.md — ARCHIVE Phase (add delegation wrapper):**

Add delegation instruction at start of ARCHIVE phase (before "Goal: Update work item status"):

```markdown
### 2. ARCHIVE Phase

**On Entry:**
```bash
just set-cycle close-work-cycle ARCHIVE {work_id}
```

> **Execution Context: DELEGATE to haiku subagent (S436 operator directive)**
> ARCHIVE is mechanical: status update, cascade, status propagation. No cognitive context
> required. Delegate to save main-agent tokens. The S436 close-work-cycle-agent ran 68
> tool calls monolithically; haiku delegation makes this mechanical and parallel.

**Delegation pattern:**
```
Task(
  subagent_type='general-purpose',
  model='haiku',
  prompt='Execute close-work-cycle ARCHIVE phase for {work_id}.
    Actions:
    1. Run: just close-work {work_id}
    2. Verify: work file has status: complete and closed date set
    3. Update associated plans to status: complete
    4. Run StatusPropagator().propagate("{work_id}")
    Report: DONE (with archived_path) or FAIL (with error).'
)
```
```

**close-work-cycle/SKILL.md — CHAIN Phase (add delegation wrapper):**

Add delegation instruction at start of CHAIN phase (before "Goal: Checkpoint context"):

```markdown
### 3. CHAIN Phase (Post-ARCHIVE)

**On Entry:**
```bash
just set-cycle close-work-cycle CHAIN {work_id}
```

> **Execution Context: PARTIAL DELEGATE to haiku subagent (S436 operator directive)**
> CHAIN has both mechanical steps (checkpoint, queue query) and interactive steps
> (AskUserQuestion for operator routing). Mechanical steps delegate to haiku; the
> AskUserQuestion MUST remain in main agent context (subagent isolated context cannot
> reliably surface interactive prompts to operator — critique A8).

**Delegation pattern (mechanical steps only):**
```
result = Task(
  subagent_type='general-purpose',
  model='haiku',
  prompt='Execute close-work-cycle CHAIN mechanical steps for {work_id}.
    Actions:
    1. Invoke checkpoint-cycle (Skill(skill="checkpoint-cycle"))
    2. Run: just ready
    3. Read each ready work item type field
    Report: list of ready items with their types.'
)
# Main agent then presents AskUserQuestion with routing options
# using the haiku result as input. AskUserQuestion stays inline.
```
```

---

### Tests

#### Test 1: retro-cycle REFLECT phase has inline marker

- **file:** `tests/test_retro_cycle.py`
- **function:** `test_reflect_phase_marked_inline()`
- **setup:** Read `.claude/skills/retro-cycle/SKILL.md` content
- **assertion:** "Execution Context: INLINE" appears in the content before the DERIVE section; "never wrap this phase in a Task" (case-insensitive) also present

#### Test 2: retro-cycle EXTRACT and COMMIT phases have delegation blocks

- **file:** `tests/test_retro_cycle.py`
- **function:** `test_extract_commit_phases_delegate_to_haiku()`
- **setup:** Read `.claude/skills/retro-cycle/SKILL.md` content
- **assertion:** Both "DELEGATE to haiku subagent" and "model='haiku'" appear in content; they appear after (higher line index than) the REFLECT section marker

#### Test 3: close-work-cycle ARCHIVE and CHAIN phases have haiku delegation

- **file:** `tests/test_close_work_cycle.py`
- **function:** `test_archive_chain_delegate_to_haiku()`
- **setup:** Read `.claude/skills/close-work-cycle/SKILL.md` content
- **assertion:** "DELEGATE to haiku subagent" appears in content; `model='haiku'` present; substring "DELEGATE to haiku subagent" found within 700-char window of both "ARCHIVE Phase" and "CHAIN Phase" sections (matches both "DELEGATE" and "PARTIAL DELEGATE")

### Design

#### File 1 (MODIFY): `.claude/skills/retro-cycle/SKILL.md`

**Location:** Phase 1 REFLECT header — insert after `## Phase 1: REFLECT` line (approx line 140)

**Current Code:**
```markdown
## Phase 1: REFLECT

Capture observations across 5 dimensions, anchored to specific evidence.
```

**Target Code:**
```markdown
## Phase 1: REFLECT

> **Execution Context: INLINE (main agent MUST execute this phase directly)**
> REFLECT requires full session context that only the main agent holds — recent tool calls,
> decisions made, surprises encountered. Delegating to a subagent is lossy because the
> subagent reconstructs context from files, not from live session state. S436 operator
> directive: REFLECT stays inline. Never wrap this phase in a Task() call.

Capture observations across 5 dimensions, anchored to specific evidence.
```

**Location:** Phase 2 DERIVE header — insert after `## Phase 2: DERIVE` line (approx line 199)

**Current Code:**
```markdown
## Phase 2: DERIVE

Extract Keep/Stop/Start directives from REFLECT observations.
```

**Target Code:**
```markdown
## Phase 2: DERIVE

> **Execution Context: INLINE (main agent MUST execute this phase directly)**
> DERIVE synthesizes from REFLECT observations. The observations exist in the main agent's
> working context — a subagent would have to read them from a file, losing the cognitive
> chain from observation to directive. S436 operator directive: DERIVE stays inline.

Extract Keep/Stop/Start directives from REFLECT observations.
```

**Location:** Phase 3 EXTRACT header — insert after `## Phase 3: EXTRACT` line (approx line 229)

**Current Code:**
```markdown
## Phase 3: EXTRACT

Classify actionable items from REFLECT observations into typed work candidates with priority signals.
```

**Target Code:**
```markdown
## Phase 3: EXTRACT

> **Execution Context: DELEGATE to haiku subagent (S436 operator directive)**
> EXTRACT is mechanical classification — takes REFLECT observations and assigns type
> (bug/feature/refactor/upgrade), confidence, priority. No live session context required;
> the observations are written output from Phase 1. Delegate to save main-agent tokens.

**Delegation pattern:**
```
Task(
  subagent_type='general-purpose',
  model='haiku',
  prompt='Execute retro-cycle EXTRACT phase for {work_id}.
    REFLECT findings (summary, not full text — chunk if >2000 tokens): {reflect_findings_text}
    Classify each actionable item. Output format per SKILL.md Phase 3 Classification table.
    Return: extracted_items list in YAML format.'
)
```

Classify actionable items from REFLECT observations into typed work candidates with priority signals.
```

**Location:** Phase 4 COMMIT header — insert after `## Phase 4: COMMIT` line (approx line 287)

**Current Code:**
```markdown
## Phase 4: COMMIT

Store all outputs to memory with typed provenance tags. No deduplication at write time.
```

**Target Code:**
```markdown
## Phase 4: COMMIT

> **Execution Context: DELEGATE to haiku subagent (S436 operator directive)**
> COMMIT is mechanical persistence — calls ingester_ingest 4 times with structured outputs
> from REFLECT/DERIVE/EXTRACT phases. No cognitive context required. Delegate to save
> main-agent tokens.

**Delegation pattern:**
```
Task(
  subagent_type='general-purpose',
  model='haiku',
  prompt='Execute retro-cycle COMMIT phase for {work_id}.
    reflect_findings: {reflect_findings_json}
    kss_directives: {kss_directives_json}
    extracted_items: {extracted_items_json}
    scaling: {scaling}
    Store each per SKILL.md Phase 4 Provenance Tags. Return: memory_concept_ids list.
    Verify: after each ingester_ingest, confirm concept_ids is non-empty (S407 silent-drop check).'
)
```

Store all outputs to memory with typed provenance tags. No deduplication at write time.
```

---

#### File 2 (MODIFY): `.claude/skills/close-work-cycle/SKILL.md`

**Location:** ARCHIVE Phase header — insert after `**On Entry:** ... just set-cycle ... ARCHIVE ...` block (approx line 173)

**Current Code:**
```markdown
### 2. ARCHIVE Phase

**On Entry:**
```bash
just set-cycle close-work-cycle ARCHIVE {work_id}
```

**Goal:** Update work item status to complete.
```

**Target Code:**
```markdown
### 2. ARCHIVE Phase

**On Entry:**
```bash
just set-cycle close-work-cycle ARCHIVE {work_id}
```

> **Execution Context: DELEGATE to haiku subagent (S436 operator directive)**
> ARCHIVE is mechanical: status update, cascade, status propagation. No cognitive context
> required. Delegate to save main-agent tokens. (S436: close-work-cycle-agent ran 68 tool
> calls monolithically; delegation makes this mechanical.)

**Delegation pattern:**
```
Task(
  subagent_type='general-purpose',
  model='haiku',
  prompt='Execute close-work-cycle ARCHIVE phase for {work_id}.
    1. Run: just close-work {work_id}
    2. Verify: work file has status: complete and closed date set
    3. Update associated plans to status: complete
    4. Run StatusPropagator().propagate("{work_id}")
    Report: DONE (archived_path) or FAIL (error).'
)
```

**Goal:** Update work item status to complete.
```

**Location:** CHAIN Phase header — insert after `**On Entry:** ... just set-cycle ... CHAIN ...` block (approx line 213)

**Current Code:**
```markdown
### 3. CHAIN Phase (Post-ARCHIVE)

**On Entry:**
```bash
just set-cycle close-work-cycle CHAIN {work_id}
```

**Goal:** Checkpoint context then route to next work item.
```

**Target Code:**
```markdown
### 3. CHAIN Phase (Post-ARCHIVE)

**On Entry:**
```bash
just set-cycle close-work-cycle CHAIN {work_id}
```

> **Execution Context: PARTIAL DELEGATE to haiku subagent (S436 operator directive)**
> CHAIN has both mechanical steps (checkpoint, queue query) and interactive steps
> (AskUserQuestion for operator routing). Mechanical steps delegate to haiku; the
> AskUserQuestion MUST remain in main agent context (subagent isolated context cannot
> reliably surface interactive prompts to operator — critique A8).

**Delegation pattern (mechanical steps only):**
```
result = Task(
  subagent_type='general-purpose',
  model='haiku',
  prompt='Execute close-work-cycle CHAIN mechanical steps for {work_id}.
    1. Invoke checkpoint-cycle (Skill(skill="checkpoint-cycle"))
    2. Run: just ready
    3. Read each ready work item type field
    Report: list of ready items with their types.'
)
# Main agent then presents AskUserQuestion with routing options
# using the haiku result as input. AskUserQuestion stays inline.
```

**Goal:** Checkpoint context then route to next work item.
```

---

#### File 3 (UPDATE): `tests/test_retro_cycle.py`

Add to `TestRetroCyclePhases` class:

```python
def test_reflect_phase_marked_inline(self):
    """REFLECT phase has inline execution context marker (S436 operator directive)."""
    content = Path(".claude/skills/retro-cycle/SKILL.md").read_text(encoding="utf-8")
    # Marker must appear before DERIVE section
    reflect_marker_pos = content.find("Execution Context: INLINE")
    derive_pos = content.find("## Phase 2: DERIVE")
    assert reflect_marker_pos != -1, "REFLECT phase must have INLINE execution context marker"
    assert reflect_marker_pos < derive_pos, "INLINE marker must appear before DERIVE section"
    # Anti-delegation note must be present
    content_lower = content.lower()
    assert "never wrap" in content_lower or "do not delegate" in content_lower or \
           "never" in content_lower, \
        "REFLECT must have explicit anti-delegation language"

def test_extract_commit_phases_delegate_to_haiku(self):
    """EXTRACT and COMMIT phases have haiku delegation blocks (S436 operator directive)."""
    content = Path(".claude/skills/retro-cycle/SKILL.md").read_text(encoding="utf-8")
    # Both delegation markers must be present
    assert "DELEGATE to haiku subagent" in content, \
        "EXTRACT/COMMIT must have haiku delegation markers"
    assert "model='haiku'" in content, \
        "Delegation blocks must specify model='haiku'"
    # Delegation markers must appear after REFLECT section
    reflect_pos = content.find("## Phase 1: REFLECT")
    first_delegate_pos = content.find("DELEGATE to haiku subagent")
    assert first_delegate_pos > reflect_pos, \
        "Delegation markers must appear after REFLECT section (not in inline phases)"
```

---

#### File 4 (UPDATE): `tests/test_close_work_cycle.py`

Add to `TestLightweightClosePatterns` class (or add new class):

```python
class TestCloseWorkCycleDelegation:
    """WORK-210: ARCHIVE and CHAIN phases delegate to haiku subagent (S436)."""

    def test_archive_chain_delegate_to_haiku(self):
        """ARCHIVE and CHAIN phases have haiku delegation blocks per S436 directive."""
        content = Path(".claude/skills/close-work-cycle/SKILL.md").read_text(encoding="utf-8")
        # Delegation marker must be present
        assert "DELEGATE to haiku subagent" in content, \
            "close-work-cycle ARCHIVE/CHAIN must have haiku delegation markers"
        assert "model='haiku'" in content, \
            "Delegation blocks must specify model='haiku'"
        # Verify delegation appears near both ARCHIVE and CHAIN sections
        archive_pos = content.find("ARCHIVE Phase")
        chain_pos = content.find("CHAIN Phase")
        # Use substring window search (not startswith) to match both
        # "DELEGATE to haiku subagent" and "PARTIAL DELEGATE to haiku subagent"
        archive_window = content[archive_pos:archive_pos + 700]
        chain_window = content[chain_pos:chain_pos + 700]
        assert "DELEGATE to haiku subagent" in archive_window, \
            "Haiku delegation must appear near ARCHIVE Phase section"
        assert "DELEGATE to haiku subagent" in chain_window, \
            "Haiku delegation must appear near CHAIN Phase section"
```

---

### Call Chain

```
/close {work_id}
    |
    +-> retro-cycle (main agent)
    |     |
    |     +-> Phase 0: SCALE (inline)
    |     +-> Phase 1: REFLECT (inline — session context required)
    |     +-> Phase 2: DERIVE (inline — session context required)
    |     +-> Phase 3: EXTRACT (Task haiku — mechanical classification)
    |     +-> Phase 4: COMMIT (Task haiku — mechanical persistence)
    |
    +-> close-work-cycle (main agent — VALIDATE inline, cognition needed)
          |
          +-> VALIDATE (inline — DoD judgment required)
          +-> ARCHIVE (Task haiku — mechanical status update)
          +-> CHAIN (Task haiku — mechanical routing + checkpoint)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Inline marker format | Blockquote with bold "Execution Context: INLINE" | Visually distinct; parseable by grep; consistent with existing SKILL.md blockquote patterns |
| Delegation marker format | Blockquote with bold "Execution Context: DELEGATE to haiku subagent" | Symmetric with inline marker; immediately visible to agent reading phase |
| Delegation pattern as code block | Yes — Task() call shown explicitly | DO agent and subagent dispatcher need exact syntax. Prose description is ambiguous |
| output_contract stability | retro-cycle output_contract fields unchanged | S436 critique pass 2 finding A1: reflect_findings, kss_directives, extracted_items, memory_concept_ids, dod_relevant_findings, scaling fields MUST remain as stability baseline |
| VALIDATE stays inline in close-work-cycle | Yes — only ARCHIVE and CHAIN delegate | VALIDATE requires judgment (DoD criteria evaluation, dod_relevant_findings review). ARCHIVE and CHAIN are mechanical |
| Memory insight respect | No multi-step delegation without step verification | mem 86986: delegation without explicit step verification loses traceability. Each delegation block specifies explicit numbered steps and expected report format |
| Test approach | Content-assertion tests (read SKILL.md, assert pattern present) | Consistent with existing test_retro_cycle.py and test_close_work_cycle.py patterns. No runtime execution of skills needed |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| Subagent for EXTRACT unavailable | Retro-cycle escape hatch: "Phase timeout" — complete current phase, skip remaining, COMMIT what we have | No new test — existing escape hatch covers |
| output_contract fields missing after edit | DO agent MUST verify frontmatter output_contract fields unchanged after editing SKILL.md | Test 1/2 — schema checks |
| close-work-cycle VALIDATE delegation confusion | VALIDATE intentionally NOT delegated — inline marker absent from VALIDATE section reinforces this | Test 3 verifies delegation only near ARCHIVE/CHAIN, not VALIDATE |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Editing SKILL.md corrupts frontmatter output_contract | H | Read full file before any edit; verify output_contract fields post-edit by grepping frontmatter section |
| Delegation block syntax invalid (Task() signature) | M | Copy exact Task() pattern from implementation-cycle/phases/DO.md which has verified working syntax |
| Test assertions too strict (brittle patterns) | M | Use case-insensitive search and substring matching; avoid exact line-number assertions |
| Existing test_retro_cycle tests break | L | New tests are additive only; existing 9 tests unchanged (all assert current patterns which are being preserved) |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)

- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Add `test_reflect_phase_marked_inline` and `test_extract_commit_phases_delegate_to_haiku` to `tests/test_retro_cycle.py`; add `TestCloseWorkCycleDelegation` class with `test_archive_chain_delegate_to_haiku` to `tests/test_close_work_cycle.py`
- **output:** 3 new test functions exist, all fail (patterns not yet present in SKILL.md files)
- **verify:** `pytest tests/test_retro_cycle.py::TestRetroCyclePhases::test_reflect_phase_marked_inline tests/test_retro_cycle.py::TestRetroCyclePhases::test_extract_commit_phases_delegate_to_haiku tests/test_close_work_cycle.py::TestCloseWorkCycleDelegation::test_archive_chain_delegate_to_haiku -v 2>&1 | grep -c "FAILED\|ERROR"` equals 3

### Step 2: Modify retro-cycle SKILL.md (GREEN for retro tests)

- **spec_ref:** Layer 1 > Design > File 1 (MODIFY)
- **input:** Step 1 complete (tests exist and fail); current SKILL.md read
- **action:** Insert execution context blockquotes into Phase 1 (REFLECT), Phase 2 (DERIVE), Phase 3 (EXTRACT), Phase 4 (COMMIT) per Layer 1 Desired State. Verify output_contract frontmatter unchanged.
- **output:** retro-cycle SKILL.md has inline markers for REFLECT/DERIVE and delegation blocks for EXTRACT/COMMIT
- **verify:** `pytest tests/test_retro_cycle.py::TestRetroCyclePhases::test_reflect_phase_marked_inline tests/test_retro_cycle.py::TestRetroCyclePhases::test_extract_commit_phases_delegate_to_haiku -v` exits 0, `2 passed` in output

### Step 3: Modify close-work-cycle SKILL.md (GREEN for close tests)

- **spec_ref:** Layer 1 > Design > File 2 (MODIFY)
- **input:** Step 2 complete; close-work-cycle SKILL.md read
- **action:** Insert execution context blockquotes with delegation patterns into ARCHIVE phase and CHAIN phase per Layer 1 Desired State
- **output:** close-work-cycle SKILL.md has haiku delegation blocks in ARCHIVE and CHAIN sections
- **verify:** `pytest tests/test_close_work_cycle.py::TestCloseWorkCycleDelegation::test_archive_chain_delegate_to_haiku -v` exits 0, `1 passed` in output

### Step 4: Full Test Suite Regression

- **spec_ref:** Layer 0 > Consumer Files
- **input:** Steps 2 and 3 complete
- **action:** Run full test suite to confirm no regressions in existing retro-cycle and close-work-cycle tests
- **output:** All previously passing tests still pass
- **verify:** `pytest tests/test_retro_cycle.py tests/test_close_work_cycle.py -v` shows 0 new failures vs baseline (existing 9 + 7 tests)

### Step 5: Verify output_contract Stability

- **spec_ref:** Layer 1 > Key Design Decisions (output_contract stability)
- **input:** Step 2 complete
- **action:** Read retro-cycle SKILL.md frontmatter and confirm all 7 output_contract fields present: success, reflect_findings, kss_directives, extracted_items, memory_concept_ids, dod_relevant_findings, scaling
- **output:** All 7 fields present and unmodified
- **verify:** `grep -c "reflect_findings\|kss_directives\|extracted_items\|memory_concept_ids\|dod_relevant_findings\|scaling" .claude/skills/retro-cycle/SKILL.md` returns 6+ matches in frontmatter section

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_retro_cycle.py::TestRetroCyclePhases::test_reflect_phase_marked_inline -v` | 1 passed, 0 failed |
| `pytest tests/test_retro_cycle.py::TestRetroCyclePhases::test_extract_commit_phases_delegate_to_haiku -v` | 1 passed, 0 failed |
| `pytest tests/test_close_work_cycle.py::TestCloseWorkCycleDelegation::test_archive_chain_delegate_to_haiku -v` | 1 passed, 0 failed |
| `pytest tests/test_retro_cycle.py tests/test_close_work_cycle.py -v` | 0 new failures vs pre-WORK-210 baseline |
| `pytest tests/ -v` | 0 new failures vs pre-WORK-210 baseline (1571 passed baseline) |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| Modified retro-cycle SKILL.md: REFLECT+DERIVE marked inline-only | `grep "Execution Context: INLINE" .claude/skills/retro-cycle/SKILL.md` | 2 matches (one per inline phase) |
| Haiku subagent delegation for EXTRACT+COMMIT | `grep "DELEGATE to haiku subagent" .claude/skills/retro-cycle/SKILL.md` | 2 matches (one per delegated phase) |
| Modified close-work-cycle: mechanical phases delegated | `grep "DELEGATE to haiku subagent" .claude/skills/close-work-cycle/SKILL.md` | 2 matches (ARCHIVE + CHAIN) |
| Tests verifying delegation boundary | `pytest tests/test_retro_cycle.py::TestRetroCyclePhases::test_reflect_phase_marked_inline tests/test_retro_cycle.py::TestRetroCyclePhases::test_extract_commit_phases_delegate_to_haiku tests/test_close_work_cycle.py::TestCloseWorkCycleDelegation::test_archive_chain_delegate_to_haiku -v` | 3 passed, 0 failed |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| REFLECT phase output schema unchanged | `grep -A2 "reflect_findings" .claude/skills/retro-cycle/SKILL.md \| head -10` | field: reflect_findings, type: list still present |
| output_contract fields stable | `grep -c "reflect_findings\|kss_directives\|extracted_items\|memory_concept_ids\|dod_relevant_findings\|scaling" .claude/skills/retro-cycle/SKILL.md` | 6+ matches |
| close.md invocation order unchanged | `grep -n "retro-cycle\|close-work-cycle" .claude/commands/close.md` | retro-cycle line number < close-work-cycle line number |
| Existing retro cycle tests still pass | `pytest tests/test_retro_cycle.py -v` | All previously existing tests pass |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 4 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] No stale references (retro-cycle SKILL.md output_contract unchanged)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- `.claude/skills/retro-cycle/SKILL.md` — primary target skill
- `.claude/skills/close-work-cycle/SKILL.md` — primary target skill
- Memory 88078 — S436 operator directive (REFLECT/DERIVE inline; EXTRACT/COMMIT delegate)
- Memory 86986 — STOP: delegating multi-step implementation without explicit step verification
- `docs/work/active/WORK-209/WORK.md` — parent work item (retro observation source)
- `tests/test_retro_cycle.py` — consumer test file (additive changes only)
- `tests/test_close_work_cycle.py` — consumer test file (additive changes only)
- `docs/ADR/ADR-048-progressive-contracts-phase-per-file-skill-fracturing.md` — S436 skill authoring context

---
