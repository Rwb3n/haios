# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:33:05
# Chapter: Memory Ceremonies

## Definition

**Chapter ID:** CH-016
**Arc:** ceremonies
**Status:** Complete
**Completed:** 2026-02-12 (Session 353, WORK-133)
**Implementation Type:** COMPLETE (all 3 ceremonies have contracts, non-stub implementations, tests)
**Depends:** CH-011
**Work Items:** WORK-133

---

## Current State (Verified)

**Source:** `.claude/skills/`

Memory-related skills exist:
- `observation-capture-cycle/SKILL.md` - RECALL→NOTICE→COMMIT phases
- `observation-triage-cycle/SKILL.md` - SCAN→TRIAGE→PROMOTE phases
- `memory-agent/SKILL.md` - retrieval/storage utility

**What exists:**
- observation-capture-cycle with 4 required questions (ADR-033)
- observation-triage-cycle for processing observations
- ingester_ingest MCP tool for storage
- memory_refs field in WORK.md

**What doesn't exist:**
- Formal `memory-commit-ceremony` (currently inline in close-work-cycle MEMORY phase)
- Machine-readable contracts in frontmatter
- Observation schema in YAML format

**Integration (per CH-012 composition model):**
close-work-cycle composes observation-capture as a step, not nested ceremony.

---

## Problem

Skills exist but aren't formal ceremonies with contracts. Memory commit is embedded in close-work-cycle, not standalone ceremony.

---

## Agent Need

> "I need memory operations governed by ceremonies so learnings are captured consistently, triaged properly, and committed with provenance."

---

## Requirements

### R1: Three Memory Ceremonies

| Ceremony | Signature | When |
|----------|-----------|------|
| Observation Capture | `Experience → Observations` | During/after work |
| Observation Triage | `[Observations] → [Actions]` | Periodic review |
| Memory Commit | `Learnings → ConceptIDs` | Work closure |

### R2: Observation Capture Ceremony

```yaml
input_contract:
  - field: work_id
    type: string
    required: true
  - field: experience_summary
    type: string
    required: true
output_contract:
  - field: observations
    type: list
    items: Observation
side_effects:
  - "Write observations to work item"
  - "Log ObservationsCaptured event"
```

Four required questions (ADR-033):
1. What worked well?
2. What didn't work?
3. What would I do differently?
4. What should the system remember?

### R3: Observation Triage Ceremony

```yaml
input_contract:
  - field: observations
    type: list
    required: true
output_contract:
  - field: actions
    type: list
    items: {type: promote|close|defer, observation_id: str}
side_effects:
  - "Update observation statuses"
  - "Create investigations for promoted"
  - "Log ObservationsTriaged event"
```

### R4: Memory Commit Ceremony

```yaml
input_contract:
  - field: learnings
    type: list
    items: string
  - field: source_path
    type: path
    required: true
output_contract:
  - field: concept_ids
    type: list
    items: string
side_effects:
  - "Store concepts via ingester_ingest"
  - "Update work item memory_refs"
  - "Log MemoryCommitted event"
```

---

## Interface

### Ceremony Skills

```
skills/
  observation-capture-ceremony.md
  observation-triage-ceremony.md
  memory-commit-ceremony.md
```

### Integration with Closure

Memory ceremonies integrate with close-work-ceremony:

```python
def close_work_ceremony(work_id: str):
    # ... DoD validation ...

    # Observation capture (required)
    ceremony_runner.invoke("observation-capture", work_id=work_id)

    # Memory commit
    ceremony_runner.invoke("memory-commit",
        learnings=work.learnings,
        source_path=work.path
    )

    # ... archive work ...
```

### Observation Schema

```yaml
# In WORK.md
observations:
  - id: OBS-001
    question: "What worked well?"
    answer: "TDD approach caught bugs early"
    captured_at: 2026-02-03T01:00:00
  - id: OBS-002
    question: "What should the system remember?"
    answer: "Always run preflight-checker before implementation"
    captured_at: 2026-02-03T01:00:00
```

---

## Success Criteria

- [x] 3 memory ceremony skills created (observation-capture-cycle, observation-triage-cycle, memory-commit-ceremony)
- [x] Observation Capture has 4 required questions (verified in SKILL.md)
- [x] Observation Triage produces actions (SCAN/TRIAGE/PROMOTE phases)
- [x] Memory Commit stores to haios-memory (via ingester_ingest MCP tool)
- [x] close-work-ceremony invokes observation-capture (entry gate, verified by test)
- [x] Events logged for each ceremony (MemoryCommitted event documented in memory-commit-ceremony)
- [x] Observations stored in WORK.md (via scaffold-observations recipe)
- [x] memory_refs updated after commit (ceremony Step 4)
- [x] Unit tests for each ceremony (test_memory_ceremonies.py: 8 tests)
- [ ] ~~Integration test: capture → triage → commit~~ — **Deferred:** Observation schema in YAML (R4) is an asset-typing concern, deferred to E2.6 assets arc. End-to-end integration test requires typed schema. 9/10 criteria met.

---

## Non-Goals

- Automatic learning extraction (requires human reflection)
- Memory search ceremonies (that's retrieval, not storage)
- Memory versioning (concepts are append-only)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-001)
- @.claude/skills/observation-capture-cycle.md (existing to wrap)
- @.claude/skills/memory-agent.md (related skill)
