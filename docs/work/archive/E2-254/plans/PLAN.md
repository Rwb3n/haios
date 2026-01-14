---
template: implementation_plan
status: complete
date: 2026-01-04
backlog_id: E2-254
title: ContextLoader Module Implementation
author: Hephaestus
lifecycle_phase: plan
session: 165
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-04T14:00:56'
---
# Implementation Plan: ContextLoader Module Implementation

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

ContextLoader module will provide programmatic bootstrap with `load_context()` returning a typed GroundedContext dataclass, `compute_session_number()` for session tracking, and CLI integration via `just coldstart` recipe.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 4 | context_loader.py, cli.py, justfile, test_context_loader.py |
| Lines of code affected | ~150 | New module + CLI command |
| New files to create | 2 | context_loader.py, test_context_loader.py |
| Tests to write | 6 | load_context, compute_session, grounded_context fields |
| Dependencies | 3 | WorkEngine, MemoryBridge, status.py |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | Calls WorkEngine.get_ready(), MemoryBridge.query() |
| Risk of regression | Low | New module, no existing code to break |
| External dependencies | Low | Reads L0-L4 files, status JSON |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Phase 1: Core module | 30 min | High |
| Phase 2: CLI + justfile | 15 min | High |
| Phase 3: Tests | 20 min | High |
| **Total** | ~65 min | High |

---

## Current State vs Desired State

### Current State

```markdown
# .claude/commands/coldstart.md - Markdown command
# Claude interprets instructions, manually reads files, constructs response
# Session number: computed ad-hoc from haios-status.json last_session field
# No programmatic interface, no typed return values
```

**Behavior:** coldstart.md is a prompt that Claude follows to read files and summarize

**Result:** Works but no programmatic API, session number scattered in status.py logic

### Desired State

```python
# .claude/haios/modules/context_loader.py
@dataclass
class GroundedContext:
    session_number: int
    prior_session: Optional[int]
    l0_telos: str          # Mission from L0
    l1_principal: str      # Operator constraints from L1
    l2_intent: str         # Goals from L2
    l3_requirements: str   # Principles from L3
    l4_implementation: str # Current architecture from L4
    checkpoint_summary: str
    strategies: List[Dict]  # From MemoryBridge query
    ready_work: List[str]   # From WorkEngine.get_ready()

class ContextLoader:
    def load_context(self, trigger: str = "coldstart") -> GroundedContext:
        """Load L0-L4 context and session state."""
        ...

    def compute_session_number(self) -> Tuple[int, Optional[int]]:
        """Return (current_session, prior_session) from status JSON."""
        ...
```

**Behavior:** Programmatic bootstrap with typed return values

**Result:** CLI command `just coldstart` can invoke ContextLoader and format output

---

## Tests First (TDD)

### Test 1: compute_session_number returns tuple
```python
def test_compute_session_number_returns_tuple():
    """compute_session_number returns (current, prior) from status."""
    loader = ContextLoader()
    current, prior = loader.compute_session_number()
    assert isinstance(current, int)
    assert current > 0
    assert prior is None or isinstance(prior, int)
```

### Test 2: load_context returns GroundedContext
```python
def test_load_context_returns_grounded_context(mocker):
    """load_context returns GroundedContext with all L0-L4 fields."""
    loader = ContextLoader()
    # Mock file reads and dependencies
    mocker.patch.object(loader, "_read_manifesto_file", return_value="content")
    mocker.patch.object(loader, "_get_ready_work", return_value=["E2-254"])
    mocker.patch.object(loader, "_get_strategies", return_value=[])

    ctx = loader.load_context()

    assert isinstance(ctx, GroundedContext)
    assert ctx.session_number > 0
    assert ctx.l0_telos != ""
```

