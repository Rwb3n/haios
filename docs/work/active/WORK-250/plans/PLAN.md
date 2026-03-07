---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-03-07
backlog_id: WORK-250
title: "Tier-Aware Gate Skipping — Proportional Ceremony Enforcement"
author: Hephaestus
lifecycle_phase: plan
session: 473
generated: 2026-03-07
last_updated: 2026-03-07T15:41:10

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-250/WORK.md"
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
# Implementation Plan: Tier-Aware Gate Skipping — Proportional Ceremony Enforcement

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification.

     SKIP RATIONALE: If ANY section is omitted, provide one-line rationale:
     **SKIPPED:** [reason] -->

---

## Goal

Modify `.claude/skills/implementation-cycle/phases/PLAN.md` so that the three exit gates (critique, plan-validation, preflight) are conditionally applied based on the work item's governance tier, eliminating unnecessary ceremony for trivial and small work items and directly addressing the 104% context budget problem (mem:85606).

---

## Open Decisions

<!-- No operator_decisions were present in WORK-250 WORK.md frontmatter. -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Where to enforce gate skipping | Skill-level (PLAN.md text) vs Hook-level (PreToolUse) vs Both | Skill-level only | critique_injector.py already handles critique injection at hook level. The other two gates (plan-validation, preflight) have no hook-level wiring — skill text is the only enforcement path. Hook-level is complementary but out of scope here. |
| How agent reads tier | detect_tier() call vs read effort field directly | Read effort field from WORK.md directly | Agent cannot call Python functions. Skill instructions must be executable by an LLM. The agent reads WORK.md frontmatter `effort` field and `source_files` list length to determine tier, matching the same logic as detect_tier(). |
| Tier determination scope | Full detect_tier() logic vs simplified effort-only check | Simplified tier lookup based on effort + source_files + type + traces_to | Agent reads WORK.md (already required at PLAN entry), applies the same predicate rules tier_detector.py uses. No new reads required. |

---

## Layer 0: Inventory

<!-- MUST complete before any design work. Map the blast radius.
     Producer: plan-author agent
     Consumer: all downstream agents (DO, CHECK, critique) -->

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/skills/implementation-cycle/phases/PLAN.md` | MODIFY | 1 |

### Consumer Files

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `tests/test_plan_phase_gates.py` | New test file validating gate skip text | new | CREATE |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_plan_phase_gates.py` | CREATE | New test file — validates PLAN.md skill text contains tier-conditional gate instructions |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 1 | Test Files table (CREATE rows) |
| Files to modify | 1 | Primary Files table (MODIFY rows) |
| Tests to write | 5 | Test Files table |
| Total blast radius | 2 | Sum of all unique files above |

---

## Layer 1: Specification

<!-- The contract that the DO agent implements.
     Producer: plan-author agent
     Consumer: DO agent

     MUST INCLUDE:
     1. Actual current code that will be changed (copy from source)
     2. Exact target code (not pseudocode)
     3. Function signatures with types
     4. Input/output examples with REAL system data -->

### Current State

