---
template: implementation_plan
status: complete
date: 2026-02-19
backlog_id: WORK-168
title: "Cycle Phase Auto-Advancement"
author: Hephaestus
lifecycle_phase: plan
session: 402
version: "1.5"
generated: 2026-02-19
last_updated: 2026-02-19T19:07:28
---
# Implementation Plan: Cycle Phase Auto-Advancement

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

After this plan is complete, the PostToolUse hook will automatically detect lifecycle skill completions and update `session_state` in `haios-status-slim.json` with the correct `active_cycle`, `current_phase`, and `phase_history` — eliminating the need for agents to execute `just set-cycle` manually during ceremony workflows.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/hooks/hooks/post_tool_use.py` |
| Lines of code affected | ~30 | New Part 8 handler + import |
| New files to create | 2 | `lib/cycle_state.py`, `tests/test_cycle_state.py` |
| Tests to write | 8 | See Tests First section (7 unit + 1 integration) |
| Dependencies | 2 | `governance_events.py` (log_phase_transition), `cycle_runner.py` (CYCLE_PHASES) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Med | PostToolUse hook + haios-status-slim.json + governance events |
| Risk of regression | Low | New Part 8 is additive; existing Parts 0-7 unchanged |
| External dependencies | Low | All deps are internal lib/ modules |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests + lib/cycle_state.py | 30 min | High |
| PostToolUse Part 8 integration | 15 min | High |
| Verification | 10 min | High |
| **Total** | ~55 min | High |

---

## Current State vs Desired State

### Current State

```python
# justfile:307 - Manual cycle state setting
# Usage: just set-cycle implementation-cycle DO E2-288
# Agent must read ceremony SKILL.md instruction, then execute Bash command
```

**Behavior:** Agent reads SKILL.md "On Entry: just set-cycle ..." instruction, executes Bash command. Each invocation costs agent tokens (reading instruction + tool call).

**Result:** Session state updated manually. Easily forgotten, leading to stale `session_state` in haios-status-slim.json. Agent spends tokens on mechanical bookkeeping.

### Desired State

```python
# lib/cycle_state.py - Automatic cycle state advancement
def advance_cycle_phase(skill_name: str, project_root: Path = None) -> bool:
    """Auto-advance session_state when lifecycle skill completes."""
    # Maps skill name -> cycle key -> next phase
    # Updates haios-status-slim.json session_state
    # Logs governance event via log_phase_transition
```

**Behavior:** PostToolUse Part 8 detects `tool_name == "Skill"`, extracts skill name from `tool_input["skill"]`, calls `advance_cycle_phase()` which reads current phase from `session_state`, computes next phase from `CYCLE_PHASES`, and writes updated state.

**Result:** Zero agent token cost for cycle state management. State always current. `just set-cycle` remains as manual override.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: advance_cycle_phase advances implementation-cycle PLAN to DO
```python
def test_advance_impl_plan_to_do(tmp_path):
    # Setup: slim JSON with session_state at PLAN phase
    slim = {"session_state": {"active_cycle": "implementation-cycle", "current_phase": "PLAN", "work_id": "WORK-168", "entered_at": "2026-02-19T00:00:00"}}
    slim_file = tmp_path / ".claude" / "haios-status-slim.json"
    slim_file.parent.mkdir(parents=True)
    slim_file.write_text(json.dumps(slim))
    # Action
    result = advance_cycle_phase("implementation-cycle", project_root=tmp_path)
    # Assert
    assert result is True
    data = json.loads(slim_file.read_text())
    assert data["session_state"]["current_phase"] == "DO"
    assert data["session_state"]["active_cycle"] == "implementation-cycle"
