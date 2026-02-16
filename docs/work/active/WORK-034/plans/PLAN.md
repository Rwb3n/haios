---
template: implementation_plan
status: complete
date: 2026-02-16
backlog_id: WORK-034
title: "Upstream Status Propagation on Work Closure"
author: Hephaestus
lifecycle_phase: plan
session: 386
version: "1.5"
generated: 2026-02-16
last_updated: 2026-02-16T20:17:15
---
# Implementation Plan: Upstream Status Propagation on Work Closure

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
| Query prior work | SHOULD | Memory queried (85642-85665 from S384) — no prior status propagation implementations |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

When a work item closes, automatically propagate status upstream: update the chapter row in ARC.md when all work items for that chapter are complete, and flag when an arc's chapters are all complete.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/skills/close-work-cycle/SKILL.md` (integration point doc) |
| New files to create | 2 | `lib/status_propagator.py`, `tests/test_status_propagator.py` |
| Tests to write | 9 | See Tests First section (8 test functions, 9 assertions) |
| Dependencies | 3 | `work_engine.py` (WorkEngine), `config.py` (ConfigLoader), `governance_events.py` (event logging) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | Reads WorkEngine, writes ARC.md, logs events |
| Risk of regression | Low | New module, no existing code modified |
| External dependencies | Low | Only reads/writes local markdown files |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 15 min | High |
| Implementation | 25 min | High |
| Integration + Verification | 10 min | High |
| **Total** | **50 min** | |

---

## Current State vs Desired State

### Current State

```
close-work-cycle ARCHIVE phase (SKILL.md:148-157):
  1. just close-work {id}  -> status: active -> complete, closed: date
  2. just cascade {id}     -> unblocks dependents
  3. just update-status    -> refreshes haios-status-slim.json
```

**Behavior:** Work item closes. Chapter/Arc status in ARC.md is NOT updated. Drift accumulates between work item status and ARC.md status tables (as seen with WORK-153, WORK-154 this session).

**Result:** Manual EPOCH.md/ARC.md updates required. Error-prone. Drift detected by EpochValidator but never auto-fixed.

### Desired State

```
close-work-cycle ARCHIVE phase:
  1. just close-work {id}  -> status: active -> complete, closed: date
  2. just cascade {id}     -> unblocks dependents
  3. just update-status    -> refreshes haios-status-slim.json
  4. propagate_status(id)  -> NEW: update chapter row in ARC.md if all chapter work complete
```

**Behavior:** After work item closes, StatusPropagator reads `chapter` and `arc` from frontmatter, resolves ARC.md path, checks if all work items for that chapter are complete, and updates the chapter status row. Logs a `StatusPropagation` event.

**Result:** ARC.md chapter status tables stay in sync with actual work item status. No manual drift fixes needed.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Extract chapter and arc from work item frontmatter
```python
def test_get_hierarchy_context_from_frontmatter(tmp_path):
    """StatusPropagator reads chapter/arc from raw WORK.md frontmatter."""
    propagator = StatusPropagator(base_path=tmp_path)
    # Create work item with chapter/arc fields
    ctx = propagator.get_hierarchy_context("WORK-034")
    assert ctx["chapter"] == "CH-045"
    assert ctx["arc"] == "engine-functions"
```

### Test 2: Detect chapter completion (all work items complete)
```python
def test_is_chapter_complete_all_done(tmp_path):
    """Returns True when all work items for a chapter have complete status."""
    propagator = StatusPropagator(base_path=tmp_path)
    # Create 2 work items for CH-049, both complete
    assert propagator.is_chapter_complete("CH-049") is True
```

### Test 3: Detect chapter incomplete (some work items still active)
```python
def test_is_chapter_complete_partial(tmp_path):
    """Returns False when some work items for a chapter are still active."""
    propagator = StatusPropagator(base_path=tmp_path)
    # Create 2 work items for CH-047, one complete, one active
    assert propagator.is_chapter_complete("CH-047") is False
```

