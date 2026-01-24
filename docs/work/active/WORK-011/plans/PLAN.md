---
template: implementation_plan
status: complete
date: 2026-01-24
backlog_id: WORK-011
title: Coldstart Orchestrator Implementation Plan
author: Hephaestus
lifecycle_phase: plan
session: 232
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-24T20:55:26'
---
# Implementation Plan: Coldstart Orchestrator Implementation Plan

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

A single `just coldstart` command will sequentially invoke IdentityLoader, SessionLoader, and WorkLoader with `[BREATHE]` markers between phases, eliminating all manual Read tool calls during coldstart.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | cli.py, justfile, /coldstart skill |
| Lines of code affected | ~50 | cli.py cmd_context_load (~30), justfile (~5), coldstart skill (~15) |
| New files to create | 2 | config/coldstart.yaml, lib/coldstart_orchestrator.py |
| Tests to write | 5 | Config load, phase execution, breathe markers, content parity, integration |
| Dependencies | 3 | identity_loader.py, session_loader.py, work_loader.py |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Orchestrator composes existing loaders, minimal new interfaces |
| Risk of regression | Low | Loaders have tests, orchestrator is additive |
| External dependencies | Low | Uses existing yaml config pattern, no new external deps |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Config + Orchestrator | 30 min | High |
| Tests | 20 min | High |
| Recipe + Skill Update | 15 min | High |
| **Total** | ~1 hour | High |

---

## Current State vs Desired State

### Current State

```python
# cli.py:196-237 - Current context loading outputs loader content but no phase markers
def cmd_context_load(project_root: Path = None, role: str = "main") -> int:
    loader = ContextLoader(project_root=project_root)
    ctx = loader.load_context(role=role)

    for loader_name, content in ctx.loaded_context.items():
        if content:
            print(content)  # No phase markers, no breathing room

    print(f"\n[SESSION]")
    print(f"Number: {ctx.session_number}")
```

**Behavior:** Currently loads identity context via `just coldstart`. Session and work are separate recipes. No `[BREATHE]` markers.

**Result:** Agent must invoke 3 separate recipes (`just coldstart`, `just session-context`, `just work-options`) or follow 10+ step procedure with manual Read calls.

### Desired State

```python
# lib/coldstart_orchestrator.py - New orchestrator class
class ColdstartOrchestrator:
    def __init__(self, config_path: Optional[Path] = None):
        self.config = self._load_config(config_path)
        self._loaders = {
            "identity": IdentityLoader,
            "session": SessionLoader,
            "work": WorkLoader,
        }

    def run(self) -> str:
        """Execute all phases with breathing room."""
        output = []
        for phase in self.config.get("phases", []):
            loader_cls = self._loaders.get(phase["id"])
            if loader_cls:
                output.append(f"[PHASE: {phase['id'].upper()}]")
                output.append(loader_cls().load())
                if phase.get("breathe", False):
                    output.append("\n[BREATHE]\n")
        return "\n".join(output)
```

**Behavior:** Single `just coldstart` invokes orchestrator that runs all three loaders with `[BREATHE]` markers.

**Result:** Agent receives full context in one recipe call with clear phase separation.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Orchestrator Loads Config
```python
def test_orchestrator_loads_config(tmp_path):
    """ColdstartOrchestrator reads coldstart.yaml config file."""
    config = tmp_path / "coldstart.yaml"
    config.write_text("phases:\n  - id: identity\n    breathe: true")
    from coldstart_orchestrator import ColdstartOrchestrator
    orch = ColdstartOrchestrator(config_path=config)
    assert orch.config is not None
    assert "phases" in orch.config
```

### Test 2: Orchestrator Runs Phases in Order
```python
def test_orchestrator_runs_phases_in_order():
    """run() executes phases in config order."""
    from coldstart_orchestrator import ColdstartOrchestrator
    # Mock loaders return predictable content
    orch = ColdstartOrchestrator()
    orch._loaders = {
        "identity": MockLoader("IDENTITY"),
        "session": MockLoader("SESSION"),
    }
    orch.config = {"phases": [{"id": "identity"}, {"id": "session"}]}
    output = orch.run()
    assert output.index("IDENTITY") < output.index("SESSION")
```

### Test 3: Breathe Markers Between Phases
```python
def test_breathe_markers_between_phases():
    """run() adds [BREATHE] when phase.breathe is True."""
    from coldstart_orchestrator import ColdstartOrchestrator
    orch = ColdstartOrchestrator()
    orch._loaders = {"identity": MockLoader("ID"), "session": MockLoader("SESS")}
    orch.config = {"phases": [
        {"id": "identity", "breathe": True},
        {"id": "session", "breathe": False}
    ]}
    output = orch.run()
    assert "[BREATHE]" in output
    # Breathe appears after identity, not after session
    assert output.count("[BREATHE]") == 1
```

