---
template: implementation_plan
status: complete
backlog_id: WORK-171
title: "Mechanical Phase Migration"
author: Hephaestus
lifecycle_phase: plan
session: 404
version: "1.5"
generated: 2026-02-19
last_updated: 2026-02-19T20:30:52
---
# Implementation Plan: Mechanical Phase Migration

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | DONE | Memory queried: 84849 (lazy import fallback), 85534 (computable predicate pattern), 84111 (centralized migration) |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

Migrate 3 mechanical ceremony phases from SKILL.md (agent-read, 100% token cost) to lib/ functions and PostToolUse hooks (auto-execute, ~0 token cost): retro-cycle Phase 0 scale assessment, cycle state initialization on skill invocation, and WORK.md cycle_phase auto-sync on phase advancement.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | `post_tool_use.py`, `cycle_state.py`, `retro-cycle/SKILL.md` |
| Lines of code affected | ~80 | cycle_state.py (add ~40), post_tool_use.py (add ~10), SKILL.md (modify ~5) |
| New files to create | 3 | `.claude/haios/lib/retro_scale.py`, `tests/test_retro_scale.py`, `tests/test_phase_migration.py` |
| Tests to write | 13 | 6 retro_scale + 4 sync_work_md_phase + 3 integration/regression |
| Dependencies | 2 | governance_events.py (event logging), ConfigLoader (path resolution) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Med | PostToolUse hook chain, haios-status-slim.json, WORK.md frontmatter |
| Risk of regression | Low | New functions; existing code paths unchanged |
| External dependencies | Low | No external APIs; file I/O only |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests + retro_scale.py | 30 min | High |
| sync_work_md_phase + hook wiring | 20 min | High |
| SKILL.md updates + integration | 15 min | High |
| **Total** | **~65 min** | |

---

## Current State vs Desired State

### Current State

```python
# retro-cycle/SKILL.md:119-137 — Agent reads and evaluates manually
# Phase 0: Scale Assessment
# Computable predicate determines trivial vs substantial:
# trivial = (files_changed <= 2)
#       AND (no plan exists in docs/work/active/{work_id}/plans/)
#       AND (no test files changed)
#       AND (no CycleTransition governance events for this work_id)
```

```python
# cycle_state.py:36-123 — Advances phase in haios-status-slim.json only
def advance_cycle_phase(skill_name, project_root=None) -> bool:
    # Writes to haios-status-slim.json session_state
    # Does NOT update WORK.md cycle_phase field
```

**Behavior:** Agent reads SKILL.md Phase 0 instructions (~30 lines) and manually evaluates 4 conditions. Phase advancement updates slim JSON but not WORK.md, causing drift (retro WCBB-2 from S403).

**Result:** Tokens spent on mechanical evaluation; WORK.md cycle_phase field stale after auto-advancement.

### Desired State

```python
# .claude/haios/lib/retro_scale.py — New lib function
def assess_scale(work_id: str, project_root: Optional[Path] = None) -> str:
    """Return 'trivial' or 'substantial' based on computable predicate."""
    # Checks: files_changed, plan_exists, test_files_changed, governance_events
    # Returns: "trivial" | "substantial"
```

```python
# .claude/haios/lib/cycle_state.py — New function added
def sync_work_md_phase(work_id: str, phase: str, project_root: Optional[Path] = None) -> bool:
    """Write cycle_phase field to WORK.md using targeted regex replacement."""
    # Fail-permissive: returns False on any error
```

**Behavior:** `assess_scale()` is callable from retro-cycle (zero agent token cost for conditions). `sync_work_md_phase()` is called by `advance_cycle_phase()` to keep WORK.md in sync.

**Result:** Agent references lib/ function instead of reading 30 lines of conditions. WORK.md cycle_phase stays synchronized with session_state.

---

## Tests First (TDD)

### Test 1: assess_scale returns trivial for small work
```python
def test_assess_scale_trivial(tmp_path):
    """Work with <=2 files changed, no plan, no tests, no events -> trivial."""
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text("---\nid: WORK-999\n---\n")
    # No plans dir, no governance events
    events_file = tmp_path / ".claude" / "haios" / "governance-events.jsonl"
    events_file.parent.mkdir(parents=True)
    events_file.write_text("")
    result = assess_scale("WORK-999", project_root=tmp_path)
    assert result == "trivial"
```

