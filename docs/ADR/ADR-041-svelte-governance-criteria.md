---
template: architecture_decision_record
status: accepted
date: 2026-01-08
adr_id: ADR-041
title: Svelte Governance Criteria
author: Hephaestus
session: 183
lifecycle_phase: decide
decision: pending
spawned_by: INV-061
memory_refs:
- 81149
- 81150
- 81151
- 81152
- 81153
- 81154
version: '1.1'
generated: '2026-01-08'
last_updated: '2026-01-08T21:45:06'
---
# ADR-041: Svelte Governance Criteria

@docs/README.md
@docs/work/archive/INV-061/WORK.md

> **Status:** Accepted
> **Date:** 2026-01-08
> **Decision:** Approved (Session 183)

---

## Context

Epoch 2.2 ("The Refinement") aims to distill the governance suite into leaner architecture. Session 182-183 survey and INV-061 investigation revealed:

1. **WorkEngine is bloated** - 1195 lines, 5 responsibility clusters
2. **Modules aren't portable** - All except WorkEngine depend on lib/
3. **Session flow lacks breath** - No [volumous] phase before picking work
4. **CycleRunner is exemplar** - 220 lines, single responsibility, correct pattern

We need explicit criteria to guide "svelte" refactoring decisions.

---

## Decision Drivers

- CycleRunner (220 lines) works; WorkEngine (1195 lines) is anti-pattern
- S20 pressure dynamics requires [volumous] phases for agent breathing
- UNIX philosophy: each module does one thing well
- Portability is Epoch 3 scope; facades acceptable for E2.2

---

## Considered Options

### Option A: No Explicit Criteria
**Description:** Continue organic growth, address bloat case-by-case.

**Pros:**
- No upfront coordination cost
- Flexible to context

**Cons:**
- Continued accumulation without retirement
- No shared vocabulary for "svelte"
- Each refactoring reinvents criteria

### Option B: Explicit Svelte Criteria
**Description:** Define numeric and structural criteria based on INV-061 findings.

**Pros:**
- Clear targets for refactoring (max 300 lines, single responsibility)
- Shared vocabulary across sessions
- Measurable compliance

**Cons:**
- May need adjustment as patterns emerge
- Rigid numbers may not fit all cases

---

## Decision

**Adopt Option B: Explicit Svelte Criteria**

### Size Constraints

| Metric | Target | Rationale |
|--------|--------|-----------|
| Max lines per module | **300** | CycleRunner is 220, ContextLoader is 195 - these work |
| Max responsibilities | **1** | UNIX philosophy: do one thing well |
| Max lib/ imports | **3** | Minimize coupling |

### Structural Constraints

| Constraint | Requirement | Rationale |
|------------|-------------|-----------|
| Single writer | Each state has exactly one module that writes it | No race conditions |
| Facades acceptable | Modules MAY delegate to lib/ | Portability is Epoch 3 |
| Events over calls | Cross-module via events when possible | Loose coupling |
| Markdown prompts | Skills are prompts, not code | Claude interprets |
| **Status over location** | `status` field determines state, not directory path | References stay valid throughout epoch |

### Breath Constraints (S20)

| Constraint | Requirement |
|------------|-------------|
| Every cycle has [volumous] | At least one explore phase |
| Gates are binary | [tight] phases are pass/fail |
| Session has SURVEY | Volumous before tight |

---

## Consequences

**Positive:**
- Clear refactoring targets
- WorkEngine decomposition has measurable goal (5 modules, each ≤300 lines)
- New modules start with constraints in mind

**Negative:**
- May need to adjust numbers as edge cases emerge
- Strict interpretation could block legitimate designs

**Neutral:**
- Portability deferred to Epoch 3 (not blocked, just scoped)

---

## Implementation

- [x] Define criteria (this ADR)
- [ ] E2-279: WorkEngine Decomposition to ≤300 lines each
- [ ] E2-280: SURVEY Skill-Cycle with [volumous] phases
- [ ] E2-281: Remove archive move from close-work (status over location)
- [ ] Update CLAUDE.md with svelte governance reference

---

## References

- INV-061: Svelte Governance Architecture investigation
- S20: Pressure Dynamics (breath patterns)
- S17: Modular Architecture (5 Chariot modules)
