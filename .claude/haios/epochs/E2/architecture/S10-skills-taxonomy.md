# generated: 2026-01-06
# System Auto: last updated on: 2026-01-06T22:02:37
# Section 10: Skills Taxonomy

Generated: 2025-12-30 (Session 151, INV-052)
Migrated: 2026-01-06 (Session 179)
Purpose: Categorize skills by type, invocation pattern, and pressure dynamics
Status: ACTIVE

---

## Skill Categories

### Category 1: Cycles (7+)

Multi-phase prompt sequences with gates. Alternate between volumous (explore) and tight (commit) phases.

| Skill | Phases | Node Binding | Pressure Pattern |
|-------|--------|--------------|------------------|
| `ground-cycle` | PROVENANCE→ARCHITECTURE→MEMORY→CONTEXT MAP | (pre-phase) | [MAY]→[MAY]→[MAY]→[MUST] |
| `implementation-cycle` | PLAN→DO→CHECK→DONE→CHAIN | implement | [MUST]→[MAY]→[MUST]→[MUST]→[MUST] |
| `investigation-cycle` | HYPOTHESIZE→EXPLORE→CONCLUDE→CHAIN | discovery | [MAY]→[MAY]→[MUST]→[MUST] |
| `close-work-cycle` | VALIDATE→OBSERVE→ARCHIVE→MEMORY→CHAIN | close | [MUST]→[MAY]→[MUST]→[MUST]→[MUST] |
| `work-creation-cycle` | VERIFY→POPULATE→READY→CHAIN | backlog | [MUST]→[MAY]→[MUST]→[MUST] |
| `checkpoint-cycle` | SCAFFOLD→FILL→VERIFY→CAPTURE→COMMIT | (none) | [MUST]→[MAY]→[MUST]→[MAY]→[MUST] |
| `observation-triage-cycle` | SCAN→TRIAGE→PROMOTE | (none) | [MAY]→[MAY]→[MUST] |
| `plan-authoring-cycle` | AMBIGUITY→ANALYZE→AUTHOR→VALIDATE→CHAIN | plan | [MAY]→[MAY]→[MAY]→[MUST]→[MUST] |

### Category 2: Bridges (3)

Blocking validators. Binary pass/fail. Always tight pressure [MUST].

| Skill | Purpose | Invoked By |
|-------|---------|------------|
| `plan-validation-cycle` | Pre-DO plan quality check | implementation-cycle PLAN |
| `design-review-validation` | During-DO design alignment | implementation-cycle DO |
| `dod-validation-cycle` | Post-DO DoD criteria check | close-work-cycle entry |

### Category 3: Utilities (4+)

One-shot capabilities. Pressure varies by purpose.

| Skill | Purpose | Pressure |
|-------|---------|----------|
| `memory-agent` | Strategy retrieval | [MAY] - exploratory |
| `audit` | Find gaps, drift | [MAY] - exploratory |
| `schema-ref` | Database schema lookup | [MUST] - precise answer |
| `extract-content` | Entity/concept extraction | [MUST] - structured output |
| `routing-gate` | Work type routing | [MUST] - decision point |

---

## Phase Categories (from S2E)

All cycles follow a semantic structure:

```
PREPARATION → EXECUTION → VALIDATION → PERSISTENCE → ROUTING
   [MAY]        [MAY]        [MUST]        [MUST]       [MUST]
  (inhale)     (inhale)     (exhale)      (exhale)     (exhale)
```

| Category | Phase Examples | Pressure | Breath |
|----------|---------------|----------|--------|
| Preparation | PLAN, HYPOTHESIZE, VERIFY, ANALYZE, SCAFFOLD, SCAN | [MAY] | Inhale |
| Execution | DO, EXPLORE, POPULATE, AUTHOR, FILL, TRIAGE | [MAY] | Inhale |
| Validation | CHECK, VERIFY, VALIDATE | [MUST] | Exhale |
| Persistence | DONE, CONCLUDE, ARCHIVE, MEMORY, CAPTURE, COMMIT, PROMOTE | [MUST] | Exhale |
| Routing | CHAIN | [MUST] | Exhale |

**Key insight:** Early phases are volumous (space to explore). Late phases are tight (commit or fail).

---

## Memory Integration by Phase

| Phase Type | Memory Action | Example |
|------------|---------------|---------|
| Preparation | Query (retrieve prior) | HYPOTHESIZE queries for similar investigations |
| Execution | Query (get strategies) | DO queries for implementation patterns |
| Persistence | Store (capture learning) | CONCLUDE stores findings |
| Routing | None | CHAIN doesn't use memory |

---

## Bridge vs Cycle vs Utility

| Aspect | Cycle | Bridge | Utility |
|--------|-------|--------|---------|
| Phases | Multiple (3-5) | Single-purpose | Stateless |
| Node binding | Yes | No | No |
| CHAIN phase | Yes | No | No |
| Standalone | Yes | No (invoked by cycle) | Yes |
| Pressure pattern | Mixed [MAY]→[MUST] | Always [MUST] | Varies |

---

## Connection to S20 (Pressure Dynamics)

The skill taxonomy IS the pressure dynamics made concrete:

- **Cycles** = breath cycles (inhale phases → exhale phases)
- **Bridges** = exhale-only (gates, binary)
- **Utilities** = single breath (one pressure type per invocation)

When decomposing monolithic skills (S19), ensure each new skill has clear pressure:
- Exploration skills: [MAY]
- Validation skills: [MUST]
- Don't mix - that's what caused observation capture to fail

---

## Related

- S19: Skill and Work Item Unification (decomposition)
- S20: Pressure Dynamics (the theory this taxonomy implements)
- S21: Cognitive Notation (how to annotate pressure)
- INV-052/SECTION-10: Original source

---

*Migrated from INV-052, enhanced with pressure dynamics (Session 179)*
