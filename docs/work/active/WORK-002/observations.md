---
template: observations
work_id: WORK-002
captured_session: '208'
generated: '2026-01-18'
last_updated: '2026-01-18T22:03:28'
---
# Observations: WORK-002

## What surprised you?

<!-- Unexpected behaviors, things easier/harder than expected -->

- [x] Queue filter gap: WorkEngine.get_ready() only filtered `status != "complete"`, not other terminal states (archived, dismissed). Revealed "query by tag" principle wasn't fully implemented.
- [x] Operator insight depth: Questions about epoch field and query-by-tag surfaced architectural thinking beyond immediate task - design pattern for WORK-001.

## What's missing?

<!-- Gaps, missing features, AgentUX friction -->

- [x] Epoch field: Work items lack explicit `epoch:` field. Currently inferred from ID prefix. Needs `epoch: E2.3` for portability. Captured for WORK-001.
- [x] Migration period concept: ADR-041 addresses work item closure, not epoch transitions. Need explicit "migration period" pattern.
- [x] Batch status tooling: Updated 43 items via script. Could use `just batch-status` recipe.

## What should we remember?

<!-- Learnings, patterns, warnings -->

- [x] Terminal status set: `{complete, archived, dismissed, invalid, deferred}` - filter from queues. Now in WorkEngine.
- [x] Query by tag, not location: Status determines visibility, not directory. Type is field, not prefix. Epoch is field, not inferred.
- [x] Epoch transition pattern: Triage work item → MANIFEST.md with rationale → status updates → queue reflects decisions.