```markdown
# .claude/skills/implementation-cycle/phases/PLAN.md  lines 61-104

**Exit Criteria:**
- [ ] **MUST:** Work item critique passed (Entry Gate — S397)
- [ ] Plan file exists with complete design
- [ ] **MUST:** Referenced specifications read and verified against plan
- [ ] Tests defined in "Tests First" section
- [ ] Current/Desired state documented
- [ ] (Optional) foresight_prep captured with prediction
- [ ] **MUST:** Invoke critique-agent and pass critique-revise loop (see Exit Gate). Minimum 2 passes when REVISE — S397.
- [ ] **MUST:** Invoke plan-validation as haiku subagent (Gate 2 — S397)
- [ ] **MUST:** Invoke preflight-checker as haiku subagent (Gate 3 — S397)

**Exit Gate (MUST):**
Before transitioning to DO phase, execute these three gates in order:

**Gate 1 - MUST: Critique (Assumption Surfacing)**
Invoke critique-agent to surface implicit assumptions on the raw plan:
```
Task(subagent_type='critique-agent', prompt='Critique plan: docs/work/active/{backlog_id}/plans/PLAN.md')
```

Apply critique-revise loop based on verdict:
- **PROCEED on first pass:** All assumptions mitigated. Continue to Gate 2. (Only case where single pass is sufficient.)
- **REVISE:** Flagged assumptions exist. Revise plan to address them, then **MUST** re-invoke critique to verify revisions. Minimum 2 passes when first verdict is REVISE — a single REVISE→address→proceed is insufficient. The revision must be re-verified by critique-agent. Repeat until PROCEED or max 3 iterations (then escalate to operator via AskUserQuestion).
- **BLOCK:** Unmitigated low-confidence assumptions. Return to plan-authoring-cycle. DO phase blocked.

> **S397 Operator Directive:** NEVER accept a single critique pass when verdict is REVISE. The agent addressing findings is not the same as the agent verifying they were addressed. Minimum 2 passes enforced.

> Critique runs BEFORE validation so assumptions are surfaced on the raw plan, not one already "blessed" by structural checks. This prevents the S343 anti-pattern where validation momentum caused critique to be skipped.

**Gate 2 - MUST: Plan Validation (as haiku subagent — S397 Operator Directive)**
```
Task(subagent_type='preflight-checker', model='haiku', prompt='Run plan-validation-cycle for {backlog_id}. Plan: docs/work/active/{backlog_id}/plans/PLAN.md. Check: all required sections present, no placeholders. Spec-align: read all referenced specs and verify plan matches. Validate: quality checks, no [BLOCKED] in Open Decisions. Report pass/fail with specifics.')
```
Validates structural completeness and quality. Runs CHECK → SPEC_ALIGN → VALIDATE → APPROVE logic. Delegated to haiku subagent to save main context tokens — these are structural checks, not judgment calls.

> **S397 Operator Directive:** Plan validation is structural, not cognitive. MUST run as haiku subagent, not inline. Saves ~5k+ main context tokens per invocation.

**Gate 3 - MUST: Preflight Check (as haiku subagent — S397 Operator Directive)**
```
Task(subagent_type='preflight-checker', model='haiku', prompt='Check plan readiness for {backlog_id}. Plan: docs/work/active/{backlog_id}/plans/PLAN.md. Work item: docs/work/active/{backlog_id}/WORK.md. Verify plan is complete and ready for DO phase.')
```
Validates plan completeness and file scope. DO phase is blocked until all three gates pass.
```

**Behavior:** All three gates are MUST/unconditional for every work item entering the PLAN phase. No tier awareness exists.

**Problem:** Trivial and small work items spend disproportionate context on ceremony gates that exist to protect against risks not present at their scale (no ADR, no architectural decisions, 1-3 source files). This directly causes 104% context budget overruns (mem:85606) for text-only or metadata-only work items.

### Desired State

The PLAN.md skill file Exit Gate section is replaced with a tier-aware version. The agent reads the work item's tier-determining fields at PLAN entry (effort, source_files count, type, traces_to) and follows the appropriate gate set.

**Tier Gate Matrix (authoritative):**

| Tier | Predicates | Gate 1: Critique | Gate 2: Plan-Validation | Gate 3: Preflight |
|------|------------|-----------------|------------------------|-------------------|
| trivial | effort=small, source_files<=2, no ADR, type!=design | SKIP | SKIP | SKIP |
| small | effort=small, source_files<=3, no ADR, type!=design | RUN (checklist mode) | SKIP | SKIP |
| standard | default | RUN (full subagent) | RUN | RUN |
| architectural | type=design OR ADR in traces_to | RUN (opus + operator) | RUN | RUN |

**Target Exit Criteria section** (replace lines 61-70 of PLAN.md):

```markdown
**Exit Criteria:**
- [ ] **MUST:** Work item critique passed (Entry Gate — S397)
- [ ] Plan file exists with complete design
- [ ] **MUST:** Referenced specifications read and verified against plan
- [ ] Tests defined in "Tests First" section
- [ ] Current/Desired state documented
- [ ] (Optional) foresight_prep captured with prediction
- [ ] **Tier-aware:** Exit gates applied per tier (see Exit Gate below)
```

