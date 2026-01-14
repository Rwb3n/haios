---
template: implementation_plan
status: complete
date: 2026-01-08
backlog_id: E2-280
title: SURVEY Skill-Cycle Implementation
author: Hephaestus
lifecycle_phase: plan
session: 184
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-08T23:20:39'
---
# Implementation Plan: SURVEY Skill-Cycle Implementation

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

A SURVEY skill-cycle will exist that creates volumous space at session level for work selection, following the GATHER-ASSESS-OPTIONS-CHOOSE-ROUTE pattern from INV-061 H3.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | coldstart.md, haios-manifest.yaml |
| Lines of code affected | ~20 | Coldstart routing section |
| New files to create | 2 | SKILL.md, test_survey_cycle.py |
| Tests to write | 3 | Phase structure, coldstart wiring, routing |
| Dependencies | 0 | New standalone skill |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single consumer (coldstart) |
| Risk of regression | Low | New skill, no existing code to break |
| External dependencies | Low | Uses existing `just ready` recipe |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 20 min | High |
| Create SKILL.md | 30 min | High |
| Wire into coldstart | 10 min | High |
| **Total** | 1 hr | High |

---

## Current State vs Desired State

### Current State

```markdown
# coldstart.md lines 61-75 - Work Routing section
## Work Routing (E2-208: Autonomous Session Loop)

After summary, **MUST** route to work:

1. Run `just ready` to see unblocked work items
2. Pick the highest-priority READY item
3. Route based on work item type:
   - Investigation (INV-*) → investigation-cycle
   - Implementation with plan → implementation-cycle
   - New work needing investigation → /new-investigation
   - New work needing plan → /new-plan
```

**Behavior:** Coldstart immediately routes to first READY item - all exhale, no inhale.

**Result:** Agent picks work reactively without surveying landscape, missing chapter/arc alignment.

### Desired State

```markdown
# coldstart.md with SURVEY integration
## Work Routing (E2-280: SURVEY before Work)

After summary, **MUST** invoke SURVEY skill-cycle:

1. Invoke `Skill(skill="survey-cycle")`
2. SURVEY presents work options aligned to chapters
3. Operator or agent CHOOSES
4. ROUTE executes to chosen work

# Then in SURVEY skill-cycle:
GATHER [volumous] → ASSESS [volumous] → OPTIONS [volumous] → CHOOSE [tight] → ROUTE [tight]
```

**Behavior:** Session has volumous exploration before tight work selection.

**Result:** Agent breathes (S20), presents options, gets explicit commitment before chaining.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: SKILL.md Has Required Phases
```python
def test_survey_cycle_has_five_phases():
    """Verify SURVEY skill has GATHER, ASSESS, OPTIONS, CHOOSE, ROUTE phases."""
    skill_path = Path(".claude/skills/survey-cycle/SKILL.md")
    assert skill_path.exists(), "SKILL.md must exist"
    content = skill_path.read_text()
    assert "GATHER" in content, "Must have GATHER phase"
    assert "ASSESS" in content, "Must have ASSESS phase"
    assert "OPTIONS" in content, "Must have OPTIONS phase"
    assert "CHOOSE" in content, "Must have CHOOSE phase"
    assert "ROUTE" in content, "Must have ROUTE phase"
```

### Test 2: Pressure Annotations Present
```python
def test_survey_cycle_has_pressure_annotations():
    """Verify SURVEY skill has [volumous] and [tight] pressure annotations per S20."""
    skill_path = Path(".claude/skills/survey-cycle/SKILL.md")
    content = skill_path.read_text()
    # GATHER, ASSESS, OPTIONS should be volumous
    assert "[volumous]" in content, "Must have volumous phases"
    # CHOOSE, ROUTE should be tight
    assert "[tight]" in content, "Must have tight phases"
```

### Test 3: Skill Registered in Manifest
```python
def test_survey_cycle_in_manifest():
    """Verify survey-cycle appears in haios manifest for discovery."""
    manifest_path = Path(".claude/haios/manifest.yaml")
    content = manifest_path.read_text()
    assert "survey-cycle" in content, "Must be registered in manifest"
```

---

## Detailed Design

### New File: `.claude/skills/survey-cycle/SKILL.md`

**Structure follows sibling pattern** (observation-capture-cycle, routing-gate):
- YAML frontmatter with name, description
- The Cycle section with ASCII flow diagram
- Phase sections with [pressure] annotations
- Quick Reference table
- Key Design Decisions table
- Related section

### Phase Specifications (from INV-061 H3)

```
SURVEY-cycle:
  GATHER     [volumous, MAY]   - Collect available work, chapters, arcs
  ASSESS     [volumous, MAY]   - Analyze landscape: priorities, blockers, alignment
  OPTIONS    [volumous, MAY]   - Present 2-3 options to operator
  CHOOSE     [tight, MUST]     - Gate: exactly one option selected
  ROUTE      [tight, MUST]     - Invoke appropriate cycle skill
```

### Phase Details

**1. GATHER Phase [volumous, MAY]**
- Run `just ready` to get available work items
- Read active chapter definitions from haios.yaml
- Collect arc status from each chapter's CHAPTER.md
- No gate - pure information gathering

**2. ASSESS Phase [volumous, MAY]**
- Analyze chapter/arc alignment of available work
- Note priorities, blockers, dependencies
- Identify operator focus from coldstart arguments (if provided)
- No gate - exploratory analysis

**3. OPTIONS Phase [volumous, MAY]**
- Present 2-3 concrete options (work items or themes)
- Each option includes:
  - Work item ID and title
  - Chapter/arc alignment
  - Estimated effort
  - Rationale for selection