### Test 4: Update ARC.md chapter status row
```python
def test_update_arc_chapter_status(tmp_path):
    """Updates the chapter row status in ARC.md from Planning to Complete."""
    propagator = StatusPropagator(base_path=tmp_path)
    # Create ARC.md with chapter table
    result = propagator.update_arc_chapter_status("engine-functions", "CH-045", "Complete")
    assert result["updated"] is True
    # Read ARC.md and verify status changed
    content = (tmp_path / ".claude/haios/epochs/E2_7/arcs/engine-functions/ARC.md").read_text()
    assert "Complete" in content
```

### Test 5: No-op when chapter/arc fields missing
```python
def test_propagate_noop_when_no_hierarchy(tmp_path):
    """Returns early with no_hierarchy result when work item lacks chapter/arc."""
    propagator = StatusPropagator(base_path=tmp_path)
    # Create work item WITHOUT chapter/arc fields
    result = propagator.propagate("WORK-999")
    assert result["action"] == "no_hierarchy"
```

### Test 6: Full propagation flow (chapter completes)
```python
def test_propagate_full_chapter_completes(tmp_path):
    """Full propagation: work closes, chapter detected complete, ARC.md updated."""
    propagator = StatusPropagator(base_path=tmp_path)
    # Create work item (complete) as sole item in chapter
    # Create ARC.md with chapter row status=Planning
    result = propagator.propagate("WORK-153")
    assert result["action"] == "chapter_completed"
    assert result["chapter"] == "CH-049"
    assert result["arc_updated"] is True
```

### Test 7: Event logging on propagation
```python
def test_propagation_logs_event(tmp_path):
    """StatusPropagation event logged to governance-events.jsonl."""
    propagator = StatusPropagator(base_path=tmp_path, events_file=tmp_path / "events.jsonl")
    result = propagator.propagate("WORK-153")
    events = (tmp_path / "events.jsonl").read_text().strip().split("\n")
    event = json.loads(events[-1])
    assert event["type"] == "StatusPropagation"
    assert event["work_id"] == "WORK-153"
    assert event["chapter"] == "CH-049"
```

### Test 8: Arc completion detection
```python
def test_is_arc_complete(tmp_path):
    """Returns True when all chapter rows in ARC.md have Complete status."""
    propagator = StatusPropagator(base_path=tmp_path)
    # Create ARC.md with 2 chapters, both Complete
    assert propagator.is_arc_complete("infrastructure") is True

def test_is_arc_not_complete(tmp_path):
    """Returns False when some chapter rows still show Planning."""
    propagator = StatusPropagator(base_path=tmp_path)
    # Create ARC.md with 2 chapters, one Complete, one Planning
    assert propagator.is_arc_complete("infrastructure") is False
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

**New File:** `.claude/haios/lib/status_propagator.py`

```python
"""
Upstream Status Propagation (WORK-034).

Propagates work item closure status to chapter rows in ARC.md.
When all work items for a chapter are complete, updates the chapter
status in the parent arc's ARC.md file.

Usage:
    from status_propagator import StatusPropagator

    # Injected (testing):
    propagator = StatusPropagator(base_path=tmp_path)

    # Disk-loading (production):
    propagator = StatusPropagator()

    result = propagator.propagate("WORK-034")
"""
import json
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

COMPLETE_STATUSES = {"complete", "completed", "done", "closed", "archived"}