### Test 2: assess_scale returns substantial when plan exists
```python
def test_assess_scale_substantial_with_plan(tmp_path):
    """Work with a plan file -> substantial."""
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
    plans_dir = work_dir / "plans"
    plans_dir.mkdir(parents=True)
    (plans_dir / "PLAN.md").write_text("---\nstatus: approved\n---\n")
    events_file = tmp_path / ".claude" / "haios" / "governance-events.jsonl"
    events_file.parent.mkdir(parents=True)
    events_file.write_text("")
    result = assess_scale("WORK-999", project_root=tmp_path)
    assert result == "substantial"
```

### Test 3: assess_scale returns substantial when governance events exist
```python
def test_assess_scale_substantial_with_events(tmp_path):
    """Work with CyclePhaseEntered events for work_id -> substantial."""
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text("---\nid: WORK-999\n---\n")
    events_file = tmp_path / ".claude" / "haios" / "governance-events.jsonl"
    events_file.parent.mkdir(parents=True)
    events_file.write_text('{"type":"CyclePhaseEntered","work_id":"WORK-999","phase":"PLAN"}\n')
    result = assess_scale("WORK-999", project_root=tmp_path)
    assert result == "substantial"
```

### Test 4: assess_scale handles missing work dir gracefully
```python
def test_assess_scale_missing_work_dir(tmp_path):
    """Missing work dir -> substantial (fail-safe)."""
    events_file = tmp_path / ".claude" / "haios" / "governance-events.jsonl"
    events_file.parent.mkdir(parents=True)
    events_file.write_text("")
    result = assess_scale("WORK-999", project_root=tmp_path)
    assert result == "substantial"
```

### Test 5: assess_scale detects test file changes
```python
import retro_scale  # Required for monkeypatch target "retro_scale._get_changed_files"
from retro_scale import assess_scale

def test_assess_scale_substantial_with_test_changes(tmp_path, monkeypatch):
    """Git diff showing test file changes -> substantial."""
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text("---\nid: WORK-999\n---\n")
    events_file = tmp_path / ".claude" / "haios" / "governance-events.jsonl"
    events_file.parent.mkdir(parents=True)
    events_file.write_text("")
    # Mock git diff to return test files
    monkeypatch.setattr("retro_scale._get_changed_files", lambda root: ["tests/test_foo.py", "lib/foo.py"])
    result = assess_scale("WORK-999", project_root=tmp_path)
    assert result == "substantial"
```

### Test 6: assess_scale returns substantial when >2 files changed
```python
def test_assess_scale_substantial_many_files(tmp_path, monkeypatch):
    """Git diff showing >2 files -> substantial."""
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text("---\nid: WORK-999\n---\n")
    events_file = tmp_path / ".claude" / "haios" / "governance-events.jsonl"
    events_file.parent.mkdir(parents=True)
    events_file.write_text("")
    monkeypatch.setattr("retro_scale._get_changed_files", lambda root: ["a.py", "b.py", "c.py"])
    result = assess_scale("WORK-999", project_root=tmp_path)
    assert result == "substantial"
```

### Test 7: sync_work_md_phase writes cycle_phase field
```python
def test_sync_work_md_phase_updates_field(tmp_path):
    """Writes cycle_phase field to WORK.md frontmatter."""
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
    work_dir.mkdir(parents=True)
    work_file = work_dir / "WORK.md"
    work_file.write_text("---\nid: WORK-999\ncycle_phase: PLAN\nstatus: active\n---\n# Content\n")
    result = sync_work_md_phase("WORK-999", "DO", project_root=tmp_path)
    assert result is True
    content = work_file.read_text()
    assert "cycle_phase: DO" in content
    assert "cycle_phase: PLAN" not in content
```

### Test 8: sync_work_md_phase preserves other frontmatter
```python
def test_sync_work_md_phase_preserves_content(tmp_path):
    """Does not corrupt other frontmatter fields or body content."""
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
    work_dir.mkdir(parents=True)
    work_file = work_dir / "WORK.md"
    original = "---\nid: WORK-999\ntitle: \"Test Item\"\ncycle_phase: PLAN\nstatus: active\n---\n# Content\nBody text here.\n"
    work_file.write_text(original)
    sync_work_md_phase("WORK-999", "DO", project_root=tmp_path)
    content = work_file.read_text()
    assert 'title: "Test Item"' in content
    assert "status: active" in content
    assert "Body text here." in content
    assert "cycle_phase: DO" in content
```

