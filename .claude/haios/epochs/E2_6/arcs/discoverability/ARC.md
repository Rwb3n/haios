# generated: 2026-02-14
# System Auto: last updated on: 2026-02-14T12:50:00
# Arc: Discoverability

## Definition

**Arc ID:** discoverability
**Epoch:** E2.6
**Theme:** Infrastructure for agent discovery of skills, recipes, commands, agents, templates
**Status:** Planning

---

## Purpose

The agent must find what it needs through infrastructure, not memorized paths. Currently 125+ entry points (77 recipes, 19 skills, 20 commands, 9 agents) exist with no unified discovery mechanism. Agents rely on CLAUDE.md hardcoding to know what tools are available.

---

## Requirements Implemented

| Requirement | Description |
|-------------|-------------|
| REQ-DISCOVER-001 | All entry points inventoried and categorized |
| REQ-DISCOVER-002 | Three-tier entry point model (commands, skills, recipes) |
| REQ-DISCOVER-003 | Agent discovers capabilities via infrastructure, not CLAUDE.md |

---

## Chapters

| CH-ID | Title | Work Items | Requirements | Dependencies |
|-------|-------|------------|--------------|--------------|
| CH-032 | EntryPointInventory | WORK-020 (EXPLORE) | REQ-DISCOVER-001 | None |
| CH-033 | ThreeTierArchitecture | WORK-020 (HYPOTHESIZE/VALIDATE) | REQ-DISCOVER-002 | CH-032 |
| CH-034 | DiscoveryMechanism | WORK-020 (CONCLUDE) + spawn | REQ-DISCOVER-003 | CH-033 |

---

## Exit Criteria

- [ ] All 125+ entry points inventoried with tier assignment
- [ ] Friction map of overlaps and gaps completed
- [ ] Three-tier model defined with clear boundaries
- [ ] Discovery mechanism designed (agent can query capabilities)
- [ ] Consolidation work spawned (deferred to E2.7+ per spawn-deferral policy)

---

## Spawn Deferral Policy

Investigation outputs (WORK-020) that don't directly serve E2.6 exit criteria are deferred to E2.7 Composability. The investigation designs; implementation follows in later epochs.

---

## References

- @docs/work/active/WORK-020/WORK.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-DISCOVER-*)
