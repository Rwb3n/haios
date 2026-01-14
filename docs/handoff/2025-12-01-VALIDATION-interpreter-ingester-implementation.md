# generated: 2025-12-01
# System Auto: last updated on: 2025-12-01 14:23:59
# Validation Handoff: Interpreter + Ingester Implementation

**To:** Next Agent
**From:** Hephaestus (Builder)
**Date:** 2025-12-01
**Subject:** Implementation specification for Interpreter and Ingester subagents

---

```yaml
Type: Feature
Severity: High
Priority: High
Date: 2025-12-01
Discovered By: Hephaestus (Session 17)
Assigned To: Next Agent
Estimated Effort: 4-8 hrs implementation
Dependencies: Session 17 MVP complete
Blocking: Agent Ecosystem functionality
Status: APPROVED - Ready for implementation
```

---

## Executive Summary

All design questions (Q1-Q10) have been answered and **approved by Operator on 2025-12-01**.
This handoff now serves as the **implementation specification**.

---

## Approved Design Decisions

### DD-012: Interpreter Translation Method
**Decision:** LLM-based translation with rule-based fallback
- Primary: Call Gemini to parse intent and extract structured directive
- Fallback: Rule-based pattern matching for common operations
- Rationale: Handles ambiguity while providing deterministic fallback

### DD-013: Confidence Handling
**Decision:** No threshold gate; return confidence, let caller decide
- Interpreter returns confidence score (0.0-1.0) with every response
- Calling agent/operator decides how to handle low confidence
- Low-confidence interpretations logged for learning
- Rationale: Flexibility over rigid gates

### DD-014: No-Context Behavior
**Decision:** Proceed but flag as "ungrounded interpretation"
- Scenarios: Cold start, novel domain, typos, vague intent
- Behavior: Return result with `grounded: false` flag
- Rationale: Fail-open for MVP, operator can provide context if needed

### DD-015: Single-Item Ingestion
**Decision:** No batching in MVP; single item per call
- Future: Batch support can be added later
- Rationale: Simplicity for MVP

### DD-016: Failure Handling
**Decision:** 3 retries with exponential backoff (2s, 4s, 8s), error classification
- RETRYABLE: rate limit, timeout, connection errors → retry
- PERMANENT: malformed, invalid, not found → fail immediately
- UNKNOWN: retry once, then fail
- Pattern: Matches existing `ExtractionConfig` in `extraction.py`

### DD-017: Provenance Tracking
**Decision:** Include agent ID in provenance
- Field: `ingested_by_agent` added to provenance records
- Rationale: Audit trail for multi-agent system

### DD-018: Synchronous Collaboration
**Decision:** Synchronous handoff for MVP
- Interpreter waits for Ingester result
- Future: Async queue can be added for scale
- Rationale: Simplicity for MVP

### DD-019: Ingester Timeout
**Decision:** 30 seconds timeout
- Covers: API call + extraction + storage
- On timeout: Return partial result with error flag
- Rationale: Industry standard for complex operations

### DD-020: Implementation Architecture
**Decision:** Hybrid (Option C) - Python modules with MCP wrappers
- Core logic: `haios_etl/agents/interpreter.py`, `haios_etl/agents/ingester.py`
- MCP exposure: `interpreter_translate`, `ingester_ingest` tools in `mcp_server.py`
- Pattern: Matches existing `database.py` + `mcp_server.py` relationship
- Rationale: Testable core + agent-accessible API

---

## Implementation Specification

### File Structure

```
haios_etl/
├── agents/
│   ├── __init__.py
│   ├── interpreter.py    # Core Interpreter logic
│   └── ingester.py       # Core Ingester logic
├── mcp_server.py         # Add interpreter_translate, ingester_ingest tools
```

### Interpreter Module (`agents/interpreter.py`)

```python
@dataclass
class InterpreterConfig:
    timeout_seconds: int = 30
    use_llm: bool = True
    fallback_to_rules: bool = True

@dataclass
class InterpretationResult:
    directive: dict           # Structured directive
    confidence: float         # 0.0-1.0
    grounded: bool           # True if context was found
    context_used: list[str]  # Memory items used

class Interpreter:
    def translate(self, intent: str) -> InterpretationResult:
        """Translate operator intent to system directive."""
        # 1. Search memory for context
        # 2. LLM translation (or rule-based fallback)
        # 3. Return result with confidence
```

**Input Schema:**
```yaml
input_schema:
  type: object
  properties:
    intent:
      type: string
      description: Natural language operator intent
  required: [intent]
```

**Output Schema:**
```yaml
output_schema:
  type: object
  properties:
    directive:
      type: object
      description: Structured system directive
    confidence:
      type: number
      minimum: 0
      maximum: 1
    grounded:
      type: boolean
      description: True if relevant context was found
    context_used:
      type: array
      items:
        type: string
```

### Ingester Module (`agents/ingester.py`)

```python
@dataclass
class IngesterConfig:
    timeout_seconds: int = 30
    max_retries: int = 3
    backoff_base: float = 2.0

@dataclass
class IngestionResult:
    concept_ids: list[int]
    entity_ids: list[int]
    classification: str       # episteme, techne, doxa
    ingested_by_agent: str   # Agent ID for provenance

class Ingester:
    def ingest(self, content: str, source_path: str,
               content_type_hint: str = "unknown") -> IngestionResult:
        """Ingest content into memory with classification."""
        # 1. Classify if hint is "unknown"
        # 2. Extract entities/concepts (with retry logic)
        # 3. Store in memory
        # 4. Return result with provenance
```

