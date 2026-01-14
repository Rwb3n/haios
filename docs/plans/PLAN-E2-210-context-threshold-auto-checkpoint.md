---
template: implementation_plan
status: complete
date: 2025-12-27
backlog_id: E2-210
title: Context Threshold Auto-Checkpoint
author: Hephaestus
lifecycle_phase: plan
session: 130
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-27T20:41:52'
---
# Implementation Plan: Context Threshold Auto-Checkpoint

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

## Goal

HAIOS will automatically warn the operator when estimated context usage exceeds 80% by analyzing transcript file size in the UserPromptSubmit hook.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/hooks/hooks/user_prompt_submit.py` |
| Lines of code affected | ~30 | New function + hook integration |
| New files to create | 0 | Function added to existing hook |
| Tests to write | 3 | Context estimation + threshold + integration |
| Dependencies | 0 | Uses only stdlib (json, pathlib) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single hook file, no other consumers |
| Risk of regression | Low | Existing tests cover hook (test_hooks.py) |
| External dependencies | Low | Reads transcript file (always exists in hook) |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 15 min | High |
| Implement estimation function | 20 min | High |
| Hook integration | 10 min | High |
| **Total** | 45 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/hooks/hooks/user_prompt_submit.py:47-93
def handle(hook_data: dict) -> str:
    output_parts = []
    output_parts.append(_get_datetime_context())
    # ... vitals, thresholds, lifecycle, rfc2119 ...
    return "\n".join(output_parts)
    # NOTE: No context estimation - operator has no warning before context exhaustion
```

**Behavior:** Hook injects date/time, vitals, thresholds, lifecycle guidance. No context monitoring.

**Result:** Agent continues until context exhausted or operator manually requests checkpoint.

### Desired State

```python
# .claude/hooks/hooks/user_prompt_submit.py:47+ - With context check
def handle(hook_data: dict) -> str:
    output_parts = []
    output_parts.append(_get_datetime_context())

    # NEW: Context threshold check
    transcript_path = hook_data.get("transcript_path", "")
    context_warning = _check_context_threshold(transcript_path)
    if context_warning:
        output_parts.append("")
        output_parts.append(context_warning)

    # ... rest of existing code ...
    return "\n".join(output_parts)
```

**Behavior:** Hook estimates context usage from transcript size, warns at 80% threshold.

**Result:** Operator receives "CONTEXT: ~85% used. Consider /new-checkpoint before context exhaustion." warning in hook output.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Context Estimation Returns Percentage
```python
def test_estimate_context_usage_calculates_percentage():
    """Estimate context from transcript file size."""
    # Create temp transcript with known content
    with tempfile.NamedTemporaryFile(mode='w', suffix='.jsonl', delete=False) as f:
        # Write ~4000 chars ≈ 1000 tokens ≈ 0.5% of 200k
        for _ in range(100):
            f.write(json.dumps({"type": "user", "content": "a" * 40}) + "\n")
        f.flush()

        from hooks.user_prompt_submit import _estimate_context_usage
        pct = _estimate_context_usage(f.name)
        assert 0 < pct < 5  # Should be small percentage
```

### Test 2: Threshold Warning Generated Above 80%
```python
def test_check_context_threshold_warns_above_80():
    """Warning returned when context > 80%."""
    # Mock _estimate_context_usage to return 85%
    with patch('hooks.user_prompt_submit._estimate_context_usage', return_value=85.0):
        from hooks.user_prompt_submit import _check_context_threshold
        warning = _check_context_threshold("/fake/path")
        assert warning is not None
        assert "CONTEXT:" in warning
        assert "85%" in warning
        assert "checkpoint" in warning.lower()
```

### Test 3: No Warning Below Threshold
```python
def test_check_context_threshold_silent_below_80():
    """No warning when context < 80%."""
    with patch('hooks.user_prompt_submit._estimate_context_usage', return_value=50.0):
        from hooks.user_prompt_submit import _check_context_threshold
        warning = _check_context_threshold("/fake/path")
        assert warning is None
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/hooks/hooks/user_prompt_submit.py`
**Location:** Add new functions after line 173, modify handle() at line 65

**New Functions (add after _get_thresholds):**
```python
def _estimate_context_usage(transcript_path: str) -> float:
    """
    Estimate context usage percentage from transcript file size.

    Uses rough heuristic: ~4 chars per token, 200k token context window.
    Returns 0-100 percentage.
    """
    if not transcript_path:
        return 0.0

    path = Path(transcript_path)
    if not path.exists():
        return 0.0

    try:
        # Get file size in bytes, convert to estimated tokens
        file_size = path.stat().st_size
        estimated_tokens = file_size // 4  # ~4 chars per token
        context_limit = 200000  # Claude's context window

        return min(100.0, (estimated_tokens / context_limit) * 100)
    except Exception:
        return 0.0


def _check_context_threshold(transcript_path: str, threshold: float = 80.0) -> Optional[str]:
    """
    Check if context usage exceeds threshold.

    Args:
        transcript_path: Path to transcript JSONL file
        threshold: Percentage threshold (default 80%)

    Returns:
        Warning message if above threshold, None otherwise.
    """
    pct = _estimate_context_usage(transcript_path)
    if pct >= threshold:
        return (
            f"CONTEXT: ~{pct:.0f}% used. "
            "Consider /new-checkpoint before context exhaustion."
        )
    return None
```

**Diff for handle():**
```diff
 def handle(hook_data: dict) -> str:
     output_parts = []
     output_parts.append(_get_datetime_context())

+    # Part 1.5: Context threshold check (E2-210)
+    transcript_path = hook_data.get("transcript_path", "")
+    context_warning = _check_context_threshold(transcript_path)
+    if context_warning:
+        output_parts.append("")
+        output_parts.append(context_warning)
+
     # Part 2: HAIOS Vitals (E2-119: refresh status before reading)
     cwd = hook_data.get("cwd", "")
```

