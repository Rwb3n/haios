---
template: implementation_plan
status: complete
date: 2026-01-26
backlog_id: E2-236
title: Orphan Session Detection and Recovery
author: Hephaestus
lifecycle_phase: plan
session: 245
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-26T20:17:38'
---
# Implementation Plan: Orphan Session Detection and Recovery

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

ColdstartOrchestrator will detect orphan sessions (sessions that started but never ended due to crash/timeout) and report incomplete work to the agent, enabling graceful recovery from unexpected terminations.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | `.claude/haios/lib/governance_events.py`, `.claude/haios/lib/coldstart_orchestrator.py`, `.claude/haios/lib/session_loader.py` |
| Lines of code affected | ~150 | New functions + integration |
| New files to create | 1 | `tests/test_orphan_detection.py` |
| Tests to write | 6 | detect_orphan, log_session_events, scan_incomplete_work, integration |
| Dependencies | 2 | ColdstartOrchestrator imports detection, SessionLoader reports it |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | governance_events, coldstart_orchestrator, session_loader |
| Risk of regression | Low | New functions, not modifying existing logic |
| External dependencies | Low | File-based only (JSONL, WORK.md) |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write tests | 20 min | High |
| Implement detection | 30 min | High |
| Wire into coldstart | 20 min | High |
| Integration test | 15 min | Medium |
| **Total** | ~85 min | High |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/lib/governance_events.py:34-54 - Only CyclePhaseEntered and ValidationOutcome
def log_phase_transition(phase: str, work_id: str, agent: str) -> dict:
    event = {
        "type": "CyclePhaseEntered",
        # ...
    }
    _append_event(event)
    return event

# No session start/end events exist
# No orphan detection exists
```

**Behavior:** Governance events log cycle phases but not session lifecycle. If a session crashes, the next coldstart has no way to know.

**Result:** Context loss - work may be incomplete with no recovery notification.

### Desired State

```python
# .claude/haios/lib/governance_events.py - Add session lifecycle events
def log_session_start(session_number: int, agent: str) -> dict:
    event = {"type": "SessionStarted", "session": session_number, ...}
    _append_event(event)
    return event

def log_session_end(session_number: int, agent: str) -> dict:
    event = {"type": "SessionEnded", "session": session_number, ...}
    _append_event(event)
    return event

def detect_orphan_session() -> Optional[dict]:
    """Detect session that started but never ended."""
    events = read_events()
    # Find SessionStarted without matching SessionEnded
    # Return orphan info or None
```

**Behavior:** Coldstart detects orphan sessions and injects warning into context.

**Result:** Agent informed of incomplete prior session, can resume or acknowledge.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Detect Orphan When Start Without End
```python
def test_detect_orphan_session_finds_orphan(tmp_path: Path):
    """Detect orphan when SessionStarted exists without SessionEnded."""
    events_file = tmp_path / "events.jsonl"
    events_file.write_text(
        '{"type": "SessionStarted", "session": 100, "timestamp": "2026-01-26T10:00:00"}\n'
        '{"type": "SessionStarted", "session": 101, "timestamp": "2026-01-26T11:00:00"}\n'
    )

    result = detect_orphan_session(events_file)

    assert result is not None
    assert result["orphan_session"] == 100
    assert result["current_session"] == 101
```

### Test 2: No Orphan When All Sessions Ended
```python
def test_detect_orphan_session_no_orphan(tmp_path: Path):
    """No orphan when all SessionStarted have matching SessionEnded."""
    events_file = tmp_path / "events.jsonl"
    events_file.write_text(
        '{"type": "SessionStarted", "session": 100, "timestamp": "2026-01-26T10:00:00"}\n'
        '{"type": "SessionEnded", "session": 100, "timestamp": "2026-01-26T10:30:00"}\n'
        '{"type": "SessionStarted", "session": 101, "timestamp": "2026-01-26T11:00:00"}\n'
    )

    result = detect_orphan_session(events_file)

    assert result is None  # Session 101 is current, not orphan