```

### Test 2: advance_cycle_phase advances investigation-cycle EXPLORE to HYPOTHESIZE
```python
def test_advance_inv_explore_to_hypothesize(tmp_path):
    slim = {"session_state": {"active_cycle": "investigation-cycle", "current_phase": "EXPLORE", "work_id": "INV-001", "entered_at": "2026-02-19T00:00:00"}}
    # ... setup ...
    result = advance_cycle_phase("investigation-cycle", project_root=tmp_path)
    assert result is True
    data = json.loads(slim_file.read_text())
    assert data["session_state"]["current_phase"] == "HYPOTHESIZE"
```

### Test 3: Unrecognized skill name returns False, no state change
```python
def test_unrecognized_skill_no_change(tmp_path):
    slim = {"session_state": {"active_cycle": "implementation-cycle", "current_phase": "DO", "work_id": "WORK-168", "entered_at": "2026-02-19T00:00:00"}}
    # ... setup ...
    result = advance_cycle_phase("retro-cycle", project_root=tmp_path)
    assert result is False
    data = json.loads(slim_file.read_text())
    assert data["session_state"]["current_phase"] == "DO"  # unchanged
```

### Test 4: Last phase (CHAIN) does not advance further
```python
def test_last_phase_no_advance(tmp_path):
    slim = {"session_state": {"active_cycle": "implementation-cycle", "current_phase": "CHAIN", "work_id": "WORK-168", "entered_at": "2026-02-19T00:00:00"}}
    # ... setup ...
    result = advance_cycle_phase("implementation-cycle", project_root=tmp_path)
    assert result is False  # Already at last phase
```

### Test 5: Handles 4-field session_state (no phase_history/active_queue)
```python
def test_four_field_schema_handled(tmp_path):
    # Only 4 fields — no phase_history or active_queue
    slim = {"session_state": {"active_cycle": "implementation-cycle", "current_phase": "PLAN", "work_id": "WORK-168", "entered_at": "2026-02-19T00:00:00"}}
    # ... setup ...
    result = advance_cycle_phase("implementation-cycle", project_root=tmp_path)
    assert result is True
    data = json.loads(slim_file.read_text())
    assert data["session_state"]["current_phase"] == "DO"
    assert "phase_history" in data["session_state"]  # auto-created
    assert len(data["session_state"]["phase_history"]) == 1
```

### Test 6: Phase history accumulates across multiple advances
```python
def test_phase_history_accumulates(tmp_path):
    slim = {"session_state": {"active_cycle": "implementation-cycle", "current_phase": "PLAN", "work_id": "WORK-168", "entered_at": "2026-02-19T00:00:00", "phase_history": [], "active_queue": None}}
    # ... setup, advance PLAN->DO, then DO->CHECK ...
    advance_cycle_phase("implementation-cycle", project_root=tmp_path)
    # Manually set current_phase to DO to simulate skill completion
    data = json.loads(slim_file.read_text())
    assert data["session_state"]["phase_history"][0]["from"] == "PLAN"
    assert data["session_state"]["phase_history"][0]["to"] == "DO"
```

### Test 7: Missing slim file returns False (fail-permissive)
```python
def test_missing_slim_file_returns_false(tmp_path):
    result = advance_cycle_phase("implementation-cycle", project_root=tmp_path)
    assert result is False  # No crash, no exception
```

### Test 8: PostToolUse handle() fires Part 8 for tool_name="Skill" (integration)
```python
def test_hook_fires_part8_for_skill(tmp_path, monkeypatch):
    """Integration: handle() with tool_name='Skill' calls advance_cycle_phase."""
    # Ensure cycle_state is importable and imported before patching
    import cycle_state
    # Monkeypatch advance_cycle_phase to record calls
    called_with = []
    monkeypatch.setattr(cycle_state, "advance_cycle_phase", lambda s, **kw: called_with.append(s) or True)
    # Call handle() with Skill tool_name
    hook_data = {"tool_name": "Skill", "tool_input": {"skill": "implementation-cycle"}}
    result = handle(hook_data)
    assert "implementation-cycle" in called_with
    assert "[CYCLE]" in (result or "")
