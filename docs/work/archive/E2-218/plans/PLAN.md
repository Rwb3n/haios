---
template: implementation_plan
status: complete
date: 2025-12-28
backlog_id: E2-218
title: Observation Triage Cycle Implementation
author: Hephaestus
lifecycle_phase: plan
session: 135
version: '1.5'
generated: 2025-12-21
last_updated: '2025-12-28T15:44:42'
---
# Implementation Plan: Observation Triage Cycle Implementation

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

## Goal

A triage cycle skill that consumes archived observations and routes them to actionable outcomes (spawn work items, store to memory, flag for discussion, or dismiss as noise).

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | observations.py, observations.md template, justfile |
| Lines of code affected | ~250 | observations.py (253 lines), adding ~100 |
| New files to create | 1 | .claude/skills/observation-triage-cycle/SKILL.md |
| Tests to write | 6 | Unit tests for new functions |
| Dependencies | 2 | scaffold.py, ingester (for memory) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Med | Skills registry, justfile, memory system |
| Risk of regression | Low | New functions, existing code unchanged |
| External dependencies | Low | Only internal HAIOS modules |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Phase 1: Core functions | 30 min | High |
| Phase 2: Skill creation | 15 min | High |
| Phase 3: Template/recipe | 15 min | High |
| Phase 4: Integration | 15 min | Med |
| **Total** | ~75 min | |

---

## Current State vs Desired State

### Current State

```
Capture (E2-217) → Archive → (nothing)
```

**Behavior:** Observations are captured during close-work-cycle's OBSERVE phase, stored in `observations.md`, then archived with work item.

**Result:** Write-only system. Observations accumulate but are never read or acted upon. Same pattern as INV-023 (ReasoningBank feedback gap).

### Desired State

```
Capture → Archive → Triage (SCAN → TRIAGE → PROMOTE) → Actions
```

**Behavior:** A triage cycle skill scans archived observations, classifies them by category/action/priority, then executes appropriate actions.

**Result:** Feedback loop closed. Observations spawn work items, get stored to memory, flagged for discussion, or dismissed as noise.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Scan finds pending observations
```python
def test_scan_archived_observations_finds_pending(tmp_path):
    """Scan finds observations with triage_status: pending."""
    # Setup: Create archived work item with pending observations
    work_dir = tmp_path / "docs" / "work" / "archive" / "E2-TEST"
    work_dir.mkdir(parents=True)
    obs_file = work_dir / "observations.md"
    obs_file.write_text("---\ntriage_status: pending\n---\n## Gaps\n- [x] Test gap")

    # Action
    result = scan_archived_observations(base_path=tmp_path)

    # Assert
    assert len(result) == 1
    assert result[0]["work_id"] == "E2-TEST"
```

### Test 2: Scan skips triaged observations
```python
def test_scan_archived_observations_skips_triaged(tmp_path):
    """Scan skips observations with triage_status: triaged."""
    # Setup
    work_dir = tmp_path / "docs" / "work" / "archive" / "E2-DONE"
    work_dir.mkdir(parents=True)
    obs_file = work_dir / "observations.md"
    obs_file.write_text("---\ntriage_status: triaged\n---\n## Gaps\n- [x] Old gap")

    # Action
    result = scan_archived_observations(base_path=tmp_path)

    # Assert
    assert len(result) == 0
```

### Test 3: Parse extracts observations
```python
def test_parse_observations_extracts_items():
    """Parse extracts checked observations from markdown sections."""
    content = """
## Unexpected Behaviors
- [x] Bug A: Something broke
- [ ] **None observed**

## Gaps Noticed
- [x] Gap B: Missing feature
"""
    result = parse_observations(content)

    assert len(result) == 2
    assert result[0]["text"] == "Bug A: Something broke"
    assert result[0]["section"] == "Unexpected Behaviors"
```

### Test 4: Parse handles "None observed"
```python
def test_parse_observations_handles_none_observed():
    """Parse skips 'None observed' items."""
    content = """
## Unexpected Behaviors
- [x] **None observed**
"""
    result = parse_observations(content)

    assert len(result) == 0
```

### Test 5: Triage validates dimensions
```python
def test_triage_observation_valid_dimensions():
    """Triage accepts valid category/action/priority."""
    obs = {"text": "Test gap", "section": "Gaps Noticed"}

    result = triage_observation(obs, category="gap", action="spawn:WORK", priority="P2")

    assert result["category"] == "gap"
    assert result["action"] == "spawn:WORK"
    assert result["priority"] == "P2"
```

