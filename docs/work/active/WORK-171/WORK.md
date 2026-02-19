---
template: work_item
id: WORK-171
title: "Mechanical Phase Migration"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-19
spawned_by: WORK-160
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: medium
traces_to:
  - REQ-CEREMONY-002
  - REQ-CEREMONY-005
requirement_refs: []
source_files:
  - .claude/skills/retro-cycle/SKILL.md
  - .claude/hooks/hooks/post_tool_use.py
  - .claude/haios/lib/session_end_actions.py
acceptance_criteria:
  - "At least 3 mechanical ceremony phases migrated from SKILL.md to hooks/modules"
  - "Retro-cycle Phase 0 scale assessment computable via lib/ function"
  - "Cycle state initialization automated on lifecycle skill invocation"
  - "Governance event logging automated on ceremony skill completion"
  - "SKILL.md files updated to reference lib/ functions instead of listing conditions"
  - "Zero regression: all existing ceremony behavior preserved"
  - "Tests verify each migrated phase produces identical outcomes"
blocked_by:
  - WORK-168
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-02-19T00:17:34
    exited: null
artifacts: []
cycle_docs: {}
memory_refs:
  - 85607
  - 84857
extensions:
  epoch: E2.8
  parent: WORK-160
version: "2.0"
generated: 2026-02-19
last_updated: 2026-02-19T00:20:00
---
# WORK-171: Mechanical Phase Migration

---

## Context

Ceremony skills (SKILL.md) consume 100% agent tokens because the agent is the runtime (mem:84857). Many ceremony phases are purely mechanical — they require zero judgment and could be executed by hooks/modules at near-zero token cost.

This capstone work item migrates at least 3 specific mechanical phases from Tier 3 (SKILL.md, agent reads) to Tier 1/2 (hooks/modules, auto-execute):

1. **Retro-cycle Phase 0 (Scale Assessment):** Currently the agent reads SKILL.md lines 119-146 and evaluates 4 computable conditions. After: `lib/retro_scale.py:assess_scale(work_id)` computes "trivial" vs "substantial" automatically.

2. **Cycle state initialization:** Currently every ceremony skill starts with "On Entry: just set-cycle ...". After: PostToolUse auto-initializes session_state when a lifecycle skill is invoked (builds on WORK-168 infrastructure).

3. **Governance event auto-logging:** Currently ceremony skills instruct the agent to log events. After: PostToolUse auto-logs ceremony start/completion events.

**Prototype:** Retro-cycle Phase 0 (mem:85607) is the proven prototype — its computable predicate pattern (4 machine-checkable conditions) extends to other mechanical phases.

---

## Deliverables

- [ ] New file `lib/retro_scale.py` with `assess_scale(work_id)` function
- [ ] PostToolUse auto-initialization of session_state on lifecycle skill invocation
- [ ] PostToolUse auto-logging of ceremony governance events
- [ ] Updated retro-cycle SKILL.md Phase 0 to reference lib/ function
- [ ] Tests in `tests/test_retro_scale.py` and `tests/test_phase_migration.py`

---

## History

### 2026-02-19 - Created (Session 399)
- Spawned from WORK-160 decomposition
- Depends on WORK-168 (Cycle Phase Auto-Advancement)
- Capstone item — satisfies WORK-160 criteria #1 and #8

---

## References

- @docs/work/active/WORK-160/WORK.md (parent)
- @docs/work/active/WORK-168/WORK.md (dependency — cycle auto-advance)
- @.claude/skills/retro-cycle/SKILL.md (Phase 0 prototype, lines 119-146)
- @.claude/hooks/hooks/post_tool_use.py (target for auto-logging)
- Memory: 85607 (retro Phase 0 prototype), 84857 (ceremony=markdown)
