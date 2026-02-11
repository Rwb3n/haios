---
template: work_item
id: WORK-127
title: Dual governance-events.jsonl file split
type: bug
status: complete
owner: Hephaestus
created: 2026-02-11
spawned_by: WORK-125
chapter: null
arc: ceremonies
closed: '2026-02-11'
priority: low
effort: small
traces_to:
- REQ-CEREMONY-001
requirement_refs: []
source_files:
- .claude/haios/lib/governance_events.py
- .claude/haios/lib/queue_ceremonies.py
- .claude/haios/config/haios.yaml
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-11 21:43:49
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 84932
- 84933
- 84934
- 84935
- 84936
- 84937
- 84938
- 84939
extensions: {}
version: '2.0'
generated: 2026-02-11
last_updated: '2026-02-11T21:55:09.108009'
---
# WORK-127: Dual governance-events.jsonl file split

---

## Context

Two separate `governance-events.jsonl` files exist:
1. `.claude/governance-events.jsonl` — written by hooks (PreToolUse, PostToolUse, etc.), last written Jan 27
2. `.claude/haios/governance-events.jsonl` — written by `queue_ceremonies.py` (`EVENTS_FILE = Path(__file__).parent.parent / "governance-events.jsonl"`)

This means `just events` and `just governance-metrics` may only read one file, missing queue ceremony events. The audit trail is split across two locations.

**Root cause:** `queue_ceremonies.py` uses a relative path from its own location (`.claude/haios/lib/` -> parent.parent -> `.claude/haios/`), while the hooks infrastructure writes to `.claude/governance-events.jsonl`.

**Fix:** Consolidate to a single canonical events file path, ideally via `ConfigLoader.get_path()`.

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning)

     These checkboxes are the SOURCE OF TRUTH for work completion.

     During CHECK phase of implementation-cycle:
     - Agent MUST read this section
     - Agent MUST verify EACH checkbox can be marked complete
     - If ANY deliverable is incomplete, work is NOT done

     "Tests pass" ≠ "Deliverables complete"
     Tests verify code works. Deliverables verify scope is complete.

     NOTE (WORK-001): Acceptance criteria are in frontmatter (machine-parseable).
     Deliverables are implementation outputs, not requirements.
-->

- [x] Identify all writers to both governance-events.jsonl files
- [x] Consolidate to single canonical path (via ConfigLoader or shared constant)
- [x] Verify `just events` and `just governance-metrics` read from canonical path

---

## History

### 2026-02-11 - Fixed (Session 348)
- Investigation found both lib modules already write to `.claude/haios/governance-events.jsonl` (correct)
- `.claude/governance-events.jsonl` was a stale orphan from pre-lib-migration era (Dec 29 - Jan 27)
- No active code wrote to the stale file — the "split" was historical, not active
- Deleted stale orphan file (38KB, last written Jan 27)
- Updated docstring comments in both lib modules to reflect actual path
- Added `governance_events` path to haios.yaml for ConfigLoader consistency
- All 11 governance_events tests pass

### 2026-02-11 - Created (Session 347)
- Discovered during WORK-125 CHECK phase: QueueCeremony events not found in expected file

---

## References

- @.claude/haios/lib/queue_ceremonies.py:56 (EVENTS_FILE constant)
- @docs/work/active/WORK-125/observations.md (source observation)