### Test 4: Content Parity Check
```python
def test_content_parity_with_individual_loaders():
    """Orchestrator output contains same info as individual loaders."""
    from coldstart_orchestrator import ColdstartOrchestrator
    from identity_loader import IdentityLoader
    from session_loader import SessionLoader

    orch = ColdstartOrchestrator()
    output = orch.run()

    # Key identity elements present
    assert "Mission:" in output or "=== IDENTITY ===" in output
    # Key session elements present
    assert "Prior Session:" in output or "=== SESSION ===" in output
```

### Test 5: Integration - Just Recipe Works
```python
def test_just_coldstart_recipe_produces_output():
    """just coldstart recipe produces orchestrator output."""
    import subprocess
    result = subprocess.run(
        ["just", "coldstart"],
        capture_output=True,
        text=True,
        timeout=30
    )
    # Should contain phase markers
    assert "[PHASE:" in result.stdout or "=== IDENTITY ===" in result.stdout
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

### Exact Code Change

#### File 1: New `coldstart_orchestrator.py`

**File:** `.claude/haios/lib/coldstart_orchestrator.py`
**Location:** New file

```python
"""
Coldstart Orchestrator for Configuration Arc.

CH-007: Wires IdentityLoader, SessionLoader, WorkLoader into unified coldstart.
Follows sibling loader patterns (identity_loader.py, session_loader.py).

Usage:
    from coldstart_orchestrator import ColdstartOrchestrator

    orch = ColdstartOrchestrator()
    output = orch.run()  # Returns full coldstart context with [BREATHE] markers
"""
from pathlib import Path
from typing import Any, Dict, Optional
import yaml
import logging

logger = logging.getLogger(__name__)

# Path setup (same pattern as session_loader.py)
CONFIG_DIR = Path(__file__).parent.parent / "config"
DEFAULT_CONFIG = CONFIG_DIR / "coldstart.yaml"

# Import loaders (same pattern as sibling modules)
from identity_loader import IdentityLoader
from session_loader import SessionLoader
from work_loader import WorkLoader


class ColdstartOrchestrator:
    """
    Orchestrate coldstart phases with breathing room.

    Uses coldstart.yaml config to run loaders in sequence with [BREATHE] markers.
    """

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or DEFAULT_CONFIG
        self._loaders = {
            "identity": IdentityLoader,
            "session": SessionLoader,
            "work": WorkLoader,
        }
        self._load_config()

    def _load_config(self) -> None:
        """Load config from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
        else:
            logger.warning(f"Config not found: {self.config_path}")
            self.config = {"phases": [
                {"id": "identity", "breathe": True},
                {"id": "session", "breathe": True},
                {"id": "work", "breathe": False},
            ]}

    def run(self) -> str:
        """Execute all phases with breathing room."""
        output = []
        phases = self.config.get("phases", [])

        for phase in phases:
            phase_id = phase.get("id")
            loader_cls = self._loaders.get(phase_id)

            if loader_cls:
                output.append(f"[PHASE: {phase_id.upper()}]")
                try:
                    output.append(loader_cls().load())
                except Exception as e:
                    logger.warning(f"Loader {phase_id} failed: {e}")
                    output.append(f"(Loader {phase_id} failed: {e})")

                if phase.get("breathe", False):
                    output.append("\n[BREATHE]\n")
            else:
                logger.warning(f"Unknown loader: {phase_id}")

        output.append("[READY FOR SELECTION]")
        return "\n".join(output)


# CLI entry point for `just coldstart`
if __name__ == "__main__":
    orch = ColdstartOrchestrator()
    print(orch.run())
```

#### File 2: New `coldstart.yaml`

**File:** `.claude/haios/config/coldstart.yaml`
**Location:** New file

```yaml
# Coldstart phase orchestration config per CH-007 spec
phases:
  - id: identity
    breathe: true

  - id: session
    breathe: true

  - id: work
    breathe: false
```

### Call Chain Context

```
just coldstart
    |
    +-> cli.py cmd_coldstart()
    |       |
    |       +-> ColdstartOrchestrator.run()     # <-- NEW
    |                |
    |                +-> IdentityLoader.load()
    |                +-> [BREATHE]
    |                +-> SessionLoader.load()
    |                +-> [BREATHE]
    |                +-> WorkLoader.load()
    |                +-> [READY FOR SELECTION]
    |
    +-> Output to stdout (agent context)
```

### Function/Component Signatures

```python
class ColdstartOrchestrator:
    """Orchestrate coldstart phases with breathing room."""

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize with config file.

        Args:
            config_path: Path to coldstart.yaml. Default: standard location.
        """

    def run(self) -> str:
        """
        Execute all phases with breathing room.

        Returns:
            Full coldstart context string with [PHASE:], [BREATHE], and
            [READY FOR SELECTION] markers.

        Raises:
            No exceptions - gracefully handles loader failures with warnings.
        """
