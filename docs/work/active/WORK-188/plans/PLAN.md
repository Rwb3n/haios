---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-22
backlog_id: WORK-188
title: "Hook Auto-Injection for Phase Contracts"
author: Hephaestus
lifecycle_phase: plan
session: 422
generated: 2026-02-22
last_updated: 2026-02-22T11:24:42

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-188/WORK.md"
    required: true
  - field: source_files_exist
    verify: "all paths in WORK.md source_files exist on disk"
    required: true

output_contract:
  - field: layer_0_complete
    verify: "Layer 0 tables have no placeholder rows"
  - field: layer_1_complete
    verify: "Layer 1 has concrete code blocks, not pseudocode"
  - field: layer_2_complete
    verify: "every step has input/action/output/verify fields"
  - field: layer_3_complete
    verify: "every verification line has a command and expected output"
---
# Implementation Plan: Hook Auto-Injection for Phase Contracts

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification.

     SKIP RATIONALE: If ANY section is omitted, provide one-line rationale:
     **SKIPPED:** [reason] -->

---

## Goal

Extend PostToolUse and UserPromptSubmit hooks to auto-inject the current phase's behavioral contract from `.claude/skills/{cycle}/phases/{PHASE}.md` after each phase transition and on every prompt, with graceful degradation when phase files are missing.

---

## Open Decisions

<!-- No operator_decisions in WORK-188 frontmatter — section not applicable. -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| No open decisions | — | — | WORK-188 has no operator_decisions field; all design choices are pre-resolved in ADR-048 |

---

## Layer 0: Inventory

<!-- MUST complete before any design work. Map the blast radius.
     Producer: plan-author agent
     Consumer: all downstream agents (DO, CHECK, critique) -->

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/haios/lib/cycle_state.py` | MODIFY | 2 |
| `.claude/hooks/hooks/post_tool_use.py` | MODIFY | 2 |
| `.claude/hooks/hooks/user_prompt_submit.py` | MODIFY | 2 |

### Consumer Files

<!-- read_phase_contract is a new shared helper; no existing consumers to update.
     PostToolUse and UserPromptSubmit already exist — no external references change. -->

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `tests/test_cycle_state.py` | imports advance_cycle_phase from cycle_state | 19 | NO CHANGE — existing tests unaffected by additive new function |
| `tests/test_hooks.py` | imports post_tool_use and user_prompt_submit helpers | 503-514 | NO CHANGE — existing tests unaffected |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_phase_contract_injection.py` | CREATE | New test file for all 8 injection tests |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 1 | Test file |
| Files to modify | 3 | cycle_state.py, post_tool_use.py, user_prompt_submit.py |
| Tests to write | 8 | Test Files table |
| Total blast radius | 4 | 3 modified + 1 created |

**Note (critique A4):** Only `implementation-cycle` has fractured phase files (WORK-187). `investigation-cycle` and `plan-authoring-cycle` have no `phases/` directory yet. Injection is correctly fall-permissive (returns None) for those cycles. ADR-048 token savings are realized incrementally as each cycle is fractured.

---

## Layer 1: Specification

<!-- The contract that the DO agent implements.
     Producer: plan-author agent
     Consumer: DO agent -->

### Current State

```python
# .claude/haios/lib/cycle_state.py — lines 38-130
# advance_cycle_phase() returns bool only; no phase content is returned.
# PostToolUse Part 8 (post_tool_use.py lines 62-75):
#   - calls advance_cycle_phase(skill_name)
#   - if advanced: appends "[CYCLE] Auto-advanced phase after {skill_name}" to messages
#   - returns early — no phase file content is injected

# user_prompt_submit.py handle() — lines 86-115:
#   - Part 2.5: _get_session_state_warning() warns when active_cycle is null
#   - No phase contract injection exists
```

**Behavior:** Phase transitions log a text string "[CYCLE] Auto-advanced phase after ...". On every prompt, UserPromptSubmit injects date, session warning, lifecycle guidance, and RFC2119 reminders — but no phase contract.

**Problem:** The agent must load the full monolithic SKILL.md to know its phase contract. ADR-048 specifies hook injection to deliver only the current phase's contract, reducing per-phase token cost by ~80%.

