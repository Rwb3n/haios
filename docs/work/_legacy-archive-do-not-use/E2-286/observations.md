---
template: observations
work_id: E2-286
captured_session: '190'
generated: '2026-01-14'
last_updated: '2026-01-14T21:36:48'
---
# Observations: E2-286

## What surprised you?

<!-- Unexpected behaviors, things easier/harder than expected -->

- Implementation was simpler than anticipated - plan specified exact code location (lines 935-957) and TDD approach worked cleanly
- One existing test (`test_output_matches_existing_slim_format`) failed after code change because it compares against on-disk JSON - required `just update-status-slim` to sync (expected for additive schema changes)

## What's missing?

<!-- Gaps, missing features, AgentUX friction -->

- Memory ingestion API key expired (Gemini) - didn't block work but learnings stored in plan instead of memory
- No automated "schema change" test pattern - comparison test could be more flexible (check structure, not exact keys)

## What should we remember?

<!-- Learnings, patterns, warnings -->

- TDD for schema changes works well: write failing tests, add field, tests pass
- Additive changes are low-risk: no existing fields touched, regression test verified
- Downstream consumers: E2-287 (warning) and E2-288 (set-cycle) complete the soft enforcement chain
