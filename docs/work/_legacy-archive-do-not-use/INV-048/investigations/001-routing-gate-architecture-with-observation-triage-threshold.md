---
template: investigation
status: active
date: 2025-12-28
backlog_id: INV-048
title: Routing Gate Architecture with Observation Triage Threshold
author: Hephaestus
session: 137
lifecycle_phase: conclude
spawned_by: null
related:
- E2-221
- E2-222
- E2-223
memory_refs:
- 79945
- 79946
- 79947
- 79948
- 79949
- 79950
- 79951
version: '2.0'
generated: 2025-12-22
last_updated: '2025-12-28T17:28:40'
---
# Investigation: Routing Gate Architecture with Observation Triage Threshold

@docs/README.md
@docs/epistemic_state.md

<!-- TEMPLATE GOVERNANCE (v2.0 - E2-144)

     INVESTIGATION CYCLE: HYPOTHESIZE -> EXPLORE -> CONCLUDE

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: Pure discovery, no design outputs needed"
     - "SKIPPED: Single hypothesis, no complex mapping required"
     - "SKIPPED: External research only, no codebase evidence"

     This prevents silent section deletion and ensures conscious decisions.

     SUBAGENT REQUIREMENT (L3):
     For EXPLORE phase, you MUST invoke investigation-agent subagent:
     Task(prompt='EXPLORE: {hypothesis}', subagent_type='investigation-agent')

     Rationale: Session 101 proved L2 ("RECOMMENDED") guidance is ignored ~20% of time.
     L3 enforcement ensures structured evidence gathering.
-->

---

## Context

<!-- HYPOTHESIZE PHASE: Describe background before exploring -->

**Trigger:** Session 136 epistemic discussion on observation feedback loop. After closing E2-217 (Observation Capture Gate), realized that observations accumulate with `triage_status: pending` but no gate forces triage.

**Problem Statement:** Routing logic is embedded in each cycle's CHAIN phase with no system health checks - observations could accumulate indefinitely (write-only), breaking the feedback loop silently.

**Prior Observations:**
- E2-217 implemented observation capture but no threshold enforcement
- Five cycle skills (implementation, investigation, work-creation, close-work, plan-authoring) all have CHAIN phases with identical routing tables
- Routing is purely work-type based (INV-* vs has-plan vs else) with no system state awareness
- observation-triage-cycle exists but is standalone - never forcibly invoked

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "routing gate architecture observation triage threshold skill extraction modular gates system health"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 78921 | Formalized "skill as node entry gate" pattern with Gate Contract specification (Entry + Guardrails + Exit) | Directly applicable - gate contract pattern for routing |
| 78924 | Formalizes the "skill as node entry gate" pattern from INV-033 | Prior art for gate extraction |
| 78876 | Skills should define entry/exit contracts, node-cycle integration, gate enforcement via events | Design guidance for routing-gate |
| 18835 | "Certainty Ratchet" - Each gate is checkpoint that validates before investing in next layer | Philosophical foundation |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] Found: INV-033 (Skill as Node Entry Gate) - foundational pattern
- [x] Found: INV-023 (ReasoningBank Feedback Loop) - same write-only problem
- [x] Found: INV-047 (Close Cycle Observation Phase Ordering) - observation timing

---

## Objective

<!-- One clear question this investigation will answer -->

**What is the optimal architecture for extracting routing logic into a modular routing-gate skill that can enforce system health thresholds (starting with observation triage) before routing to next work?**

---

## Scope

### In Scope
- Map current routing logic across all 5 cycle CHAIN phases
- Design routing-gate contract (inputs, outputs, threshold interface)
- Define threshold configuration mechanism (YAML vs haios-status)
- Prototype observation triage threshold as first implementation
- Identify enforcement point (skill entry vs CHAIN phase)
- Design escape hatch for urgent work

