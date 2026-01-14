---
template: implementation_plan
status: approved
date: 2025-12-17
backlog_id: E2-096
title: "Cycle State Frontmatter"
author: Hephaestus
lifecycle_phase: plan
session: 85
spawned_by: Session-83
blocked_by: [E2-091]
related: [E2-076b, E2-091, E2-097, E2-106, ADR-038, epoch3/foresight-spec.md]
milestone: M3-Cycles
enables: [E2-097]
version: "1.3"
---
# generated: 2025-12-17
# System Auto: last updated on: 2025-12-19 21:31:28
# Implementation Plan: Cycle State Frontmatter

@docs/README.md
@docs/epistemic_state.md
@docs/ADR/ADR-038-m2-governance-symphony-architecture.md

---

## Goal

Plan files have a `cycle_phase` frontmatter field tracking their position in the PLAN-DO-CHECK-DONE cycle, enabling RHYTHM tracking (ADR-038) and unlocking E2-097 (Cycle Events Integration).

---

## Current State vs Desired State

### Current State

```yaml
# docs/plans/PLAN-E2-092-*.md frontmatter
---
template: implementation_plan
status: approved
lifecycle_phase: plan  # Static ADR-034 phase, not cycle phase
---
```

**Behavior:** Plans have `lifecycle_phase` (discovery/plan/implement/verify/complete) but no cycle state.

**Result:** Can't track where a work item is in PLAN-DO-CHECK-DONE without reading file content.

### Desired State

```yaml
# docs/plans/PLAN-E2-092-*.md frontmatter
---
template: implementation_plan
status: approved
lifecycle_phase: plan
cycle_phase: PLAN  # NEW: PLAN | DO | CHECK | DONE | null
---
```

**Behavior:** Plans explicitly track cycle position in frontmatter.

**Result:** UpdateHaiosStatus can aggregate cycle states, enable events, show progress.

### Enhanced State (E2-106: FORESIGHT Preparation)

```yaml
# docs/plans/PLAN-E2-092-*.md frontmatter - with optional foresight_prep
---
template: implementation_plan
status: approved
lifecycle_phase: plan
cycle_phase: DO
foresight_prep:  # OPTIONAL: Epoch 3 data generation
  # PLAN phase captures (set when entering PLAN/DO)
  predicted_outcome: "Test runner subagent executes tests and returns structured results"
  predicted_confidence: 0.75  # 0-1 scale
  knowledge_gaps: ["pytest fixture patterns", "mock injection"]
  skill_gaps: []
  competence_domain: "subagent_creation"
  # CHECK phase additions (filled during CHECK)
  actual_outcome: "Test runner works, fixture handling needed iteration"
  prediction_error: 0.2  # How wrong was prediction (0-1)
  competence_estimate: 0.7  # Self-assessed capability at this domain
  failure_modes_discovered: ["pytest collection phase complexity"]
---
```

**Behavior:** Cycles optionally capture prediction/calibration data for future FORESIGHT layer.

**Result:** When Epoch 3 arrives, we have rich seed data for:
- **World Model:** predicted_outcome vs actual_outcome calibration
- **Self Model:** competence_estimate by domain
- **Goal Network:** knowledge_gaps/skill_gaps as blocking_on precursors
- **Metamemory:** prediction confidence tracking

---

## Tests First (TDD)

### Test 1: Schema Includes cycle_phase
```yaml
# Verify template schema allows cycle_phase
# .claude/templates/implementation_plan.md should have cycle_phase field
```

### Test 2: ValidateTemplate Accepts cycle_phase
```bash
# After adding to template, validation should pass
/validate docs/plans/PLAN-E2-092-*.md
# Expected: Valid
```

### Test 3: UpdateHaiosStatus Parses cycle_phase
```powershell
# After enhancement, status should show cycle distribution
# haios-status.json should have lifecycle.counts_by_cycle_phase
```

---

## Detailed Design

### Schema Addition

Add to `.claude/templates/implementation_plan.md`:

```yaml
# After lifecycle_phase
cycle_phase: {{CYCLE_PHASE}}  # Optional: PLAN, DO, CHECK, DONE
```

Valid values:
- `PLAN` - Design phase, plan not yet implemented
- `DO` - Implementation in progress
- `CHECK` - Verification in progress
- `DONE` - Cycle complete (typically status: complete)
- `null`/omitted - Cycle not started or N/A

### State Transitions