class StatusPropagator:
    def __init__(
        self,
        base_path: Optional[Path] = None,
        events_file: Optional[Path] = None,
    ):
        self._base_path = base_path or Path(__file__).parent.parent.parent.parent
        self._events_file = events_file or (
            self._base_path / ".claude" / "haios" / "governance-events.jsonl"
        )

    def propagate(self, work_id: str) -> dict:
        """Main entry: propagate status for a closed work item."""
        ctx = self.get_hierarchy_context(work_id)
        if ctx is None:
            return {"action": "no_hierarchy", "work_id": work_id}

        chapter_id = ctx["chapter"]
        arc_name = ctx["arc"]

        if not self.is_chapter_complete(chapter_id):
            return {
                "action": "chapter_incomplete",
                "work_id": work_id,
                "chapter": chapter_id,
            }

        update_result = self.update_arc_chapter_status(arc_name, chapter_id, "Complete")
        arc_complete = self.is_arc_complete(arc_name)
        action = "arc_completed" if arc_complete else "chapter_completed"
        self._log_event(work_id, chapter_id, arc_name, action)

        return {
            "action": action,
            "work_id": work_id,
            "chapter": chapter_id,
            "arc": arc_name,
            "arc_updated": update_result["updated"],
            "arc_complete": arc_complete,
        }

    def get_hierarchy_context(self, work_id: str) -> Optional[Dict]:
        """Read chapter/arc from work item raw frontmatter."""
        # Search active work dir for matching WORK.md
        work_dir = self._base_path / "docs" / "work" / "active" / work_id / "WORK.md"
        if not work_dir.exists():
            return None
        content = work_dir.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None
        fm = yaml.safe_load(parts[1]) or {}
        chapter = fm.get("chapter")
        arc = fm.get("arc")
        if not chapter or not arc:
            return None
        return {"chapter": chapter, "arc": arc}

    def is_chapter_complete(self, chapter_id: str) -> bool:
        """Check if all work items assigned to chapter_id are complete."""
        active_dir = self._base_path / "docs" / "work" / "active"
        if not active_dir.exists():
            return False
        chapter_items = []
        for work_path in active_dir.iterdir():
            if not work_path.is_dir():
                continue
            work_file = work_path / "WORK.md"
            if not work_file.exists():
                continue
            content = work_file.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            if len(parts) < 3:
                continue
            fm = yaml.safe_load(parts[1]) or {}
            if fm.get("chapter") == chapter_id:
                chapter_items.append(fm.get("status", "active"))
        if not chapter_items:
            return False  # No items = not complete (unfunded)
        return all(s.lower() in COMPLETE_STATUSES for s in chapter_items)

    def update_arc_chapter_status(
        self, arc_name: str, chapter_id: str, new_status: str
    ) -> dict:
        """Update the chapter row in ARC.md status table."""
        # Load arcs_dir from haios.yaml
        haios_path = self._base_path / ".claude" / "haios" / "config" / "haios.yaml"
        if not haios_path.exists():
            return {"updated": False, "reason": "haios_config_not_found"}
        haios_config = yaml.safe_load(haios_path.read_text(encoding="utf-8"))
        arcs_dir = haios_config.get("epoch", {}).get("arcs_dir", "")
        arc_file = self._base_path / arcs_dir / arc_name / "ARC.md"
        if not arc_file.exists():
            return {"updated": False, "reason": "arc_file_not_found"}

        content = arc_file.read_text(encoding="utf-8")
        # Match table row: | CH-XXX | ... | Status |
        # Pattern: capture everything up to last pipe, then status cell
        pattern = rf"(\|\s*{re.escape(chapter_id)}\s*\|.*\|\s*)[^|]+?(\s*\|)"
        match = re.search(pattern, content)
        if not match:
            return {"updated": False, "reason": "chapter_row_not_found"}

        updated = re.sub(pattern, rf"\g<1>{new_status}\2", content)
        arc_file.write_text(updated, encoding="utf-8")
        return {"updated": True}

    def is_arc_complete(self, arc_name: str) -> bool:
        """Check if all chapters in ARC.md have Complete status.
        Parses the chapter table and checks every status cell."""
        haios_path = self._base_path / ".claude" / "haios" / "config" / "haios.yaml"
        if not haios_path.exists():
            return False
        haios_config = yaml.safe_load(haios_path.read_text(encoding="utf-8"))
        arcs_dir = haios_config.get("epoch", {}).get("arcs_dir", "")
        arc_file = self._base_path / arcs_dir / arc_name / "ARC.md"
        if not arc_file.exists():
            return False
        content = arc_file.read_text(encoding="utf-8")
        # Find all chapter status rows: | CH-XXX | ... | Status |
        rows = re.findall(r"\|\s*CH-\d+\s*\|.*\|\s*([^|]+?)\s*\|", content)
        if not rows:
            return False
        return all(s.strip().lower() in {"complete", "completed", "done"} for s in rows)

    def _log_event(self, work_id: str, chapter: str, arc: str, action: str) -> None:
        """Append StatusPropagation event to governance-events.jsonl."""
        event = {
            "type": "StatusPropagation",
            "work_id": work_id,
            "chapter": chapter,
            "arc": arc,
            "action": action,
            "timestamp": datetime.now().isoformat(),
        }
        self._events_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self._events_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
