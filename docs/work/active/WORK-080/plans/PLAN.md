---
template: implementation_plan
status: complete
date: 2026-02-02
backlog_id: WORK-080
title: Single Source Path Constants Implementation
author: Hephaestus
lifecycle_phase: plan
session: 291
version: '1.5'
generated: 2026-02-02
last_updated: '2026-02-02T19:06:02'
---
# Implementation Plan: Single Source Path Constants Implementation

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

Centralize all path constants in haios.yaml and expose via ConfigLoader.paths property, eliminating scattered path definitions across Python modules.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 4 | haios.yaml, config.py, work_engine.py, context_loader.py |
| Lines of code affected | ~50 | Config additions + constant replacements |
| New files to create | 0 | Extending existing files |
| Tests to write | 5 | paths property, get_path simple/interpolated/error, integration |
| Dependencies | 2 | work_engine.py, context_loader.py import ConfigLoader |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | ConfigLoader already used by modules |
| Risk of regression | Low | Existing tests cover ConfigLoader singleton |
| External dependencies | Low | Pure Python, no external services |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Add paths to haios.yaml | 10 min | High |
| Add ConfigLoader.paths + get_path() | 15 min | High |
| Write tests | 15 min | High |
| Migrate work_engine.py | 10 min | High |
| Migrate context_loader.py | 10 min | High |
| **Total** | ~1 hr | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/modules/work_engine.py:63-65
WORK_DIR = Path("docs/work")
ACTIVE_DIR = WORK_DIR / "active"
ARCHIVE_DIR = WORK_DIR / "archive"
QUEUE_CONFIG_PATH = Path(".claude/haios/config/work_queues.yaml")

# .claude/haios/modules/context_loader.py:71-73
MANIFESTO_PATH = Path(".claude/haios/manifesto")
STATUS_PATH = Path(".claude/haios-status.json")
CONFIG_PATH = Path(".claude/haios/config/haios.yaml")
```

**Behavior:** Each module defines its own path constants at module level.

**Result:** When path conventions change, all 11 Python files with hardcoded paths must be manually updated. Drift risk.

### Desired State

```python
# .claude/haios/config/haios.yaml
paths:
  work_dir: "docs/work"
  work_active: "docs/work/active"
  work_archive: "docs/work/archive"
  work_queues: ".claude/haios/config/work_queues.yaml"
  manifesto: ".claude/haios/manifesto"
  status: ".claude/haios-status.json"
  haios_config: ".claude/haios/config/haios.yaml"

# .claude/haios/modules/work_engine.py - usage
config = ConfigLoader.get()
active_dir = config.get_path("work_active")

# .claude/haios/modules/context_loader.py - usage
config = ConfigLoader.get()
manifesto_path = config.get_path("manifesto")
```

**Behavior:** All modules get paths from single source (haios.yaml via ConfigLoader).

**Result:** Path changes require only haios.yaml update. Single source of truth.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: ConfigLoader.paths property returns dict
```python
def test_config_loader_paths_property():
    """ConfigLoader.paths returns paths dict from haios.yaml."""
    from config import ConfigLoader
    ConfigLoader.reset()

    config = ConfigLoader.get()
    paths = config.paths
    assert isinstance(paths, dict)
    assert "work_dir" in paths
    assert paths["work_dir"] == "docs/work"
```

### Test 2: ConfigLoader.get_path without interpolation
```python
def test_config_loader_get_path_simple():
    """get_path returns Path for simple keys."""
    from config import ConfigLoader
    ConfigLoader.reset()

    config = ConfigLoader.get()
    path = config.get_path("work_dir")
    assert isinstance(path, Path)
    assert str(path) == "docs/work"
```

### Test 3: ConfigLoader.get_path with interpolation
```python
def test_config_loader_get_path_interpolated():
    """get_path substitutes placeholders."""
    from config import ConfigLoader
    ConfigLoader.reset()

    config = ConfigLoader.get()
    path = config.get_path("work_item", id="WORK-080")
    assert str(path) == "docs/work/active/WORK-080/WORK.md"