```

---

## Detailed Design

<!-- REQUIRED: Document HOW the implementation works, not just WHAT it does.
     Future agents should be able to implement from this section alone.
     This section bridges the gap between tests (WHAT) and steps (HOW).

     MUST INCLUDE (per Session 88 enhancement):
     1. Actual current code that will be changed (copy from source)
     2. Exact diff/change to be made
     3. Function signature details with context
     4. Input/output examples with REAL data from the system

     PATTERN VERIFICATION (E2-255 Learning):
     IF creating a new module that imports from siblings:
       - MUST read at least one sibling module for import/error patterns
       - Verify: try/except conditional imports? sys.path manipulation? error types?
       - Use the SAME patterns as existing siblings (consistency > preference)

     IF modifying existing module:
       - Follow existing patterns in that file

     IF creating module with no siblings (new directory):
       - Document chosen patterns in Key Design Decisions with rationale -->

### New File: `lib/cycle_state.py`

```python
"""
Cycle phase auto-advancement for PostToolUse hook (WORK-168).

Follows session_end_actions.py pattern:
- Pure functions in lib/
- Fail-permissive (never raises)
- _default_project_root() for path derivation
- Testable without hook infrastructure
"""
import json
from datetime import datetime
from pathlib import Path
from typing import Optional

# Skill name -> CYCLE_PHASES key mapping
# Only lifecycle skills that have phase sequences are mapped.
# Ceremony skills (retro-cycle, close-work-cycle, etc.) are NOT mapped —
# they use CEREMONY_PHASES which is a separate concern.
SKILL_TO_CYCLE = {
    "implementation-cycle": "implementation-cycle",
    "investigation-cycle": "investigation-cycle",
    "plan-authoring-cycle": "plan-authoring-cycle",
}


def _default_project_root() -> Path:
    """Derive project root from this file's location.
    lib/ -> haios/ -> .claude/ -> project root.
    """
    return Path(__file__).parent.parent.parent.parent


def advance_cycle_phase(
    skill_name: str,
    project_root: Optional[Path] = None,
) -> bool:
    """Advance session_state to next phase after a lifecycle skill completes.

    Reads current phase from haios-status-slim.json, looks up next phase
    in CYCLE_PHASES, writes updated state. Appends to phase_history.

    Args:
        skill_name: Name of the completed skill (e.g., "implementation-cycle")
        project_root: Project root path. Defaults to derived path.

    Returns:
        True if phase was advanced, False if no advancement (unrecognized
        skill, already at last phase, missing file, or error).
    """
    try:
        root = project_root or _default_project_root()
        slim_file = root / ".claude" / "haios-status-slim.json"
        if not slim_file.exists():
            return False

        # Map skill name to cycle key
        cycle_key = SKILL_TO_CYCLE.get(skill_name)
        if cycle_key is None:
            return False

        # Get phase sequence
        # Import here to avoid circular imports in hook context
        from cycle_runner import CYCLE_PHASES
        phases = CYCLE_PHASES.get(cycle_key, [])
        if not phases:
            return False

        # Read current state
        data = json.loads(slim_file.read_text(encoding="utf-8"))
        session_state = data.get("session_state", {})
        current_phase = session_state.get("current_phase")

        if current_phase is None:
            return False

        # Find next phase
        try:
            idx = phases.index(current_phase)
        except ValueError:
            return False  # Current phase not in sequence

        if idx >= len(phases) - 1:
            return False  # Already at last phase

        next_phase = phases[idx + 1]
        now = datetime.now().isoformat()

        # Update session_state (normalize to 6-field schema)
        session_state["current_phase"] = next_phase
        session_state["entered_at"] = now
        # Ensure phase_history exists (handles 4-field schema)
        history = session_state.setdefault("phase_history", [])
        history.append({"from": current_phase, "to": next_phase, "at": now})
        session_state.setdefault("active_queue", None)

        data["session_state"] = session_state
        slim_file.write_text(json.dumps(data, indent=4), encoding="utf-8")

        # Log governance event (fail-permissive)
        try:
            from governance_events import log_phase_transition
            work_id = session_state.get("work_id", "unknown")
            log_phase_transition(next_phase, work_id, "PostToolUse-auto")
        except Exception:
            pass  # Event logging failure is non-fatal

        return True

    except Exception:
        return False
