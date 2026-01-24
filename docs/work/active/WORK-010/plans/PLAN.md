---
template: implementation_plan
status: complete
date: 2026-01-24
backlog_id: WORK-010
title: Work Loader for Coldstart Phase 3
author: Hephaestus
lifecycle_phase: plan
session: 231
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-24T19:53:28'
---
# Implementation Plan: Work Loader for Coldstart Phase 3

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

A single `just work-options` command will output formatted work options with queue items, pending checkpoint work, and epoch alignment warnings for token-efficient coldstart Phase 3 context injection.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `context_loader.py` (add registration), `justfile` (add recipe) |
| Lines of code affected | ~10 | Registration in context_loader.py:109-117 |
| New files to create | 2 | `work_loader.py`, `work.yaml`, `test_work_loader.py` |
| Tests to write | 5 | Config, extract queue, extract pending, epoch warning, load |
| Dependencies | 1 | ContextLoader (registers WorkLoader) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Same pattern as IdentityLoader/SessionLoader |
| Risk of regression | Low | New code, existing loaders have tests |
| External dependencies | Low | Only depends on existing `just queue` |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests + Config | 20 min | High |
| WorkLoader class | 30 min | High |
| Integration | 10 min | High |
| **Total** | 60 min | High |

---

## Current State vs Desired State

### Current State

```python
# survey-cycle/SKILL.md - Work extraction inline in skill prose
# Agent must:
# 1. Run `just queue` bash command
# 2. Parse output manually
# 3. Check checkpoint pending field
# 4. Format and present options
```

**Behavior:** Survey-cycle skill performs work extraction inline, requiring multiple tool calls.

**Result:** Token-inefficient, no epoch alignment check, error-prone parsing.

### Desired State

```python
# .claude/haios/lib/work_loader.py
class WorkLoader:
    def load(self) -> str:
        """Single call returns formatted work options."""
        return self.format(self.extract())
```

**Behavior:** WorkLoader extracts queue, pending, and epoch alignment in one call.

**Result:** Token-efficient, single `just work-options` invocation for coldstart Phase 3.

---

## Tests First (TDD)

### Test 1: Config Loading
```python
def test_work_loader_loads_config():
    """WorkLoader reads work.yaml config file."""
    from work_loader import WorkLoader
    loader = WorkLoader()
    assert loader.config is not None
    assert "sources" in loader.config or "output" in loader.config
```

### Test 2: Queue Extraction
```python
def test_extract_parses_queue_output(tmp_path):
    """extract() parses queue command output."""
    from work_loader import WorkLoader
    # Mock queue_fn returns list of work items
    mock_queue = lambda: [
        {"id": "E2-072", "title": "Critique Subagent", "priority": "medium"},
        {"id": "E2-236", "title": "Orphan Detection", "priority": "medium"},
    ]
    loader = WorkLoader(queue_fn=mock_queue)
    extracted = loader.extract()
    assert len(extracted["queue"]) == 2
    assert extracted["queue"][0]["id"] == "E2-072"
```

### Test 3: Pending Extraction
```python
def test_extract_gets_pending_from_checkpoint(tmp_path):
    """extract() gets pending items from checkpoint."""
    from work_loader import WorkLoader
    cp_dir = tmp_path / "docs" / "checkpoints"
    cp_dir.mkdir(parents=True)
    (cp_dir / "2026-01-24-checkpoint.md").write_text("""---
session: 230
pending:
  - CH-006 Work Loader
  - INV-068 Cycle Delegation
---""")
    loader = WorkLoader(checkpoint_dir=cp_dir)
    extracted = loader.extract()
    assert "CH-006" in str(extracted["pending"])
```

### Test 4: Epoch Alignment Warning
```python
def test_format_warns_on_epoch_mismatch():
    """format() warns when queue items are from prior epochs."""
    from work_loader import WorkLoader
    loader = WorkLoader()
    extracted = {
        "queue": [{"id": "E2-072", "title": "Old epoch item"}],
        "pending": [],
        "current_epoch": "E2.3",
        "legacy_count": 1,
    }
    formatted = loader.format(extracted)
    assert "WARNING" in formatted or "prior epoch" in formatted.lower()
```