**Target Exit Gate section** (replace lines 72-104 of PLAN.md):

```markdown
**Exit Gate (Tier-Aware — REQ-LIFECYCLE-005, REQ-CEREMONY-005):**

Before transitioning to DO phase, determine the work item's governance tier, then apply the appropriate gate set.

**Step 1: Determine Tier**

Read `docs/work/active/{backlog_id}/WORK.md` frontmatter (already read at PLAN entry) and classify:

| Tier | Conditions |
|------|-----------|
| **architectural** | `type: design` OR any entry in `traces_to` starts with `ADR-` |
| **trivial** | `effort: small` AND `source_files` has 1-2 entries AND not architectural |
| **small** | `effort: small` AND `source_files` has 1-3 entries AND not architectural |
| **standard** | All other cases (default — conservative) |

> **Note:** Architectural is checked first (escalation always wins). Absent or empty `source_files` defaults to **standard** per REQ-LIFECYCLE-005 invariant: "Absent data MUST NOT produce a more permissive classification."

**Step 2: Apply Gate Set**

**If tier = trivial:**
> All exit gates SKIPPED. Trivial work items have no architectural decisions, no plan complexity requiring independent validation, and no source-file scope requiring preflight. Rationale: REQ-CEREMONY-005 (ceremony depth scales proportionally: none→checklist→full→operator). Gate-skip governance events are logged by the hook layer (PostToolUse observes PLAN→DO transition; critique_injector.py logs CritiqueInjected events for non-trivial tiers).

**If tier = small:**
> Gate 1 (Critique) runs in checklist mode — no subagent, inline self-check only. Verify:
> - [ ] All acceptance criteria are achievable with current design
> - [ ] Source files referenced in WORK.md exist and are correct
> - [ ] No implicit assumptions about interfaces or data formats
> - [ ] Edge cases identified (empty inputs, missing files, permission errors)
> - [ ] Fail-permissive pattern applied where appropriate
>
> Gate 2 (Plan-Validation) SKIPPED. Gate 3 (Preflight) SKIPPED.
> Rationale: Small items have 1-3 source files and no ADR. Structural validation overhead exceeds protection benefit.
> **Note:** critique_injector.py hook may also inject this same checklist via additionalContext. If you see the checklist in both the hook injection and this skill text, run it once (they are the same check).

**If tier = standard:**

**Gate 1 - MUST: Critique (Assumption Surfacing)**
Invoke critique-agent to surface implicit assumptions on the raw plan:
```
Task(subagent_type='critique-agent', model='sonnet', prompt='Critique plan: docs/work/active/{backlog_id}/plans/PLAN.md')
```

Apply critique-revise loop based on verdict:
- **PROCEED on first pass:** All assumptions mitigated. Continue to Gate 2.
- **REVISE:** Flagged assumptions exist. Revise plan to address them, then **MUST** re-invoke critique to verify revisions. Minimum 2 passes when first verdict is REVISE. Repeat until PROCEED or max 3 iterations (then escalate to operator via AskUserQuestion).
- **BLOCK:** Unmitigated low-confidence assumptions. Return to plan-authoring-cycle. DO phase blocked.

> **S397 Operator Directive:** NEVER accept a single critique pass when verdict is REVISE.

**Gate 2 - MUST: Plan Validation (as haiku subagent — S397 Operator Directive)**
```
Task(subagent_type='preflight-checker', model='haiku', prompt='Run plan-validation-cycle for {backlog_id}. Plan: docs/work/active/{backlog_id}/plans/PLAN.md. Check: all required sections present, no placeholders. Spec-align: read all referenced specs and verify plan matches. Validate: quality checks, no [BLOCKED] in Open Decisions. Report pass/fail with specifics.')
```

**Gate 3 - MUST: Preflight Check (as haiku subagent — S397 Operator Directive)**
```
Task(subagent_type='preflight-checker', model='haiku', prompt='Check plan readiness for {backlog_id}. Plan: docs/work/active/{backlog_id}/plans/PLAN.md. Work item: docs/work/active/{backlog_id}/WORK.md. Verify plan is complete and ready for DO phase.')
```

**If tier = architectural:**

Same as standard (Gates 1+2+3), PLUS:

**Gate 4 - MUST: Operator Approval**
After Gate 3 passes, invoke operator confirmation:
```
AskUserQuestion(questions=[{"question": "Architectural work item {backlog_id} has passed all 3 automated gates. Confirm approach and approve DO phase.", "header": "Operator Approval Required", "options": [{"label": "Approved — proceed to DO phase"}, {"label": "BLOCK — revise plan first"}], "multiSelect": false}])
```
> Gate 4 was implicit before (mentioned in critique_injector.py TIER_INJECTIONS). Now explicit in skill text.
```