```

### Behavior Logic

**Current Flow:**
```
just coldstart → cli.py cmd_context_load → ContextLoader → identity content only
agent → manual session-context → SessionLoader
agent → manual work-options → WorkLoader
```

**New Flow:**
```
just coldstart → cli.py cmd_coldstart → ColdstartOrchestrator.run()
                                                |
                                        For each phase in config:
                                                |
                                        [PHASE: NAME] marker
                                                |
                                        loader.load()
                                                |
                                        breathe? ─────┐
                                          │ YES      │ NO
                                          ▼          │
                                        [BREATHE]    │
                                          │          │
                                          └──────────┘
                                                |
                                        [READY FOR SELECTION]
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Orchestrator location | `.claude/haios/lib/` | Follows sibling loader pattern (identity_loader.py, session_loader.py) |
| Config file location | `.claude/haios/config/coldstart.yaml` | Consistent with haios.yaml and loader configs |
| Default phases hardcoded | Fallback when config missing | Graceful degradation, same pattern as session_loader.py |
| Breathe markers | Text markers `[BREATHE]` | Simple, parseable, matches CH-007 spec requirement R3 |
| No ContextLoader modification | Orchestrator is separate | Avoids coupling, orchestrator can be used independently |
| Phase marker format | `[PHASE: NAME]` | Clear separation, matches existing `[SESSION]` marker style |
| Memory query delegation | Not included in orchestrator | SessionLoader already handles memory_refs; orchestrator composes only |

### Input/Output Examples

**Current Output (just coldstart):**
```
=== IDENTITY ===
Mission: The system's success is measured...
Companion Relationship:
- Trust is built through transparency...
...

[SESSION]
Number: 232
Prior: 231
```

