---
template: work_item
id: WORK-144
title: "Agent Capability Cards"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-14
spawned_by: S365-epoch-planning
spawned_children: []
chapter: CH-042
arc: observability
closed: null
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
- Agent definitions discoverable via infrastructure
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-02-14T12:45:14
    exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 85211
extensions:
  epoch: E2.6
version: "2.0"
generated: 2026-02-14
last_updated: 2026-02-14T12:48:00
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

- [ ] Agent Card schema defined (YAML frontmatter fields)
- [ ] All 11 agents updated with capability cards
- [ ] Cards include: identity, description, tools, trigger conditions, input/output contracts
- [ ] Discovery mechanism can enumerate agent capabilities from card metadata

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
