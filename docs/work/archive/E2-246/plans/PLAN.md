---
template: implementation_plan
status: complete
date: 2026-01-03
backlog_id: E2-246
title: Consolidate Config Files MVP
author: Hephaestus
lifecycle_phase: plan
session: 159
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-03T14:54:49'
---
# Implementation Plan: Consolidate Config Files MVP

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

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

Consolidate the 3 existing YAML config files (.claude/config/) into a new modular config structure (.claude/haios/config/) with 3 domain-organized files (haios.yaml, cycles.yaml, components.yaml) that enables future module implementations (E2-240, E2-241, E2-242) while maintaining backward compatibility with current config loaders.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 4 | `pre_tool_use.py`, `observations.py`, `node_cycle.py`, + tests |
| Lines of code affected | ~119 | `wc -l .claude/config/*.yaml` (total existing config) |
| New files to create | 4 | `haios.yaml`, `cycles.yaml`, `components.yaml`, + config loader |
| Tests to write | 5 | Config loading, migration, backward compat, schema validation |
| Dependencies | 3 | `pre_tool_use.py`, `observations.py`, `node_cycle.py` |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Med | 3 Python files load config |
| Risk of regression | Low | Good test coverage for hooks |
| External dependencies | Low | Pure YAML, no external services |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Phase 1: Create new config files | 20 min | High |
| Phase 2: Create config loader | 30 min | High |
| Phase 3: Update consumers | 30 min | Med |
| Phase 4: Tests + validation | 40 min | Med |
| **Total** | ~2 hours | High |

---

## Current State vs Desired State

### Current State

**Directory structure:**
```
.claude/config/
├── governance-toggles.yaml   (25 lines) - PowerShell blocking toggle
├── node-cycle-bindings.yaml  (68 lines) - DAG node → cycle mappings
└── routing-thresholds.yaml   (26 lines) - Observation pending thresholds
```

**Current loading pattern (pre_tool_use.py:27-38):**
```python
def _load_governance_toggles() -> dict:
    """
    Load governance toggles from config file.
    Returns empty dict on failure (safe defaults).
    """
    global _governance_toggles_cache
    if _governance_toggles_cache is not None:
        return _governance_toggles_cache

    config_path = Path(__file__).parent.parent.parent / "config" / "governance-toggles.yaml"
```

**Behavior:** Each consumer has its own hardcoded path and loading logic.

**Problem:**
- 3 separate loading functions with duplicated patterns
- Paths scattered across codebase
- No unified config access for future modules

### Desired State

**Directory structure:**
```
.claude/haios/config/
├── haios.yaml       - Manifest + governance toggles + thresholds (merged)
├── cycles.yaml      - Cycle definitions + gates + node-bindings (merged)
└── components.yaml  - Future: skill/agent/hook registries
```

**Unified loading pattern (.claude/lib/config.py):**
```python
from .claude.lib.config import load_config

class ConfigLoader:
    """Unified config access for HAIOS modules."""

    _instance: Optional["ConfigLoader"] = None

    @classmethod
    def get(cls) -> "ConfigLoader":
        """Get singleton config instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.haios = self._load("haios.yaml")
        self.cycles = self._load("cycles.yaml")
        self.components = self._load("components.yaml")

    @property
    def toggles(self) -> dict:
        """Governance toggles (backward compat)."""
        return self.haios.get("toggles", {})

    @property
    def thresholds(self) -> dict:
        """Routing thresholds (backward compat)."""
        return self.haios.get("thresholds", {})

    @property
    def node_bindings(self) -> dict:
        """Node-cycle bindings (backward compat)."""
        return self.cycles.get("nodes", {})
```

**Behavior:** Single config loader with domain-organized files and backward-compatible accessors.

**Result:** Clean foundation for E2-240 (GovernanceLayer), E2-241 (MemoryBridge), E2-242 (WorkEngine) to consume config.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Config Loader Singleton
```python
def test_config_loader_singleton():
    """ConfigLoader.get() returns same instance."""
    loader1 = ConfigLoader.get()
    loader2 = ConfigLoader.get()
    assert loader1 is loader2
```

### Test 2: Load HAIOS Config
```python
def test_load_haios_config():
    """haios.yaml loads with toggles and thresholds."""
    loader = ConfigLoader.get()
    assert "toggles" in loader.haios
    assert "thresholds" in loader.haios
    assert loader.toggles.get("block_powershell") is True
```

