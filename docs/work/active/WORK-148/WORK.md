---
template: work_item
id: WORK-148
title: "Remove Stub and Deprecated Skills"
type: cleanup
status: active
owner: Hephaestus
created: 2026-02-14
spawned_by: WORK-020
spawned_children: []
chapter: CH-034
arc: discoverability
closed: null
priority: low
effort: trivial
traces_to:
- REQ-DISCOVER-003
requirement_refs: []
source_files:
- .claude/skills/arc-review/SKILL.md
- .claude/skills/chapter-review/SKILL.md
- .claude/skills/epoch-review/SKILL.md
- .claude/skills/requirements-review/SKILL.md
- .claude/skills/observation-capture-cycle/SKILL.md
acceptance_criteria:
- 4 stub skills (arc-review, chapter-review, epoch-review, requirements-review) removed or converted to non-stub
- Deprecated observation-capture-cycle skill removed
- System prompt no longer lists removed skills
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-14T14:38:34
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  epoch: E2.6
version: "2.0"
generated: 2026-02-14
last_updated: 2026-02-14T14:38:34
---
# WORK-148: Remove Stub and Deprecated Skills

---

## Context

WORK-020 investigation found 4 stub skills and 1 deprecated skill in the system prompt contributing no value but consuming tokens and adding cognitive noise.

**Stub skills (stub: true in frontmatter):** arc-review, chapter-review, epoch-review, requirements-review — all feedback ceremonies with no implementation.

**Deprecated skill:** observation-capture-cycle — replaced by retro-cycle (WORK-142).

**Action:** Remove or convert these 5 skills to reduce system prompt bloat.

---

## Deliverables

- [ ] Remove deprecated observation-capture-cycle skill directory
- [ ] Decide per stub: remove entirely or convert to minimal functional skill
- [ ] Verify system prompt no longer lists removed skills
- [ ] Update any references in other skills/commands that mention removed skills

---

## History

### 2026-02-14 - Created (Session 368)
- Spawned from WORK-020 Discoverability Architecture investigation

---

## References

- @docs/work/active/WORK-020/WORK.md (spawn source)
- Memory: 85302 (WORK-020 findings)