**Behavior after change:** Agent reads tier at PLAN entry (no new files needed — WORK.md already read), applies proportional gate set. Trivial items enter DO phase immediately after plan authoring; small items run a 30-second inline checklist; standard/architectural items run the full gate sequence.

**Result:** Context budget for trivial/small items reduced by ~3-5k tokens (elimination of 2-3 subagent invocations). Addresses mem:85606.

### Tests

<!-- Write test specs BEFORE implementation code.
     Tests here verify the PLAN.md skill TEXT contains correct tier-conditional content.
     This is a skill/markdown verification pattern — not Python unit tests for logic.
     The logic (detect_tier) is already tested in test_tier_detector.py. -->

#### Test 1: PLAN.md Contains Tier Gate Matrix
- **file:** `tests/test_plan_phase_gates.py`
- **function:** `test_plan_md_contains_tier_gate_matrix()`
- **setup:** Read `.claude/skills/implementation-cycle/phases/PLAN.md` as text
- **assertion:** Text contains "trivial" AND "small" AND "standard" AND "architectural" in the Exit Gate section; text contains "SKIP" for trivial gates; text contains the tier determination table

#### Test 2: Trivial Tier Has All Gates Skipped
- **file:** `tests/test_plan_phase_gates.py`
- **function:** `test_plan_md_trivial_all_gates_skipped()`
- **setup:** Read PLAN.md text, locate the trivial tier section
- **assertion:** After "If tier = trivial" heading, text contains "SKIPPED" (all 3 gates) and does NOT contain a Task() invocation for critique-agent, plan-validation, or preflight-checker

#### Test 3: Small Tier Has Only Inline Checklist (No Subagents)
- **file:** `tests/test_plan_phase_gates.py`
- **function:** `test_plan_md_small_tier_inline_checklist_only()`
- **setup:** Read PLAN.md text, locate the small tier section
- **assertion:** After "If tier = small" heading, text contains checklist items ("acceptance criteria", "Source files referenced") and does NOT contain `Task(subagent_type='critique-agent'` or `Task(subagent_type='preflight-checker'`

#### Test 4: Standard Tier Has All Three Gates
- **file:** `tests/test_plan_phase_gates.py`
- **function:** `test_plan_md_standard_tier_has_three_gates()`
- **setup:** Read PLAN.md text, locate the standard tier section
- **assertion:** After "If tier = standard" heading, text contains "Gate 1", "Gate 2", "Gate 3", and Task() invocations for critique-agent AND preflight-checker (plan-validation and preflight)

#### Test 5: Architectural Tier Has Gate 4 Operator Approval
- **file:** `tests/test_plan_phase_gates.py`
- **function:** `test_plan_md_architectural_tier_has_operator_approval()`
- **setup:** Read PLAN.md text, locate the architectural tier section
- **assertion:** After "If tier = architectural" heading, text contains "Gate 4" AND "AskUserQuestion" AND "Operator Approval"

### Design

#### File 1 (MODIFY): `.claude/skills/implementation-cycle/phases/PLAN.md`

**Location:** Lines 61-104 (Exit Criteria and Exit Gate sections)

