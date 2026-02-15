---
template: work_item
id: WORK-144
title: Agent Capability Cards
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-14
spawned_by: S365-epoch-planning
spawned_children: []
chapter: CH-042
arc: observability
closed: '2026-02-15'
priority: medium
effort: medium
traces_to:
- REQ-DISCOVER-004
requirement_refs: []
source_files:
- .claude/agents/
acceptance_criteria:
- All 11 agents have structured capability cards
- Cards include identity, tools, contracts, trigger conditions
- Cards follow A2A-inspired pattern
- Agent definitions discoverable via infrastructure (YAML frontmatter = machine-readable
  infrastructure per REQ-DISCOVER-003; discovery tooling deferred to E2.7)
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-14 12:45:14
  exited: '2026-02-15T21:12:44.358730'
artifacts: []
cycle_docs: {}
memory_refs:
- 85211
- 85463
- 85464
- 85465
- 85466
- 85467
extensions:
  epoch: E2.6
version: '2.0'
generated: 2026-02-14
last_updated: '2026-02-15T21:12:44.362737'
queue_history:
- position: ready
  entered: '2026-02-15T20:51:17.510508'
  exited: '2026-02-15T20:51:24.334528'
- position: working
  entered: '2026-02-15T20:51:24.334528'
  exited: '2026-02-15T21:12:44.358730'
- position: done
  entered: '2026-02-15T21:12:44.358730'
  exited: null
---
# WORK-144: Agent Capability Cards

---

## Context

**Problem:** 11 agents exist (.claude/agents/) but have no structured capability metadata. Other agents and the operator cannot discover what an agent does, what tools it uses, or when it should be triggered without reading its full system prompt.

**Evidence (S365 system audit):**
- 11 agent files in .claude/agents/
- No standardized capability card format
- Agent selection relies on CLAUDE.md descriptions (hardcoded, not discoverable)
- Memory 85211: "create Agent Cards for all 11 agents" (operator directive)

**A2A-inspired pattern:** Google's Agent-to-Agent protocol defines Agent Cards with identity, capabilities, and interaction contracts. Adapt this pattern for HAIOS agents.

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning) -->

- [ ] Agent Card schema defined as extended YAML frontmatter fields (beyond existing name/description/tools/model)
- [ ] Schema includes: trigger_conditions, input_contract, output_contract, invoked_by, requirement_level, related_agents
- [ ] All 11 agent .md files updated with capability card frontmatter
- [ ] Cards backward-compatible (existing frontmatter fields preserved, new fields added)
- [ ] CLAUDE.md agent table updated to reference capability card fields instead of hardcoded descriptions

---

## History

### 2026-02-14 - Created (Session 366)
- E2.6 arc decomposition: assigned to observability arc, CH-042
- Derives from S365 operator directive (memory 85211)

---

## References

- @.claude/agents/ (agent definitions)
- @.claude/haios/epochs/E2_6/system-audit-S365.md (inventory)
- Memory: 85211 (directive)