```

### Test 3: Scan WORK.md for Incomplete Transitions
```python
def test_scan_incomplete_work_finds_exited_null(tmp_path: Path):
    """Find work items with exited: null in node_history."""
    work_dir = tmp_path / "docs" / "work" / "active" / "E2-999"
    work_dir.mkdir(parents=True)
    (work_dir / "WORK.md").write_text('''---
id: E2-999
node_history:
- node: doing
  entered: 2026-01-26 10:00:00
  exited: null
---
''')

    result = scan_incomplete_work(tmp_path)

    assert len(result) == 1
    assert result[0]["id"] == "E2-999"
    assert result[0]["incomplete_node"] == "doing"
```

### Test 4: Log Session Start Event
```python
def test_log_session_start(tmp_path: Path, monkeypatch):
    """Log SessionStarted event to events file."""
    events_file = tmp_path / "events.jsonl"
    monkeypatch.setattr(governance_events, "EVENTS_FILE", events_file)

    event = log_session_start(session_number=245, agent="Hephaestus")

    assert event["type"] == "SessionStarted"
    assert event["session"] == 245
    assert events_file.read_text().strip() != ""
```

### Test 5: Log Session End Event
```python
def test_log_session_end(tmp_path: Path, monkeypatch):
    """Log SessionEnded event to events file."""
    events_file = tmp_path / "events.jsonl"
    monkeypatch.setattr(governance_events, "EVENTS_FILE", events_file)

    event = log_session_end(session_number=245, agent="Hephaestus")

    assert event["type"] == "SessionEnded"
    assert event["session"] == 245
```

### Test 6: Backward Compatibility - Existing Events Still Work
```python
def test_existing_log_phase_transition_unchanged(tmp_path: Path, monkeypatch):
    """Verify log_phase_transition still works as before."""
    events_file = tmp_path / "events.jsonl"
    monkeypatch.setattr(governance_events, "EVENTS_FILE", events_file)

    event = log_phase_transition("PLAN", "E2-236", "Hephaestus")

    assert event["type"] == "CyclePhaseEntered"
    assert event["phase"] == "PLAN"
```

---

## Detailed Design

<!-- REQUIRED: Document HOW the implementation works, not just WHAT it does. -->

### Exact Code Change

**File 1:** `.claude/haios/lib/governance_events.py`
**Location:** After line 86 (after `log_validation_outcome`)

**Add new functions:**
```python
def log_session_start(session_number: int, agent: str) -> dict:
    """
    Log session start event.

    Args:
        session_number: Current session number
        agent: Agent name (e.g., "Hephaestus")

    Returns:
        The logged event dict
    """
    event = {
        "type": "SessionStarted",
        "session": session_number,
        "agent": agent,
        "timestamp": datetime.now().isoformat(),
    }
    _append_event(event)
    return event


def log_session_end(session_number: int, agent: str) -> dict:
    """
    Log session end event.

    Args:
        session_number: Current session number
        agent: Agent name

    Returns:
        The logged event dict
    """
    event = {
        "type": "SessionEnded",
        "session": session_number,
        "agent": agent,
        "timestamp": datetime.now().isoformat(),
    }
    _append_event(event)
    return event


def detect_orphan_session(events_file: Optional[Path] = None) -> Optional[dict]:
    """
    Detect orphan session (started but never ended).

    Scans events for SessionStarted without matching SessionEnded.

    Args:
        events_file: Path to events JSONL (default: EVENTS_FILE constant)

    Returns:
        Dict with orphan_session, current_session if orphan found, else None
    """
    # Use read_events() which reads from EVENTS_FILE, or read custom path for testing
    if events_file is None:
        events = read_events()
    else:
        # For testing: read from custom path
        events = []
        if events_file.exists():
            with open(events_file, encoding="utf-8") as f:
                for line in f:
                    if line.strip():
                        try:
                            events.append(json.loads(line))
                        except json.JSONDecodeError:
                            continue

    # Track session starts and ends
    started = set()
    ended = set()
    latest_start = None

    for e in events:
        if e.get("type") == "SessionStarted":
            started.add(e.get("session"))
            latest_start = e.get("session")
        elif e.get("type") == "SessionEnded":
            ended.add(e.get("session"))

    # Find orphans (started but not ended, excluding current)
    orphans = started - ended
    if latest_start in orphans:
        orphans.discard(latest_start)  # Current session isn't orphan yet

    if orphans:
        orphan_session = max(orphans)  # Most recent orphan
        return {
            "orphan_session": orphan_session,
            "current_session": latest_start,
        }
    return None


