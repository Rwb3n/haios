---
template: implementation_plan
status: complete
date: 2025-12-23
backlog_id: E2-153
title: "Unified Metaphor Section"
author: Hephaestus
lifecycle_phase: plan
session: 109
version: "1.5"
generated: 2025-12-23
last_updated: 2025-12-23T20:56:40
---
# Implementation Plan: Unified Metaphor Section

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

## Goal

ARCHITECTURE.md will contain a "Three-Layer Architecture" section documenting the Symphony→Cycles→DAG metaphor integration from INV-026, reducing re-discovery time for new sessions.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/REFS/ARCHITECTURE.md` |
| Lines of code affected | ~80 | New section added |
| New files to create | 0 | - |
| Tests to write | 0 | Pure documentation task |
| Dependencies | 0 | No code changes |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Documentation only |
| Risk of regression | None | No code changes |
| External dependencies | None | Content from INV-026 |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Add section | 15 min | High |
| Verify content | 5 min | High |
| **Total** | 20 min | High |

---

## Current State vs Desired State

### Current State

**File:** `.claude/REFS/ARCHITECTURE.md` (92 lines)

**Content:** Contains Technical Architecture section with general HAIOS overview, but no explicit documentation of the three-layer metaphor architecture (Symphony→Cycles→DAG).

**Problem:** New sessions must re-discover the metaphor relationships from scattered sources (ADR-038, INV-022, INV-026).

### Desired State

**File:** `.claude/REFS/ARCHITECTURE.md` (~170 lines)

**Content:** New "Three-Layer Governance Architecture" section containing:
1. Layer definitions (Infrastructure, Patterns, Flow)
2. Mapping table from INV-026
3. Simplified architecture diagram
4. Governance Flywheel ancestry reference

**Result:** New sessions understand metaphor layering immediately from one canonical reference.

---

## Tests First (TDD)

**SKIPPED:** Pure documentation task, no code changes. Verification is visual/content-based.

---

## Detailed Design

### Content to Add

The new section will be inserted after "Technical Architecture" (line 65) and before "Coordination & Handoffs" (line 66).

**Source Material:** INV-026 sections:
- Lines 227-232: Mapping Table
- Lines 236-257: Three-Layer Architecture Diagram

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Location | After "Technical Architecture" | Logical flow: overview → layers → coordination |
| Content source | INV-026 verbatim | Already synthesized and approved in investigation |
| Diagram style | ASCII | Consistent with existing docs, no external dependencies |

---

## Implementation Steps

### Step 1: Add Three-Layer Section to ARCHITECTURE.md
- [ ] Insert new section after "Technical Architecture" (after line 65)
- [ ] Include: Layer definitions, mapping table, diagram
- [ ] Reference INV-026 and ADR-038 as sources

### Step 2: Verify Content
- [ ] Read final ARCHITECTURE.md to verify section added correctly
- [ ] Verify `/validate` passes on the file
- [ ] Visual check: diagram renders correctly

### Step 3: Consumer Verification
**SKIPPED:** No migration/rename - new section only. No stale references possible.

---

## Verification

- [ ] ARCHITECTURE.md section exists and content is complete
- [ ] File validates via `/validate`

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Content becomes stale | Low | References source INV-026; update if architecture evolves |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 109 | 2025-12-23 | (pending) | In Progress | Plan created |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/REFS/ARCHITECTURE.md` | Contains "Three-Layer Governance Architecture" section | [x] | Lines 66-133 |

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| Section added to ARCHITECTURE.md? | Yes | Lines 66-133 |
| Mapping table present? | Yes | Lines 94-101 |
| Diagram present? | Yes | Lines 72-84, 117-125 |
| Any deviations from plan? | Yes | Added Enforcement Spectrum and Work Item Flow sections beyond INV-026 source |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Section added to ARCHITECTURE.md
- [x] WHY captured (reasoning stored to memory)
- [x] Content matches INV-026 source material (enhanced with INV-020, INV-024)

---

## References

- **INV-026:** Unified Architecture Metaphor Integration
- **ADR-038:** M2-Governance Symphony Architecture
- **INV-022:** Work-Cycle-DAG Unified Architecture
- **Session 105:** Investigation that spawned this work item

---
