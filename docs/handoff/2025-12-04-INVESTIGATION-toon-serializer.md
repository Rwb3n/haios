---
template: handoff
version: 1.0
type: investigation
date: 2025-12-04
author: Hephaestus (Builder)
status: ready
priority: high
estimated_effort: 4 hours
source: "@docs/libraries/research-2025-12-04/06-toon-format.md"
generated: 2025-12-04
last_updated: 2025-12-04T21:04:53
---

# Investigation Handoff: TOON Serializer for Output Pipeline

## Objective

Deep-dive into Token-Oriented Object Notation (TOON) format and design a Python serializer for HAIOS ReasoningBank output. Goal: ~40% token savings on epoch artifacts.

---

## Background

**Source:** https://github.com/toon-format/toon

**Key Claims:**
- ~40% token savings vs JSON
- +4% retrieval accuracy
- YAML-like structure with CSV-style tabular arrays
- Schema-aware serialization

**Current State:**
- HAIOS outputs concepts/entities as JSON or raw text
- No token optimization for context injection
- ReasoningBank strategies not yet serialized

---

## Investigation Spec

### 1. Format Deep-Dive

**Questions to Answer:**
- [ ] What is the exact TOON grammar/syntax?
- [ ] How does tabular array serialization work?
- [ ] What are the edge cases (nested objects, special characters, nulls)?
- [ ] Does TOON have a formal spec or just examples?

**Actions:**
- Read full TOON specification from GitHub repo
- Analyze existing JS/TS SDK implementation
- Document grammar rules for Python port

### 2. Token Efficiency Validation

**Questions to Answer:**
- [ ] How is the 40% savings calculated? (which tokenizer?)
- [ ] Does the savings hold for HAIOS data shapes?
- [ ] What is the breakeven point (when is JSON actually better)?

**Actions:**
- Create test dataset from existing HAIOS concepts (sample 100)
- Serialize to JSON, YAML, and manual TOON
- Count tokens using `tiktoken` (cl100k_base) and Gemini tokenizer
- Report actual savings percentage

### 3. Python Implementation Design

**Questions to Answer:**
- [ ] Can we port the JS SDK or write from scratch?
- [ ] What Python patterns fit best (dataclasses? pydantic?)
- [ ] How to handle schema inference vs explicit schemas?

**Deliverables:**
```python
# Target API
from haios_etl.toon import TOONSerializer

serializer = TOONSerializer()
toon_str = serializer.dumps(reasoning_bank_strategies)
data = serializer.loads(toon_str)
```

### 4. Integration Points

**Where TOON connects to HAIOS:**

| Component | Integration |
|-----------|-------------|
| `haios_etl/refinement.py` | Output format for refined concepts |
| `haios-memory-mcp` | Context injection format |
| Epoch artifacts | `strategies.toon` file in release |

**Schema mapping:**
- `concepts` table -> TOON tabular array
- `entities` table -> TOON tabular array
- ReasoningBank strategies -> TOON nested structure

---

## Acceptance Criteria

- [ ] TOON grammar documented for Python implementation
- [ ] Token savings validated on HAIOS data (target: >30%)
- [ ] Python serializer design spec (API, error handling, schema)
- [ ] Integration plan with existing `haios_etl` modules
- [ ] Prototype code (even if incomplete) demonstrating core serialization

---

## Risks & Mitigations

| Risk | Mitigation |
|------|------------|
| No Python SDK exists | Port from JS or write minimal implementation |
| Format not stable | Pin to specific commit/version |
| Savings don't materialize | Fallback to optimized JSON (strip whitespace, short keys) |

---

## Key References

- @docs/libraries/research-2025-12-04/06-toon-format.md
- @docs/libraries/research-2025-12-04/SUMMARY-output-pipeline.md
- https://github.com/toon-format/toon
- @haios_etl/refinement.py

---

## Output Expected

Investigation report containing:
1. TOON grammar specification (Python-readable)
2. Token efficiency benchmark results
3. Python serializer design document
4. Implementation recommendation (build vs skip)