### Desired State

```python
# .claude/haios/lib/cycle_state.py — NEW function added at end of file

def read_phase_contract(
    cycle_name: str,
    phase_name: str,
    project_root: Optional[Path] = None,
) -> Optional[str]:
    """Read phase contract file for the given cycle and phase.

    Falls back gracefully: returns None if file not found or any error.
    Never raises.

    Args:
        cycle_name: Lifecycle cycle name (e.g., "implementation-cycle")
        phase_name: Phase name uppercase (e.g., "DO", "PLAN", "CHECK")
        project_root: Project root path. Defaults to derived path.

    Returns:
        File content as string, or None if missing/error (fall-permissive).
    """
    try:
        root = project_root or _default_project_root()
        phase_file = root / ".claude" / "skills" / cycle_name / "phases" / f"{phase_name}.md"
        if not phase_file.exists():
            return None
        return phase_file.read_text(encoding="utf-8")
    except Exception:
        return None


# .claude/hooks/hooks/post_tool_use.py — Part 8 modification (lines 62-75)
# BEFORE:
    if tool_name == "Skill":
        skill_name = hook_data.get("tool_input", {}).get("skill", "")
        if skill_name:
            try:
                lib_dir = Path(__file__).parent.parent.parent / "haios" / "lib"
                if str(lib_dir) not in sys.path:
                    sys.path.insert(0, str(lib_dir))
                from cycle_state import advance_cycle_phase
                advanced = advance_cycle_phase(skill_name)
                if advanced:
                    messages.append(f"[CYCLE] Auto-advanced phase after {skill_name}")
            except Exception:
                pass  # Fail-permissive: never break hook chain
        return "\n".join(messages) if messages else None

# AFTER:
    if tool_name == "Skill":
        skill_name = hook_data.get("tool_input", {}).get("skill", "")
        if skill_name:
            try:
                lib_dir = Path(__file__).parent.parent.parent / "haios" / "lib"
                if str(lib_dir) not in sys.path:
                    sys.path.insert(0, str(lib_dir))
                from cycle_state import advance_cycle_phase, read_phase_contract
                advanced = advance_cycle_phase(skill_name)
                if advanced:
                    messages.append(f"[CYCLE] Auto-advanced phase after {skill_name}")
                    # Inject phase contract for the new phase
                    try:
                        slim_file = Path(__file__).parent.parent.parent.parent / ".claude" / "haios-status-slim.json"
                        slim = json.loads(slim_file.read_text(encoding="utf-8"))
                        session_state = slim.get("session_state", {})
                        new_phase = session_state.get("current_phase")
                        cycle_key = session_state.get("active_cycle")
                        if new_phase and cycle_key:
                            contract = read_phase_contract(cycle_key, new_phase)
                            if contract:
                                messages.append(f"\n--- Phase Contract: {cycle_key}/{new_phase} ---\n{contract}\n---")
                    except Exception:
                        pass  # Fail-permissive: injection failure is non-fatal
            except Exception:
                pass  # Fail-permissive: never break hook chain
        return "\n".join(messages) if messages else None


# .claude/hooks/hooks/user_prompt_submit.py — NEW Part 2.6 after Part 2.5 (lines 89-93)
# Added between "Part 2.5: Session state warning" and "Part 3: Dynamic thresholds"

    # Part 2.6: Phase contract injection (WORK-188, ADR-048)
    phase_contract = _get_phase_contract(cwd)
    if phase_contract:
        output_parts.append("")
        output_parts.append(phase_contract)


# NEW function added to user_prompt_submit.py:
def _get_phase_contract(cwd: str) -> Optional[str]:
    """
    Inject current phase's behavioral contract from phase file.

    ADR-048: Belt-and-suspenders injection. Reads haios-status-slim.json for
    active_cycle + current_phase, then reads
    .claude/skills/{cycle}/phases/{PHASE}.md.

    Fall-permissive: returns None if no active cycle, phase file missing, or any error.

    Args:
        cwd: Working directory path

    Returns:
        Formatted phase contract string, or None if not applicable.
    """
    if not cwd:
        return None

    slim_path = Path(cwd) / ".claude" / "haios-status-slim.json"
    if not slim_path.exists():
        return None

    try:
        slim = json.loads(slim_path.read_text(encoding="utf-8-sig"))
        session_state = slim.get("session_state", {})
        active_cycle = session_state.get("active_cycle")
        current_phase = session_state.get("current_phase")

        if not active_cycle or not current_phase:
            return None

        phase_file = Path(cwd) / ".claude" / "skills" / active_cycle / "phases" / f"{current_phase}.md"
        if not phase_file.exists():
            return None

        content = phase_file.read_text(encoding="utf-8")
        return f"--- Phase Contract: {active_cycle}/{current_phase} ---\n{content}\n---"
    except Exception:
        return None
```

