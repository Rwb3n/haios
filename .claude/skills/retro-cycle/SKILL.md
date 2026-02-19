---
name: retro-cycle
type: ceremony
description: "Multi-step autonomous reflection with typed provenance for work closure.
  Replaces observation-capture-cycle with structured pipeline: REFLECT->DERIVE->EXTRACT->COMMIT."
category:
  - memory
  - closure
input_contract:
  - field: work_id
    type: string
    required: true
    description: "Work item ID being closed"
    pattern: "WORK-\\d{3}"
  - field: skip_retro
    type: boolean
    required: false
    description: "Escape hatch - skip retro with governance event logging"
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: "Whether retro-cycle completed successfully"
  - field: reflect_findings
    type: list
    guaranteed: on_success
    description: "Evidence-anchored observations from 4 REFLECT dimensions"
  - field: kss_directives
    type: object
    guaranteed: on_success
    description: "Keep/Stop/Start directives derived from REFLECT"
  - field: extracted_items
    type: list
    guaranteed: on_success
    description: "Bug/feature items with confidence tags"
  - field: memory_concept_ids
    type: list
    guaranteed: on_success
    description: "Concept IDs from all COMMIT stores"
  - field: dod_relevant_findings
    type: list
    guaranteed: on_success
    description: "Findings tagged dod-relevant that should flow to VALIDATE"
  - field: scaling
    type: string
    guaranteed: on_success
    description: "trivial or substantial - result of scale assessment"
  - field: error
    type: string
    guaranteed: on_failure
    description: "Error description"
side_effects:
  - "Store reflections to memory (retro-reflect provenance)"
  - "Store K/S/S directives to memory (retro-kss provenance)"
  - "Store bug/feature extractions to memory (retro-extract provenance)"
  - "Store closure summary to memory (absorbs close-work-cycle MEMORY phase)"
  - "Log ceremony event to governance-events.jsonl"
generated: 2026-02-13
last_updated: 2026-02-13T19:30:00
---
# Retro-Cycle

Multi-step autonomous reflection with typed provenance for work closure. Replaces observation-capture-cycle (WORK-142).

## When to Use

**Invoked automatically** by `/close` command before close-work-cycle.
**Manual invocation:** `Skill(skill="retro-cycle")` when capturing structured reflection for a work item.

---

## The Cycle

```
/close {work_id}
  |
  +-> retro-cycle
  |     |
  |     +-> Phase 0: SCALE ASSESSMENT (computable predicate)
  |     |     trivial? -> single-pass retro
  |     |     substantial? -> full 4-phase pipeline
  |     |     --skip-retro? -> governance event, return early
  |     |
  |     +-> Phase 1: REFLECT (WCBB, WSY, WDN, WMI)
  |     |     Evidence-anchored observations
  |     |     DoD-relevant findings tagged
  |     |
  |     +-> Phase 2: DERIVE (Keep / Stop / Start)
  |     |     Proportional to scale assessment
  |     |
  |     +-> Phase 3: EXTRACT (Bugs + Features)
  |     |     Confidence-tagged, NO auto-spawn
  |     |
  |     +-> Phase 4: COMMIT (All to memory)
  |           Typed provenance: retro-reflect, retro-kss, retro-extract
  |           Also stores closure summary (absorbs MEMORY phase)
  |
  +-> close-work-cycle
        VALIDATE -> ARCHIVE -> CHAIN
```

---

## Why 4 Phases? (S20 Pressure Dynamics)

Each phase operates under different cognitive pressure:

| Phase | Pressure | Function |
|-------|----------|----------|
| REFLECT | Observation (what happened?) | Data gathering with evidence anchoring |
| DERIVE | Synthesis (what to do about it?) | Pattern extraction from observations |
| EXTRACT | Classification (what type of action?) | Bug vs feature vs behavioral |
| COMMIT | Persistence (store with provenance) | Memory writes with typed tags |

Collapsing phases conflates observation with action, losing the signal quality that typed provenance enables. Each phase has a distinct input/output contract and can degrade independently.

---

## Phase 0: Scale Assessment

**Computable predicate** — call `assess_scale(work_id)` from `.claude/haios/lib/retro_scale.py`:

```python
from retro_scale import assess_scale
scaling = assess_scale(work_id)  # Returns "trivial" or "substantial"
```

