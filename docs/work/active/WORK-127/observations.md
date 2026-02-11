---
template: observations
work_id: 'WORK-127'
captured_session: '348'
generated: '2026-02-11'
last_updated: '2026-02-11T21:53:31'
---
# Observations: WORK-127

## What surprised you?

- The bug was simpler than described. WORK-127 stated hooks write to `.claude/governance-events.jsonl` while `queue_ceremonies.py` writes to `.claude/haios/governance-events.jsonl`. Investigation found no hooks write to governance-events.jsonl at all. Both `governance_events.py` and `queue_ceremonies.py` use `Path(__file__).parent.parent / "governance-events.jsonl"` which resolves identically to `.claude/haios/governance-events.jsonl`. The stale `.claude/governance-events.jsonl` (38KB, Dec 29 - Jan 27) was an orphan from when lib modules lived at `.claude/lib/` before the `.claude/haios/lib/` migration. The migration silently fixed the path resolution.

## What's missing?

- No `events_file` path was registered in haios.yaml before this fix. The `Path(__file__).parent.parent` pattern works but is fragile — if files move again (portability arc CH-028), the path silently changes. Added `governance_events` to haios.yaml paths section but didn't wire `governance_events.py` to use ConfigLoader (that's portability scope, WORK-067).

## What should we remember?

- Memory 84909 pattern confirmed: "verify actual state before implementing — may find work is already done." The lib migration had already resolved the dual-file issue by changing `Path(__file__)` resolution. The stale file was dormant, not actively written. Always investigate the actual state of claimed bugs before fixing.
- `Path(__file__).parent.parent` patterns are migration-sensitive. When files move directories, these paths silently change. The portability arc (CH-028 PathConfigMigration) should audit all such patterns.

## What drift did you notice?

- WORK-127 context section incorrectly described hooks as writing to `.claude/governance-events.jsonl`. The stale file predated hooks infrastructure and was created by the old lib location. No active code drift — only stale documentation in the work item itself.