**Behavior:** After each phase transition, the agent receives the new phase's contract in the hook output. On every prompt, if an active cycle is running, the current phase contract is injected into context. Both paths are fall-permissive.

**Result:** Agents enter each phase with the relevant behavioral contract already in context. Per ADR-048: ~80% token reduction per lifecycle phase invocation vs loading full monolithic SKILL.md.

### Tests

<!-- Write test specs BEFORE implementation code.
     Each test: name, file, setup, assertion. -->

#### Test 1: read_phase_contract — existing file returns content
- **file:** `tests/test_phase_contract_injection.py`
- **function:** `test_read_phase_contract_returns_content(tmp_path)`
- **setup:** Create `.claude/skills/implementation-cycle/phases/DO.md` with `"# DO Phase\nDo stuff"` in tmp_path; call `read_phase_contract("implementation-cycle", "DO", project_root=tmp_path)`
- **assertion:** Result is `"# DO Phase\nDo stuff"` (exact file content)

#### Test 2: read_phase_contract — missing file returns None
- **file:** `tests/test_phase_contract_injection.py`
- **function:** `test_read_phase_contract_missing_file_returns_none(tmp_path)`
- **setup:** Create `.claude/skills/implementation-cycle/phases/` directory but no PLAN.md; call `read_phase_contract("implementation-cycle", "PLAN", project_root=tmp_path)`
- **assertion:** Result is None (fall-permissive)

#### Test 3: read_phase_contract — missing cycle directory returns None
- **file:** `tests/test_phase_contract_injection.py`
- **function:** `test_read_phase_contract_missing_cycle_dir_returns_none(tmp_path)`
- **setup:** No `.claude/skills/` directory at all; call `read_phase_contract("nonexistent-cycle", "DO", project_root=tmp_path)`
- **assertion:** Result is None (fall-permissive, no exception)

#### Test 4: PostToolUse Skill handler injects phase content after advance
- **file:** `tests/test_phase_contract_injection.py`
- **function:** `test_posttooluse_injects_phase_contract_after_advance(tmp_path, monkeypatch)`
- **setup:**
  - Create slim JSON in `tmp_path/.claude/haios-status-slim.json` with `session_state: {active_cycle: "implementation-cycle", current_phase: "DO", work_id: "WORK-188", entered_at: "..."}`
  - Create `.claude/skills/implementation-cycle/phases/DO.md` with content `"# DO Phase"`
  - Monkeypatch `advance_cycle_phase` to return True (simulating advance already happened and slim already updated to new phase)
  - Test via `handle()` directly: call `handle(hook_data)` where `hook_data` has `tool_name="Skill"` and `tool_input={"skill": "implementation-cycle"}`
- **assertion:** Return value contains `"Phase Contract: implementation-cycle/DO"` and `"# DO Phase"`

#### Test 5: PostToolUse Skill handler gracefully handles missing phase file
- **file:** `tests/test_phase_contract_injection.py`
- **function:** `test_posttooluse_missing_phase_file_no_crash(tmp_path, monkeypatch)`
- **setup:**
  - Create slim JSON with valid session_state (active_cycle: "implementation-cycle", current_phase: "DO")
  - No phase file created
  - Monkeypatch `advance_cycle_phase` to return True
- **assertion:** No exception raised; return value contains `"[CYCLE] Auto-advanced"` but no phase contract content

