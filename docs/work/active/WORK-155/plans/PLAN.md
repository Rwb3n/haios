---
template: implementation_plan
subtype: design
status: complete
date: 2026-02-16
backlog_id: WORK-155
title: "Lifecycle Work-Type Awareness Beyond Plan Templates"
author: Hephaestus
lifecycle_phase: plan
session: 390
version: "1.5"
generated: 2026-02-16
last_updated: 2026-02-16T23:30:00
---
# Design Plan: Lifecycle Work-Type Awareness Beyond Plan Templates

---

<!-- TEMPLATE GOVERNANCE (v1.4)
     Design plan template — optimized for ADRs, specs, and documentation work.
     No code-specific sections (TDD, code diffs, function signatures).
     WORK-152: Fractured from monolithic implementation_plan template.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Query prior work | DONE | 13 memory concepts loaded (85528-85608), all cycle skills read |
| Document design decisions | MUST | Key Design Decisions table populated below |
| Ground truth metrics | MUST | File counts from Glob, skill analysis from Read |

---

## Goal

Design a specification for how the lifecycle ceremony chain adapts to work item type, extending the computable predicate pattern from retro-cycle Phase 0 to the full implementation-cycle pipeline, and defining which phases/gates are mandatory vs optional per work type.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 0 | Design-only work item, no code changes |
| New files to create | 1 | This specification document |
| Dependencies | 8 | Cycle skills that will consume this spec (implementation-cycle, investigation-cycle, plan-validation-cycle, close-work-cycle, retro-cycle, dod-validation-cycle, routing-gate, design-review-validation) |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| EXPLORE | 45 min | High (complete) |
| SPECIFY | 30 min | High |
| CRITIQUE | 15 min | Medium |
| **Total** | ~90 min | |

---

## Current State vs Desired State

### Current State

**What exists now:** The ceremony chain is type-agnostic. All work items (feature, design, investigation, bug, chore) route through the same implementation-cycle phases: plan-authoring → plan-validation → critique → preflight → DO (TDD) → design-review-validation → CHECK (pytest) → retro → close. The only type-awareness is:

1. **Routing-gate:** Routes `type: investigation` to investigation-cycle; everything else to implementation-cycle or work-creation-cycle
2. **PLAN_TYPE_MAP (WORK-152):** Maps work types to plan template types (implementation/design/cleanup) for section-appropriate plans
3. **Implementation-cycle CHECK (ad-hoc):** Lines 214-224 note "for non-code tasks: skip pytest, focus on Ground Truth"
4. **Retro-cycle Phase 0:** Computable predicate scales retro depth by effort indicators (files changed, plan exists, tests changed, cycle events)

**Problem:** A `type: design` work item routes through the same 12-phase ceremony chain as `type: feature`. Design work doesn't need TDD gates, file manifests, design-review-validation, or pytest. This wastes ~25% of ceremony context budget (~5000 tokens) and forces agents to SKIP irrelevant gates. The `allowed_types` in validate.py only permits 5 types (`feature`, `investigation`, `bug`, `chore`, `spike`) while 10 types exist in the system. Memory 85606: full ceremony chain = ~104% context budget.

### Desired State

**What should exist:** A ceremony profile system that configures which phases/gates are mandatory, optional, or skipped per work type. The system uses computable predicates (extending retro-cycle Phase 0) to determine the ceremony profile at work selection time. Each cycle skill checks its profile and skips irrelevant phases.

**Outcome:** Design work items skip TDD/file-manifest/design-review gates. Bug/chore items use lighter critique. Investigation already has its own cycle. The ceremony-to-substance ratio improves for all non-implementation work types. Type taxonomy is rationalized.

---

