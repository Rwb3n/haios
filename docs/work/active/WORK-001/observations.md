---
template: observations
work_id: WORK-001
captured_session: '210'
generated: '2026-01-19'
last_updated: '2026-01-19T16:44:41'
---
# Observations: WORK-001

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

- [x] **3-file threshold friction:** Preflight blocked for 4 tightly-coupled files (template, parser, validation, scaffold). Operator noted "occurring more often as the project progresses" - systemic signal that governance may need to evolve from raw count to risk-based model.
- [x] **Backward compat was clean:** The `type` fallback to `category` worked without issues. Legacy E2-XXX items parse correctly with no migration needed.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

- [x] **Coordinated change model:** No way to express "these files MUST change together" to preflight. Risk assessment per-file or file groupings would be more nuanced than raw count.
- [x] **Template substitution gap:** `{{TYPE}}` placeholder exists but scaffold doesn't substitute it for new work items. Gap for `/new-work` command.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

- [x] **Universal refactor pattern:** (1) Add new fields with sensible defaults, (2) Create fallback parsing (new -> legacy -> default), (3) Keep legacy fields as optional in validation, (4) Test both new and legacy data structures.
- [x] **Incremental commits for multi-file changes:** When scope exceeds threshold but changes are related, commit after each logical unit to reduce risk while preserving context.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

- [x] **get_queue() FIFO ordering:** Already captured (obs-209-001). Queue shows wrong order despite YAML saying WORK-001 first.
- [x] **Test assumptions outdated:** TestWorkItemTemplate expected operator_decisions from E2-272 but WORK-001 universal structure superseded it. Tests updated to check universal fields.