#### Test 6: UserPromptSubmit injects phase content when active cycle exists
- **file:** `tests/test_phase_contract_injection.py`
- **function:** `test_user_prompt_submit_injects_phase_contract(tmp_path)`
- **setup:**
  - Create slim JSON with `session_state: {active_cycle: "implementation-cycle", current_phase: "DO"}`
  - Create `.claude/skills/implementation-cycle/phases/DO.md` with `"# DO Phase"`
  - Import `_get_phase_contract` from user_prompt_submit; call with `str(tmp_path)`
- **assertion:** Result contains `"Phase Contract: implementation-cycle/DO"` and `"# DO Phase"`

#### Test 7: UserPromptSubmit skips injection when no active cycle
- **file:** `tests/test_phase_contract_injection.py`
- **function:** `test_user_prompt_submit_no_active_cycle_returns_none(tmp_path)`
- **setup:**
  - Create slim JSON with `session_state: {active_cycle: null, current_phase: null}`
  - Call `_get_phase_contract(str(tmp_path))`
- **assertion:** Result is None

#### Test 8: UserPromptSubmit skips injection when phase file missing
- **file:** `tests/test_phase_contract_injection.py`
- **function:** `test_user_prompt_submit_missing_phase_file_returns_none(tmp_path)`
- **setup:**
  - Create slim JSON with `session_state: {active_cycle: "implementation-cycle", current_phase: "DO"}`
  - No phase file in skills directory
  - Call `_get_phase_contract(str(tmp_path))`
- **assertion:** Result is None

### Design

#### File 1 (MODIFY): `.claude/haios/lib/cycle_state.py`

**Location:** Append after line 172 (end of file, after `sync_work_md_phase`)

**Current Code (end of file):**
```python
# .claude/haios/lib/cycle_state.py lines 168-172
        work_file.write_text(updated, encoding="utf-8")
        return True
    except Exception:
        return False
```

**Target Code (append after line 172):**
```python
        work_file.write_text(updated, encoding="utf-8")
        return True
    except Exception:
        return False


def read_phase_contract(
    cycle_name: str,
    phase_name: str,
    project_root: Optional[Path] = None,
) -> Optional[str]:
    """Read phase contract file for the given cycle and phase.

    Reads from .claude/skills/{cycle_name}/phases/{phase_name}.md.
    Fall-permissive: returns None if file not found or any error. Never raises.

    Args:
        cycle_name: Lifecycle cycle name (e.g., "implementation-cycle")
        phase_name: Phase name in uppercase (e.g., "DO", "PLAN", "CHECK")
        project_root: Project root path. Defaults to derived path.

    Returns:
        File content as string, or None if missing or error.
    """
    try:
        root = project_root or _default_project_root()
        phase_file = (
            root / ".claude" / "skills" / cycle_name / "phases" / f"{phase_name}.md"
        )
        if not phase_file.exists():
            return None
        return phase_file.read_text(encoding="utf-8")
    except Exception:
        return None
```

**Diff:**
```diff
         work_file.write_text(updated, encoding="utf-8")
         return True
     except Exception:
         return False
+
+
+def read_phase_contract(
+    cycle_name: str,
+    phase_name: str,
+    project_root: Optional[Path] = None,
+) -> Optional[str]:
+    """Read phase contract file for the given cycle and phase.
+
+    Reads from .claude/skills/{cycle_name}/phases/{phase_name}.md.
+    Fall-permissive: returns None if file not found or any error. Never raises.
+
+    Args:
+        cycle_name: Lifecycle cycle name (e.g., "implementation-cycle")
+        phase_name: Phase name in uppercase (e.g., "DO", "PLAN", "CHECK")
+        project_root: Project root path. Defaults to derived path.
+
+    Returns:
+        File content as string, or None if missing or error.
+    """
+    try:
+        root = project_root or _default_project_root()
+        phase_file = (
+            root / ".claude" / "skills" / cycle_name / "phases" / f"{phase_name}.md"
+        )
+        if not phase_file.exists():
+            return None
+        return phase_file.read_text(encoding="utf-8")
+    except Exception:
+        return None
```

#### File 2 (MODIFY): `.claude/hooks/hooks/post_tool_use.py`

**Location:** Part 8 block, lines 62-75