### Test 3: grounded_context has all required fields
```python
def test_grounded_context_has_required_fields():
    """GroundedContext dataclass has all L0-L4 fields."""
    from context_loader import GroundedContext
    import dataclasses

    fields = {f.name for f in dataclasses.fields(GroundedContext)}
    required = {"session_number", "l0_telos", "l1_principal", "l2_intent",
                "l3_requirements", "l4_implementation", "strategies", "ready_work"}
    assert required <= fields
```

### Test 4: load_context integrates with WorkEngine
```python
def test_load_context_calls_work_engine(mocker):
    """load_context gets ready work from WorkEngine."""
    from work_engine import WorkEngine

    mock_engine = mocker.Mock(spec=WorkEngine)
    mock_engine.get_ready.return_value = []

    loader = ContextLoader(work_engine=mock_engine)
    loader.load_context()

    mock_engine.get_ready.assert_called_once()
```

### Test 5: load_context integrates with MemoryBridge
```python
def test_load_context_calls_memory_bridge(mocker):
    """load_context gets strategies from MemoryBridge."""
    from memory_bridge import MemoryBridge

    mock_bridge = mocker.Mock(spec=MemoryBridge)
    mock_bridge.query.return_value = QueryResult(concepts=[], reasoning={})

    loader = ContextLoader(memory_bridge=mock_bridge)
    loader.load_context()

    mock_bridge.query.assert_called()
```

### Test 6: CLI command exists and runs
```python
def test_cli_coldstart_runs(mocker):
    """CLI coldstart command invokes ContextLoader."""
    import cli
    mocker.patch("cli.ContextLoader")

    result = cli.cmd_coldstart()
    assert result == 0
```

---

## Detailed Design

### New File: context_loader.py

**File:** `.claude/haios/modules/context_loader.py`

