---
template: work_item
id: WORK-213
title: 'Retro-Cycle Phase Reordering: COMMIT before EXTRACT'
type: refactor
status: complete
owner: Hephaestus
created: 2026-02-24
spawned_by: null
spawned_children: []
chapter: CH-059
arc: call
closed: '2026-02-24'
priority: medium
effort: medium
traces_to:
- REQ-CEREMONY-002
requirement_refs: []
source_files:
- .claude/skills/retro-cycle/SKILL.md
acceptance_criteria:
- Retro-cycle phase order is REFLECT → DERIVE → COMMIT → EXTRACT
- COMMIT stores observations + K/S/S to memory, returns concept IDs
- EXTRACT stores findings to memory with concept IDs (no auto-spawn per REQ-LIFECYCLE-004)
- 'EXTRACT responsibility narrowed: classifies observations into bug/feature/refactor/upgrade
  and stores to memory; DERIVE handles K/S/S synthesis'
- Context alert threshold changed to 15% in retro-cycle SKILL.md
- SKILL.md output_contract updated to reflect EXTRACT semantic changes
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: CHAIN
current_node: CHAIN
node_history:
- node: backlog
  entered: 2026-02-24 10:57:10
  exited: 2026-02-24 11:00:00
- node: PLAN
  entered: 2026-02-24 11:00:00
  exited: '2026-02-24T11:57:09.093873'
artifacts: []
cycle_docs: {}
memory_refs:
- 88137
- 88138
- 88139
- 88140
- 88141
- 88142
- 88143
- 88146
- 88147
- 88148
- 88149
- 88150
- 88151
- 88152
- 88153
- 88154
- 88197
- 88198
- 88199
- 88200
- 88201
- 88202
- 88203
- 88204
- 88205
extensions: {}
version: '2.0'
generated: 2026-02-24
last_updated: '2026-02-24T11:57:09.098824'
queue_history:
- position: done
  entered: '2026-02-24T11:57:09.093873'
  exited: null
---
# WORK-213: Retro-Cycle Phase Reordering: COMMIT before EXTRACT

---

## Context

S439 retro-cycle revealed phase ordering issue. Current: REFLECT → DERIVE → EXTRACT → COMMIT. EXTRACT (haiku subagent) used 37K tokens, 146s, 14 tool calls for marginal signal over DERIVE — it reclassifies observations that DERIVE already synthesized into K/S/S. COMMIT stores everything at the end, meaning EXTRACT can't reference memory IDs.

Operator directive: reorder to REFLECT → DERIVE → COMMIT → EXTRACT. COMMIT stores observations + K/S/S immediately (they're complete cognitive outputs). EXTRACT then classifies and stores findings to memory with concept IDs — traceable from birth. No auto-spawn (REQ-LIFECYCLE-004 preserved; triage decides work item creation). Clean separation: DERIVE = K/S/S synthesis, COMMIT = persistence, EXTRACT = classify observations and store to memory.

Also: context alert threshold should be 15% (currently 19% triggers). 10% is close territory, 5% is emergency stop.

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

- [x] retro-cycle SKILL.md updated with new phase order (REFLECT -> DERIVE -> COMMIT -> EXTRACT)
- [x] COMMIT phase moved before EXTRACT with memory persistence logic
- [x] EXTRACT phase redefined: stores findings to memory with concept IDs (no auto-spawn)
- [x] Context alert threshold set to 15% in retro-cycle SKILL.md (prose, not code)
- [x] SKILL.md output_contract updated to reflect EXTRACT semantic changes

---

## History

### 2026-02-24 - Created (Session 439)
- Initial creation

---

## References

- @.claude/skills/retro-cycle/SKILL.md
- Memory: 88137-88143 (S439 operator directive on phase reordering)
- S439 retro evidence: EXTRACT haiku 37K tokens / 14 tool calls for marginal signal
