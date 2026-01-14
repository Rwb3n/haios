# Investigation Report: TOON Serializer

**Date:** 2025-12-04
**Author:** Hephaestus (Builder)
**Status:** Draft

## 1. Executive Summary
To maximize the utility of the "Output Pipeline", we investigated **Token-Oriented Object Notation (TOON)** as a serialization format for Epoch artifacts. Benchmarks on HAIOS concept data show a **57.56% reduction in token usage** compared to standard JSON. We recommend implementing a Python `TOONSerializer` to encode the ReasoningBank strategies for the next epoch.

## 2. Format Deep-Dive
TOON is a line-oriented, indentation-based format optimized for LLMs.
*   **Tabular Arrays:** The core efficiency driver. `key[N]{f1,f2}:` followed by CSV-like rows.
*   **Schema-Aware:** The header `{f1,f2}` provides an explicit schema, helping the LLM parse the data.
*   **Constraint:** Tabular arrays only support primitive values. Nested lists (like `tags`) must be flattened or handled via "Mixed Arrays".

## 3. Token Efficiency Validation
We ran a benchmark (`scripts/benchmark_toon.py`) using 50 synthetic HAIOS concepts.

**Results:**
*   **JSON:** 3810 tokens (13,304 chars)
*   **TOON:** 1617 tokens (5,289 chars)
*   **Savings:** **57.56%**

**Implication:**
We can fit **2.3x more knowledge** in the same context window by using TOON. This is critical for the "Context Injection" phase of the Agent Ecosystem.

## 4. Python Implementation Design
Since no official Python SDK exists, we will implement a lightweight `TOONSerializer`.

### API Design
```python
class TOONSerializer:
    def dumps(self, data: Any) -> str:
        """Serialize data to TOON string."""
        pass
        
    def loads(self, toon_str: str) -> Any:
        """Deserialize TOON string to data."""
        pass
```

### Strategy
1.  **Detect Tabular Candidates:** Scan lists of dicts. If keys are identical and values are primitives, use Tabular Form.
2.  **Handle Nested Lists:** For fields like `tags`, flatten to pipe-separated strings (`tag1|tag2`) during serialization to maintain tabular eligibility, or fall back to Expanded List format if complexity is high.
3.  **Streaming:** Implement a generator-based serializer to handle large datasets without memory overhead.

## 5. Integration Plan
1.  **Create Module:** `haios_etl/toon.py`
2.  **Update Refinement:** Use `TOONSerializer` when exporting `concepts` for the next epoch.
3.  **Update MCP:** Allow `haios-memory-mcp` to serve `application/toon` content.

## 6. Recommendation
**Proceed immediately.** The 57% savings is a massive multiplier for agent intelligence. The implementation complexity is moderate (writing a serializer), but the payoff is high.
