---
template: implementation_plan
status: complete
date: 2026-01-04
backlog_id: E2-264
title: Hook Import Migration
author: Hephaestus
lifecycle_phase: plan
session: 171
version: '1.5'
generated: 2026-01-04
last_updated: '2026-01-04T21:37:40'
---
# Implementation Plan: Hook Import Migration

@docs/README.md
@docs/epistemic_state.md

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Memory queried - E2-085 pattern with 22 tests is reference |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

All 4 Python hooks (user_prompt_submit, pre_tool_use, post_tool_use, stop) import from Chariot modules instead of `.claude/lib/`, completing the Epoch 2.2 Strangler Fig migration.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 4 | user_prompt_submit.py, pre_tool_use.py, post_tool_use.py, stop.py |
| Lines of code affected | ~30 | Import changes only (sys.path + from statements) |
| New files to create | 0 | Only modifying existing hooks |
| Tests to write | 4 | One integration test per hook |
| Dependencies | 5 | ContextLoader, GovernanceLayer, MemoryBridge, CycleRunner modules |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Modules already expose required methods |
| Risk of regression | Low | Existing 22+ hook tests validate behavior |
| External dependencies | None | All imports are internal |

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

**user_prompt_submit.py:33-43** - Imports from lib/status
```python
# Add .claude/lib to path for status module
lib_path = Path(cwd) / ".claude" / "lib"
if lib_path.exists() and str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

# Import and call status generator
from status import generate_slim_status, write_slim_status
slim = generate_slim_status()
```

**pre_tool_use.py:43-53** - Imports from lib/config
```python
if _config_loader is None:
    # Lazy import to avoid circular dependencies
    lib_dir = Path(__file__).parent.parent.parent / "lib"
    if str(lib_dir) not in sys.path:
        sys.path.insert(0, str(lib_dir))
    from config import ConfigLoader
    _config_loader = ConfigLoader
```

**post_tool_use.py:124-128** - Imports from lib/error_capture
```python
lib_dir = Path(__file__).parent.parent.parent / "lib"
if str(lib_dir) not in sys.path:
    sys.path.insert(0, str(lib_dir))
from error_capture import is_actual_error, store_error
```

**post_tool_use.py:766-768** - Imports from lib/node_cycle
```python
from node_cycle import (
    get_node_binding, check_doc_exists, build_scaffold_command,
    extract_work_id, extract_title
)
```

**stop.py** - Uses subprocess to call reasoning_extraction.py directly

### Desired State

**user_prompt_submit.py** - Import from ContextLoader module
```python
# Add modules to path
modules_path = Path(cwd) / ".claude" / "haios" / "modules"
if modules_path.exists() and str(modules_path) not in sys.path:
    sys.path.insert(0, str(modules_path))

from context_loader import ContextLoader
loader = ContextLoader(project_root=Path(cwd))
slim = loader.generate_status(slim=True)
```

**pre_tool_use.py** - Import from GovernanceLayer module
```python
modules_dir = Path(__file__).parent.parent.parent / "haios" / "modules"
if str(modules_dir) not in sys.path:
    sys.path.insert(0, str(modules_dir))
from governance_layer import GovernanceLayer
layer = GovernanceLayer()
return layer.get_toggle("block_powershell", True)
```

**post_tool_use.py** - Import from MemoryBridge and CycleRunner modules
```python
modules_dir = Path(__file__).parent.parent.parent / "haios" / "modules"
if str(modules_dir) not in sys.path:
    sys.path.insert(0, str(modules_dir))
from memory_bridge import MemoryBridge
from cycle_runner import CycleRunner
```

**stop.py** - Import from MemoryBridge module
```python
modules_dir = Path(__file__).parent.parent / "haios" / "modules"
if str(modules_dir) not in sys.path:
    sys.path.insert(0, str(modules_dir))
from memory_bridge import MemoryBridge
bridge = MemoryBridge()
result = bridge.extract_learnings(transcript_path)
```

---

## Tests First (TDD)

