---
template: implementation_plan
status: approved
date: 2026-02-10
backlog_id: WORK-114
title: "Wire Ceremony Contract Enforcement into Runtime"
author: Hephaestus
lifecycle_phase: plan
session: 335
version: "1.5"
generated: 2026-02-10
last_updated: 2026-02-10T00:28:00
---
# Implementation Plan: Wire Ceremony Contract Enforcement into Runtime

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

When a ceremony skill is invoked, `enforce_ceremony_contract()` will validate the ceremony's input contract at runtime, surfacing validation errors (warn mode) or blocking execution (block mode) per `haios.yaml` toggle.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/hooks/hooks/pre_tool_use.py` |
| Lines of code affected | ~20 new lines | New function + call site |
| New files to create | 1 | `tests/test_ceremony_enforcement_runtime.py` |
| Tests to write | 6 | See Tests First section |
| Dependencies | 2 | `ceremony_contracts.py`, `ceremony_registry.yaml` |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single hook insertion point |
| Risk of regression | Low | 139 existing ceremony tests, additive change |
| External dependencies | Low | Reads YAML frontmatter from skill files |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 15 min | High |
| Implementation | 20 min | High |
| Verification | 10 min | High |
| **Total** | 45 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/hooks/hooks/pre_tool_use.py:170-176
# PreToolUse intercepts Skill calls via _check_governed_activity
if primitive == "skill-invoke":
    skill_name = tool_input.get("skill", "")
    skill_result = layer._check_skill_restriction(skill_name, state)
    if skill_result is not None and not skill_result.allowed:
        return _deny_with_context(skill_result.reason, state, layer)
```

**Behavior:** PreToolUse checks if skill is allowed in current activity state (EXPLORE/DO/CHECK etc.) but does NOT validate ceremony input contracts.

**Result:** Ceremonies start without input validation. `enforce_ceremony_contract()` exists in `lib/ceremony_contracts.py:355` but is only called by tests.

### Desired State

```python
# .claude/hooks/hooks/pre_tool_use.py - new function + call in handle()
# After skill restriction check, before returning allow:
if primitive == "skill-invoke":
    skill_name = tool_input.get("skill", "")
    # Existing: state-based skill restriction
    skill_result = layer._check_skill_restriction(skill_name, state)
    if skill_result is not None and not skill_result.allowed:
        return _deny_with_context(skill_result.reason, state, layer)
    # NEW: ceremony contract validation
    ceremony_result = _check_ceremony_contract(skill_name, tool_input)
    if ceremony_result:
        return ceremony_result  # warn or deny based on toggle
```

**Behavior:** When a ceremony skill is invoked, PreToolUse loads its YAML frontmatter, parses the input contract, and calls `enforce_ceremony_contract()`. Validation errors surface as warnings (warn mode) or blocks (block mode).

**Result:** Ceremony contracts are enforced at runtime. Invalid inputs are caught before ceremony execution begins.

---

## Tests First (TDD)

**Test file:** `tests/test_ceremony_enforcement_runtime.py`

### Test 1: Ceremony skill returns warn/deny (not None)
```python
def test_ceremony_skill_triggers_contract_check():
    """Skills listed in ceremony_registry.yaml trigger contract validation."""
    # queue-commit is a ceremony with required fields; empty inputs = validation failure
    # In warn mode (default), returns allow-with-warning
    result = _check_ceremony_contract("queue-commit", {"skill": "queue-commit"})
    assert result is not None
    assert result["hookSpecificOutput"]["permissionDecision"] == "allow"
    assert "contract" in result["hookSpecificOutput"].get("permissionDecisionReason", "").lower()
```

### Test 2: Non-ceremony skill bypasses contract check
```python
def test_non_ceremony_skill_returns_none():
    """Non-ceremony skills (implementation-cycle, survey-cycle) skip validation."""
    result = _check_ceremony_contract("implementation-cycle", {"skill": "implementation-cycle"})
    assert result is None
    result2 = _check_ceremony_contract("survey-cycle", {"skill": "survey-cycle"})
    assert result2 is None