### Out of Scope
- Full implementation (this spawns E2-xxx items)
- Thresholds beyond observation triage (future pattern application)
- Integration with heartbeat or scheduled triggers
- Historical observation backfill

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | 6 | 5 cycle SKILL.md files + observation-triage-cycle |
| Hypotheses to test | 3 | Listed below |
| Expected evidence sources | 3 | Codebase (skills), Memory (prior work), External (none) |
| Estimated complexity | Medium | Architectural but scoped to single pattern |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | Routing logic in all CHAIN phases is nearly identical and can be extracted into a single routing-gate skill | High | Compare CHAIN phase routing tables across 5 cycle skills | 1st |
| **H2** | A threshold-based pre-routing check (e.g., pending observations > N) can be cleanly inserted before work-type routing | Med | Review skill entry patterns and existing gate mechanisms | 2nd |
| **H3** | The escape hatch for urgent work can use existing priority field (P0 = blocking) without new infrastructure | Med | Check WORK.md frontmatter schema and priority handling | 3rd |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [x] Query memory for INV-033 (skill as node entry gate) findings
2. [x] Read all 5 cycle SKILL.md CHAIN phases, extract routing tables
3. [x] Read observation-triage-cycle for integration points

### Phase 2: Hypothesis Testing
4. [x] Test H1: Diff routing tables across cycles - identify commonality vs divergence
5. [x] Test H2: Review existing gate patterns (dod-validation-cycle, plan-validation-cycle) for threshold insertion model
6. [x] Test H3: Check work_item template for priority field usage and P0 semantics

### Phase 3: Synthesis
7. [x] Design routing-gate contract (inputs/outputs/interface)
8. [x] Define threshold configuration schema
9. [x] Specify observation threshold implementation
10. [x] Document escape hatch mechanism
11. [x] Identify spawned implementation items

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| 3 skills share identical 4-signal routing table | `implementation-cycle/SKILL.md:218-224`, `investigation-cycle/SKILL.md:127-133`, `close-work-cycle/SKILL.md:184-190` | H1 | Word-for-word identical |
| work-creation-cycle uses 6-signal confidence-based routing | `work-creation-cycle/SKILL.md:106-113` | H1 | Different architecture |
| plan-authoring-cycle has fixed chain target | `plan-authoring-cycle/SKILL.md:115-119` | H1 | Always chains to plan-validation |
| dod-validation-cycle invoked as MUST gate before VALIDATE | `close-work-cycle/SKILL.md:35-38` | H2 | Bridge skill pattern |
| `scan_archived_observations()` returns pending items with counts | `observations.py:294-332` | H2 | Threshold function exists |
| Work item priority field allows critical/high/medium/low | `validate.py:127` | H3 | Schema exists |
| P0-P3 scale defined only for observations | `observations.py:227` | H3 | Different scale than work items |
| No code checks priority for routing bypass | Grep search (no matches) | H3 | New implementation needed |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 78921 | Skill as node entry gate pattern with Gate Contract (Entry + Guardrails + Exit) | H1, H2 | Foundational pattern for extraction |
| 78924 | Formalized gate pattern from INV-033 | H1, H2 | Prior art validation |
| 78876 | Skills should define entry/exit contracts, emit events | H2 | Design guidance |
| 18835 | Certainty Ratchet - gates validate before next layer | H2 | Philosophical foundation |

### External Evidence (if applicable)

**SKIPPED:** No external sources needed - all evidence from codebase and memory.

---

## Findings

<!-- EXPLORE PHASE: Document findings as discovered
     CONCLUDE PHASE: Synthesize into coherent narrative

     DoD: This section MUST have actual content, not placeholder text -->

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | **Partially Confirmed** | 3/5 skills share identical routing; 2 have divergent logic (work-creation = confidence-based, plan-authoring = fixed target) | High |
| H2 | **Confirmed** | Bridge skill pattern exists (dod-validation-cycle), `scan_archived_observations()` provides threshold function, natural insertion point in CHAIN phase | High |
| H3 | **Partially Confirmed** | Priority field exists with critical/high/medium/low values, but no code uses it for routing bypass - requires new implementation | Med |

### Detailed Findings

#### Finding 1: Three Skills Share Identical Routing Logic

**Evidence:**
```markdown
# Identical in implementation-cycle:218-224, investigation-cycle:127-133, close-work-cycle:184-190
| Signal | Action |
|--------|--------|
| No items returned | Report "No unblocked work. Awaiting operator direction." |
| ID starts with `INV-` | Invoke `Skill(skill="investigation-cycle")` |
| Work file has plan in `documents.plans` | Invoke `Skill(skill="implementation-cycle")` |
| Otherwise | Invoke `Skill(skill="work-creation-cycle")` to populate |
```