### Test 6: Triage rejects invalid dimensions
```python
def test_triage_observation_rejects_invalid():
    """Triage rejects invalid dimension values."""
    obs = {"text": "Test", "section": "Gaps"}

    with pytest.raises(ValueError):
        triage_observation(obs, category="invalid", action="spawn:WORK", priority="P2")
```

---

## Detailed Design

### New Functions in observations.py

**File:** `.claude/lib/observations.py`
**Location:** Add after existing functions (line 212+)

#### 1. scan_archived_observations()

```python
def scan_archived_observations(base_path: Optional[Path] = None) -> list[dict]:
    """Scan archived work items for untriaged observations.

    Args:
        base_path: Override project root (for testing)

    Returns:
        List of dicts with work_id, path, observations for pending items.
    """
    root = base_path or PROJECT_ROOT
    archive_dir = root / "docs" / "work" / "archive"

    results = []
    for work_dir in archive_dir.iterdir():
        if not work_dir.is_dir():
            continue

        obs_path = work_dir / "observations.md"
        if not obs_path.exists():
            continue

        content = obs_path.read_text(encoding="utf-8")
        # Check triage_status in frontmatter
        if "triage_status: pending" in content or "triage_status:" not in content:
            observations = parse_observations(content)
            if observations:
                results.append({
                    "work_id": work_dir.name,
                    "path": obs_path,
                    "observations": observations
                })

    return results
```

#### 2. parse_observations()

```python
def parse_observations(content: str) -> list[dict]:
    """Parse observations.md into structured list.

    Args:
        content: Raw markdown content

    Returns:
        List of dicts with text, section for each checked observation.
    """
    results = []
    current_section = None

    for line in content.split("\n"):
        # Track section headers
        if line.startswith("## "):
            current_section = line[3:].strip()
            continue

        # Find checked items (not "None observed")
        match = re.match(r'\[x\]\s*(.+)', line, re.IGNORECASE)
        if match and current_section:
            text = match.group(1).strip()
            # Skip "None observed" entries
            if "**None observed**" in text:
                continue
            results.append({
                "text": text,
                "section": current_section
            })

    return results
```

#### 3. triage_observation()

```python
VALID_CATEGORIES = {"bug", "gap", "debt", "insight", "question", "noise"}
VALID_ACTIONS = {"spawn:INV", "spawn:WORK", "spawn:FIX", "memory", "discuss", "dismiss"}
VALID_PRIORITIES = {"P0", "P1", "P2", "P3"}

def triage_observation(obs: dict, category: str, action: str, priority: str) -> dict:
    """Apply triage dimensions to an observation.

    Args:
        obs: Observation dict with text and section
        category: bug|gap|debt|insight|question|noise
        action: spawn:INV|spawn:WORK|spawn:FIX|memory|discuss|dismiss
        priority: P0|P1|P2|P3

    Returns:
        Observation dict with triage fields added

    Raises:
        ValueError: If any dimension is invalid
    """
    if category not in VALID_CATEGORIES:
        raise ValueError(f"Invalid category: {category}. Valid: {VALID_CATEGORIES}")
    if action not in VALID_ACTIONS:
        raise ValueError(f"Invalid action: {action}. Valid: {VALID_ACTIONS}")
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Invalid priority: {priority}. Valid: {VALID_PRIORITIES}")

    return {
        **obs,
        "category": category,
        "action": action,
        "priority": priority
    }
```

#### 4. promote_observation()

```python
def promote_observation(obs: dict) -> dict:
    """Execute the action for a triaged observation.

    Args:
        obs: Triaged observation with category, action, priority

    Returns:
        Dict with result of promotion (spawned_id, memory_id, or status)
    """
    action = obs.get("action", "")

    if action == "dismiss":
        return {"status": "dismissed", "message": "No action needed"}

    if action == "discuss":
        return {"status": "flagged", "message": "Flagged for operator discussion"}

    if action == "memory":
        # Would call ingester_ingest in real implementation
        return {"status": "stored", "message": "Stored to memory"}

    if action.startswith("spawn:"):
        spawn_type = action.split(":")[1]
        # Would call scaffold in real implementation
        return {"status": "spawned", "type": spawn_type, "message": f"Would spawn {spawn_type}"}

    return {"status": "unknown", "message": f"Unknown action: {action}"}
```

### Call Chain Context

