---
template: observations
work_id: INV-072
captured_session: '246'
generated: '2026-01-26'
last_updated: '2026-01-26T21:42:48'
---
# Observations: INV-072

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

**The collision was not a spawn function bug but an agent decision bug.** Initial hypothesis was that `just work` or `create_work()` had a bug in ID allocation. Investigation revealed that E2-XXX IDs are agent-specified, not auto-generated. The collision happened because Session 245 agent manually chose "E2-294" without checking if that ID existed as complete. The tooling gap is lack of validation, not lack of auto-generation. This reframes the fix from "fix ID allocation" to "add validation gate."

**Memory already documented this class of bug.** Concepts 77290 and 79940 both describe prior ID collision incidents (INV-011 in Session 101, INV-042 collision). This is a recurring pattern, not a one-off. The fact that we keep re-discovering it suggests either: (1) memory isn't being queried before spawning, or (2) the fix was never implemented from prior discoveries.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

**No `get_next_e2_id()` function exists.** `get_next_work_id()` in scaffold.py:153-174 only handles WORK-XXX format. E2-XXX and INV-XXX IDs are explicitly ignored ("Ignores legacy E2-XXX and INV-XXX directories"). This means agents must manually pick IDs for these formats with no tooling support. Either we need auto-generation for all formats, or we need a pre-check that validates the chosen ID is available.

**No "status-aware existence check" pattern.** The codebase has `_work_file_exists()` (scaffold.py:117-139) which checks file existence but not status. A reusable pattern like `is_id_available(id) -> bool` that checks both existence AND terminal status would prevent this class of bug across multiple entry points.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

**ADR-041 "status over location" is correct but creates preconditions for collision.** The policy of keeping completed items in active/ until epoch cleanup is sound (preserves references). However, combined with no creation-time validation, it enables this bug class. The fix is validation, not location change. This should be documented as a design rationale in E2-304.

**Survey-cycle detected the collision through PLAN/WORK mismatch.** The symptom that triggered investigation was PLAN.md content not matching WORK.md deliverables. This is a useful canary: when plan content doesn't match work item, check for ID collision. Could be automated as a validation hook.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

**WORK-XXX auto-generation vs E2-XXX manual specification is undocumented.** TRD-WORK-ITEM-UNIVERSAL established WORK-XXX as the universal format, but E2-XXX and INV-XXX are still in active use. The split behavior (auto vs manual ID generation) is implicit in code (scaffold.py:153-174 comment) but not documented anywhere agents can reference. This creates a knowledge gap where agents don't know they must manually check ID availability for legacy formats.