```

### Test 4: ConfigLoader.get_path raises KeyError for missing key
```python
def test_config_loader_get_path_missing_key():
    """get_path raises KeyError for unknown keys."""
    from config import ConfigLoader
    ConfigLoader.reset()

    config = ConfigLoader.get()
    with pytest.raises(KeyError) as exc_info:
        config.get_path("nonexistent_key")
    assert "nonexistent_key" in str(exc_info.value)
```

### Test 5: Backward Compatibility - existing properties unchanged
```python
def test_existing_properties_unchanged():
    """Existing toggles/thresholds properties still work."""
    from config import ConfigLoader
    ConfigLoader.reset()

    config = ConfigLoader.get()
    # Existing behavior must be preserved
    assert config.toggles.get("block_powershell") is True
    assert "observation_pending" in config.thresholds
```

---

## Detailed Design

### Change 1: Add paths section to haios.yaml

**File:** `.claude/haios/config/haios.yaml`
**Location:** After `thresholds:` section (line ~47)

**Addition:**
```yaml
# Path constants (single source of truth - WORK-080)
paths:
  # Work item paths
  work_dir: "docs/work"
  work_active: "docs/work/active"
  work_archive: "docs/work/archive"
  work_item: "docs/work/active/{id}/WORK.md"
  work_plan: "docs/work/active/{id}/plans/PLAN.md"
  work_queues: ".claude/haios/config/work_queues.yaml"

  # Document paths
  checkpoints: "docs/checkpoints"
  reports: "docs/reports"
  adr: "docs/ADR"
  specs: "docs/specs"

  # Plugin paths
  templates: ".claude/templates"
  skills: ".claude/skills"
  commands: ".claude/commands"
  agents: ".claude/agents"
  hooks: ".claude/hooks"

  # Config paths
  haios_config: ".claude/haios/config"
  manifesto: ".claude/haios/manifesto"
  status: ".claude/haios-status.json"
  status_slim: ".claude/haios-status-slim.json"
```

### Change 2: Add ConfigLoader.paths property and get_path() method

**File:** `.claude/haios/lib/config.py`
**Location:** After `node_bindings` property (line ~91)

**Addition:**
```python
    @property
    def paths(self) -> Dict[str, str]:
        """Path constants from haios.yaml (single source of truth - WORK-080)."""
        return self._haios.get("paths", {})

    def get_path(self, key: str, **kwargs) -> Path:
        """
        Get path with placeholder substitution.

        Args:
            key: Path key from haios.yaml paths section
            **kwargs: Placeholder values (e.g., id="WORK-080")

        Returns:
            Path object with placeholders resolved

        Raises:
            KeyError: If key not found in paths
        """
        template = self.paths.get(key)
        if template is None:
            raise KeyError(f"Path key '{key}' not found in haios.yaml paths section")
        resolved = template.format(**kwargs) if kwargs else template
        return Path(resolved)
```

### Change 3: Migrate work_engine.py

**File:** `.claude/haios/modules/work_engine.py`

**Current Code (lines 63-65, 125):**
```python
WORK_DIR = Path("docs/work")
ACTIVE_DIR = WORK_DIR / "active"
ARCHIVE_DIR = WORK_DIR / "archive"
# ...
QUEUE_CONFIG_PATH = Path(".claude/haios/config/work_queues.yaml")
```

**Changed Code:**
```python
# Remove module-level constants, add import
try:
    from ..lib.config import ConfigLoader
except ImportError:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
    from config import ConfigLoader
```

**Property changes (lines 167-174):**
```python
    @property
    def active_dir(self) -> Path:
        """Path to active work items directory."""
        config = ConfigLoader.get()
        return self._base_path / config.get_path("work_active")

    @property
    def archive_dir(self) -> Path:
        """Path to archived work items directory."""
        config = ConfigLoader.get()
        return self._base_path / config.get_path("work_archive")
```

### Change 4: Migrate context_loader.py

**File:** `.claude/haios/modules/context_loader.py`

**Current Code (lines 71-73):**
```python
    MANIFESTO_PATH = Path(".claude/haios/manifesto")
    STATUS_PATH = Path(".claude/haios-status.json")
    CONFIG_PATH = Path(".claude/haios/config/haios.yaml")
