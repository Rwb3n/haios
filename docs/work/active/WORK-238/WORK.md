---
template: work_item
id: WORK-238
title: 'Investigation: Implementation-Cycle DONE/CHAIN Phase Duplication with Close-Work-Cycle'
type: investigation
status: complete
owner: Hephaestus
created: 2026-03-06
spawned_by: WORK-237
spawned_children:
- WORK-241
- WORK-242
- WORK-243
chapter: CH-059
arc: call
closed: '2026-03-06'
priority: medium
effort: medium
traces_to:
- REQ-CEREMONY-002
- REQ-LIFECYCLE-005
requirement_refs: []
source_files:
- .claude/skills/implementation-cycle/phases/DONE.md
- .claude/skills/implementation-cycle/phases/CHAIN.md
- .claude/skills/close-work-cycle/SKILL.md
- .claude/skills/retro-cycle/SKILL.md
acceptance_criteria:
- 'Duplication map documented: which actions appear in multiple phases/skills with
  evidence'
- 'Root cause identified: why DONE/CHAIN diverged from close-work-cycle over time'
- 'Design proposal: unified closure flow that eliminates duplication while preserving
  all gates'
- 'Impact assessment: which other lifecycle skills (investigation-cycle, design-cycle)
  have similar patterns'
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: CHAIN
current_node: CHAIN
node_history:
- node: backlog
  entered: 2026-03-06 21:46:30
  exited: '2026-03-06T23:50:13.743289'
artifacts: []
cycle_docs: {}
memory_refs:
- 89161
- 89162
- 89163
- 89164
- 89165
- 89180
- 89181
- 89182
- 89183
- 89284
- 89285
- 89286
- 89287
- 89288
- 89334
- 89335
- 89336
- 89337
- 89338
- 89339
- 89340
- 89341
- 89342
- 89343
- 89344
- 89374
extensions: {}
version: '2.0'
generated: 2026-03-06
last_updated: '2026-03-06T23:50:13.752018'
queue_history:
- position: ready
  entered: '2026-03-06T23:37:05.150439'
  exited: '2026-03-06T23:37:07.044343'
- position: working
  entered: '2026-03-06T23:37:07.044343'
  exited: '2026-03-06T23:50:13.743289'
- position: done
  entered: '2026-03-06T23:50:13.743289'
  exited: null
---
# WORK-238: Investigation: Implementation-Cycle DONE/CHAIN Phase Duplication with Close-Work-Cycle

---

## Context

**Trigger:** During WORK-237 implementation (S461), retro-cycle was skipped in the DONE→CHAIN transition because implementation-cycle's CHAIN phase uses `mcp__haios-operations__work_close()` directly instead of invoking `/close` (which chains retro→close-work-cycle).

**Problem Statement:** Implementation-cycle's DONE and CHAIN phases duplicate responsibilities that close-work-cycle and retro-cycle now handle. This duplication emerged because DONE/CHAIN were written before retro-cycle (WORK-142) and close-work-cycle matured. The result:

| Action | DONE | CHAIN | close-work-cycle |
|--------|------|-------|------------------|
| WHY capture | YES (ingester_ingest) | — | retro-cycle COMMIT |
| Plan status → complete | YES | — | ARCHIVE |
| Git commit | YES | YES | CHAIN (checkpoint) |
| Set status complete | — | YES (work_close) | ARCHIVE |
| Retro-cycle | **MISSING** | **MISSING** | /close prerequisite |
| Routing | — | YES | CHAIN |
| Checkpoint | — | — | CHAIN |
| DoD validation | — | — | VALIDATE |

**Scope:** This may affect investigation-cycle and design-cycle DONE/CHAIN phases too (same template origin). This investigation should assess all lifecycle skills, not just implementation-cycle.

---

## Deliverables

- [ ] Duplication map across all lifecycle DONE/CHAIN phases vs close-work-cycle
- [ ] Root cause analysis: timeline of when divergence occurred
- [ ] Design proposal: unified closure flow
- [ ] Impact assessment across investigation-cycle, design-cycle, validation-cycle

---

## History

### 2026-03-06 - Created (Session 461)
- Spawned from WORK-237 retro-cycle WCBB-2, WMI-1 findings
- Operator confirmed investigation type — "start of another big flow revisit"
- Initial duplication map captured from live session evidence

---

## References

- @.claude/skills/implementation-cycle/phases/DONE.md
- @.claude/skills/implementation-cycle/phases/CHAIN.md
- @.claude/skills/close-work-cycle/SKILL.md
- @.claude/skills/retro-cycle/SKILL.md
- WORK-237 retro findings: WCBB-2 (retro skipped), WMI-1 (no mechanical enforcement)
- Memory: 89161-89165 (retro-reflect), 89180-89183 (retro-kss)
- WORK-235 investigation findings (S464): Triple DoD verification redundancy confirmed, dod-validation-cycle redundant for all tiers, DONE→CHECK merge proposed, ~3900 tokens/closure savings estimated
- @docs/work/active/WORK-235/investigations/001-post-work-ceremony-token-efficiency.md
