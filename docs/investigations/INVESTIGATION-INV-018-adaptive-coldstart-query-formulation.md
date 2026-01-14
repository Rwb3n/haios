---
template: investigation
status: complete
date: 2025-12-19
backlog_id: INV-018
title: "Investigation: Adaptive Coldstart Query Formulation"
author: Hephaestus
session: 87
lifecycle_phase: conclude
memory_refs: []
spawned_by: memory_self_critique
related: [E2-078, ADR-037]
milestone: M3-Cycles
version: "1.1"
generated: 2025-12-22
last_updated: 2025-12-22T22:39:13
---
# Investigation: Adaptive Coldstart Query Formulation

@docs/README.md
@docs/epistemic_state.md
@.claude/commands/coldstart.md

---

## Context

During Session 87 coldstart, the memory retrieval returned a self-critique:

> "Static query 'HAIOS session context initialization' doesn't adapt"
> (Memory ID: 71367, 71325)

The current `/coldstart` command uses a hardcoded query regardless of:
- What the previous session worked on
- What backlog items are active
- What milestone is current
- What the session_delta indicates

This is a meta-cognitive gap: the memory system identified its own retrieval limitation.

---

## Objective

Determine how to make coldstart memory retrieval context-aware, returning strategies and learnings relevant to the likely work of the upcoming session.

---

## Scope

### In Scope
- Current coldstart query mechanism
- session_delta data available at coldstart
- Recent checkpoint backlog_ids
- Retrieval mode options (ADR-037)
- Query formulation strategies

### Out of Scope
- Changes to memory schema
- Epoch 3 memory-v2 architecture
- Synthesis algorithm changes

---

## Hypotheses

1. **H1:** Using recent checkpoint backlog_ids to formulate query will yield more relevant strategies
2. **H2:** session_delta.added items indicate likely work focus, should weight query
3. **H3:** Milestone context (e.g., "M3-Cycles implementation") is more useful than generic "session context"
4. **H4:** A two-stage retrieval (generic + specific) might capture both broad context and focused strategies

---

## Investigation Steps

1. [ ] Analyze current coldstart.md query formulation
2. [ ] Review what data is available before memory query (slim status, checkpoint frontmatter)
3. [ ] Examine ADR-037 retrieval modes for applicable enhancements
4. [ ] Prototype dynamic query generation approaches
5. [ ] Compare retrieval quality: static vs. adaptive queries
6. [ ] Document recommendation

---

## Findings

### SUPERSEDED (Session 101)

**This investigation was superseded by E2-083 implementation without formal investigation.**

The `/coldstart` command now implements adaptive query formulation:

1. **H1 IMPLEMENTED:** Uses checkpoint `backlog_ids` in query formulation
2. **H2 IMPLEMENTED:** References `session_delta` from haios-status-slim.json
3. **H3 IMPLEMENTED:** Builds targeted query: `"learnings and strategies for {backlog_ids} {focus}"`
4. **H4 PARTIAL:** Uses `mode='session_recovery'` from ADR-037

**Evidence (coldstart.md lines 25-29):**
```markdown
6. **Context Retrieval (E2-083: Targeted Query):**
   - Extract focus/theme from the latest checkpoint title
   - Build targeted query using extracted `backlog_ids` and focus
   - Query `memory_search_with_experience` with this targeted query and `mode='session_recovery'`
```

**Conclusion:** Investigation objectives achieved through implementation. No further investigation needed.

---

## Spawned Work Items

- [x] E2-083: Proactive Memory Query - **IMPLEMENTED** (supersedes this investigation)

---

## Expected Deliverables

- [x] Investigation document (this file)
- [ ] Findings with retrieval quality comparison
- [ ] Recommendation (implement vs. defer)
- [ ] Memory storage of learnings

---

## References

- Memory IDs 71367, 71325 (self-critique concepts)
- `.claude/commands/coldstart.md` - current implementation
- ADR-037 - Hybrid Retrieval Architecture
- E2-078 - Coldstart work delta (session_delta)

---