**Current Code (lines 61-70):**
```markdown
**Exit Criteria:**
- [ ] **MUST:** Work item critique passed (Entry Gate — S397)
- [ ] Plan file exists with complete design
- [ ] **MUST:** Referenced specifications read and verified against plan
- [ ] Tests defined in "Tests First" section
- [ ] Current/Desired state documented
- [ ] (Optional) foresight_prep captured with prediction
- [ ] **MUST:** Invoke critique-agent and pass critique-revise loop (see Exit Gate). Minimum 2 passes when REVISE — S397.
- [ ] **MUST:** Invoke plan-validation as haiku subagent (Gate 2 — S397)
- [ ] **MUST:** Invoke preflight-checker as haiku subagent (Gate 3 — S397)
```

**Target Code (lines 61-70 replacement):**
```markdown
**Exit Criteria:**
- [ ] **MUST:** Work item critique passed (Entry Gate — S397)
- [ ] Plan file exists with complete design
- [ ] **MUST:** Referenced specifications read and verified against plan
- [ ] Tests defined in "Tests First" section
- [ ] Current/Desired state documented
- [ ] (Optional) foresight_prep captured with prediction
- [ ] **Tier-aware:** Exit gates applied per tier (see Exit Gate below — REQ-LIFECYCLE-005)
```

**Current Code (lines 72-104):**
```markdown
**Exit Gate (MUST):**
Before transitioning to DO phase, execute these three gates in order:
[... unconditional Gate 1 + Gate 2 + Gate 3 as shown in Current State above ...]
```

**Target Code (lines 72-end replacement):** The full tier-aware Exit Gate block shown in Desired State above. The complete replacement text is specified in Layer 1 > Desired State > "Target Exit Gate section".

**Diff summary:**
```diff
-**Exit Gate (MUST):**
-Before transitioning to DO phase, execute these three gates in order:
+**Exit Gate (Tier-Aware — REQ-LIFECYCLE-005, REQ-CEREMONY-005):**
+
+Before transitioning to DO phase, determine the work item's governance tier, then apply the appropriate gate set.
+
+**Step 1: Determine Tier**
+[... tier table ...]
+
+**Step 2: Apply Gate Set**
+
+**If tier = trivial:**
+> All exit gates SKIPPED. [...]
+
+**If tier = small:**
+> Gate 1 (Critique) runs in checklist mode — no subagent, inline self-check only. [...]
+> Gate 2 (Plan-Validation) SKIPPED. Gate 3 (Preflight) SKIPPED.
+
+**If tier = standard:**
+**Gate 1 - MUST: Critique [...]**
+**Gate 2 - MUST: Plan Validation [...]**
+**Gate 3 - MUST: Preflight Check [...]**
+
+**If tier = architectural:**
+Same as standard (Gates 1+2+3), PLUS:
+**Gate 4 - MUST: Operator Approval [...]**
```

#### File 2 (CREATE): `tests/test_plan_phase_gates.py`