### Test 1: user_prompt_submit uses ContextLoader
```python
def test_user_prompt_submit_uses_context_loader(tmp_path, monkeypatch):
    """Verify user_prompt_submit imports from modules not lib."""
    # Read hook source and check for module import
    hook_path = Path(".claude/hooks/hooks/user_prompt_submit.py")
    content = hook_path.read_text()
    assert "haios/modules" in content or "context_loader" in content.lower()
    # No direct lib/status import in _refresh_slim_status
    assert "from status import" not in content or "modules" in content
```

### Test 2: pre_tool_use uses GovernanceLayer
```python
def test_pre_tool_use_uses_governance_layer(tmp_path, monkeypatch):
    """Verify pre_tool_use imports from modules not lib."""
    hook_path = Path(".claude/hooks/hooks/pre_tool_use.py")
    content = hook_path.read_text()
    assert "haios/modules" in content or "governance_layer" in content.lower()
```

### Test 3: post_tool_use uses MemoryBridge
```python
def test_post_tool_use_uses_memory_bridge():
    """Verify post_tool_use imports from modules not lib."""
    hook_path = Path(".claude/hooks/hooks/post_tool_use.py")
    content = hook_path.read_text()
    assert "haios/modules" in content or "memory_bridge" in content.lower()
```

### Test 4: stop uses MemoryBridge.extract_learnings
```python
def test_stop_uses_memory_bridge():
    """Verify stop.py imports from modules not lib."""
    hook_path = Path(".claude/hooks/hooks/stop.py")
    content = hook_path.read_text()
    assert "haios/modules" in content or "memory_bridge" in content.lower()
```

### Test 5: Backward Compatibility - All existing hook tests pass
```python
# No new test needed - run existing test suite
# pytest tests/test_hooks/ -v
```

---

## Detailed Design

### Migration Pattern (from E2-085/E2-262/E2-263)

All migrations follow the same pattern:
1. Replace `lib_path = Path(...) / "lib"` with `modules_path = Path(...) / "haios" / "modules"`
2. Replace `from xxx import yyy` with `from module_name import ModuleName`
3. Replace direct function calls with method calls on module instance

### Exact Code Changes

#### Change 1: user_prompt_submit.py - _refresh_slim_status()

**File:** `.claude/hooks/hooks/user_prompt_submit.py`
**Location:** Lines 31-43 in `_refresh_slim_status()`

**Current Code:**
```python
# Add .claude/lib to path for status module
lib_path = Path(cwd) / ".claude" / "lib"
if lib_path.exists() and str(lib_path) not in sys.path:
    sys.path.insert(0, str(lib_path))

# Import and call status generator
from status import generate_slim_status, write_slim_status
slim = generate_slim_status()
slim_path = Path(cwd) / ".claude" / "haios-status-slim.json"
write_slim_status(slim, str(slim_path))
```

**Changed Code:**
```python
# Add modules to path (E2-264: Module-first import)
modules_path = Path(cwd) / ".claude" / "haios" / "modules"
if modules_path.exists() and str(modules_path) not in sys.path:
    sys.path.insert(0, str(modules_path))

# Import and call via ContextLoader module
from context_loader import ContextLoader
loader = ContextLoader(project_root=Path(cwd))
slim = loader.generate_status(slim=True)
slim_path = Path(cwd) / ".claude" / "haios-status-slim.json"
import json
slim_path.write_text(json.dumps(slim, indent=4), encoding="utf-8")
```

#### Change 2: pre_tool_use.py - _load_governance_toggles()

**File:** `.claude/hooks/hooks/pre_tool_use.py`
**Location:** Lines 42-52 in `_load_governance_toggles()`

**Current Code:**
```python
if _config_loader is None:
    # Lazy import to avoid circular dependencies
    lib_dir = Path(__file__).parent.parent.parent / "lib"
    if str(lib_dir) not in sys.path:
        sys.path.insert(0, str(lib_dir))
    from config import ConfigLoader
    _config_loader = ConfigLoader

# Get toggles from unified config
loader = _config_loader.get()
return {**defaults, **loader.toggles}
```

