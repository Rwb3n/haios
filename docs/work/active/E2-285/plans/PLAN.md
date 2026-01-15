---
template: implementation_plan
status: complete
date: 2026-01-15
backlog_id: E2-285
title: "Skill Template Single-Phase Default"
author: Hephaestus
lifecycle_phase: done
session: 189
version: "1.5"
generated: 2026-01-15
last_updated: 2026-01-15T14:25:00
---
# Implementation Plan: Skill Template Single-Phase Default

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

A skill template will exist that defaults to single-phase structure, requires justification for multi-phase design, and enforces S20 "each skill does ONE thing" principle through structural guidance.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 0 | No existing files to change |
| Lines of code affected | 0 | New template creation |
| New files to create | 1 | `.claude/templates/skill.md` |
| Tests to write | 3-4 | Template structure validation |
| Dependencies | 18 skills | All existing skills are potential consumers |

**Context:**
- 18 existing skills in `.claude/skills/*/SKILL.md`
- 10 skills currently use multi-phase "The Cycle" pattern
- Template size estimate: ~120-150 lines (similar to investigation template at 371 lines but simpler)

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Template is passive - used during skill creation |
| Risk of regression | Low | No existing skill template to break |
| External dependencies | Low | Standalone markdown file, no code execution |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Design template structure | 20 min | High |
| Write template content | 30 min | High |
| Write validation tests | 20 min | Medium |
| Verify against S20 principles | 15 min | High |
| **Total** | ~90 min | High |

---

## Current State vs Desired State

### Current State

**File:** `.claude/templates/skill.md` - **DOES NOT EXIST**

**Behavior:** Agents creating new skills have no structural template to follow.

**Result:**
- Agents default to multi-phase "The Cycle" pattern by copying existing skills
- 10 of 18 skills (56%) use multi-phase structure
- Exit criteria checklists become "procedural theater" (S20)
- Violates S20 principle: "each skill does ONE thing"
- No explicit prompt to justify multi-phase design

**Evidence from checkpoint:**
- survey-cycle: 5 phases
- observation-capture-cycle: 3 phases (now simplified to single-phase in E2-284)
- implementation-cycle: 5 phases
- All built as multi-phase because pattern was available to copy

### Desired State

**File:** `.claude/templates/skill.md` - **EXISTS** with single-phase default

**Behavior:** Agents creating new skills are guided toward single-phase design with explicit justification required for multi-phase.

**Result:**
- Template defaults to single-phase structure (like observation-capture-cycle post-E2-284)
- "When Multi-Phase is Justified" section forces explicit rationale
- No default exit criteria checklists (ceremony reduced)
- "Principle Alignment" section verifies S20 compliance
- Future skills follow "smaller containers, harder boundaries" principle

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Template File Exists
```python
def test_skill_template_exists():
    """Verify skill template file can be read"""
    template_path = Path(".claude/templates/skill.md")
    assert template_path.exists(), "skill.md template must exist"
    assert template_path.is_file(), "skill.md must be a file"
```

### Test 2: Template Has Required Sections
```python
def test_template_has_required_sections():
    """Verify template contains all required sections per E2-285"""
    template = Path(".claude/templates/skill.md").read_text()

    # MUST have single-phase default structure
    assert "## When to Use" in template, "Missing: When to Use section"
    assert "## Instructions" in template or "## Logic" in template, "Missing: Instructions/Logic section"
    assert "## Output" in template or "## Gate" in template, "Missing: Output/Gate section"

    # MUST have multi-phase justification section
    assert "Multi-Phase" in template or "multi-phase" in template, "Missing: Multi-phase justification section"
    assert "When Multi-Phase is Justified" in template, "Missing: explicit multi-phase rationale section"

    # MUST have principle alignment section
    assert "Principle Alignment" in template, "Missing: Principle Alignment section"
    assert "S20" in template or "pressure dynamics" in template, "Missing: S20 reference"

    # MUST NOT have default exit criteria checklists
    assert "Exit Criteria:" not in template, "Template should not have default Exit Criteria checklists"
```

### Test 3: Template Discourages Multi-Phase Design
```python
def test_template_discourages_multi_phase():
    """Verify template structure nudges toward single-phase"""
    template = Path(".claude/templates/skill.md").read_text()

    # Should NOT have "## The Cycle" as primary section
    lines = template.split('\n')
    cycle_section_line = next((i for i, line in enumerate(lines) if "## The Cycle" in line), None)

    # If "The Cycle" exists, it should be in the multi-phase justification section
    # with warning text, not as the primary structure
    if cycle_section_line:
        # Check surrounding context for justification/warning
        context = '\n'.join(lines[max(0, cycle_section_line-5):cycle_section_line+10])
        assert any(word in context.lower() for word in ["justification", "rationale", "only if", "must"]), \
            "If The Cycle section exists, it must be accompanied by justification requirement"
```

