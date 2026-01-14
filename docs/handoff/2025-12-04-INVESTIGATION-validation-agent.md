---
template: handoff
version: 1.0
type: investigation
date: 2025-12-04
author: Hephaestus (Builder)
status: ready
priority: high
estimated_effort: 6 hours
source: "@docs/libraries/research-2025-12-04/02-arxiv-2407-13578.md"
generated: 2025-12-04
last_updated: 2025-12-04T21:05:32
---

# Investigation Handoff: Validation Agent for Epoch Promotion

## Objective

Design a Validation Agent that gates epoch promotion using reliability metrics (Factuality, Consistency). Prevents publishing low-quality knowledge to Epoch N+1.

---

## Background

**Source:** https://arxiv.org/abs/2407.13578 - "How Reliable are LLMs as Knowledge Bases?"

**Key Concepts:**
- **Factuality:** Accuracy on seen vs unseen data
- **Consistency:** Stability of answers across question variations
- **NCCR (Net Consistently Correct Rate):** Primary quality metric
- **IUR (Uninformative Rate):** High IUR on unseen data = good (prevents hallucination)

**Current State:**
- HAIOS has no validation gate for refined knowledge
- Greek Triad classification exists but no reliability scoring
- Epoch promotion is implicit (no quality threshold)

---

## Investigation Spec

### 1. Metrics Deep-Dive

**Questions to Answer:**
- [ ] How is NCCR calculated exactly? (formula, edge cases)
- [ ] How is IUR calculated? What counts as "uninformative"?
- [ ] What thresholds are used in the paper for "reliable"?
- [ ] How to adapt these metrics for HAIOS data (not QA pairs)?

**Actions:**
- Read full paper methodology section
- Extract mathematical formulas for NCCR/IUR
- Map to HAIOS data structures (concepts, entities, strategies)

### 2. Consistency Check Design

**Questions to Answer:**
- [ ] How to generate "distractor" questions for HAIOS knowledge?
- [ ] What constitutes a "variation" of a query for consistency?
- [ ] How many variations needed for statistical significance?
- [ ] Can we use existing LLM to generate distractors?

**Pattern from Paper:**
```
Original: "What is the capital of France?"
Variations:
  - "France's capital city is?"
  - "Which city serves as France's capital?"
Distractors: [Paris, London, Berlin, Rome]
Consistency = Agreement rate across variations
```

**HAIOS Adaptation:**
```
Original Concept: "Memory is ENGINE not DESTINATION"
Variations:
  - "What is the role of memory in HAIOS?"
  - "How should memory be characterized?"
Test: Does the system return consistent answers?
```

### 3. Factuality Check Design

**Questions to Answer:**
- [ ] How to define "seen" vs "unseen" knowledge for HAIOS?
- [ ] What is the ground truth for factuality? (source documents?)
- [ ] How to handle doxa (opinions) which have no ground truth?

**HAIOS Adaptation:**
- **Seen:** Concepts extracted from ingested artifacts
- **Unseen:** Queries about topics not in the corpus
- **Ground Truth:** Source file content (provenance chain)

### 4. Validation Agent Architecture

**Proposed Flow:**
```
Refined Knowledge (Epoch N candidate)
    |
    v
[Consistency Check]
    - Generate variations
    - Query against candidate
    - Calculate NCCR
    |
    v
[Factuality Check]
    - Sample seen knowledge
    - Verify against source
    - Calculate accuracy
    |
    v
[Unseen Probe]
    - Generate unseen queries
    - Verify "I don't know" responses
    - Calculate IUR
    |
    v
[Decision Gate]
    - NCCR > threshold?
    - IUR > threshold?
    - -> PROMOTE or REJECT
```

### 5. Integration Points

**Where Validation Agent connects to HAIOS:**

| Component | Integration |
|-----------|-------------|
| `haios_etl/refinement.py` | Post-refinement validation hook |
| `haios-memory-mcp` | Expose validation as tool |
| Epoch management | Gate for `epoch_promote()` function |
| `concepts` table | Add `reliability_score` column? |

---

## Acceptance Criteria

- [ ] NCCR/IUR formulas documented with HAIOS adaptations
- [ ] Consistency check design spec (distractor generation, variation patterns)
- [ ] Factuality check design spec (ground truth source, sampling)
- [ ] Validation Agent architecture diagram
- [ ] Threshold recommendations (with rationale)
- [ ] Prototype pseudocode for core validation loop

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| Metrics don't map to HAIOS data | Start with simpler consistency checks, iterate |
| Validation too slow (LLM calls) | Batch processing, sampling strategies |
| Thresholds too strict | Make configurable, start permissive |
| Distractor generation poor | Use structured prompts, manual review first |

---

## Key References

- @docs/libraries/research-2025-12-04/02-arxiv-2407-13578.md
- @docs/libraries/research-2025-12-04/SUMMARY-output-pipeline.md
- https://arxiv.org/abs/2407.13578
- @haios_etl/refinement.py
- @docs/vision/2025-11-30-VISION-INTERPRETATION-SESSION.md (reliability = utility)

---

## Output Expected

Investigation report containing:
1. NCCR/IUR metric specifications (HAIOS-adapted)
2. Consistency check algorithm design
3. Factuality check algorithm design
4. Validation Agent architecture spec
5. Recommended thresholds and configuration
6. Implementation recommendation (complexity vs value)

---

## Key Quote (Why This Matters)

> "For unseen knowledge, a factual LLM should demonstrate a high uninformative rate."

Translation for HAIOS: If we don't know, we should say "doxa" (opinion) or "unknown", not hallucinate "episteme" (fact). This is the core of the Greek Triad integrity.