## Detailed Design

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Map types to profiles, don't normalize | CEREMONY_PROFILE_MAP: 9 types -> 4 profiles | PLAN_TYPE_MAP precedent (WORK-152). Keep existing types for backward compat. Adding a mapping layer is proven pattern. (Critique A1: limit to proven types only.) |
| No new cycle skill for design | Implementation-cycle gains type-aware gate skipping | Design lifecycle templates exist but creating a 9th cycle skill adds maintenance cost. Better to make existing cycles type-aware. (Critique A5: add Quick Reference section so agents skip irrelevant gates early.) |
| On-demand profile resolution | Each gate resolves profile from work item `type` field | Critique A2/A3: Pre-computing profile at survey-cycle requires a write dependency. On-demand is stateless, self-healing, and eliminates the risk of stale extension fields. |
| Dual enforcement (SKILL.md + Python) | Prose table in SKILL.md + `should_execute_gate()` in cycle_runner.py | Critique A2: Relying solely on markdown interpretation is fragile. Programmatic backup ensures gates are correctly evaluated even if agent misinterprets conditional text. |
| Profile name "full" not "implementation" | Avoid type/profile naming collision | Critique A8: `type: implementation` and `profile: implementation` are confusingly identical. "full" is self-descriptive and unambiguous. |
| SHOULD = execute by default | Forward-compatible annotation for WORK-101 | Critique A4: Until proportional governance provides computable skip predicates, SHOULD gates behave as MUST with softer audit trail. No current behavior change. |
| validate.py allowed_types expanded | Add `design`, `bugfix`, `cleanup`, `task` (not `implementation`) | Critique A1/A8: Only add types with proven usage. `implementation` excluded due to redundancy with `feature`. |
| plan-validation-cycle reads subtype | Route to type-specific section registry | WORK-152 pattern: `subtype` in frontmatter routes to correct validation rules. Already implemented in `validate_template()`. |
| dod-validation adapts by type directly | Type-aware criteria in dod-validation-cycle SKILL.md | Critique A7: Rather than external PHASE_CONFIG lookup, dod-validation checks work item `type` directly for test criterion adaptation. Self-contained. |

### Design Content

#### 1. Ceremony Profile System

**Four ceremony profiles** (mapped from work types):

```
CEREMONY_PROFILE_MAP = {
    # Full ceremony chain
    "feature": "full",
    "spike": "full",

    # Investigation has own cycle (already handled by routing-gate)
    "investigation": "investigation",

    # Design: skip TDD, file manifests, design-review, pytest
    "design": "design",

    # Cleanup: lighter critique, simpler validation
    "bug": "cleanup",
    "bugfix": "cleanup",
    "chore": "cleanup",
    "cleanup": "cleanup",
    "task": "cleanup",
}
# Default: "full" for any unmapped type
```

**Note (Critique A1, A8):** `type: implementation` is NOT added — it is redundant with `type: feature` and causes naming collision with the former profile name. Existing items with `type: implementation` should be treated as `feature` (the default profile). The profile name is "full" (not "implementation") to avoid type/profile confusion.

#### 2. Per-Profile Phase Configuration

Each profile defines which implementation-cycle gates are mandatory/optional/skipped:

| Gate/Phase | full | design | cleanup | investigation |
|------------|------|--------|---------|---------------|
| plan-authoring-cycle | MUST | MUST (design template) | MUST (cleanup template) | N/A (own cycle) |
| plan-validation-cycle | MUST (all sections) | MUST (design sections) | SHOULD (relaxed) | N/A |
| critique-agent (Gate 1) | MUST | MUST (decision quality) | SHOULD | N/A |
| preflight-checker (Gate 3) | MUST | SKIP | SHOULD | N/A |
| DO phase: TDD | MUST | SKIP (authoring, not coding) | MUST | N/A |
| DO phase: file manifest | MUST | SKIP | SHOULD | N/A |
| design-review-validation | MUST | SKIP | SKIP | N/A |
| CHECK phase: pytest | MUST | SKIP (/validate only) | MUST | N/A |
| CHECK phase: deliverables | MUST | MUST | MUST | N/A |
| retro-cycle | Computable | Computable | Computable | Computable |
| dod-validation-cycle | MUST | MUST (no test check) | MUST | MUST (epistemic) |
| close-work-cycle | MUST | MUST | MUST | MUST |

