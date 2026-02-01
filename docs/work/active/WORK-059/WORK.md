---
template: work_item
id: WORK-059
title: Claude Code Task System vs HAIOS WorkEngine Comparison
type: investigation
status: backlog
owner: Hephaestus
created: 2026-02-01
spawned_by: WORK-056
chapter: null
arc: workuniversal
closed: null
priority: medium
effort: medium
traces_to:
- REQ-WORK-001
requirement_refs: []
source_files:
- .claude/haios/modules/work_engine.py
acceptance_criteria:
- Claude Code task system capabilities documented
- Comparison matrix: CC Tasks vs HAIOS WorkEngine
- Identify complementary vs overlapping features
- Recommendation: adopt, adapt, or ignore
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-01 15:18:20
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-02-01
last_updated: '2026-02-01T15:20:30'
---
# WORK-059: Claude Code Task System vs HAIOS WorkEngine Comparison

---

## Context

Claude Code 2.1.16+ introduced a new task management system with dependency tracking. HAIOS has its own WorkEngine. This investigation compares them.

**Claude Code Task System (from Changelog):**
- TaskCreate, TaskUpdate, TaskGet, TaskList tools
- Dependency tracking (blockedBy, blocks)
- Status workflow: pending -> in_progress -> completed
- Task deletion via TaskUpdate
- Controlled by `CLAUDE_CODE_ENABLE_TASKS` env var

**HAIOS WorkEngine:**
- Work items with WORK.md files
- Full lifecycle tracking (node_history, current_node)
- Type-based routing (investigation, implementation, cleanup)
- Rich frontmatter (traces_to, acceptance_criteria, memory_refs)
- Governance integration (cycles, gates)

**Questions:**
1. Are these complementary (CC tasks = ephemeral, HAIOS = persistent)?
2. Should HAIOS use CC tasks for within-session work tracking?
3. Can CC task dependencies replace/augment HAIOS blocked_by?
4. What does CC task system do that WorkEngine doesn't?

---

## Deliverables

- [ ] **CC Task System doc** - Full capability inventory
- [ ] **Comparison matrix** - Feature-by-feature comparison
- [ ] **Overlap analysis** - What's redundant, what's complementary
- [ ] **Recommendation** - Adopt for ephemeral, keep WorkEngine for persistent, or unify

---

## History

### 2026-02-01 - Created (Session 271)
- Spawned from WORK-056 parent investigation
- Linked to workuniversal arc (work item management)

---

## References

- @docs/work/active/WORK-056/WORK.md (parent investigation)
- @.claude/haios/modules/work_engine.py (HAIOS implementation)