```python
# generated: 2026-03-07
"""
Tests for tier-aware gate skipping in PLAN phase skill (WORK-250).

Verifies that .claude/skills/implementation-cycle/phases/PLAN.md contains
tier-conditional gate instructions per REQ-LIFECYCLE-005 / REQ-CEREMONY-005.

These are skill TEXT verification tests — not logic unit tests.
The underlying tier detection logic is tested in test_tier_detector.py.

Pattern: read file as text, assert structural content per tier section.
"""
from pathlib import Path

import pytest

# Path to the PLAN.md skill file under test
PLAN_MD_PATH = (
    Path(__file__).parent.parent
    / ".claude"
    / "skills"
    / "implementation-cycle"
    / "phases"
    / "PLAN.md"
)


@pytest.fixture(scope="module")
def plan_md_text():
    """Read PLAN.md skill file once for all tests in this module."""
    return PLAN_MD_PATH.read_text(encoding="utf-8")


def _section_after(text: str, heading: str) -> str:
    """Extract text after a heading until the next heading of same/higher level."""
    idx = text.find(heading)
    if idx == -1:
        return ""
    # Find next "**If tier" or "**Gate" heading after the section start
    after = text[idx + len(heading):]
    # Find the next section boundary (next "**If tier" heading)
    next_section = after.find("\n**If tier")
    if next_section != -1:
        return after[:next_section]
    return after


class TestTierGateMatrix:
    """Test 1: PLAN.md contains the tier gate matrix."""

    def test_plan_md_contains_tier_gate_matrix(self, plan_md_text):
        """Exit Gate section must include tier determination table."""
        assert "Tier-Aware" in plan_md_text, (
            "Exit Gate section must be labeled Tier-Aware"
        )
        assert "Step 1: Determine Tier" in plan_md_text, (
            "Must have Step 1: Determine Tier"
        )
        assert "Step 2: Apply Gate Set" in plan_md_text, (
            "Must have Step 2: Apply Gate Set"
        )
        # All four tiers must appear in the gate section
        gate_section_start = plan_md_text.find("Exit Gate (Tier-Aware")
        assert gate_section_start != -1, "Exit Gate (Tier-Aware) section not found"
        gate_section = plan_md_text[gate_section_start:]
        for tier in ("trivial", "small", "standard", "architectural"):
            assert tier in gate_section, f"Tier '{tier}' not found in gate section"


class TestTrivialTierGateSkip:
    """Test 2: Trivial tier skips all three gates."""

    def test_plan_md_trivial_all_gates_skipped(self, plan_md_text):
        """After 'If tier = trivial', all gates must be marked SKIPPED."""
        trivial_section = _section_after(plan_md_text, "If tier = trivial")
        assert trivial_section != "", "Trivial tier section not found"
        assert "SKIPPED" in trivial_section or "SKIP" in trivial_section, (
            "Trivial section must indicate gates are skipped"
        )
        # Must NOT invoke any subagent Task() for gates
        assert "Task(subagent_type='critique-agent'" not in trivial_section, (
            "Trivial tier must not invoke critique-agent subagent"
        )
        assert "Task(subagent_type='preflight-checker'" not in trivial_section, (
            "Trivial tier must not invoke preflight-checker subagent"
        )


class TestSmallTierInlineChecklist:
    """Test 3: Small tier has only inline checklist, no subagents."""

    def test_plan_md_small_tier_inline_checklist_only(self, plan_md_text):
        """After 'If tier = small', Gate 1 is inline checklist, Gates 2+3 skipped."""
        small_section = _section_after(plan_md_text, "If tier = small")
        assert small_section != "", "Small tier section not found"
        # Must have inline checklist items
        assert "acceptance criteria" in small_section.lower(), (
            "Small tier must include inline checklist with acceptance criteria check"
        )
        # Must NOT invoke critique-agent or preflight-checker subagents
        assert "Task(subagent_type='critique-agent'" not in small_section, (
            "Small tier must not invoke critique-agent as subagent"
        )
        assert "Task(subagent_type='preflight-checker'" not in small_section, (
            "Small tier must not invoke preflight-checker subagent"
        )
        # Gate 2 and 3 must be skipped
        assert "Gate 2" in small_section and "SKIP" in small_section, (
            "Small tier must explicitly skip Gate 2"
        )


class TestStandardTierThreeGates:
    """Test 4: Standard tier has all three gates."""

    def test_plan_md_standard_tier_has_three_gates(self, plan_md_text):
        """After 'If tier = standard', Gates 1, 2, and 3 must all be present."""
        standard_section = _section_after(plan_md_text, "If tier = standard")
        assert standard_section != "", "Standard tier section not found"
        assert "Gate 1" in standard_section, "Standard tier must have Gate 1 (Critique)"
        assert "Gate 2" in standard_section, "Standard tier must have Gate 2 (Plan-Validation)"
        assert "Gate 3" in standard_section, "Standard tier must have Gate 3 (Preflight)"
        assert "Task(subagent_type='critique-agent'" in standard_section, (
            "Standard tier must invoke critique-agent subagent"
        )
        assert "Task(subagent_type='preflight-checker'" in standard_section, (
            "Standard tier must invoke preflight-checker subagent for validation and preflight"
        )


class TestArchitecturalTierGate4:
    """Test 5: Architectural tier has Gate 4 operator approval."""

    def test_plan_md_architectural_tier_has_operator_approval(self, plan_md_text):
        """After 'If tier = architectural', Gate 4 with AskUserQuestion must be present."""
        arch_section = _section_after(plan_md_text, "If tier = architectural")
        assert arch_section != "", "Architectural tier section not found"
        assert "Gate 4" in arch_section, "Architectural tier must have Gate 4"
        assert "AskUserQuestion" in arch_section, (
            "Architectural tier must invoke AskUserQuestion for operator approval"
        )
        assert "Operator Approval" in arch_section or "operator" in arch_section.lower(), (
            "Architectural tier Gate 4 must require operator approval"
        )
```

