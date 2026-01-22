---
template: observations
work_id: WORK-009
captured_session: '228'
generated: '2026-01-22'
last_updated: '2026-01-22T22:33:02'
---
# Observations: WORK-009

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

- [x] Windows Unicode encoding issue on stdout more pervasive than expected. Identity loader produces Unicode arrows (→) that cp1252 can't handle. Had to wrap stdout with UTF-8 TextIOWrapper in cli.py. Cross-cutting concern for any recipe outputting structured content.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

- [x] coldstart.md Steps 3-10 still make Read calls for epoch context, checkpoint manifest, principles, memory, CLAUDE.md. Identity phase now injected but other phases still use manual file reads. Needs CH-005 (Session Loader) and CH-006 (Work Loader).

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

- [x] Content injection pattern works: recipe outputs content → agent sees it in context → no Read calls needed
- [x] justfile → cli.py → modules is the correct stack for all context loading
- [x] UTF-8 stdout wrapper is needed on Windows for any output containing Unicode
- [x] capsys fixture doesn't work with stdout wrappers - test return codes instead of captured output

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

- [x] None significant. Implementation aligned well with CH-007 spec for identity phase scope. Spec allows incremental implementation (R1-R4 not all required at once).