### Test 3: Load Cycles Config
```python
def test_load_cycles_config():
    """cycles.yaml loads with node bindings."""
    loader = ConfigLoader.get()
    assert "nodes" in loader.cycles
    assert "backlog" in loader.node_bindings
    assert "discovery" in loader.node_bindings
```

### Test 4: Backward Compatibility - Toggles
```python
def test_backward_compat_toggles():
    """loader.toggles matches old governance-toggles.yaml content."""
    loader = ConfigLoader.get()
    # Old behavior: block_powershell from governance-toggles.yaml
    assert loader.toggles.get("block_powershell") is True
```

### Test 5: Missing Config Fallback
```python
def test_missing_config_returns_empty():
    """Missing config file returns empty dict (graceful degradation)."""
    loader = ConfigLoader.get()
    # components.yaml may not exist initially
    assert loader.components == {} or isinstance(loader.components, dict)
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
     4. Input/output examples with REAL data from the system -->

### File 1: New Config Loader

**File:** `.claude/lib/config.py` (NEW)

```python
"""
Unified configuration loader for HAIOS modules.

Provides single access point for all config files:
- haios.yaml: toggles, thresholds, manifest
- cycles.yaml: node bindings, cycle definitions
- components.yaml: skill/agent/hook registries

Usage:
    from .claude.lib.config import ConfigLoader
    config = ConfigLoader.get()
    if config.toggles.get("block_powershell"):
        # handle blocked
"""
from pathlib import Path
from typing import Any, Dict, Optional
import yaml

# Config directory relative to this file
CONFIG_DIR = Path(__file__).parent.parent / "haios" / "config"


class ConfigLoader:
    """Unified config access for HAIOS modules."""

    _instance: Optional["ConfigLoader"] = None

    @classmethod
    def get(cls) -> "ConfigLoader":
        """Get singleton config instance. Creates on first call."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton (for testing)."""
        cls._instance = None

    def __init__(self):
        """Load all config files on init."""
        self._haios = self._load("haios.yaml")
        self._cycles = self._load("cycles.yaml")
        self._components = self._load("components.yaml")

    def _load(self, filename: str) -> Dict[str, Any]:
        """Load a YAML config file, returning empty dict on failure."""
        path = CONFIG_DIR / filename
        if not path.exists():
            return {}
        try:
            with open(path) as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    @property
    def haios(self) -> Dict[str, Any]:
        """Full haios.yaml content."""
        return self._haios

    @property
    def cycles(self) -> Dict[str, Any]:
        """Full cycles.yaml content."""
        return self._cycles

    @property
    def components(self) -> Dict[str, Any]:
        """Full components.yaml content."""
        return self._components

    # Backward compatibility accessors
    @property
    def toggles(self) -> Dict[str, Any]:
        """Governance toggles (backward compat for governance-toggles.yaml)."""
        return self._haios.get("toggles", {})

    @property
    def thresholds(self) -> Dict[str, Any]:
        """Routing thresholds (backward compat for routing-thresholds.yaml)."""
        return self._haios.get("thresholds", {})

    @property
    def node_bindings(self) -> Dict[str, Any]:
        """Node-cycle bindings (backward compat for node-cycle-bindings.yaml)."""
        return self._cycles.get("nodes", {})
```

### File 2: haios.yaml

**File:** `.claude/haios/config/haios.yaml` (NEW - consolidates governance-toggles.yaml + routing-thresholds.yaml)

```yaml
# HAIOS System Configuration
# Consolidates: governance-toggles.yaml, routing-thresholds.yaml
# Version: 1.0 (E2-246)

# Plugin manifest (for portable plugin spec)
manifest:
  name: haios
  version: "2.2"
  description: "Hybrid AI Operating System - Trust Engine"

# Governance toggles (from governance-toggles.yaml)
toggles:
  block_powershell: true  # PowerShell through bash mangles $_ variables
  # block_sql: true       # Future: migrate from hardcoded

# Routing thresholds (from routing-thresholds.yaml)
thresholds:
  observation_pending:
    enabled: true
    max_count: 10
    divert_to: observation-triage-cycle
    escape_priorities: [critical]
```

### File 3: cycles.yaml

**File:** `.claude/haios/config/cycles.yaml` (NEW - consolidates node-cycle-bindings.yaml)

```yaml
# HAIOS Cycle Configuration
# Consolidates: node-cycle-bindings.yaml
# Version: 1.0 (E2-246)