```

### PostToolUse Part 8: Auto-advance on lifecycle skill completion

**File:** `.claude/hooks/hooks/post_tool_use.py`
**Location:** BEFORE the `tool_name not in ("Edit", "MultiEdit", "Write")` guard at line 60-62, AFTER Part 0.5 (line 53-58). Same pattern as Part 0.5: tool-specific block with early return.

**CRITICAL (Critique A6):** Parts 2-7 are inside the Edit/Write guard. `tool_name == "Skill"` fails that guard, so Part 8 MUST be placed before it or it is dead code.

**New Code (Part 8) — insert between line 58 and line 60:**
```python
    # Part 8: Cycle phase auto-advancement (WORK-168)
    if tool_name == "Skill":
        skill_name = hook_data.get("tool_input", {}).get("skill", "")
        if skill_name:
            try:
                lib_dir = Path(__file__).parent.parent / "haios" / "lib"
                if str(lib_dir) not in sys.path:
                    sys.path.insert(0, str(lib_dir))
                from cycle_state import advance_cycle_phase
                advanced = advance_cycle_phase(skill_name)
                if advanced:
                    messages.append(f"[CYCLE] Auto-advanced phase after {skill_name}")
            except Exception:
                pass  # Fail-permissive: never break hook chain
        return "\n".join(messages) if messages else None
```

**Why early return:** Skill invocations have no file path to process. Parts 2-7 are all file-path-based. Returning early is correct and matches the Part 0.5 pattern.

### Call Chain Context

```
Claude Code PostToolUse event
    |
    +-> post_tool_use(hook_data)
    |       tool_name = hook_data["tool_name"]
    |       tool_input = hook_data["tool_input"]
    |
    +-> Part 0: Error capture (all tools)
    +-> Part 0.5: Memory auto-link (MCP ingester only) -> early return
    +-> Part 8: Cycle auto-advance (Skill only) -> early return  # <-- NEW
    |       |
    |       +-> advance_cycle_phase("implementation-cycle")
    |               |
    |               +-> Read haios-status-slim.json
    |               +-> CYCLE_PHASES["implementation-cycle"] = ["PLAN","DO","CHECK","DONE","CHAIN"]
    |               +-> current_phase="PLAN" -> next_phase="DO"
    |               +-> Write updated session_state
    |               +-> log_phase_transition("DO", "WORK-168", "PostToolUse-auto")
    |
    +-> Guard: tool_name not in (Edit, MultiEdit, Write) -> early return
    +-> Parts 2-7: File-specific processing (Edit/Write only)
    +-> return "\n".join(messages)
```

### Function/Component Signatures

```python
def advance_cycle_phase(
    skill_name: str,
    project_root: Optional[Path] = None,
) -> bool:
    """Advance session_state to next phase after a lifecycle skill completes.

    Args:
        skill_name: Name of the completed skill (e.g., "implementation-cycle").
                    Must be in SKILL_TO_CYCLE mapping to trigger advancement.
        project_root: Project root path. Defaults to derived from file location.

    Returns:
        True if phase was advanced successfully.
        False if: unrecognized skill, at last phase, missing file, any error.

    Side effects:
        - Writes to haios-status-slim.json (session_state fields)
        - Appends to governance-events.jsonl (CyclePhaseEntered event)
    """