### Test 5: Load Returns Formatted String
```python
def test_load_returns_formatted_string(tmp_path):
    """load() returns formatted string for context injection."""
    from work_loader import WorkLoader
    mock_queue = lambda: [{"id": "WORK-010", "title": "Test", "priority": "medium"}]
    loader = WorkLoader(queue_fn=mock_queue)
    result = loader.load()
    assert isinstance(result, str)
    assert "WORK" in result.upper()
```

---

## Detailed Design

### Pattern Verification (E2-255)

**Sibling Pattern Source:** `session_loader.py`

Verified patterns to follow:
- Path constants: `CONFIG_DIR`, `DEFAULT_CONFIG`, `PROJECT_ROOT`
- Import pattern: Direct import `from loader import Loader` (no try/except needed)
- Dependency injection: `queue_fn: Optional[Callable]` for testability
- Config loading: `_load_config()` with graceful degradation

### File 1: Config File

**File:** `.claude/haios/config/loaders/work.yaml`

```yaml
# Work extraction config per CH-006 spec
# Extracts queue, pending, and epoch alignment for coldstart Phase 3

# Queue extraction
queue:
  limit: 5

# Checkpoint for pending items
checkpoint_dir: "docs/checkpoints/"

# Epoch alignment check
epoch:
  current_field: "current"
  config_path: ".claude/haios/config/haios.yaml"

# Output formatting
output:
  template: |
    === WORK OPTIONS ===

    {epoch_warning}

    Queue (top {queue_limit}):
    {queue}

    Pending from checkpoint:
    {pending}
  list_separator: "\n  "
```

### File 2: WorkLoader Class

**File:** `.claude/haios/lib/work_loader.py`

```python
# generated: 2026-01-24
"""
Work Loader for Configuration Arc.

CH-006: Implements work context loading for coldstart Phase 3.
Follows SessionLoader pattern (CH-005).

Extracts queue items, pending work, and epoch alignment warnings
for token-efficient work selection context injection.
"""
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import subprocess
import re
import yaml
import logging

logger = logging.getLogger(__name__)

CONFIG_DIR = Path(__file__).parent.parent / "config" / "loaders"
DEFAULT_CONFIG = CONFIG_DIR / "work.yaml"
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


class WorkLoader:
    """Extract work context for coldstart Phase 3."""

    def __init__(
        self,
        config_path: Optional[Path] = None,
        checkpoint_dir: Optional[Path] = None,
        queue_fn: Optional[Callable[[], List[Dict]]] = None,
    ):
        self.config_path = config_path or DEFAULT_CONFIG
        self._checkpoint_dir = checkpoint_dir
        self._queue_fn = queue_fn or self._default_queue_fn
        self._load_config()

    def _load_config(self) -> None:
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
        else:
            logger.warning(f"Config not found: {self.config_path}")
            self.config = {}

    @property
    def checkpoint_dir(self) -> Path:
        if self._checkpoint_dir:
            return self._checkpoint_dir
        return PROJECT_ROOT / self.config.get("checkpoint_dir", "docs/checkpoints/")

    def _default_queue_fn(self) -> List[Dict]:
        """Run `just queue` and parse output."""
        try:
            result = subprocess.run(
                ["just", "queue"],
                capture_output=True, text=True, cwd=PROJECT_ROOT
            )
            return self._parse_queue_output(result.stdout)
        except Exception as e:
            logger.warning(f"Queue command failed: {e}")
            return []

    def _parse_queue_output(self, output: str) -> List[Dict]:
        """Parse queue output into list of dicts."""
        items = []
        for line in output.strip().split("\n"):
            match = re.match(r"\s*\d+\.\s+(\S+):\s+(.+?)\s+\(priority=(\w+)\)", line)
            if match:
                items.append({
                    "id": match.group(1),
                    "title": match.group(2),
                    "priority": match.group(3),
                })
        return items

    def _get_pending_from_checkpoint(self) -> List[str]:
        """Get pending items from latest checkpoint."""
        if not self.checkpoint_dir.exists():
            return []
        checkpoints = sorted(self.checkpoint_dir.glob("*.md"), reverse=True)
        checkpoints = [cp for cp in checkpoints if cp.name != "README.md"]
        if not checkpoints:
            return []
        content = checkpoints[0].read_text(encoding="utf-8")
        # Parse frontmatter
        match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if match:
            try:
                fm = yaml.safe_load(match.group(1)) or {}
                return fm.get("pending", [])
            except yaml.YAMLError:
                return []
        return []

    def _check_epoch_alignment(self, queue: List[Dict]) -> tuple:
        """Check if queue items match current epoch."""
        # Get current epoch from config
        haios_config_path = PROJECT_ROOT / ".claude/haios/config/haios.yaml"
        try:
            with open(haios_config_path, "r") as f:
                haios = yaml.safe_load(f) or {}
            current_epoch = haios.get("epoch", {}).get("current", "E2.3")
        except Exception:
            current_epoch = "E2.3"

        # Count legacy items (E2-xxx when epoch is E2.3)
        legacy_count = sum(1 for item in queue if item["id"].startswith("E2-"))
        return current_epoch, legacy_count

    def extract(self) -> Dict[str, Any]:
        """Extract work context."""
        queue = self._queue_fn()
        limit = self.config.get("queue", {}).get("limit", 5)
        queue = queue[:limit]

        pending = self._get_pending_from_checkpoint()
        current_epoch, legacy_count = self._check_epoch_alignment(queue)

        return {
            "queue": queue,
            "pending": pending,
            "current_epoch": current_epoch,
            "legacy_count": legacy_count,
            "queue_limit": limit,
        }

    def format(self, extracted: Dict[str, Any]) -> str:
        """Format extracted data for injection."""
        output_config = self.config.get("output", {})
        template = output_config.get("template", "")
        sep = output_config.get("list_separator", "\n  ")

        # Build epoch warning
        epoch_warning = ""
        if extracted["legacy_count"] > 0:
            epoch_warning = f"WARNING: Queue contains {extracted['legacy_count']} items from prior epochs.\nCurrent epoch: {extracted['current_epoch']}"

        # Format queue items
        queue_lines = [f"{i+1}. {item['id']}: {item['title']}"
                       for i, item in enumerate(extracted["queue"])]
        queue_str = sep.join(queue_lines) if queue_lines else "(empty)"

        # Format pending
        pending = extracted["pending"]
        pending_str = sep.join(pending) if pending else "(none)"

        if not template:
            template = """=== WORK OPTIONS ===

{epoch_warning}

Queue (top {queue_limit}):
{queue}

Pending from checkpoint:
{pending}"""

        return template.format(
            epoch_warning=epoch_warning,
            queue=queue_str,
            pending=pending_str,
            queue_limit=extracted["queue_limit"],
        )

    def load(self) -> str:
        """Extract and format in one call."""
        return self.format(self.extract())


if __name__ == "__main__":
    loader = WorkLoader()
    print(loader.load())
```

