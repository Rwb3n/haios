# generated: 2026-02-14
# System Auto: last updated on: 2026-02-14T14:40:00
# Arc: Discoverability

## Definition

**Arc ID:** discoverability
**Epoch:** E2.6
**Theme:** Infrastructure for agent discovery of skills, recipes, commands, agents, templates
**Status:** Complete

---

## Purpose

The agent must find what it needs through infrastructure, not memorized paths. Investigation (WORK-020, S368) revealed **151 entry points** (87 recipes, 34 skills, 19 commands, 11 agents) with a three-tier architecture already implicit but unenforced. Claude Code plugin system already auto-discovers commands, skills, and agents — the main gap is recipe visibility (agents shouldn't call recipes directly) and intent-based matching (solved by capability cards).

---

## Requirements Implemented

| Requirement | Description |
|-------------|-------------|
| REQ-DISCOVER-001 | All entry points inventoried and categorized |
| REQ-DISCOVER-002 | Three-tier entry point model (commands, skills, recipes) |
| REQ-DISCOVER-003 | Agent discovers capabilities via infrastructure, not CLAUDE.md |

---

## Chapters

| CH-ID | Title | Work Items | Requirements | Dependencies | Status |
|-------|-------|------------|--------------|--------------|--------|
| CH-032 | EntryPointInventory | WORK-020 (EXPLORE) | REQ-DISCOVER-001 | None | Complete (S368) |
| CH-033 | ThreeTierArchitecture | WORK-020 (HYPOTHESIZE/VALIDATE) | REQ-DISCOVER-002 | CH-032 | Complete (S368) |
| CH-034 | DiscoveryMechanism | WORK-020 (CONCLUDE) + spawn | REQ-DISCOVER-003 | CH-033 | Complete (S368) |

---

## Exit Criteria

- [x] All 151 entry points inventoried with tier assignment (WORK-020 S368: 87 recipes, 34 skills, 19 commands, 11 agents)
- [x] Friction map of overlaps and gaps completed (WORK-020 S368: 7 friction points documented)
- [x] Three-tier model defined with clear boundaries (WORK-020 S368: Tier 1 commands, Tier 2 skills+agents, Tier 3 recipes)
- [x] Discovery mechanism designed (WORK-020 S368: Claude Code auto-discovery + capability cards + recipe hiding)
- [x] Consolidation work spawned (WORK-148 S382: stubs removed; E2.7 deferred items documented in ARC spawn table)

---

## Spawn Deferral Policy

Investigation outputs (WORK-020) that don't directly serve E2.6 exit criteria are deferred to E2.7 Composability. The investigation designs; implementation follows in later epochs.

---

## Spawned Work (from WORK-020)

| ID | Title | Type | Deferred To |
|----|-------|------|-------------|
| WORK-148 | Remove Stub and Deprecated Skills | cleanup | E2.6 |
| WORK-149 | Three-Tier Entry Point Architecture ADR | design | E2.6 |
| TBD | Recipe Consolidation (18 orphans) | implementation | E2.7 |
| TBD | Skill Categorization Frontmatter | design | E2.7 |
| TBD | docs/README.md Refresh | cleanup | E2.6 |

---

## References

- @docs/work/active/WORK-020/WORK.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-DISCOVER-*)
- Memory: 85302, 85303 (WORK-020 findings)
