---
template: implementation_plan
status: approved
date: 2026-02-01
backlog_id: WORK-061
title: EXPLORE-FIRST Investigation Cycle Implementation
author: Hephaestus
lifecycle_phase: plan
session: 272
version: '1.5'
generated: 2026-02-01
last_updated: '2026-02-01T15:56:26'
---
# Implementation Plan: EXPLORE-FIRST Investigation Cycle Implementation

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

The investigation-cycle skill will use the EXPLORE-FIRST pattern (EXPLORE→HYPOTHESIZE→VALIDATE→CONCLUDE) with fractured phase templates, reducing Template Tax by 62% while improving discovery depth through unrestricted exploration before hypothesis formation.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `.claude/skills/investigation-cycle/SKILL.md`, `.claude/haios/config/activity_matrix.yaml` |
| Lines of code affected | ~250 | SKILL.md (228 lines full rewrite), activity_matrix.yaml (~20 lines) |
| New files to create | 0 | Fractured templates already exist (WORK-043, Session 271) |
| Tests to write | 0 | Skill/template changes are markdown, not code |
| Dependencies | 2 | close-work-cycle (routes), routing-gate (type detection) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Skills are markdown - no runtime imports |
| Risk of regression | Low | No code changes, only skill restructure |
| External dependencies | None | Pure markdown/yaml changes |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Update activity_matrix.yaml | 10 min | High |
| Rewrite investigation-cycle skill | 30 min | High |
| Add deprecation to monolithic template | 5 min | High |
| Verification | 10 min | High |
| **Total** | ~1 hr | High |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/skills/investigation-cycle/SKILL.md (lines 26-29)
## The Cycle

HYPOTHESIZE --> EXPLORE --> CONCLUDE --> CHAIN
```

**Behavior:** Investigation starts with hypothesis formation, then explores to test hypotheses, then concludes.

**Result:** Template Tax (25 MUST + 27 checkboxes), premature hypothesis constrains exploration depth.

### Desired State

```markdown
# .claude/skills/investigation-cycle/SKILL.md (target)
## The Cycle

EXPLORE --> HYPOTHESIZE --> VALIDATE --> CONCLUDE --> CHAIN
```

**Behavior:** Investigation starts with unrestricted exploration, then synthesizes hypotheses from evidence, validates each, then concludes.

**Result:** Reduced Template Tax (9 MUST gates), deeper exploration, evidence-driven hypothesis formation.

---

## Tests First (TDD)

**SKIPPED:** This implementation modifies markdown skill files and YAML config, not Python code. No unit tests applicable. Verification is manual reading of updated skill flow and activity matrix.

---

## Detailed Design

### Change 1: Update activity_matrix.yaml Phase Mappings

**File:** `.claude/haios/config/activity_matrix.yaml`
**Location:** Lines 186-189 (investigation-cycle section)

**Current Code:**
```yaml
# activity_matrix.yaml:186-189
  # investigation-cycle (EXPLORE-FIRST per E2.4)
  investigation-cycle/HYPOTHESIZE: DESIGN
  investigation-cycle/EXPLORE: EXPLORE
  investigation-cycle/CONCLUDE: DONE
```

**Changed Code:**
```yaml
# activity_matrix.yaml:186-191
  # investigation-cycle (EXPLORE-FIRST per E2.4 - WORK-061)
  investigation-cycle/EXPLORE: EXPLORE       # Phase 1: Evidence gathering
  investigation-cycle/HYPOTHESIZE: DESIGN    # Phase 2: Form hypotheses from evidence
  investigation-cycle/VALIDATE: CHECK        # Phase 3: Test hypotheses
  investigation-cycle/CONCLUDE: DONE         # Phase 4: Synthesize and spawn
```

**Rationale:** Adds VALIDATE phase mapping (new) and reorders to match actual flow. Comments clarify phase numbers.

---

### Change 2: Rewrite investigation-cycle Skill

**File:** `.claude/skills/investigation-cycle/SKILL.md`

**Structure (from WORK-037 design spec):**

```
# Investigation Cycle

## When to Use (unchanged)

## The Cycle (CHANGED)
- Old: HYPOTHESIZE --> EXPLORE --> CONCLUDE --> CHAIN
- New: EXPLORE --> HYPOTHESIZE --> VALIDATE --> CONCLUDE --> CHAIN

