---
template: implementation_plan
status: complete
date: 2026-02-20
backlog_id: WORK-169
title: "Critique-as-Hook"
author: Hephaestus
lifecycle_phase: plan
session: 408
version: "1.5"
generated: 2026-02-20
last_updated: 2026-02-20T19:15:00
---
# Implementation Plan: Critique-as-Hook

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Done: mem:84334 (pure additive hook pattern), mem:86037 (critique-as-hook concept) |
| Document design decisions | MUST | See Key Design Decisions table |
| Ground truth metrics | MUST | wc -l on all source files, Glob for file counts |

---

## Goal

PreToolUse hook automatically detects inhale-to-exhale lifecycle transitions and injects tier-appropriate critique guidance via `additionalContext`, eliminating the need for agents to manually read and follow critique instructions from ceremony SKILL.md files.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `pre_tool_use.py` (918 lines), `governance_events.py` (446 lines) |
| Lines of code affected | ~30 | Single call-site insertion in pre_tool_use.py + 1 new log function |
| New files to create | 2 | `lib/critique_injector.py`, `tests/test_critique_injector.py` |
| Tests to write | 10 | 4 tiers x 2 transition types + fallback + regression |
| Dependencies | 2 | `tier_detector.py`, `governance_events.py` |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Med | pre_tool_use.py (hook), tier_detector.py (lib), governance_events.py (lib) |
| Risk of regression | Low | Pure additive pattern (mem:84334) -- new function + single call-site, no existing code modified |
| External dependencies | Low | Only reads haios-status-slim.json (local file) |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 20 min | High |
| critique_injector.py | 30 min | High |
| pre_tool_use.py integration | 10 min | High |
| governance_events.py log function | 5 min | High |
| **Total** | **~65 min** | High |

---

## Current State vs Desired State

### Current State

```python
# pre_tool_use.py:178-183 - Skill-invoke handling
        # 4. Special handling for skill-invoke
        if primitive == "skill-invoke":
            skill_name = tool_input.get("skill", "")
            skill_result = layer._check_skill_restriction(skill_name, state)
            if skill_result is not None and not skill_result.allowed:
                return _deny_with_context(skill_result.reason, state, layer)

            # 4b. Ceremony contract validation (WORK-114)
            ceremony_result = _check_ceremony_contract(skill_name, tool_input)
            if ceremony_result:
                # Merge state context into ceremony result
                ctx = _build_additional_context(state, layer)
                ceremony_result["hookSpecificOutput"]["additionalContext"] = ctx
                return ceremony_result
```

**Behavior:** When agent invokes a skill, hook checks skill restrictions and ceremony contracts. No critique injection occurs.

**Result:** Critique depends entirely on agents reading implementation-cycle SKILL.md and manually invoking `Task(subagent_type='critique-agent')`. Easily skipped. Costs agent tokens.

### Desired State

```python
# pre_tool_use.py:178+ - Skill-invoke handling with critique injection
        if primitive == "skill-invoke":
            skill_name = tool_input.get("skill", "")
            skill_result = layer._check_skill_restriction(skill_name, state)
            if skill_result is not None and not skill_result.allowed:
                return _deny_with_context(skill_result.reason, state, layer)

            # 4b. Ceremony contract validation (WORK-114)
            ceremony_result = _check_ceremony_contract(skill_name, tool_input)
            if ceremony_result:
                ctx = _build_additional_context(state, layer)
                ceremony_result["hookSpecificOutput"]["additionalContext"] = ctx
                return ceremony_result

            # 4c. Critique injection (WORK-169)
            critique_ctx = _check_critique_injection(skill_name)
            if critique_ctx:
                return critique_ctx
```

**Behavior:** After existing checks pass, hook detects inhale-to-exhale transitions and injects tier-appropriate critique guidance into `additionalContext`.

**Result:** Agent automatically receives critique guidance without reading SKILL.md. Zero manual steps. Tier-proportional.

---

## Tests First (TDD)

### Test 1: Trivial tier produces no injection
```python
def test_trivial_tier_no_injection(monkeypatch):
    """Trivial work items get no critique injection."""
    monkeypatch.setattr(critique_injector, "_get_current_phase", lambda: "PLAN")
    monkeypatch.setattr(critique_injector, "_get_current_work_id_for_critique", lambda: "WORK-999")
    monkeypatch.setattr(tier_detector, "detect_tier", lambda wid, **kw: "trivial")
    result = compute_critique_injection("implementation-cycle")
    assert result is None
```