The function checks 4 machine-checkable conditions (files_changed <= 2, no plan exists, no test files changed, no CyclePhaseEntered governance events). See `retro_scale.py` for details. Defaults to "substantial" on any error (fail-safe).

### Escape Hatch: --skip-retro

If `skip_retro` is set:
1. Log governance event: `RetroCycleSkipped` with work_id and rationale
2. Return early with `success: true`, empty findings lists, `scaling: "skipped"`

**RETRO never blocks closure.** Even if evidence is unavailable, phases degrade gracefully (see per-phase degradation below).

---

## Phase 1: REFLECT

Capture observations across 4 dimensions, anchored to specific evidence.

### Dimensions

| Dimension | Code | What It Captures | Orientation |
|-----------|------|-----------------|-------------|
| What could've been better? | WCBB | Quality gaps, process friction | Evaluative (negative) |
| What surprised you? | WSY | Unexpected behaviors, wrong assumptions | Epistemic |
| What drift did you notice? | WDN | Reality vs docs, code vs spec | Systemic |
| What's missing? | WMI | Tooling gaps, architectural gaps | Prescriptive |

### Evidence Sources

Read these artifacts to ground observations:

1. **Work item:** `docs/work/active/{work_id}/WORK.md` (context, deliverables, acceptance criteria)
2. **Plan:** `docs/work/active/{work_id}/plans/PLAN.md` (design decisions, predicted outcomes)
3. **Tests:** Changed test files (what was verified, what wasn't)
4. **Diff:** `git diff` for the work scope (actual code changes)
5. **Governance events:** `grep "{work_id}" .claude/haios/governance-events.jsonl` (cycle transitions, gate outcomes)

### Evidence Anchoring Rule (MUST)

Every REFLECT observation **MUST** include at least one of:
- File path (e.g., `.claude/skills/foo/SKILL.md`)
- Diff hunk reference (e.g., "lines 42-55 of bar.py")
- Governance event ID (e.g., "CycleTransition event at 2026-02-12T...")
- Test name (e.g., `test_foo_handles_edge_case`)

Generic statements without evidence anchors are logged as "unanchored" (warning, not blocking). They are still stored but tagged `evidence: none` in provenance.

### DoD-Relevant Severity Tag

If any REFLECT observation identifies something that should block closure:
- Tag it with `severity: dod-relevant`
- Include in `dod_relevant_findings` output field
- This flows to close-work-cycle's VALIDATE phase as input

### Proportional Scaling

| Scale | REFLECT Behavior |
|-------|-----------------|
| Trivial | Single pass: answer all 4 dimensions briefly (1-2 sentences each) |
| Substantial | Full analysis: per-dimension deep dive with multiple observations |

### Degradation

If evidence sources are unavailable (e.g., no plan, no governance events):
- Skip those sources
- Log which sources were unavailable
- REFLECT proceeds with available evidence
- Never blocks

---

## Phase 2: DERIVE

Extract Keep/Stop/Start directives from REFLECT observations.

### K/S/S Framework

| Category | Question | Example |
|----------|----------|---------|
| **Keep** | What worked well and should continue? | "Keep: TDD RED-GREEN pattern (test_retro_cycle.py:all 9 passed first run)" |
| **Stop** | What should we stop doing? | "Stop: Hardcoding epoch versions in test assertions (test_decision_traceability.py:156)" |
| **Start** | What should we start doing? | "Start: Computable predicates for ceremony scaling (retro-cycle Phase 0)" |

### Traceability

Each K/S/S directive **MUST** trace to at least one REFLECT observation. Directives without a source observation are filtered.

### Proportional Scaling

| Scale | DERIVE Behavior |
|-------|----------------|
| Trivial | Max 1 directive per category (3 total max) |
| Substantial | Uncapped |

### Degradation

If REFLECT produced zero observations (edge case), DERIVE is skipped. Log: "No observations to derive from."

---

## Phase 3: EXTRACT

Classify actionable items from REFLECT observations into bugs and features.

### Classification

| Type | Criteria | Confidence Levels |
|------|----------|------------------|
| **Bug** | Something broken, wrong, or inconsistent | high / medium / low |
| **Feature** | Something missing that would improve the system | high / medium / low |

### Output Format

For each extracted item:
```yaml
- type: bug|feature
  title: "Brief description"
  evidence: "File path, test name, or diff reference"
  confidence: high|medium|low
  severity: dod-relevant|high|medium|low  # bugs only
  source_dimension: WCBB|WSY|WDN|WMI
```

### No Auto-Spawn (REQ-LIFECYCLE-004)

Extracted bugs and features are stored to memory only. They are NOT automatically converted to work items. Surfacing happens at the downstream triage ceremony (WORK-143).

**Rationale:** Chaining is caller choice. The agent producing observations is not the right agent to decide whether they warrant new work items. Frequency across sessions is a stronger signal than single-session confidence.

### Proportional Scaling

| Scale | EXTRACT Behavior |
|-------|-----------------|
| Trivial | Max 2 items total |
| Substantial | Uncapped |

### Degradation

If REFLECT produced no actionable items, EXTRACT produces an empty list. This is a valid outcome, not an error.

---

## Phase 4: COMMIT

Store all outputs to memory with typed provenance tags. No deduplication at write time.

### Provenance Tags

| Tag | Source Path Pattern | Content | Type Hint |
|-----|-------------------|---------|-----------|
| retro-reflect | `retro-reflect:{work_id}` | Raw 4-dimensional observations with evidence anchors | techne |
| retro-kss | `retro-kss:{work_id}` | Keep/Stop/Start directives with traceability | techne |
| retro-extract | `retro-extract:{work_id}` | Bug/feature items with confidence and severity | techne |

### Storage Implementation

**MUST: Full Detail Preservation (S399 Operator Directive)**

Each ingester_ingest call **MUST** preserve the full detail from the phase output. The content field is NOT a summary — it is the complete structured output. Downstream consumers (triage, future agents) must be able to act on stored data without re-deriving it from source artifacts.

**retro-reflect content MUST include for each observation:**
- Observation ID (e.g., WCBB-1, WSY-2)
- Severity tag (if assigned)
- Full description (not abbreviated)
- Evidence anchor: exact file path with line numbers, exact diff reference, exact governance event, or exact test name
- Impact statement

**retro-kss content MUST include for each directive:**
- K/S/S category and ID (e.g., K1, S2, S3)
- Full directive text (not abbreviated)
- Traceability: which REFLECT observation(s) it traces to (by ID)
- For START directives: target file path and implementation sketch
- For STOP directives: evidence of the anti-pattern with file path

**retro-extract content MUST include for each item:**
- Type (bug/feature)
- Title
- File path(s) affected
- Reproduction steps (bugs) or implementation scope (features)
- Confidence level with rationale
- Severity level (bugs)
- Source dimension (WCBB/WSY/WDN/WMI)

**Anti-pattern (S399):** Storing compressed summaries like "STOP: Don't use EnterPlanMode" loses the evidence anchors, file paths, and traceability that make the observation actionable. A future agent reading this cannot determine WHERE the hook should be added, WHAT the redirect message should say, or WHY the pattern is wrong. Full detail is the minimum viable signal.

For each provenance type:
```
ingester_ingest(
  content="<FULL structured output from phase — see detail requirements above>",
  source_path="retro-reflect:{work_id}",  # or retro-kss, retro-extract
  content_type_hint="techne"
)
```

### Closure Summary (Absorbs MEMORY Phase)

In addition to the 3 typed stores, COMMIT also stores a closure summary:
```
ingester_ingest(
  content="Closure: {work_id} - {title}\nScale: {trivial|substantial}\nReflections: {count}\nK/S/S: {count}\nExtractions: {count}\nDoD-relevant: {count}",
  source_path="closure:{work_id}",
  content_type_hint="techne"
)
```

This absorbs the responsibility previously held by close-work-cycle's MEMORY phase.

### No Deduplication at Write Time

Agents are stateless across sessions. If independent sessions converge on the same observation, frequency IS the signal. Deduplication happens at read time during the triage ceremony (WORK-143).

### Governance Event

Log ceremony completion:
```
RetroCycleCompleted: {work_id}, scaling: {trivial|substantial}, reflect_count: N, kss_count: N, extract_count: N
```

### Degradation

If memory storage fails for any provenance type:
- Log the failure
- Continue with remaining stores
- Include failed store in error output
- Never blocks closure

---

## Escape Hatches

| Escape | Trigger | Behavior |
|--------|---------|----------|
| `--skip-retro` | Operator passes `skip_retro: true` | Log `RetroCycleSkipped` event, return early |
| Evidence unavailable | Source files missing or unreadable | Skip unavailable sources, proceed with available |
| Empty REFLECT | No observations surfaced | Skip DERIVE and EXTRACT, COMMIT stores empty summary |
| Memory failure | `ingester_ingest` returns error | Log error, continue with remaining stores |
| Phase timeout | Agent context approaching limits | Complete current phase, skip remaining, COMMIT what we have |

**Principle:** RETRO never blocks closure. Every sub-phase degrades gracefully.

---

## Consumer Migration Table

| Responsibility | From | To |
|----------------|------|-----|
| 4 reflection questions | observation-capture-cycle | retro-cycle REFLECT (evidence-anchored WCBB/WSY/WDN/WMI) |
| Memory storage of observations | observation-capture-cycle (ingester_ingest, doxa) | retro-cycle COMMIT (typed provenance: retro-reflect, retro-kss, retro-extract) |
| Closure summary storage | close-work-cycle MEMORY phase | retro-cycle COMMIT phase |
| Governance event check | close-work-cycle MEMORY phase | close-work-cycle VALIDATE phase |

---

## Composition Map

| Phase | Primary Tool | Memory Integration | Output |
|-------|--------------|-------------------|--------|
| Phase 0: Scale | Glob, Grep, Bash(git diff) | - | scaling: trivial\|substantial |
| Phase 1: REFLECT | Read (work, plan, tests, diff, events) | - | reflect_findings list |
| Phase 2: DERIVE | (synthesis from REFLECT output) | - | kss_directives object |
| Phase 3: EXTRACT | (classification from REFLECT output) | - | extracted_items list |
| Phase 4: COMMIT | ingester_ingest | 3 typed stores + closure summary | memory_concept_ids list |

---

## Quick Reference

| Phase | Question to Ask | If NO |
|-------|-----------------|-------|
| Phase 0 | Is skip_retro set? | Continue to scale assessment |
| Phase 0 | Is work trivial? | Full substantial pipeline |
| Phase 1 | Are evidence sources available? | Degrade: skip missing sources |
| Phase 1 | Are observations evidence-anchored? | Warn: tag as unanchored |
| Phase 1 | Any DoD-relevant findings? | Tag and include in dod_relevant_findings |
| Phase 2 | Do observations exist to derive from? | Skip DERIVE |
| Phase 2 | Do directives trace to observations? | Filter untraceable directives |
| Phase 3 | Are there actionable items? | Empty list (valid outcome) |
| Phase 4 | Did memory stores succeed? | Log failure, continue |

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| RETRO before VALIDATE | Reordered from post-archive | INV-059: completion mode bias. Reflecting before confirming DoD preserves cognitive separation |
| No auto-spawn | Bugs/features to memory only | REQ-LIFECYCLE-004: chaining is caller choice. Surfaced at triage |
| No dedup at write time | Frequency IS signal | Agents are stateless across sessions. Independent convergence = stronger signal |
| Evidence anchoring | MUST reference artifact | Generic statements without evidence get lost. Evidence enables downstream triage |
| 4 phases not 1 | REFLECT/DERIVE/EXTRACT/COMMIT | Observation != synthesis != classification != persistence |
| Proportional scaling | Computable predicate | files_changed, plan, tests, CyclePhaseEntered -- all machine-checkable |
| Absorb MEMORY phase | Closure summary in COMMIT | Reduces ceremony overhead. Single pass for all memory stores |
| deprecated: true not stub: true | observation-capture-cycle kept valid | stub: true breaks test_existing_skills_not_marked_stub |

---

## Related

- **observation-capture-cycle:** DEPRECATED, replaced by this skill (WORK-142)
- **close-work-cycle:** Predecessor relationship -- /close invokes retro-cycle then close-work-cycle
- **observation-triage-cycle:** Downstream consumer, reads retro-* provenance tags (WORK-143)
- **/close command:** Invokes this skill before close-work-cycle
- **dod-validation-cycle:** Invoked by close-work-cycle VALIDATE phase (unchanged)
- **INV-059:** Completion mode bias finding (cognitive separation rationale)
- **REQ-CEREMONY-001, REQ-CEREMONY-002:** Ceremony contract requirements
- **REQ-LIFECYCLE-004:** Chaining is caller choice (no auto-spawn)
- **WORK-143:** Companion -- triage consumer update for retro-* provenance tags