**This table is the single source of truth.** The PHASE_CONFIG dict (Section 4) is a subset covering only gates that vary by profile. Gates that are always MUST or always Computable are omitted from PHASE_CONFIG because they don't need profile-based branching.

Legend:
- **MUST**: Gate is mandatory, cannot skip
- **SHOULD**: Gate is recommended, can skip with rationale (see Section 4 note on SHOULD semantics)
- **SKIP**: Gate is not applicable for this profile
- **N/A**: Work type uses a different cycle entirely
- **Computable**: Retro-cycle Phase 0 predicate applies (independent of ceremony profile)

#### 3. Profile Resolution (On-Demand)

**Critique A2/A3 revision:** Profile is resolved on-demand at each gate, not pre-computed and stored. This eliminates the survey-cycle write dependency and makes the system self-healing (no stale extension field).

```python
def get_ceremony_profile(work_type: str) -> str:
    """Resolve ceremony profile from work item type.

    Called at each gate to determine MUST/SHOULD/SKIP.
    Falls back to "full" for unmapped types.
    """
    return CEREMONY_PROFILE_MAP.get(work_type, "full")

def should_execute_gate(work_type: str, gate_name: str) -> str:
    """Check gate disposition for a work type.

    Returns: "MUST", "SHOULD", or "SKIP"
    """
    profile = get_ceremony_profile(work_type)
    return PHASE_CONFIG.get(profile, {}).get(gate_name, "MUST")
```

**Dual enforcement (Critique A2 mitigation):**
1. **SKILL.md documentation:** The Per-Profile Phase Configuration table (Section 2) is the human-readable reference. Agents read it when interpreting the skill.
2. **Programmatic backup:** `get_ceremony_profile()` and `should_execute_gate()` live in `cycle_runner.py` alongside CYCLE_PHASES. Any agent or hook can call these to get a definitive answer. This prevents silent failure from markdown misinterpretation.

**No extensions field needed.** The work item's `type` field is the only input. Resolution is stateless and deterministic.

#### 4. Gate Skip Mechanism

Each gate in implementation-cycle checks the profile before executing:

```
# In implementation-cycle PLAN phase, before invoking preflight:
# Read work_type from WORK.md frontmatter (already available in phase)
gate = should_execute_gate(work_type, "preflight")
if gate == "SKIP":
    # Log: "GateSkipped: preflight, profile={profile}, type={work_type}"
    # Proceed to next gate
elif gate == "SHOULD":
    # Execute unless operator has explicitly opted out
    # Log: "GateExecuted: preflight, profile={profile}, disposition=SHOULD"
elif gate == "MUST":
    # Execute unconditionally
```

**SHOULD semantics (Critique A4):** A SHOULD gate executes by default. It can only be skipped if:
1. The operator explicitly opts out (via AskUserQuestion during the session), OR
2. WORK-101 (proportional governance, E2.9) provides a computable predicate for skipping

Until WORK-101 is implemented, SHOULD gates behave as MUST with a softer audit trail (GateExecuted vs GatePassed). This makes SHOULD a forward-compatible annotation, not a current behavior change.

The phase configuration covers only gates that vary by profile:

```python
PHASE_CONFIG = {
    "full": {
        "plan_validation": "MUST",
        "critique": "MUST",
        "preflight": "MUST",
        "tdd": "MUST",
        "file_manifest": "MUST",
        "design_review": "MUST",
        "pytest": "MUST",
    },
    "design": {
        "plan_validation": "MUST",
        "critique": "MUST",
        "preflight": "SKIP",
        "tdd": "SKIP",
        "file_manifest": "SKIP",
        "design_review": "SKIP",
        "pytest": "SKIP",
    },
    "cleanup": {
        "plan_validation": "SHOULD",
        "critique": "SHOULD",
        "preflight": "SHOULD",
        "tdd": "MUST",
        "file_manifest": "SHOULD",
        "design_review": "SKIP",
        "pytest": "MUST",
    },
}
# Gates NOT in PHASE_CONFIG (always MUST for all profiles, or use own scaling):
# - plan_authoring: always MUST (template selection handles type adaptation)
# - deliverables: always MUST
# - retro-cycle: uses own Phase 0 computable predicate (independent of profile)
# - dod-validation: always MUST (criteria adapt internally by type)
# - close-work-cycle: always MUST
# "investigation" profile: not needed — routing-gate sends to investigation-cycle
```