### Call Chain Context

```
Claude Code CLI
    |
    +-> UserPromptSubmit hook triggered
    |       |
    |       +-> hook_dispatcher.dispatch_hook()
    |               |
    |               +-> user_prompt_submit.handle()  # <-- We're adding to this
    |                       |
    |                       +-> _get_datetime_context()
    |                       +-> _check_context_threshold()  # <-- NEW
    |                       +-> _refresh_slim_status()
    |                       +-> _get_vitals()
    |                       ...
    |
    +-> Context injected before prompt
```

### Function/Component Signatures

```python
def _estimate_context_usage(transcript_path: str) -> float:
    """
    Estimate context window usage from transcript file size.

    Args:
        transcript_path: Absolute path to transcript JSONL file

    Returns:
        Estimated percentage (0.0-100.0) of context used
    """

def _check_context_threshold(transcript_path: str, threshold: float = 80.0) -> Optional[str]:
    """
    Generate warning if context exceeds threshold.

    Args:
        transcript_path: Path to transcript file
        threshold: Warning threshold percentage (default 80%)

    Returns:
        Warning string if above threshold, None otherwise
    """
```

### Behavior Logic

**New Flow:**
```
hook_data → extract transcript_path
              |
              +-> _estimate_context_usage(path)
                      |
                      +-> file exists? → get size → estimate tokens → calculate %
                      |                                                    |
                      +-> return 0.0 if error                             |
                                                                          v
              +-> _check_context_threshold() <----------------------------+
                      |
                      +-> pct >= 80%? ─┬─ YES → return "CONTEXT: ~X% used..."
                                       └─ NO  → return None
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| File size vs parsing | File size | Parsing JSONL is slow; size heuristic is O(1) and "good enough" |
| 4 chars/token ratio | Industry standard | Conservative estimate, errs toward earlier warning |
| 80% threshold | Configurable param | Leaves buffer before context exhaustion |
| Insert after datetime | Before vitals | Context warning is high-priority, should be visible early |

### Input/Output Examples

**Example: 50MB transcript (below threshold):**
```
Input: transcript_path = "/tmp/transcript.jsonl" (50MB)
Calculation:
  - file_size = 52428800 bytes
  - estimated_tokens = 52428800 / 4 = 13107200
  - pct = 13107200 / 200000 * 100 = 6553%... wait

ISSUE DISCOVERED: 50MB transcript would be way over 100%.
Need to cap at 100%. Already have min(100.0, ...) in design.

Realistic example:
  - file_size = 400000 bytes (400KB)
  - estimated_tokens = 100000
  - pct = 50%
  - Result: None (below 80%)
```

**Example: 700KB transcript (above threshold):**
```
Input: transcript_path = "/tmp/transcript.jsonl" (700KB)
Calculation:
  - file_size = 716800 bytes
  - estimated_tokens = 179200
  - pct = 89.6%
  - Result: "CONTEXT: ~90% used. Consider /new-checkpoint before context exhaustion."
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Transcript doesn't exist | Return 0.0 | Test with mock path.exists() |
| Empty transcript | Return 0.0 | Test with 0-byte file |
| Very large transcript | Cap at 100% | Test with huge file size |
| File read error | Return 0.0, fail silently | Exception handling in function |

### Open Questions

**Q: Should threshold be configurable via config file?**

Per memory 2205: "required checks should not be in hook's code, should be in governing configuration artifact". However, for this initial implementation, hardcoded 80% with parameter default is acceptable. Future E2-xxx can add config file support.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add tests to `tests/test_hooks.py` (in new TestContextThreshold class)
- [ ] Verify all 3 tests fail (red)

### Step 2: Add Context Estimation Function
- [ ] Add `_estimate_context_usage()` to user_prompt_submit.py
- [ ] Test 1 passes (green)

### Step 3: Add Threshold Check Function
- [ ] Add `_check_context_threshold()` to user_prompt_submit.py
- [ ] Tests 2, 3 pass (green)

### Step 4: Integrate into handle()
- [ ] Add context check after datetime in handle()
- [ ] All tests pass (green)

### Step 5: Integration Verification
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] No regressions

### Step 6: README Sync (MUST)
- [ ] **MUST:** Update `.claude/hooks/README.md` with context threshold feature
- [ ] Note: No directory structure changes, parent README update not needed

### Step 7: Consumer Verification
**SKIPPED:** No code migration or renaming. New functions added to existing file.

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| File size doesn't correlate with tokens | Medium | Conservative 4 chars/token ratio, early warning is better than late |
| Hook performance impact | Low | O(1) stat() call, no parsing |
| False positives on large files | Low | 80% threshold leaves buffer; warning is advisory only |

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
| `.claude/hooks/hooks/user_prompt_submit.py` | `_estimate_context_usage()` and `_check_context_threshold()` exist | [ ] | |
| `tests/test_hooks.py` | TestContextThreshold class with 3 tests | [ ] | |
| `.claude/hooks/README.md` | **MUST:** Context threshold feature documented | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_hooks.py -v -k "context"
# Expected: 3 tests passed
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
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- Work item: `docs/work/active/WORK-E2-210-context-threshold-auto-checkpoint.md`
- INV-041: Autonomous Session Loop Gap Analysis (spawned this work)
- Memory 68696: "proactive checkpointing at 9% context threshold"
- Memory 2205: "required checks should be in governing configuration artifact"

---
