---
template: work_item
id: WORK-087
title: Implement Caller Chaining (CH-004)
type: feature
status: complete
owner: Hephaestus
created: 2026-02-03
spawned_by: E2.5-decomposition
chapter: CH-004-CallerChaining
arc: lifecycles
closed: '2026-02-03'
priority: high
effort: medium
traces_to:
- REQ-LIFECYCLE-004
requirement_refs: []
source_files:
- .claude/haios/modules/cycle_runner.py
- .claude/skills/close-work-cycle/SKILL.md
acceptance_criteria:
- CycleRunner.run() returns without auto-chaining
- close-work-cycle prompts for next action, doesn't auto-spawn
- Complete without spawn is valid and doesn't warn
blocked_by:
- WORK-084
- WORK-085
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-03 19:30:00
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 83400
- 83401
- 83402
- 83403
- 83404
- 83409
- 83410
extensions:
  epoch: E2.5
  implementation_type: REFACTOR
version: '2.0'
generated: 2026-02-03
last_updated: '2026-02-03T23:05:50'
---
# WORK-087: Implement Caller Chaining (CH-004)

---

## Context

CHAIN phase has routing logic embedded in skill, not returned to caller. The skill decides next action based on work type, not the operator/caller.

**Current State:**
```markdown
# From SKILL.md:191-200
6. **Apply routing decision table** (WORK-030: type field is authoritative):
   - If `next_work_id` is None -> `await_operator`
   - If `type` == "investigation" -> `invoke_investigation`
   ...
```

**Gap to address:**
- Skill-embedded routing vs caller-controlled routing
- Need explicit `spawn_next=None` acceptance

**NOTE:** Per CH-025 decision, `cycle_runner.chain()` was removed in favor of `asset.pipe()`. Assets carry data; chaining is about data flow.

---

## Deliverables

- [ ] Ensure CycleRunner.run() returns output without auto-chaining
- [ ] Update close-work-cycle CHAIN phase to prompt options without auto-executing
- [ ] Verify "Complete without spawn" path doesn't emit warnings
- [ ] Unit tests: design completes -> no implementation started
- [ ] Integration test: Design -> prompt -> choose "store only" -> verify no spawn

---

## History

### 2026-02-03 - Completed (Session 303)
- Implemented REQ-LIFECYCLE-004 caller chaining
- Refactored close-work-cycle CHAIN phase to present options via AskUserQuestion
- "Complete without spawn" now first-class valid option
- Added 3 tests in test_close_work_cycle.py (all pass)
- Memory refs: 83400-83404

### 2026-02-03 - Created (Session 297)
- Decomposed from E2.5 CH-004-CallerChaining
- Depends on WORK-084, WORK-085

---

## References

- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-004-CallerChaining.md
- @.claude/haios/epochs/E2_5/arcs/assets/CH-025-AssetPiping.md (asset.pipe() for chaining)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-LIFECYCLE-004)