#### 5. Integration Points

**5a. Survey-cycle (CHOOSE phase):**
No changes needed. Profile is resolved on-demand, not stored. Survey-cycle continues to route by type as it does today.

**5b. Routing-gate:**
Add `type: design` handling. Currently only routes investigation vs implementation. Update decision table:
- `type: investigation` → investigation-cycle (unchanged)
- `type: design` with plan → implementation-cycle (profile resolved on-demand)
- `type: design` without plan → work-creation-cycle (unchanged)

No new cycle skill needed. Design work uses implementation-cycle. The profile is resolved on-demand from the `type` field at each gate.

**5c. Implementation-cycle SKILL.md (Critique A5 mitigation):**
Add a "Profile Quick Reference" section near the top of the skill, before the phase details:
```markdown
## Ceremony Profile Quick Reference

Read the work item `type` field. Look up profile:

| Work Type | Profile | Key Skips |
|-----------|---------|-----------|
| feature, spike | full | None — all gates mandatory |
| design | design | Skip: preflight, TDD, file manifest, design-review, pytest |
| bug, bugfix, chore, cleanup, task | cleanup | Skip: design-review. SHOULD: validation, critique, preflight, file manifest |

If profile is "design" or "cleanup", skip to the relevant gates below.
Do NOT read gates marked SKIP for your profile.
```

Then each MUST gate adds a one-line profile annotation:
```
**Gate 1 - Critique** [full: MUST | design: MUST | cleanup: SHOULD]
```

**5d. Plan-validation-cycle:**
CHECK phase reads `subtype` from plan frontmatter to select section registry:
- `subtype: null` or missing → `implementation_plan` registry (full section list)
- `subtype: design` → `implementation_plan_design` registry
- `subtype: cleanup` → `implementation_plan_cleanup` registry

This is the WORK-152 pattern already implemented in `validate_template()`. The plan-validation-cycle SKILL.md should reference the subtype routing.

**5e. dod-validation-cycle (Critique A7 mitigation):**
VALIDATE phase adapts "Tests MUST pass" criterion based on work item type:
- `type` in [feature, spike, bug, bugfix, chore, cleanup, task] → pytest required
- `type: design` → /validate required, pytest N/A
- `type: investigation` → epistemic review required (already in investigation-cycle CONCLUDE)

Update dod-validation-cycle SKILL.md directly with these type-aware criteria, rather than depending on an external PHASE_CONFIG lookup.

**5f. validate.py allowed_types:**
Expand to include proven types only (Critique A1 mitigation):
```python
"allowed_types": [
    "feature", "investigation", "bug", "chore", "spike",
    "design", "bugfix", "cleanup", "task",
],
# NOTE: "implementation" type NOT added — redundant with "feature" (Critique A8).
# Existing items with type: implementation are legacy; validate.py will warn but
# CEREMONY_PROFILE_MAP.get("implementation", "full") still returns "full" safely.
```

#### 6. Relationship to WORK-101 (Proportional Governance)

WORK-155 and WORK-101 are **orthogonal**:

| Dimension | WORK-155 | WORK-101 |
|-----------|----------|----------|
| **What scales** | Which gates apply | How deep each gate goes |
| **Input signal** | `type` field (categorical) | `effort` field + computable predicate (continuous) |
| **Mechanism** | Profile → skip gates | Predicate → fast-path through gates |
| **Example** | Design skips TDD entirely | Small feature skips detailed design within TDD |
| **Scope** | E2.7 (Composability) | E2.9 (Governance) |

WORK-155 removes irrelevant gates. WORK-101 makes relevant gates proportional. They compose.

### Open Questions