### Call Chain

```
Agent at PLAN phase entry
    |
    +-> Read WORK.md (already required — no new reads)
    |       Extracts: effort, source_files, type, traces_to
    |
    +-> Classify tier (inline logic per Step 1 table)
    |       Returns: trivial | small | standard | architectural
    |
    +-> Apply gate set (Step 2)
            |
            +-> trivial: skip all gates, enter DO directly
            +-> small: inline checklist only, enter DO
            +-> standard: Gate 1 (critique-agent) -> Gate 2 (plan-validation haiku) -> Gate 3 (preflight haiku) -> DO
            +-> architectural: standard gates + Gate 4 (AskUserQuestion) -> DO
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Skill-level enforcement only | Modify PLAN.md markdown text | critique_injector.py already handles critique tier-awareness at hook level. The other two gates have no hook wiring. Skill text is the primary enforcement mechanism for agent behavior per Module-First principle. Adding hook-level gate injection would require a new lib module (scope creep). |
| Agent reads WORK.md fields directly | No Python call; inline tier classification in skill instructions | Agents cannot call Python functions. The skill instructions must be LLM-executable. The WORK.md is already required reading at PLAN entry — no additional reads needed. |
| Architectural gets Gate 4 (explicit) | Add AskUserQuestion as Gate 4 | critique_injector.py mentions operator confirmation for architectural tier in TIER_INJECTIONS but it was implicit. Making it an explicit Gate 4 in skill text gives agents unambiguous instructions. |
| Absent source_files defaults standard | Explicitly stated in tier table note | Per REQ-LIFECYCLE-005 invariant "Absent data MUST NOT produce a more permissive classification." Explicitly documenting this in the skill text prevents agent from treating absent=trivial. |
| No hook-level gate injection | Out of scope for WORK-250 | Would require new lib module (compute_gate_set.py) and PreToolUse wiring. PreToolUse hook already at 400+ lines. Separate concern — if desired, create follow-on work item. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| effort field absent | Standard (conservative default) — documented in tier table note | Test 1 (gate matrix contains conservative default note) |
| source_files=[] (empty list) | Standard (conservative default — same as absent) | Test 1 |
| WORK-250 itself (effort=medium) | Standard — all 3 gates run. Self-referential but consistent. | Test 4 |
| Plan exists for "trivial" predicate | If plan exists, trivial predicate fails → small or standard. Tier table documents this. | Test 2 (no plan invocation in trivial section) |
| type=design with effort=small | Architectural wins (checked first) — all 4 gates run | Test 5 |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agent misreads tier table and skips gates on standard items | H | Test 4 explicitly asserts standard tier has all 3 Task() invocations in the skill text. Gate 4 makes architectural explicit. |
| Skill text changes not detected by existing tests | M | New test_plan_phase_gates.py locks in the structural content. Any regression in PLAN.md will fail the test suite. |
| critique_injector.py and PLAN.md skill text diverge | L | Both encode the same tier logic. critique_injector is hook-level (fires before skill); PLAN.md is skill-level (agent reads it). They are complementary, not duplicates. Document in PLAN.md comment. |
| Agent misidentifies tier for WORK-250 itself (effort=medium) | L | WORK-250 has effort=medium → standard tier → all 3 gates run. No self-referential paradox. |

---

## Layer 2: Implementation Steps

<!-- Ordered steps. Each step is a sub-agent delegation unit. -->

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Create `tests/test_plan_phase_gates.py` from Layer 1 Tests section (File 2 design contains the complete file)
- **output:** Test file exists; all 5 tests FAIL (PLAN.md still has unconditional gates)
- **verify:** `pytest tests/test_plan_phase_gates.py -v 2>&1 | grep -c "FAILED\|ERROR"` equals 5

### Step 2: Modify PLAN.md Exit Gate Section (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Replace Exit Criteria and Exit Gate sections in `.claude/skills/implementation-cycle/phases/PLAN.md` with the tier-aware versions specified in Layer 1 Desired State
- **output:** PLAN.md contains tier-aware Exit Gate with trivial/small/standard/architectural branches
- **verify:** `pytest tests/test_plan_phase_gates.py -v` exits 0, `5 passed` in output

### Step 3: Verify Full Test Suite (No Regressions)
- **spec_ref:** Layer 0 > Scope Metrics
- **input:** Step 2 complete (PLAN.md modified, new tests pass)
- **action:** Run full test suite to confirm no regressions
- **output:** Zero new failures vs pre-change baseline
- **verify:** `pytest tests/ -v 2>&1 | tail -5` shows 0 new failures; existing 1571+ pass count maintained

---

## Ground Truth Verification

<!-- Computable verification protocol. -->

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_plan_phase_gates.py -v` | 5 passed, 0 failed |
| `pytest tests/ -v 2>&1 \| tail -5` | 0 new failures vs pre-change baseline |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| PLAN.md Exit Gate is tier-aware | `grep "Tier-Aware" .claude/skills/implementation-cycle/phases/PLAN.md` | 1 match |
| Trivial tier skips documented | `grep "trivial" .claude/skills/implementation-cycle/phases/PLAN.md \| grep -i "SKIP"` | 1+ match |
| Small tier inline-only documented | `grep "small" .claude/skills/implementation-cycle/phases/PLAN.md \| grep -i "checklist"` | 1+ match |
| Gate 4 operator approval present | `grep "Gate 4" .claude/skills/implementation-cycle/phases/PLAN.md` | 1 match |
| Test file created | `test -f tests/test_plan_phase_gates.py && echo exists` | exists |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| No stale "Exit Gate (MUST)" pattern | `grep "Exit Gate (MUST)" .claude/skills/implementation-cycle/phases/PLAN.md` | 0 matches |
| critique_injector.py unchanged | `python -m pytest tests/test_critique_injector.py -v` | all pass |
| tier_detector.py unchanged | `python -m pytest tests/test_tier_detector.py -v` | all pass |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 2 verify — 5 new tests green)
- [ ] All WORK.md deliverables verified (table above)
- [ ] No stale unconditional "Exit Gate (MUST)" pattern in PLAN.md
- [ ] Full test suite: zero new failures
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> For skill text changes, "runtime consumer" = the agent reading the updated skill instructions on next PLAN phase entry.

---

## References

- `.claude/skills/implementation-cycle/phases/PLAN.md` — primary file under modification
- `.claude/haios/lib/tier_detector.py` — authoritative tier predicate logic (WORK-167)
- `.claude/haios/lib/critique_injector.py` — existing hook-level critique tier awareness (WORK-169)
- `tests/test_tier_detector.py` — existing tier detection tests (not modified)
- `tests/test_critique_injector.py` — existing critique injection tests (not modified)
- `.claude/haios/manifesto/L4/functional_requirements.md` — REQ-LIFECYCLE-005, REQ-CEREMONY-005
- Memory 85606 — 104% context budget problem (root cause addressed by this work)
- Memory 89187 — Operator directive for this exact work
- Memory 89185 — Decision on proportional gate reduction
- CH-059: CeremonyAutomation (implementation chapter)
- WORK-167: Governance Tier Detection (complete — tier_detector.py)
- WORK-169: Critique-as-Hook (complete — critique_injector.py)

---