### File 3: Registration in ContextLoader

**File:** `.claude/haios/modules/context_loader.py`
**Location:** Lines 109-117 in `_register_default_loaders()`

**Current Code:**
```python
# context_loader.py:109-117
    def _register_default_loaders(self) -> None:
        """Register built-in loaders."""
        try:
            # Import from sibling lib directory
            import sys
            lib_path = str(self._project_root / ".claude" / "haios" / "lib")
            if lib_path not in sys.path:
                sys.path.insert(0, lib_path)
            from identity_loader import IdentityLoader
            self._loader_registry["identity"] = IdentityLoader
        except ImportError as e:
            logger.warning(f"Could not import IdentityLoader: {e}")

        try:
            # CH-005: Register SessionLoader for session context
            from session_loader import SessionLoader
            self._loader_registry["session"] = SessionLoader
        except ImportError as e:
            logger.warning(f"Could not import SessionLoader: {e}")
```

**Add After SessionLoader registration:**
```python
        try:
            # CH-006: Register WorkLoader for work context
            from work_loader import WorkLoader
            self._loader_registry["work"] = WorkLoader
        except ImportError as e:
            logger.warning(f"Could not import WorkLoader: {e}")
```

### Call Chain Context

```
just work-options
    |
    +-> WorkLoader.load()
    |       |
    |       +-> extract() → {queue, pending, epoch_warning}
    |       +-> format()  → Formatted string
    |
    +-> stdout (for coldstart consumption)

coldstart (future Phase 3)
    |
    +-> just work-options
    |
    +-> Inject into context
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Dependency injection for queue | `queue_fn` parameter | Testability without subprocess mocking (82323) |
| Wrapper over subprocess | Direct `just queue` call | Reuses existing queue recipe rather than reimplementing |
| Epoch alignment warning | Check E2- prefix vs current epoch | CH-006 R2 requirement |
| Legacy count as warning | Non-blocking | Queue items from prior epochs are valid, just need visibility |
| Follow SessionLoader pattern | Same structure | 82327 - pattern established for future loaders |

### Input/Output Examples

**Current (survey-cycle inline):**
```
Agent: Bash(command="just queue") -> parse -> Bash(command="just ready") -> merge -> format
Result: Multiple tool calls, no epoch check
```

**After (WorkLoader):**
```
just work-options
=== WORK OPTIONS ===

