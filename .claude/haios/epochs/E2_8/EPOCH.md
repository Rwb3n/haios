# generated: 2026-02-14
# System Auto: last updated on: 2026-02-14T01:20:00
# Epoch 2.8: Agent UX

## L4 Object Definition

**Epoch ID:** E2.8
**Name:** Agent UX
**Status:** Future
**Prior:** E2.7 (Composability)
**Next:** E2.9 (Governance)

---

## Purpose

The headline epoch. With foundations solid (E2.6) and building blocks composable (E2.7), now make the agent experience efficient. Agents spend tokens on work, not bookkeeping.

**The Mission:**
```
The agent should not read what it can call.
The agent should not search what it can query.
The agent should not guess what it can discover.
```

**Depends on E2.7:** Composable engine functions and flat metadata are prerequisites. Without them, agent UX improvements are band-aids.

---

## What We Carry Forward

### The Core Problem (E2.5 S339 Finding)
Governance works but costs ~40% of tokens. Ceremony overhead is disproportionate for small work items.

### From E2.7 (Composability)
- Flat metadata queryable via engine functions
- Status cascades automatically
- Typed lifecycle assets composable
- Recipes rationalized and documented

### From E2.5 Trend Analysis
| Trend | Evidence Count | Relevance |
|-------|---------------|-----------|
| Ceremony overhead disproportionate | 9+ memory entries | CRITICAL |
| Coldstart overhead for housekeeping | 3 memory entries | HIGH |
| Batch fixes avoid ceremony overhead | 4+ memory entries | HIGH |

### Inspiration: A2A Agent Cards + Dragon Quest Classes
Each agent has a stateless identity card: role, capabilities, tools, triggers, what it produces. Agents discover each other through infrastructure, not hardcoded knowledge. (Google A2A Protocol, operator vision S365)

---

## Scope

### Work Items Assigned

| ID | Title | Theme |
|----|-------|-------|
| WORK-101 | Proportional Governance Design | Right-size ceremony to work item complexity |
| WORK-136 | Checkpoint Pending Staleness | Reduce noise in agent context |

### Anticipated Work

| Theme | Description |
|-------|-------------|
| Lightweight coldstart | Right-size session overhead for housekeeping vs deep work |
| Dynamic ceremony composition | Config-driven ceremonies, not monolithic skill injection (obs-313) |
| Context-efficient contracts | Progressive disclosure in WORK.md / PLAN.md |
| Batch mode | Skip per-item ceremony overhead for batched operations |
| Agent-to-agent discovery | Agents find each other via cards, not CLAUDE.md |

---

## Exit Criteria

- [ ] Governance overhead measurably reduced (target: perceptible improvement over E2.5 baseline)
- [ ] Lightweight coldstart variant exists for housekeeping sessions
- [ ] Ceremonies composable from config (not monolithic skill files)
- [ ] Contracts designed for progressive disclosure (agent reads what it needs, not everything)
- [ ] Batch mode available for trivial operations

---

## Observations Feeding This Epoch

| Source | Key Finding |
|--------|-------------|
| obs-313 | Ceremonies need dynamic composition, not static skills |
| obs-339 | Governance works but expensive, scope inflation biggest risk |
| mem:84332 | ~40% tokens on governance for small items |
| mem:84836 | Coldstart overhead overkill for doc fixes |
| mem:84951 | 12+ ceremony invocations for a single change |

---

## Architecture

- `architecture/breath-architecture-handover.md` — Opinionated vs delegative design, breath metaphor as fractal system pattern. Three open questions on phase transitions. (Operator design session, filed S365)

---

## References

- @.claude/haios/epochs/E2_7/EPOCH.md (prior epoch)
- @.claude/haios/epochs/E2_9/EPOCH.md (next epoch)
- @.claude/haios/epochs/E2_6/retro-synthesis.md (trend analysis)
- @.claude/haios/epochs/E2_8/architecture/breath-architecture-handover.md (breath architecture)
- @docs/work/active/WORK-101/WORK.md (proportional governance)