**Input Schema:**
```yaml
input_schema:
  type: object
  properties:
    content:
      type: string
    source_path:
      type: string
    content_type_hint:
      type: string
      enum: [episteme, techne, doxa, unknown]
      default: unknown
  required: [content, source_path]
```

**Output Schema:**
```yaml
output_schema:
  type: object
  properties:
    concept_ids:
      type: array
      items:
        type: integer
    entity_ids:
      type: array
      items:
        type: integer
    classification:
      type: string
      enum: [episteme, techne, doxa]
    ingested_by_agent:
      type: string
```

### MCP Tool Wrappers

Add to `mcp_server.py`:

```python
@mcp.tool()
def interpreter_translate(intent: str) -> str:
    """Translate operator intent to system directive."""
    from haios_etl.agents.interpreter import Interpreter
    interpreter = Interpreter()
    result = interpreter.translate(intent)
    return json.dumps(asdict(result), indent=2)

@mcp.tool()
def ingester_ingest(content: str, source_path: str,
                    content_type_hint: str = "unknown") -> str:
    """Ingest content into memory with classification."""
    from haios_etl.agents.ingester import Ingester
    ingester = Ingester()
    result = ingester.ingest(content, source_path, content_type_hint)
    return json.dumps(asdict(result), indent=2)
```

---

## Test Requirements

### Minimum Test Coverage

| Test | Description | Priority |
|------|-------------|----------|
| `test_interpreter_translate_basic` | Happy path translation | HIGH |
| `test_interpreter_no_context` | Returns grounded=false when no context | HIGH |
| `test_interpreter_low_confidence` | Returns confidence < 0.5 for ambiguous | MEDIUM |
| `test_interpreter_rule_fallback` | Falls back to rules when LLM fails | MEDIUM |
| `test_ingester_ingest_episteme` | Classifies knowledge correctly | HIGH |
| `test_ingester_ingest_techne` | Classifies how-to correctly | HIGH |
| `test_ingester_ingest_doxa` | Classifies opinion correctly | HIGH |
| `test_ingester_extraction_failure` | Retries then fails gracefully | HIGH |
| `test_ingester_provenance` | Includes agent ID in result | MEDIUM |
| `test_collaboration_flow` | Interpreter -> Ingester end-to-end | HIGH |
| `test_mcp_interpreter_translate` | MCP tool wrapper works | MEDIUM |
| `test_mcp_ingester_ingest` | MCP tool wrapper works | MEDIUM |

### Test File Structure

```
tests/
├── test_interpreter.py    # Unit tests for Interpreter
├── test_ingester.py       # Unit tests for Ingester
└── test_mcp.py           # Add MCP wrapper tests (existing file)
```

---

## Acceptance Criteria

### Interpreter
- [ ] `translate()` returns valid `InterpretationResult`
- [ ] Confidence score between 0.0-1.0
- [ ] `grounded=false` when no context found
- [ ] Falls back to rule-based when LLM unavailable
- [ ] MCP tool `interpreter_translate` exposed and functional

### Ingester
- [ ] `ingest()` returns valid `IngestionResult`
- [ ] Classifies content into episteme/techne/doxa
- [ ] Retry logic with exponential backoff (3 retries, 2s/4s/8s)
- [ ] Provenance includes `ingested_by_agent`
- [ ] MCP tool `ingester_ingest` exposed and functional

### Integration
- [ ] Interpreter can invoke Ingester (via module import)
- [ ] End-to-end flow: intent -> directive -> ingestion -> result
- [ ] All tests pass
- [ ] Full test suite remains at 88+ tests

---

## References

| Document | Purpose |
|----------|---------|
| [PLAN-AGENT-ECOSYSTEM-001](../plans/PLAN-AGENT-ECOSYSTEM-001.md) | Architecture decisions Q1-Q3 |
| [Gap Closer Handoff](2025-12-01-GAP-CLOSER-remaining-system-gaps.md) | Gap inventory |
| [Session 17 Checkpoint](../checkpoints/2025-11-30-SESSION-17-agent-ecosystem-vision.md) | Vision context |
| [extraction.py](../../haios_etl/extraction.py) | Error handling pattern (lines 40-46, 186-296) |
| [MCP Integration Guide](../MCP_INTEGRATION.md) | Tool patterns |

---

## Implementation Checklist

```
[ ] Create haios_etl/agents/__init__.py
[ ] Create haios_etl/agents/interpreter.py
[ ] Create haios_etl/agents/ingester.py
[ ] Create tests/test_interpreter.py
[ ] Create tests/test_ingester.py
[ ] Add MCP tools to mcp_server.py
[ ] Add MCP tests to tests/test_mcp.py
[ ] Run full test suite (expect 100+ tests)
[ ] Update epistemic_state.md
[ ] Create completion handoff
```

---

**Status:** APPROVED - Ready for implementation
**Approved By:** Operator (2025-12-01)
**Last Updated:** 2025-12-01