### Test 2: Small tier produces checklist injection
```python
def test_small_tier_checklist_injection(monkeypatch):
    """Small work items get checklist injected as additionalContext."""
    monkeypatch.setattr(critique_injector, "_get_current_phase", lambda: "PLAN")
    monkeypatch.setattr(critique_injector, "_get_current_work_id_for_critique", lambda: "WORK-100")
    monkeypatch.setattr(tier_detector, "detect_tier", lambda wid, **kw: "small")
    result = compute_critique_injection("implementation-cycle")
    assert result is not None
    assert "checklist" in result.lower() or "verify" in result.lower()
```

### Test 3: Standard tier produces full subagent instruction
```python
def test_standard_tier_full_subagent(monkeypatch):
    """Standard work items get instruction to invoke critique-agent subagent."""
    monkeypatch.setattr(critique_injector, "_get_current_phase", lambda: "PLAN")
    monkeypatch.setattr(critique_injector, "_get_current_work_id_for_critique", lambda: "WORK-100")
    monkeypatch.setattr(tier_detector, "detect_tier", lambda wid, **kw: "standard")
    result = compute_critique_injection("implementation-cycle")
    assert result is not None
    assert "critique-agent" in result
```

### Test 4: Architectural tier produces operator dialogue instruction
```python
def test_architectural_tier_operator_dialogue(monkeypatch):
    """Architectural work items get critique-agent + operator confirmation."""
    monkeypatch.setattr(critique_injector, "_get_current_phase", lambda: "PLAN")
    monkeypatch.setattr(critique_injector, "_get_current_work_id_for_critique", lambda: "WORK-100")
    monkeypatch.setattr(tier_detector, "detect_tier", lambda wid, **kw: "architectural")
    result = compute_critique_injection("implementation-cycle")
    assert result is not None
    assert "critique-agent" in result
    assert "operator" in result.lower() or "AskUserQuestion" in result
```

### Test 5: Non-transition skill produces no injection
```python
def test_non_transition_skill_no_injection(monkeypatch):
    """Skills that are not inhale-to-exhale transitions produce no injection."""
    monkeypatch.setattr(critique_injector, "_get_current_phase", lambda: "DO")
    result = compute_critique_injection("retro-cycle")
    assert result is None
```

### Test 6: EXPLORE-to-HYPOTHESIZE transition (investigation)
```python
def test_explore_to_hypothesize_transition(monkeypatch):
    """Investigation cycle EXPLORE->HYPOTHESIZE triggers critique injection."""
    monkeypatch.setattr(critique_injector, "_get_current_phase", lambda: "EXPLORE")
    monkeypatch.setattr(critique_injector, "_get_current_work_id_for_critique", lambda: "WORK-100")
    monkeypatch.setattr(tier_detector, "detect_tier", lambda wid, **kw: "standard")
    result = compute_critique_injection("investigation-cycle")
    assert result is not None
```

### Test 7: Unknown work_id defaults to standard tier
```python
def test_unknown_work_id_defaults_standard(monkeypatch):
    """Unresolvable work_id defaults to standard tier, not silent skip."""
    monkeypatch.setattr(critique_injector, "_get_current_phase", lambda: "PLAN")
    monkeypatch.setattr(critique_injector, "_get_current_work_id_for_critique", lambda: "unknown")
    # detect_tier("unknown") returns "standard" because file doesn't exist
    result = compute_critique_injection("implementation-cycle")
    assert result is not None  # Standard tier = full subagent
```

### Test 8: Unknown phase defaults to no injection (fail-permissive)
```python
def test_unknown_phase_no_injection(monkeypatch):
    """Unresolvable phase produces no injection (fail-permissive)."""
    monkeypatch.setattr(critique_injector, "_get_current_phase", lambda: "unknown")
    result = compute_critique_injection("implementation-cycle")
    assert result is None
```