def scan_incomplete_work(project_root: Path) -> list[dict]:
    """
    Scan WORK.md files for incomplete transitions (exited: null).

    Per INV-052 Section 2A: Scan for `exited: null` entries in node_history.

    Args:
        project_root: Project root path

    Returns:
        List of dicts with id, incomplete_node, entered_at
    """
    work_dirs = [
        project_root / "docs" / "work" / "active",
        project_root / "docs" / "work" / "blocked",
    ]
    incomplete = []

    for dir_path in work_dirs:
        if not dir_path.exists():
            continue
        for subdir in dir_path.iterdir():
            if not subdir.is_dir():
                continue
            work_file = subdir / "WORK.md"
            if not work_file.exists():
                continue

            content = work_file.read_text(encoding="utf-8", errors="ignore")
            # Parse YAML frontmatter
            match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
            if not match:
                continue

            yaml_content = match.group(1)
            # Check for exited: null in node_history
            if "exited: null" in yaml_content or "exited: ~" in yaml_content:
                # Extract id
                id_match = re.search(r"id:\s*(\S+)", yaml_content)
                # Extract current node
                node_match = re.search(r"node:\s*(\S+)", yaml_content)
                if id_match:
                    incomplete.append({
                        "id": id_match.group(1).strip(),
                        "incomplete_node": node_match.group(1).strip() if node_match else "unknown",
                        "path": str(work_file.relative_to(project_root)),
                    })

    return incomplete
```

**File 2:** `.claude/haios/lib/coldstart_orchestrator.py`
**Location:** Line 72, add recovery phase before other phases

**Current run() method:**
```python
def run(self) -> str:
    output = []
    phases = self.config.get("phases", [])

    for phase in phases:
        # ... existing phase loop
```

**Changed run() method:**
```python
def run(self) -> str:
    output = []

    # PHASE 0: Orphan detection (E2-236)
    recovery_result = self._check_for_orphans()
    if recovery_result:
        output.append("[PHASE: RECOVERY]")
        output.append(recovery_result)
        output.append("\n[BREATHE]\n")

    phases = self.config.get("phases", [])
    # ... rest unchanged
```

**Add helper method:**
```python
def _check_for_orphans(self) -> Optional[str]:
    """
    Check for orphan sessions and incomplete work.

    Returns:
        Warning message if orphans found, else None
    """
    try:
        import sys
        # coldstart_orchestrator.py is in .claude/haios/lib/, so .parent is lib/
        lib_path = str(Path(__file__).parent)
        if lib_path not in sys.path:
            sys.path.insert(0, lib_path)
        from governance_events import detect_orphan_session, scan_incomplete_work

        project_root = Path(__file__).parent.parent.parent.parent
        warnings = []

        # Check for orphan session
        orphan = detect_orphan_session()
        if orphan:
            warnings.append(f"=== ORPHAN SESSION DETECTED ===")
            warnings.append(f"Session {orphan['orphan_session']} started but never ended.")
            warnings.append(f"Current session: {orphan['current_session']}")
            # Log synthetic end for orphan
            from governance_events import log_session_end
            log_session_end(orphan['orphan_session'], "SYNTHETIC_RECOVERY")

        # Check for incomplete work transitions
        incomplete = scan_incomplete_work(project_root)
        if incomplete:
            warnings.append("=== INCOMPLETE WORK DETECTED ===")
            for item in incomplete:
                warnings.append(f"- {item['id']}: stuck in '{item['incomplete_node']}'")

        return "\n".join(warnings) if warnings else None
    except Exception as e:
        logger.warning(f"Orphan detection failed: {e}")
        return None
