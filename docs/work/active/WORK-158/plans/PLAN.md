---
template: implementation_plan
status: complete
date: 2026-02-17
backlog_id: WORK-158
title: "ConfigLoader Path Migration"
author: Hephaestus
lifecycle_phase: plan
session: 393
version: "1.5"
generated: 2026-02-17
last_updated: 2026-02-17T19:26:04
---
# Implementation Plan: ConfigLoader Path Migration

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests for ConfigLoader path resolution |
| Query prior work | DONE | Memory: 85048 (ConfigLoader for all paths), 85073 (Path objects for platform safety), 85355 (STOP multi-level parent traversal) |
| Document design decisions | MUST | Key Design Decisions table |
| Ground truth metrics | MUST | Grep audit: 57 occurrences in 6 files |

---

## Goal

Migrate all 57 hardcoded `PROJECT_ROOT / "path"` patterns across 6 lib/ modules to use `ConfigLoader.get_path()`, adding 7 missing path keys to haios.yaml, so path resolution has a single source of truth.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 7 | 6 lib/*.py files + haios.yaml |
| Occurrences to migrate | 57 | `Grep(pattern="PROJECT_ROOT /", glob="**/*.py")` |
| New path keys | 7 | work_blocked, plans, investigations, backlog, status_slim, session, memory_db |
| Tests to write | 8 | 7 new path keys + 1 regression test for existing keys |
| Dependencies | 1 | ConfigLoader (lib/config.py) |

### File Breakdown

| File | Occurrences | Complexity |
|------|-------------|------------|
| `status.py` | 35 | Repetitive — same ~8 paths used in multiple functions |
| `scaffold.py` | 13 | Mix of work_active, templates, session, status |
| `observations.py` | 5 | work_active and work_archive |
| `work_loader.py` | 2 | checkpoints and haios_config |
| `session_loader.py` | 1 | checkpoints |
| `loader.py` | 1 | base_path |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Each file independently uses PROJECT_ROOT |
| Risk of regression | Medium | 57 substitutions — one typo breaks a function. Tests mitigate. |
| External dependencies | Low | ConfigLoader already exists and works |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Add path keys to haios.yaml | 10 min | High |
| Tests (RED) | 20 min | High |
| Migration (GREEN) | 45 min | High — mechanical but 57 occurrences |
| Verification | 15 min | High |
| **Total** | ~1.5 hr | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/lib/scaffold.py:128
work_dir = PROJECT_ROOT / "docs" / "work" / "active"

# .claude/haios/lib/status.py:74
agents_dir = PROJECT_ROOT / ".claude" / "agents"

# .claude/haios/lib/status.py:540-547
PROJECT_ROOT / "docs" / "checkpoints",
PROJECT_ROOT / "docs" / "plans",
PROJECT_ROOT / "docs" / "investigations",
PROJECT_ROOT / "docs" / "ADR",
PROJECT_ROOT / "docs" / "reports",
PROJECT_ROOT / "docs" / "work" / "active",
PROJECT_ROOT / "docs" / "work" / "blocked",
PROJECT_ROOT / "docs" / "work" / "archive",
```

**Behavior:** Each module hardcodes paths with `PROJECT_ROOT /`. If directory structure changes, every file must be updated.

**Result:** 57 places to change for any path modification. Single source of truth violated (REQ-CONFIG-003).

### Desired State

```python
# .claude/haios/lib/scaffold.py:128
from config import ConfigLoader
config = ConfigLoader.get()
work_dir = PROJECT_ROOT / config.get_path("work_active")

# .claude/haios/lib/status.py:74
agents_dir = PROJECT_ROOT / config.get_path("agents")

# .claude/haios/lib/status.py:540-547
PROJECT_ROOT / config.get_path("checkpoints"),
PROJECT_ROOT / config.get_path("plans"),
PROJECT_ROOT / config.get_path("investigations"),
PROJECT_ROOT / config.get_path("adr"),
PROJECT_ROOT / config.get_path("reports"),
PROJECT_ROOT / config.get_path("work_active"),
PROJECT_ROOT / config.get_path("work_blocked"),
PROJECT_ROOT / config.get_path("work_archive"),
```

**Behavior:** All paths resolved via ConfigLoader. Changes to directory structure only require updating haios.yaml.

**Result:** Single source of truth for all paths.

---

## Tests First (TDD)

### Test 1: New path keys resolve correctly
```python
def test_new_path_keys_exist(tmp_path):
    """All new path keys added in WORK-158 resolve without error."""
    config = _setup_config(tmp_path)
    new_keys = ["work_blocked", "plans", "investigations", "backlog", "status_slim", "session", "memory_db"]
    for key in new_keys:
        path = config.get_path(key)
        assert path is not None
        assert "{" not in str(path)  # No unresolved placeholders