WARNING: Queue contains 11 items from prior epochs.
Current epoch: E2.3

Queue (top 5):
  1. E2-072: Critique Subagent
  2. E2-236: Orphan Detection
  3. E2-293: Add set-queue Recipe
  4. INV-017: Observability Gap
  5. INV-019: Requirements Synthesis

Pending from checkpoint:
  CH-006 Work Loader
  INV-068 Cycle Delegation
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Empty queue | Return "(empty)" | Test 2 |
| No checkpoint | Return "(none)" for pending | Test 3 |
| Queue command fails | Log warning, return empty list | Test 2 |
| Config file missing | Graceful degradation with defaults | Test 1 |

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| (none) | - | - | No operator decisions in WORK-010 frontmatter |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_work_loader.py` with 5 tests from Tests First section
- [ ] Verify all tests fail (red) - WorkLoader doesn't exist yet

### Step 2: Create Config File
- [ ] Create `.claude/haios/config/loaders/work.yaml` per Detailed Design
- [ ] Test 1 (config loading) passes (green)

### Step 3: Create WorkLoader Class
- [ ] Create `.claude/haios/lib/work_loader.py` per Detailed Design
- [ ] Tests 2, 3, 4, 5 pass (green)

### Step 4: Register in ContextLoader
- [ ] Add WorkLoader registration in `context_loader.py:117` (after SessionLoader)
- [ ] Run `pytest tests/test_context_loader.py -v` - no regressions

### Step 5: Add Justfile Recipe
- [ ] Add `work-options` recipe to `justfile` (after `session-context` recipe)
- [ ] Verify `just work-options` outputs formatted work context

### Step 6: Integration Verification
- [ ] All tests pass: `pytest tests/test_work_loader.py -v`
- [ ] Run full test suite (no regressions): `pytest tests/ -v`

### Step 7: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/lib/README.md` with `work_loader.py`
- [ ] **MUST:** Update `.claude/haios/config/loaders/README.md` (if exists) with `work.yaml`

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Queue output format changes | Low | Regex parsing with fallback to empty list |
| Checkpoint frontmatter changes | Low | Graceful degradation if `pending` field missing |
| Subprocess call on Windows | Medium | Use `just` which handles platform differences |
| Config file path resolution | Low | Use same PROJECT_ROOT pattern as siblings |

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

**MUST** read `docs/work/active/WORK-010/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| `config/loaders/work.yaml` | [ ] | File exists with queue/pending config |
| `.claude/haios/lib/work_loader.py` | [ ] | WorkLoader class with extract/format/load |
| `tests/test_work_loader.py` | [ ] | 5 tests pass |
| Register in ContextLoader | [ ] | WorkLoader in `_loader_registry` |
| `just work-options` recipe | [ ] | Recipe exists in justfile |
| Epoch alignment warning | [ ] | WARNING appears when legacy items in queue |
| Formatted output | [ ] | `just work-options` outputs readable format |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/config/loaders/work.yaml` | Config with queue/output sections | [ ] | |
| `.claude/haios/lib/work_loader.py` | WorkLoader class per design | [ ] | |
| `tests/test_work_loader.py` | 5 tests covering config/extract/format/load | [ ] | |
| `.claude/haios/modules/context_loader.py` | WorkLoader registered at line 117+ | [ ] | |
| `justfile` | `work-options` recipe added | [ ] | |
| `.claude/haios/lib/README.md` | **MUST:** Includes work_loader.py | [ ] | |

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

- @.claude/haios/epochs/E2_3/arcs/configuration/CH-006-work-loader.md (chapter spec)
- @.claude/haios/lib/session_loader.py (pattern to follow)
- @.claude/haios/config/loaders/session.yaml (config pattern)
- Memory: 82322 (loader pattern), 82323 (DI for testability), 82327 (pattern for future loaders)

---