### Test 9: detect_tier exception handled fail-permissive
```python
def test_detect_tier_exception_defaults_standard(monkeypatch):
    """detect_tier() exception produces standard injection + warning event."""
    monkeypatch.setattr(critique_injector, "_get_current_phase", lambda: "PLAN")
    monkeypatch.setattr(critique_injector, "_get_current_work_id_for_critique", lambda: "WORK-100")
    monkeypatch.setattr(tier_detector, "detect_tier", lambda wid, **kw: (_ for _ in ()).throw(RuntimeError("test")))
    result = compute_critique_injection("implementation-cycle")
    assert result is not None  # Falls back to standard
```

### Test 10: Existing PreToolUse behavior unchanged
```python
def test_existing_pretooluse_behavior_unchanged():
    """Verify existing governance checks still fire first (regression guard)."""
    # SQL block still works
    from pre_tool_use import handle
    result = handle({"tool_name": "Bash", "tool_input": {"command": "SELECT * FROM concepts"}})
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
```

---

## Detailed Design

### Exact Code Change

**File 1:** `.claude/haios/lib/critique_injector.py` (NEW)

```python
"""
Critique injection for PreToolUse hook (WORK-169).

Pure function to compute tier-appropriate critique guidance for
inhale-to-exhale lifecycle transitions.

Pattern: session_end_actions.py / tier_detector.py (fail-permissive,
_default_project_root, no exceptions escape).
"""
import json
from pathlib import Path
from typing import Optional


# Inhale phases: gathering, exploring, planning (input)
# Exhale phases: committing, executing, producing (output)
# Inhale: gathering, exploring, planning, specifying (input phases)
INHALE_PHASES = {"EXPLORE", "PLAN", "DESIGN", "SCAN"}
# Exhale: committing, executing, producing, validating (output phases)
EXHALE_PHASES = {"DO", "HYPOTHESIZE", "CHECK", "DONE", "SPECIFY", "ASSESS", "RANK", "COMMIT", "VERIFY", "JUDGE", "REPORT"}

# Skill-to-lifecycle mapping: which skills trigger transition detection.
# Only includes skills tracked by cycle_state.py SKILL_TO_CYCLE (PostToolUse
# writes phase data for these). design-review-validation excluded: not in
# SKILL_TO_CYCLE, so phase data would be stale (critique A2).
TRANSITION_SKILLS = {
    "implementation-cycle",
    "investigation-cycle",
    "plan-authoring-cycle",
}

# Tier -> injection content
TIER_INJECTIONS = {
    "trivial": None,  # No injection
    "small": (
        "[CRITIQUE CHECKPOINT] Before proceeding to the next phase, verify:\n"
        "- [ ] All acceptance criteria are achievable with current design\n"
        "- [ ] Source files referenced in WORK.md exist and are correct\n"
        "- [ ] No implicit assumptions about interfaces or data formats\n"
        "- [ ] Edge cases identified (empty inputs, missing files, permission errors)\n"
        "- [ ] Fail-permissive pattern applied where appropriate"
    ),
    "standard": (
        "[CRITIQUE REQUIRED] MUST invoke critique-agent before proceeding:\n"
        "Task(subagent_type='critique-agent', model='sonnet', "
        "prompt='Critique plan: docs/work/active/{work_id}/plans/PLAN.md')\n"
        "Apply critique-revise loop: PROCEED -> continue, REVISE -> fix + re-critique, "
        "BLOCK -> return to plan-authoring."
    ),
    "architectural": (
        "[CRITIQUE + OPERATOR REQUIRED] MUST invoke critique-agent AND get operator approval:\n"
        "1. Task(subagent_type='critique-agent', model='opus', "
        "prompt='Critique plan: docs/work/active/{work_id}/plans/PLAN.md')\n"
        "2. After critique passes, MUST use AskUserQuestion to confirm approach with operator.\n"
        "Architectural changes require explicit operator sign-off before DO phase."
    ),
}


def _default_project_root() -> Path:
    """Derive project root from this file's location.
    lib/ -> haios/ -> .claude/ -> project root."""
    return Path(__file__).parent.parent.parent.parent


def _get_current_phase(project_root: Optional[Path] = None) -> str:
    """Get current lifecycle phase from haios-status-slim.json.

    Returns phase string (e.g., "PLAN", "DO") or "unknown" on failure.
    """
    try:
        root = project_root or _default_project_root()
        slim_file = root / ".claude" / "haios-status-slim.json"
        if not slim_file.exists():
            return "unknown"
        data = json.loads(slim_file.read_text(encoding="utf-8"))
        phase = data.get("session_state", {}).get("current_phase")
        return phase if phase else "unknown"
    except Exception:
        return "unknown"


def _get_current_work_id_for_critique(project_root: Optional[Path] = None) -> str:
    """Get current work_id from haios-status-slim.json.

    Returns work_id string or "unknown" on failure.
    """
    try:
        root = project_root or _default_project_root()
        slim_file = root / ".claude" / "haios-status-slim.json"
        if not slim_file.exists():
            return "unknown"
        data = json.loads(slim_file.read_text(encoding="utf-8"))
        work_id = data.get("session_state", {}).get("work_id")
        return work_id if work_id else "unknown"
    except Exception:
        return "unknown"


def _is_inhale_to_exhale(current_phase: str, skill_name: str) -> bool:
    """Determine if invoking this skill at this phase is an inhale-to-exhale transition.

    The hook fires BEFORE the phase advances. So if we're in an inhale phase
    and the skill is a lifecycle skill, the next invocation will move to an
    exhale phase. This is the transition point where critique should fire.
    """
    if skill_name not in TRANSITION_SKILLS:
        return False
    if current_phase in INHALE_PHASES:
        return True
    return False


def compute_critique_injection(
    skill_name: str,
    project_root: Optional[Path] = None,
) -> Optional[str]:
    """Compute tier-appropriate critique injection text for a skill invocation.

    Called by PreToolUse hook when a lifecycle skill is invoked. Determines
    whether the current phase is an inhale-to-exhale transition, reads the
    governance tier, and returns the appropriate injection text.

    Args:
        skill_name: Name of the skill being invoked.
        project_root: Project root. Defaults to derived path.

    Returns:
        Injection text string for additionalContext, or None if no injection needed.
    """
    try:
        root = project_root or _default_project_root()

        # 1. Get current phase
        current_phase = _get_current_phase(root)
        if current_phase == "unknown":
            return None  # Can't determine transition, fail-permissive

        # 2. Check if this is an inhale-to-exhale transition
        if not _is_inhale_to_exhale(current_phase, skill_name):
            return None

        # 3. Get work_id and tier
        work_id = _get_current_work_id_for_critique(root)

        # Import tier_detector (sibling in lib/)
        import sys
        lib_dir = Path(__file__).parent
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))
        from tier_detector import detect_tier

        tier = detect_tier(work_id, project_root=root)

        # 4. Get injection template
        injection = TIER_INJECTIONS.get(tier)
        if injection is None:
            return None

        # 5. Format with work_id
        formatted = injection.replace("{work_id}", work_id)

        # 6. Log governance event (fail-permissive)
        _log_critique_injection(work_id, tier, current_phase, skill_name)

        return formatted

    except Exception:
        # Fail-permissive: on any error, default to standard injection
        try:
            work_id = _get_current_work_id_for_critique(project_root)
            _log_critique_warning(work_id, "exception_in_compute")
            injection = TIER_INJECTIONS.get("standard", "")
            return injection.replace("{work_id}", work_id) if injection else None
        except Exception:
            return None


def _log_critique_injection(work_id: str, tier: str, phase: str, skill: str) -> None:
    """Log CritiqueInjected governance event. Fail-permissive."""
    try:
        from governance_events import log_critique_injected
        log_critique_injected(work_id, tier, phase, skill)
    except Exception:
        pass


def _log_critique_warning(work_id: str, reason: str) -> None:
    """Log GovernanceWarning for critique injection failure. Fail-permissive."""
    try:
        from governance_events import log_gate_violation
        log_gate_violation("critique_injection", work_id, "warn", f"Critique injection fallback: {reason}")
    except Exception:
        pass
```