## 1. EXPLORE Phase (NEW - was phase 2)
- On Entry: just set-cycle investigation-cycle EXPLORE {work_id}
- Goal: Gather evidence before forming hypotheses
- Actions: Read, Glob, Grep, memory_search, WebSearch (open exploration)
- NO subagent requirement (main agent explores freely)
- Exit criteria: Evidence documented in investigation doc

## 2. HYPOTHESIZE Phase (CHANGED - was phase 1)
- On Entry: just set-cycle investigation-cycle HYPOTHESIZE {work_id}
- Goal: Form hypotheses FROM gathered evidence
- Actions: Synthesize, write hypotheses with evidence citations
- Exit criteria: Hypotheses table with evidence citations

## 3. VALIDATE Phase (NEW)
- On Entry: just set-cycle investigation-cycle VALIDATE {work_id}
- Goal: Test each hypothesis against evidence
- Actions: Review evidence, render verdict per hypothesis
- No new evidence gathering (that was EXPLORE)
- Exit criteria: All hypotheses have verdict

## 4. CONCLUDE Phase (unchanged behavior)
- On Entry: just set-cycle investigation-cycle CONCLUDE {work_id}
- Goal: Synthesize findings, spawn work, store memory
- Exit criteria: Findings, spawns, memory_refs

## 5. CHAIN Phase (unchanged)

## Composition Map (UPDATED for 5 phases)

## Quick Reference (UPDATED)

## Key Design Decisions (UPDATED)

## Related (ADD reference to fractured templates)
```

---

### Change 3: Add Deprecation Notice to Monolithic Template

**File:** `.claude/templates/investigation.md`
**Location:** Top of file (after frontmatter, before content)

**Addition:**
```markdown
<!-- DEPRECATION NOTICE (E2.4 - WORK-061)

     This monolithic template is preserved for backward compatibility.

     NEW investigations should use the fractured phase templates:
       .claude/templates/investigation/EXPLORE.md
       .claude/templates/investigation/HYPOTHESIZE.md
       .claude/templates/investigation/VALIDATE.md
       .claude/templates/investigation/CONCLUDE.md

     The investigation-cycle skill reads these phase-specific templates.
     This monolithic template will be removed in E2.5.
