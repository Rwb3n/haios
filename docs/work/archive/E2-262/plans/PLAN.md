---
template: implementation_plan
status: complete
date: 2026-01-04
backlog_id: E2-262
title: MemoryBridge Learning Extraction
author: Hephaestus
lifecycle_phase: plan
session: 170
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-04T20:44:58'
---
# Implementation Plan: MemoryBridge Learning Extraction

@docs/README.md
@docs/epistemic_state.md

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: New feature, no existing code to show current state"
     - "SKIPPED: Pure documentation task, no code changes"
     - "SKIPPED: Trivial fix, single line change doesn't warrant detailed design"

     This prevents silent section deletion and ensures conscious decisions.
-->

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

MemoryBridge module will provide `extract_learnings(transcript_path)` method that delegates to existing reasoning_extraction.py functionality, enabling stop.py hook to import from modules instead of hooks/ directory.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | memory_bridge.py, test_memory_bridge.py |
| Lines of code affected | ~50 | Add dataclass (~10) + method (~30) + tests (~10) |
| New files to create | 0 | Adding to existing module |
| Tests to write | 3 | Result type, error handling, delegation |
| Dependencies | 1 | reasoning_extraction.py (hooks/) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single delegation to existing module |
| Risk of regression | Low | Adding new method, not modifying existing |
| External dependencies | Low | Uses existing haios_etl infrastructure |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 10 min | High |
| Implement method | 15 min | High |
| Update docs | 5 min | High |
| **Total** | 30 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/hooks/hooks/stop.py:45-58
hooks_dir = Path(__file__).parent.parent
extraction_script = hooks_dir / "reasoning_extraction.py"

if not extraction_script.exists():
    return None

result = subprocess.run(
    [sys.executable, str(extraction_script), transcript_path],
    capture_output=True,
    text=True,
    timeout=10,
    cwd=str(hooks_dir)
)
```

**Behavior:** stop.py hook imports reasoning_extraction.py directly from hooks/ directory

**Result:** Hook bypasses module architecture, violating Strangler Fig migration pattern

### Desired State

```python
# .claude/haios/modules/memory_bridge.py (new method)
def extract_learnings(self, transcript_path: str) -> LearningExtractionResult:
    """Extract learnings from session transcript."""
    # Delegates to reasoning_extraction module
```

**Behavior:** MemoryBridge exposes extract_learnings() method that delegates to existing implementation

**Result:** E2-264 can rewire stop.py to import from MemoryBridge instead of hooks/

---

## Tests First (TDD)

### Test 1: Returns LearningExtractionResult type
```python
def test_extract_learnings_returns_result_type():
    """extract_learnings returns LearningExtractionResult."""
    from memory_bridge import MemoryBridge, LearningExtractionResult
    bridge = MemoryBridge()
    # Non-existent file should return error result
    result = bridge.extract_learnings("/nonexistent/path.jsonl")
    assert isinstance(result, LearningExtractionResult)
```

### Test 2: Handles missing transcript gracefully
```python
def test_extract_learnings_handles_missing_file():
    """extract_learnings handles missing transcript file."""
    from memory_bridge import MemoryBridge
    bridge = MemoryBridge()
    result = bridge.extract_learnings("/nonexistent/transcript.jsonl")
    assert result.success is False
    assert result.reason == "error"
    assert result.error is not None
```

### Test 3: Delegates to reasoning_extraction module
```python
def test_extract_learnings_delegates_to_reasoning_extraction(mocker):
    """extract_learnings delegates to reasoning_extraction functions."""
    from memory_bridge import MemoryBridge

    # Mock the reasoning_extraction functions
    mock_parse = mocker.patch(
        "reasoning_extraction.parse_transcript",
        return_value={"initial_query": "test", "tool_count": 5, "message_count": 10}
    )
    mock_should = mocker.patch(
        "reasoning_extraction.should_extract",
        return_value=(True, "qualified")
    )
    mock_outcome = mocker.patch(
        "reasoning_extraction.determine_outcome",
        return_value="success"
    )
    mock_extract = mocker.patch(
        "reasoning_extraction.extract_and_store",
        return_value=True
    )
    mocker.patch("os.path.exists", return_value=True)

    bridge = MemoryBridge()
    result = bridge.extract_learnings("/path/to/transcript.jsonl")

    assert result.success is True
    mock_parse.assert_called_once()
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/haios/modules/memory_bridge.py`
**Location:** After line 389 (after capture_error method, in E2-261 section)

**New Dataclass (after StoreResult, line 54):**
```python
@dataclass
class LearningExtractionResult:
    """Result of learning extraction operation."""
    success: bool
    reason: str  # qualified, too_short, no_tool_usage, trivial_query, error
    outcome: Optional[str] = None  # success, partial_success, failure
    initial_query: Optional[str] = None
    tools_used: Optional[List[str]] = None
    error: Optional[str] = None
