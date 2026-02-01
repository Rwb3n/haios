---
template: work_item
id: WORK-059
title: Claude Code Task System vs HAIOS WorkEngine Comparison
type: investigation
status: complete
owner: Hephaestus
created: 2026-02-01
spawned_by: WORK-056
chapter: null
arc: workuniversal
closed: '2026-02-01'
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
memory_refs:
- 82904
- 82905
- 82906
- 82907
- 82908
- 82913
- 82914
extensions: {}
version: '2.0'
generated: 2026-02-01
last_updated: '2026-02-01T16:50:09'
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

- [x] **CC Task System doc** - Full capability inventory
- [x] **Comparison matrix** - Feature-by-feature comparison
- [x] **Overlap analysis** - What's redundant, what's complementary
- [x] **Recommendation** - Adopt for ephemeral, keep WorkEngine for persistent, or unify

---

## History

### 2026-02-01 - Created (Session 271)
- Spawned from WORK-056 parent investigation
- Linked to workuniversal arc (work item management)

### 2026-02-01 - Investigation Complete (Session 274)
- Explored CC Task tools (TaskCreate, TaskUpdate, TaskGet, TaskList)
- Compared with HAIOS WorkEngine feature-by-feature
- Findings: Systems are COMPLEMENTARY, not competing
  - CC Tasks: Ephemeral, session-scoped, UX-focused (activeForm spinner)
  - WorkEngine: Persistent, disk-based, governance-integrated
- Recommendation: Two-layer model
  - Strategic: WorkEngine for work items (days/weeks)
  - Tactical: CC Tasks for DO phase sub-tasks (minutes/hours)
- No integration between systems needed
- Memory refs: 82904-82908

---

## Findings

### CC Task System Capabilities

| Tool | Purpose | Parameters |
|------|---------|------------|
| `TaskCreate` | Create task | subject, description, activeForm |
| `TaskUpdate` | Modify task | taskId, status, addBlockedBy, addBlocks |
| `TaskGet` | Get details | taskId |
| `TaskList` | List all | (none) |

**Key Characteristics:**
- Auto-increment integer IDs (#1, #2, #3...)
- Status: pending -> in_progress -> completed
- Ephemeral: Lost on session restart
- activeForm: Spinner text during in_progress

### Comparison Matrix

| Feature | CC Tasks | WorkEngine | Winner |
|---------|----------|------------|--------|
| Persistence | Session-scoped | Disk (WORK.md) | WorkEngine |
| UX (spinner) | activeForm | None | CC Tasks |
| Dependencies | blockedBy/blocks | blocked_by + traces_to | WorkEngine |
| Status states | 3 | Full DAG + history | WorkEngine |
| Metadata | description only | 15+ fields | WorkEngine |
| Governance | None | GovernanceLayer | WorkEngine |
| Creation speed | Instant | File scaffold | CC Tasks |

### Recommendation

**Two-Layer Model:**
- **Strategic Layer:** HAIOS WorkEngine (unchanged)
- **Tactical Layer:** CC Tasks for DO phase micro-tracking (RECOMMENDED)

No integration between systems. CC Task adoption is L2 (RECOMMENDED), not L3 (REQUIRED).

---

## References

- @docs/work/active/WORK-056/WORK.md (parent investigation)
- @.claude/haios/modules/work_engine.py (HAIOS implementation)
