---
template: proposal
version: 1.0
type: extraction-improvement
date: 2025-12-04
author: Hephaestus (Builder)
status: draft
priority: high
references:
  - "@haios_etl/extraction.py"
  - "@output/semantic_duplicates.json"
  - "@docs/checkpoints/2025-12-04-SESSION-26-prototype-consolidation.md"
generated: 2025-12-04
last_updated: 2025-12-04T22:36:49
---

# Proposal: Extraction Type Discrimination Improvement

## Problem Statement

Semantic duplicate detection revealed that identical content is being classified with different concept types. This creates data quality issues that complicate consolidation.

### Evidence

| Pair | Content | Type 1 | Type 2 |
|------|---------|--------|--------|
| 19699/15580 | "Commit: Once a majority of agents..." | Critique | Directive |
| 11790/9428 | "Here is how HAiOS must be positioned..." | Directive | Proposal |
| 32558/32568 | "I'm now implementing the revisions..." | Directive | Decision |

### Root Causes

1. **Overlapping definitions** - Current type definitions are not mutually exclusive
2. **No priority rules** - When multiple types match, random selection occurs
3. **Missing type** - Process descriptions forced into wrong categories
4. **Weak discriminators** - Few-shot examples don't cover edge cases

---

## Current Definitions (extraction.py:77-81)

```
CONCEPTS to extract:
- Directive: Direct commands or instructions
- Critique: Corrective feedback or flaw identification
- Proposal: Plans, solutions, or recommendations
- Decision: Formal decisions
```

### Issues with Current Definitions

| Type | Definition | Problem |
|------|------------|---------|
| Directive | "Direct commands or instructions" | Overlaps with Decision (commands can announce decisions) |
| Critique | "Corrective feedback or flaw identification" | Too narrow - misses analytical evaluations |
| Proposal | "Plans, solutions, or recommendations" | Overlaps with Directive (plans can be prescriptive) |
| Decision | "Formal decisions" | Ambiguous - what makes it "formal"? |

---

## Proposed Improvements

### Option A: Clarified Definitions with Priority Rules

```
CONCEPTS to extract (in priority order - use first matching type):

1. Decision: FORMAL CHOICES announced with explicit decision language
   - Markers: "decided", "decision:", "will adopt", "choosing", "selected"
   - NOT: Status updates ("I'm now doing X" without choice context)

2. Critique: EVALUATIVE statements identifying problems or quality assessments
   - Markers: "wrong", "flaw", "issue", "problem", "risk", "concern", "should not"
   - Includes: Both negative feedback AND analytical assessments

3. Proposal: SUGGESTIONS or RECOMMENDATIONS for future action
   - Markers: "propose", "suggest", "recommend", "could", "might", "consider"
   - NOT: Statements with imperative mood (those are Directives)

4. Directive: COMMANDS or INSTRUCTIONS requiring action
   - Markers: Imperative verbs ("implement", "create", "ensure"), "must", "shall"
   - NOT: Descriptions of how something works (those are not extracted)
```

### Option B: Add New Type (Description)

Add a fifth type to handle descriptive content:

```
CONCEPTS to extract:
- Directive: Direct commands or instructions (imperative mood)
- Critique: Evaluative feedback or problem identification
- Proposal: Suggestions, recommendations, or plans
- Decision: Formal choices being announced
- Description: Process explanations or factual statements (LOW PRIORITY - extract sparingly)
```

### Recommendation

**Option A** - It's more conservative (no schema change needed) and addresses the core issue of ambiguity through priority rules.

---

## Proposed Few-Shot Examples

### New Example: Distinguishing Directive from Description

```python
# NEGATIVE EXAMPLE - Description, NOT a Directive
lx.data.ExampleData(
    text="The commit phase works as follows: the leader sends a commit message to all followers.",
    extractions=[]  # Nothing extracted - this is description, not instruction
),
```

### New Example: Distinguishing Proposal from Directive

```python
# POSITIVE EXAMPLE - Proposal (suggestive, not imperative)
lx.data.ExampleData(
    text="Agent: We could implement caching here to improve performance.",
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="We could implement caching here to improve performance",
            attributes={"concept_type": "Proposal"}  # "could" = suggestive
        ),
    ]
),

# POSITIVE EXAMPLE - Directive (imperative, not suggestive)
lx.data.ExampleData(
    text="Agent: Implement caching here to improve performance.",
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="Implement caching here to improve performance",
            attributes={"concept_type": "Directive"}  # Imperative verb
        ),
    ]
),
```

### New Example: Distinguishing Decision from Status Update

```python
# POSITIVE EXAMPLE - Decision (formal choice announced)
lx.data.ExampleData(
    text="After discussion, we've decided to use PostgreSQL for the database.",
    extractions=[
        lx.data.Extraction(
            extraction_class="concept",
            extraction_text="we've decided to use PostgreSQL for the database",
            attributes={"concept_type": "Decision"}  # Explicit decision marker
        ),
    ]
),

# NEGATIVE EXAMPLE - Status Update, NOT a Decision
lx.data.ExampleData(
    text="I'm now implementing the changes from the review.",
    extractions=[]  # Nothing extracted - status update, not a choice announcement
),
```

---

## Implementation Plan

### Phase 1: Update Prompt (Low Risk)
1. Update `_build_prompt()` with clarified definitions and priority rules
2. No schema changes required
3. Affects only new extractions

### Phase 2: Add Discrimination Examples (Medium Risk)
1. Add new few-shot examples to `_build_examples()`
2. Test with sample documents before full deployment
3. Compare extraction quality before/after

### Phase 3: (Optional) Retroactive Fix
1. Re-extract high-value documents with improved prompt
2. Compare against existing extractions
3. Consolidate duplicates with different types

---

## Test Cases for Validation

| Input | Expected Type | Discriminating Feature |
|-------|---------------|------------------------|
| "Implement the caching layer" | Directive | Imperative verb |
| "We could add caching" | Proposal | Suggestive "could" |
| "Decision: Use Redis for caching" | Decision | Explicit "Decision:" marker |
| "The caching layer is inefficient" | Critique | Evaluative statement |
| "Caching works by storing data in memory" | (skip) | Description, not actionable |

---

## Success Metrics

1. **Type consistency**: Same content should get same type across artifacts
2. **Reduced duplicates**: Fewer type-variant duplicates in semantic analysis
3. **Clearer boundaries**: Manual review confirms types are correctly discriminated

---

## Next Steps

1. [ ] Operator approval of Option A or B
2. [ ] Implement prompt changes in extraction.py
3. [ ] Create test fixtures with expected outputs
4. [ ] Run extraction on test documents
5. [ ] Compare before/after type consistency