```

**New Method (after capture_error):**
```python
    # =========================================================================
    # E2-262: Learning Extraction
    # =========================================================================

    def extract_learnings(self, transcript_path: str) -> LearningExtractionResult:
        """
        Extract learnings from session transcript.

        Delegates to hooks/reasoning_extraction.py for transcript parsing
        and learning storage.

        Args:
            transcript_path: Path to session transcript JSONL file

        Returns:
            LearningExtractionResult with extraction status and details
        """
        import os
        import sys

        if not os.path.exists(transcript_path):
            return LearningExtractionResult(
                success=False,
                reason="error",
                error=f"Transcript not found: {transcript_path}"
            )

        # Add hooks directory to path for reasoning_extraction import
        hooks_path = str(Path(__file__).parent.parent.parent / "hooks")
        if hooks_path not in sys.path:
            sys.path.insert(0, hooks_path)

        try:
            from reasoning_extraction import (
                parse_transcript,
                should_extract,
                determine_outcome,
                extract_and_store,
                load_env
            )

            # Load environment for API keys
            load_env()

            # Parse transcript
            session_info = parse_transcript(transcript_path)
            if not session_info:
                return LearningExtractionResult(
                    success=False,
                    reason="error",
                    error="Failed to parse transcript"
                )

            # Check if extraction is warranted
            should, reason = should_extract(session_info)
            if not should:
                return LearningExtractionResult(
                    success=False,
                    reason=reason,
                    initial_query=session_info.get("initial_query"),
                    tools_used=session_info.get("tools_used")
                )

            # Determine outcome and extract
            outcome = determine_outcome(session_info)
            extraction_success = extract_and_store(session_info)

            return LearningExtractionResult(
                success=extraction_success,
                reason="qualified" if extraction_success else "error",
                outcome=outcome,
                initial_query=session_info.get("initial_query"),
                tools_used=session_info.get("tools_used"),
                error=None if extraction_success else "Extraction failed"
            )

        except Exception as e:
            return LearningExtractionResult(
                success=False,
                reason="error",
                error=str(e)
            )
```

### Call Chain Context

```
stop.py:handle()
    |
    +-> MemoryBridge.extract_learnings()  # <-- NEW METHOD
    |       Returns: LearningExtractionResult
    |
    +-> reasoning_extraction.parse_transcript()
    +-> reasoning_extraction.should_extract()
    +-> reasoning_extraction.determine_outcome()
    +-> reasoning_extraction.extract_and_store()
            |
            +-> haios_etl.retrieval.record_reasoning_trace()
```

### Function/Component Signatures

```python
def extract_learnings(self, transcript_path: str) -> LearningExtractionResult:
    """
    Extract learnings from session transcript.

    Args:
        transcript_path: Path to JSONL transcript file from Claude Code session

    Returns:
        LearningExtractionResult with:
        - success: True if extraction completed
        - reason: qualified, too_short, no_tool_usage, trivial_query, error
        - outcome: success, partial_success, failure (if qualified)
        - initial_query: First user message from session
        - tools_used: List of tool names used
        - error: Error message if failed
    """
