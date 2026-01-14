---
template: implementation_plan
status: complete
date: 2026-01-05
backlog_id: E2-238
title: memory_refs Auto-Linking
author: Hephaestus
lifecycle_phase: plan
session: 173
version: '1.5'
generated: 2026-01-05
last_updated: '2026-01-05T20:55:06'
---
# Implementation Plan: memory_refs Auto-Linking

@docs/README.md
@docs/epistemic_state.md

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

Add a PostToolUse handler that detects `ingester_ingest` MCP tool completions and auto-updates the source work item's `memory_refs` field with the returned concept IDs.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/hooks/hooks/post_tool_use.py` |
| Lines of code affected | ~50 | New handler function |
| New files to create | 0 | Handler added to existing file |
| Tests to write | 3 | test_post_tool_use.py |
| Dependencies | 2 | MemoryBridge, WorkEngine modules |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | PostToolUse hook + MemoryBridge + WorkEngine |
| Risk of regression | Low | New handler, doesn't modify existing handlers |
| External dependencies | Low | Uses existing modules |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 15 min | High |
| Implement handler | 20 min | High |
| Integration test | 10 min | High |
| **Total** | 45 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/hooks/hooks/post_tool_use.py:44-54
def handle(hook_data: dict) -> Optional[str]:
    tool_name = hook_data.get("tool_name", "")
    messages = []

    # Part 0: Error capture (runs for ALL tools) - E2-130
    error_msg = _capture_errors(hook_data)
    if error_msg:
        messages.append(error_msg)

    # File-specific processing only for editing tools
    if tool_name not in ("Edit", "MultiEdit", "Write"):
        return "\n".join(messages) if messages else None
    # ... no handling for MCP tools like mcp__haios-memory__ingester_ingest
```

**Behavior:** When agent calls `mcp__haios-memory__ingester_ingest`, the MCP server stores content and returns concept_ids, but the source work item's `memory_refs` field is never updated.

**Result:** E2-269 observation: WHY captured to memory (80762-80771) but WORK.md memory_refs stayed empty.

### Desired State

```python
# .claude/hooks/hooks/post_tool_use.py:44-60
def handle(hook_data: dict) -> Optional[str]:
    tool_name = hook_data.get("tool_name", "")
    messages = []

    # Part 0: Error capture (runs for ALL tools) - E2-130
    error_msg = _capture_errors(hook_data)
    if error_msg:
        messages.append(error_msg)

    # Part 0.5: Memory auto-link (E2-238) - for MCP ingester
    if tool_name == "mcp__haios-memory__ingester_ingest":
        autolink_msg = _auto_link_memory_refs(hook_data)
        if autolink_msg:
            messages.append(autolink_msg)
        return "\n".join(messages) if messages else None

    # File-specific processing only for editing tools
    if tool_name not in ("Edit", "MultiEdit", "Write"):
        return "\n".join(messages) if messages else None
```

**Behavior:** When agent calls `ingester_ingest`, PostToolUse handler extracts work_id from source_path, parses concept_ids from response, and calls WorkEngine.add_memory_refs().

**Result:** WORK.md memory_refs automatically populated with concept IDs.

---

## Tests First (TDD)

### Test 1: Auto-link extracts work_id from source_path
```python
def test_auto_link_extracts_work_id():
    """PostToolUse extracts work_id from docs/work/active/{id}/... paths."""
    hook_data = {
        "tool_name": "mcp__haios-memory__ingester_ingest",
        "tool_input": {"source_path": "docs/work/active/E2-238/plans/PLAN.md"},
        "tool_response": {"concept_ids": [80001, 80002], "classification": "techne"}
    }

    # Call the extraction function
    work_id = _extract_work_id_from_source_path(hook_data["tool_input"]["source_path"])
    assert work_id == "E2-238"
```

### Test 2: Auto-link extracts work_id from closure: prefix
```python
def test_auto_link_extracts_work_id_from_closure():
    """PostToolUse extracts work_id from closure:{id} source_path."""
    hook_data = {
        "tool_name": "mcp__haios-memory__ingester_ingest",
        "tool_input": {"source_path": "closure:E2-269"},
        "tool_response": {"concept_ids": [80772, 80773], "classification": "techne"}
    }

    work_id = _extract_work_id_from_source_path(hook_data["tool_input"]["source_path"])
    assert work_id == "E2-269"