```
status: draft     → cycle_phase: null (not in cycle)
status: approved  → cycle_phase: PLAN (ready to implement)
[implementation]  → cycle_phase: DO
[testing]         → cycle_phase: CHECK
status: complete  → cycle_phase: DONE
```

### UpdateHaiosStatus Enhancement

Add to Get-LiveFiles in `UpdateHaiosStatus.ps1`:

```powershell
# Parse cycle_phase from YAML
$cyclePhase = if ($yaml -match 'cycle_phase:\s*(\S+)') {
    $Matches[1].Trim()
} else {
    "untracked"
}

# Add to counts
$cyclePhaseCounts = @{
    PLAN = 0
    DO = 0
    CHECK = 0
    DONE = 0
    untracked = 0
}
```

### Symphony Integration (ADR-038)

| Movement | Integration |
|----------|-------------|
| **RHYTHM** | haios-status.json shows cycle_phase distribution |
| **DYNAMICS** | Could add "STUCK" threshold if DO > 3 items |
| **RESONANCE** | E2-097 uses cycle_phase transitions as events |

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Field name | `cycle_phase` | Distinct from `lifecycle_phase` (ADR-034) |
| Values | PLAN/DO/CHECK/DONE | Match implementation-cycle skill phases |
| Optional field | Yes | Backward compatible, not all items need cycles |
| Case | UPPERCASE | Visually distinct, matches skill documentation |

### Input/Output Examples

| Plan Status | cycle_phase | Notes |
|-------------|-------------|-------|
| draft | null | Not ready for cycle |
| approved | PLAN | Ready, awaiting implementation |
| approved | DO | Implementation started |
| approved | CHECK | Tests running |
| complete | DONE | Cycle complete |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Old plans without field | Treat as "untracked" | Test 3 |
| Invalid value | Treat as "untracked", log warning | Manual |
| Investigations | cycle_phase: null (no cycle) | N/A |

---

## Implementation Steps

### Step 1: Update Template Schema
- [ ] Add `cycle_phase` field to `.claude/templates/implementation_plan.md`
- [ ] Document allowed values in template comments

### Step 2: Update ValidateTemplate
- [ ] Add cycle_phase to valid fields in `ValidateTemplate.ps1`
- [ ] Add value validation (PLAN|DO|CHECK|DONE or null)

### Step 3: Update UpdateHaiosStatus
- [ ] Parse cycle_phase in Get-LiveFiles function
- [ ] Add counts_by_cycle_phase to lifecycle section
- [ ] Include in slim status output

### Step 4: Update Existing Plans
- [ ] Add cycle_phase to E2-092 through E2-097 plans
- [ ] Set appropriate phase based on current status

### Step 5: FORESIGHT Preparation (E2-106)
- [ ] Add optional `foresight_prep` section to template schema
- [ ] ValidateTemplate accepts foresight_prep as optional nested object
- [ ] Document foresight_prep fields (predicted_outcome, predicted_confidence, knowledge_gaps, skill_gaps, competence_domain, actual_outcome, prediction_error, competence_estimate, failure_modes_discovered)
- [ ] Note: Not parsed by UpdateHaiosStatus yet - data collection for Epoch 3

---

## Verification

- [ ] Template includes cycle_phase field
- [ ] ValidateTemplate accepts the field
- [ ] UpdateHaiosStatus parses and counts cycle phases
- [ ] haios-status.json shows cycle distribution

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing validation | Medium | Make field optional |
| Manual phase updates | Low | /implement command could auto-update |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 85 | 2025-12-18 | - | Plan filled | Design complete |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/templates/implementation_plan.md` | Has cycle_phase field | [ ] | |
| `.claude/hooks/ValidateTemplate.ps1` | Accepts cycle_phase | [ ] | |
| `.claude/hooks/UpdateHaiosStatus.ps1` | Parses cycle_phase | [ ] | |
| `haios-status.json` | Shows counts_by_cycle_phase | [ ] | |

**Verification Commands:**
```bash
# Validate a plan with cycle_phase
/validate docs/plans/PLAN-E2-092-*.md

# Check status output
just update-status
# Look for counts_by_cycle_phase in output
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| cycle_phase appears in status? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass (validation, parsing)
- [ ] WHY captured (reasoning stored to memory)
- [ ] Documentation current
- [ ] Ground Truth Verification completed above

---

## References

- E2-091: Implementation Cycle Skill (defines PLAN-DO-CHECK-DONE)
- E2-097: Cycle Events Integration (depends on this)
- ADR-034: Document Ontology (lifecycle_phase)
- ADR-038: M2-Governance Symphony (RHYTHM movement)

---