```
Skill(skill="observation-triage-cycle")
    |
    +-> SCAN phase
    |       scan_archived_observations()
    |           Returns: list[dict] of pending observations
    |
    +-> TRIAGE phase (interactive)
    |       triage_observation() for each
    |           Returns: triaged observation
    |
    +-> PROMOTE phase
            promote_observation() for each
                Returns: action result
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Standalone skill | Not embedded in close-work-cycle | Keeps closure lean; triage can run independently |
| Interactive triage | Agent prompts per observation | Avoids automated misclassification; builds agent calibration |
| triage_status field | In frontmatter | Enables scan to skip already-processed files |
| promote_observation stubs | Return dicts, don't execute | Full integration requires scaffold/ingester; stubs enable testing |

### Input/Output Examples

**Real archived observations (E2-217):**
```
scan_archived_observations()
Returns: [
    {
        "work_id": "E2-217",
        "path": "docs/work/archive/E2-217/observations.md",
        "observations": [
            {"text": "Nested directory on archive move...", "section": "Unexpected Behaviors"},
            {"text": "commit-close recipe uses legacy patterns...", "section": "Gaps Noticed"},
            {"text": "No scaffold for AGENT variable...", "section": "Gaps Noticed"},
            {"text": "Extend to transcript scanning...", "section": "Future Considerations"},
            {"text": "Triage cycle needed...", "section": "Future Considerations"}
        ]
    }
]
```

**After triage:**
```
triage_observation(obs[1], category="gap", action="spawn:FIX", priority="P2")
Returns: {
    "text": "commit-close recipe uses legacy patterns...",
    "section": "Gaps Noticed",
    "category": "gap",
    "action": "spawn:FIX",
    "priority": "P2"
}
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No observations.md | Skip work item | Implicit in scan logic |
| All "None observed" | Return empty list | Test 4 |
| Already triaged | Skip file | Test 2 |
| Invalid dimensions | Raise ValueError | Test 6 |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add 6 tests to `tests/test_observations.py`
- [ ] Verify all tests fail (red)

### Step 2: Core Functions (observations.py)
- [ ] Add `parse_observations()` function
- [ ] Add `triage_observation()` with validation
- [ ] Add `scan_archived_observations()` function
- [ ] Add `promote_observation()` stub
- [ ] Tests 1-6 pass (green)

### Step 3: Create Skill
- [ ] Create `.claude/skills/observation-triage-cycle/` directory
- [ ] Write SKILL.md with SCAN → TRIAGE → PROMOTE phases
- [ ] Verify skill auto-discovered in haios-status-slim.json

### Step 4: Template and Recipe
- [ ] Update observations.md template with `triage_status: pending`
- [ ] Add `just triage-observations` recipe to justfile
- [ ] Add CLI entry point to observations.py

### Step 5: Integration Verification
- [ ] All tests pass
- [ ] Run full test suite (no regressions)
- [ ] Demo: Run `just triage-observations` on real data

### Step 6: README Sync (MUST)
- [ ] **MUST:** Update `.claude/lib/README.md` if observations.py changes documented
- [ ] **MUST:** Update `.claude/skills/README.md` with new skill
- [ ] **MUST:** Verify CLAUDE.md skills table includes new skill

---

## Verification

- [ ] Tests pass (`pytest tests/test_observations.py -v`)
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Demo: `just triage-observations` runs successfully

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Modifying archived files | Low | Only append to Triage Log section |
| Agent triage quality | Med | Interactive prompts with validation |
| Action execution failures | Low | Error handling in promote_observation() |

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
| `.claude/lib/observations.py` | Contains 4 new functions | [ ] | |
| `tests/test_observations.py` | Contains 6 tests, all pass | [ ] | |
| `.claude/skills/observation-triage-cycle/SKILL.md` | Skill exists with 3 phases | [ ] | |
| `.claude/templates/observations.md` | Has triage_status field | [ ] | |
| `justfile` | Has triage-observations recipe | [ ] | |
| `.claude/haios-status-slim.json` | Skill appears in skills list | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_observations.py -v
# Expected: 6 tests passed

just triage-observations
# Expected: Scans archived observations
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [ ] | |
| Test output pasted above? | [ ] | |
| Any deviations from plan? | [ ] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- E2-217: Observation Capture Gate (upstream)
- INV-047: Close Cycle Observation Phase Ordering
- INV-023: ReasoningBank Feedback Loop Architecture
- Session 134: Design discussion
- ADR-033: Work Item Lifecycle

---
