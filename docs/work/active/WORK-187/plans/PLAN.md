---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-22
backlog_id: WORK-187
title: "Fracture Implementation-Cycle SKILL.md into Phase Files"
author: Hephaestus
lifecycle_phase: plan
session: 421
generated: 2026-02-22
last_updated: 2026-02-22T12:00:00

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-187/WORK.md"
    required: true
  - field: source_files_exist
    verify: "all paths in WORK.md source_files exist on disk"
    required: true

output_contract:
  - field: layer_0_complete
    verify: "Layer 0 tables have no placeholder rows"
  - field: layer_1_complete
    verify: "Layer 1 has concrete content blocks, not pseudocode"
  - field: layer_2_complete
    verify: "every step has input/action/output/verify fields"
  - field: layer_3_complete
    verify: "every verification line has a command and expected output"
---
# Implementation Plan: Fracture Implementation-Cycle SKILL.md into Phase Files

---

## Goal

Reduce `.claude/skills/implementation-cycle/SKILL.md` from 468 lines to a ~80-line slim router by extracting each phase's behavioral contract into self-contained per-phase files under `phases/` and shared reference material into `reference/`.

---

## Open Decisions

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| No open decisions | — | — | No operator_decisions in WORK-187 frontmatter |

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/skills/implementation-cycle/SKILL.md` | MODIFY | 1 |
| `.claude/skills/implementation-cycle/phases/PLAN.md` | CREATE | 1 |
| `.claude/skills/implementation-cycle/phases/DO.md` | CREATE | 1 |
| `.claude/skills/implementation-cycle/phases/CHECK.md` | CREATE | 1 |
| `.claude/skills/implementation-cycle/phases/DONE.md` | CREATE | 1 |
| `.claude/skills/implementation-cycle/phases/CHAIN.md` | CREATE | 1 |
| `.claude/skills/implementation-cycle/reference/decisions.md` | CREATE | 1 |
| `.claude/skills/implementation-cycle/reference/composition.md` | CREATE | 1 |

### Consumer Files

<!-- Tests that read SKILL.md content and will need updating after fracturing -->

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `tests/test_implementation_cycle_critique.py` | Reads SKILL.md, slices PLAN section between `### 1. PLAN Phase` and `### 2. DO Phase` | 20–61 (full TestImplementationCycleCritiqueGate class) | UPDATE — redirect assertions to `phases/PLAN.md` |
| `tests/test_plan_authoring_agent.py` | Reads SKILL.md for `plan-authoring-agent` and `Task(subagent_type='plan-authoring-agent'` | 77–86 | UPDATE — redirect assertions to `phases/PLAN.md` |
| `tests/test_manifest.py` | Scans `*/SKILL.md` for skill manifest validation | 45–52 | NO UPDATE — passes correctly, acts as deletion safety net |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_implementation_cycle_critique.py` | UPDATE | Redirect from SKILL.md to phases/PLAN.md (content moved) |
| `tests/test_plan_authoring_agent.py` | UPDATE | Redirect from SKILL.md to phases/PLAN.md (content moved) |
| `tests/test_implementation_cycle_fracture.py` | CREATE | New: verify phase files exist, contain required keywords, slim router is ~80 lines |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 8 | Primary Files table (CREATE rows: 5 phase + 2 reference + 1 test) |
| Files to modify | 3 | SKILL.md router + 2 existing test files |
| Tests to write | 1 new test file | test_implementation_cycle_fracture.py |
| Total blast radius | 11 | Sum of all unique files above |

**Note on unwired templates:** `.claude/templates/implementation/{PLAN,DO,CHECK,DONE}.md` are scaffolding templates for work artifacts (not orchestration contracts). Per ADR-048 Note: "They are unwired (no consumer references them) and were created in a weak session. This ADR addresses the orchestration contract (SKILL.md), not the artifact template." These files are NOT modified by this work item.

---

## Layer 1: Specification

### Current State

The monolithic SKILL.md (468 lines, ~21,500 chars) contains all 5 phase behavioral contracts inline. An agent executing any single phase loads all phases. The structure is:

```
### 1. PLAN Phase     (lines 43-145)   ~3,200 chars
### 2. DO Phase       (lines 147-226)  ~3,100 chars
### 3. CHECK Phase    (lines 228-302)  ~3,200 chars
### 4. DONE Phase     (lines 304-327)  ~900 chars
### 5. CHAIN Phase    (lines 329-366)  ~1,200 chars
## Composition Map    (lines 368-380)  ~700 chars
## Quick Reference    (lines 382-407)  ~1,000 chars
## TDD Cycle          (lines 409-424)  ~600 chars
## Governance Events  (lines 426-456)  ~1,200 chars
## Related            (lines 458-469)  ~500 chars
```

**Behavior:** Loading `Skill(skill="implementation-cycle")` loads all 468 lines regardless of current phase.
**Problem:** ~80% of loaded content is dead weight for any single phase invocation. Memory 85815 identifies context-switching token cost as a key overhead.

### Desired State

After fracturing, the directory structure is:

```
.claude/skills/implementation-cycle/
  SKILL.md                    # ~80 lines: router only
  phases/
    PLAN.md                   # Full PLAN behavioral contract (~3,200 chars)
    DO.md                     # Full DO behavioral contract (~3,100 chars)
    CHECK.md                  # Full CHECK behavioral contract (~3,200 chars)
    DONE.md                   # Full DONE behavioral contract (~900 chars)
    CHAIN.md                  # Full CHAIN behavioral contract (~1,200 chars)
  reference/
    decisions.md              # Key Design Decisions, Related links
    composition.md            # Composition Map, Quick Reference, TDD Cycle, Governance Events
