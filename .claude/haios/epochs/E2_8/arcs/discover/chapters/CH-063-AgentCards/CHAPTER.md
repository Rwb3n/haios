---
id: CH-063
name: Agent Cards
arc: discover
epoch: E2.8
status: Complete
work_items:
- id: WORK-164
  title: Agent Cards
  status: Complete
  type: design
exit_criteria:
- text: All agents have structured capability cards
  checked: true
  evidence: 14 agents in .claude/agents/ with full frontmatter schema. WORK-164 closed S424.
- text: Cards discoverable via infrastructure query (not CLAUDE.md lookup)
  checked: true
  evidence: agent_cards.py provides list_agents(), get_agent(), filter_agents(). AGENTS.md auto-generated.
- text: 'Schema defined: id, role, capabilities, tools, triggers, produces, consumes'
  checked: true
  evidence: All 14 agent cards include id, role, capabilities, tools, trigger_conditions, produces, consumes, plus model, category, input/output contracts.
dependencies: []
---
# generated: 2026-02-19
# System Auto: last updated on: 2026-02-19T08:30:00
# Chapter: AgentCards

## Chapter Definition

**Chapter ID:** CH-063
**Arc:** discover
**Epoch:** E2.8
**Name:** Agent Cards
**Status:** Planning

---

## Purpose

Define structured capability cards for all agents — discoverable via infrastructure, not hardcoded in CLAUDE.md. Inspired by Google A2A Agent Cards and Dragon Quest class system.

**Core insight:** Agents are currently hardcoded in the CLAUDE.md agent table (mem:85154, 85210). There is no way for an agent to discover what other agents exist, what they can do, or when to use them — except by reading documentation. Agent Cards provide typed, queryable identity.

**Schema (proposed):** id, role, capabilities, tools, triggers, produces, consumes.

---

## Work Items

| ID | Title | Status | Type |
|----|-------|--------|------|
| WORK-164 | Agent Cards | Complete | design |

---

## Exit Criteria

- [ ] All agents have structured capability cards
- [ ] Cards discoverable via infrastructure query (not CLAUDE.md lookup)
- [ ] Schema defined: id, role, capabilities, tools, triggers, produces, consumes

---

## Dependencies

| Direction | Target | Reason |
|-----------|--------|--------|
| None | - | No inbound or outbound dependencies |

---

## References

- @.claude/haios/epochs/E2_8/arcs/discover/ARC.md (parent arc)
- @.claude/haios/epochs/E2_8/EPOCH.md (parent epoch)
- Memory: 85154, 85210 (agents not discoverable), 85476 (capability card query tool)