```

### Test 2: Existing path keys still work
```python
def test_existing_path_keys_unchanged(tmp_path):
    """Existing keys from haios.yaml still resolve correctly."""
    config = _setup_config(tmp_path)
    assert str(config.get_path("work_active")) == "docs/work/active"
    assert str(config.get_path("checkpoints")) == "docs/checkpoints"
    assert str(config.get_path("templates")) == ".claude/templates"
```

### Test 3: Path key with placeholder substitution
```python
def test_path_key_with_placeholder(tmp_path):
    """work_item key resolves with id placeholder."""
    config = _setup_config(tmp_path)
    path = config.get_path("work_item", id="WORK-158")
    assert "WORK-158" in str(path)
```

### Test 4: Unknown key raises KeyError
```python
def test_unknown_path_key_raises(tmp_path):
    """Missing key raises KeyError."""
    config = _setup_config(tmp_path)
    with pytest.raises(KeyError):
        config.get_path("nonexistent_key")
```

### Test 5-8: Per-file migration verification
```python
def test_status_no_hardcoded_project_root():
    """status.py has zero PROJECT_ROOT / 'docs' patterns."""
    content = Path(".claude/haios/lib/status.py").read_text()
    # Allow PROJECT_ROOT definition line but not path construction
    lines = [l for l in content.split("\n")
             if "PROJECT_ROOT /" in l and "PROJECT_ROOT = " not in l]
    assert len(lines) == 0, f"Found hardcoded paths: {lines[:3]}"
```
(Repeat for scaffold.py, observations.py, work_loader.py, session_loader.py, loader.py)

---

## Detailed Design

### New Path Keys (haios.yaml additions)

```yaml
paths:
  # ... existing keys ...

  # New keys (WORK-158)
  work_blocked: "docs/work/blocked"
  plans: "docs/plans"
  investigations: "docs/investigations"
  backlog: "docs/pm/backlog.md"
  status_slim: ".claude/haios-status-slim.json"
  session: ".claude/session"
  memory_db: "haios_memory.db"
```

### Migration Pattern

Each file follows the same pattern:

```python
# BEFORE:
some_path = PROJECT_ROOT / "docs" / "work" / "active"

# AFTER:
from config import ConfigLoader
# ... (one import per file, at top)
# Per-function ConfigLoader.get() calls (A5 critique: NOT module-level)
def some_function():
    config = ConfigLoader.get()
    some_path = PROJECT_ROOT / config.get_path("work_active")
```

**Key insight:** `get_path()` returns a relative `Path`. We still need `PROJECT_ROOT /` prefix for absolute resolution. The migration changes the hardcoded relative path to a config-driven one, not the absolute resolution mechanism.

**Test fixture strategy (A3 critique):** ConfigLoader is a singleton reading from disk. For tests:
- Use `monkeypatch.setattr` on ConfigLoader's `_haios` dict to inject test paths
- Or use `ConfigLoader.reset()` + patch `ConfigLoader._load()` to return test YAML
- Per-function calls (not module-level) ensure `reset()` takes effect between tests

### Per-File Migration Map

| File | Import needed | Patterns to replace |
|------|---------------|-------------------|
| `status.py` | Yes (new) | 35: work_active(7), work_archive(4), work_blocked(4), checkpoints(3), plans(6), backlog(3), investigations(1), adr(1), reports(1), agents(1), commands(1), skills(1), status_slim(1), memory_db(1) |
| `scaffold.py` | Already imports | 13: work_active(5), templates(3), session(1), status(2), work_item(1), work_plan(1) |
| `observations.py` | Yes (new) | 5: work_active(3), work_archive(2) |
| `work_loader.py` | Yes (new) | 2: checkpoints(1), haios_config(1) |
| `session_loader.py` | Yes (new) | 1: checkpoints(1) |
| `loader.py` | Yes (new) | 1: base_path handling (special case) |

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Keep PROJECT_ROOT prefix | Yes — `PROJECT_ROOT / config.get_path(key)` | get_path() returns relative paths. Absolute resolution still needs root. |
| Per-function config access | `config = ConfigLoader.get()` inside each function (A5 critique) | Module-level evaluated at import time, breaks test isolation. Per-function respects reset(). |
| Test isolation via monkeypatch | Patch ConfigLoader._haios dict or _load() method (A3 critique) | ConfigLoader reads from hardcoded disk path. tmp_path alone insufficient. |
| No base_path injection change | Keep existing __file__-based PROJECT_ROOT | Migration scope is path constants, not root resolution mechanism |
| loader.py special case | Keep base_path parameter, use config for default | loader.py has explicit base_path injection for testing |
| 7 new keys only | Don't restructure existing keys | Minimal change — add what's missing, don't reorganize |
| Audit external imports first | Grep for `from status import` etc. before migrating (A4 critique) | External code depending on path variables would break silently |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| ConfigLoader not initialized | Singleton auto-creates on first .get() | Existing ConfigLoader tests |
| Path key missing from haios.yaml | KeyError raised (existing behavior) | Test 4 |
| Tests using tmp_path | ConfigLoader.reset() + custom haios.yaml | Test fixture pattern |

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| No unresolved operator decisions | N/A | N/A | Scope narrowed per operator direction |

---

## Implementation Steps

### Step 1: Add path keys to haios.yaml
- [ ] Add 7 new keys: work_blocked, plans, investigations, backlog, status_slim, session, memory_db
- [ ] Verify ConfigLoader.get().paths includes new keys

### Step 2: Write failing tests
- [ ] Create `tests/test_configloader_paths.py` with 8 tests
- [ ] Tests 5-8: grep-based verification that each file has zero hardcoded paths
- [ ] Verify tests 5-8 fail (RED) — files still have hardcoded paths

### Step 3: Migrate status.py (35 occurrences)
- [ ] Add ConfigLoader import
- [ ] Replace all 35 `PROJECT_ROOT / "..."` patterns
- [ ] Test 5 passes (green)

### Step 4: Migrate scaffold.py (13 occurrences)
- [ ] Replace all 13 patterns (ConfigLoader already imported)
- [ ] Test 6 passes (green)

### Step 5: Migrate observations.py (5 occurrences)
- [ ] Add ConfigLoader import
- [ ] Replace all 5 patterns
- [ ] Test 7 passes (green)

### Step 6: Migrate remaining files (4 occurrences)
- [ ] work_loader.py: 2 patterns
- [ ] session_loader.py: 1 pattern
- [ ] loader.py: 1 pattern (special case)
- [ ] Test 8 passes (green)

### Step 7: Integration Verification
- [ ] All 8 new tests pass
- [ ] Run full test suite (no regressions)
- [ ] Grep verify: zero `PROJECT_ROOT /` in path construction (only definition)

### Step 8: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/lib/README.md` if needed
- [ ] **MUST:** Verify README content matches actual file state

