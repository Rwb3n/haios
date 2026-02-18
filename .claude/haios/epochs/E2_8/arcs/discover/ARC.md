# generated: 2026-02-17
# System Auto: last updated on: 2026-02-17T21:00:00
# Arc: Discover

## Definition

**Arc ID:** discover
**Epoch:** E2.8
**Theme:** The agent should not guess what it can discover
**Status:** Planning
**Started:** 2026-02-17 (Session 393)

---

## Purpose

Agent Cards for infrastructure-driven capability discovery. Agents find each other through typed interfaces, not hardcoded knowledge in CLAUDE.md. Ceremonies become infrastructure, not markdown instructions.

**The Discovery Problem:** Agents are currently hardcoded in CLAUDE.md agent table (mem:85154, 85210). There is no way for an agent to discover what other agents exist, what they can do, or when to use them — except by reading documentation. This is the same problem as ceremony overhead: reading instead of querying.

**Inspiration:** Google A2A Agent Cards + Dragon Quest class system (mem:85154, 85155). Each agent has a stateless identity card: role, capabilities, tools, triggers, what it produces. Agents discover each other through infrastructure.

---

## Requirements Implemented

| Requirement | Description |
|-------------|-------------|
| REQ-DISCOVER-002 | Agents discoverable via infrastructure |
| REQ-DISCOVER-003 | Agent capabilities typed and queryable |
| REQ-CEREMONY-001 | Ceremonies are side-effect boundaries |
| REQ-CEREMONY-002 | Ceremony overhead proportional to work complexity |

---

## Chapters

| CH-ID | Title | Work Items | Requirements | Dependencies | Status |
|-------|-------|------------|--------------|--------------|--------|
| CH-063 | AgentCards | New | REQ-DISCOVER-002, REQ-DISCOVER-003 | None | Planning |
| CH-064 | InfrastructureCeremonies | New | REQ-CEREMONY-001, REQ-CEREMONY-002 | None | Planning |

---

## Exit Criteria

- [ ] All agents have structured capability cards discoverable via infrastructure
- [x] Open-epoch-ceremony skill exists (full ceremony loop standardized) (S393)
- [ ] Agents not hardcoded in CLAUDE.md — discovered via infrastructure

---

## Notes

- Open-epoch-ceremony skill was created in S393 — partial exit criterion already met
- Agent cards need a schema: id, role, capabilities, tools, triggers, produces, consumes
- Infrastructure ceremonies = ceremonies that run via hooks/modules, not agent-read SKILL.md
- WORK-143 triage consumer update (mem:85098, 85108) was closed prior to E2.8

---

## References

- @.claude/haios/epochs/E2_8/EPOCH.md (parent epoch)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-DISCOVER-*, REQ-CEREMONY-*)
- Memory: 85154, 85210 (agents not discoverable), 85098/85108 (WORK-143 triage consumer), 85476 (capability card query tool)
