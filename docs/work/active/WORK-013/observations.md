---
template: observations
work_id: WORK-013
captured_session: '238'
generated: '2026-01-25'
last_updated: '2026-01-25T20:11:18'
---
# Observations: WORK-013

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

- [x] **Spawn logic is already correct.** Expected H2 (spawn generates legacy prefixes) to be major issue, but `scaffold.py:154-174` already exclusively generates WORK-XXX IDs. Problem is purely routing, not spawning.
- [x] **Scope narrower than expected.** 12 files sounds large, but 8 are prose skill/command files (text edits) and only 4 are Python modules requiring code changes.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

- [x] **Type field fallback not documented.** WorkEngine falls back to inferring type from prefix when `type` field missing, but this isn't in TRD-WORK-ITEM-UNIVERSAL. Future maintainers won't know legacy items still route correctly.
- [x] **No prefix-to-type validation.** When legacy items have both prefix AND type field, no check for consistency (e.g., `id: INV-017` should have `type: investigation`).

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

- [x] **"Hypothesis + Evidence Table" pattern.** Structuring H1/H2/H3 with expected outcomes, then populating findings as table, made audit systematic.
- [x] **Module-first principle applied.** Used investigation-agent subagent rather than manual grep/glob chains.
- [x] **TRD is source of truth.** Lines 209-213 of TRD-WORK-ITEM-UNIVERSAL specify "let legacy age out" - just follow the spec.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

- [x] **Skill routing tables duplicate code logic in prose.** Six skill files have routing logic in markdown ("If ID starts with INV-*..."). Changes require editing multiple prose files rather than one code path in `routing.py`.
