---
template: observations
work_id: INV-065
captured_session: '194'
generated: '2026-01-16'
last_updated: '2026-01-16T20:47:35'
---
# Observations: INV-065

## What surprised you?

<!-- Unexpected behaviors, things easier/harder than expected -->

- [x] PostToolUse is fundamentally limited - Skills are markdown files, not hookable tool events. Hooks cannot distinguish "read skill file" from "read any file." This is a Claude Code platform constraint, not a HAIOS design flaw.

## What's missing?

<!-- Gaps, missing features, AgentUX friction -->

- [x] No `just new-investigation` recipe - noted in ARC-008 (JustfileAudit). Creates friction when trying to use consistent patterns.
- [x] No phase-aware skill invocation API - soft enforcement is the ceiling within Claude Code architecture.

## What should we remember?

<!-- Learnings, patterns, warnings -->

- [x] "Soft enforcement via skill prose is the ceiling" - hard enforcement requires Epoch 4 SDK migration (S25). Accept this constraint and optimize within it.
- [x] Design-implementation gap pattern: INV-062 designed cascade, E2-286/287/288 built schema/warning but NOT the write path. E2-292 completes the circuit. Always verify the full chain is wired.
