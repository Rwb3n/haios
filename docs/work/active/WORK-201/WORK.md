---
template: work_item
id: WORK-201
title: Governance Events Not Written by set-cycle Recipe
type: investigation
status: complete
owner: Hephaestus
created: 2026-02-23
spawned_by: WORK-200
spawned_children: []
chapter: CH-059
arc: call
closed: '2026-02-23'
priority: medium
effort: small
traces_to:
- REQ-CEREMONY-005
requirement_refs: []
source_files:
- justfile
- .claude/haios/governance-events.jsonl
acceptance_criteria:
- 'Root cause identified: why just set-cycle does not write to governance-events.jsonl'
- Fix implemented or documented as intentional (if hooks are the sole event source)
- close-work-cycle VALIDATE soft gate no longer false-warns on properly governed items
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: CHAIN
current_node: CHAIN
node_history:
- node: backlog
  entered: 2026-02-23 12:26:34
  exited: '2026-02-23T14:20:17.769416'
artifacts: []
cycle_docs: {}
memory_refs:
- 87756
- 87801
- 87802
- 87803
- 87804
- 87805
- 87825
extensions: {}
version: '2.0'
generated: 2026-02-23
last_updated: '2026-02-23T14:20:17.774292'
queue_history:
- position: ready
  entered: '2026-02-23T14:11:55.980931'
  exited: '2026-02-23T14:12:05.804772'
- position: working
  entered: '2026-02-23T14:12:05.804772'
  exited: '2026-02-23T14:20:17.769416'
- position: done
  entered: '2026-02-23T14:20:17.769416'
  exited: null
---
# WORK-201: Governance Events Not Written by set-cycle Recipe

---

## Context

During WORK-200 closure, `grep WORK-200 governance-events.jsonl` returned empty despite multiple `just set-cycle` invocations during the implementation cycle. The close-work-cycle VALIDATE phase checks governance events as a soft gate — no events triggers a warning that governance may have been bypassed.

Root cause hypothesis: `just set-cycle` updates `.claude/haios-status-slim.json` but may not write to `governance-events.jsonl`. Events may only be written by PreToolUse/PostToolUse hooks, not by the justfile recipe. If so, this is either:
1. A bug: set-cycle should write events (and doesn't)
2. By design: only hooks write events (and the soft gate should account for this)

Investigation needed to determine which, then fix accordingly.

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning) -->

- [x] Root cause identified and documented
- [x] Fix implemented: added log_phase_transition() call to just set-cycle recipe (justfile:312)
- [x] Soft gate self-corrected: events now written, check_work_item_events() finds them

---

## History

### 2026-02-23 - Investigation Complete (Session 432)

**Root Cause:** `just set-cycle` (`justfile:309-311`) only updates `haios-status-slim.json` and syncs `WORK.md` cycle_phase via `sync_work_md_phase()`. It does NOT call `log_phase_transition()` from `governance_events.py`.

**Event logging exists in two other paths, neither covering `just set-cycle`:**
1. `CycleRunner._emit_phase_entered()` (`cycle_runner.py:275`) — CLI-invoked cycle entry
2. `cycle_state.advance_cycle_phase()` (`cycle_state.py:118-125`) — PostToolUse auto-advance for 3 lifecycle skills only (implementation-cycle, investigation-cycle, plan-authoring-cycle)

**All 30+ skill callsites use `just set-cycle` for phase entry.** This means most phase transitions go unlogged.

**Hypothesis Verdicts:**
- H1 (bug — missing `log_phase_transition` call): **CONFIRMED** (high confidence)
- H2 (CycleRunner intended as sole source): **REFUTED** (high confidence)
- H3 (soft gate needs adjustment): **CONFIRMED** (medium) — self-corrects once H1 fixed

**Recommended Fix:** Add `log_phase_transition()` call to `just set-cycle` recipe. Single-line addition:
```python
from governance_events import log_phase_transition; log_phase_transition('{{phase}}', '{{work_id}}', 'Hephaestus')
```

**Epistemic Review:** PROCEED — no blocking unknowns. Root cause clear, fix straightforward.

### 2026-02-23 - Created (Session 430)
- Spawned from WORK-200 retro-cycle EXTRACT-1 (bug, priority: next)
- Evidence: grep WORK-200 governance-events.jsonl returned empty after full implementation cycle

---

## References

- @docs/work/active/WORK-200/WORK.md (parent)
- @.claude/haios/governance-events.jsonl (target)
- @justfile:309-311 (set-cycle recipe — root cause location)
- @.claude/haios/lib/governance_events.py:38-58 (log_phase_transition function)
- @.claude/haios/lib/cycle_state.py:118-125 (auto-advance event logging)
- @.claude/haios/modules/cycle_runner.py:272-275 (CycleRunner event logging)
- Memory: 87756 (retro-extract:WORK-200 EXTRACT-1), 87801-87805 (S432 findings)
