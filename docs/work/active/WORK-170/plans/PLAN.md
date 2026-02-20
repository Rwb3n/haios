---
template: implementation_plan
status: complete
date: 2026-02-20
backlog_id: WORK-170
title: "Checkpoint Field Auto-Population"
author: Hephaestus
lifecycle_phase: plan
session: 409
version: "1.5"
generated: 2026-02-20
last_updated: 2026-02-20T20:32:58
---
# Implementation Plan: Checkpoint Field Auto-Population

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Done: mem:85582 (hook noise), mem:86727 (PostToolUse constraint) |
| Document design decisions | MUST | Filled below |
| Ground truth metrics | MUST | Based on actual file reads |

---

## Goal

After this plan is complete, checkpoint files created via `/new-checkpoint` will have their `session`, `prior_session`, `date`, `work_id`, and `plan_ref` fields auto-populated from infrastructure (session file, haios-status-slim.json, work directory), eliminating mechanical agent token spend on field lookup.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | post_tool_use.py (call-site), checkpoint.md (template — already done) |
| Lines of code affected | ~15 (call-site in post_tool_use.py) | Read of post_tool_use.py:80-128 |
| New files to create | 2 | lib/checkpoint_auto.py, tests/test_checkpoint_auto.py |
| Tests to write | 8 | Based on test strategy below |
| Dependencies | 2 | session_end_actions.py (read_session_number pattern), haios-status-slim.json |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single call-site in post_tool_use.py after template validation |
| Risk of regression | Low | Additive — new handler, no modification of existing logic |
| External dependencies | Low | Reads session file and slim JSON only |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests + implementation | 20 min | High |
| Integration + verification | 10 min | High |
| **Total** | 30 min | High |

---

## Current State vs Desired State

### Current State

```
Agent runs /new-checkpoint
  → scaffold creates checkpoint file with {{SESSION}}, {{PREV_SESSION}}, {{DATE}}, {{WORK_ID}}, {{PLAN_REF}} placeholders
  → Agent must manually:
    1. Read .claude/session → get session number
    2. Read haios-status-slim.json → get work_id
    3. Compute prior_session = session - 1
    4. Compute date = today
    5. Glob plans dir → get plan_ref
    6. Edit checkpoint file to fill all 5 fields
  → Cost: ~5 tool calls, ~2k tokens on mechanical lookup
```

**Result:** Agent spends tokens on zero-judgment field population.

### Desired State

```
Agent runs /new-checkpoint
  → scaffold creates checkpoint file with placeholders
  → PostToolUse hook detects Write to docs/checkpoints/
  → calls populate_checkpoint_fields(path)
  → fields auto-populated from infrastructure
  → Agent sees populated file, no manual lookup needed
  → Cost: 0 agent tokens
```

**Result:** Checkpoint fields populated automatically.

---

## Tests First (TDD)

### Test 1: All fields populated (happy path)
```python
def test_populate_all_fields(tmp_path):
    """All 5 fields populated when all sources available."""
    # Setup: checkpoint file with placeholders, session file, slim JSON, plan file
    # Assert: session, prior_session, date, work_id, plan_ref all replaced
```

### Test 2: Missing session file degrades gracefully
```python
def test_missing_session_file(tmp_path):
    """No session file → session and prior_session remain as placeholders."""
    # Setup: checkpoint file, NO session file, slim JSON exists
    # Assert: session={{SESSION}}, prior_session={{PREV_SESSION}}, date+work_id populated
```

### Test 3: Missing slim JSON degrades gracefully
```python
def test_missing_slim_json(tmp_path):
    """No slim JSON → work_id remains as placeholder."""
    # Setup: checkpoint file, session file, NO slim JSON
    # Assert: work_id={{WORK_ID}}, session+date populated
```