**Analysis:** Perfect duplication across 3 skills = clear extraction candidate. DRY principle violated.

**Implication:** Extract into `routing-gate` skill with standard 4-signal routing table.

#### Finding 2: Threshold Check Infrastructure Exists

**Evidence:**
```python
# observations.py:294-332
def scan_archived_observations(base_path: Optional[Path] = None) -> list[dict]:
    """Scan archived work items for untriaged observations."""
    # Returns list with work_id, path, observations for pending items
```

**Analysis:** Function already returns count of pending observations. Threshold check is `len(result) > N`.

**Implication:** No new infrastructure needed for observation threshold - just invoke function and compare.

#### Finding 3: Escape Hatch Requires New Logic

**Evidence:**
- `validate.py:127` allows priority: critical/high/medium/low
- Grep for priority routing: 0 matches
- `status.py:188-200` uses priority for reporting only

**Analysis:** Priority field exists but is never used for routing decisions. Semantic mapping critical=bypass is intuitive but not implemented.

**Implication:** Add single check: `if priority == "critical": bypass_threshold = True`

---

## Design Outputs

<!-- If investigation produces architectural designs, document them here
     SKIP this section if investigation is pure discovery with no design outputs -->

### Routing-Gate Skill Contract

```yaml
# routing-gate skill contract
name: routing-gate
type: bridge

# Inputs
inputs:
  current_work_id: string  # The work item just completed (for logging)
  next_work_id: string     # The work item to route to (from `just ready`)
  next_work_type: string   # INV-*, E2-*, etc.
  has_plan: boolean        # Whether next_work has documents.plans populated
  priority: string         # critical/high/medium/low (for escape hatch)

# Outputs
outputs:
  action: enum[invoke_investigation, invoke_implementation, invoke_work_creation, invoke_triage, await_operator]
  reason: string           # Why this action was chosen
  threshold_triggered: boolean  # Whether a threshold check caused diversion

# Threshold Configuration
thresholds:
  observation_pending_max: 10  # If pending observations > N, divert to triage
  # Future: memory_stale_max, plan_incomplete_max, etc.
```

### Threshold Configuration Schema

```yaml
# .claude/config/routing-thresholds.yaml
thresholds:
  observation_pending:
    enabled: true
    max_count: 10
    divert_to: observation-triage-cycle
    escape_priorities: [critical]  # Skip threshold for these priorities

  # Future extensibility
  # memory_stale:
  #   enabled: false
  #   max_days: 7
  #   divert_to: memory-cleanup-cycle
```

### Mechanism Design

```
TRIGGER: CHAIN phase invokes routing-gate before work-type routing

PRE-ROUTING CHECKS:
    1. Check escape hatch: if priority == "critical", skip all thresholds
    2. Check observation threshold:
       - pending = scan_archived_observations()
       - if len(pending) > threshold:
           - return {action: invoke_triage, threshold_triggered: true}
    3. [Future: additional threshold checks]

WORK-TYPE ROUTING (if no threshold triggered):
    4. if next_work_id starts with "INV-": return invoke_investigation
    5. if has_plan: return invoke_implementation
    6. if no next_work_id: return await_operator
    7. else: return invoke_work_creation

OUTCOME: Single action to invoke (skill or await)
```

### Skill Adoption Map

| Skill | Current CHAIN | After Routing-Gate |
|-------|---------------|-------------------|
| implementation-cycle | Inline routing table | `Skill(skill="routing-gate")` |
| investigation-cycle | Inline routing table | `Skill(skill="routing-gate")` |
| close-work-cycle | Inline routing table | `Skill(skill="routing-gate")` |
| work-creation-cycle | Confidence-based (6 signals) | Keep inline (different pattern) |
| plan-authoring-cycle | Fixed chain to plan-validation | Keep inline (trivial) |

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Extract routing for 3 skills only | Leave work-creation and plan-authoring inline | Confidence-based and fixed-target routing are fundamentally different patterns - extraction adds complexity without value |
| Threshold before work-type routing | Pre-routing check, not parallel check | Thresholds are "system health" gates, work-type routing is "what to do next" - logically sequential |
| Config in YAML file | Not in haios-status.json | Thresholds are operator-tunable policy, not runtime state |
| priority=critical as escape hatch | Not a new field | Reuses existing schema, semantic mapping is intuitive |
| Single threshold implementation first | Observation triage only | Pattern validation before expanding to other thresholds |

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Immediate (Can implement now)