```

**Integration Change:** `.claude/skills/close-work-cycle/SKILL.md` ARCHIVE phase

Add after step 2 (Update associated plans):
```
3. Run status propagation:
   StatusPropagator(from lib/status_propagator.py).propagate(work_id)
   This propagates chapter completion status to ARC.md.
```

### Call Chain Context

```
/close {id}
  |
  +-> retro-cycle (prerequisite)
  +-> dod-validation-cycle
  +-> close-work-cycle
        |
        +-> VALIDATE phase
        +-> ARCHIVE phase
        |     |
        |     +-> just close-work {id}     (status -> complete)
        |     +-> just cascade {id}        (unblock dependents)
        |     +-> just update-status       (refresh status JSON)
        |     +-> StatusPropagator.propagate(id)  # <-- NEW
        |
        +-> CHAIN phase
```

### Function/Component Signatures

```python
class StatusPropagator:
    """Upstream status propagation from work item closure to ARC.md chapter rows.
    All I/O injectable via base_path for testing. Production auto-detects from __file__."""

    def __init__(self, base_path: Optional[Path] = None, events_file: Optional[Path] = None) -> None: ...

    def propagate(self, work_id: str) -> dict:
        """Main entry point. Returns dict with action, work_id, chapter, arc, arc_updated."""

    def get_hierarchy_context(self, work_id: str) -> Optional[Dict]:
        """Read chapter/arc from work item frontmatter. Returns {"chapter": ..., "arc": ...} or None."""

    def is_chapter_complete(self, chapter_id: str) -> bool:
        """Scan active work items for matching chapter. True if all are complete."""

    def update_arc_chapter_status(self, arc_name: str, chapter_id: str, new_status: str) -> dict:
        """Find ARC.md, locate chapter row, replace status cell. Returns {"updated": bool, "reason": str}."""

    def is_arc_complete(self, arc_name: str) -> bool:
        """Parse ARC.md chapter table. True if all chapter rows have Complete status."""

    def _log_event(self, work_id: str, chapter: str, arc: str, action: str) -> None:
        """Append StatusPropagation event to governance events JSONL."""