**Current Code:**
```python
    # Part 8: Cycle phase auto-advancement (WORK-168)
    if tool_name == "Skill":
        skill_name = hook_data.get("tool_input", {}).get("skill", "")
        if skill_name:
            try:
                lib_dir = Path(__file__).parent.parent.parent / "haios" / "lib"
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

**Target Code:**
```python
    # Part 8: Cycle phase auto-advancement (WORK-168) + phase contract injection (WORK-188)
    if tool_name == "Skill":
        skill_name = hook_data.get("tool_input", {}).get("skill", "")
        if skill_name:
            try:
                lib_dir = Path(__file__).parent.parent.parent / "haios" / "lib"
                if str(lib_dir) not in sys.path:
                    sys.path.insert(0, str(lib_dir))
                from cycle_state import advance_cycle_phase, read_phase_contract
                advanced = advance_cycle_phase(skill_name)
                if advanced:
                    messages.append(f"[CYCLE] Auto-advanced phase after {skill_name}")
                    # Inject phase contract for the new phase (WORK-188, ADR-048)
                    try:
                        slim_file = (
                            Path(__file__).parent.parent.parent.parent
                            / ".claude" / "haios-status-slim.json"
                        )
                        slim = json.loads(slim_file.read_text(encoding="utf-8"))
                        session_state = slim.get("session_state", {})
                        new_phase = session_state.get("current_phase")
                        cycle_key = session_state.get("active_cycle")
                        if new_phase and cycle_key:
                            contract = read_phase_contract(cycle_key, new_phase)
                            if contract:
                                messages.append(
                                    f"\n--- Phase Contract: {cycle_key}/{new_phase} ---\n"
                                    f"{contract}\n---"
                                )
                    except Exception:
                        pass  # Fail-permissive: injection failure is non-fatal
            except Exception:
                pass  # Fail-permissive: never break hook chain
        return "\n".join(messages) if messages else None
```

**Diff:**
```diff
     # Part 8: Cycle phase auto-advancement (WORK-168)
+    # Part 8: Cycle phase auto-advancement (WORK-168) + phase contract injection (WORK-188)
     if tool_name == "Skill":
         skill_name = hook_data.get("tool_input", {}).get("skill", "")
         if skill_name:
             try:
                 lib_dir = Path(__file__).parent.parent.parent / "haios" / "lib"
                 if str(lib_dir) not in sys.path:
                     sys.path.insert(0, str(lib_dir))
-                from cycle_state import advance_cycle_phase
+                from cycle_state import advance_cycle_phase, read_phase_contract
                 advanced = advance_cycle_phase(skill_name)
                 if advanced:
                     messages.append(f"[CYCLE] Auto-advanced phase after {skill_name}")
+                    # Inject phase contract for the new phase (WORK-188, ADR-048)
+                    try:
+                        slim_file = (
+                            Path(__file__).parent.parent.parent.parent
+                            / ".claude" / "haios-status-slim.json"
+                        )
+                        slim = json.loads(slim_file.read_text(encoding="utf-8"))
+                        session_state = slim.get("session_state", {})
+                        new_phase = session_state.get("current_phase")
+                        cycle_key = session_state.get("active_cycle")
+                        if new_phase and cycle_key:
+                            contract = read_phase_contract(cycle_key, new_phase)
+                            if contract:
+                                messages.append(
+                                    f"\n--- Phase Contract: {cycle_key}/{new_phase} ---\n"
+                                    f"{contract}\n---"
+                                )
+                    except Exception:
+                        pass  # Fail-permissive: injection failure is non-fatal
             except Exception:
                 pass  # Fail-permissive: never break hook chain
         return "\n".join(messages) if messages else None
```

#### File 3 (MODIFY): `.claude/hooks/hooks/user_prompt_submit.py`

**Location A — handle() function body:** New Part 2.6 injected between lines 93 and 95 (between Part 2.5 and Part 3)

**Current Code (handle() body, lines 89-100):**
```python
    # Part 2.5: Session state warning (E2-287)
    session_warning = _get_session_state_warning(cwd)
    if session_warning:
        output_parts.append("")
        output_parts.append(session_warning)

    # Part 3: Dynamic thresholds
    # DISABLED Session 259: ...