```python
"""
ContextLoader Module (E2-254)

Programmatic bootstrap for HAIOS sessions. Provides:
- L0-L4 context loading with typed return
- Session number computation
- Integration with WorkEngine and MemoryBridge

Per INV-052 S17.3:
- INPUT: trigger ("coldstart" | "session_recovery")
- OUTPUT: GroundedContext dataclass
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
import json
import logging

logger = logging.getLogger(__name__)


@dataclass
class GroundedContext:
    """Result of context loading - L0-L4 grounding."""

    session_number: int
    prior_session: Optional[int] = None
    l0_telos: str = ""         # WHY - Mission, Prime Directive
    l1_principal: str = ""     # WHO - Operator constraints
    l2_intent: str = ""        # WHAT - Goals, trade-offs
    l3_requirements: str = ""  # HOW - Principles, boundaries
    l4_implementation: str = "" # WHAT to build - Architecture
    checkpoint_summary: str = ""
    strategies: List[Dict[str, Any]] = field(default_factory=list)
    ready_work: List[str] = field(default_factory=list)


class ContextLoader:
    """
    Bootstrap the agent with L0-L4 context grounding.

    Per INV-052 S17.3, ContextLoader:
    - Loads manifesto files (L0-L4)
    - Computes session number from status
    - Queries MemoryBridge for strategies
    - Gets ready work from WorkEngine
    """

    MANIFESTO_PATH = Path(".claude/haios/manifesto")
    STATUS_PATH = Path(".claude/haios-status.json")

    def __init__(
        self,
        work_engine=None,
        memory_bridge=None,
        project_root: Optional[Path] = None,
    ):
        """
        Initialize ContextLoader with optional dependencies.

        Args:
            work_engine: WorkEngine instance for ready work
            memory_bridge: MemoryBridge instance for strategy query
            project_root: Project root path (default: auto-detect)
        """
        self._work_engine = work_engine
        self._memory_bridge = memory_bridge
        self._project_root = project_root or Path(__file__).parent.parent.parent.parent

    def compute_session_number(self) -> Tuple[int, Optional[int]]:
        """
        Compute current and prior session from status JSON.

        Returns:
            (current_session, prior_session) where prior may be None
        """
        status_path = self._project_root / self.STATUS_PATH
        try:
            with open(status_path, "r", encoding="utf-8") as f:
                status = json.load(f)
            last_session = status.get("last_session", 0)
            return (last_session + 1, last_session if last_session > 0 else None)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not read status: {e}")
            return (1, None)

    def load_context(self, trigger: str = "coldstart") -> GroundedContext:
        """
        Load L0-L4 context and session state.

        Args:
            trigger: "coldstart" for full bootstrap, "session_recovery" for minimal

        Returns:
            GroundedContext with all grounding fields populated
        """
        session, prior = self.compute_session_number()

        ctx = GroundedContext(
            session_number=session,
            prior_session=prior,
            l0_telos=self._read_manifesto_file("L0-telos.md"),
            l1_principal=self._read_manifesto_file("L1-principal.md"),
            l2_intent=self._read_manifesto_file("L2-intent.md"),
            l3_requirements=self._read_manifesto_file("L3-requirements.md"),
            l4_implementation=self._read_manifesto_file("L4-implementation.md"),
            checkpoint_summary=self._get_latest_checkpoint(),
            strategies=self._get_strategies(trigger),
            ready_work=self._get_ready_work(),
        )
        return ctx

    def _read_manifesto_file(self, filename: str) -> str:
        """Read a manifesto file, return empty string on error."""
        path = self._project_root / self.MANIFESTO_PATH / filename
        try:
            return path.read_text(encoding="utf-8")
        except FileNotFoundError:
            logger.warning(f"Manifesto file not found: {filename}")
            return ""

    def _get_latest_checkpoint(self) -> str:
        """Get summary from latest checkpoint file."""
        checkpoint_dir = self._project_root / "docs" / "checkpoints"
        try:
            checkpoints = sorted(checkpoint_dir.glob("*.md"), reverse=True)
            if checkpoints:
                return checkpoints[0].read_text(encoding="utf-8")[:2000]
        except Exception as e:
            logger.warning(f"Could not read checkpoint: {e}")
        return ""

    def _get_strategies(self, trigger: str) -> List[Dict[str, Any]]:
        """Query MemoryBridge for session strategies."""
        if not self._memory_bridge:
            return []
        try:
            mode = "session_recovery" if trigger == "coldstart" else "semantic"
            result = self._memory_bridge.query("session strategies learnings", mode=mode)
            return result.concepts[:5] if result.concepts else []
        except Exception as e:
            logger.warning(f"Strategy query failed: {e}")
            return []

    def _get_ready_work(self) -> List[str]:
        """Get ready work items from WorkEngine."""
        if not self._work_engine:
            return []
        try:
            ready = self._work_engine.get_ready()
            return [w.id for w in ready[:10]]
        except Exception as e:
            logger.warning(f"Ready work query failed: {e}")
            return []
```

### Call Chain Context

```
just coldstart (justfile recipe)
    |
    +-> cli.py cmd_coldstart()
    |       Creates: ContextLoader
    |
    +-> ContextLoader.load_context()
    |       Returns: GroundedContext
    |       Calls:
    |       ├── compute_session_number()
    |       ├── _read_manifesto_file() x5 (L0-L4)
    |       ├── _get_latest_checkpoint()
    |       ├── MemoryBridge.query() (if available)
    |       └── WorkEngine.get_ready() (if available)
    |
    +-> Format and print summary
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Dataclass for return | GroundedContext | Typed interface per INV-052 S17.3 spec |
| Optional dependencies | Constructor injection | Allows mocking in tests, graceful degradation |
| Read full manifesto files | Yes | Token budget managed by caller, not loader |
| Checkpoint truncation | 2000 chars | Prevent context overflow, summary sufficient |
| Strategy limit | 5 | Reasonable for session recovery context |

### Input/Output Examples

**Current system state:**
```json
// .claude/haios-status.json
{"last_session": 165, ...}
```

**After load_context():**
```python
ctx = loader.load_context()
ctx.session_number  # 166
ctx.prior_session   # 165
ctx.l0_telos        # "# L0: Telos (North Star)..."
ctx.ready_work      # ["E2-254", "E2-255", ...]
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Status file missing | Return session 1, prior None | Test 1 |
| Manifesto file missing | Return empty string | Test 2 |
| WorkEngine not injected | Return empty ready_work | Test 4 |
| MemoryBridge not injected | Return empty strategies | Test 5 |

