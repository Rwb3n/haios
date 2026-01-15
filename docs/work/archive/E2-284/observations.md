---
template: observations
work_id: E2-284
captured_session: '187'
generated: '2026-01-10'
last_updated: '2026-01-10T16:58:25'
---
# Observations: E2-284

## What surprised you?

<!-- Unexpected behaviors, things easier/harder than expected -->

- The simplification was straightforward - No resistance from the codebase. The old 3-phase structure had no runtime dependencies beyond the skill file itself. Replacing 134 lines with 41 lines was a clean swap.
- Existing tests caught the right signals - The old tests verified phase names (RECALL, NOTICE, COMMIT). The new tests verify structure (questions, line count, gate). The inversion worked well.

## What's missing?

<!-- Gaps, missing features, AgentUX friction -->

- No automated gate enforcement - The skill says "Empty responses BLOCK closure" but there's no hook or validation that actually enforces this. The gate is documentation, not code.
- close.md line 273 still references old flow "(RECALL->NOTICE->COMMIT)" - stale documentation since phases are removed.

## What should we remember?

<!-- Learnings, patterns, warnings -->

- S20 line 98 was literal guidance - "3 questions, hard gate" wasn't a metaphor. Building exactly what the spec says prevents drift.
- Phases add procedural overhead - Agent pattern-matches through phases without thinking differently. Questions force the same reflection with less ceremony.
- Template simplification compounds - 105→26 lines means less scrolling, faster comprehension, lower token cost.