```

### Behavior Logic

```
transcript_path
    |
    +-> File exists?
    |     ├─ NO  → LearningExtractionResult(success=False, reason="error")
    |     └─ YES → Continue
    |
    +-> parse_transcript()
    |     ├─ Empty → LearningExtractionResult(success=False, reason="error")
    |     └─ session_info → Continue
    |
    +-> should_extract()
    |     ├─ (False, reason) → LearningExtractionResult(success=False, reason=reason)
    |     └─ (True, "qualified") → Continue
    |
    +-> determine_outcome() → outcome
    +-> extract_and_store()
          ├─ False → LearningExtractionResult(success=False, reason="error")
          └─ True  → LearningExtractionResult(success=True, reason="qualified", outcome=outcome)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Delegation pattern | Import and call functions from reasoning_extraction.py | Matches E2-261 error capture pattern; single source of truth |
| Path import | Use sys.path to hooks/ directory | Same pattern as E2-261 uses for lib/ directory |
| Return type | Structured LearningExtractionResult dataclass | Provides rich status info for caller (stop.py can log/report) |
| Error handling | Catch all exceptions, return error result | Matches graceful degradation invariant of MemoryBridge |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| File not found | Return error result immediately | Test 2 |
| Empty transcript | Return error from parse failure | Covered by delegation |
| Too short session | Return reason="too_short" | Covered by delegation |
| API key missing | Return error from extract_and_store | Covered by delegation |

### Open Questions

**Q: Should we also expose the individual functions (parse_transcript, should_extract)?**

No. The method provides a single entry point that handles the full flow. If finer control is needed later, we can add methods. Keep interface minimal for now.

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add LearningExtractionResult import test to test_memory_bridge.py
- [ ] Add test_extract_learnings_returns_result_type
- [ ] Add test_extract_learnings_handles_missing_file
- [ ] Add test_extract_learnings_delegates_to_reasoning_extraction
- [ ] Verify all 3 tests fail (red)

### Step 2: Add LearningExtractionResult Dataclass
- [ ] Add dataclass after StoreResult (line 54)
- [ ] Export in module imports
- [ ] Test 1 passes (green) - type exists

### Step 3: Implement extract_learnings Method
- [ ] Add E2-262 section comment after E2-261 section
- [ ] Add extract_learnings method with delegation to hooks/reasoning_extraction.py
- [ ] Tests 2, 3 pass (green)

### Step 4: Integration Verification
- [ ] All tests pass: `pytest tests/test_memory_bridge.py -v`
- [ ] Run full test suite: `pytest tests/ -v` (no regressions)

### Step 5: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/modules/README.md` with new method

---

## Verification

- [ ] Tests pass: `pytest tests/test_memory_bridge.py -v`
- [ ] **MUST:** `.claude/haios/modules/README.md` updated
- [ ] Demo: Import and call extract_learnings on a test path

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| hooks/ path differs across environments | Low | Use Path() for cross-platform compatibility |
| reasoning_extraction imports fail | Medium | Wrap in try/except, return error result |
| E2-264 not yet rewired | Low | This work item adds method; E2-264 does the rewiring |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/memory_bridge.py` | LearningExtractionResult + extract_learnings method | [x] | Lines 56-65 (dataclass), 406-483 (method) |
| `tests/test_memory_bridge.py` | 3 new tests in TestLearningExtraction class | [x] | Lines 340-401, all pass |
| `.claude/haios/modules/README.md` | **MUST:** Documents extract_learnings method | [x] | Line 135 (table), 191-196 (usage) |

**Verification Commands:**
```bash
# Actual output:
pytest tests/test_memory_bridge.py::TestLearningExtraction -v
# tests/test_memory_bridge.py::TestLearningExtraction::test_extract_learnings_returns_result_type PASSED [ 33%]
# tests/test_memory_bridge.py::TestLearningExtraction::test_extract_learnings_handles_missing_file PASSED [ 66%]
# tests/test_memory_bridge.py::TestLearningExtraction::test_extract_learnings_delegates_to_reasoning_extraction PASSED [100%]
# 3 passed in 1.12s
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | Read all 3 files during CHECK phase |
| Test output pasted above? | Yes | 3/3 passed |
| Any deviations from plan? | No | Implementation matches plan exactly |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.

---

## References

- INV-056: Hook-to-Module Migration Investigation
- E2-261: MemoryBridge Error Capture (pattern to follow)
- `.claude/hooks/reasoning_extraction.py`: Source implementation
- `.claude/haios/modules/memory_bridge.py`: Target module
- Memory 80684: Original mapping finding

---