### Open Questions

**Q: Should ContextLoader also log SessionStarted event?**

Per INV-052 S17.3, SessionStarted event should be emitted. However, event emission is GovernanceLayer's responsibility. ContextLoader returns data, governance logs events. This maintains separation of concerns.

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_context_loader.py`
- [ ] Add tests 1-6 from Tests First section
- [ ] Verify all tests fail (red) - module doesn't exist yet

### Step 2: Create ContextLoader Module
- [ ] Create `.claude/haios/modules/context_loader.py`
- [ ] Implement GroundedContext dataclass
- [ ] Implement ContextLoader class with compute_session_number()
- [ ] Tests 1, 3 pass (green)

### Step 3: Implement load_context
- [ ] Implement load_context() method
- [ ] Implement _read_manifesto_file()
- [ ] Implement _get_latest_checkpoint()
- [ ] Implement _get_strategies() and _get_ready_work()
- [ ] Tests 2, 4, 5 pass (green)

### Step 4: Add CLI Integration
- [ ] Add cmd_coldstart() to cli.py
- [ ] Add CLI dispatch for "context-load" command
- [ ] Add `context-load` recipe to justfile
- [ ] Test 6 passes (green)

### Step 4b: Update /coldstart Command
- [ ] Update `.claude/commands/coldstart.md` to invoke `just context-load`
- [ ] ContextLoader output replaces manual file reads
- [ ] Markdown still provides summary formatting, but data comes from module

### Step 5: Integration Verification
- [ ] All tests pass
- [ ] Run full test suite (no regressions)

### Step 6: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/modules/README.md` with ContextLoader
- [ ] **MUST:** Verify README content matches actual file state

### Step 7: Consumer Verification
- [ ] Grep for "ContextLoader" to verify imports work
- [ ] Verify justfile recipe runs

> **Anti-pattern prevented:** "Ceremonial Completion" - code created but no runtime consumers

---

## Verification

- [ ] Tests pass: `pytest tests/test_context_loader.py -v`
- [ ] **MUST:** All READMEs current (`.claude/haios/modules/README.md`)
- [ ] Runtime consumer works: `just context-load`
- [ ] Full suite passes: `pytest tests/ -v`

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Status JSON format changes | Low | Parse defensively with .get() |
| Manifesto path changes | Low | Use class constant, easy to update |
| Large manifesto files | Medium | Truncation handled by caller, not loader |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/context_loader.py` | ContextLoader class with load_context() | [ ] | |
| `tests/test_context_loader.py` | 6 tests exist and pass | [ ] | |
| `.claude/haios/modules/README.md` | Documents ContextLoader | [ ] | |
| `.claude/haios/modules/cli.py` | cmd_coldstart() exists | [ ] | |
| `justfile` | context-load recipe exists | [ ] | |
| `.claude/commands/coldstart.md` | Invokes `just context-load` | [x] | Step 0 added |

**Verification Commands:**
```bash
pytest tests/test_context_loader.py -v
# Expected: 6 tests passed

just context-load
# Expected: Returns GroundedContext summary (no error)
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
- [ ] **Runtime consumer exists** (justfile recipe calls cli.py)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories
- [ ] **MUST:** Consumer verification complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.

---

## References

- INV-052 Section 17.3: ContextLoader Module specification
- `.claude/commands/coldstart.md`: Current markdown implementation
- `.claude/haios/manifesto/L0-L4.md`: Context files to load

---