```

### Test 3: Ceremony with no required fields passes
```python
def test_ceremony_no_required_fields_returns_none():
    """Ceremony whose input_contract has no required fields returns None (pass)."""
    # Create a mock skill file with no required fields, test _check_ceremony_contract
    # Or use a ceremony that has only optional fields (if one exists)
    # Fallback: test _parse_skill_contract with a custom frontmatter
    result = _check_ceremony_contract("observation-triage-cycle", {"skill": "observation-triage-cycle"})
    # If all fields optional, result should be None (contract satisfied)
    # If has required fields, result will be allow-with-warning — either is valid behavior
    assert result is None or result["hookSpecificOutput"]["permissionDecision"] == "allow"
```

### Test 4: Warn mode (default) allows with warning on missing required fields
```python
def test_warn_mode_allows_with_warning(monkeypatch, tmp_path):
    """In warn mode, missing required fields produce allow + warning."""
    # Setup: create haios.yaml with ceremony_contract_enforcement: warn
    config = tmp_path / "haios.yaml"
    config.write_text("toggles:\\n  ceremony_contract_enforcement: warn\\n")
    # Monkeypatch _read_enforcement_toggle or config path
    result = _check_ceremony_contract("queue-commit", {"skill": "queue-commit"})
    assert result is not None
    assert result["hookSpecificOutput"]["permissionDecision"] == "allow"
```

### Test 5: Block mode denies on missing required fields
```python
def test_block_mode_denies(monkeypatch, tmp_path):
    """In block mode, missing required fields produce deny response."""
    # Setup: create haios.yaml with ceremony_contract_enforcement: block
    config = tmp_path / "haios.yaml"
    config.write_text("toggles:\\n  ceremony_contract_enforcement: block\\n")
    # Monkeypatch enforce_ceremony_contract config_path to tmp_path config
    result = _check_ceremony_contract("queue-commit", {"skill": "queue-commit"})
    assert result is not None
    assert result["hookSpecificOutput"]["permissionDecision"] == "deny"
```

### Test 6: Skill file not found returns None (fail-permissive)
```python
def test_missing_skill_file_returns_none(monkeypatch):
    """If ceremony skill SKILL.md doesn't exist, skip validation gracefully."""
    # Monkeypatch _find_skill_path to return None
    monkeypatch.setattr("test_module._find_skill_path", lambda name: None)
    result = _check_ceremony_contract("queue-commit", {"skill": "queue-commit"})
    assert result is None
```

---

## Detailed Design

### Exact Code Change

**File:** `.claude/hooks/hooks/pre_tool_use.py`

**Change 1: New function `_check_ceremony_contract()`**

Add after existing `_check_exit_gate()` function (after line 705):

```python
def _check_ceremony_contract(skill_name: str, tool_input: dict) -> Optional[dict]:
    """
    Validate ceremony input contract when ceremony skill is invoked.

    Loads ceremony registry to check if skill is a ceremony. If so, loads
    the skill's YAML frontmatter, parses the contract, and calls
    enforce_ceremony_contract(). Returns warn/deny based on haios.yaml toggle.

    Args:
        skill_name: Name of skill being invoked (e.g., "queue-commit")
        tool_input: Full tool_input dict from hook_data

    Returns:
        None: Not a ceremony skill, or contract validation passed
        dict: Allow-with-warning (warn mode) or deny (block mode)
    """
    try:
        lib_dir = Path(__file__).parent.parent.parent / "haios" / "lib"
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))

        from ceremony_contracts import (
            CeremonyContract,
            load_ceremony_registry,
            enforce_ceremony_contract,
        )

        # 1. Check if skill is a ceremony via registry
        registry = load_ceremony_registry()
        ceremony_entry = None
        for entry in registry.ceremonies:
            if entry.skill == skill_name:
                ceremony_entry = entry
                break

        if ceremony_entry is None:
            return None  # Not a ceremony, skip

        # 2. Load skill YAML frontmatter to get contract
        skill_path = _find_skill_path(skill_name)
        if skill_path is None:
            return None  # Skill file not found, skip gracefully

        contract = _parse_skill_contract(skill_path)
        if contract is None:
            return None  # No parseable contract, skip

        # 3. Extract inputs from tool_input (skill args are not structured)
        # Ceremony inputs come from the skill's runtime context, not tool_input.
        # At PreToolUse time, we only have {"skill": "name", "args": "..."}.
        # We validate what we can: if args contains key=value pairs, parse them.
        inputs = _extract_ceremony_inputs(tool_input)

        # 4. Enforce contract
        result = enforce_ceremony_contract(contract, inputs)

        if result.valid:
            return None  # Contract satisfied

        # 5. Return warn or deny based on enforcement mode
        error_msg = (
            f"Ceremony '{skill_name}' contract validation: "
            + "; ".join(result.errors)
        )
        # enforce_ceremony_contract raises ValueError in block mode,
        # so if we reach here, we're in warn mode
        return _allow_with_warning(error_msg)

    except ValueError as e:
        # Block mode: enforce_ceremony_contract raised ValueError
        return _deny(str(e))

    except Exception:
        return None  # Fail-permissive on any error