### Test 9: sync_work_md_phase returns False on missing file
```python
def test_sync_work_md_phase_missing_file(tmp_path):
    """Returns False when WORK.md does not exist (fail-permissive)."""
    result = sync_work_md_phase("WORK-999", "DO", project_root=tmp_path)
    assert result is False
```

### Test 10: sync_work_md_phase returns False when no cycle_phase field
```python
def test_sync_work_md_phase_no_field(tmp_path):
    """Returns False when WORK.md has no cycle_phase field."""
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
    work_dir.mkdir(parents=True)
    work_file = work_dir / "WORK.md"
    work_file.write_text("---\nid: WORK-999\nstatus: active\n---\n")
    result = sync_work_md_phase("WORK-999", "DO", project_root=tmp_path)
    assert result is False
```

### Test 11: advance_cycle_phase calls sync_work_md_phase
```python
import cycle_runner  # Required for monkeypatch target

def test_advance_cycle_phase_syncs_work_md(tmp_path, monkeypatch):
    """advance_cycle_phase calls sync_work_md_phase after advancing."""
    # Setup slim JSON with session_state
    slim_file = tmp_path / ".claude" / "haios-status-slim.json"
    slim_file.parent.mkdir(parents=True)
    import json
    slim_file.write_text(json.dumps({
        "session_state": {
            "active_cycle": "implementation-cycle",
            "current_phase": "PLAN",
            "work_id": "WORK-999",
            "entered_at": "2026-01-01T00:00:00",
            "active_queue": None,
            "phase_history": []
        }
    }))
    # Setup WORK.md
    work_dir = tmp_path / "docs" / "work" / "active" / "WORK-999"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text("---\nid: WORK-999\ncycle_phase: PLAN\n---\n")
    # Patch CYCLE_PHASES at the source module (cycle_runner), not cycle_state
    monkeypatch.setattr(cycle_runner, "CYCLE_PHASES", {"implementation-cycle": ["PLAN", "DO", "CHECK", "DONE"]})
    result = advance_cycle_phase("implementation-cycle", project_root=tmp_path)
    assert result is True
    content = (work_dir / "WORK.md").read_text()
    assert "cycle_phase: DO" in content
```

### Test 12: Backward compatibility - advance_cycle_phase still works without WORK.md
```python
def test_advance_cycle_phase_no_work_md_still_advances(tmp_path, monkeypatch):
    """Phase still advances in slim JSON even if WORK.md sync fails."""
    slim_file = tmp_path / ".claude" / "haios-status-slim.json"
    slim_file.parent.mkdir(parents=True)
    import json
    slim_file.write_text(json.dumps({
        "session_state": {
            "active_cycle": "implementation-cycle",
            "current_phase": "PLAN",
            "work_id": "WORK-999",
            "entered_at": "2026-01-01T00:00:00",
            "active_queue": None,
            "phase_history": []
        }
    }))
    # Patch CYCLE_PHASES at the source module (cycle_runner)
    monkeypatch.setattr(cycle_runner, "CYCLE_PHASES", {"implementation-cycle": ["PLAN", "DO", "CHECK", "DONE"]})
    # No WORK.md exists — sync will fail but advance should still succeed
    result = advance_cycle_phase("implementation-cycle", project_root=tmp_path)
    assert result is True
    data = json.loads(slim_file.read_text())
    assert data["session_state"]["current_phase"] == "DO"
```

### Test 13: Regression - advance_cycle_phase handles missing session_state
```python
def test_advance_cycle_phase_no_session_state(tmp_path):
    """Returns False cleanly when slim JSON has no session_state key."""
    slim_file = tmp_path / ".claude" / "haios-status-slim.json"
    slim_file.parent.mkdir(parents=True)
    import json
    slim_file.write_text(json.dumps({"version": "1.0"}))
    result = advance_cycle_phase("implementation-cycle", project_root=tmp_path)
    assert result is False
```

---

## Detailed Design

### Component 1: `retro_scale.py` (New File)

**File:** `.claude/haios/lib/retro_scale.py`