**Q: Should PHASE_CONFIG live in haios.yaml or in Python code?**

Answer: Both cycle_runner.py (programmatic) and SKILL.md (documentation). Move to haios.yaml only when WORK-101 (proportional governance) needs dynamic configuration. YAGNI for now — the mapping is small and stable.

**Q: How does the profile interact with activity_matrix.yaml phase_to_state mapping?**

Answer: No interaction needed. The phase_to_state mapping maps cycle phases to governance states. The profile determines which phases execute, but each phase still maps to the same state. If a phase is skipped, no state mapping is needed for it.

**Q: What happens when a SHOULD gate is skipped?**

Answer: Until WORK-101 is implemented, SHOULD gates execute by default (behave as MUST with softer audit trail). Only operator explicit opt-out can skip a SHOULD gate. When skipped, log: `GateSkipped: {gate_name}, profile={profile}, rationale="operator opt-out"`.

**Q: Does "cleanup skips detailed design" (acceptance criterion 2) mean a ceremony-level skip?**

Answer: No. "Cleanup skips detailed design" is handled by WORK-152's plan template fracturing. The cleanup plan template omits "Current/Desired State" and "Detailed Design" sections entirely. This is a template-level adaptation, not a ceremony-level skip. The ceremony profile for cleanup adapts other gates (critique SHOULD, preflight SHOULD, design-review SKIP). The acceptance criterion is satisfied by the combination of WORK-152 (template) + WORK-155 (ceremony).

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Where does CEREMONY_PROFILE_MAP live? | [scaffold.py, cycle_runner.py, haios.yaml] | cycle_runner.py | PLAN_TYPE_MAP lives in scaffold.py (plan-specific). CEREMONY_PROFILE_MAP is lifecycle-specific, belongs with CYCLE_PHASES in cycle_runner.py. |
| Where does PHASE_CONFIG live? | [SKILL.md only, cycle_runner.py only, both] | Both (Critique A2) | Dual enforcement: prose table in SKILL.md for agent interpretation + `should_execute_gate()` function in cycle_runner.py for programmatic backup. Neither alone is sufficient. |
| Profile storage vs on-demand? | [Store in extensions, Resolve on-demand] | On-demand (Critique A3) | Eliminates survey-cycle write dependency. Work item `type` field is the only input. Stateless and deterministic. |
| Profile name for full chain? | ["implementation", "full"] | "full" (Critique A8) | Avoids naming collision between `type: implementation` and profile name. "full" is self-descriptive. |
| What does SHOULD mean before WORK-101? | [Execute always, Skip always, Execute by default] | Execute by default (Critique A4) | SHOULD = MUST with softer audit trail until WORK-101 provides computable skip predicates. Forward-compatible annotation. |

---

## Implementation Steps

<!-- Each step describes authoring work, not code changes -->

### Step 0: Fix Type Taxonomy (prerequisite, code work)
- [ ] Expand `allowed_types` in validate.py to add: `design`, `bugfix`, `cleanup`, `task`
- [ ] Add tests for new type validation
- [ ] Can be a separate WORK item or bundled with Step 1b

### Step 1a: Author Specification Document (this document)
- [x] EXPLORE phase: Read all cycle skills, activity matrix, plan templates, type taxonomy
- [x] SPECIFY phase: Write this specification
- [x] CRITIQUE phase: Invoke critique-agent, apply revisions (A2/A3/A4/A6/A7/A8 addressed)

### Step 1b: Implement Programmatic Backup (code work)
- [ ] Add `CEREMONY_PROFILE_MAP` and `PHASE_CONFIG` to cycle_runner.py
- [ ] Add `get_ceremony_profile()` and `should_execute_gate()` functions
- [ ] Add tests for profile resolution and gate checking
- [ ] This is code work; should be a spawned WORK item

### Step 2: Update Implementation-Cycle SKILL.md
- [ ] Add "Ceremony Profile Quick Reference" section near top
- [ ] Add one-line profile annotations to each gate
- [ ] Reference `should_execute_gate()` as programmatic backup