### Test 4: Null work_id in slim JSON (A6)
```python
def test_null_work_id_in_slim(tmp_path):
    """session_state.work_id is null → work_id remains as placeholder."""
    # Setup: checkpoint file, slim JSON with work_id=None
    # Assert: work_id={{WORK_ID}} (placeholder preserved)
```

### Test 5: No plan file → plan_ref placeholder preserved
```python
def test_no_plan_file(tmp_path):
    """No plan file for work_id → plan_ref remains as placeholder."""
    # Setup: checkpoint file, slim JSON with work_id=WORK-170, NO plan file
    # Assert: plan_ref={{PLAN_REF}}
```

### Test 6: Plan file exists → plan_ref populated
```python
def test_plan_file_exists(tmp_path):
    """Plan file found → plan_ref populated with relative path."""
    # Setup: checkpoint file, slim JSON, plan file at work/active/{id}/plans/PLAN.md
    # Assert: plan_ref contains path to plan
```

### Test 7: Non-checkpoint path returns early
```python
def test_non_checkpoint_path_noop(tmp_path):
    """File not in docs/checkpoints/ → no modification."""
    # Setup: write a file outside checkpoints dir
    # Assert: file content unchanged
```

### Test 8: Missing checkpoint file degrades gracefully (A7)
```python
def test_missing_checkpoint_file(tmp_path):
    """Non-existent path → returns None without raising."""
    # Setup: path that does not exist
    # Assert: returns None
```

---

## Detailed Design

### Exact Code Change

**File 1 (NEW):** `.claude/haios/lib/checkpoint_auto.py`

```python
"""
Checkpoint field auto-population (WORK-170).

Pure function to populate checkpoint frontmatter fields from infrastructure.
Pattern: session_end_actions.py (fail-permissive, _default_project_root).
"""
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Optional


def _default_project_root() -> Path:
    """Derive project root. lib/ -> haios/ -> .claude/ -> project root."""
    return Path(__file__).parent.parent.parent.parent


def populate_checkpoint_fields(
    checkpoint_path: Path,
    project_root: Optional[Path] = None,
) -> Optional[str]:
    """Populate placeholder fields in a checkpoint file.

    Reads session file, haios-status-slim.json, and work directory
    to fill: session, prior_session, date, work_id, plan_ref.

    Fields that cannot be resolved are left as placeholders (no errors).

    Args:
        checkpoint_path: Path to the checkpoint .md file.
        project_root: Project root. Defaults to derived path.

    Returns:
        Status message, or None on error. Never raises.
    """
    try:
        root = project_root or _default_project_root()
        content = checkpoint_path.read_text(encoding="utf-8")

        # Only process files with frontmatter placeholders
        if "{{" not in content:
            return None

        # Resolve fields
        session_num = _read_session_number(root)
        work_id = _read_work_id(root)
        plan_ref = _resolve_plan_ref(root, work_id) if work_id else None
        today = datetime.now().strftime("%Y-%m-%d")

        # Replace placeholders (only if value resolved)
        if session_num is not None:
            content = content.replace("{{SESSION}}", str(session_num))
            content = content.replace("{{PREV_SESSION}}", str(max(0, session_num - 1)))
        if work_id:
            content = content.replace("{{WORK_ID}}", work_id)
        if plan_ref:
            content = content.replace("{{PLAN_REF}}", plan_ref)
        content = content.replace("{{DATE}}", today)

        checkpoint_path.write_text(content, encoding="utf-8")
        return f"[CHECKPOINT] Auto-populated fields in {checkpoint_path.name}"

    except Exception:
        return None  # Fail-permissive


def _read_session_number(root: Path) -> Optional[int]:
    """Read session number from .claude/session. Reuses pattern from session_end_actions."""
    try:
        session_file = root / ".claude" / "session"
        if not session_file.exists():
            return None
        for line in session_file.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            try:
                return int(line)
            except ValueError:
                continue
        return None
    except Exception:
        return None


def _read_work_id(root: Path) -> Optional[str]:
    """Read work_id from haios-status-slim.json session_state."""
    try:
        slim_file = root / ".claude" / "haios-status-slim.json"
        if not slim_file.exists():
            return None
        data = json.loads(slim_file.read_text(encoding="utf-8"))
        work_id = data.get("session_state", {}).get("work_id")
        return work_id if work_id else None
    except Exception:
        return None


def _resolve_plan_ref(root: Path, work_id: str) -> Optional[str]:
    """Resolve plan file path for work_id. Glob docs/work/active/{work_id}/plans/PLAN.md."""
    try:
        plan_path = root / "docs" / "work" / "active" / work_id / "plans" / "PLAN.md"
        if plan_path.exists():
            return f"docs/work/active/{work_id}/plans/PLAN.md"
        return None
    except Exception:
        return None
```