```python
"""
Retro-cycle scale assessment (WORK-171).

Computable predicate for retro-cycle Phase 0: determines if a work item
is 'trivial' or 'substantial' based on 4 machine-checkable conditions.

Follows session_end_actions.py pattern:
- Pure functions in lib/
- Fail-permissive (never raises)
- _default_project_root() for path derivation
- Testable without hook infrastructure
"""
import json
import subprocess
from pathlib import Path
from typing import Optional


def _default_project_root() -> Path:
    """Derive project root from this file's location.
    lib/ -> haios/ -> .claude/ -> project root.
    """
    return Path(__file__).parent.parent.parent.parent


def _get_changed_files(project_root: Path) -> list[str]:
    """Get list of changed files via git diff (fail-safe: empty list)."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD~5"],
            capture_output=True, text=True, timeout=5,
            cwd=str(project_root),
        )
        if result.returncode != 0:
            return []
        return [f for f in result.stdout.splitlines() if f.strip()]
    except Exception:
        return []


def assess_scale(
    work_id: str,
    project_root: Optional[Path] = None,
) -> str:
    """Assess work item scale for retro-cycle Phase 0.

    Computable predicate: trivial if ALL of:
    1. files_changed <= 2
    2. no plan exists in docs/work/active/{work_id}/plans/
    3. no test files in changed files
    4. no CyclePhaseEntered governance events for work_id

    Args:
        work_id: Work item ID (e.g., "WORK-171")
        project_root: Project root. Defaults to derived path.

    Returns:
        "trivial" or "substantial". Defaults to "substantial" on error.
    """
    try:
        root = project_root or _default_project_root()

        # Condition 1: files_changed <= 2
        changed = _get_changed_files(root)
        if len(changed) > 2:
            return "substantial"

        # Condition 2: no plan exists
        plan_path = root / "docs" / "work" / "active" / work_id / "plans" / "PLAN.md"
        if plan_path.exists():
            return "substantial"

        # Condition 3: no test files changed
        if any(f.startswith("tests/") or f.startswith("tests\\") for f in changed):
            return "substantial"

        # Condition 4: no CyclePhaseEntered events for work_id
        events_file = root / ".claude" / "haios" / "governance-events.jsonl"
        if events_file.exists():
            for line in events_file.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                    if (event.get("type") == "CyclePhaseEntered"
                            and event.get("work_id") == work_id):
                        return "substantial"
                except json.JSONDecodeError:
                    continue

        return "trivial"
    except Exception:
        return "substantial"  # Fail-safe: assume substantial
```

### Component 2: `sync_work_md_phase()` in `cycle_state.py`

**File:** `.claude/haios/lib/cycle_state.py`
**Location:** New function added after `advance_cycle_phase()`

```python
def sync_work_md_phase(
    work_id: str,
    phase: str,
    project_root: Optional[Path] = None,
) -> bool:
    """Write cycle_phase field to WORK.md frontmatter.

    Uses targeted regex line-replacement (not full YAML re-serialization)
    to avoid frontmatter corruption. Pattern from work_item.py:56-71.

    Args:
        work_id: Work item ID (e.g., "WORK-171")
        phase: New phase value (e.g., "DO", "CHECK")
        project_root: Project root. Defaults to derived path.

    Returns:
        True if written, False on error or missing file (fail-permissive).
    """
    import re
    try:
        root = project_root or _default_project_root()
        work_file = root / "docs" / "work" / "active" / work_id / "WORK.md"
        if not work_file.exists():
            return False

        content = work_file.read_text(encoding="utf-8")

        # Verify cycle_phase field exists before writing
        if not re.search(r'^cycle_phase:\s', content, re.MULTILINE):
            return False

        updated = re.sub(
            r'^cycle_phase:\s.*$',
            f'cycle_phase: {phase}',
            content,
            flags=re.MULTILINE,
        )
        work_file.write_text(updated, encoding="utf-8")
        return True
    except Exception:
        return False
```

**Integration into `advance_cycle_phase()`:**

Add after line 109 (after `slim_file.write_text(...)`) and before the governance event logging:

```python
        # Sync WORK.md cycle_phase (WORK-171, fail-permissive)
        work_id = session_state.get("work_id")
        if work_id:
            sync_work_md_phase(work_id, next_phase, project_root=root)
```