# Node-to-cycle bindings (from node-cycle-bindings.yaml)
nodes:
  backlog:
    cycle: null
    scaffold: []
    exit_criteria: []

  discovery:
    cycle: investigation-cycle
    scaffold:
      - type: investigation
        command: '/new-investigation {id} "{title}"'
        pattern: "docs/investigations/INVESTIGATION-{id}-*.md"
    exit_criteria:
      - type: file_status
        pattern: "docs/investigations/INVESTIGATION-{id}-*.md"
        field: status
        value: complete
        message: "Investigation status not complete"
      - type: section_content
        pattern: "docs/investigations/INVESTIGATION-{id}-*.md"
        section: "## Findings"
        min_length: 50
        message: "Findings section is empty or placeholder"

  plan:
    cycle: plan-cycle
    scaffold:
      - type: plan
        command: '/new-plan {id} "{title}"'
        pattern: "docs/work/active/{id}/plans/PLAN.md"
    exit_criteria:
      - type: file_status
        pattern: "docs/work/active/{id}/plans/PLAN.md"
        field: status
        value: approved
        message: "Plan status not approved (still draft)"

  implement:
    cycle: implementation-cycle
    scaffold: []
    exit_criteria: []

  close:
    cycle: closure-cycle
    scaffold: []
    exit_criteria: []
```

### File 4: components.yaml

**File:** `.claude/haios/config/components.yaml` (NEW - placeholder for future)

```yaml
# HAIOS Component Registry
# Future: skill, agent, hook registries
# Version: 1.0 (E2-246)

# Placeholder - will be populated by E2-240 (GovernanceLayer)
skills: {}
agents: {}
hooks: {}
```

### Consumer Updates

**File:** `.claude/hooks/hooks/pre_tool_use.py`
**Change:** Replace `_load_governance_toggles()` with `ConfigLoader.get().toggles`

```diff
- from pathlib import Path
- import yaml
+ from ...lib.config import ConfigLoader

- # Cache for governance toggles
- _governance_toggles_cache: dict | None = None

- def _load_governance_toggles() -> dict:
-     """Load governance toggles from config file."""
-     global _governance_toggles_cache
-     if _governance_toggles_cache is not None:
-         return _governance_toggles_cache
-     config_path = Path(__file__).parent.parent.parent / "config" / "governance-toggles.yaml"
-     ...

  def _check_powershell_blocking(tool_input: dict) -> dict | None:
-     toggles = _load_governance_toggles()
+     toggles = ConfigLoader.get().toggles
      if toggles.get("block_powershell", True):
```

**File:** `.claude/lib/observations.py`
**Change:** Replace threshold loading with `ConfigLoader.get().thresholds`

```diff
- THRESHOLD_CONFIG_PATH = Path(__file__).parent.parent / "config" / "routing-thresholds.yaml"
+ from .config import ConfigLoader

- def _load_threshold_config() -> dict:
-     """Load threshold configuration from routing-thresholds.yaml."""
-     ...

  def get_pending_observation_threshold() -> dict:
-     config = _load_threshold_config()
+     config = ConfigLoader.get().thresholds
      return config.get("observation_pending", {})
```

**File:** `.claude/lib/node_cycle.py`
**Change:** Replace bindings loading with `ConfigLoader.get().node_bindings`

```diff
- CONFIG_PATH = Path(".claude/config/node-cycle-bindings.yaml")
+ from .config import ConfigLoader

- def load_node_cycle_bindings() -> Dict[str, Any]:
-     """Load node-cycle bindings from config file."""
-     ...

  def get_cycle_for_node(node: str) -> Optional[str]:
-     bindings = load_node_cycle_bindings()
+     bindings = ConfigLoader.get().node_bindings
      node_config = bindings.get(node, {})
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Singleton pattern | `ConfigLoader.get()` | Config loaded once, cached. No repeated file I/O. |
| Graceful degradation | Return `{}` on missing/invalid | Matches current behavior. Safe defaults. |
| Directory location | `.claude/haios/config/` | Future modules live under `.claude/haios/`. Keeps plugin portable. |
| Backward compat accessors | `.toggles`, `.thresholds`, `.node_bindings` | Consumers can migrate incrementally. |
| 3-file consolidation | haios/cycles/components | Per INV-053: domain organization, not file proliferation. |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Config file missing | Return empty dict | Test 5 |
| Invalid YAML | Return empty dict, log warning | Manual verification |
| Singleton reset needed | `ConfigLoader.reset()` for tests | Test fixture |
| Old config still present | Ignored - consumers use new loader | Migration complete when old files deleted |

### Open Questions

**Q: Should old config files be deleted or kept during migration?**