- [x] **E2-221: Routing-Gate Skill Implementation**
  - Description: Create routing-gate skill with threshold check and work-type routing
  - Fixes: DRY violation in 3 skills, enables observation triage threshold
  - Spawned via: `/new-work E2-221 "Routing-Gate Skill Implementation"`

- [x] **E2-222: Routing Threshold Configuration**
  - Description: Create `.claude/config/routing-thresholds.yaml` with observation threshold
  - Fixes: No configurable thresholds exist
  - Spawned via: `/new-work E2-222 "Routing Threshold Configuration"`

- [x] **E2-223: Integrate Routing-Gate into Cycle Skills**
  - Description: Update implementation-cycle, investigation-cycle, close-work-cycle CHAIN phases to invoke routing-gate
  - Fixes: Routing logic duplication across 3 skills
  - Blocked by: E2-221
  - Spawned via: `/new-work E2-223 "Integrate Routing-Gate into Cycle Skills"`

### Future (Requires more work first)

- [ ] **Future: Additional Threshold Types**
  - Description: Add memory_stale, plan_incomplete, etc. thresholds
  - Blocked by: E2-221 (pattern validation first)
  - **Not spawned:** Wait for observation threshold to prove pattern

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 137 | 2025-12-28 | HYPOTHESIZE | Complete | Context, hypotheses, exploration plan |
| 137 | 2025-12-28 | EXPLORE | Complete | All 3 hypotheses tested via investigation-agent |
| 137 | 2025-12-28 | CONCLUDE | Complete | Design documented, spawned E2-221/222/223 |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-HN have verdict | [x] | H1: Partial, H2: Confirmed, H3: Partial |
| Evidence has sources | All findings have file:line or concept ID | [x] | 8 codebase, 4 memory evidence items |
| Spawned items created | Items exist in backlog or via /new-* | [x] | E2-221, E2-222, E2-223 created |
| Memory stored | ingester_ingest called, memory_refs populated | [x] | 79945-79951 |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | Yes | 3 invocations (H1, H2, H3) |
| Are all evidence sources cited with file:line or concept ID? | Yes | See Evidence Collection section |
| Were all hypotheses tested with documented verdicts? | Yes | See Hypothesis Verdicts table |
| Are spawned items created (not just listed)? | Yes | E2-221, E2-222, E2-223 in docs/work/active/ |
| Is memory_refs populated in frontmatter? | Yes | [79945-79951] |

---

## Closure Checklist

<!-- CONCLUDE PHASE: Complete ALL items before /close -->

### Required (MUST complete)
- [x] **Findings synthesized** - Answer to objective documented in Findings section
- [x] **Evidence sourced** - All findings have file:line or concept ID citations
- [x] **Hypotheses resolved** - All hypotheses have Confirmed/Refuted/Inconclusive verdict
- [x] **Spawned items created** - Via /new-* commands with `spawned_by` field (or rationale if none)
- [x] **Memory stored** - `ingester_ingest` called with findings summary
- [x] **memory_refs populated** - Frontmatter updated with concept IDs
- [x] **lifecycle_phase updated** - Set to `conclude`
- [x] **Ground Truth Verification complete** - All items checked above

### Optional
- [x] Design outputs documented (if applicable)
- [x] Session progress updated (if multi-session)

---

## References

- Spawned by: Session 136 epistemic discussion
- Related: E2-217 (Observation Capture Gate)
- Related: E2-218 (Observation Triage Cycle) - now observation-triage-cycle skill
- Related: INV-033 (Skill as Node Entry Gate) - foundational pattern
- Related: INV-023 (ReasoningBank Feedback Loop) - same write-only problem pattern
- Related: INV-047 (Close Cycle Observation Phase Ordering)
- Memory: 78921, 78924, 78876 (gate contract patterns)

---
