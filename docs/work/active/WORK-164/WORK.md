---
template: work_item
id: WORK-164
title: Agent Cards
type: design
status: complete
owner: Hephaestus
created: 2026-02-17
spawned_by: Session-394-decomposition
spawned_children: []
chapter: CH-063
arc: discover
closed: '2026-02-24'
priority: medium
effort: large
traces_to:
- REQ-DISCOVER-002
- REQ-DISCOVER-003
requirement_refs: []
source_files:
- .claude/agents/critique-agent.md
- .claude/agents/investigation-agent.md
- .claude/agents/validation-agent.md
- CLAUDE.md
acceptance_criteria:
- Agent card schema defined (id, role, capabilities, tools, triggers, produces, consumes)
- All existing agents have structured capability cards
- Infrastructure query mechanism for agent discovery
- CLAUDE.md agent table replaced by infrastructure discovery
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: CHAIN
current_node: CHAIN
node_history:
- node: backlog
  entered: 2026-02-17 22:08:08
  exited: '2026-02-24T10:46:35.346560'
artifacts:
- docs/work/active/WORK-164/plans/PLAN.md
- .claude/haios/lib/agent_cards.py
- .claude/haios/lib/generate_agents_md.py
- AGENTS.md
- tests/test_agent_cards.py
- tests/test_generate_agents_md.py
cycle_docs:
  plan: docs/work/active/WORK-164/plans/PLAN.md
memory_refs:
- 85154
- 85155
- 85210
- 85476
- 88132
- 88133
- 88134
- 88135
- 85322
- 88136
extensions:
  epoch: E2.8
  inspiration: Google A2A Agent Cards + Dragon Quest class system
version: '2.0'
generated: 2026-02-17
last_updated: '2026-02-24T10:46:35.367859'
queue_history:
- position: ready
  entered: '2026-02-24T10:09:54.006724'
  exited: '2026-02-24T10:10:03.131543'
- position: working
  entered: '2026-02-24T10:10:03.131543'
  exited: '2026-02-24T10:46:35.346560'
- position: done
  entered: '2026-02-24T10:46:35.346560'
  exited: null
---
# WORK-164: Agent Cards

---

## Context

Agents are currently hardcoded in the CLAUDE.md agent table (mem:85154, 85210). There is no way for an agent to discover what other agents exist, what they can do, or when to use them — except by reading documentation. This is the same problem as ceremony overhead: reading instead of querying.

**Inspiration:** Google A2A Agent Cards + Dragon Quest class system (mem:85154, 85155). Each agent has a stateless identity card: role, capabilities, tools, triggers, what it produces, what it consumes. Agents discover each other through infrastructure, not hardcoded knowledge.

**Design scope:**
1. Define the agent card schema (YAML frontmatter in agent .md files?)
2. Query mechanism (engine function? MCP tool?)
3. Migration path from CLAUDE.md table to infrastructure

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning)

     These checkboxes are the SOURCE OF TRUTH for work completion.

     During CHECK phase of implementation-cycle:
     - Agent MUST read this section
     - Agent MUST verify EACH checkbox can be marked complete
     - If ANY deliverable is incomplete, work is NOT done

     "Tests pass" ≠ "Deliverables complete"
     Tests verify code works. Deliverables verify scope is complete.

     NOTE (WORK-001): Acceptance criteria are in frontmatter (machine-parseable).
     Deliverables are implementation outputs, not requirements.
-->

- [x] Agent card schema definition
- [x] Existing agent audit (how many, what metadata exists)
- [x] Query mechanism design (infrastructure discovery)
- [x] Migration plan from CLAUDE.md table
- [x] Design document or ADR

---

## History

### 2026-02-17 - Created (Session 394)
- Spawned during E2.8 arc decomposition
- CH-063 AgentCards

---

## References

- @.claude/haios/epochs/E2_8/arcs/discover/ARC.md
- @.claude/agents/ (existing agent definitions)
- Memory: 85154 (Dragon Quest pattern), 85210 (agents not discoverable), 85476 (capability card query tool)
