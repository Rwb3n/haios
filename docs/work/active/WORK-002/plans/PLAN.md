---
template: implementation_plan
status: complete
date: 2026-01-18
backlog_id: WORK-002
title: E2.3 Triage - Strategic triage of E2 arcs and work items
author: Hephaestus
lifecycle_phase: plan
session: 207
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-18T22:00:22'
---
# Implementation Plan: E2.3 Triage - Strategic triage of E2 arcs and work items

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

Disposition all E2 arcs, architecture docs, and active work items with clear transfer/archive/dismiss decisions documented in a Migration Manifest, enabling clean E2.3 work selection.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| E2 arcs to triage | 6 | `.claude/haios/epochs/E2/arcs/` |
| Architecture docs | 16 | `.claude/haios/epochs/E2/architecture/S*.md` |
| Active work items | 57 | `docs/work/active/*/WORK.md` |
| New files to create | 1 | `epochs/E2_3/arcs/migration/MANIFEST.md` |
| Queue entries to update | 40 | `just queue default` output |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Mostly documentation/decision work |
| Risk of regression | Low | No code changes, only manifest creation |
| External dependencies | None | Pure file-based triage |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Step 1: Arc Triage | 30 min | High |
| Step 2: Architecture Doc Classification | 20 min | High |
| Step 3: Work Item Triage | 60 min | Medium |
| Step 4: Queue Cleanup | 15 min | High |
| Step 5: Manifest Creation | 15 min | High |
| **Total** | ~2.5 hrs | Medium |

---

## Current State vs Desired State

### Current State

**E2 Epoch Structure:**
```
.claude/haios/epochs/E2/
├── EPOCH.md                    # Active epoch definition
├── architecture/               # 16 S-docs (S2, S10, S12, S14-26)
└── arcs/                       # 6 arcs
    ├── breath/                 # Pressure dynamics
    ├── chariot/                # Module architecture
    ├── form/                   # Skill decomposition
    ├── ground/                 # Context loading
    ├── tongue/                 # Cognitive notation
    └── workinfra/              # Work infrastructure
```

**Active Work Items:** 57 items in `docs/work/active/` referencing E2 milestones and arcs.

**Queue State:** 40 items in default queue, all E2-prefixed.

**Problem:** E2.3 reframed HAIOS as doc-to-product pipeline. E2 artifacts reference PM infrastructure concepts that may not transfer.

### Desired State

**E2.3 Epoch Structure:**
```
.claude/haios/epochs/E2_3/
├── EPOCH.md                    # New mission definition
├── architecture/               # Pipeline-relevant S-docs only
├── arcs/                       # 5 new arcs
│   ├── migration/
│   │   └── MANIFEST.md         # Triage decisions with rationale
│   ├── observations/
│   ├── pipeline/
│   ├── provenance/
│   └── workuniversal/
└── work/                       # Transferred work items (future)
```

**Queue State:** Only pipeline-relevant items remain in queue.

**Result:** Clean separation between E2 (archived) and E2.3 (active), with documented rationale for every decision.

---

## Tests First (TDD)

**SKIPPED:** Strategic triage work produces documentation artifacts (MANIFEST.md), not code. Verification is via deliverable checklist, not automated tests.

---

## Detailed Design

### Triage Categories

| Category | Criteria | Action |
|----------|----------|--------|
| **Pipeline-relevant** | Supports doc-to-product pipeline directly | Transfer to E2.3 architecture/ |
| **Reusable-infra** | Generic infrastructure (hooks, memory, work items) | Keep in place, reference from E2.3 |
| **HAIOS-specific** | PM infrastructure for HAIOS development itself | Archive with summary |
| **Obsolete** | Completed or superseded | Archive, no action needed |

### Arc Triage Matrix

| Arc | Theme | Pipeline Relevance | Disposition |
|-----|-------|-------------------|-------------|
| **chariot** | Module architecture (9 modules) | High - modules are pipeline agents | Transfer principles, defer module work |
| **breath** | Pressure dynamics (S20) | High - inhale/exhale is pipeline pattern | Transfer S20 to E2.3 |
| **form** | Skill decomposition | Medium - skills support pipeline | Archive, skills are HAIOS-specific |
| **ground** | Context loading, portals | High - context loading = corpus loading | Transfer ground-cycle concept |
| **tongue** | Cognitive notation (S21) | Low - notation is HAIOS-specific | Archive |
| **workinfra** | Work item infrastructure | Medium - universal work items transfer | Transfer structure, archive E2-specific |

### Architecture Doc Classification

| Doc | Content | Classification |
|-----|---------|----------------|
| S2 | Lifecycle diagrams | Reusable-infra |
| S10 | Skills taxonomy | HAIOS-specific |
| S12 | Invocation paradigm | HAIOS-specific |
| S14 | Bootstrap architecture (L0-L4) | Reusable-infra |
| S15 | Information architecture | Reusable-infra |
| S17 | Modular architecture | Pipeline-relevant |
| S19 | Skill/work unification | HAIOS-specific |
| S20 | Pressure dynamics | Pipeline-relevant |
| S21 | Cognitive notation | HAIOS-specific |
| S22 | Skill patterns | Pipeline-relevant |
| S23 | Files as context | Pipeline-relevant |
| S24 | Staging pattern | Pipeline-relevant |
| S25 | SDK path to autonomy | Pipeline-relevant |
| S26-skill-recipe | Skill/recipe binding | HAIOS-specific |
| S26-pipeline | Pipeline architecture | Pipeline-relevant |
| S2C | Work item directory | Reusable-infra |