**File 2:** `.claude/hooks/hooks/pre_tool_use.py` -- single call-site insertion

**Location:** Lines 186-191 in `_check_governed_activity()`, after ceremony contract check

**Current Code:**
```python
            # 4b. Ceremony contract validation (WORK-114)
            ceremony_result = _check_ceremony_contract(skill_name, tool_input)
            if ceremony_result:
                # Merge state context into ceremony result
                ctx = _build_additional_context(state, layer)
                ceremony_result["hookSpecificOutput"]["additionalContext"] = ctx
                return ceremony_result
```

**Changed Code:**
```python
            # 4b. Ceremony contract validation (WORK-114)
            ceremony_result = _check_ceremony_contract(skill_name, tool_input)
            if ceremony_result:
                # Merge state context into ceremony result
                ctx = _build_additional_context(state, layer)
                ceremony_result["hookSpecificOutput"]["additionalContext"] = ctx
                return ceremony_result

            # 4c. Critique injection (WORK-169)
            critique_ctx = _check_critique_injection(skill_name)
            if critique_ctx:
                # Merge critique injection with state context
                base_ctx = _build_additional_context(state, layer)
                merged_ctx = f"{base_ctx}\n{critique_ctx}"
                return {
                    "hookSpecificOutput": {
                        "hookEventName": "PreToolUse",
                        "permissionDecision": "allow",
                        "additionalContext": merged_ctx,
                    }
                }
```