### Step 3: Update Routing-Gate SKILL.md
- [ ] Add `type: design` handling to routing decision table
- [ ] Document that design uses implementation-cycle with profile adaptation

### Step 4: Update Plan-Validation-Cycle SKILL.md
- [ ] Add subtype-aware section validation documentation
- [ ] Reference WORK-152 `validate_template()` pattern

### Step 5: Update DoD-Validation-Cycle SKILL.md
- [ ] Add type-aware test criterion (pytest vs /validate vs epistemic)
- [ ] Type check reads directly from work item, no external profile lookup

### Step 6: Update References
- [ ] **MUST:** Update CLAUDE.md if behavior documented
- [ ] **MUST:** Update READMEs in affected directories
- [ ] Update activity_matrix.yaml phase_to_state if needed

---

## Verification

- [ ] Specification document exists and covers all 4 acceptance criteria
- [ ] Per-profile phase configuration table is complete
- [ ] Computable predicate extension design is documented
- [ ] WORK-152 and WORK-101 relationships are clarified
- [ ] **MUST:** All READMEs current
- [ ] Review complete (critique-agent)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Profile table becomes stale as cycle skills evolve | Medium | PHASE_CONFIG lives in SKILL.md (same file as phase definitions), so updates are co-located |
| SHOULD gates get skipped too aggressively | Medium | Governance event logging preserves audit trail; can tighten to MUST if patterns emerge |
| Type taxonomy continues to fragment (new types added) | Low | CEREMONY_PROFILE_MAP defaults to "implementation" for unmapped types (safe fallback) |
| This spec is design-only; implementation requires separate work items | Low | Steps 0-6 are scoped. Each can be a work item if needed (or batched per validated practice Memory: 84963) |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 390 | 2026-02-16 | - | CRITIQUE | EXPLORE complete, SPECIFY complete, critique-revise (8 findings, A2/A3/A4/A6/A7/A8 addressed) |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-155/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Design document: lifecycle adaptation by work type | [x] | This specification: 4 profiles, 9 design decisions, 12-gate configuration |
| Type-to-ceremony mapping: which phases/gates are mandatory/optional per type | [x] | Per-Profile Phase Configuration table (Section 2): 12 gates x 4 profiles |
| Computable predicate extension design (from retro-cycle Phase 0 to full cycle) | [x] | Profile Resolution (Section 3): get_ceremony_profile() + should_execute_gate() |
| Relationship to WORK-152 and WORK-101 clarified | [x] | Section 6: orthogonal dimensions (type vs effort). Open Questions Q4: template vs ceremony. |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `docs/work/active/WORK-155/plans/PLAN.md` | Specification complete, status: approved | [x] | 320+ lines, all sections populated |

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | Plan read and verified during COMPLETE phase |
| Any deviations from plan? | No | All 4 deliverables met per acceptance criteria |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Design artifact complete
- [x] **MUST:** All WORK.md deliverables verified complete
- [x] WHY captured (memory concepts 85737-85744)
- [x] **MUST:** READMEs updated in all modified directories (no directories modified — design-only work item)
- [x] Ground Truth Verification completed above

---

## References

- WORK-152: Plan Template Fracturing by Work Type (predecessor, closed S390)
- WORK-101: Proportional Governance Design (orthogonal, deferred E2.9)
- Memory: 85528-85541, 85558, 85578, 85605-85608 (S383 triage evidence)
- Memory: 85730-85735 (WORK-152 closure learnings)
- `.claude/skills/implementation-cycle/SKILL.md` (primary consumer)
- `.claude/skills/retro-cycle/SKILL.md` (Phase 0 prototype)
- `.claude/haios/config/activity_matrix.yaml` (governance state mapping)
- `.claude/haios/modules/cycle_runner.py` (CYCLE_PHASES, PAUSE_PHASES)
- `.claude/haios/lib/validate.py` (allowed_types, section registries)
- `.claude/haios/lib/scaffold.py` (PLAN_TYPE_MAP precedent)

---