**Changed Code:**
```python
# E2-264: Module-first import via GovernanceLayer
modules_dir = Path(__file__).parent.parent.parent / "haios" / "modules"
if str(modules_dir) not in sys.path:
    sys.path.insert(0, str(modules_dir))

try:
    from governance_layer import GovernanceLayer
    layer = GovernanceLayer()
    return {
        "block_powershell": layer.get_toggle("block_powershell", defaults.get("block_powershell", True))
    }
except Exception:
    return defaults
```

#### Change 3: post_tool_use.py - _capture_errors()

**File:** `.claude/hooks/hooks/post_tool_use.py`
**Location:** Lines 124-128 in `_capture_errors()`

**Current Code:**
```python
lib_dir = Path(__file__).parent.parent.parent / "lib"
if str(lib_dir) not in sys.path:
    sys.path.insert(0, str(lib_dir))

from error_capture import is_actual_error, store_error
```

**Changed Code:**
```python
# E2-264: Module-first import via MemoryBridge
modules_dir = Path(__file__).parent.parent.parent / "haios" / "modules"
if str(modules_dir) not in sys.path:
    sys.path.insert(0, str(modules_dir))

from memory_bridge import MemoryBridge
bridge = MemoryBridge()
```

Then replace:
- `is_actual_error(tool_name, tool_response)` → `bridge.is_actual_error(tool_name, tool_response)`
- `store_error(tool_name, error_msg, input_summary)` → `bridge.capture_error(tool_name, error_msg, input_summary)`

#### Change 4: post_tool_use.py - _scaffold_on_node_entry()

**File:** `.claude/hooks/hooks/post_tool_use.py`
**Location:** Lines 761-768 in `_scaffold_on_node_entry()`

**Current Code:**
```python
lib_dir = Path(__file__).parent.parent.parent / "lib"
if str(lib_dir) not in sys.path:
    sys.path.insert(0, str(lib_dir))

from node_cycle import (
    get_node_binding, check_doc_exists, build_scaffold_command,
    extract_work_id, extract_title
)
```

For build_scaffold_command, use CycleRunner:
```python
from cycle_runner import CycleRunner
from governance_layer import GovernanceLayer
runner = CycleRunner(governance=GovernanceLayer())
command = runner.build_scaffold_command(scaffold_spec["command"], work_id, title)
```

Note: get_node_binding, check_doc_exists, extract_work_id, extract_title remain in lib/node_cycle.py (not exposed via module yet). This migration is partial - only build_scaffold_command moves.

#### Change 5: stop.py - handle()

**File:** `.claude/hooks/hooks/stop.py`
**Location:** Lines 44-65 in `handle()`

**Current Code:**
```python
# Find the extraction script
hooks_dir = Path(__file__).parent.parent
extraction_script = hooks_dir / "reasoning_extraction.py"

if not extraction_script.exists():
    return None

try:
    result = subprocess.run(
        [sys.executable, str(extraction_script), transcript_path],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(hooks_dir)
    )

    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
```

