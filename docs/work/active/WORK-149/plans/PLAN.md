---
template: implementation_plan
status: complete
date: 2026-02-15
backlog_id: WORK-149
title: "Three-Tier Entry Point Architecture ADR"
author: Hephaestus
lifecycle_phase: plan
session: 378
version: "1.5"
generated: 2026-02-15
last_updated: 2026-02-15T22:28:00
---
# Implementation Plan: Three-Tier Entry Point Architecture ADR

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | **SKIPPED:** Pure documentation task (ADR). No code changes. |
| Query prior work | SHOULD | WORK-020 investigation (S368) is the source. Memory 85302, 85303, 82302 queried. |
| Document design decisions | MUST | See Key Design Decisions table |
| Ground truth metrics | MUST | All counts from WORK-020 verified inventory (151 entry points) |

---

## Goal

ADR-045 formalizes the three-tier entry point architecture (commands, skills+agents, recipes) discovered in WORK-020 investigation, establishing clear tier boundaries and assignment criteria for all 151 HAIOS entry points.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | CLAUDE.md (add ADR reference) |
| New files to create | 1 | docs/ADR/ADR-045-three-tier-entry-points.md |
| Tests to write | 0 | Pure documentation task |
| Dependencies | 0 | No code changes |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | ADR is documentation only |
| Risk of regression | Low | No code changes |
| External dependencies | Low | All source material from WORK-020 |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Author ADR | 15 min | High |
| Update CLAUDE.md reference | 5 min | High |
| Validation | 5 min | High |
| **Total** | **25 min** | High |

---

## Current State vs Desired State

### Current State

**SKIPPED:** No code. The three-tier model exists as findings in WORK-020 (docs/work/active/WORK-020/WORK.md, Section "5. Three-Tier Architecture Design") but is not formalized as an Architecture Decision Record. No authoritative reference for tier boundaries exists.

### Desired State

ADR-045 exists in `docs/ADR/ADR-045-three-tier-entry-points.md` with:
- Decision context from WORK-020 investigation
- Three tiers defined with boundary criteria
- Tier assignment table for current entry points
- Migration path for 18 unwrapped Tier 2 recipes (deferred to E2.7)
- CLAUDE.md references the ADR

---

## Tests First (TDD)

**SKIPPED:** Pure documentation task. No code changes, no tests needed. Verification is structural (ADR exists, has correct frontmatter, content covers requirements) via `/validate` command.

---

## Detailed Design

### ADR Content Structure

**File:** `docs/ADR/ADR-045-three-tier-entry-points.md`

The ADR follows the established format (see ADR-044 as template reference):

```markdown
# ADR-045: Three-Tier Entry Point Architecture

## Context
- 151 entry points across 4 systems (87 recipes, 34 skills, 19 commands, 11 agents)
- 7 friction points from WORK-020 investigation
- No unified discovery model

## Decision Drivers
- Agent decision space too large (151 options)
- Multiple paths to same action
- No tier boundaries enforced

## Considered Options
### Option A: Flat namespace (status quo)
### Option B: Two-tier (commands + everything else)
### Option C: Three-tier (commands, skills+agents, recipes)

## Decision
Option C: Three-tier model

## Tier Definitions
| Tier | Name | Audience | Count | Discovery |
|------|------|----------|-------|-----------|
| 1 | Commands | Human (operator) | 19 | Claude Code auto-discovery (.claude/commands/) |
| 2 | Skills + Agents | Agent | 45 (34 skills + 11 agents) | Claude Code auto-discovery (.claude/skills/, .claude/agents/) |
| 3 | Recipes | Internal (called by Tier 1/2) | 87 | None needed (invisible to agent) |

## Tier Assignment Criteria
- How to decide which tier something belongs to

## Consequences
- Agent decision space: 151 -> ~40
- Clear boundaries for new entry points
- Migration path for 18 unwrapped recipes

## Migration Path (deferred to E2.7)
- 18 unwrapped Tier 2 recipes need skill wrappers
- Recipe namespace hiding (prefix convention)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| ADR number | ADR-045 | Next sequential after ADR-044 |
| Include full tier assignment table | Yes | REQ-DISCOVER-002 requires each entry point assigned to exactly one tier |
| Include migration path | Yes, as deferred section | WORK-149 acceptance criteria requires it; actual work is E2.7 |
| Tier 2 combines skills+agents | Yes | Both are agent-invocable via Claude Code auto-discovery; same audience |
| Reference WORK-020 findings directly | Yes | ADR records decision; investigation has the evidence |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| New entry point created after ADR | ADR includes assignment criteria for future entry points | N/A (doc) |
| Recipe needs agent access | Promote to Tier 2 by wrapping in skill | Documented in migration path |
| Skill becomes operator-only | Demote to command (Tier 1) or recipe (Tier 3) | Documented in tier criteria |

---

## Open Decisions (MUST resolve before implementation)

No operator decisions needed. All content sourced from WORK-020 findings (already approved).

---

## Implementation Steps

### Step 1: Author ADR-045
- [ ] Create `docs/ADR/ADR-045-three-tier-entry-points.md`
- [ ] Populate all sections from WORK-020 findings
- [ ] Include tier definitions, assignment criteria, and current inventory
- [ ] Include migration path for 18 unwrapped recipes (deferred to E2.7)

### Step 2: Update CLAUDE.md
- [ ] Add ADR-045 reference to relevant section

### Step 3: Validate
- [ ] Run `/validate` on ADR file
- [ ] Verify all WORK-149 acceptance criteria met

### Step 4: README Sync (MUST)
- [ ] Verify docs/ADR/ directory has no README requiring update (it doesn't — ADRs are self-documenting)

### Step 5: Consumer Verification
- [ ] **SKIPPED:** No migrations or renames. New file only.

---

## Verification

- [ ] ADR file exists with correct frontmatter
- [ ] All 3 WORK-149 acceptance criteria verifiable from ADR content
- [ ] `/validate` passes on ADR
- [ ] CLAUDE.md references ADR-045

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| ADR numbers collision | Low | Verified ADR-044 is latest |
| Stale counts in ADR | Low | All counts from WORK-020 (verified S368) |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| ADR documents three-tier model (commands, skills+agents, recipes) | [ ] | ADR-045 Section "Decision" + "Tier Definitions" |
| ADR defines tier boundaries and assignment criteria | [ ] | ADR-045 Section "Tier Assignment Criteria" |
| ADR records decision context from WORK-020 investigation | [ ] | ADR-045 Section "Context" + References |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `docs/ADR/ADR-045-three-tier-entry-points.md` | Exists with full ADR content | [ ] | |
| `CLAUDE.md` | References ADR-045 | [ ] | |

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] **MUST:** All WORK.md deliverables verified complete
- [ ] **Runtime consumer exists** — N/A: documentation task, no code. ADR is referenced by CLAUDE.md and WORK-149.
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** CLAUDE.md updated with ADR reference
- [ ] Ground Truth Verification completed above

---

## References

- @docs/work/active/WORK-020/WORK.md (source investigation)
- @docs/work/active/WORK-149/WORK.md
- @docs/ADR/ADR-044-l4-stateless-principle.md (template reference)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-DISCOVER-002, REQ-DISCOVER-003)
- Memory: 85302, 85303, 82302

---