```

**Changed Code:**
```python
    # Remove class-level constants, use ConfigLoader in methods
    # Add import at top:
    try:
        from ..lib.config import ConfigLoader
    except ImportError:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "lib"))
        from config import ConfigLoader
```

**Method changes:**
```python
    def _load_config(self) -> None:
        """Load context config from haios.yaml."""
        config = ConfigLoader.get()
        config_path = self._project_root / config.get_path("haios_config") / "haios.yaml"
        # ... rest unchanged
```

### Call Chain Context

```
WorkEngine.__init__()
    |
    +-> active_dir (property)
    |       +-> ConfigLoader.get()
    |       +-> ConfigLoader.get_path("work_active")
    |       Returns: Path
    |
    +-> get_work(id)
            +-> _find_work_file(id)
                    +-> active_dir  # Uses the property
```

### Function/Component Signatures

```python
@property
def paths(self) -> Dict[str, str]:
    """Path constants from haios.yaml (single source of truth - WORK-080)."""

def get_path(self, key: str, **kwargs) -> Path:
    """
    Get path with placeholder substitution.

    Args:
        key: Path key from haios.yaml paths section (e.g., "work_item")
        **kwargs: Placeholder values (e.g., id="WORK-080")

    Returns:
        Path object with placeholders resolved

    Raises:
        KeyError: If key not found in paths section

    Examples:
        config.get_path("work_dir")  # Returns Path("docs/work")
        config.get_path("work_item", id="WORK-080")  # Returns Path("docs/work/active/WORK-080/WORK.md")
    """
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Path storage format | Strings with {placeholder} syntax | Dual consumption: Python interpolates, prose uses raw strings |
| Error handling | KeyError for missing keys | Fail-fast prevents silent bugs from typos |
| Return type | Path object | Consistent with existing code patterns |
| Singleton access | ConfigLoader.get() | Already established pattern, no change needed |
| Import pattern | try/except conditional | Matches existing sibling module pattern (work_engine.py:51-54) |

### Input/Output Examples

**get_path simple:**
```python
config = ConfigLoader.get()
config.get_path("work_dir")
# Returns: Path("docs/work")
```

**get_path interpolated:**
```python
config.get_path("work_item", id="WORK-080")
# Returns: Path("docs/work/active/WORK-080/WORK.md")
```