```

### Test 3: Auto-link calls WorkEngine when work_id found
```python
def test_auto_link_calls_work_engine(tmp_path, monkeypatch):
    """PostToolUse calls WorkEngine.add_memory_refs when valid response."""
    # Create mock work file
    work_dir = tmp_path / "docs/work/active/E2-238"
    work_dir.mkdir(parents=True)
    work_file = work_dir / "WORK.md"
    work_file.write_text("---\nmemory_refs: []\n---\n# Test")

    hook_data = {
        "tool_name": "mcp__haios-memory__ingester_ingest",
        "tool_input": {"source_path": "docs/work/active/E2-238/plans/PLAN.md"},
        "tool_response": {"concept_ids": [80001, 80002], "classification": "techne"}
    }

    # Monkeypatch paths
    monkeypatch.chdir(tmp_path)

    result = _auto_link_memory_refs(hook_data)

    assert result is not None
    assert "80001" in result or "E2-238" in result
```

### Test 4: Auto-link skips invalid source_paths
```python
def test_auto_link_skips_invalid_paths():
    """PostToolUse returns None when source_path has no work_id."""
    hook_data = {
        "tool_name": "mcp__haios-memory__ingester_ingest",
        "tool_input": {"source_path": "some/random/path.md"},
        "tool_response": {"concept_ids": [80001], "classification": "techne"}
    }

    result = _auto_link_memory_refs(hook_data)
    assert result is None
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/hooks/hooks/post_tool_use.py`
**Location:** After error capture, before file-specific processing

**Current Code (lines 44-54):**
```python
def handle(hook_data: dict) -> Optional[str]:
    tool_name = hook_data.get("tool_name", "")
    messages = []

    # Part 0: Error capture (runs for ALL tools) - E2-130
    error_msg = _capture_errors(hook_data)
    if error_msg:
        messages.append(error_msg)

    # File-specific processing only for editing tools
    if tool_name not in ("Edit", "MultiEdit", "Write"):
        return "\n".join(messages) if messages else None
```

**Changed Code:**
```python
def handle(hook_data: dict) -> Optional[str]:
    tool_name = hook_data.get("tool_name", "")
    messages = []

    # Part 0: Error capture (runs for ALL tools) - E2-130
    error_msg = _capture_errors(hook_data)
    if error_msg:
        messages.append(error_msg)

    # Part 0.5: Memory auto-link (E2-238) - for MCP ingester
    if tool_name == "mcp__haios-memory__ingester_ingest":
        autolink_msg = _auto_link_memory_refs(hook_data)
        if autolink_msg:
            messages.append(autolink_msg)
        return "\n".join(messages) if messages else None

    # File-specific processing only for editing tools
    if tool_name not in ("Edit", "MultiEdit", "Write"):
        return "\n".join(messages) if messages else None
```

### New Handler Function

```python
def _auto_link_memory_refs(hook_data: dict) -> Optional[str]:
    """
    Auto-link memory concept IDs to source work item (E2-238).

    When ingester_ingest returns concept_ids, parse work_id from source_path
    and update the work item's memory_refs field.

    Args:
        hook_data: Hook data with tool_input.source_path and tool_response.concept_ids

    Returns:
        Status message if auto-linked, None otherwise.
    """
    try:
        tool_input = hook_data.get("tool_input", {})
        tool_response = hook_data.get("tool_response", {})

        # Extract source_path and concept_ids
        source_path = tool_input.get("source_path", "")

        # Handle tool_response which may be a string (JSON) or dict
        if isinstance(tool_response, str):
            import json
            tool_response = json.loads(tool_response)

        # Get concept_ids from response
        result = tool_response.get("result", tool_response)
        if isinstance(result, str):
            import json
            result = json.loads(result)

        concept_ids = result.get("concept_ids", [])

        if not concept_ids:
            return None

        # Extract work_id from source_path
        work_id = _extract_work_id_from_source_path(source_path)
        if not work_id:
            return None

        # Import WorkEngine module
        modules_dir = Path(__file__).parent.parent.parent / "haios" / "modules"
        if str(modules_dir) not in sys.path:
            sys.path.insert(0, str(modules_dir))

        from work_engine import WorkEngine
        from governance_layer import GovernanceLayer

        engine = WorkEngine(governance=GovernanceLayer())
        engine.add_memory_refs(work_id, concept_ids)

        return f"[AUTO-LINK] {work_id} memory_refs += {concept_ids}"

    except Exception as e:
        # Don't break hook flow on auto-link errors
        return None


