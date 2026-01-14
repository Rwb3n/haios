# generated: 2025-12-04
# System Auto: last updated on: 2025-12-04 23:34:49
# TRD-VALIDATION-AGENT-v1
## Technical Requirements Document: Validation Agent

> **Progressive Disclosure:** [Quick Reference](#quick-reference) -> [Architecture](#architecture) -> [Implementation](#implementation)
>
> **Navigation:** [Validation Report](../reports/2025-12-04-REPORT-validation-agent.md) | [Schema](memory_db_schema_v3.sql) | [MCP Server](../../haios_etl/mcp_server.py)

---

## Quick Reference

| Attribute | Value |
|-----------|-------|
| **Purpose** | Gate epoch promotion via quality metrics |
| **Metrics** | NCCR (consistency on known facts), IUR (refusal of unknowns) |
| **Thresholds** | NCCR > 0.8, IUR > 0.9 |
| **Approach** | LLM + Embeddings hybrid |
| **Dependencies** | @haios_etl/retrieval.py, @haios_etl/extraction.py, Gemini API |

---

## 1. Problem Statement

Before promoting a memory epoch, we need to verify:
1. **Factual Consistency** - Does the system answer known facts correctly and consistently?
2. **Hallucination Prevention** - Does the system refuse to answer questions outside its knowledge?

Without validation, epochs may contain:
- Corrupted or inconsistent knowledge
- Overconfident answers to unknown questions
- Degraded retrieval quality

---

## 2. Metrics Definition

### 2.1 NCCR (Net Consistently Correct Rate)

**Purpose:** Measure consistency on "seen" facts from the corpus.

**Formula:**
```
NCCR = (Consistent_Correct - Consistent_Wrong) / Total_Seen_Queries
```

**Definitions:**
- **Consistent_Correct**: All 3 question variations answered correctly
- **Consistent_Wrong**: All 3 question variations answered incorrectly
- **Inconsistent**: Mixed correct/incorrect across variations

**Target:** NCCR > 0.8

### 2.2 IUR (Inconsistent/Uninformative Rate)

**Purpose:** Measure appropriate refusal on "unseen" (out-of-corpus) questions.

**Formula:**
```
IUR = (Uninformative + Inconsistent) / Total_Unseen_Queries
```

**Definitions:**
- **Uninformative**: System responds "I don't know" / "Not in memory" / low confidence
- **Inconsistent**: System gives contradictory answers across variations
- **Hallucination**: System confidently answers incorrectly (BAD)

**Target:** IUR > 0.9 (we WANT high refusal of unknowns)

---

## 3. Architecture

### 3.1 Hybrid LLM + Embeddings Approach

```
┌─────────────────────────────────────────────────────────────────┐
│                     VALIDATION PIPELINE                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────┐    ┌─────────────┐         │
│  │   SAMPLE    │───▶│   GENERATE  │───▶│    PROBE    │         │
│  │  Concepts   │    │  Questions  │    │   Memory    │         │
│  │   (N=50)    │    │   (LLM)     │    │   Search    │         │
│  └─────────────┘    └─────────────┘    └─────────────┘         │
│                                               │                 │
│                                               ▼                 │
│                     ┌─────────────────────────────────┐         │
│                     │      VERIFY ANSWERS             │         │
│                     │  ┌───────────┐  ┌───────────┐  │         │
│                     │  │ Embedding │  │ LLM-Judge │  │         │
│                     │  │ Similarity│─▶│ (if 0.6-  │  │         │
│                     │  │  Score    │  │   0.85)   │  │         │
│                     │  └───────────┘  └───────────┘  │         │
│                     └─────────────────────────────────┘         │
│                                               │                 │
│                                               ▼                 │
│                     ┌─────────────────────────────────┐         │
│                     │         SCORE & GATE            │         │
│                     │  NCCR > 0.8 AND IUR > 0.9?      │         │
│                     │  ┌─────┐          ┌──────┐      │         │
│                     │  │PASS │──────────│FAIL  │      │         │
│                     │  │Epoch│          │Refine│      │         │
│                     │  └─────┘          └──────┘      │         │
│                     └─────────────────────────────────┘         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 3.2 Component Roles

| Component | Technology | Role |
|-----------|------------|------|
| Question Generator | Gemini LLM | Convert concept -> 3 question variations |
| Memory Probe | `memory_search_with_experience()` | Query the system under test |
| Similarity Scorer | text-embedding-004 | Fast semantic comparison |
| LLM Judge | Gemini LLM | Nuanced answer verification |
| Unseen Generator | Gemini LLM | Generate out-of-corpus questions |

---

## 4. Design Decisions (Require Approval)

### DD-V01: Question Generation Method
**Decision:** Use LLM to generate natural question variations from concept content.

**Rationale:**
- Template-based questions are unnatural and easy to game
- LLM generates diverse phrasings that test true understanding
- Cost is acceptable (50 concepts x 3 variations = 150 LLM calls)

**Alternative Rejected:** Template-based (`"What is {noun}?"`) - too predictable.

### DD-V02: Verification Strategy (Hybrid)
**Decision:** Use embeddings for fast scoring, LLM-as-judge for ambiguous cases.

**Flow:**
```python
similarity = cosine(answer_embedding, ground_truth_embedding)
if similarity > 0.85:
    return "Correct"
elif similarity < 0.6:
    return "Wrong"
else:
    # Ambiguous - use LLM judgment
    return llm_judge(answer, ground_truth)
```

**Rationale:**
- Embeddings are cheap and fast (covers 70% of cases)
- LLM judgment for edge cases ensures accuracy
- Reduces API costs by ~70% vs. pure LLM approach

### DD-V03: Unseen Query Generation
**Decision:** LLM generates plausible but out-of-corpus questions.

**Prompt:**
```
Given this is a knowledge base about AI agent development and HAIOS architecture,
generate 50 questions that are:
1. Plausible (sound like real questions someone might ask)
2. Definitely NOT answerable from the corpus
3. Diverse (cover different domains: cooking, sports, history, etc.)
```

**Rationale:**
- Curated lists are brittle and may overlap with corpus
- LLM can generate domain-aware "negative examples"

### DD-V04: Test Set Size
**Decision:** 50 seen + 50 unseen queries (100 total per validation run).

**Statistical Justification:**
- 50 samples gives 95% CI of +/- 14% for proportion estimates
- Sufficient for epoch gating (not academic publication)
- Can increase to 100+ for production hardening

### DD-V05: Consistency Threshold
**Decision:** Require 3/3 correct for "Consistent_Correct".

**Rationale:**
- Strict threshold catches subtle inconsistencies
- 2/3 would be "Inconsistent" (still counts against NCCR)

---

## 5. Implementation Specification

### 5.1 Data Structures

```python
@dataclass
class ValidationConfig:
    seen_sample_size: int = 50
    unseen_sample_size: int = 50
    variations_per_concept: int = 3
    similarity_high_threshold: float = 0.85
    similarity_low_threshold: float = 0.60
    nccr_threshold: float = 0.80
    iur_threshold: float = 0.90

@dataclass
class QuestionSet:
    concept_id: int
    ground_truth: str
    variations: List[str]  # 3 question phrasings

@dataclass
class ProbeResult:
    question: str
    answer: str
    answer_embedding: List[float]
    similarity_score: float
    llm_judgment: Optional[str]  # "Correct" | "Wrong" | None
    final_verdict: str  # "Correct" | "Wrong"

@dataclass
class ValidationReport:
    epoch_id: str
    timestamp: str
    nccr: float
    iur: float
    passed: bool
    seen_results: List[Dict]
    unseen_results: List[Dict]
    config: ValidationConfig
```

### 5.2 Module Structure

```
haios_etl/
├── validation/
│   ├── __init__.py
│   ├── generator.py      # Question generation (LLM)
│   ├── prober.py         # Memory search probe
│   ├── verifier.py       # Embedding + LLM verification
│   ├── scorer.py         # NCCR/IUR calculation
│   └── agent.py          # ValidationAgent orchestrator
```

### 5.3 Key Functions

```python
# generator.py
def generate_question_variations(concept_content: str, n: int = 3) -> List[str]:
    """Use LLM to generate n question phrasings for a concept."""

def generate_unseen_questions(corpus_summary: str, n: int = 50) -> List[str]:
    """Use LLM to generate out-of-corpus questions."""

# verifier.py
def verify_answer(answer: str, ground_truth: str, config: ValidationConfig) -> ProbeResult:
    """Hybrid verification: embeddings first, LLM if ambiguous."""

# scorer.py
def calculate_nccr(seen_results: List[ProbeResult]) -> float:
    """Calculate Net Consistently Correct Rate."""

def calculate_iur(unseen_results: List[ProbeResult]) -> float:
    """Calculate Inconsistent/Uninformative Rate."""

# agent.py
class ValidationAgent:
    def validate_epoch(self, epoch_id: str) -> ValidationReport:
        """Run full validation pipeline and return report."""
```

---

## 6. Integration Points

### 6.1 Trigger
- Runs after `synthesis.py` completes
- Or manually via CLI: `python -m haios_etl.cli validate --epoch <id>`

### 6.2 Output
- `validation_report.json` stored in epoch artifacts
- Summary printed to CLI
- If FAIL: blocks `publish_epoch` command

### 6.3 MCP Tool (Future)
```python
@mcp.tool()
def validate_epoch(epoch_id: str, dry_run: bool = False) -> str:
    """Run validation on an epoch candidate."""
```

---

## 7. Success Criteria

| Criterion | Target |
|-----------|--------|
| NCCR on test epoch | > 0.8 |
| IUR on test epoch | > 0.9 |
| Validation runtime | < 5 minutes (100 queries) |
| API cost per run | < $0.50 |
| False positive rate | < 5% (verified manually on 20 samples) |

---

## 8. Risks & Mitigations

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LLM judgment inconsistency | Medium | Medium | Use temperature=0, structured output |
| Embedding similarity threshold wrong | Medium | High | Tune on held-out validation set |
| Unseen questions overlap corpus | Low | Medium | LLM prompt includes corpus summary |
| API cost overrun | Low | Low | Batch embeddings, cache questions |

---

## 9. Open Questions (For Operator)

1. **Shadow Mode Duration**: How many epochs to run in shadow mode before enabling blocking?
2. **Failure Action**: On validation failure, auto-trigger refinement or require manual intervention?
3. **Metrics Storage**: Store detailed probe results or just aggregate scores?

---

## 10. References

- @docs/reports/2025-12-04-REPORT-validation-agent.md - Original investigation
- @haios_etl/retrieval.py - Memory search implementation
- @haios_etl/extraction.py - Embedding generation
- @docs/specs/memory_db_schema_v3.sql - Database schema

---

**STATUS: DRAFT - Awaiting Operator Approval**
**Author:** Hephaestus (Builder)
**Date:** 2025-12-04