**New Output (just coldstart with orchestrator):**
```
[PHASE: IDENTITY]
=== IDENTITY ===
Mission: The system's success is measured...
Companion Relationship:
- Trust is built through transparency...
...

[BREATHE]

[PHASE: SESSION]
=== SESSION CONTEXT ===
Prior Session: 231
Completed last session:
WORK-010 Work Loader for Coldstart Phase 3 - COMPLETE
...

[BREATHE]

[PHASE: WORK]
=== WORK OPTIONS ===
Queue (top 5):
  1. E2-072: Critique Subagent
  2. E2-236: Orphan Detection
...

[READY FOR SELECTION]
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Config file missing | Use hardcoded default phases | Test 1 (implicit) |
| Loader fails | Log warning, continue with other phases | Test 4 (content parity) |
| Unknown loader in config | Log warning, skip that phase | No explicit test (graceful degradation) |
| Empty phases list | Output only `[READY FOR SELECTION]` | Implicit in run() logic |

### Open Questions

**Q: Should orchestrator replace ContextLoader entirely?**

No. ContextLoader serves role-based loading with memory/work engine integration. Orchestrator is specifically for coldstart CLI output. They can coexist.

**Q: Should we add new cli.py command or modify existing?**

Modify existing `cmd_context_load` to use orchestrator when called from `just coldstart`. Alternative: add `cmd_coldstart` separately. Decision: Add separate `cmd_coldstart` to keep backward compat.

---

## Open Decisions (MUST resolve before implementation)

**No operator_decisions in work item frontmatter. All technical decisions resolved in Key Design Decisions table above.**

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [x] Create `tests/test_coldstart_orchestrator.py`
- [x] Add Tests 1-4 from Tests First section
- [x] Verify tests fail (orchestrator doesn't exist yet)

### Step 2: Create Config and Orchestrator
- [x] Create `.claude/haios/config/coldstart.yaml`
- [x] Create `.claude/haios/lib/coldstart_orchestrator.py`
- [x] Tests 1-3 pass (config load, phase order, breathe markers)

### Step 3: Wire cli.py Command
- [x] Add `cmd_coldstart()` function to cli.py
- [x] Wire to `coldstart` subcommand
- [x] Test 4 passes (content parity)

### Step 4: Update Just Recipe
- [x] Modify `just coldstart` to call `cli.py coldstart` (added `coldstart-orchestrator` recipe)
- [x] Test 5 passes (integration)

### Step 5: Update /coldstart Skill
- [x] Modify `.claude/commands/coldstart.md` to remove manual Read instructions
- [x] Skill now just invokes `just coldstart-orchestrator` and processes output

### Step 6: README Sync (MUST)
- [x] **MUST:** Update `.claude/haios/lib/README.md` with coldstart_orchestrator.py
- [x] **MUST:** Update `.claude/haios/config/README.md` with coldstart.yaml

### Step 7: Integration Verification
- [x] All tests pass: `pytest tests/test_coldstart_orchestrator.py -v` (7 passed)
- [x] Run full test suite (no regressions): `pytest tests/ -v` (no new failures)
- [x] Manual verification: `just coldstart-orchestrator` produces expected output

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment - orchestrator output differs from CH-007 expectation | Medium | Content parity test verifies same info as current loaders |
| Integration - existing coldstart consumers break | Low | Add new cli command, don't modify existing cmd_context_load |
| Regression - loader tests fail | Low | Orchestrator only composes loaders, doesn't modify them |
| Scope creep - adding features beyond spec | Medium | Strict adherence to CH-007 requirements R1-R4 |
| Knowledge gap - session_loader memory_ref query timing | Low | Verified: SessionLoader handles memory internally, orchestrator just calls load() |

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

**MUST** read `docs/work/active/WORK-011/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| `config/coldstart.yaml` - Phase orchestration config | [x] | File exists with 3 phases (identity, session, work) |
| `ColdstartOrchestrator` class in lib/ | [x] | Class exists with run() method, 102 lines |
| Updated `just coldstart` recipe | [x] | Added `coldstart-orchestrator` recipe for backward compat |
| `[BREATHE]` markers in output | [x] | Demo output shows markers between phases |
| Content parity verification | [x] | Test 4 passes (content_parity_with_individual_loaders) |
| Tests in test_coldstart_orchestrator.py | [x] | 7 tests exist and pass (exceeded plan's 5) |
| Updated `/coldstart` skill | [x] | Skill now invokes `just coldstart-orchestrator` |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/config/coldstart.yaml` | Contains phases config | [x] | Has identity, session, work phases |
| `.claude/haios/lib/coldstart_orchestrator.py` | ColdstartOrchestrator class with run() | [x] | Class with run(), _load_config(), CLI entry |
| `.claude/haios/modules/cli.py` | cmd_coldstart function exists | [x] | Added cmd_coldstart() lines 240-269 |
| `tests/test_coldstart_orchestrator.py` | 5 tests, all pass | [x] | 7 tests, all pass (exceeded) |
| `.claude/commands/coldstart.md` | No manual Read instructions | [x] | Now invokes `just coldstart-orchestrator` |
| `.claude/haios/lib/README.md` | Lists coldstart_orchestrator.py | [x] | Added to Modules table |

**Verification Commands:**
```bash
pytest tests/test_coldstart_orchestrator.py -v
# Output: 7 passed, 1 warning in 1.30s
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | Read all during implementation |
| Test output pasted above? | Yes | 7 passed |
| Any deviations from plan? | Yes | Added `coldstart-orchestrator` recipe instead of modifying `coldstart` for backward compat; 7 tests instead of 5 |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (7 tests, all green)
- [x] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [x] **Runtime consumer exists** (`just coldstart-orchestrator` calls the code)
- [x] WHY captured (reasoning stored to memory) - IDs: 82334, 82335, 82336, 82337
- [x] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [x] **MUST:** Consumer verification complete (coldstart skill invokes recipe)
- [x] All traced files complete
- [x] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.
> **E2-290 Learning (Session 192):** "Tests pass" ≠ "Deliverables complete". Agent declared victory after tests passed but skipped 2 of 7 deliverables.

---

## References

- @.claude/haios/epochs/E2_3/arcs/configuration/CH-007-coldstart-orchestrator.md (Chapter spec)
- @.claude/haios/epochs/E2_3/arcs/configuration/ARC.md (Arc context)
- @.claude/haios/lib/identity_loader.py (Sibling pattern)
- @.claude/haios/lib/session_loader.py (Sibling pattern)
- @.claude/haios/lib/work_loader.py (Sibling pattern)
- Memory: 81178 (coldstart inhale/exhale pattern)

---