### Component 3: SKILL.md Updates

**File:** `.claude/skills/retro-cycle/SKILL.md`
**Location:** Phase 0 section (lines 119-137)

Replace the inline condition listing with a reference to the lib function:

```markdown
## Phase 0: Scale Assessment

**Computable predicate** — call `assess_scale(work_id)` from `.claude/haios/lib/retro_scale.py`:

```python
from retro_scale import assess_scale
scaling = assess_scale(work_id)  # Returns "trivial" or "substantial"
```

The function checks 4 machine-checkable conditions (files_changed, plan_exists, test_files_changed, governance_events). See `retro_scale.py` for details.
```

### Call Chain Context

```
PostToolUse hook (post_tool_use.py)
    |
    +-> Skill tool invoked
    |       |
    |       +-> advance_cycle_phase(skill_name)     # cycle_state.py
    |               |
    |               +-> reads/writes haios-status-slim.json
    |               +-> sync_work_md_phase(work_id, phase)  # NEW
    |               |       Writes cycle_phase to WORK.md
    |               +-> log_phase_transition()               # governance_events.py
    |
    +-> retro-cycle Skill invoked
            |
            +-> Phase 0: assess_scale(work_id)    # NEW retro_scale.py
            |       Returns: "trivial" | "substantial"
            +-> Phase 1-4: based on scale result
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Regex line-replacement for WORK.md writes | `re.sub(r'^cycle_phase:\s.*$', ...)` | Established pattern from `work_item.py:56-71`. Avoids full YAML re-serialization which can reorder fields and corrupt nested structures. Critique A8 mitigation. |
| Fail-safe to "substantial" | `assess_scale()` returns "substantial" on any error | Prevents trivial-scale retros from accidentally skipping substantial work items. Conservative default. |
| `_get_changed_files()` uses `HEAD~5` | Looks at recent 5 commits | Approximation — exact work-scoped diff would require commit tagging. HEAD~5 covers typical session scope. Good enough for heuristic. |
| sync called inside advance, not separately | sync_work_md_phase is called within advance_cycle_phase | Single call site ensures sync happens whenever phase advances. No risk of forgetting to call sync separately. |
| New file for retro_scale, function-in-file for sync | retro_scale.py is standalone; sync_work_md_phase joins cycle_state.py | retro_scale is a separate concern (assessment vs state management). sync_work_md_phase is a natural extension of cycle_state. Memory 84849: lazy import fallback for backward compat. |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| WORK.md missing | sync_work_md_phase returns False, advance still succeeds | Test 9, 12 |
| No cycle_phase field in WORK.md | sync_work_md_phase returns False | Test 10 |
| Git not available | _get_changed_files returns [], contributes to trivial (0 files) | Test 4 (no git setup) |
| Governance events file missing | Events check passes (no events = trivial condition met) | Test 1 |
| WORK.md has unusual encoding | read_text with utf-8 catches; returns False on error | Fail-permissive pattern |

### Open Questions

**Q: Should `_get_changed_files` scope to work-specific commits?**

For now, HEAD~5 is a reasonable approximation. Exact scoping would require commit message parsing or tagging — complexity not justified for a heuristic predicate. Can be refined in E2.9+ if needed.

---

## Open Decisions (MUST resolve before implementation)

No operator decisions required. All design choices are within established patterns.

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| None | - | - | All decisions resolved during plan authoring |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_retro_scale.py` with Tests 1-6
- [ ] Create `tests/test_phase_migration.py` with Tests 7-12
- [ ] Verify all 13 tests fail (red)

### Step 2: Implement retro_scale.py
- [ ] Create `.claude/haios/lib/retro_scale.py` with `assess_scale()` and `_get_changed_files()`
- [ ] Tests 1-6 pass (green)

### Step 3: Implement sync_work_md_phase
- [ ] Add `sync_work_md_phase()` to `.claude/haios/lib/cycle_state.py`
- [ ] Add sync call inside `advance_cycle_phase()` after slim JSON write
- [ ] Tests 7-10 pass (green)

### Step 4: Integration (advance + sync)
- [ ] Tests 11-12 pass (green)
- [ ] Run existing cycle_state tests — zero regressions