```

**Behavior:** Hook system (WORK-188) auto-injects current phase file. SKILL.md router remains valid skill description for Claude Code's skill system.
**Result:** ~80% token reduction per phase invocation. Phase contracts independently maintainable.

### Tests

<!-- TDD: Write these first as RED, then implement files to make them GREEN -->

#### Test 1: Slim Router Line Count
- **file:** `tests/test_implementation_cycle_fracture.py`
- **function:** `test_slim_router_line_count()`
- **setup:** Read `.claude/skills/implementation-cycle/SKILL.md`
- **assertion:** `len(content.splitlines()) <= 100` (target ~80, allow 20 buffer for frontmatter/spacing)

#### Test 2: All Phase Files Exist
- **file:** `tests/test_implementation_cycle_fracture.py`
- **function:** `test_phase_files_exist()`
- **setup:** Construct paths for each phase file
- **assertion:** All 5 phase files exist: `phases/PLAN.md`, `phases/DO.md`, `phases/CHECK.md`, `phases/DONE.md`, `phases/CHAIN.md`

#### Test 3: All Reference Files Exist
- **file:** `tests/test_implementation_cycle_fracture.py`
- **function:** `test_reference_files_exist()`
- **setup:** Construct paths for reference files
- **assertion:** Both reference files exist: `reference/decisions.md`, `reference/composition.md`

#### Test 4: PLAN Phase File Contains Critique Contract
- **file:** `tests/test_implementation_cycle_fracture.py`
- **function:** `test_plan_phase_contains_critique_contract()`
- **setup:** Read `phases/PLAN.md`
- **assertion:** `critique-agent` in content, `PROCEED` in content, `REVISE` in content, `BLOCK` in content

#### Test 5: PLAN Phase File Contains Plan-Authoring-Agent
- **file:** `tests/test_implementation_cycle_fracture.py`
- **function:** `test_plan_phase_contains_authoring_agent()`
- **setup:** Read `phases/PLAN.md`
- **assertion:** `plan-authoring-agent` in content, `Task(subagent_type='plan-authoring-agent'` in content

#### Test 6: Phase Files Are Self-Contained
- **file:** `tests/test_implementation_cycle_fracture.py`
- **function:** `test_phase_files_self_contained()`
- **setup:** Read each phase file
- **assertion:** No phase file contains "see PLAN phase" or "see DO phase" or "see CHECK phase" cross-references (self-containment rule from ADR-048)

#### Test 7: Slim Router Contains Phase Table
- **file:** `tests/test_implementation_cycle_fracture.py`
- **function:** `test_slim_router_has_phase_table()`
- **setup:** Read `SKILL.md`
- **assertion:** Contains `PLAN`, `DO`, `CHECK`, `DONE`, `CHAIN` and the cycle diagram `PLAN --> DO --> CHECK --> DONE --> CHAIN`

### Updated Tests (Consumer File Changes)

#### test_implementation_cycle_critique.py Updates

**Current code (lines 22-37):**
```python
skill_path = Path(".claude/skills/implementation-cycle/SKILL.md")
content = skill_path.read_text()
# ...
plan_section_start = content.index("### 1. PLAN Phase")
do_section_start = content.index("### 2. DO Phase")
plan_section = content[plan_section_start:do_section_start]
assert "critique-agent" in plan_section, ...
```

**Target code:**
```python
# After fracturing, critique content lives in phases/PLAN.md
plan_phase_path = Path(".claude/skills/implementation-cycle/phases/PLAN.md")
content = plan_phase_path.read_text()

# critique-agent must be in the full PLAN phase file
assert "critique-agent" in content, (
    "implementation-cycle phases/PLAN.md must reference critique-agent"
)

# Must describe the revise loop and three verdicts
assert "revise" in content.lower(), "PLAN phase must describe critique-revise loop"
assert "PROCEED" in content, "Must describe PROCEED verdict"
assert "REVISE" in content, "Must describe REVISE verdict"
assert "BLOCK" in content, "Must describe BLOCK verdict"
```

Note: The `plan_section_start`/`do_section_start` slice logic is no longer needed — the entire `phases/PLAN.md` file IS the PLAN phase content.

#### test_plan_authoring_agent.py Updates

**Current code (lines 77-86):**
```python
skill_path = ROOT / ".claude" / "skills" / "implementation-cycle" / "SKILL.md"
content = skill_path.read_text(encoding="utf-8")
assert "plan-authoring-agent" in content, ...
assert "Task(subagent_type='plan-authoring-agent'" in content, ...
```

**Target code:**
```python
# After fracturing, plan-authoring delegation lives in phases/PLAN.md
plan_phase_path = ROOT / ".claude" / "skills" / "implementation-cycle" / "phases" / "PLAN.md"
assert plan_phase_path.exists(), f"Phase file not found: {plan_phase_path}"
content = plan_phase_path.read_text(encoding="utf-8")

assert "plan-authoring-agent" in content, (
    "implementation-cycle phases/PLAN.md must reference plan-authoring-agent"
)
assert "Task(subagent_type='plan-authoring-agent'" in content, (
    "implementation-cycle phases/PLAN.md must contain Task invocation pattern"
)
```

### Design

#### File 1 (MODIFY): `.claude/skills/implementation-cycle/SKILL.md`

The slim router retains: frontmatter, cycle diagram, phase table, "When to Use". Removes all phase content (sections 1-5 with actions/gates/tools), Composition Map, Quick Reference, TDD Cycle, Governance Events, Related.

**Target content (~80 lines):**

```markdown
---
name: implementation-cycle
type: lifecycle
description: HAIOS Implementation Cycle for structured work item implementation. Use
  when starting implementation of a plan. Guides PLAN->DO->CHECK->DONE workflow with
  phase-specific tooling.
recipes:
- node
generated: 2025-12-22
last_updated: '2026-02-22T12:00:00'
---
# Implementation Cycle

This skill defines the PLAN-DO-CHECK-DONE cycle for structured implementation of work items. It composes existing primitives (Skills, Commands, Subagents, Justfile) into a coherent workflow.

## When to Use

**SHOULD** invoke this skill when:
- Starting implementation of a backlog item
- Resuming work on an in-progress item
- Unsure of next step in implementation workflow

**Invocation:** `Skill(skill="implementation-cycle")`

---

## The Cycle

```
PLAN --> DO --> CHECK --> DONE --> CHAIN
  ^       ^       |                  |
  |       +-------+ (if tests fail)  [route next]
  +-- (if no plan)                   |
                              /-------------\
                        type=investigation  has plan?   else
                        OR INV-* prefix        |          |
                               |          implement  work-creation
                          investigation    -cycle     -cycle
                             -cycle
```

## Phase Contracts

Each phase's full behavioral contract is in its own file (ADR-048 progressive disclosure):

| Phase | File | Content |
|-------|------|---------|
| PLAN | `phases/PLAN.md` | Entry gate (critique), plan authoring, exit gates (critique loop, plan-validation, preflight) |
| DO | `phases/DO.md` | Dispatch protocol, TDD enforcement, design-review exit gate |
| CHECK | `phases/CHECK.md` | Test suite, deliverables verification, DoD criteria |
| DONE | `phases/DONE.md` | WHY capture, plan status, documentation |
| CHAIN | `phases/CHAIN.md` | Close work, routing decision table, next cycle invocation |

## Reference

- `reference/decisions.md` — Key design decisions, rationale, related ADRs
- `reference/composition.md` — Composition map, quick reference, TDD cycle, governance events

---

**On Entry (any phase):**
```bash
just set-cycle implementation-cycle {PHASE} {work_id}
```

**On Complete:**
```bash
just clear-cycle
```
```

#### File 2 (CREATE): `.claude/skills/implementation-cycle/phases/PLAN.md`

Full content extracted verbatim from current SKILL.md PLAN phase section plus On Entry command. Self-contained — no cross-phase references.

**Target content (verbatim from SKILL.md lines 43-145):**

```markdown
---
phase: PLAN
skill: implementation-cycle
---
# PLAN Phase

**On Entry:**
```bash
just set-cycle implementation-cycle PLAN {work_id}
```

**Goal:** Verify plan exists and is ready for implementation.

**Entry Gate (MUST): Work Item Critique (S397 Operator Directive)**
Before reading the plan or taking any action, **MUST** invoke critique-agent on the work item:
```
Task(subagent_type='critique-agent', model='sonnet', prompt='Critique work item for correctness: docs/work/active/{backlog_id}/WORK.md ...')
```
- **PROCEED:** Work item is valid. Continue to Actions.
- **REVISE:** Fix identified issues in WORK.md before proceeding.
- **BLOCK:** Fundamental flaws (wrong IDs, nonexistent paths). Fix before any planning.

[... full PLAN section content ...]

**Exit Gate (MUST):**
Gate 1 - Critique, Gate 2 - Plan Validation, Gate 3 - Preflight (full text preserved)

**Tools:** Read, Glob, AskUserQuestion, Task(plan-authoring-agent, model=sonnet), Task(critique-agent, model=sonnet), Task(preflight-checker, model=haiku), Task(plan-validation, model=haiku)
```

Note: DO agent copies EXACT text from SKILL.md lines 43-145 (the PLAN Phase section). No summarization.

#### File 3 (CREATE): `.claude/skills/implementation-cycle/phases/DO.md`

Full content extracted verbatim from SKILL.md DO phase section (lines 147-226).

#### File 4 (CREATE): `.claude/skills/implementation-cycle/phases/CHECK.md`

Full content extracted verbatim from SKILL.md CHECK phase section (lines 228-302).

#### File 5 (CREATE): `.claude/skills/implementation-cycle/phases/DONE.md`

Full content extracted verbatim from SKILL.md DONE phase section (lines 304-327).

#### File 6 (CREATE): `.claude/skills/implementation-cycle/phases/CHAIN.md`

Full content extracted verbatim from SKILL.md CHAIN phase section (lines 329-366).

#### File 7 (CREATE): `.claude/skills/implementation-cycle/reference/decisions.md`

Content from SKILL.md "Related" section (lines 458-469). Also includes ADR-048 rationale for the fracturing decision itself.

**Target content:**

```markdown
---
type: reference
skill: implementation-cycle
---
# Implementation Cycle — Key Design Decisions

## Related

- **ADR-033:** Work Item Lifecycle (DoD criteria)
- **ADR-038:** M2-Governance Symphony Architecture
- **ADR-048:** Progressive Contracts — Phase-Per-File Skill Fracturing (this fracture)
- **E2-108:** Gate Observability (governance event logging)
- **/implement command:** E2-092 will invoke this skill
- **Preflight Checker:** E2-093 will enforce DO phase guardrails
- **Test Runner:** E2-094 for isolated test execution
- **WHY Capturer:** E2-095 for automated learning capture
- **FORESIGHT Prep:** E2-106 adds optional prediction/calibration fields (Epoch 3 bridge)
- **Epoch 3 Spec:** `epoch3/foresight-spec.md` - SIMULATE, INTROSPECT, ANTICIPATE, UPDATE operations

## Fracturing Decision (ADR-048)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Fracture approach | Phase-per-file (Option A) | Dual hook injection means zero agent cognitive overhead; each file independently maintainable |
| Self-containment rule | No cross-phase references allowed | Agent loads only current phase — cross-refs require loading another file, defeating the purpose |
| Content duplication | Acceptable | Duplication is preferable to requiring multi-file reads (CHAIN routing logic may appear in multiple phases) |
| Slim router size | ~80 lines | Enough for cycle diagram + phase table; delegates behavioral contracts to phase files |
| Unwired templates | Not deleted | `.claude/templates/implementation/` are artifact templates, not orchestration contracts (separate concern) |
```

#### File 8 (CREATE): `.claude/skills/implementation-cycle/reference/composition.md`

Content from SKILL.md Composition Map, Quick Reference, TDD Cycle within DO Phase, and Governance Event Logging sections (lines 370-456).

**Target content (verbatim extraction):**

```markdown
---
type: reference
skill: implementation-cycle
---
# Implementation Cycle — Composition and Quick Reference

## Composition Map

| Phase | Primary Tool | Subagent | Command |
|-------|--------------|----------|---------|
| PLAN  | Read, Glob   | plan-authoring-agent (sonnet)*, preflight-checker (haiku) | /new-plan |
| DO    | Write, Edit  | design-review-validation-agent (sonnet, exit gate) | - |
| CHECK | Bash(pytest) | test-runner (haiku), preflight-checker/deliverables (haiku) | /validate |
| DONE  | Edit, Write  | why-capturer | - |
| CHAIN | Bash, Skill  | - | /close |

## Quick Reference

[... full Quick Reference table from SKILL.md ...]

## TDD Cycle Within DO Phase

[... full TDD cycle content from SKILL.md ...]

## Governance Event Logging (E2-108)

[... full Governance Events content from SKILL.md ...]
```

#### File 9 (CREATE): `tests/test_implementation_cycle_fracture.py`

```python
# generated: 2026-02-22
# WORK-187: Fracture Implementation-Cycle SKILL.md into Phase Files
"""
Tests for WORK-187: Phase-per-file fracturing of implementation-cycle SKILL.md.

Verifies:
1. Slim router line count <= 100
2. All 5 phase files exist under phases/
3. Both reference files exist under reference/
4. PLAN phase file contains critique contract (moved from SKILL.md)
5. PLAN phase file contains plan-authoring-agent delegation
6. Phase files are self-contained (no cross-phase references)
7. Slim router retains cycle diagram and phase table
"""

from pathlib import Path

SKILL_DIR = Path(".claude/skills/implementation-cycle")


class TestSlimRouter:
    """Verify the slim SKILL.md router meets size and content constraints."""

    def test_slim_router_line_count(self):
        """Slim router must be <= 100 lines (target ~80)."""
        skill_path = SKILL_DIR / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        line_count = len(content.splitlines())
        assert line_count <= 100, (
            f"Slim router is {line_count} lines — must be <= 100. "
            "Phase content should be in phases/ files."
        )

    def test_slim_router_has_cycle_diagram(self):
        """Slim router must retain the PLAN->DO->CHECK->DONE->CHAIN cycle diagram."""
        skill_path = SKILL_DIR / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        assert "PLAN --> DO --> CHECK --> DONE --> CHAIN" in content, (
            "Slim router must contain the cycle diagram"
        )

    def test_slim_router_has_phase_table(self):
        """Slim router must contain a phase table referencing phase files."""
        skill_path = SKILL_DIR / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        for phase in ["PLAN", "DO", "CHECK", "DONE", "CHAIN"]:
            assert phase in content, f"Slim router must reference {phase} phase"
        assert "phases/" in content, "Slim router must reference phases/ directory"


class TestPhaseFilesExist:
    """Verify all required phase files exist."""

    def test_plan_phase_exists(self):
        assert (SKILL_DIR / "phases" / "PLAN.md").exists()

    def test_do_phase_exists(self):
        assert (SKILL_DIR / "phases" / "DO.md").exists()

    def test_check_phase_exists(self):
        assert (SKILL_DIR / "phases" / "CHECK.md").exists()

    def test_done_phase_exists(self):
        assert (SKILL_DIR / "phases" / "DONE.md").exists()

    def test_chain_phase_exists(self):
        assert (SKILL_DIR / "phases" / "CHAIN.md").exists()


class TestReferenceFilesExist:
    """Verify all required reference files exist."""

    def test_decisions_reference_exists(self):
        assert (SKILL_DIR / "reference" / "decisions.md").exists()

    def test_composition_reference_exists(self):
        assert (SKILL_DIR / "reference" / "composition.md").exists()


class TestPlanPhaseContent:
    """Verify PLAN phase file contains required content (moved from SKILL.md)."""

    def test_plan_phase_contains_critique_contract(self):
        """PLAN phase must contain critique-agent reference."""
        content = (SKILL_DIR / "phases" / "PLAN.md").read_text(encoding="utf-8")
        assert "critique-agent" in content, (
            "phases/PLAN.md must reference critique-agent"
        )

    def test_plan_phase_contains_critique_verdicts(self):
        """PLAN phase must describe all three critique verdicts."""
        content = (SKILL_DIR / "phases" / "PLAN.md").read_text(encoding="utf-8")
        assert "revise" in content.lower(), "PLAN phase must describe critique-revise loop"
        assert "PROCEED" in content, "Must describe PROCEED verdict"
        assert "REVISE" in content, "Must describe REVISE verdict"
        assert "BLOCK" in content, "Must describe BLOCK verdict"

    def test_plan_phase_contains_authoring_agent(self):
        """PLAN phase must contain plan-authoring-agent delegation."""
        content = (SKILL_DIR / "phases" / "PLAN.md").read_text(encoding="utf-8")
        assert "plan-authoring-agent" in content, (
            "phases/PLAN.md must reference plan-authoring-agent"
        )
        assert "Task(subagent_type='plan-authoring-agent'" in content, (
            "phases/PLAN.md must contain Task invocation pattern"
        )


class TestSelfContainment:
    """Verify phase files have no cross-phase references (ADR-048 self-containment rule)."""

    CROSS_PHASE_PATTERNS = [
        "see PLAN phase",
        "see DO phase",
        "see CHECK phase",
        "see DONE phase",
        "see CHAIN phase",
    ]

    def _check_phase(self, phase_name: str):
        content = (SKILL_DIR / "phases" / f"{phase_name}.md").read_text(encoding="utf-8")
        for pattern in self.CROSS_PHASE_PATTERNS:
            assert pattern.lower() not in content.lower(), (
                f"phases/{phase_name}.md contains cross-phase reference: '{pattern}'. "
                "Phase files must be self-contained (ADR-048)."
            )

    def test_plan_self_contained(self):
        self._check_phase("PLAN")

    def test_do_self_contained(self):
        self._check_phase("DO")

    def test_check_self_contained(self):
        self._check_phase("CHECK")

    def test_done_self_contained(self):
        self._check_phase("DONE")

    def test_chain_self_contained(self):
        self._check_phase("CHAIN")
```

### Call Chain

```
Skill(skill="implementation-cycle")
    |
    +-> SKILL.md (slim router, ~80 lines)
    |       Contains: cycle diagram, phase table, "When to Use"
    |
    +-> phases/PLAN.md    (loaded by hook on PLAN entry)
    +-> phases/DO.md      (loaded by hook on DO entry)
    +-> phases/CHECK.md   (loaded by hook on CHECK entry)
    +-> phases/DONE.md    (loaded by hook on DONE entry)
    +-> phases/CHAIN.md   (loaded by hook on CHAIN entry)
    |
    +-> reference/decisions.md   (loaded on demand)
    +-> reference/composition.md (loaded on demand)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Verbatim extraction | Copy phase content exactly from SKILL.md | No risk of behavioral drift — content is reorganized not rewritten |
| Test migration strategy | Update existing tests to read phases/PLAN.md | Tests assert on the same behavioral contracts, just in new location |
| New test file | test_implementation_cycle_fracture.py | Verifies structural properties (file existence, line count, self-containment) that are orthogonal to behavioral contract tests |
| Self-containment enforcement | No cross-phase text like "see PLAN phase" | ADR-048 rule: agent loading one phase must not need another phase file |
| Unwired templates untouched | Leave `.claude/templates/implementation/` as-is | ADR-048 explicitly calls these a separate concern (artifact templates vs orchestration contracts) |
| Slim router size limit | 100 lines max (target 80) | 80-line target from ADR-048; 20-line buffer for frontmatter and spacing variation |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| SKILL.md still needed by skill system | Slim router is valid skill description | Test 7 (phase table present) |
| Existing tests break | Update 2 test files to read phases/PLAN.md | Tests 4, 5 (via updated test files) |
| Phase content duplication (CHAIN routing) | Acceptable per ADR-048 | Test 6 (self-containment, not no-duplication) |
| Cross-phase references | Prohibited by ADR-048 self-containment rule | Test 6 |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Behavioral drift during extraction | H | Verbatim copy of phase content — no paraphrasing, no rewriting |
| Test file updates miss edge cases | M | Run full `pytest tests/ -v` after all changes; compare to baseline 1571 passed |
| Slim router too large | L | Test 1 enforces <= 100 lines; target is 80 |
| Self-containment violation introduced | M | Test 6 catches "see X phase" patterns across all 5 phase files |
| Unwired templates confused with phase files | L | ADR-048 note explicitly distinguishes them; this plan doesn't touch them |
| Interim context gap (WORK-187 shipped, WORK-188 not yet) | H | Between WORK-187 and WORK-188, agents see only slim router without phase auto-injection. Do NOT re-expand SKILL.md. WORK-188 delivers phase injection. Document in session checkpoint. |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Create `tests/test_implementation_cycle_fracture.py` from Layer 1 Tests section. Run `pytest tests/test_implementation_cycle_fracture.py -v` — all tests should FAIL (phase files don't exist yet).
- **output:** Test file exists, all tests fail with FileNotFoundError or AssertionError
- **verify:** `pytest tests/test_implementation_cycle_fracture.py -v 2>&1 | grep -c "FAILED\|ERROR"` >= 7

### Step 2: Create phases/ directory and extract phase files (GREEN)
- **spec_ref:** Layer 1 > Design > Files 2-6 (PLAN.md, DO.md, CHECK.md, DONE.md, CHAIN.md)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Create `.claude/skills/implementation-cycle/phases/` directory. Extract each phase section verbatim from current SKILL.md into the corresponding phase file. Add minimal frontmatter (phase, skill fields). Add `On Entry:` bash command at top of each phase file (from SKILL.md). Exclude trailing `---` document-level separators from each extracted phase file — these are SKILL.md structural dividers, not phase content.
- **output:** 5 phase files exist with full behavioral contract content
- **verify:** `ls .claude/skills/implementation-cycle/phases/` shows PLAN.md, DO.md, CHECK.md, DONE.md, CHAIN.md

### Step 3: Create reference/ directory and extract reference files
- **spec_ref:** Layer 1 > Design > Files 7-8 (decisions.md, composition.md)
- **input:** Step 2 complete
- **action:** Create `.claude/skills/implementation-cycle/reference/` directory. Extract Composition Map, Quick Reference, TDD Cycle, Governance Events into `reference/composition.md`. Extract Related section plus ADR-048 fracturing rationale into `reference/decisions.md`.
- **output:** 2 reference files exist
- **verify:** `ls .claude/skills/implementation-cycle/reference/` shows decisions.md, composition.md

### Step 4: Slim down SKILL.md router
- **spec_ref:** Layer 1 > Design > File 1 (SKILL.md)
- **input:** Step 3 complete (all content extracted to phase/reference files)
- **action:** Rewrite SKILL.md to slim router (~80 lines). Keep: frontmatter, "When to Use", cycle diagram, phase table with links to phases/ files, reference section. Remove: all inline phase content (sections 1-5), Composition Map, Quick Reference, TDD Cycle, Governance Events, Related.
- **output:** SKILL.md is <= 100 lines, contains phase table
- **verify:** `wc -l .claude/skills/implementation-cycle/SKILL.md` <= 100

### Step 5: Update test_implementation_cycle_critique.py
- **spec_ref:** Layer 1 > Design > Updated Tests section (test_implementation_cycle_critique.py)
- **input:** Step 4 complete (SKILL.md no longer has PLAN section inline)
- **action:** Update `tests/test_implementation_cycle_critique.py` to read `phases/PLAN.md` instead of slicing SKILL.md. Remove `plan_section_start`/`do_section_start` slice logic. Keep all assertions (same content now in phases/PLAN.md).
- **output:** test_implementation_cycle_critique.py reads phases/PLAN.md
- **verify:** `grep "phases/PLAN.md" tests/test_implementation_cycle_critique.py` returns 1+ match

### Step 6: Update test_plan_authoring_agent.py
- **spec_ref:** Layer 1 > Design > Updated Tests section (test_plan_authoring_agent.py)
- **input:** Step 5 complete
- **action:** Update `tests/test_plan_authoring_agent.py` `test_implementation_cycle_delegates_to_subagent` test to read `phases/PLAN.md` instead of SKILL.md. Keep assertions (same content, new location).
- **output:** test_plan_authoring_agent.py reads phases/PLAN.md
- **verify:** `grep "phases/PLAN.md" tests/test_plan_authoring_agent.py` returns 1+ match

### Step 7: Run full test suite (VERIFY)
- **spec_ref:** Layer 0 > Test Files + Ground Truth Verification
- **input:** Steps 1-6 complete
- **action:** Run `pytest tests/ -v`
- **output:** All tests pass, no regressions
- **verify:** `pytest tests/ -v 2>&1 | tail -5` shows `1571+ passed, 0 failed` (or same baseline count)

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_implementation_cycle_fracture.py -v` | 18 passed, 0 failed |
| `pytest tests/test_implementation_cycle_critique.py -v` | 4 passed, 0 failed |
| `pytest tests/test_plan_authoring_agent.py -v` | 4 passed, 0 failed |
| `pytest tests/ -v` | 1571+ passed, 0 failed (no regressions) |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| Slim router SKILL.md (~80 lines) | `wc -l .claude/skills/implementation-cycle/SKILL.md` | <= 100 lines |
| phases/PLAN.md exists | `ls .claude/skills/implementation-cycle/phases/PLAN.md` | File found |
| phases/DO.md exists | `ls .claude/skills/implementation-cycle/phases/DO.md` | File found |
| phases/CHECK.md exists | `ls .claude/skills/implementation-cycle/phases/CHECK.md` | File found |
| phases/DONE.md exists | `ls .claude/skills/implementation-cycle/phases/DONE.md` | File found |
| phases/CHAIN.md exists | `ls .claude/skills/implementation-cycle/phases/CHAIN.md` | File found |
| reference/decisions.md exists | `ls .claude/skills/implementation-cycle/reference/decisions.md` | File found |
| reference/composition.md exists | `ls .claude/skills/implementation-cycle/reference/composition.md` | File found |
| All existing tests pass | `pytest tests/ -v 2>&1 \| grep -E "passed\|failed"` | 0 failed |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| test_critique updated to phases/ | `grep "phases/PLAN.md" tests/test_implementation_cycle_critique.py` | 1+ match |
| test_authoring_agent updated to phases/ | `grep "phases/PLAN.md" tests/test_plan_authoring_agent.py` | 1+ match |
| No stale SKILL.md content assertions | `pytest tests/test_implementation_cycle_critique.py -v` | 0 failed |
| PLAN phase self-contained | `grep -i "see plan phase" .claude/skills/implementation-cycle/phases/DO.md` | 0 matches |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 7 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] No stale references to SKILL.md phase content in tests
- [ ] Phase files are self-contained (no cross-phase references)
- [ ] WHY captured (memory_refs populated via ingester_ingest)
- [ ] KNOWN INTERIM STATE documented: Between WORK-187 merge and WORK-188 ship, agents see only slim router. Do NOT re-expand SKILL.md. WORK-188 delivers phase injection.
- [ ] ADR-048 status updated to accepted (operator ratified S421)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- `docs/ADR/ADR-048-progressive-contracts-phase-per-file-skill-fracturing.md`
- `.claude/skills/implementation-cycle/SKILL.md` (source of truth for phase content to extract)
- Memory 85815: Context-switching token cost dimension
- `tests/test_implementation_cycle_critique.py` (consumer to update)
- `tests/test_plan_authoring_agent.py` (consumer to update)

---
