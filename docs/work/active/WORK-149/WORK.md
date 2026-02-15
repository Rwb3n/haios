---
template: work_item
id: WORK-149
title: Three-Tier Entry Point Architecture ADR
type: design
status: complete
owner: Hephaestus
created: 2026-02-14
spawned_by: WORK-020
spawned_children: []
chapter: CH-034
arc: discoverability
closed: '2026-02-15'
priority: medium
effort: small
traces_to:
- REQ-DISCOVER-002
- REQ-DISCOVER-003
requirement_refs: []
source_files: []
acceptance_criteria:
- ADR documents three-tier model (commands, skills+agents, recipes)
- ADR defines tier boundaries and assignment criteria
- ADR records decision context from WORK-020 investigation
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-14 14:38:34
  exited: '2026-02-15T22:49:39.840044'
artifacts: []
cycle_docs: {}
memory_refs:
- 85527
extensions:
  epoch: E2.6
version: '2.0'
generated: 2026-02-14
last_updated: '2026-02-15T22:49:39.843180'
queue_history:
- position: done
  entered: '2026-02-15T22:49:39.840044'
  exited: null
---
# WORK-149: Three-Tier Entry Point Architecture ADR

---

## Context

WORK-020 investigation (S368) designed a three-tier entry point architecture for HAIOS. This ADR formalizes that decision.

**The model:**
- **Tier 1 (Commands):** Human-invocable, 19 total, auto-discovered by Claude Code from `.claude/commands/`
- **Tier 2 (Skills + Agents):** Agent-invocable, 45 total, auto-discovered by Claude Code from `.claude/skills/` and `.claude/agents/`
- **Tier 3 (Recipes):** Implementation details, 87 total, called only by skills/commands, never by agent directly

**Key decision:** Agents should never run `just X` directly. All recipe functionality is accessed through Tier 1/2 wrappers.

---

## Deliverables

- [ ] ADR document created (docs/ADR/ADR-XXX-three-tier-entry-points.md)
- [ ] Decision context from WORK-020 investigation included
- [ ] Tier boundary definitions with assignment criteria
- [ ] Migration path for 18 unwrapped Tier 2 recipes (deferred to E2.7)
- [ ] CLAUDE.md updated to reference ADR

---

## History

### 2026-02-14 - Created (Session 368)
- Spawned from WORK-020 Discoverability Architecture investigation

---

## References

- @docs/work/active/WORK-020/WORK.md (spawn source)
- Memory: 85302, 85303 (WORK-020 findings)
- Memory: 82302 (recipe layer stack decision)
