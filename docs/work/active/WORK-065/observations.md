---
template: observations
work_id: WORK-065
captured_session: '276'
generated: '2026-02-01'
last_updated: '2026-02-01T20:21:54'
---
# Observations: WORK-065

## What surprised you?

**The scale of the vocabulary conflict.** I expected some inconsistency between `current_node` values in TRD vs GovernanceLayer, but found THREE completely different sets of allowed values:
- TRD-WORK-ITEM-UNIVERSAL (docs/specs/TRD-WORK-ITEM-UNIVERSAL.md:110): `backlog|planning|in_progress|review|complete`
- GovernanceLayer.VALID_TRANSITIONS (.claude/haios/modules/governance_layer.py:61-68): `backlog|discovery|plan|implement|close|complete`
- L5-execution.md manifesto (.claude/haios/manifesto/L5-execution.md:76): `backlog → ready → in_progress → blocked → complete`

**The empirical scan was damning.** 121 out of 128 work items (94%) have `current_node: backlog` regardless of actual status. This proves the field is completely unused in practice - obs-230-001 wasn't an isolated incident but systemic.

## What's missing?

**No enforcement mechanism for single-item focus.** The "1 in_progress per agent instance" constraint mentioned in WORK-065 context does not exist in code. WorkEngine.get_ready() returns ALL unblocked items (.claude/haios/modules/work_engine.py:325-349), and survey-cycle allows any selection. There's no gate preventing context-switching.

**No clear mapping between queue position and cycle phase.** The two concepts are conflated in `current_node`, but they're orthogonal: queue position answers "WHICH item am I working on?" while cycle phase answers "WHAT phase of work am I in?" E2.4 activity states (activity_matrix.yaml) only address the latter.

## What should we remember?

**The four-dimensional model.** Work item state has four orthogonal dimensions:
1. `status` - Is this item alive? (ADR-041 authoritative)
2. `queue_position` (PROPOSED) - Which item am I working on?
3. `cycle_phase` (rename from current_node) - Where in the cycle?
4. `activity_state` (E2.4) - What activities allowed?

Conflating any two causes semantic confusion. This is the key architectural finding.

**CH-006 and WORK-016 already exist.** This investigation (WORK-065) overlaps with existing workuniversal arc work (.claude/haios/epochs/E2_3/arcs/workuniversal/CH-006-node-transitions.md). Findings should merge into those items rather than spawning new work.

## What drift did you notice?

**L5-execution.md is outdated.** It describes a work DAG with values (`ready`, `blocked`) that don't exist in either TRD or GovernanceLayer. The manifesto hasn't been updated since governance was implemented.

**TRD-WORK-ITEM-UNIVERSAL doesn't match GovernanceLayer.** The TRD was "approved Session 218" but GovernanceLayer uses completely different `current_node` values. Either the TRD wasn't implemented as specified, or the implementation evolved past the spec without updating the spec.
