---
template: handoff
version: 1.0
type: task
date: 2025-12-03
author: Hephaestus (Claude)
status: complete
priority: medium
estimated_effort: 2 hours
generated: 2025-12-03
last_updated: 2025-12-03T20:59:06
---

# Task Handoff: GAP-B3 LLM Classification in Refinement

## Task Summary

Add LLM-based Greek Triad classification to `refinement.py`, replacing the current mock/heuristic logic.

---

## Context

**Gap ID:** GAP-B3
**Source:** @docs/handoff/2025-12-01-GAP-CLOSER-remaining-system-gaps.md
**Investigated:** Session 21 (2025-12-03)

**Current state:** `refinement.py:refine_memory()` uses hardcoded heuristics:
- "Directive" or "must" -> doxa
- "Concept" -> episteme
- Default -> doxa

**Target state:** LLM-based classification with heuristic fallback.

---

## Implementation Spec

### File: `haios_etl/refinement.py`

### Change 1: Add API key parameter

```python
# Line 17 (modify __init__)
class RefinementManager:
    def __init__(self, db_path: str, api_key: Optional[str] = None):
        self.db = DatabaseManager(db_path)
        self.api_key = api_key
```

### Change 2: Add LLM classification method

```python
# Add after line 39 (after scan_raw_memories)
def _classify_with_llm(self, content: str) -> Optional[str]:
    """
    Classify content using LLM (Greek Triad taxonomy).

    Returns:
        Classification string or None if LLM fails
    """
    if not self.api_key:
        return None

    try:
        import google.generativeai as genai

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel("gemini-2.5-flash-lite")

        prompt = f"""Classify this content using Greek Triad taxonomy.

DEFINITIONS:
- episteme: Factual knowledge, definitions, architecture specs, verified truths
- techne: How-to guides, procedures, implementation steps, practical skills
- doxa: Opinions, recommendations, beliefs, proposals, critiques

CONTENT:
{content[:2000]}

Respond with ONLY one word: episteme, techne, or doxa"""

        response = model.generate_content(prompt)
        result = response.text.strip().lower()

        if result in ("episteme", "techne", "doxa"):
            return result
        return None

    except Exception as e:
        logging.warning(f"LLM classification failed: {e}")
        return None
```

### Change 3: Modify refine_memory to use LLM

```python
# Replace lines 41-69 (refine_memory method)
def refine_memory(self, memory_id: int, content: str) -> RefinementResult:
    """
    Analyze memory content using LLM with heuristic fallback.
    """
    # Try LLM first
    llm_result = self._classify_with_llm(content)

    if llm_result:
        return RefinementResult(
            knowledge_type=llm_result,
            confidence=0.9,
            concepts=[],
            reasoning=f"LLM classification: {llm_result}"
        )

    # Fallback to heuristic
    if "Directive" in content or "must" in content.lower():
        return RefinementResult(
            knowledge_type="doxa",
            confidence=0.6,
            concepts=[],
            reasoning="Heuristic: directive language detected."
        )
    elif "Concept" in content:
        return RefinementResult(
            knowledge_type="episteme",
            confidence=0.7,
            concepts=[],
            reasoning="Heuristic: concept label detected."
        )
    else:
        return RefinementResult(
            knowledge_type="doxa",
            confidence=0.5,
            concepts=[],
            reasoning="Heuristic: default classification."
        )
```

---

## Test Requirements

### Existing tests to verify

```bash
pytest tests/test_refinement.py -v
```

### New test cases to add

```python
# In tests/test_refinement.py

def test_classify_with_llm_episteme():
    """Test LLM classifies factual content as episteme."""
    # Mock genai to return "episteme"
    pass

def test_classify_with_llm_fallback():
    """Test fallback to heuristic when LLM fails."""
    # Set api_key=None, verify heuristic used
    pass
```

---

## Acceptance Criteria

- [ ] `RefinementManager` accepts optional `api_key` parameter
- [ ] `_classify_with_llm` method added and working
- [ ] `refine_memory` uses LLM first, falls back to heuristic
- [ ] Existing tests still pass
- [ ] At least 2 new test cases for LLM path
- [ ] Confidence score reflects LLM vs heuristic source

---

## Key References

- @haios_etl/refinement.py - Target file (lines 41-69)
- @haios_etl/extraction.py - LLM pattern (lines 357-360)
- @haios_etl/agents/ingester.py - Classification patterns (lines 73-89)

---

## Risk Mitigation

1. **LLM rate limits:** Classification prompt is small (~200 tokens)
2. **API failures:** Fallback to heuristic ensures functionality
3. **Test coverage:** Mock LLM calls in tests to avoid API dependency

---

## Verification After Implementation

```bash
# Run tests
pytest tests/test_refinement.py -v

# Manual test
python -c "
from haios_etl.refinement import RefinementManager
import os; from dotenv import load_dotenv; load_dotenv()
rm = RefinementManager('haios_memory.db', os.getenv('GOOGLE_API_KEY'))
result = rm.refine_memory(1, 'The system architecture defines three layers.')
print(f'Type: {result.knowledge_type}, Reasoning: {result.reasoning}')
"
```

---

**Ready for implementation by next agent.**