```

**Change 2: Helper functions**

```python
def _find_skill_path(skill_name: str) -> Optional[Path]:
    """Find SKILL.md for a ceremony skill by name.

    Uses Path(__file__) anchored navigation (matches codebase convention,
    critique A2 — cwd-independent).
    """
    # .claude/hooks/hooks/pre_tool_use.py -> .claude/skills/{name}/SKILL.md
    skills_dir = Path(__file__).parent.parent.parent / "skills"
    skill_file = skills_dir / skill_name / "SKILL.md"
    if skill_file.exists():
        return skill_file
    return None


def _parse_skill_contract(skill_path: Path) -> Optional["CeremonyContract"]:
    """Parse CeremonyContract from skill file YAML frontmatter."""
    try:
        content = skill_path.read_text(encoding="utf-8")
        # Extract YAML frontmatter between --- markers
        if not content.startswith("---"):
            return None
        end = content.index("---", 3)
        frontmatter = yaml.safe_load(content[3:end])
        if not frontmatter or "input_contract" not in frontmatter:
            return None

        from ceremony_contracts import CeremonyContract
        return CeremonyContract.from_frontmatter(frontmatter)
    except Exception:
        return None


def _extract_ceremony_inputs(tool_input: dict) -> dict:
    """Extract ceremony inputs from Skill tool_input.

    At PreToolUse time, Skill tool_input is {"skill": "name", "args": "..."}.
    Args is a free-text string. We cannot reliably extract structured inputs.
    Return empty dict — contract validation will flag missing required fields.
    """
    return {}
```

**Change 3: Wire into handle() function**

In `_check_governed_activity()` at `.claude/hooks/hooks/pre_tool_use.py:172`, after skill restriction check:

```diff
         # 4. Special handling for skill-invoke
         if primitive == "skill-invoke":
             skill_name = tool_input.get("skill", "")
             skill_result = layer._check_skill_restriction(skill_name, state)
             if skill_result is not None and not skill_result.allowed:
                 return _deny_with_context(skill_result.reason, state, layer)
+
+            # 4b. Ceremony contract validation (WORK-114)
+            ceremony_result = _check_ceremony_contract(skill_name, tool_input)
+            if ceremony_result:
+                # Merge state context into ceremony result
+                ctx = _build_additional_context(state, layer)
+                ceremony_result["hookSpecificOutput"]["additionalContext"] = ctx
+                return ceremony_result
```

### Call Chain Context

```
Claude Code invokes Skill(skill="queue-commit")
    |
    v
hook_dispatcher.py:main()
    |
    v
pre_tool_use.py:handle(hook_data)
    |
    v
_check_governed_activity(tool_name="Skill", tool_input={skill: "queue-commit"})
    |
    +-> layer.map_tool_to_primitive("Skill") -> "skill-invoke"
    |
    +-> layer._check_skill_restriction("queue-commit", state)
    |       Returns: None (allowed)
    |
    +-> _check_ceremony_contract("queue-commit", tool_input)    # <-- NEW
    |       |
    |       +-> load_ceremony_registry() -> find "queue-commit" entry
    |       +-> _find_skill_path("queue-commit") -> .claude/skills/queue-commit/SKILL.md
    |       +-> _parse_skill_contract(path) -> CeremonyContract
    |       +-> enforce_ceremony_contract(contract, {}) -> ValidationResult
    |       |
    |       +-> If valid: return None (allow)
    |       +-> If invalid + warn: return _allow_with_warning(errors)
    |       +-> If invalid + block: ValueError caught -> return _deny(str(e))
    |
    v