```

### Call Chain Context

```
just coldstart-orchestrator
    |
    +-> ColdstartOrchestrator.run()
    |       |
    |       +-> _check_for_orphans()  # <-- NEW (E2-236)
    |       |       |
    |       |       +-> detect_orphan_session()
    |       |       +-> scan_incomplete_work()
    |       |       +-> log_session_end() if orphan
    |       |
    |       +-> [PHASE: IDENTITY] -> IdentityLoader
    |       +-> [PHASE: SESSION]  -> SessionLoader
    |       +-> [PHASE: WORK]     -> WorkLoader
    |
    +-> print(output)
```

### Function/Component Signatures

```python
def detect_orphan_session(events_file: Optional[Path] = None) -> Optional[dict]:
    """
    Detect orphan session (started but never ended).

    Args:
        events_file: Path to events JSONL (default: EVENTS_FILE constant)

    Returns:
        Dict with keys:
        - orphan_session: int - The session number that never ended
        - current_session: int - The most recent session start
        Or None if no orphans found.
    """

def scan_incomplete_work(project_root: Path) -> list[dict]:
    """
    Scan WORK.md files for incomplete transitions.

    Args:
        project_root: Project root path

    Returns:
        List of dicts with keys:
        - id: str - Work item ID (e.g., "E2-236")
        - incomplete_node: str - Node with exited: null (e.g., "doing")
        - path: str - Relative path to WORK.md
    """

def log_session_start(session_number: int, agent: str) -> dict:
    """Log SessionStarted event. Returns logged event."""

def log_session_end(session_number: int, agent: str) -> dict:
    """Log SessionEnded event. Returns logged event."""
```

### Behavior Logic

**Current Flow:**
```
coldstart → load identity → load session → load work → [READY]
              (no orphan check)
```

**Fixed Flow:**
```
coldstart → [RECOVERY PHASE?]
                ├─ orphan found → log synthetic end, warn agent
                └─ incomplete work → list items
           → load identity → load session → load work → [READY]
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Where to add session events | governance_events.py | Already handles event logging, consistent pattern |
| Orphan detection location | Before identity phase | Must happen first to inform agent of recovery state |
| Synthetic session-end | Log automatically on detection | Cleans up state so next detection doesn't re-fire |
| Work scan target | active + blocked dirs only | Archive is intentionally closed, not incomplete |
| Pattern: sibling imports | `sys.path` manipulation | Matches session_loader.py:37-40 pattern |

### Input/Output Examples

**Real Example - Current Events:**
```
$ head -3 .claude/governance-events.jsonl
{"type": "CyclePhaseEntered", "phase": "PLAN", "work_id": "E2-108", ...}
{"type": "CyclePhaseEntered", "phase": "DO", "work_id": "E2-108", ...}
```

**After Implementation - With Session Events:**
```
$ head -3 .claude/governance-events.jsonl
{"type": "SessionStarted", "session": 245, "agent": "Hephaestus", ...}
{"type": "CyclePhaseEntered", "phase": "PLAN", "work_id": "E2-236", ...}
...
{"type": "SessionEnded", "session": 245, "agent": "Hephaestus", ...}
```