-->
```

---

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Remove MUST investigation-agent in EXPLORE | Main agent explores freely | Session 262 showed unconstrained exploration produces deeper analysis than forced subagent |
| Add VALIDATE as separate phase | Explicit hypothesis testing | Separating verdict-rendering from evidence-gathering improves traceability |
| Keep CHAIN phase | Still routes to next work | Routing logic unchanged, just 4 phases before it now |
| Preserve monolithic template | Backward compatibility | Existing investigations can still reference it; deprecate, don't delete |
| Reference fractured templates from skill | Point skill consumers to new structure | Skill's "Related" section links to `.claude/templates/investigation/` |

---

### Edge Cases

| Case | Handling | Notes |
|------|----------|-------|
| In-flight investigation using old flow | Complete with old flow | Grandfather clause - don't force mid-work migration |
| New investigation started before skill update | Agent may see old skill | Low risk - skill changes are immediate on next read |
| EXPLORE produces no evidence | Proceed to HYPOTHESIZE with empty evidence | Agent should document "no evidence found" as valid finding |

---

### Open Questions

**Q: Should investigation-agent be updated for new flow?**

Per WORK-037 design, this is a separate work item. investigation-agent relaxation (output format changes) is out of scope for WORK-061.

---

## Open Decisions (MUST resolve before implementation)

**N/A:** Work item WORK-061 has no `operator_decisions` field. Design decisions were made during WORK-037 investigation and approved as part of L4 Decision (Session 265).

---

## Implementation Steps

### Step 1: Update activity_matrix.yaml
- [ ] Add investigation-cycle/VALIDATE mapping to CHECK state
- [ ] Reorder existing mappings to match EXPLORE→HYPOTHESIZE→VALIDATE→CONCLUDE flow
- [ ] Add clarifying comments for phase numbers

### Step 2: Rewrite investigation-cycle/SKILL.md
- [ ] Change cycle diagram to EXPLORE→HYPOTHESIZE→VALIDATE→CONCLUDE→CHAIN
- [ ] Reorder phase sections (EXPLORE becomes Phase 1)
- [ ] Update EXPLORE phase: remove MUST investigation-agent, add free exploration guidance
- [ ] Update HYPOTHESIZE phase: now synthesizes FROM evidence (Phase 2)
- [ ] Add VALIDATE phase section (Phase 3) - focused hypothesis testing
- [ ] Update CONCLUDE phase numbering (Phase 4)
- [ ] Update CHAIN phase numbering (Phase 5)
- [ ] Update Composition Map for 5 phases
- [ ] Update Quick Reference table
- [ ] Update Key Design Decisions table
- [ ] Add fractured templates reference to Related section

### Step 3: Add Deprecation Notice to Monolithic Template
- [ ] Add deprecation comment block to `.claude/templates/investigation.md`
- [ ] Point to `.claude/templates/investigation/` directory

### Step 4: Verification
- [ ] Read updated activity_matrix.yaml - verify 4 investigation-cycle mappings exist
- [ ] Read updated SKILL.md - verify 5 phases in correct order
- [ ] Verify deprecation notice in monolithic template

### Step 5: Consumer Verification
- [ ] Grep for "HYPOTHESIZE.*EXPLORE.*CONCLUDE" to find any hardcoded old flow references
- [ ] Update EPOCH.md exit criteria if needed
- [ ] Update flow arc ARC.md chapter status if needed

---

## Verification

- [ ] activity_matrix.yaml has 4 investigation-cycle phase mappings
- [ ] SKILL.md has 5 phases in EXPLORE→HYPOTHESIZE→VALIDATE→CONCLUDE→CHAIN order
- [ ] Deprecation notice added to monolithic template
- [ ] No hardcoded old flow references remain

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agents still invoke old HYPOTHESIZE-first | Low | Skill is read each invocation; update is immediate |
| In-flight investigations confused by flow change | Low | Document grandfather clause - complete with flow at start |
| investigation-agent output format still rigid | Low | Out of scope (separate work item) - agent invocation optional now |
| Fractured templates not found by skill | Low | Templates already exist (verified); add explicit path in Related section |

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

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-061/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Update activity_matrix.yaml with new phase-to-state mappings | [ ] | Read file, verify 4 investigation-cycle mappings |
| Create fractured templates directory | [ ] | Already exists: `.claude/templates/investigation/` |
| Create EXPLORE.md phase template | [ ] | Already exists: verified ~53 lines |
| Create HYPOTHESIZE.md phase template | [ ] | Already exists: verified ~54 lines |
| Create VALIDATE.md phase template | [ ] | Already exists: verified ~55 lines |
| Create CONCLUDE.md phase template | [ ] | Already exists: verified ~61 lines |
| Update investigation-cycle/SKILL.md with new flow | [ ] | Read file, verify EXPLORE→HYPOTHESIZE→VALIDATE→CONCLUDE→CHAIN |
| Add deprecation notice to monolithic investigation.md | [ ] | Read file, verify deprecation comment exists |
| Store implementation learnings to memory | [ ] | Call `ingester_ingest`, verify memory_refs |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/config/activity_matrix.yaml` | 4 investigation-cycle phase mappings | [ ] | |
| `.claude/skills/investigation-cycle/SKILL.md` | 5 phases in new order | [ ] | |
| `.claude/templates/investigation.md` | Deprecation notice at top | [ ] | |
| `.claude/templates/investigation/README.md` | Links to 4 phase templates | [ ] | Already verified |
| `Grep: HYPOTHESIZE.*EXPLORE.*CONCLUDE` | Zero old-flow references in skills | [ ] | |

**Verification Commands:**
```bash
# Verify phase mappings in activity_matrix
grep "investigation-cycle" .claude/haios/config/activity_matrix.yaml
# Expected: 4 lines (EXPLORE, HYPOTHESIZE, VALIDATE, CONCLUDE)
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Fractured templates exist and are correct? | [Yes/No] | Created by WORK-043 |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] All WORK.md deliverables verified complete (see table above)
- [ ] **Runtime consumer exists** - investigation-cycle skill is invoked by survey-cycle, routing-gate
- [ ] WHY captured (reasoning stored to memory via ingester_ingest)
- [ ] No stale old-flow references in skill files
- [ ] Ground Truth Verification completed above

> **Note:** No tests for this work item - changes are markdown/YAML, not Python code.

---

## References

- @docs/work/active/WORK-037/investigations/001-explore-first-design.md - Design specification
- @.claude/haios/epochs/E2_4/EPOCH.md - L4 Decision (Session 265) approving EXPLORE-FIRST
- @.claude/haios/epochs/E2_4/arcs/flow/ARC.md - Parent arc (CH-003: InvestigationFlow)
- Memory concepts 82829-82837 - WORK-037 design findings
- Memory concept 82838 - Template contract pattern

---