- No gate - preparation for choice

**4. CHOOSE Phase [tight, MUST]**
- Present options via `AskUserQuestion` if operator steering expected
- Or agent selects based on priority/alignment if autonomous
- **Gate:** Exactly one option must be selected
- Output: chosen work item ID

**5. ROUTE Phase [tight, MUST]**
- Apply routing-gate logic (from routing-gate skill)
- Invoke appropriate cycle:
  - INV-* → investigation-cycle
  - has_plan → implementation-cycle
  - else → work-creation-cycle
- **Gate:** Skill invoked

### Call Chain Context

```
/coldstart
    |
    +-> Load epoch context (existing)
    +-> Load manifesto L0-L3 (existing)
    +-> Load checkpoint (existing)
    +-> Run just session-start (existing)
    |
    +-> SURVEY-cycle  # <-- NEW, replaces immediate routing
            |
            +-> GATHER [volumous] - just ready, chapter status
            +-> ASSESS [volumous] - alignment analysis
            +-> OPTIONS [volumous] - present choices
            +-> CHOOSE [tight] - commit to one
            +-> ROUTE [tight] - invoke cycle skill
```

### Coldstart Modification

**File:** `.claude/commands/coldstart.md`
**Location:** Lines 61-75 "Work Routing" section

**Current:**
```markdown
## Work Routing (E2-208: Autonomous Session Loop)

After summary, **MUST** route to work:

1. Run `just ready` to see unblocked work items
2. Pick the highest-priority READY item
```

**Changed:**
```markdown
## Work Routing (E2-280: SURVEY before Work)

After summary, **MUST** invoke SURVEY skill-cycle:

```
Skill(skill="survey-cycle")
```

SURVEY creates volumous exploration space before work selection (S20 pressure dynamics).
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Five phases | GATHER→ASSESS→OPTIONS→CHOOSE→ROUTE | Matches INV-061 H3 specification |
| 3 volumous, 2 tight | Explore first, commit last | S20 inhale/exhale rhythm |
| OPTIONS via AskUserQuestion | Interactive when operator present | Enables human steering |
| Reuse routing-gate | Call existing skill for ROUTE | DRY, consistent routing logic |
| Standalone skill directory | `.claude/skills/survey-cycle/` | Matches sibling pattern |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No READY items | OPTIONS presents "No work available" | Test via mock just ready |
| Operator provides focus | Pre-filter options to focused area | OPTIONS phase logic |
| All work blocked | Present blockers, offer investigation | ASSESS phase surfaces |

### Open Questions

**Q: Should CHOOSE phase always use AskUserQuestion or can agent autonomously select?**

Answer: Per S20, agent MAY autonomously select in the absence of operator steering. The gate is "exactly one selected" - the selection method is flexible. Document in SKILL.md that AskUserQuestion is OPTIONAL based on session mode.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| None | N/A | N/A | No unresolved operator decisions in work item |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_survey_cycle.py`
- [ ] Add test_survey_cycle_has_five_phases()
- [ ] Add test_survey_cycle_has_pressure_annotations()
- [ ] Add test_survey_cycle_in_manifest()
- [ ] Verify all tests fail (red) - skill doesn't exist yet

### Step 2: Create SKILL.md
- [ ] Create directory `.claude/skills/survey-cycle/`
- [ ] Write SKILL.md with 5 phases per design
- [ ] Add [volumous]/[tight] pressure annotations
- [ ] Include Quick Reference table
- [ ] Tests 1, 2 pass (green)

### Step 3: Register in Manifest
- [ ] Add survey-cycle to `.claude/haios/manifest.yaml`
- [ ] Test 3 passes (green)

### Step 4: Wire into Coldstart
- [ ] Modify `.claude/commands/coldstart.md` Work Routing section
- [ ] Replace direct routing with `Skill(skill="survey-cycle")` invocation

### Step 5: Integration Verification
- [ ] All tests pass
- [ ] Run full test suite (no regressions)
- [ ] Run `just update-status-slim` to verify discovery

### Step 6: README Sync (MUST)
- [ ] **MUST:** Update `.claude/skills/README.md` to include survey-cycle
- [ ] **MUST:** Verify README content matches actual skill files

---

## Verification

- [ ] Tests pass: `pytest tests/test_survey_cycle.py -v`
- [ ] **MUST:** `.claude/skills/README.md` updated
- [ ] Skill discoverable: `just update-status-slim` shows survey-cycle

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Coldstart behavior change breaks existing flow | Medium | Test manually before committing |
| CHOOSE phase UX confusion (when to ask vs auto-select) | Low | Document clearly in SKILL.md |
| Infinite loop if ROUTE invokes back to SURVEY | Medium | ROUTE goes to specific cycle skills, never back to survey |

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
| `.claude/skills/survey-cycle/SKILL.md` | 5 phases with pressure annotations | [ ] | |
| `tests/test_survey_cycle.py` | 3 tests covering phases, pressure, manifest | [ ] | |
| `.claude/haios/manifest.yaml` | survey-cycle listed in skills | [ ] | |
| `.claude/commands/coldstart.md` | Invokes survey-cycle skill | [ ] | |
| `.claude/skills/README.md` | survey-cycle documented | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_survey_cycle.py -v
# Expected: 3 tests passed
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
- [ ] **Runtime consumer exists** (coldstart invokes survey-cycle)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** .claude/skills/README.md updated
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.

---

## References

- INV-061: Svelte Governance Architecture (source investigation)
- ADR-041: Svelte Governance Criteria
- S20: Pressure Dynamics (foundational architecture)
- S22: Skill Patterns (composable patterns)

---