### Work Item Triage Strategy

**Batch by type:**
1. `INV-*` items: Review investigation scope, archive if HAIOS-specific
2. `E2-*` items: Review deliverables, archive if milestone-specific
3. `TD-*` items: Technical debt - likely archive unless infrastructure
4. `WORK-*` items: New universal format - keep active

**Decision factors:**
- Does this enable pipeline stages (INGEST/PLAN/BUILD/VALIDATE)?
- Is this generic infrastructure usable in any project?
- Is this HAIOS development PM overhead?

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Transfer S20, S22, S23-26 to E2.3 | Selected pipeline-relevant docs | These directly support doc-to-product transformation |
| Archive form, tongue arcs | HAIOS-specific | Skills and notation are implementation details, not pipeline |
| Keep ground arc concept | Transfer | Corpus loading IS context loading - same pattern |
| Don't move E2 archive | Keep in place | References from memory_refs would break |

### Edge Cases

| Case | Handling |
|------|----------|
| Work item blocks another | Check if blocker transfers, update or dismiss blocked_by |
| Investigation spawned work | If investigation archived, check if spawned work is independent |
| Memory refs point to E2 concepts | Memory concepts are immutable, keep references valid |

---

## Open Decisions (MUST resolve before implementation)

**No open decisions.** Work item `operator_decisions` field is empty. All triage decisions will be made during implementation based on the criteria above and documented in MANIFEST.md.

---

## Implementation Steps

### Step 1: Arc Triage
- [x] Read each E2 arc ARC.md (6 arcs)
- [x] Apply triage matrix from Detailed Design
- [x] Record disposition for each arc in working notes

### Step 2: Architecture Doc Classification
- [x] Read each S-doc header/purpose (16 docs)
- [x] Apply classification from Detailed Design
- [x] Note any docs that need copying to E2.3 architecture/

### Step 3: Work Item Triage
- [x] Export list of active work items (59 items - 2 new universal items)
- [x] Batch by prefix (INV-, E2-, TD-, WORK-)
- [x] For each item: read title/deliverables, apply decision factors
- [x] Mark as: transfer, archive, or dismiss

### Step 4: Create Migration Manifest
- [x] Create `epochs/E2_3/arcs/migration/MANIFEST.md`
- [x] Document arc triage decisions with rationale
- [x] Document architecture doc dispositions
- [x] Document work item dispositions

### Step 5: Queue Cleanup
- [x] Remove archived/dismissed items from queue (via status update)
- [x] Verify `just queue default` shows only transferred items (16 items)

### Step 6: Verification
- [x] All 6 arcs have documented disposition
- [x] All 16 architecture docs classified
- [x] All 59 work items dispositioned
- [x] MANIFEST.md complete with rationale
- [x] Queue reflects only transferred items

---

## Verification

- [x] MANIFEST.md exists at `epochs/E2_3/arcs/migration/MANIFEST.md`
- [x] All arcs have disposition entry with rationale
- [x] All architecture docs have classification
- [x] All work items have disposition
- [x] Queue cleaned up (16 items, was 54)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Wrong classification | Medium | Use explicit criteria, document rationale, operator can override |
| Break memory_refs | High | Don't move/rename archived items, only mark disposition |
| Miss work items | Medium | Use Glob to enumerate, verify count matches expected |
| Dismiss needed items | Low | Disposition is documentation, items remain in place until explicit action |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 207 | 2026-01-18 | SESSION-207 | Plan created | Plan authored and approved |
| 208 | 2026-01-18 | (pending) | Complete | Full implementation, queue cleanup, filter fix |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-002/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Arc triage manifest | [ ] | MANIFEST.md has 6 arc entries |
| Work item triage | [ ] | MANIFEST.md has 57 work item entries |
| Architecture doc classification | [ ] | MANIFEST.md has 16 S-doc entries |
| Queue cleanup | [ ] | `just queue default` shows reduced count |
| Migration manifest | [ ] | File exists at expected path |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `epochs/E2_3/arcs/migration/MANIFEST.md` | Contains arc, doc, and work item sections | [ ] | |
| `epochs/E2_3/arcs/migration/ARC.md` | Status updated to reflect progress | [ ] | |

**Verification Commands:**
```bash
# Count manifest entries
Grep(pattern="^\|", path="epochs/E2_3/arcs/migration/MANIFEST.md", output_mode="count")
# Expected: >80 rows (arcs + docs + items + headers)
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All arc dispositions documented? | [Yes/No] | |
| All architecture docs classified? | [Yes/No] | |
| All work items dispositioned? | [Yes/No] | |
| Queue reflects only transferred items? | [Yes/No] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] MANIFEST.md created with all sections
- [ ] WHY captured (reasoning stored to memory)
- [ ] Ground Truth Verification completed above

> **Note:** This is documentation/decision work, not code. "Tests pass" and "runtime consumer" criteria don't apply.

---

## References

- @.claude/haios/epochs/E2_3/arcs/migration/ARC.md (Migration arc definition)
- @.claude/haios/epochs/E2/EPOCH.md (Source epoch)
- @.claude/haios/epochs/E2_3/EPOCH.md (Target epoch)
- @docs/checkpoints/2026-01-18-05-SESSION-206-e23-epoch-creation-and-strategic-review.md (Strategic review)

---
