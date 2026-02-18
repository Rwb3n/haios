---
template: implementation_plan
subtype: design
status: complete
date: 2026-02-18
backlog_id: WORK-101
title: "Proportional Governance Design"
author: Hephaestus
lifecycle_phase: plan
session: 397
version: "1.8"
generated: 2026-02-18
last_updated: 2026-02-18T23:05:34
---
# Design Plan: Proportional Governance Design

---

<!-- TEMPLATE GOVERNANCE (v1.4)
     Design plan template — optimized for ADRs, specs, and documentation work.
     No code-specific sections (TDD, code diffs, function signatures).
     WORK-152: Fractured from monolithic implementation_plan template.

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Query prior work | SHOULD | Search memory for similar designs before authoring |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

Define L3.20 Proportional Governance principle, two L4 requirements (REQ-LIFECYCLE-005 fast-path, REQ-CEREMONY-005 proportional depth), update close-work-cycle with pytest hard gate, and document complexity threshold criteria — so governance overhead scales with blast radius instead of being uniform.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 5 | L3-requirements.md, functional_requirements.md, close-work-cycle/SKILL.md, CLAUDE.md, WORK-101/WORK.md (C1 revision) |
| New files to create | 0 | All edits to existing files |
| Dependencies | 1 | EPOCH.md (references CH-058) |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Author L3.20 principle | 15 min | High |
| Author L4 requirements (2) | 20 min | High |
| Update close-work-cycle pytest gate | 15 min | High |
| Document threshold criteria | 10 min | High |
| Verification & references | 10 min | High |
| **Total** | **~70 min** | High |

---

## Current State vs Desired State

### Current State

**What exists now:** Governance overhead is uniform. Every work item — from a 5-line typo fix to a multi-session architecture redesign — goes through the same ceremony chain. L3 has no principle that explicitly calls for proportional governance. L4 has no requirements for fast-path lifecycles or proportional ceremony depth. Close-work-cycle relies on operator confirmation for tests rather than a hard gate. The only existing proportional scaling is retro-cycle Phase 0 (computable predicate: files_changed <= 2 AND no plan AND no test changes AND no CycleTransition events → trivial path).

**Problem:** Full ceremony chain consumes ~104% of 200k context budget (mem:85390). A 15-minute investigation goes through the same 8-skill chain as a multi-session redesign (Session 314 finding). This is not overhead — it is architectural mismatch between governance weight and work complexity.

### Desired State

**What should exist:** L3.20 Proportional Governance principle establishing that governance overhead must scale with blast radius. Two L4 requirements: REQ-LIFECYCLE-005 (fast-path for effort=small work items that can skip phases within a lifecycle) and REQ-CEREMONY-005 (proportional ceremony depth — ceremony weight scales from none to full based on computable predicates). Close-work-cycle updated with pytest hard gate for code work items (not just operator confirmation). Complexity threshold criteria documented as computable predicates (extending the retro-cycle Phase 0 pattern).

**Outcome:** Enables CH-059 (CeremonyAutomation) to implement proportional scaling based on these defined requirements. Establishes the principle that the E2.8 "call" arc implements. Unblocks the four-tier scaling model: none (trivial) → checklist (hook-injected) → full (critique-agent) → operator (design dialogue).

---

