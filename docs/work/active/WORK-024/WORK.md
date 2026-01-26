---
template: work_item
id: WORK-024
title: Prune deprecated .claude/lib/ - consolidate to .claude/haios/lib/
type: investigation
status: active
owner: Hephaestus
created: 2026-01-26
spawned_by: null
chapter: null
arc: migration
closed: null
priority: high
effort: medium
traces_to: []
requirement_refs: []
source_files:
- .claude/lib/
- .claude/haios/lib/
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-26 23:22:37
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-26
last_updated: '2026-01-26T23:23:58'
---
# WORK-024: Prune deprecated .claude/lib/ - consolidate to .claude/haios/lib/

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Two library locations exist causing confusion and bugs:
- `.claude/lib/` - marked DEPRECATED but still used by justfile recipes and tests
- `.claude/haios/lib/` - the target location but not consistently used

**Evidence:**
- Session 247: E2-306 plan specified wrong path, caught by critique-agent
- Session 245: Drift warning about test_governance_events.py importing from deprecated location
- 11+ justfile recipes use `.claude/lib/` pattern
- New functions (log_session_start, log_session_end) only exist in `.claude/haios/lib/`

**Impact:**
- Agent confusion about which path to use
- ImportError risk when functions exist in one location but not the other
- Technical debt accumulating

---

## Deliverables

- [ ] Inventory all consumers of `.claude/lib/` (justfile, tests, imports)
- [ ] Inventory function differences between the two locations
- [ ] Create migration plan (spawn work items for each migration step)
- [ ] Block legacy ID patterns (E2-XXX, INV-XXX) in scaffold command

---

## History

### 2026-01-26 - Created (Session 247)
- Pattern keeps causing issues - time to fix systematically
- Operator requested investigation for next session

---

## References

- @.claude/lib/DEPRECATED.md (if exists)
- @docs/work/active/E2-306/observations.md (critique-agent findings)
- Session 245 checkpoint (drift warning)