```

### Behavior Logic

```
propagate(work_id)
  |
  +-> get_hierarchy_context(work_id)
  |     Read WORK.md frontmatter -> extract chapter, arc
  |     +-- Missing chapter/arc -> return {"action": "no_hierarchy"}
  |     +-- Found -> continue
  |
  +-> is_chapter_complete(chapter_id)
  |     Scan docs/work/active/*/WORK.md for chapter == chapter_id
  |     +-- Any non-complete -> return {"action": "chapter_incomplete"}
  |     +-- All complete -> continue
  |
  +-> update_arc_chapter_status(arc_name, chapter_id, "Complete")
  |     Resolve: {arcs_dir}/{arc_name}/ARC.md
  |     Regex: find table row with chapter_id, replace status cell
  |     +-- Write updated content back
  |
  +-> is_arc_complete(arc_name)
  |     Parse ARC.md chapter table, check all status cells
  |     +-- All Complete -> action = "arc_completed"
  |     +-- Some not Complete -> action = "chapter_completed"
  |
  +-> _log_event(work_id, chapter, arc, action)
  |     Append to governance-events.jsonl
  |
  +-> return {"action": action, "arc_complete": bool, ...}
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Module location | `lib/status_propagator.py` | Follows sibling pattern (epoch_validator.py, queue_ceremonies.py) in lib/ |
| Injectable base_path | Constructor injection | Same pattern as EpochValidator — enables testing with tmp_path |
| Read raw frontmatter, not WorkState | Parse YAML directly | WorkState doesn't include chapter/arc fields; adding them is scope creep for CH-044 |
| Scan active work dir for chapter membership | Glob + frontmatter parse | No chapter-to-work mapping exists; scanning is O(n) on ~100+ active items, still fast |
| Regex table row update for ARC.md | Regex on markdown table | ARC.md is markdown, not YAML. Same approach as epoch_validator.py for EPOCH.md |
| Arc path from haios.yaml epoch.arcs_dir | ConfigLoader pattern | Single source of truth per CLAUDE.md rule |
| Event type "StatusPropagation" | New event type in governance-events.jsonl | Follows existing event types (CyclePhaseEntered, ValidationOutcome) |
| No EPOCH.md exit criteria auto-check | Explicit non-goal | Deliverables scope to chapter-to-arc. Epoch exit criteria is a separate concern |
| Unfunded chapters = not complete | `is_chapter_complete` returns False when no items found | Prevents vacuous truth from auto-completing unfunded chapters |
| Integration via skill doc, not code hook | Document in close-work-cycle SKILL.md | The skill is the recipe; agent follows skill instructions |

### Input/Output Examples

**Real Example — WORK-153 (BugBatch, CH-049, infrastructure arc):**

Before propagation (ARC.md infrastructure table):
```
| CH-049 | BugBatch | WORK-153 | REQ-CEREMONY-001, REQ-CEREMONY-002 | None | Planning |
```

After propagation (WORK-153 is the only item in CH-049, and it's complete):
```python
result = propagator.propagate("WORK-153")
# result = {
#   "action": "chapter_completed",
#   "work_id": "WORK-153",
#   "chapter": "CH-049",
#   "arc": "infrastructure",
#   "arc_updated": True
# }
```

ARC.md after:
```
| CH-049 | BugBatch | WORK-153 | REQ-CEREMONY-001, REQ-CEREMONY-002 | None | Complete |
```

**Real Example — WORK-152 (TemplateComposability, CH-047, composability arc):**

CH-047 has TWO work items: WORK-152 and WORK-155. If WORK-152 closes but WORK-155 is still active:
```python
result = propagator.propagate("WORK-152")
# result = {
#   "action": "chapter_incomplete",
#   "work_id": "WORK-152",
#   "chapter": "CH-047"
# }
# No ARC.md update — chapter not yet complete.
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Work item has no chapter/arc fields | Return `no_hierarchy`, no error | Test 5 |
| Chapter has zero work items (unfunded) | `is_chapter_complete` returns False | By design — unfunded chapters don't auto-complete |
| ARC.md file doesn't exist | Return `{"updated": False, "reason": "arc_file_not_found"}` | Implicit in setup |
| Chapter ID not found in ARC.md table | Return `{"updated": False, "reason": "chapter_row_not_found"}` | Implicit in regex |
| Multiple arcs for same epoch | Each work item has specific `arc` field; no ambiguity | By design |
| Work item already archived | `get_hierarchy_context` checks active dir; propagation runs at close time when still active | Low risk |

### Open Questions

**Q: Should unfunded chapters (no work items) block arc completion detection?**

Unfunded chapters are "Planning" in ARC.md. They won't auto-complete because no work item closure triggers propagation for them. This is correct — unfunded means "not started." Arc completion detection is out of scope.

**Q: Should we also update EPOCH.md arc status tables?**

No. EPOCH.md has its own table format and the EpochValidator already detects drift. Cascading to EPOCH.md is a separate concern — could be a follow-up work item or part of CH-044's hierarchy engine.

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
| No open decisions | - | Resolved | Design fully determined by existing metadata fields and patterns |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Create `tests/test_status_propagator.py`
- [ ] Write all 9 tests with tmp_path fixtures
- [ ] Verify all tests fail (red) — module doesn't exist yet

### Step 2: Implement StatusPropagator Core
- [ ] Create `.claude/haios/lib/status_propagator.py`
- [ ] Implement `get_hierarchy_context()` — YAML frontmatter parsing
- [ ] Implement `is_chapter_complete()` — scan active work items
- [ ] Tests 1-3, 5 pass (green)

### Step 3: Implement ARC.md Update, Arc Completion, and Event Logging
- [ ] Implement `update_arc_chapter_status()` — regex table row update
- [ ] Implement `is_arc_complete()` — parse ARC.md chapter table statuses
- [ ] Implement `_log_event()` — append to governance-events.jsonl
- [ ] Implement `propagate()` — orchestration method
- [ ] Tests 4, 6, 7, 8 pass (green)

### Step 4: Integration — Update close-work-cycle SKILL.md
- [ ] Add step to ARCHIVE phase actions: run StatusPropagator.propagate()
- [ ] Add StatusPropagation to side_effects in frontmatter
- [ ] Document the new integration point

### Step 5: Integration Verification
- [ ] All 9 tests pass
- [ ] Run full test suite (no regressions)
- [ ] Demo: manually verify with real data (WORK-153/154 already complete)

### Step 6: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/lib/README.md` with new status_propagator.py
- [ ] **MUST:** Verify README content matches actual file state

### Step 7: Consumer Verification
- [ ] **MUST:** Grep for `status_propagat` to verify no stale references
- [ ] **MUST:** Verify close-work-cycle SKILL.md integration point is documented

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| ARC.md format changes break regex | Medium | Tests use real ARC.md format; regex is lenient on whitespace |
| WorkState doesn't expose chapter/arc | Low | Design explicitly uses raw frontmatter parsing, not WorkState |
| Concurrent work item closures race | Low | Single-agent system; closures are sequential |
| Large active work directory slows scan | Low | Currently ~100+ items; O(n) still acceptable for sequential small-file reads |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 386 | 2026-02-16 | - | Plan authored | PLAN phase |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-034/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| `StatusPropagator` module in lib/status_propagator.py | [ ] | File exists with class |
| Parse work item `chapter` and `arc` fields | [ ] | `get_hierarchy_context()` method |
| Update Chapter status in ARC.md when work completes chapter | [ ] | `update_arc_chapter_status()` method |
| Check if all chapters in arc are complete -> log arc completion | [ ] | `is_arc_complete()` method + propagation flow |
| Log StatusPropagation event to governance-events.jsonl | [ ] | `_log_event()` with action type |
| Integration with close-work-cycle ARCHIVE phase | [ ] | SKILL.md updated |
| Tests: propagation scenarios | [ ] | 7 tests in test_status_propagator.py |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/status_propagator.py` | StatusPropagator class with 4 public methods | [ ] | |
| `tests/test_status_propagator.py` | 9 tests covering all scenarios | [ ] | |
| `.claude/skills/close-work-cycle/SKILL.md` | ARCHIVE phase references StatusPropagator | [ ] | |
| `.claude/haios/lib/README.md` | Lists status_propagator.py | [ ] | |

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

- @docs/work/active/WORK-034/WORK.md
- @.claude/skills/close-work-cycle/SKILL.md
- @.claude/haios/lib/epoch_validator.py (sibling pattern)
- @.claude/haios/lib/governance_events.py (event logging pattern)
- @.claude/haios/epochs/E2_7/arcs/infrastructure/ARC.md (real ARC.md format)
- REQ-TRACE-005 (Traceability chain)

---