Keep old files during transition. Delete after all consumers migrated and tests pass. This is reversible.

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests (RED)
- [ ] Create `tests/test_config.py`
- [ ] Add 5 tests from Tests First section
- [ ] Verify all tests fail (config module doesn't exist yet)

### Step 2: Create Config Directory and Files
- [ ] Create `.claude/haios/config/` directory
- [ ] Create `haios.yaml` with content from Detailed Design
- [ ] Create `cycles.yaml` with content from Detailed Design
- [ ] Create `components.yaml` placeholder

### Step 3: Implement ConfigLoader (GREEN)
- [ ] Create `.claude/lib/config.py` with ConfigLoader class
- [ ] Implement singleton pattern with `get()` and `reset()`
- [ ] Implement `_load()` with graceful degradation
- [ ] Add backward compat properties (toggles, thresholds, node_bindings)
- [ ] Tests 1-5 pass (green)

### Step 4: Update Consumer - pre_tool_use.py
- [ ] Import ConfigLoader
- [ ] Replace `_load_governance_toggles()` with `ConfigLoader.get().toggles`
- [ ] Remove old loading function and cache
- [ ] Verify PowerShell blocking still works

### Step 5: Update Consumer - observations.py
- [ ] Import ConfigLoader
- [ ] Replace `_load_threshold_config()` with `ConfigLoader.get().thresholds`
- [ ] Remove THRESHOLD_CONFIG_PATH constant
- [ ] Verify observation threshold still works

### Step 6: Update Consumer - node_cycle.py
- [ ] Import ConfigLoader
- [ ] Replace `load_node_cycle_bindings()` with `ConfigLoader.get().node_bindings`
- [ ] Remove CONFIG_PATH constant
- [ ] Verify node-cycle bindings still work

### Step 7: Integration Verification
- [ ] All tests pass: `pytest tests/test_config.py -v`
- [ ] Run full test suite: `just test`
- [ ] Manual verification: `/coldstart` loads correctly

### Step 8: README Sync (MUST)
- [ ] **MUST:** Create `.claude/haios/config/README.md`
- [ ] **MUST:** Update `.claude/haios/README.md` to include config directory
- [ ] **MUST:** Update `.claude/lib/README.md` to include config.py

### Step 9: Consumer Verification (MUST)
- [ ] **MUST:** Grep for references to old config paths
- [ ] **MUST:** Verify no stale references to `governance-toggles.yaml`, `routing-thresholds.yaml`, `node-cycle-bindings.yaml`
- [ ] **MUST:** Old config files can be deleted after verification (optional - keep for safety)

**Consumer Discovery Pattern:**
```bash
Grep(pattern="governance-toggles|routing-thresholds|node-cycle-bindings", path=".claude", glob="**/*.py")
```

> **Anti-pattern prevented:** "Ceremonial Completion" - code migrated but consumers still reference old location (see epistemic_state.md)

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Import path issues | Med | Test imports from all consumer locations |
| Config not found at runtime | Med | Graceful degradation returns `{}` |
| Breaking hooks during migration | High | Update consumers incrementally, test after each |
| Stale references left behind | Low | Consumer verification grep before closing |

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
| `.claude/lib/config.py` | ConfigLoader class with get(), reset(), properties | [ ] | |
| `.claude/haios/config/haios.yaml` | toggles + thresholds sections | [ ] | |
| `.claude/haios/config/cycles.yaml` | nodes section with bindings | [ ] | |
| `.claude/haios/config/components.yaml` | Placeholder with skills/agents/hooks | [ ] | |
| `tests/test_config.py` | 5 tests, all passing | [ ] | |
| `.claude/hooks/hooks/pre_tool_use.py` | Uses ConfigLoader.get().toggles | [ ] | |
| `.claude/lib/observations.py` | Uses ConfigLoader.get().thresholds | [ ] | |
| `.claude/lib/node_cycle.py` | Uses ConfigLoader.get().node_bindings | [ ] | |
| `.claude/haios/config/README.md` | Documents 3 config files | [ ] | |
| `Grep: governance-toggles\|routing-thresholds\|node-cycle-bindings` | Zero stale references in .claude/**/*.py | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_config.py -v
# Expected: 5 tests passed
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

- INV-053: HAIOS Modular Architecture Review (source of 3-file consolidation decision)
- INV-052: HAIOS Architecture Reference (original 7-file proposal)
- Memory 80489: "CONFIG CONSOLIDATION: Reduce 7 proposed files to 3 MVP files"
- Session 158 Checkpoint: Architecture review and L5-L7 formalization

---