**Orphan Detection Output:**
```
[PHASE: RECOVERY]
=== ORPHAN SESSION DETECTED ===
Session 244 started but never ended.
Current session: 245

=== INCOMPLETE WORK DETECTED ===
- E2-236: stuck in 'doing'

[BREATHE]

[PHASE: IDENTITY]
...
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No events file exists | Return None (no orphan) | Implied by default behavior |
| Multiple orphans | Return most recent orphan | Test 1 |
| Current session only started | Not counted as orphan | Test 2 |
| Work file with malformed YAML | Skip, continue scanning | Defensive parsing |
| Empty events file | Return None | Graceful degradation |

### Open Questions

**Q: Should we wire session-start/end logging into hooks?**

TBD - For now, implement detection. Wiring `log_session_start` into `just session-start` recipe is a follow-up.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| N/A | - | - | No operator_decisions in work item - design is straightforward |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_orphan_detection.py`
- [ ] Add all 6 tests from Tests First section
- [ ] Verify tests fail (red) - functions don't exist yet

### Step 2: Add Session Event Functions to governance_events.py
- [ ] Add `log_session_start()` function
- [ ] Add `log_session_end()` function
- [ ] Tests 4, 5, 6 pass (green)

### Step 3: Add Detection Functions to governance_events.py
- [ ] Add `detect_orphan_session()` function
- [ ] Add `scan_incomplete_work()` function
- [ ] Tests 1, 2, 3 pass (green)

### Step 4: Wire into ColdstartOrchestrator
- [ ] Add `_check_for_orphans()` helper method
- [ ] Modify `run()` to call orphan check before phases
- [ ] Integration test: run `just coldstart-orchestrator` and verify no errors

### Step 5: Wire Session Logging into Recipes
- [ ] Modify `just session-start` to call `log_session_start()`
- [ ] Add checkpoint hook to call `log_session_end()` (or defer to follow-up work)

### Step 6: Integration Verification
- [ ] Run `pytest tests/test_orphan_detection.py -v` - all pass
- [ ] Run `pytest` - no regressions in existing tests
- [ ] Run `just coldstart-orchestrator` - no errors

### Step 7: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/lib/README.md` to document new functions
- [ ] **MUST:** Verify function list matches actual exports

### Step 8: Runtime Consumer Verification
- [ ] Verify ColdstartOrchestrator imports `detect_orphan_session`
- [ ] Verify `just coldstart-orchestrator` runs detection phase

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| False positive orphan detection | Low | Only flag sessions where a newer session started (clear evidence) |
| Performance: scanning all WORK.md | Low | Only scan active/blocked dirs, not archive |
| Circular import in coldstart_orchestrator | Medium | Use lazy import inside _check_for_orphans method |
| Events file grows unbounded | Low | Future: add rotation (not in scope for E2-236) |

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

**MUST** read `docs/work/active/E2-236/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Add function `detect_orphan_session()` in `.claude/lib/status.py` | [ ] | Function exists and works |
| Check governance-events.jsonl for "start without end" pattern | [ ] | Test 1, 2 pass |
| Scan WORK.md files for `exited: null` node_history entries | [ ] | Test 3 passes |
| Report incomplete work to agent during coldstart | [ ] | Output shows RECOVERY phase |
| Log synthetic session-end event for orphaned session | [ ] | Events file shows synthetic end |
| Wire into ColdstartOrchestrator to run detection before context loading | [ ] | `_check_for_orphans()` called first |
| Test recovery with simulated crash scenarios | [ ] | Tests 1-6 all pass |
| Runtime consumer: ColdstartOrchestrator calls `detect_orphan_session()` | [ ] | Grep confirms import |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/governance_events.py` | Contains log_session_start, log_session_end, detect_orphan_session, scan_incomplete_work | [ ] | |
| `.claude/haios/lib/coldstart_orchestrator.py` | Contains _check_for_orphans() method, run() calls it first | [ ] | |
| `tests/test_orphan_detection.py` | 6 tests exist and pass | [ ] | |
| `.claude/haios/lib/README.md` | **MUST:** Documents new functions | [ ] | |

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

- @docs/work/archive/INV-052/SECTION-2A-SESSION-LIFECYCLE.md (design source, lines 68-76)
- @.claude/haios/lib/governance_events.py (existing event logging)
- @.claude/haios/lib/coldstart_orchestrator.py (integration point)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CONTEXT-001)

---