**Diff:**
```diff
             ceremony_result["hookSpecificOutput"]["additionalContext"] = ctx
                 return ceremony_result
+
+            # 4c. Critique injection (WORK-169)
+            critique_ctx = _check_critique_injection(skill_name)
+            if critique_ctx:
+                # Merge critique injection with state context
+                base_ctx = _build_additional_context(state, layer)
+                merged_ctx = f"{base_ctx}\n{critique_ctx}"
+                return {
+                    "hookSpecificOutput": {
+                        "hookEventName": "PreToolUse",
+                        "permissionDecision": "allow",
+                        "additionalContext": merged_ctx,
+                    }
+                }
```

**File 3:** New function in `pre_tool_use.py` (top-level helper):

```python
def _check_critique_injection(skill_name: str) -> Optional[str]:
    """Check if critique injection is needed for this skill invocation (WORK-169).

    Delegates to critique_injector.compute_critique_injection(). Fail-permissive.

    Returns:
        Critique injection text, or None if no injection needed.
    """
    try:
        lib_dir = Path(__file__).parent.parent.parent / "haios" / "lib"
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))

        from critique_injector import compute_critique_injection
        return compute_critique_injection(skill_name)
    except Exception:
        return None  # Fail-permissive
```

**File 4:** New log function in `governance_events.py`:

```python
def log_critique_injected(work_id: str, tier: str, phase: str, skill: str) -> dict:
    """Log CritiqueInjected governance event.

    Args:
        work_id: Work item ID.
        tier: Governance tier (trivial/small/standard/architectural).
        phase: Current lifecycle phase.
        skill: Skill that triggered the injection.

    Returns:
        Event dict.
    """
    event = {
        "type": "CritiqueInjected",
        "work_id": work_id,
        "tier": tier,
        "phase": phase,
        "skill": skill,
        "timestamp": datetime.now().isoformat(),
    }
    _append_event(event)
    return event
```

### Call Chain Context

```
handle(hook_data)                           # pre_tool_use.py:55
    |
    +-> _check_governed_activity()          # pre_tool_use.py:146
    |       |
    |       +-> skill-invoke branch         # pre_tool_use.py:179
    |       |       |
    |       |       +-> _check_skill_restriction()     # existing
    |       |       +-> _check_ceremony_contract()     # existing (WORK-114)
    |       |       +-> _check_critique_injection()    # NEW (WORK-169)
    |       |               |
    |       |               +-> compute_critique_injection()  # lib/critique_injector.py
    |       |                       |
    |       |                       +-> _get_current_phase()       # reads haios-status-slim.json
    |       |                       +-> _is_inhale_to_exhale()     # phase classification
    |       |                       +-> detect_tier()              # lib/tier_detector.py
    |       |                       +-> log_critique_injected()    # lib/governance_events.py
    |       |
    |       +-> check_activity()            # existing
```

### Function/Component Signatures

