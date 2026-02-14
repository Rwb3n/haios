# generated: 2026-02-14
# System Auto: last updated on: 2026-02-14T01:30:00
# Epoch 4: Cognitive Memory

## L4 Object Definition

**Epoch ID:** E4
**Name:** Cognitive Memory
**Status:** Future
**Prior:** E3 (TBD)
**Theme:** "The Memory Palace"

---

## Vision

The operating system is built (E2.x). The platform is decided (E3). Now the system learns to know.

**The Mission:**
```
From 85k concepts to structured knowledge.
From ad-hoc retrieval to metamemory.
From reactive to predictive.
```

---

## Three-Paradigm Memory (from epoch3/ specifications)

| Paradigm | Inspiration | Purpose | Current State |
|----------|-------------|---------|---------------|
| Declarative | HINDSIGHT paper | Facts, beliefs, entities, experiences with confidence | Partial (concepts/entities in haios_memory.db) |
| Procedural | ReasoningBank paper | Strategies, skills, failure lessons | Partial (reasoning_traces table) |
| Predictive | FORESIGHT (novel) | World models, self-models, goal networks, metamemory | NOT BUILT |

### FORESIGHT Layer
- **SIMULATE:** Predict outcomes before action
- **INTROSPECT:** Assess own capabilities (Bayesian Competence Calibration)
- **ANTICIPATE:** Flag likely failure modes
- **UPDATE:** Calibrate from results

### Key Concepts (epoch3/ research)
- Bayesian Competence Model (Beta distributions, cold-start priors)
- Metamemory / Feeling-of-Knowing as retrieval confidence
- Failure learning as core signal
- Strategy Compressor (DBSCAN clustering + LLM abstraction)

---

## Known Issues to Address

| Issue | Source | Detail |
|-------|--------|--------|
| Greek Triad taxonomy dead | E2.5 S339 | 0 doxa, 14 episteme (all old), auto-classifier diverged |
| 76% pair-only synthesis | obs-e3-002 | Greedy clustering, threshold too high, no centroid recomputation |
| PRUNE not implemented | obs-e3-001 | 46k raw/untouched concepts, no archival |
| haios_etl migration | E2.3 | "Deprecated" package is still the runtime |
| Retrieval ad-hoc | E2.5 S339 | No structured query patterns, no usage tracking |

---

## Entry Criteria

- [ ] E3 complete (whatever E3 becomes)
- [ ] Platform decision made (CLI vs SDK vs hybrid)
- [ ] haios_etl runtime location resolved

---

## References

- @.claude/haios/epochs/E3/EPOCH.md (prior epoch)
- @epoch3/ (three-paradigm memory specifications)
- @epoch4_vision/ (philosophical foundation, nursery metaphor)
- @haios_etl/ (current memory engine)
- @docs/COGNITIVE_MEMORY_SYSTEM_SPEC.md (~85% implemented)
- @docs/VISION_ANCHOR.md (LangExtract + ReasoningBank)

---

*"First the Chariot, then the Memory Palace."*