def _extract_work_id_from_source_path(source_path: str) -> Optional[str]:
    """
    Extract work ID from source_path patterns.

    Patterns:
    - docs/work/active/E2-238/... -> E2-238
    - docs/work/archive/INV-052/... -> INV-052
    - closure:E2-269 -> E2-269

    Args:
        source_path: Source path from ingester_ingest call

    Returns:
        Work ID or None if not found.
    """
    # Pattern 1: closure:{id}
    if source_path.startswith("closure:"):
        return source_path[8:]  # Strip "closure:" prefix

    # Pattern 2: docs/work/(active|archive)/{id}/...
    match = re.search(r"docs[/\\]work[/\\](?:active|archive)[/\\]([A-Z]+-\d+)", source_path)
    if match:
        return match.group(1)

    return None
```

### Call Chain Context

```
Agent calls: mcp__haios-memory__ingester_ingest(content, source_path)
    |
    +-> MCP server stores content, returns concept_ids
    |
    +-> Claude Code emits PostToolUse hook
            |
            +-> post_tool_use.py:handle()
                    |
                    +-> _auto_link_memory_refs(hook_data)
                            |
                            +-> _extract_work_id_from_source_path()
                            |       Returns: "E2-238" (or None)
                            |
                            +-> WorkEngine.add_memory_refs("E2-238", [80001, 80002])
                                    |
                                    +-> Writes to WORK.md memory_refs field
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Handler placement | Early in handle(), before file checks | MCP tools aren't file operations, need separate path |
| Import pattern | Same as _capture_errors (sys.path + import) | Consistency with existing E2-264 pattern |
| Error handling | Silent failure (return None) | Don't break hook flow for non-critical feature |
| Response parsing | Handle both dict and JSON string | MCP responses may come as either format |
| Work ID patterns | closure: prefix + docs/work/ path | Covers all observed source_path patterns |

### Input/Output Examples

**Before (E2-269 closure):**
```
Agent calls: ingester_ingest(content="WHY...", source_path="closure:E2-269")
MCP returns: {"concept_ids": [80772, 80773], "classification": "techne"}
PostToolUse: (no handler for MCP tools)
WORK.md memory_refs: []  # NOT UPDATED
```

**After (with E2-238):**
```
Agent calls: ingester_ingest(content="WHY...", source_path="closure:E2-269")
MCP returns: {"concept_ids": [80772, 80773], "classification": "techne"}
PostToolUse: _auto_link_memory_refs() -> "[AUTO-LINK] E2-269 memory_refs += [80772, 80773]"
WORK.md memory_refs: [80772, 80773]  # UPDATED
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No concept_ids in response | Return None (skip) | Test 4 |
| Invalid source_path | Return None (skip) | Test 4 |
| Work file not found | WorkEngine returns silently | Implicit |
| JSON response format | Parse JSON string | Covered in handler |
| Exception during processing | Catch and return None | Handler code |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add tests to `tests/test_post_tool_use.py`
- [ ] Verify all tests fail (red)

### Step 2: Add Handler Function
- [ ] Add `_extract_work_id_from_source_path()` function
- [ ] Add `_auto_link_memory_refs()` function
- [ ] Tests 1, 2, 4 pass (green)

### Step 3: Wire Handler into handle()
- [ ] Add MCP tool check after error capture
- [ ] Call `_auto_link_memory_refs()` for ingester_ingest
- [ ] Test 3 passes (green)

### Step 4: Integration Verification
- [ ] All tests pass
- [ ] Run full test suite (no regressions)

### Step 5: README Sync (MUST)
- [ ] **MUST:** Update `.claude/hooks/hooks/README.md` if it exists
- [ ] **MUST:** Document new handler in hook documentation

### Step 6: Demo Feature
- [ ] Call `ingester_ingest` with work item source_path
- [ ] Verify WORK.md memory_refs updated

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Response format varies | Medium | Parse both dict and JSON string formats |
| WorkEngine import fails | Low | Use existing E2-264 import pattern with try/except |
| Hook slows down | Low | Quick path extraction, no I/O unless work_id found |
| False positives (wrong work_id) | Low | Strict regex patterns, only docs/work/ paths |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 173 | 2026-01-05 | - | Plan authored | Ready for implementation |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/hooks/hooks/post_tool_use.py` | Has `_auto_link_memory_refs` and `_extract_work_id_from_source_path` functions | [ ] | |
| `tests/test_post_tool_use.py` | Has 4 new tests for auto-link | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_post_tool_use.py -v -k auto_link
# Expected: 4 tests passed
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **Runtime consumer exists** (PostToolUse hook is called by Claude Code)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- @docs/work/archive/INV-052/SECTION-8-MEMORY-INTEGRATION.md (gap analysis source)
- @docs/work/archive/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md (handler list)
- @docs/work/archive/E2-269/observations.md (evidence of gap)
- Memory concept 80772: "Gap: WORK.md memory_refs not auto-updated after ingester_ingest"

---