**get_path missing key:**
```python
config.get_path("nonexistent")
# Raises: KeyError("Path key 'nonexistent' not found in haios.yaml paths section")
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Missing key | Raise KeyError with descriptive message | Test 4 |
| Empty paths section | Return empty dict, get_path raises KeyError | Graceful degradation |
| Placeholder without kwargs | Return template string as-is (e.g., "{id}" remains) | Acceptable - caller error |

### Open Questions

**Q: Should we migrate all 11 files in this work item?**

A: No. Scope limited to config.py (core), work_engine.py, context_loader.py. Remaining 8 files can be migrated incrementally in follow-up work. This establishes pattern without excessive scope.

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
| N/A | - | - | No operator decisions required. Design from INV-041 is complete. |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add 5 tests to `tests/test_config.py` for paths functionality
- [ ] Verify all new tests fail (RED) - paths property and get_path don't exist yet

### Step 2: Add paths section to haios.yaml
- [ ] Add `paths:` section after `thresholds:` in `.claude/haios/config/haios.yaml`
- [ ] Include all path definitions per Detailed Design
- [ ] Test 1 (paths property) passes (GREEN)

### Step 3: Add ConfigLoader.paths property
- [ ] Add `paths` property to `.claude/haios/lib/config.py`
- [ ] Test 1 passes (GREEN)

### Step 4: Add ConfigLoader.get_path() method
- [ ] Add `get_path()` method to `.claude/haios/lib/config.py`
- [ ] Tests 2, 3, 4 pass (GREEN)

### Step 5: Migrate work_engine.py
- [ ] Remove WORK_DIR, ACTIVE_DIR, ARCHIVE_DIR, QUEUE_CONFIG_PATH constants
- [ ] Add ConfigLoader import (try/except pattern)
- [ ] Update `active_dir` and `archive_dir` properties to use ConfigLoader
- [ ] Run `pytest tests/test_work_engine.py -v` - verify no regressions

### Step 6: Migrate context_loader.py
- [ ] Remove MANIFESTO_PATH, STATUS_PATH, CONFIG_PATH class constants
- [ ] Add ConfigLoader import (try/except pattern)
- [ ] Update `_load_config()` and other methods to use ConfigLoader
- [ ] Run `pytest tests/test_context_loader.py -v` - verify no regressions

### Step 7: Integration Verification
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] All tests pass (no regressions)
- [ ] Test 5 (backward compatibility) passes

### Step 8: Update Documentation
- [ ] Update CLAUDE.md with ConfigLoader.paths usage pattern
- [ ] Verify `.claude/haios/lib/README.md` mentions config.py paths functionality

### Step 9: Consumer Verification (MUST)
- [ ] `Grep(pattern="WORK_DIR = Path|ACTIVE_DIR = |ARCHIVE_DIR = ", path=".claude/haios/modules/")` returns empty
- [ ] `Grep(pattern="MANIFESTO_PATH = Path|STATUS_PATH = Path|CONFIG_PATH = Path", path=".claude/haios/modules/")` returns empty
- [ ] No stale module-level path constants remain

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Breaking existing imports | Medium | Migrate one module at a time, run tests after each |
| Missing path keys at runtime | Low | KeyError with descriptive message guides debugging |
| Circular imports | Medium | ConfigLoader is in lib/, modules import from lib/ (no circular) |
| Spec misalignment | Low | Design from INV-041 already verified, memory refs 83179-83183 |
| Regression in existing tests | Medium | Run full test suite after each migration step |

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

**MUST** read `docs/work/active/WORK-080/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Add `paths:` section to haios.yaml | [ ] | Read file, verify section exists |
| Add `ConfigLoader.paths` property | [ ] | Read config.py, verify property exists |
| Add `ConfigLoader.get_path()` method | [ ] | Read config.py, verify method exists |
| Migrate work_engine.py constants | [ ] | Grep returns empty for old constants |
| Migrate context_loader.py constants | [ ] | Grep returns empty for old constants |
| Tests for paths functionality | [ ] | pytest passes for new tests |
| Update CLAUDE.md | [ ] | Read file, verify pattern documented |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/config/haios.yaml` | Contains `paths:` section with all definitions | [ ] | |
| `.claude/haios/lib/config.py` | Has `paths` property and `get_path()` method | [ ] | |
| `tests/test_config.py` | Has 5 new tests for paths functionality | [ ] | |
| `.claude/haios/modules/work_engine.py` | No WORK_DIR/ACTIVE_DIR/ARCHIVE_DIR constants | [ ] | |
| `.claude/haios/modules/context_loader.py` | No MANIFESTO_PATH/STATUS_PATH/CONFIG_PATH constants | [ ] | |
| `CLAUDE.md` | Documents ConfigLoader.paths pattern | [ ] | |

**Verification Commands:**
```bash
# Run all config tests
pytest tests/test_config.py -v
# Expected: All tests pass including 5 new paths tests

# Verify no stale constants in work_engine.py
Grep(pattern="^WORK_DIR = |^ACTIVE_DIR = |^ARCHIVE_DIR = ", path=".claude/haios/modules/work_engine.py")
# Expected: No matches

# Verify no stale constants in context_loader.py
Grep(pattern="MANIFESTO_PATH = Path|STATUS_PATH = Path|CONFIG_PATH = Path", path=".claude/haios/modules/context_loader.py")
# Expected: No matches
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

- INV-041: Single Source Path Constants Architecture (spawned WORK-080)
- Memory refs: 83179-83183 (INV-041 findings and architecture decision)
- WORK-080: Work item definition
- E2-246: Consolidate Config Files MVP (established ConfigLoader pattern)

---