## Detailed Design

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Principle ID | L3.20 (not L3.8) | L3.8 is already "No Autonomous Irreversibility". Clean append, no renumbering. |
| Requirement IDs | REQ-LIFECYCLE-005, REQ-CEREMONY-005 | REQ-CEREMONY-004 is already "Epistemic review". REQ-LIFECYCLE-005 is available. |
| Scaling model | Four tiers: none → checklist → full → operator | Matches E2.8 EPOCH.md principle. Extends retro Phase 0 prototype. |
| Threshold approach | Computable predicates (not heuristics) | Retro Phase 0 proves this works: 4 machine-checkable conditions. Zero agent judgment needed. |
| Pytest gate scope | Code work items only (type: implementation with source_files) | Design/investigation items produce docs, not code. Pytest irrelevant for them. |
| Phase skipping vs lightweight phases | Lightweight (phases can't be skipped per REQ-FLOW invariant) | L4 functional_requirements.md line 165: "Phases cannot be skipped within a lifecycle (though can be lightweight)". Fast-path = lightweight phases, not missing phases. |

### Design Content

#### L3.20 Proportional Governance (New Principle)

```markdown
### [L3.20] Proportional Governance
Governance overhead scales with blast radius, not uniformly. Trivial changes get trivial oversight;
architectural decisions get full ceremony. The weight of governance must be proportional to the
risk and complexity of the work being governed. L3.10 prohibits grinding as a boundary (what NOT
to do); L3.20 requires proportionality as a positive obligation (what TO do). These are
complementary, not redundant.

*Added Session 397 under operator authorization (same precedent as L3.19, S393). Derived from
E2.5 finding that full ceremony chain consumes ~104% of 200k context budget (mem:85390), E2.8
Arc 1 "call" theme, and validated retro-cycle Phase 0 prototype (mem:85607). Derives from
L3.10 (No Grinding the Operator), L2.20, L1.6 (Limited Time), L1.9 (Human as Bottleneck).*
```

**Note (A1 — critique finding):** L3-requirements.md header declares `Mutability: IMMUTABLE`. Adding L3.20 follows the L3.19 (S393) precedent: principles are immutable once published, but new principles can be appended under operator authorization. Implementation Step 1 must update the L3 header to `Mutability: IMMUTABLE (append-only under operator authorization)` to resolve this.

**Note (A3 — critique finding):** Derivation chain includes L3.10 ("No Grinding the Operator") which already maps L2.20. L3.20 is the positive obligation counterpart to L3.10's prohibition.

Category: Principle (alongside L3.1-L3.7, L3.19). Not a boundary (L3.8-L3.12).

Element Registry entry:
```
| L3.20 | Principle | Proportional Governance | L3.10, L2.20, L1.6, L1.9 | REQ-LIFECYCLE-005, REQ-CEREMONY-005 |
```

#### REQ-LIFECYCLE-005 Fast-Path Lifecycle (New Requirement)

```markdown
| **REQ-LIFECYCLE-005** | Fast-path: effort=small work items MAY use lightweight phases within lifecycle | L3.20, L3.6 | Trivial work item completes lifecycle with reduced ceremony weight |
```

Full requirement text:
```markdown
## Fast-Path Lifecycle Requirements (E2.8 - Session 397)

*Derived from L3.20 (Proportional Governance) + L3.6 (Graceful Degradation)*

| ID | Requirement | Derives From | Acceptance Test |
|----|-------------|--------------|-----------------|
| **REQ-LIFECYCLE-005** | Effort=small work items MAY use lightweight phases within lifecycle. Phases are not skipped but their ceremony weight is reduced. | L3.20, L3.6 | Work item with effort=small completes lifecycle without full ceremony chain |

**Fast-Path Predicates (computable, extending retro-cycle Phase 0):**

| Condition | How to Compute | Source |
|-----------|----------------|--------|
| effort=small | Read WORK.md `effort:` field | Frontmatter |
| source_files <= 3 | Read WORK.md `source_files:` list length | Frontmatter |
| No architectural decisions | No ADR referenced in `traces_to:` AND no `type: design` | Frontmatter |
| No plan exists | Glob `docs/work/active/{id}/plans/PLAN.md` returns empty | Filesystem |

**Per-tier predicates (A8 revision: separate predicates, not one binary):**

**Trivial tier (governance: None):**
ALL of: effort=small AND source_files <= 2 AND no plan AND no ADR AND no architectural decisions

**Small tier (governance: Checklist):**
ALL of: effort=small AND source_files <= 3 AND no ADR AND no architectural decisions
(differs from Trivial: plan MAY exist, source_files up to 3)

**Standard tier (governance: Full):** Default when neither Trivial nor Small predicates match.

**Architectural tier (governance: Operator):** type=design OR ADR in traces_to.

**Fast-Path Lightweight Phases (A4 revision: phases are never skipped, only reduced in weight):**

| Lifecycle | Standard | Fast-Path (lightweight) |
|-----------|----------|------------------------|
| Investigation | EXPLORE → HYPOTHESIZE → VALIDATE → CONCLUDE | All 4 phases execute. HYPOTHESIZE/VALIDATE lightweight: inline reasoning, no separate doc. |
| Implementation | PLAN → DO → CHECK → DONE | All 4 phases execute. PLAN lightweight: CycleTransition event logged + inline note in WORK.md (no separate PLAN.md file required). |
| Close | retro → dod-validate → VALIDATE → ARCHIVE → CHAIN | retro(trivial via Phase 0) → VALIDATE(lightweight) → ARCHIVE → CHAIN |

**Note (A4 — critique finding):** "Lightweight PLAN" means the phase transition is logged and a minimal artifact exists (inline note in WORK.md), NOT that the PLAN phase is skipped. Every phase produces a governance event. This preserves REQ-FLOW-001 invariant: "Phases cannot be skipped within a lifecycle (though can be lightweight)."

**Note (A2 — critique finding):** `source_files` is a *prospective* predicate (declared scope before work begins). This is intentionally different from retro-cycle Phase 0's `files_changed` (retrospective, git diff after work). The justification: fast-path decisions must be made BEFORE work starts, not after. `source_files` enables upfront classification; `files_changed` enables post-hoc validation. Both are valid for their lifecycle position.

**Invariants:**
- Fast-path is computable (zero agent judgment)
- Phases are lightweight, not skipped (preserves REQ-FLOW invariant)
- Every phase transition logs a CycleTransition governance event, even in fast-path
- Fast-path can be overridden by operator (AskUserQuestion if uncertain)
- Threshold criteria must be documented alongside requirement
- If `source_files:` field is absent or empty in WORK.md, default to Standard tier (conservative safe default). Absent data MUST NOT produce a more permissive classification. (B1 critique finding)
```

#### REQ-CEREMONY-005 Proportional Ceremony Depth (New Requirement)

```markdown
| **REQ-CEREMONY-005** | Ceremony depth scales proportionally: none (trivial) → checklist (hook) → full (agent) → operator (design) | L3.20, L3.7 | Ceremony weight matches work complexity tier |
```

Full requirement text:
```markdown
## Proportional Ceremony Depth (E2.8 - Session 397)

*Derived from L3.20 (Proportional Governance) + L3.7 (Traceability)*

| ID | Requirement | Derives From | Acceptance Test |
|----|-------------|--------------|-----------------|
| **REQ-CEREMONY-005** | Ceremony depth MUST scale proportionally with work complexity. Four tiers: none → checklist → full → operator. | L3.20, L3.7 | Trivial item gets none/checklist; design item gets full/operator |

**Four-Tier Scaling Model:**

| Tier | Weight | Trigger | Mechanism | Token Cost |
|------|--------|---------|-----------|------------|
| None | 0 | Trivial (fast-path predicate true) | Skip ceremony entirely | ~0 |
| Checklist | Low | Small (effort=small, has plan) | Hook injects checklist, agent checks items | ~500 tokens |
| Full | High | Standard (effort=medium+) | Full ceremony skill execution | ~5000+ tokens |
| Operator | Maximum | Architectural (type=design, new ADR) | Critique-agent + operator dialogue | ~10000+ tokens |

**Detection Mechanism:**
(a) Manual verification (now): agent correctly applies tier determination logic from work item metadata when prompted.
(b) Automated verification (after CH-059): PreToolUse hook computes tier from work item metadata (zero agent tokens).
Computable from: `effort`, `type`, `source_files` count, plan existence, ADR reference.
Note: (b) depends on CH-059 CeremonyAutomation. Until then, (a) is the acceptance test.

**Invariants:**
- Detection is computable (hook, not agent judgment)
- Tier selection is logged to governance events (traceability)
- Operator can escalate any tier upward (never downward without explicit override)
- Retro-cycle Phase 0 is the prototype for this pattern (validated E2.6-E2.8)
- Tier scaling governs ceremony weight WITHIN a lifecycle, not cross-lifecycle boundary ceremonies. The Trivial/None tier does NOT exempt the investigation-to-implementation boundary from REQ-CEREMONY-004 (epistemic review). Cross-lifecycle boundaries are governed by their own requirements, independent of tier. (B4 critique finding)
```

#### Close-Work-Cycle Pytest Hard Gate

Update close-work-cycle SKILL.md VALIDATE phase to add a hard gate for code work items:

**Current (line 101-102):** Tests MUST pass — operator confirmation only.

**Proposed addition after line 101:**
```markdown
6b. **Pytest Hard Gate (WORK-101, code items only):**
    - If work item has `type: implementation` AND `source_files:` contains `.py` files:
      - **MUST** run `pytest tests/ -v` (or scoped to relevant test files)
      - If any test fails: **BLOCK** closure. Return to DO phase.
      - If no tests exist for changed files: **WARN** (soft gate, not block)
    - If work item is `type: design` or `type: investigation`: Skip pytest gate (N/A).
      Rationale: these types produce documents, not executable artifacts. Python files in
      design/investigation source_files are reference artifacts, not deployable code. (A9 critique)
```

This replaces the informal "Prompt user to confirm tests pass" with an enforced gate for code work.

#### Complexity Threshold Criteria

The threshold criteria are the fast-path predicates above, documented in a single table:

| Dimension | Trivial | Small | Standard | Architectural |
|-----------|---------|-------|----------|---------------|
| effort | small | small | medium+ | any |
| source_files | <= 2 | <= 3 | any | any |
| plan exists | no | MAY exist | yes | yes |
| ADR referenced | no | no | no | yes |
| Governance tier | None | Checklist | Full | Operator |
| **Predicate** | ALL conditions match | ALL conditions match | Default (neither Trivial nor Small) | type=design OR ADR in traces_to |

**Note (C2 — critique finding):** The `type` dimension was removed from this table because the Architectural predicate (`type=design OR ADR in traces_to`) already catches all design items. Including `type: implementation` as a condition in Trivial/Small would contradict the per-tier predicate text (which does not check type). The Architectural predicate is the authoritative type-based routing — Trivial/Small predicates check effort, source_files, plan existence, and ADR reference only.

### Open Questions

**Q: Should fast-path predicates be hardcoded in skills or configurable via YAML?**

Hardcoded in skills for now (matching retro-cycle Phase 0 approach). CH-059 (CeremonyAutomation) can migrate to YAML config when implementing the hook-based detection. This avoids premature abstraction.

**Q: Should the pytest gate in close-work-cycle run the full suite or scoped tests?**

Scoped to relevant test files when identifiable (from plan or source_files), full suite as fallback. This is consistent with how the implementation-cycle CHECK phase works.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Principle ID | L3.8 (collision), L3.20 (append) | L3.20 | Operator decision S397: L3.8 is "No Autonomous Irreversibility", clean append preferred |
| Ceremony requirement ID | REQ-CEREMONY-004 (collision), REQ-CEREMONY-005 (append) | REQ-CEREMONY-005 | Operator decision S397: REQ-CEREMONY-004 is "Epistemic review", append preferred |
| Fast-path config location | Hardcoded in skills, YAML config | Hardcoded | Matches retro Phase 0 pattern. CH-059 can migrate to YAML later. |

---

## Implementation Steps

### Step 1: Author L3.20 Proportional Governance
- [ ] **FIRST (C4 — atomic with L3.20):** Update L3-requirements.md `Mutability:` from `IMMUTABLE (principles, not rules)` to `IMMUTABLE (append-only under operator authorization)` (A1 critique finding — matching L3.19 S393 precedent). Must happen before L3.20 is written to prevent mid-implementation header contradiction.
- [ ] Add L3.20 to Element Registry table in L3-requirements.md
- [ ] Add L3.20 principle text after L3.19 in Core Behavioral Principles section. **Insertion point (A11):** immediately after the `### [L3.19] Coordination by Intent` block, before the `## Context Architecture` section header. L3.20 is a Principle (like L3.1-L3.7, L3.19), NOT a Boundary (L3.8-L3.12) or LLM Nature item (L3.13-L3.18).
- [ ] Verify derivation chain references (L2.20, L1.6, L1.9)

### Step 2: Author L4 Requirements
- [ ] Add REQ-LIFECYCLE-005 to Requirement ID Registry in functional_requirements.md
- [ ] Add REQ-CEREMONY-005 to Requirement ID Registry in functional_requirements.md
- [ ] Author full "Fast-Path Lifecycle Requirements" section with predicates and invariants
- [ ] Author full "Proportional Ceremony Depth" section with four-tier model and invariants
- [ ] Add complexity threshold criteria table

### Step 3: Update Close-Work-Cycle
- [ ] Add pytest hard gate to VALIDATE phase (step 6b) in close-work-cycle/SKILL.md
- [ ] Add gate to Quick Reference table
- [ ] Update Key Design Decisions table with pytest gate rationale

### Step 4: Update References and Traceability
- [ ] **MUST:** Update CLAUDE.md Governance Quick Reference to mention L3.20. **Content (A12):** Add a "Proportional Governance" entry under the Governance Triggers table explaining: effort=small work items MAY use lightweight phases per L3.20/REQ-LIFECYCLE-005. Include pointer to L4 functional_requirements.md for threshold criteria. This gives agents actionable guidance, not just a name reference.
- [ ] **MUST (sequencing A10):** Update WORK-101 `traces_to:` to include REQ-LIFECYCLE-005 and REQ-CEREMONY-005 (A6 critique finding). **Step 2 MUST be complete first** — requirement IDs must exist in functional_requirements.md before WORK.md references them (REQ-TRACE-002).
- [ ] **MUST:** Update WORK-101 memory_refs with stored concept IDs
- [ ] Verify no stale references to old IDs (L3.8, REQ-CEREMONY-004) in proportional governance context
- [ ] **MUST (B2):** Update WORK-101 WORK.md Context section (lines 76-78) to replace phase-skipping language with lightweight-phase language. Current: "EXPLORE -> CONCLUDE (skip HYPOTHESIZE/VALIDATE when self-evident)" and "DO -> DONE (skip PLAN/CHECK when < 20 lines)". Replace with: "All phases execute with lightweight weight (e.g., inline reasoning instead of separate documents)" — aligning with A4 invariant and REQ-FLOW-001.

### ~~Step 5: Update L3 Header~~ (Merged into Step 1 per C4 — atomic write)

---

## Verification

- [ ] L3.20 principle exists in L3-requirements.md with correct derivation chain
- [ ] REQ-LIFECYCLE-005 exists in functional_requirements.md with acceptance test
- [ ] REQ-CEREMONY-005 exists in functional_requirements.md with four-tier model
- [ ] Close-work-cycle SKILL.md has pytest hard gate in VALIDATE phase
- [ ] Complexity threshold table is documented (either in L4 or plan)
- [ ] CLAUDE.md references proportional governance
- [ ] No references to old IDs (L3.8 as proportional governance, REQ-CEREMONY-004 as proportional depth)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Fast-path predicates too permissive | Medium | Conservative defaults (ALL 4 conditions must be true). Operator can escalate. |
| Pytest gate blocks non-code items | Low | Gate scoped to type=implementation with .py source_files only. |
| Downstream consumers reference old IDs | Medium | Grep for L3.8/REQ-CEREMONY-004 in proportional governance context after authoring. |
| Threshold criteria become stale | Low | Criteria are in L4 (dynamic layer), not L3 (immutable). Can evolve with evidence. |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 397 | 2026-02-18 | - | PLAN authored | Critique REVISE verdict — 9 findings, all addressed (A1-A9) |
| 398 | 2026-02-18 | - | PLAN revised v1.6 | Fresh critique pass 1: 3 findings (A10-A12), all addressed. Step 1/4 clarified. |
| 398 | 2026-02-18 | - | PLAN revised v1.7 | Critique pass 2: 4 findings (B1-B4), 3 addressed (B1,B2,B4). B3 advisory. |
| 398 | 2026-02-18 | - | PLAN revised v1.8 | Critique pass 3: 4 findings (C1-C4), 3 addressed (C1,C2,C4). C3 advisory. Step 5 merged into Step 1. |
| 398 | 2026-02-18 | - | DO→CHECK→DONE | All 4 steps executed. 5 files modified. Ground Truth verified. WHY captured. |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-101/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| L3.20 Proportional Governance principle authored in L3-requirements.md | [ ] | Read L3-requirements.md, find L3.20 |
| REQ-LIFECYCLE-005 fast-path requirement authored in functional_requirements.md | [ ] | Read functional_requirements.md, find REQ-LIFECYCLE-005 |
| REQ-CEREMONY-005 proportional depth requirement authored in functional_requirements.md | [ ] | Read functional_requirements.md, find REQ-CEREMONY-005 |
| Close-work-cycle SKILL.md updated with pytest hard gate for code work items | [ ] | Read SKILL.md, find pytest gate in VALIDATE |
| Complexity threshold criteria documented | [ ] | Read functional_requirements.md, find threshold table |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/manifesto/L3-requirements.md` | L3.20 principle + registry entry | [ ] | |
| `.claude/haios/manifesto/L4/functional_requirements.md` | REQ-LIFECYCLE-005, REQ-CEREMONY-005, threshold table | [ ] | |
| `.claude/skills/close-work-cycle/SKILL.md` | Pytest hard gate in VALIDATE phase | [ ] | |
| `CLAUDE.md` | Proportional Governance entry in Governance Triggers (A12) | [ ] | |
| `docs/work/active/WORK-101/WORK.md` | traces_to updated, Context section corrected (B2) | [ ] | |

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Design artifact complete
- [ ] **MUST:** All WORK.md deliverables verified complete
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories
- [ ] Ground Truth Verification completed above

---

## References

- @.claude/haios/manifesto/L3-requirements.md (L3 principles — target for L3.20)
- @.claude/haios/manifesto/L4/functional_requirements.md (L4 requirements — target for REQ-LIFECYCLE-005, REQ-CEREMONY-005)
- @.claude/skills/close-work-cycle/SKILL.md (close ceremony — target for pytest gate)
- @.claude/skills/retro-cycle/SKILL.md (Phase 0 prototype for proportional scaling)
- @.claude/haios/epochs/E2_8/EPOCH.md (E2.8 context, Arc 1 "call" principles)
- @docs/work/active/WORK-101/WORK.md (work item)
- Memory: 85390 (104% problem), 85607/85363 (retro Phase 0 prototype), 84332 (40% overhead)

---