### Test 4: Template Alignment with S20
```python
def test_template_aligns_with_s20_principle():
    """Verify template enforces 'each skill does ONE thing'"""
    template = Path(".claude/templates/skill.md").read_text()

    # Should reference S20 or the principle
    assert any(phrase in template for phrase in [
        "each skill does ONE thing",
        "smaller containers",
        "UNIX philosophy",
        "single responsibility"
    ]), "Template must reference S20 'each skill does ONE thing' principle"
```

---

## Detailed Design

### Template Structure

**File:** `.claude/templates/skill.md` (NEW)

The template will follow existing template patterns (YAML frontmatter + markdown) and provide single-phase structure as default.

### Template Content

**The template will contain these sections:**

```markdown
---
template: skill
name: {{SKILL_NAME}}
description: {{DESCRIPTION}}
recipes: []
generated: {{DATE}}
last_updated: {{DATE}}
---
# {{SKILL_NAME}}

[Brief description of what this skill does - ONE thing]

## When to Use

**Invoked by:** [Command, skill, or manual invocation pattern]
**Purpose:** [One sentence describing when to use this skill]

---

## Instructions

[Step-by-step instructions for the single task this skill performs]

### Step 1: [Action]
[Description]

### Step 2: [Action]
[Description]

---

## Gate (Optional)

**MUST provide:**
- [Required output or condition]

**BLOCKS if:**
- [Blocking condition]

---

## Output

[Description of what this skill produces]

---

## Principle Alignment

**S20 Compliance:**
- [ ] This skill does ONE thing (describe what)
- [ ] Skill is atomic and cannot be decomposed further
- [ ] If multi-phase, justification provided below

**Related Principles:**
- [Reference to relevant S-sections or ADRs]

---

## When Multi-Phase is Justified

> **DEFAULT: Skills should be single-phase.** Multi-phase design is ONLY justified when:
> 1. Phases have fundamentally different pressure (volumous vs tight per S20)
> 2. Early exit is required (fail fast before later phases)
> 3. Phases cannot be extracted to separate skills due to tight coupling
>
> **MUST provide explicit rationale below if using multi-phase structure.**

**Justification for Multi-Phase:**
[If this skill has multiple phases, explain WHY they cannot be separate skills]

**Phase Structure:**
[Only include this section if justified above]

```
PHASE1 [pressure] --> PHASE2 [pressure] --> ...
```

---

## Related

- **[Related skill]:** [How they compose]
- **[Template/command]:** [Integration point]

---
```

### Pattern Verification (E2-255)

Checked existing templates for pattern consistency:
- All templates use YAML frontmatter with `template`, `generated`, `last_updated` fields
- Variable substitution uses `{{VARIABLE}}` syntax
- Section headers use `##` level-2 markdown
- RFC 2119 keywords used for governance (MUST, SHOULD, MAY)

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Single-phase as default** | Template shows "Instructions" section, not "The Cycle" | Structural nudge - agents copy structure they see. Making single-phase the visible pattern discourages multi-phase by default. |
| **"When Multi-Phase is Justified" section** | Explicit section with criteria list | Forces conscious decision. Blank template would allow silentslip into multi-phase. This section makes justification visible and required. |
| **No default Exit Criteria checklists** | Removed from template | Exit criteria become "procedural theater" - agents check boxes without reflection. S20 says "hard gates" not checklists. |
| **Principle Alignment section** | Added as explicit section | Makes S20 compliance verifiable. Agents must explicitly confirm "this does ONE thing" rather than assume it. |
| **Pressure typing in multi-phase** | Requires `[volumous]` or `[tight]` labels | If multi-phase is justified, phases must be typed per S20. This enforces the "Inhale/Exhale" rhythm principle. |
| **Gate section optional** | Marked "(Optional)" | Not all skills need hard gates. Memory-agent has steps, not gates. Template shouldn't force structure that doesn't fit. |
| **Variables follow existing pattern** | `{{SKILL_NAME}}`, `{{DESCRIPTION}}`, `{{DATE}}` | Consistency with other templates (implementation_plan, investigation, etc.). Same scaffolding patterns. |

### Input/Output Examples

**Current State (no template):**
```
Agent task: Create new skill "config-validator"
Agent behavior: Reads existing skill (e.g., plan-authoring-cycle)
Agent copies: "## The Cycle" with 4-5 phases, Exit Criteria checklists
Result: Multi-phase skill created because pattern was visible
```

**After Template (single-phase default):**
```
Agent task: Create new skill "config-validator"
Agent behavior: Reads template .claude/templates/skill.md
Agent sees: "## Instructions" (single-phase), "When Multi-Phase is Justified" (requires rationale)
Result:
  - If simple task: Uses single-phase Instructions
  - If complex: Must justify multi-phase in "When Multi-Phase is Justified" section
```

**Real Example - observation-capture-cycle Evolution:**
- **Before E2-284:** 3-phase cycle (RECALL → NOTICE → COMMIT)
- **After E2-284:** Simplified to 3 questions + Gate (single-phase)
- **Lines reduced:** ~80 lines → 44 lines (45% reduction)
- **Behavior:** Same functionality, less procedural theater

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Agent ignores template | Template is guidance, not enforcement | Test validates template structure exists, not agent compliance |
| Valid multi-phase skill | "When Multi-Phase is Justified" section provides space | Test 3 verifies this section exists |
| Skill has no gate | Gate section marked "(Optional)" | Template accommodates gated and non-gated skills |