```python
def compute_critique_injection(
    skill_name: str,
    project_root: Optional[Path] = None,
) -> Optional[str]:
    """Compute tier-appropriate critique injection text.

    Args:
        skill_name: Name of the skill being invoked (e.g., "implementation-cycle").
        project_root: Project root path. Defaults to derived path.

    Returns:
        Injection text string for additionalContext, or None if no injection needed.
        Never raises -- all exceptions caught and handled fail-permissive.
    """
```

### Behavior Logic

```
Skill invoked → _check_critique_injection(skill_name)
                    |
                    +→ Is skill in TRANSITION_SKILLS?
                          |
                          ├─ NO → return None (not a lifecycle skill)
                          └─ YES → _get_current_phase()
                                    |
                                    +→ Is phase in INHALE_PHASES?
                                          |
                                          ├─ NO → return None (not a transition point)
                                          └─ YES → detect_tier(work_id)
                                                    |
                                                    +→ TIER_INJECTIONS[tier]
                                                          |
                                                          ├─ trivial → None
                                                          ├─ small → checklist text
                                                          ├─ standard → critique-agent instruction
                                                          └─ architectural → critique-agent + operator
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Integration point | PreToolUse skill-invoke branch (line 179+) | Existing interception point for skill governance; pure additive (mem:84334) |
| Phase resolution | Read `haios-status-slim.json` session_state.current_phase | Same file `cycle_state.py` already reads; no subprocess call needed unlike `_get_current_work_id()` |
| New lib file vs extend pre_tool_use.py | New `lib/critique_injector.py` | Follows session_end_actions.py/tier_detector.py pattern: pure function in lib/, testable without hook infrastructure |
| Fail-permissive behavior | Exception in detect_tier() -> default to standard + log warning | Standard is conservative safe default (same as tier_detector.py invariant). Warning via _log_violation() provides observability. |
| Checklist content | Static but domain-specific items | Covers the 5 most common critique findings from E2.6-E2.8 (acceptance criteria validity, path existence, implicit assumptions, edge cases, fail-permissive). Not boilerplate. |
| Injection merging | Append critique to existing state context | `f"{base_ctx}\n{critique_ctx}"` preserves `[STATE: PLAN] Blocked: ...` while adding critique guidance |

### Input/Output Examples

**Before (current behavior):**
```
Agent invokes: Skill(skill="implementation-cycle")
Hook returns: {"hookSpecificOutput": {"permissionDecision": "allow", "additionalContext": "[STATE: PLAN] Blocked: notebook-edit, shell-background"}}
No critique guidance injected.
```

**After (with WORK-169):**
```
Agent invokes: Skill(skill="implementation-cycle")
Current phase: PLAN (inhale)
Work item: WORK-169 (effort=medium, has plan -> standard tier)
Hook returns: {"hookSpecificOutput": {"permissionDecision": "allow", "additionalContext": "[STATE: PLAN] Blocked: notebook-edit, shell-background\n[CRITIQUE REQUIRED] MUST invoke critique-agent before proceeding:\nTask(subagent_type='critique-agent', model='sonnet', prompt='Critique plan: docs/work/active/WORK-169/plans/PLAN.md')\nApply critique-revise loop: PROCEED -> continue, REVISE -> fix + re-critique, BLOCK -> return to plan-authoring."}}
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Phase is "unknown" (slim file missing/unreadable) | Return None (no injection) | Test 8 |
| Work_id is "unknown" | detect_tier returns "standard" (file not found) | Test 7 |
| detect_tier raises exception | Catch, log warning, default to standard injection | Test 9 |
| Non-lifecycle skill (e.g., "retro-cycle") | Not in TRANSITION_SKILLS, return None | Test 5 |
| Phase is exhale (e.g., "DO") | Not in INHALE_PHASES, return None | Test 5 variant |
| slim JSON malformed | _get_current_phase returns "unknown", no injection | Covered by Test 8 |

### Open Questions

**Q: Should DESIGN phase be inhale or exhale?**
DESIGN is inhale (gathering/specifying). The exhale would be COMPLETE (committing the design). This matches the design lifecycle: EXPLORE -> SPECIFY -> CRITIQUE -> COMPLETE.