```

### Behavior Logic

```
PostToolUse fires with tool_name="Skill"
    |
    +-> Extract skill_name from tool_input["skill"]
    |
    +-> skill_name in SKILL_TO_CYCLE?
          |
          ├─ NO → return False (silent, no state change)
          |
          └─ YES → Read haios-status-slim.json
                     |
                     +-> current_phase in CYCLE_PHASES[cycle_key]?
                           |
                           ├─ NO → return False (unknown phase)
                           |
                           └─ YES → Is this the last phase?
                                      |
                                      ├─ YES → return False (can't advance)
                                      |
                                      └─ NO → Write next_phase
                                               Append to phase_history
                                               Log governance event
                                               return True
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Where to put logic | `lib/cycle_state.py` (new file) | Follows `session_end_actions.py` pattern — pure lib/, testable without hooks |
| Skill-to-cycle mapping | Static dict `SKILL_TO_CYCLE` in cycle_state.py | Only 3 lifecycle cycles exist; static is simpler than dynamic import. Easy to extend. |
| Schema handling | `setdefault` for `phase_history` and `active_queue` | Handles both 4-field (current live) and 6-field (clear_cycle_state normalized) schemas (critique A1) |
| Unrecognized skills | Return False silently | Fail-permissive per AC#4; ceremony skills (retro-cycle etc.) intentionally excluded (critique A2) |
| Import strategy | Late imports inside function body | `cycle_runner.CYCLE_PHASES` and `governance_events.log_phase_transition` imported at call time to avoid hook-level import errors |
| `just set-cycle` compat | No changes to justfile | Both write same JSON keys; last writer wins; sequential execution prevents races (critique A4) |

### Input/Output Examples

**Before (manual):**
```
Agent reads SKILL.md: "On Entry: just set-cycle implementation-cycle DO WORK-168"
Agent executes: Bash("just set-cycle implementation-cycle DO WORK-168")
Cost: ~500 tokens (reading instruction + tool call)
```

**After (automatic):**
```
PostToolUse fires after Skill(skill="implementation-cycle") completes
Part 8: advance_cycle_phase("implementation-cycle")
  Reads: session_state.current_phase = "PLAN"
  Writes: session_state.current_phase = "DO"
  Logs: CyclePhaseEntered(phase="DO", work_id="WORK-168", agent="PostToolUse-auto")
Cost: 0 agent tokens
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Missing slim file | Return False | Test 7 |
| 4-field session_state (no phase_history) | `setdefault` creates fields | Test 5 |
| Unrecognized skill (retro-cycle etc.) | Return False, no state change | Test 3 |
| Already at last phase (CHAIN) | Return False | Test 4 |
| current_phase not in CYCLE_PHASES sequence | Return False (ValueError caught) | Implicit in Test 3 |
| Null current_phase | Return False | Implicit in Test 7 |
| governance_events import fails | Silently skip logging | Inner try/except in advance_cycle_phase |

### Open Questions

**Q: Should ceremony skills (retro-cycle, close-work-cycle) also auto-advance?**

No. Ceremony phases are in `CEREMONY_PHASES` (ceremony_runner.py), not `CYCLE_PHASES`. WORK-171 (Mechanical Phase Migration) may extend this later. For now, only the 3 lifecycle cycles are supported.

---

## Open Decisions (MUST resolve before implementation)

<!-- Decisions from work item's operator_decisions field.
     If ANY row has [BLOCKED] in Chosen column, plan-validation-cycle will BLOCK.

     POPULATE FROM: Work item frontmatter `operator_decisions` field
     - question -> Decision column
     - options -> Options column
     - chosen -> Chosen column (null = [BLOCKED])
     - rationale -> Rationale column (filled when resolved) -->

**SKIPPED:** No operator decisions required. All design choices are driven by existing patterns (session_end_actions.py, CYCLE_PHASES dict) and critique mitigations (A1-A3).

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_cycle_state.py` with all 7 tests
- [ ] Verify all tests fail (red) — module doesn't exist yet

### Step 2: Implement `lib/cycle_state.py`
- [ ] Create `.claude/haios/lib/cycle_state.py` with `advance_cycle_phase()`
- [ ] Include `SKILL_TO_CYCLE` mapping dict
- [ ] Include `_default_project_root()` following session_end_actions.py pattern
- [ ] Tests 1, 2, 3, 4, 5, 6, 7 pass (green)

### Step 3: Integrate PostToolUse Part 8
- [ ] Add Part 8 handler BETWEEN Part 0.5 (line 58) and the Edit/Write guard (line 60) in `post_tool_use.py`
- [ ] Include `sys.path` lib/ setup inside Part 8 try block (pattern: `Path(__file__).parent.parent / "haios" / "lib"`)
- [ ] Include early `return` after Skill processing (matches Part 0.5 pattern)
- [ ] Verify existing Parts 0-7 unchanged (no line shifts break them)

### Step 4: Integration Verification
- [ ] All 7 new tests pass
- [ ] Run full test suite (no regressions)
- [ ] Verify `just set-cycle` still works (manual override)

### Step 5: README Sync (MUST)
- [ ] **MUST:** Update lib/ README if one exists
- [ ] No parent directory structure changes

### Step 6: Consumer Verification
**SKIPPED:** This is additive code (new file + new Part). No migrations or renames. No existing consumers to update.

---

## Verification

- [ ] All 8 tests in `tests/test_cycle_state.py` pass
- [ ] Full test suite — no regressions
- [ ] `just set-cycle` still works as manual override
- [ ] `just clear-cycle` still clears all 6 fields
- [ ] **MUST:** lib/ README updated if exists

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Part 8 fires for non-lifecycle skills | Low | `SKILL_TO_CYCLE.get()` returns None; returns False silently |
| Schema mismatch (4 vs 6 fields) | Medium | `setdefault` normalizes on write (critique A1) |
| Import failure in hook subprocess | Low | All imports wrapped in try/except; fail-permissive |
| Race with `just set-cycle` | Low | Sequential agent execution; last-writer-wins is acceptable (critique A4) |

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

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-168/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| New file `lib/cycle_state.py` with `advance_cycle_phase()` function | [ ] | File exists, function defined |
| PostToolUse hook Part 8: auto-advance on lifecycle skill completion | [ ] | Part 8 added to post_tool_use.py |
| Governance event logged via existing `log_phase_transition()` | [ ] | Test verifies or manual check of events |
| Tests in `tests/test_cycle_state.py` for phase advancement logic | [ ] | pytest output shows all green |
| `just set-cycle` continues to work unchanged (manual override) | [ ] | Manual verification via Bash |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/cycle_state.py` | `advance_cycle_phase()` + `SKILL_TO_CYCLE` | [ ] | |
| `tests/test_cycle_state.py` | 7 tests covering all edge cases | [ ] | |
| `.claude/hooks/hooks/post_tool_use.py` | Part 8 added between Part 0.5 return (line 58) and Edit/Write guard (line 60) | [ ] | |
| `.claude/haios-status-slim.json` | session_state updated correctly by Part 8 | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest [test_file] -v
# Expected: X tests passed
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
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.
> **E2-290 Learning (Session 192):** "Tests pass" ≠ "Deliverables complete". Agent declared victory after tests passed but skipped 2 of 7 deliverables.

---

## References

- @docs/work/active/WORK-168/WORK.md (work item)
- @docs/work/active/WORK-160/WORK.md (parent — Ceremony Automation)
- @.claude/haios/lib/session_end_actions.py (pattern template)
- @.claude/haios/modules/cycle_runner.py (CYCLE_PHASES dict, line 103)
- @.claude/hooks/hooks/post_tool_use.py (integration target)
- @.claude/hooks/hooks/pre_tool_use.py:834 (confirms tool_name="Skill" for skill invocations)
- @.claude/haios/lib/governance_events.py (log_phase_transition, line 38)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-005, REQ-OBSERVE-001)
- Memory: 85390 (104% context budget problem)

---