### Step 5: Update SKILL.md files
- [ ] Replace retro-cycle/SKILL.md Phase 0 computable predicate section (lines 119-137) with reference to `assess_scale()` — preserve Escape Hatch at lines 139-145
- [ ] Ensure NO "CycleTransition" text remains (the actual event type is "CyclePhaseEntered")
- [ ] Update implementation-cycle/SKILL.md to note auto-init behavior

### Step 6: Integration Verification
- [ ] All 13 new tests pass
- [ ] Run full test suite: `pytest tests/ -v` — no regressions
- [ ] Manual demo: invoke retro-cycle, verify assess_scale is called

### Step 7: Consumer Verification (MUST)
- [ ] Grep for old Phase 0 condition text in all SKILL.md files
- [ ] Grep for "CycleTransition" in retro-cycle/SKILL.md — MUST find zero occurrences
- [ ] Grep for `cycle_phase` write patterns to verify no conflicts
- [ ] Verify no stale references remain

---

## Verification

- [ ] Tests pass (13 new + 0 regressions)
- [ ] retro_scale.py callable from retro-cycle
- [ ] sync_work_md_phase keeps WORK.md in sync with session_state

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| HEAD~5 git diff includes unrelated changes | Low | Fail-safe to "substantial" — worst case is a full retro when trivial would suffice |
| WORK.md frontmatter corruption from regex write | Med | Targeted single-field replacement (not full YAML reserialization). Established pattern from work_item.py. Fail-permissive: advance still works even if sync fails. |
| Import failure in hook context (sys.path) | Low | Existing pattern in post_tool_use.py (Part 8) already handles this with try/except. Same lib_dir derivation. |
| Retro-cycle SKILL.md references become stale | Low | Only changing Phase 0 section. Rest of SKILL.md unchanged. Consumer verification step catches stale refs. |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 404 | 2026-02-19 | - | Plan authored | 3 critique passes, plan authoring complete |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-171/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| New file `.claude/haios/lib/retro_scale.py` with `assess_scale(work_id)` | [ ] | File exists, function callable |
| PostToolUse auto-initialization of session_state on lifecycle skill invocation | [ ] | Already exists (WORK-168). Verify preserved. |
| PostToolUse auto-logging of ceremony governance events | [ ] | Already exists in advance_cycle_phase. Verify preserved. |
| Updated retro-cycle SKILL.md Phase 0 to reference lib/ function | [ ] | SKILL.md Phase 0 references assess_scale() |
| Updated implementation-cycle SKILL.md to reference auto-init/auto-log | [ ] | SKILL.md notes auto-init behavior |
| Tests in test_retro_scale.py and test_phase_migration.py | [ ] | 13 tests pass |
| Auto-sync WORK.md cycle_phase via sync_work_md_phase() in cycle_state.py | [ ] | Function exists, called by advance_cycle_phase |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/retro_scale.py` | assess_scale() + _get_changed_files() | [ ] | |
| `.claude/haios/lib/cycle_state.py` | sync_work_md_phase() added, advance_cycle_phase updated | [ ] | |
| `.claude/skills/retro-cycle/SKILL.md` | Phase 0 references assess_scale() | [ ] | |
| `tests/test_retro_scale.py` | 6 tests covering scale assessment | [ ] | |
| `tests/test_phase_migration.py` | 7 tests covering sync + integration + regression | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_retro_scale.py tests/test_phase_migration.py -v
# Expected: 13 tests passed
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
- [ ] **Runtime consumer exists** (PostToolUse hook calls advance_cycle_phase which calls sync_work_md_phase; retro-cycle agent calls assess_scale)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** Consumer verification complete (zero stale Phase 0 references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- @docs/work/active/WORK-171/WORK.md (work item)
- @docs/work/active/WORK-168/WORK.md (dependency — cycle auto-advance)
- @.claude/haios/lib/cycle_state.py (target for sync_work_md_phase)
- @.claude/haios/lib/session_end_actions.py (pattern reference)
- @.claude/haios/lib/work_item.py (regex write pattern, lines 56-71)
- @.claude/haios/lib/governance_events.py (event logging)
- @.claude/skills/retro-cycle/SKILL.md (Phase 0 migration target)
- Memory: 84849 (lazy import fallback), 85534 (computable predicate pattern), 85607 (retro Phase 0 prototype)

---