**File 2 (MODIFY):** `.claude/hooks/hooks/post_tool_use.py`

Insert after Part 2 (template validation, line ~106), before Part 3:

```python
    # Part 2.5: Checkpoint auto-population (WORK-170)
    checkpoint_msg = _auto_populate_checkpoint(path)
    if checkpoint_msg:
        messages.append(checkpoint_msg)
```

Add helper function at end of file:

```python
def _auto_populate_checkpoint(path: Path) -> Optional[str]:
    """Auto-populate checkpoint fields on Write to docs/checkpoints/ (WORK-170).

    Delegates to checkpoint_auto.populate_checkpoint_fields(). Fail-permissive.
    """
    try:
        path_str = str(path).replace("\\", "/")
        if "/checkpoints/" not in path_str:
            return None

        lib_dir = Path(__file__).parent.parent.parent / "haios" / "lib"
        if str(lib_dir) not in sys.path:
            sys.path.insert(0, str(lib_dir))

        from checkpoint_auto import populate_checkpoint_fields
        return populate_checkpoint_fields(path)
    except Exception:
        return None  # Fail-permissive
```

### Call Chain Context

```
PostToolUse hook (handle)
    |
    +-> tool_name == "Write"
    |       path = tool_input.file_path
    |
    +-> Part 2: _validate_template(path)
    |
    +-> Part 2.5: _auto_populate_checkpoint(path)   # <-- NEW
    |       |
    |       +-> path contains /checkpoints/ ?
    |       |     NO  -> return None
    |       |     YES -> populate_checkpoint_fields(path)
    |       |              |
    |       |              +-> _read_session_number(root)
    |       |              +-> _read_work_id(root)
    |       |              +-> _resolve_plan_ref(root, work_id)
    |       |              +-> Replace {{placeholders}} in file
    |       |
    |       +-> Return status message
    |
    +-> Part 3: _refresh_discoverable_artifacts(path)
    +-> Part 4: _log_cycle_transition(path)
    ...
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Separate lib module | checkpoint_auto.py in lib/ | Testable without hook infrastructure, consistent with tier_detector/critique_injector pattern |
| PostToolUse Write trigger | Only fires on Write to /checkpoints/ path | Narrow scope avoids noise (mem:85582). Checkpoint scaffold always uses Write. |
| Part 2.5 after Part 2 | Auto-population runs after template validation | _validate_template (Part 2) fires first and sees unfilled placeholders. This is pre-existing noise (checkpoint template already missing validate.py required fields), not introduced by WORK-170. Acceptable. |
| Placeholder replacement | String replace `{{X}}` | Simple, matches scaffold template syntax. No YAML parsing needed. |
| prior_session derivation | `session_number - 1` | Simple arithmetic. A7 notes slim.json has authoritative source but low risk in practice. |
| Fail-permissive | All exceptions caught, return None | Pattern from session_end_actions.py. Never blocks agent workflow. |
| plan_ref resolution | Direct path check, not glob | `docs/work/active/{work_id}/plans/PLAN.md` is the canonical path per haios.yaml. No ambiguity. |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No session file | session + prior_session stay as `{{SESSION}}`, `{{PREV_SESSION}}` | Test 2 |
| No slim JSON | work_id stays as `{{WORK_ID}}` | Test 3 |
| Null work_id in slim | work_id stays as `{{WORK_ID}}`, plan_ref stays as `{{PLAN_REF}}` | Test 4 |
| No plan file | plan_ref stays as `{{PLAN_REF}}` | Test 5 |
| Non-checkpoint file | _auto_populate_checkpoint returns None (early return) | Test 7 |
| File has no `{{` | populate_checkpoint_fields returns None (early return) | Implicit in all tests |

### Open Questions

None. All assumptions addressed by critique rounds.

---

## Open Decisions (MUST resolve before implementation)

No operator decisions required. All design choices are consistent with established patterns.

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_checkpoint_auto.py` with 8 tests
- [ ] Verify all tests fail (RED — ModuleNotFoundError)

### Step 2: Create checkpoint_auto.py (GREEN)
- [ ] Create `.claude/haios/lib/checkpoint_auto.py` with `populate_checkpoint_fields()`
- [ ] Tests 1-7 pass

### Step 3: Integrate into PostToolUse hook
- [ ] Add `_auto_populate_checkpoint()` to post_tool_use.py
- [ ] Add call-site after Part 2 (template validation)

### Step 4: Integration Verification
- [ ] All 8 tests pass
- [ ] Full test suite — no regressions

### Step 5: README Sync (MUST)
- [ ] Update `.claude/haios/lib/README.md` with checkpoint_auto.py entry

### Step 6: Consumer Verification
- [ ] Verify PostToolUse hook calls checkpoint_auto (runtime consumer)
- [ ] No stale references

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Hook fires on non-checkpoint writes | Low | Path check `/checkpoints/` narrows scope |
| Template placeholders change | Low | Consistent with scaffold_template() output |
| Session file format changes | Low | Reuses proven read_session_number pattern |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 409 | 2026-02-20 | - | PLAN | Plan authored |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-170/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| New file lib/checkpoint_auto.py | [ ] | File exists with populate_checkpoint_fields() |
| PostToolUse integration | [ ] | _auto_populate_checkpoint() in post_tool_use.py |
| Handles: session, prior_session, date, work_id, plan_ref | [ ] | 5 field replacements in populate_checkpoint_fields() |
| Template update: work_id and plan_ref placeholders | [ ] | checkpoint.md has {{WORK_ID}} and {{PLAN_REF}} (done in PLAN phase) |
| Graceful degradation | [ ] | Tests 2-5 verify placeholder preservation |
| Tests in test_checkpoint_auto.py | [ ] | 8 tests, all green |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/checkpoint_auto.py` | populate_checkpoint_fields() exists | [ ] | |
| `tests/test_checkpoint_auto.py` | 8 tests pass | [ ] | |
| `.claude/hooks/hooks/post_tool_use.py` | _auto_populate_checkpoint() added | [ ] | |
| `.claude/templates/checkpoint.md` | Has {{WORK_ID}} and {{PLAN_REF}} | [ ] | Already done |
| `.claude/haios/lib/README.md` | checkpoint_auto.py entry added | [ ] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **MUST:** All WORK.md deliverables verified complete
- [ ] **Runtime consumer exists** (PostToolUse hook calls checkpoint_auto)
- [ ] WHY captured
- [ ] **MUST:** READMEs updated
- [ ] Ground Truth Verification completed above

---

## References

- @docs/work/active/WORK-170/WORK.md (work item)
- @docs/work/active/WORK-160/WORK.md (parent)
- @.claude/haios/lib/session_end_actions.py (pattern template)
- @.claude/hooks/hooks/post_tool_use.py (integration point)
- Memory: 85582 (hook noise warning), 86727 (PostToolUse architectural constraint)

---