```

**Target Code:**
```python
    # Part 2.5: Session state warning (E2-287)
    session_warning = _get_session_state_warning(cwd)
    if session_warning:
        output_parts.append("")
        output_parts.append(session_warning)

    # Part 2.6: Phase contract injection (WORK-188, ADR-048)
    phase_contract = _get_phase_contract(cwd)
    if phase_contract:
        output_parts.append("")
        output_parts.append(phase_contract)

    # Part 3: Dynamic thresholds
    # DISABLED Session 259: ...
```

**Location B — new function:** Append `_get_phase_contract()` after `_get_session_state_warning()` (after line 166)

**Current Code (end of _get_session_state_warning, lines 163-166):**
```python
        return None
    except Exception:
        return None


def _get_vitals(cwd: str) -> Optional[str]:
```

**Target Code:**
```python
        return None
    except Exception:
        return None


def _get_phase_contract(cwd: str) -> Optional[str]:
    """
    Inject current phase's behavioral contract from phase file.

    ADR-048 belt-and-suspenders: on every prompt, if an active lifecycle cycle
    is running, read and inject the current phase's contract file so the agent
    always has the behavioral contract in context (recovery after compaction).

    Phase files live at: .claude/skills/{cycle}/phases/{PHASE}.md

    Fall-permissive: returns None if no active cycle, phase file missing, or any error.

    Args:
        cwd: Working directory path

    Returns:
        Formatted phase contract string, or None if not applicable.
    """
    if not cwd:
        return None

    slim_path = Path(cwd) / ".claude" / "haios-status-slim.json"
    if not slim_path.exists():
        return None

    try:
        slim = json.loads(slim_path.read_text(encoding="utf-8-sig"))
        session_state = slim.get("session_state", {})
        active_cycle = session_state.get("active_cycle")
        current_phase = session_state.get("current_phase")

        if not active_cycle or not current_phase:
            return None

        phase_file = (
            Path(cwd) / ".claude" / "skills" / active_cycle / "phases" / f"{current_phase}.md"
        )
        if not phase_file.exists():
            return None

        content = phase_file.read_text(encoding="utf-8")
        return f"--- Phase Contract: {active_cycle}/{current_phase} ---\n{content}\n---"
    except Exception:
        return None


def _get_vitals(cwd: str) -> Optional[str]:
```

### Call Chain

```
UserPromptSubmit event
    |
    +-> handle(hook_data)
    |       |
    |       +-> _get_session_state_warning(cwd)   # Part 2.5 (existing)
    |       +-> _get_phase_contract(cwd)           # Part 2.6 (NEW)
    |               |
    |               +-> reads haios-status-slim.json
    |               +-> reads .claude/skills/{cycle}/phases/{PHASE}.md
    |               Returns: str (contract) | None (fall-permissive)
    |
    Returns: context string injected before Claude sees prompt