**Q: Should retro-cycle and close-work-cycle trigger critique?**
No. They are ceremony skills, not lifecycle skills. They operate after the work is already done. Critique is about assumption surfacing before commitment, not post-hoc review.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| No operator_decisions in WORK-169 | N/A | N/A | All design decisions resolved during plan authoring |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_critique_injector.py` with all 10 tests
- [ ] Verify all tests fail (red) -- module doesn't exist yet

### Step 2: Create critique_injector.py
- [ ] Create `.claude/haios/lib/critique_injector.py` with full implementation
- [ ] Tests 1-9 pass (green)

### Step 3: Add log_critique_injected to governance_events.py
- [ ] Add `log_critique_injected()` function to `governance_events.py`
- [ ] Verify critique_injector.py logging path works

### Step 4: Integrate into pre_tool_use.py
- [ ] Add `_check_critique_injection()` helper function
- [ ] Add call-site after ceremony contract check (line 191+)
- [ ] Test 10 (regression) passes

### Step 5: Integration Verification
- [ ] All 10 tests pass
- [ ] Run full test suite (no regressions)
- [ ] Demo: invoke implementation-cycle while in PLAN phase, verify additionalContext contains critique guidance

### Step 6: README Sync (MUST)
- [ ] Update `.claude/haios/lib/README.md` with critique_injector.py entry
- [ ] Verify README content matches actual file state

### Step 7: Consumer Verification
- [ ] Not a migration/refactor -- no stale references to check
- [ ] Verify pre_tool_use.py is the only consumer of critique_injector.py (by design)

---

## Verification

- [ ] Tests pass (10 new + full regression suite)
- [ ] **MUST:** All READMEs current
- [ ] Demo shows critique injection in additionalContext

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hook subprocess timeout reading slim JSON | Low | File read is <1ms; same file read by cycle_state.py in production |
| Critique injection noise for every skill invocation | Low | Only fires for lifecycle skills in inhale phases; trivial tier produces no injection |
| Phase classification wrong (DESIGN as exhale) | Medium | DESIGN is in INHALE_PHASES; validated against all 5 lifecycle definitions in CLAUDE.md |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 408 | 2026-02-20 | - | Plan authored | Critique-revise loop complete (2 rounds) |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-169/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| New file `lib/critique_injector.py` with `compute_critique_injection()` | [ ] | File exists, function exported |
| Phase resolution via `haios-status-slim.json` | [ ] | `_get_current_phase()` reads session_state.current_phase |
| Work_id resolution via existing mechanism | [ ] | `_get_current_work_id_for_critique()` reads session_state.work_id |
| PreToolUse hook handler for transition detection | [ ] | `_check_critique_injection()` in pre_tool_use.py |
| Tier-based injection via additionalContext | [ ] | TIER_INJECTIONS dict with 4 tiers |
| Fail-permissive with GovernanceWarning via _log_violation() | [ ] | try/except in compute_critique_injection with _log_critique_warning |
| Governance event logged (CritiqueInjected) | [ ] | log_critique_injected() in governance_events.py |
| Tests in tests/test_critique_injector.py | [ ] | 10 tests covering all tiers and transitions |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/critique_injector.py` | compute_critique_injection() exists | [ ] | |
| `.claude/hooks/hooks/pre_tool_use.py` | _check_critique_injection() call-site at line ~193 | [ ] | |
| `.claude/haios/lib/governance_events.py` | log_critique_injected() exists | [ ] | |
| `tests/test_critique_injector.py` | 10 tests, all passing | [ ] | |
| `.claude/haios/lib/README.md` | critique_injector.py listed | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_critique_injector.py -v
# Expected: 10 tests passed
```

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **MUST:** All WORK.md deliverables verified complete
- [ ] **Runtime consumer exists** (pre_tool_use.py calls compute_critique_injection)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated
- [ ] Ground Truth Verification completed above

---

## References

- @docs/work/active/WORK-169/WORK.md (work item)
- @docs/work/active/WORK-160/WORK.md (parent)
- @docs/work/active/WORK-167/WORK.md (tier detection dependency)
- @.claude/hooks/hooks/pre_tool_use.py (integration target)
- @.claude/haios/lib/tier_detector.py (tier computation)
- @.claude/haios/lib/governance_events.py (event logging)
- @.claude/haios/lib/cycle_state.py (phase advancement pattern reference)
- Memory: 84334 (pure additive hook pattern), 86037 (critique-as-hook concept), 85390 (104% problem)

---