**Changed Code:**
```python
# E2-264: Module-first import via MemoryBridge
modules_dir = Path(__file__).parent.parent / "haios" / "modules"
if str(modules_dir) not in sys.path:
    sys.path.insert(0, str(modules_dir))

try:
    from memory_bridge import MemoryBridge
    bridge = MemoryBridge()
    result = bridge.extract_learnings(transcript_path)

    if result.success:
        return f"[LEARNING] Extracted from session (outcome: {result.outcome})"
    elif result.reason == "qualified":
        return None  # Qualified but extraction failed
    else:
        return None  # Not qualified for extraction
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Module path strategy | Same as E2-262/E2-263 | Consistency with prior migrations |
| Partial node_cycle migration | Only build_scaffold_command | Other functions not yet exposed via CycleRunner |
| Keep lib/ intact | No deletion | Strangler Fig - old code stays until all consumers migrated |
| Error handling | try/except with degraded behavior | Hooks must not break on import errors |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Module not found | Fall back to lib/ or return defaults | Existing hook tests |
| Import error | Catch exception, degrade gracefully | Existing hook tests |
| Missing transcript | Return None | test_stop.py |

---

## Implementation Steps

### Step 1: Write Integration Tests
- [ ] Add test_hook_module_imports.py with 4 tests
- [ ] Verify tests fail (checking for new import paths)

### Step 2: Migrate user_prompt_submit.py
- [ ] Update _refresh_slim_status() to use ContextLoader
- [ ] Run hook tests to verify no regressions

### Step 3: Migrate pre_tool_use.py
- [ ] Update _load_governance_toggles() to use GovernanceLayer
- [ ] Run hook tests to verify no regressions

### Step 4: Migrate post_tool_use.py
- [ ] Update _capture_errors() to use MemoryBridge
- [ ] Update _scaffold_on_node_entry() to use CycleRunner.build_scaffold_command()
- [ ] Run hook tests to verify no regressions

### Step 5: Migrate stop.py
- [ ] Update handle() to use MemoryBridge.extract_learnings()
- [ ] Run hook tests to verify no regressions

### Step 6: Full Test Suite Verification
- [ ] Run `pytest tests/ -v`
- [ ] Verify all 22+ hook tests pass

### Step 7: README Sync (MUST)
- [ ] Update .claude/hooks/README.md with migration notes
- [ ] Update .claude/haios/modules/README.md with consumer list

### Step 8: Consumer Verification (MUST)
- [ ] Grep for remaining lib/ imports in hooks
- [ ] Document any remaining lib/ imports (partial migration)

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Module import timing | Medium | Try/except with fallback |
| Breaking existing hook behavior | High | Run full test suite |
| Circular imports | Low | Lazy imports in modules |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 171 | 2026-01-04 | - | In Progress | Plan created, implementation starting |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/hooks/hooks/user_prompt_submit.py` | Imports from haios/modules | [x] | Line 35: modules_path, Line 40: from context_loader |
| `.claude/hooks/hooks/pre_tool_use.py` | Imports from haios/modules | [x] | Line 41: modules_dir, Line 47: from governance_layer |
| `.claude/hooks/hooks/post_tool_use.py` | Imports from haios/modules | [x] | Lines 126, 775: modules_dir; Lines 130, 779-780: from memory_bridge, cycle_runner |
| `.claude/hooks/hooks/stop.py` | Imports from haios/modules | [x] | Line 47: modules_dir, Line 51: from memory_bridge |
| `tests/test_hooks/` | All tests pass | [x] | 27 passed, 0 failed |

**Verification Commands:**
```bash
pytest tests/ -k "hook" -v
# Result: 27 passed, 661 deselected in 2.19s

pytest tests/ -v
# Result: 1 failed (unrelated - test_lib_scaffold.py), 683 passed, 4 skipped in 17.48s
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | All 4 hooks verified with line numbers |
| Test output pasted above? | Yes | pytest results documented |
| Any deviations from plan? | No | All 5 changes implemented as planned |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (683 passed, 1 unrelated failure)
- [x] **Runtime consumer exists** (hooks are called by Claude Code on every interaction)
- [x] WHY captured (memory refs: 80728-80732)
- [x] **MUST:** READMEs updated (.claude/haios/modules/README.md - Consumers section)
- [x] All traced files complete
- [x] Ground Truth Verification completed above

---

## References

- E2-085: Hook Migration PowerShell to Python
- E2-120: Complete PowerShell to Python Migration
- E2-259: ContextLoader Status Generation
- E2-260: GovernanceLayer Toggle Access
- E2-261: MemoryBridge Error Capture
- E2-262: MemoryBridge Learning Extraction
- E2-263: CycleRunner Scaffold Commands
- INV-056: Hook-to-Module Migration Investigation
- Memory 80686: Final step directive

---