PostToolUse event (tool_name == "Skill")
    |
    +-> handle(hook_data)
    |       |
    |       +-> advance_cycle_phase(skill_name)    # existing
    |       |       Returns: bool
    |       +-> [if advanced] reads haios-status-slim.json for new phase
    |       +-> read_phase_contract(cycle_key, new_phase)  # NEW call
    |               |
    |               +-> reads .claude/skills/{cycle}/phases/{PHASE}.md
    |               Returns: str (contract) | None (fall-permissive)
    |
    Returns: messages string appended to hook output
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Where to add `read_phase_contract` | `cycle_state.py` lib module | Co-location with `advance_cycle_phase`. Both functions share the same domain (phase lifecycle state). Consistent with module-first pattern. |
| How PostToolUse gets new phase after advance | Re-read slim JSON after `advance_cycle_phase()` returns True | Avoids changing `advance_cycle_phase()` signature (bool → str would break 8 existing tests). Slim file is already written by advance; re-reading is safe and consistent with how UserPromptSubmit reads it. |
| `read_phase_contract` project_root parameter | Optional, defaults to `_default_project_root()` | Same pattern as `advance_cycle_phase`. Makes function testable with tmp_path without needing real filesystem structure. |
| Path derivation in PostToolUse for slim file | `Path(__file__).parent.parent.parent.parent / ".claude" / "haios-status-slim.json"` | Follows existing `_default_project_root()` logic: lib/ → haios/ → .claude/ → project root. PostToolUse is in `.claude/hooks/hooks/`, so 4 parents = project root. |
| `utf-8-sig` in UserPromptSubmit vs `utf-8` in PostToolUse | UserPromptSubmit uses `utf-8-sig` (matches existing `_get_session_state_warning`); PostToolUse uses `utf-8` (matches existing Skill handler slim read pattern) | Consistency with surrounding code in each file. BOM handling is already in `_get_session_state_warning`. |
| Fall-permissive at every level | All new code wrapped in try/except returning None | ADR-048 explicit requirement. Hooks must never crash the agent. Phase injection is an enhancement, not a requirement for hook operation. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| Phase file does not exist | `read_phase_contract` returns None; hook skips injection | Test 2, Test 5, Test 8 |
| Cycle directory does not exist | `read_phase_contract` returns None (path.exists() = False) | Test 3 |
| `advance_cycle_phase` returns False (no advance) | PostToolUse skips contract injection block entirely (guarded by `if advanced:`) | Implicit — no explicit test; code path is trivially correct |
| `session_state.active_cycle` is null | `_get_phase_contract` returns None early | Test 7 |
| `session_state.current_phase` is null | `_get_phase_contract` returns None early | Test 7 |
| slim file missing | Both injection paths return None | Covered by existing tests (graceful fail) |
| slim file read error | Caught by outer try/except; returns None | Implicit in all tests |
| Phase file encoding error | Caught by outer try/except; returns None | Implicit coverage |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| PostToolUse path derivation wrong for slim file | M | Verified: hooks file is at `.claude/hooks/hooks/post_tool_use.py`. Path(__file__).parent × 4 = project root. Matches `_default_project_root()` in `cycle_state.py` (lib/ → haios/ → .claude/ → project root, same 4 levels from different start). Added explicit path in test setup. |
| Phase file injection makes hook output very large | L | Phase files are ~3-4K chars per ADR-048 audit. Hook output is `additionalContext` which Claude handles. PostToolUse fires only on Skill tool — rare event. UserPromptSubmit fires every prompt but phase file is the point. |
| Existing test_hooks.py tests break | L | Additive changes only. New function `_get_phase_contract` is only injected when active_cycle is set AND phase file exists. Existing tests use `/nonexistent/path` or real project root where phase files may or may not exist — returns None in both cases. |
| `advance_cycle_phase` race: slim written before re-read | L | `advance_cycle_phase` is synchronous. It writes slim then returns True. Re-read happens in same process immediately after. No race condition. |

---

## Layer 2: Implementation Steps

<!-- Ordered steps. Each step is a sub-agent delegation unit. -->

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Create `tests/test_phase_contract_injection.py` from Layer 1 Tests section (all 8 tests)
- **output:** Test file exists, all 8 tests fail (functions not yet implemented)
- **verify:** `pytest tests/test_phase_contract_injection.py -v 2>&1 | grep -c "FAILED\|ERROR"` equals 8

### Step 2: Implement read_phase_contract (GREEN — cycle_state.py)
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY) `.claude/haios/lib/cycle_state.py`
- **input:** Step 1 complete (tests exist and fail)
- **action:** Append `read_phase_contract()` function to end of `cycle_state.py` per target code
- **output:** Tests 1, 2, 3 pass; tests 4-8 still fail
- **verify:** `pytest tests/test_phase_contract_injection.py::test_read_phase_contract_returns_content tests/test_phase_contract_injection.py::test_read_phase_contract_missing_file_returns_none tests/test_phase_contract_injection.py::test_read_phase_contract_missing_cycle_dir_returns_none -v` all pass