### Step 9: Consumer Verification (MUST)
- [ ] **MUST:** Grep for any remaining `PROJECT_ROOT / "docs"` patterns
- [ ] **MUST:** Grep for any remaining `PROJECT_ROOT / ".claude"` patterns
- [ ] **MUST:** Verify zero hardcoded path construction remains

---

## Verification

- [ ] Tests pass (`pytest tests/test_configloader_paths.py -v`)
- [ ] Full suite passes (`pytest tests/ --tb=no -q`)
- [ ] **MUST:** Zero `PROJECT_ROOT /` path construction patterns remain
- [ ] **MUST:** All READMEs current

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Typo in path key name breaks function | High | Each file tested independently. Grep verification. |
| ConfigLoader singleton not initialized in test context | Medium | ConfigLoader.reset() in test fixtures. Existing pattern. |
| status.py has 35 replacements — high error count | Medium | Do systematically: group by path key, replace all of same key at once |
| loader.py base_path logic is unique | Low | Special handling documented in design. Keep base_path param. |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 393 | 2026-02-17 | - | Plan authored | Audit: 57 occurrences in 6 files |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-158/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Audit of all hardcoded path patterns | [ ] | Grep output shows 57 patterns pre-migration |
| All paths migrated to ConfigLoader | [ ] | Grep shows zero patterns post-migration |
| New path keys in haios.yaml | [ ] | Read haios.yaml, verify 7 new keys |
| Tests for ConfigLoader path resolution | [ ] | test_configloader_paths.py exists, all pass |
| No regressions | [ ] | Full suite pass count unchanged |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/config/haios.yaml` | 7 new path keys | [ ] | |
| `tests/test_configloader_paths.py` | 8 tests | [ ] | |
| `.claude/haios/lib/status.py` | Zero PROJECT_ROOT / path construction | [ ] | |
| `.claude/haios/lib/scaffold.py` | Zero PROJECT_ROOT / path construction | [ ] | |
| `.claude/haios/lib/observations.py` | Zero PROJECT_ROOT / path construction | [ ] | |
| `Grep: PROJECT_ROOT / "docs"` | **MUST:** Zero matches in lib/*.py | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_configloader_paths.py -v
# Expected: 8 tests passed
Grep(pattern="PROJECT_ROOT / ", path=".claude/haios/lib", glob="**/*.py")
# Expected: Only PROJECT_ROOT definition lines, zero path construction
```

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **MUST:** All WORK.md deliverables verified complete
- [ ] **Runtime consumer exists** (all 6 lib/ modules use ConfigLoader)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated
- [ ] **MUST:** Consumer verification complete (zero hardcoded patterns)
- [ ] Ground Truth Verification completed above

---

## References

- @.claude/haios/config/haios.yaml (path keys)
- @.claude/haios/lib/config.py (ConfigLoader implementation)
- @.claude/haios/epochs/E2_7/arcs/composability/ARC.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CONFIG-001, REQ-CONFIG-003)
- Memory: 85048 (ConfigLoader for all paths), 85073 (Path objects for platform safety), 85355 (STOP multi-level parent traversal)

---