### Open Questions

**Q: Should we add a scaffolding command `/new-skill` that uses this template?**

**A:** Out of scope for E2-285. This work item creates the template. A future work item (E2-286+) could add scaffolding command. The template is valuable even without scaffolding - agents can manually copy and customize it.

---

## Open Decisions (MUST resolve before implementation)

<!-- Decisions from work item's operator_decisions field.
     If ANY row has [BLOCKED] in Chosen column, plan-validation-cycle will BLOCK.

     POPULATE FROM: Work item frontmatter `operator_decisions` field
     - question -> Decision column
     - options -> Options column
     - chosen -> Chosen column (null = [BLOCKED])
     - rationale -> Rationale column (filled when resolved) -->

**No unresolved decisions.** Work item `operator_decisions` field is empty.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_skill_template.py` with 4 tests from Tests First section
- [ ] Verify all tests fail (red) - template doesn't exist yet
- [ ] Tests: test_skill_template_exists, test_template_has_required_sections, test_template_discourages_multi_phase, test_template_aligns_with_s20_principle

### Step 2: Create Template File
- [ ] Create `.claude/templates/skill.md` with structure from Detailed Design
- [ ] Include frontmatter with `template: skill`, placeholder variables
- [ ] Test 1 passes (green): file exists

### Step 3: Add Single-Phase Structure Sections
- [ ] Add "## When to Use" section
- [ ] Add "## Instructions" section (with Step 1, Step 2 placeholders)
- [ ] Add "## Gate (Optional)" section
- [ ] Add "## Output" section
- [ ] Partial Test 2 passes: required sections exist

### Step 4: Add Principle Alignment Section
- [ ] Add "## Principle Alignment" section with S20 compliance checklist
- [ ] Reference S20 "each skill does ONE thing" principle
- [ ] Reference "smaller containers, harder boundaries"
- [ ] Test 4 passes (green): S20 reference present

### Step 5: Add Multi-Phase Justification Section
- [ ] Add "## When Multi-Phase is Justified" section
- [ ] Include blockquote with criteria (different pressure, early exit, tight coupling)
- [ ] Include "MUST provide explicit rationale" instruction
- [ ] Test 2 passes (green): all required sections present
- [ ] Test 3 passes (green): multi-phase discouraged but accommodated

### Step 6: Add Related Section and Finalize
- [ ] Add "## Related" section for composition documentation
- [ ] Verify no "Exit Criteria:" checklists in template
- [ ] All tests pass (green)

### Step 7: README Sync (MUST)
- [ ] **MUST:** Update `.claude/templates/README.md` to include skill template entry
- [ ] **MUST:** Add row to Available Templates table:
  ```
  | `skill` | Skill implementation | SKILL_NAME, DESCRIPTION, DATE | Active |
  ```
- [ ] **MUST:** Verify README content matches actual file state

### Step 8: Integration Verification
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] Verify no regressions in other tests
- [ ] Read created template file to verify structure
- [ ] Compare against Tests First assertions

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Template ignored by agents** | Medium | Template is guidance, not enforcement. However, agents are prompted to follow templates via CLAUDE.md and skill commands. Future work could add `/new-skill` scaffolding command (like `/new-plan`) to enforce template usage. |
| **Multi-phase still overused** | Medium | "When Multi-Phase is Justified" section provides criteria but doesn't prevent misuse. Risk accepted - template nudges behavior but doesn't eliminate all drift. Audit skill can detect violations. |
| **Template becomes stale** | Low | Like other templates, requires manual updates. Mitigated by including `last_updated` field in frontmatter and linking to S20 (single source of truth). |
| **Existing skills not updated** | Low | Template applies to new skills only. Existing 10 multi-phase skills remain unchanged. This is acceptable - template prevents future drift, not retroactive fix. Future work items can refactor existing skills if needed. |
| **Misalignment with S20 evolution** | Low | S20 is marked as PRINCIPLE (foundational), unlikely to change. If S20 evolves, template update is straightforward (single file). |

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
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.

---

## References

- **S20-pressure-dynamics.md** - "Each skill does ONE thing" principle, smaller containers/harder boundaries
- **E2-284: Observation-Capture Simplify to 3 Questions** - Example of single-phase simplification success (80→44 lines)
- **E2-283: Survey-Cycle Prune to Minimal Routing** - Example of multi-phase simplification (242→42 lines)
- **Checkpoint 2026-01-12 (Session 188)** - Drift observation: "Agent skipped governance because 'I know how to do this'"
- **Memory 81248-81266** - E2.2 drift diagnosis
- **Existing skills** - observation-capture-cycle (single-phase), plan-authoring-cycle (multi-phase)
- **.claude/templates/README.md** - Template registry and patterns

---