### Step 3: Integrate PostToolUse injection (GREEN — post_tool_use.py)
- **spec_ref:** Layer 1 > Design > File 2 (MODIFY) `.claude/hooks/hooks/post_tool_use.py`
- **input:** Step 2 complete
- **action:** Modify Part 8 block in `post_tool_use.py` per target code (import `read_phase_contract`, add slim re-read + injection block)
- **output:** Tests 4, 5 pass
- **verify:** `pytest tests/test_phase_contract_injection.py::test_posttooluse_injects_phase_contract_after_advance tests/test_phase_contract_injection.py::test_posttooluse_missing_phase_file_no_crash -v` both pass

### Step 4: Integrate UserPromptSubmit injection (GREEN — user_prompt_submit.py)
- **spec_ref:** Layer 1 > Design > File 3 (MODIFY) `.claude/hooks/hooks/user_prompt_submit.py`
- **input:** Step 3 complete
- **action:** Add `_get_phase_contract()` function to `user_prompt_submit.py` and add Part 2.6 call in `handle()` per target code
- **output:** Tests 6, 7, 8 pass; all 8 tests green
- **verify:** `pytest tests/test_phase_contract_injection.py -v` shows 8 passed, 0 failed

### Step 5: Full regression check
- **spec_ref:** Layer 0 > Consumer Files
- **input:** Step 4 complete (all 8 new tests green)
- **action:** Run full test suite to confirm no regressions
- **output:** All existing tests still pass
- **verify:** `pytest tests/ -v 2>&1 | tail -5` shows 0 new failures vs baseline (1571 passed)

---

## Ground Truth Verification

<!-- Computable verification protocol. -->

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_phase_contract_injection.py -v` | 8 passed, 0 failed |
| `pytest tests/ -v 2>&1 \| tail -5` | 0 new failures vs baseline (1571+ passed) |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| PostToolUse injects phase contract after advance_cycle_phase | `grep "read_phase_contract" .claude/hooks/hooks/post_tool_use.py` | 1+ match |
| UserPromptSubmit injects current phase contract on every prompt | `grep "_get_phase_contract" .claude/hooks/hooks/user_prompt_submit.py` | 2+ matches (function def + call site) |
| Injection reads from .claude/skills/{cycle}/phases/{phase}.md | `grep "skills.*phases" .claude/haios/lib/cycle_state.py` | 1+ match |
| Graceful degradation if phase file missing | `pytest tests/test_phase_contract_injection.py::test_read_phase_contract_missing_file_returns_none -v` | 1 passed |
| Existing tests still pass | `pytest tests/test_cycle_state.py tests/test_hooks.py -v` | All pass, 0 failed |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| read_phase_contract importable from cycle_state | `grep "def read_phase_contract" .claude/haios/lib/cycle_state.py` | 1 match |
| PostToolUse Part 8 imports read_phase_contract | `grep "from cycle_state import advance_cycle_phase, read_phase_contract" .claude/hooks/hooks/post_tool_use.py` | 1 match |
| UserPromptSubmit Part 2.6 call site present | `grep "phase_contract = _get_phase_contract" .claude/hooks/hooks/user_prompt_submit.py` | 1 match |
| No stale import of advance_cycle_phase alone | `grep "from cycle_state import advance_cycle_phase$" .claude/hooks/hooks/post_tool_use.py` | 0 matches |

### Completion Criteria (DoD)

- [ ] All 8 new tests pass (Layer 2 Step 4 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] No regressions in existing test suite (Step 5)
- [ ] `read_phase_contract` importable from `cycle_state` (Consumer Integrity)
- [ ] PostToolUse Part 8 injects phase content after advance (Deliverables table)
- [ ] UserPromptSubmit Part 2.6 injects phase content on every prompt (Deliverables table)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- ADR-048: `docs/ADR/ADR-048-progressive-contracts-phase-per-file-skill-fracturing.md`
- WORK-188: `docs/work/active/WORK-188/WORK.md`
- WORK-168: Cycle phase auto-advancement (PostToolUse Part 8 — existing code this plan extends)
- WORK-187: Phase file fracturing (produces phase files this plan reads)
- cycle_state.py: `.claude/haios/lib/cycle_state.py`
- post_tool_use.py: `.claude/hooks/hooks/post_tool_use.py`
- user_prompt_submit.py: `.claude/hooks/hooks/user_prompt_submit.py`
- Memory: 85815 (context-switching token cost — ADR-048 motivation)

---