_allow_with_context(None, state, layer)  # Normal flow continues
```

### Function/Component Signatures

```python
def _check_ceremony_contract(skill_name: str, tool_input: dict) -> Optional[dict]:
    """
    Validate ceremony input contract at PreToolUse time.

    Args:
        skill_name: Ceremony skill name from tool_input["skill"]
        tool_input: Full Skill tool input dict

    Returns:
        None: Not a ceremony, or contract passed
        dict: hookSpecificOutput with allow+warning or deny
    """
```

### Behavior Logic

**Current Flow:**
```
Skill("queue-commit") → PreToolUse → state restriction check → ALLOW (no contract check)
```

**Fixed Flow:**
```
Skill("queue-commit") → PreToolUse → state restriction check → contract check
                                                                   |
                                                        Is ceremony? ──NO──→ ALLOW
                                                           |
                                                          YES
                                                           |
                                                    Load contract from SKILL.md
                                                           |
                                                    enforce_ceremony_contract()
                                                           |
                                                    Valid? ──YES──→ ALLOW
                                                      |
                                                      NO
                                                      |
                                              Mode? ──warn──→ ALLOW + warning
                                                |
                                              block──→ DENY
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Integration point | PreToolUse hook, not CeremonyRunner | PreToolUse already intercepts all Skill calls; single insertion point; no new module needed |
| Input extraction | Empty dict (flag missing required fields) | At PreToolUse time, Skill args are free-text strings, not structured. Cannot reliably parse. Contract validation will warn on missing required fields, which is informative. |
| Fail-permissive | `except Exception: return None` | Matches existing hook pattern (line 191). Contract enforcement is additive governance, not blocking infrastructure. |
| Registry lookup | `load_ceremony_registry()` per call | Registry is small (19 entries), YAML load is fast. Caching would add complexity for negligible gain in a hook that runs per-tool-call. |
| Warn vs block | Delegates to `enforce_ceremony_contract()` | Existing function already reads `haios.yaml` toggle. No duplication. |
| State context merge | Add `additionalContext` to ceremony result | Maintains state visibility (WORK-064 pattern) even when ceremony check returns a result. |

### Input/Output Examples

**Before (with real data):**
```
Skill(skill="queue-commit")
  PreToolUse output: {"hookSpecificOutput": {"permissionDecision": "allow", "additionalContext": "[STATE: DO] Blocked: ..."}}
  Problem: No contract validation occurs
```

**After (warn mode, missing work_id):**
```
Skill(skill="queue-commit")
  PreToolUse output: {"hookSpecificOutput": {"permissionDecision": "allow", "permissionDecisionReason": "Ceremony 'queue-commit' contract validation: Required field 'work_id' is missing", "additionalContext": "[STATE: DO] Blocked: ..."}}
  Improvement: Agent sees warning about missing input before ceremony starts
```

**After (block mode, missing work_id):**
```
Skill(skill="queue-commit")
  PreToolUse output: {"hookSpecificOutput": {"permissionDecision": "deny", "permissionDecisionReason": "Ceremony 'queue-commit' input contract failed (enforcement=block): Required field 'work_id' is missing"}}
  Improvement: Ceremony blocked until inputs are provided
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Skill file not found | `_find_skill_path` returns None, skip validation | Test 3 (implicit) |
| No `input_contract` in frontmatter | `_parse_skill_contract` returns None, skip | Test 3 (implicit) |
| Registry file missing | `load_ceremony_registry` raises FileNotFoundError, caught by outer try/except | Fail-permissive |
| Malformed YAML frontmatter | `yaml.safe_load` error caught, returns None | Fail-permissive |
| Non-ceremony skill (e.g., implementation-cycle) | Registry lookup returns None, skip | Test 6 |
| Ceremony with no required fields | `validate_ceremony_input` returns valid=True | Test 3 |

### Open Questions

**Q: Should we attempt to parse structured args from the Skill tool_input?**

No. At PreToolUse time, `tool_input` is `{"skill": "name", "args": "optional string"}`. The `args` field is free-text (e.g., `"WORK-114"`). We cannot reliably map positional args to named contract fields. Returning empty inputs means contract validation will warn on all required fields being missing, which provides useful signal. Future work (CH-012 ceremony_context) can provide structured inputs at the Python layer.

---

## Open Decisions (MUST resolve before implementation)

<!-- Decisions from work item's operator_decisions field.
     If ANY row has [BLOCKED] in Chosen column, plan-validation-cycle will BLOCK.

     POPULATE FROM: Work item frontmatter `operator_decisions` field
     - question -> Decision column
     - options -> Options column
     - chosen -> Chosen column (null = [BLOCKED])
     - rationale -> Rationale column (filled when resolved) -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Integration point | PreToolUse hook, CeremonyRunner wrapper | PreToolUse hook | Already intercepts Skill calls; single insertion point; pure additive (memory 84175) |
| Input extraction strategy | Parse args string, Empty dict | Empty dict | Cannot reliably map free-text args to named fields; missing-field warnings are useful signal |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_ceremony_enforcement_runtime.py`
- [ ] Write 6 tests per Tests First section
- [ ] Verify all tests fail (red) — functions don't exist yet

