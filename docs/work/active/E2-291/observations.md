---
template: observations
work_id: E2-291
captured_session: '193'
generated: '2026-01-15'
last_updated: '2026-01-15T23:09:12'
---
# Observations: E2-291

## What surprised you?

<!-- Unexpected behaviors, things easier/harder than expected -->

- [x] Infrastructure already existed - `just queue` and `just queue-check` recipes were already created in E2-290. Added `is-cycle-allowed` as canonical recipe per plan spec (returns ALLOWED/BLOCKED).

## What's missing?

<!-- Gaps, missing features, AgentUX friction -->

- [x] No queue context propagation - survey-cycle picks a queue but no mechanism to pass queue name to routing-gate. Future: add queue context to session_state.

## What should we remember?

<!-- Learnings, patterns, warnings -->

- [x] Consumer wiring pattern: When building infrastructure, trace the call chain in the same session to identify all consumers. E2-290 built methods but left survey-cycle and routing-gate unwired - that's why E2-291 exists.
