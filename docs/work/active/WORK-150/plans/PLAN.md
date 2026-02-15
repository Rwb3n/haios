---
template: implementation_plan
status: complete
date: 2026-02-15
backlog_id: WORK-150
title: "Plan Decomposition Traceability ADR"
author: Hephaestus
lifecycle_phase: plan
session: 379
version: "1.5"
generated: 2026-02-15
last_updated: 2026-02-15T23:15:29
---
# Implementation Plan: Plan Decomposition Traceability ADR

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Query prior work | SHOULD | Memory queried: 85326, 85332, 85523, 85526, 85518, 85519 |
| Document design decisions | MUST | Key Design Decisions table populated |
| Use /new-adr command | MUST | Memory 85518/85526: governance hooks block raw Write to docs/ADR/ |

---

## Goal

Create ADR-046 formalizing the plan decomposition traceability pattern designed in WORK-097: spawn_type field, decomposition_map section, and computable trigger thresholds.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 0 | Pure ADR creation, no code changes |
| New files to create | 1 | `docs/ADR/ADR-046-plan-decomposition-traceability.md` |
| Tests to write | 0 | ADR is a design document |
| Dependencies | 0 | No code dependencies |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | ADR document only |
| Risk of regression | Low | No code changes |
| External dependencies | Low | None |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| ADR authoring | 20 min | High |
| Critique + revision | 10 min | High |
| **Total** | **30 min** | High |

---

## Current State vs Desired State

**SKIPPED:** Pure ADR document task, no code changes. Current/desired state is documented in WORK-097 findings (Sections 1-5).

---

## Tests First (TDD)

**SKIPPED:** ADR is a design document — no testable code produced.

---

## Detailed Design

### ADR Content Structure

The ADR will follow the established pattern from ADR-045 (most recent accepted ADR):

**Frontmatter:**
```yaml
template: architecture_decision_record
status: proposed
adr_id: ADR-046
title: "Plan Decomposition Traceability"
spawned_by: WORK-150
traces_to: [REQ-ASSET-003, REQ-ASSET-004, REQ-ASSET-005]
memory_refs: [85325, 85326, 85331, 85332, 85340]
```

**Sections (following ADR template):**
1. Context — problem statement from WORK-097 Section 1 (E2-292 case study)
2. Decision Criteria (RFC 2119) — governance requirements for this ADR
3. Considered Options — 3 alternatives evaluated
4. Decision — the three design decisions formalized
5. Consequences — positive/negative/neutral impacts

### Three Decisions to Formalize

**Decision 1: spawn_type field**
- Source: WORK-097 Section 2
- Content: `spawn_type` enum with 4 values (decomposition, investigation, observation, follow-up)
- Rationale: Decomposition IS spawning with a type tag (Memory 85325)

**Decision 2: decomposition_map section**
- Source: WORK-097 Section 3
- Content: Plan frontmatter `decomposed: true` + markdown table mapping steps to children
- Rationale: Parent plan stays intact, children reference it

**Decision 3: computable trigger thresholds**
- Source: WORK-097 Section 4
- Content: Threshold table (files >5, steps >5, modules >2, effort >2h) checked at plan-validation-cycle
- Rationale: Move decomposition check from DO phase (too late) to end of PLAN phase

### Considered Options (for ADR)

| Option | Description | Verdict |
|--------|-------------|---------|
| A: Separate decomposed_into/from fields | New fields on parent and child | Rejected — adds fields when spawned_by already carries the link |
| B: spawn_type + decomposition_map (chosen) | Extend existing spawned_by with type tag | Accepted — minimal new infrastructure, reuses SpawnTree |
| C: No formal pattern | Continue ad-hoc decomposition | Rejected — loses traceability (E2-292 evidence) |

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| ADR creation method | `/new-adr` command | Memory 85518/85526: governance hooks block raw Write to docs/ADR/ |
| ADR numbering | ADR-046 | Next sequential after ADR-045 |
| Content source | WORK-097 findings verbatim | Investigation already completed, ADR formalizes |
| Status | proposed (operator accepts) | ADR requires operator approval per template |

### Open Questions

None — all design decisions were resolved in WORK-097 investigation.

---

## Open Decisions (MUST resolve before implementation)

No operator decisions pending. All decisions resolved in WORK-097.

---

## Implementation Steps

### Step 1: Create ADR via /new-adr command
- [ ] Invoke `/new-adr` to scaffold ADR-046
- [ ] Read scaffolded file

### Step 2: Author ADR content
- [ ] Populate frontmatter (spawned_by, traces_to, memory_refs)
- [ ] Write Context section from WORK-097 Section 1 (E2-292 case study)
- [ ] Write Considered Options (3 options from Detailed Design above)
- [ ] Write Decision section with all 3 decisions
- [ ] Write Consequences section

### Step 3: Critique
- [ ] Run critique-agent on ADR content (Memory 85519: ADR content critique found gaps plan critique missed)

### Step 4: Operator Approval
- [ ] Present ADR for operator review
- [ ] Update status to `accepted` on approval

### Step 5: Update WORK-150 artifacts
- [ ] Add ADR path to WORK-150 artifacts field

---

## Verification

- [ ] ADR file exists at `docs/ADR/ADR-046-plan-decomposition-traceability.md`
- [ ] All 4 acceptance criteria from WORK-150 met
- [ ] ADR status is `accepted`

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| ADR content duplicates WORK-097 without adding value | Low | ADR formalizes decisions; WORK-097 documents investigation process — different purposes |
| Governance hooks block ADR creation | Medium | Use `/new-adr` command per Memory 85518 |
| spawn_type enum values incomplete | Low | 4 values cover all observed spawn patterns; can extend later |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 379 | 2026-02-15 | - | Plan authored | - |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-150/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| ADR document created | [ ] | File exists at docs/ADR/ADR-046-*.md |
| spawn_type enum values documented | [ ] | ADR Decision section contains enum table |
| decomposition_map section format specified | [ ] | ADR Decision section contains format spec |
| Trigger thresholds with SHOULD/MAY levels | [ ] | ADR Decision section contains threshold table |
| CLAUDE.md updated if needed | [ ] | Verify — likely N/A (ADR doesn't change code) |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `docs/ADR/ADR-046-plan-decomposition-traceability.md` | ADR with status: accepted | [ ] | |
| `docs/work/active/WORK-150/WORK.md` | artifacts field updated | [ ] | |

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] **MUST:** All WORK.md deliverables verified complete
- [ ] WHY captured (reasoning stored to memory)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> Note: "Tests pass" and "Runtime consumer exists" N/A for pure ADR design work.

---

## References

- @docs/work/active/WORK-097/WORK.md (source investigation)
- @docs/work/active/E2-292/WORK.md (case study)
- @docs/ADR/ADR-045-three-tier-entry-point-architecture.md (ADR template pattern)
- Memory: 85325, 85326, 85331, 85332, 85340 (WORK-097 findings)
- Memory: 85518, 85519, 85523, 85526 (S378 ADR learnings)

---