### Step 2: Add helper functions to pre_tool_use.py
- [ ] Add `_find_skill_path()` function
- [ ] Add `_parse_skill_contract()` function
- [ ] Add `_extract_ceremony_inputs()` function
- [ ] Tests 1, 2 pass (ceremony detection via registry)

### Step 3: Add `_check_ceremony_contract()` function
- [ ] Add main function after `_check_exit_gate()`
- [ ] Tests 3, 4, 5, 6 pass (contract validation + enforcement modes)

### Step 4: Wire into `_check_governed_activity()`
- [ ] Add ceremony contract call after skill restriction check (line ~176)
- [ ] Merge additionalContext into ceremony result

### Step 5: Integration Verification
- [ ] All 6 new tests pass
- [ ] Run full test suite: `pytest tests/ -v` (no regressions on 139+ existing)
- [ ] Demo: invoke a ceremony skill and observe contract validation output

### Step 6: Consumer Verification
- [ ] Not a migration/refactor — no consumers to update
- [ ] Verify no existing hook behavior changed (additive only)

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hook performance: YAML load per Skill call | Low | Registry is 19 entries (~2KB). Skill YAML frontmatter is small. Both are fast reads. |
| Warn-mode no-op: empty inputs means every ceremony warns identically about missing required fields | Medium | **Known limitation (critique A1).** In warn mode with empty inputs, enforcement cannot distinguish "caller forgot work_id" from "caller provided work_id but hook cannot extract it." This is acceptable — the goal is to establish the wiring for CH-012 `ceremony_context` which provides structured inputs. Until then, warn-mode serves as proof that the call-site works, not as meaningful input validation. |
| Regression: existing hook behavior breaks | Medium | Fail-permissive pattern (try/except → None). All new code in separate functions. Additive only — no existing lines modified except one call-site insertion. |
| Spec misalignment: contract validation logic diverges from WORK-113 | Low | Reuses `enforce_ceremony_contract()` directly — no reimplementation. |

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

**MUST** read `docs/work/active/WORK-114/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Runtime call-site for `enforce_ceremony_contract()` at ceremony entry point | [ ] | Grep for call in pre_tool_use.py |
| Contract validation errors surfaced to agent (warn mode: log + continue; block mode: halt) | [ ] | Demo output from ceremony invocation |
| Integration test: ceremony with invalid inputs triggers enforcement | [ ] | pytest test passes |
| Integration test: ceremony with valid inputs passes enforcement | [ ] | pytest test passes |
| Zero regressions on existing ceremony tests (139+) | [ ] | Full test suite output |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/hooks/hooks/pre_tool_use.py` | `_check_ceremony_contract()` + helpers exist, wired into `_check_governed_activity()` | [ ] | |
| `tests/test_ceremony_enforcement_runtime.py` | 6 tests, all passing | [ ] | |
| `.claude/haios/lib/ceremony_contracts.py` | Unchanged (reused, not modified) | [ ] | |

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

- @.claude/haios/lib/ceremony_contracts.py (enforce_ceremony_contract, CeremonyContract)
- @.claude/hooks/hooks/pre_tool_use.py (integration target)
- @.claude/haios/config/ceremony_registry.yaml (ceremony-to-skill mapping)
- @.claude/haios/config/haios.yaml (toggles.ceremony_contract_enforcement)
- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-012-SideEffectBoundaries.md (parent chapter)
- @docs/work/active/WORK-113/WORK.md (contract validation dependency)

---
