---
template: implementation_plan
status: complete
date: 2026-01-26
backlog_id: E2-306
title: Wire Session Event Logging into Lifecycle
author: Hephaestus
lifecycle_phase: plan
session: 246
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-26T23:15:43'
---
# Implementation Plan: Wire Session Event Logging into Lifecycle

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

`just session-start` and `just session-end` will call `log_session_start()` and `log_session_end()` from governance_events.py, enabling orphan session detection to function.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `justfile` |
| Lines of code affected | ~10 | 2 recipe definitions (lines 280-285) |
| New files to create | 0 | Functions exist in governance_events.py |
| Tests to write | 1 | Manual verification (events appear in correct file) |
| Dependencies | 0 | governance_events.py already imports correctly |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Just justfile recipes |
| Risk of regression | Low | Session logging is additive |
| External dependencies | Low | File-based only |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Modify justfile recipes | 10 min | High |
| Verify events file | 5 min | High |
| **Total** | ~15 min | High |

---

## Current State vs Desired State

### Current State

```bash
# justfile:280-281 - session-start recipe
session-start session:
    @python -c "import json,datetime,os; ... open(ef,'a').write(json.dumps({'ts':...,'type':'session','action':'start','session':s})+chr(10)); ..."
```

**Behavior:** Writes events to `.claude/haios-events.jsonl` with simple format `{ts, type: "session", action: "start", session}`

**Result:** `detect_orphan_session()` cannot find events because it reads from `.claude/haios/governance-events.jsonl` and expects `{type: "SessionStarted", ...}`

### Desired State

```bash
# justfile:280-281 - session-start recipe calling governance_events
session-start session:
    @python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from governance_events import log_session_start; log_session_start({{session}}, 'Hephaestus'); print(f'Session {{session}} start logged')"
```

**Behavior:** Calls `log_session_start()` which writes to `.claude/haios/governance-events.jsonl` with correct format

**Result:** `detect_orphan_session()` finds events correctly, enabling orphan detection

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Session Start Event Appears in governance-events.jsonl
```bash
# Manual verification
just session-start 999
cat .claude/haios/governance-events.jsonl | tail -1
# Expected: {"type": "SessionStarted", "session": 999, "agent": "Hephaestus", "timestamp": "..."}
```

### Test 2: Session End Event Appears in governance-events.jsonl
```bash
# Manual verification
just session-end 999
cat .claude/haios/governance-events.jsonl | tail -1
# Expected: {"type": "SessionEnded", "session": 999, "agent": "Hephaestus", "timestamp": "..."}
```

### Test 3: Orphan Detection Works After Wiring
```bash
# Run coldstart after session with events
just session-start 247
# Simulate crash (don't call session-end)
# On next coldstart:
python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from governance_events import detect_orphan_session; print(detect_orphan_session())"
# Expected: {"orphan_session": 247, "current_session": None} or similar
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

**File:** `justfile`
**Location:** Lines 280-285 (session-start and session-end recipes)

**Current Code (session-start):**
```bash
# justfile:280-281
session-start session:
    @python -c "import json,datetime,os; sf='.claude/session'; jf='.claude/haios-status.json'; ef='.claude/haios-events.jsonl'; s={{session}}; lines=open(sf).readlines() if os.path.exists(sf) else []; hdr=[l for l in lines if l.startswith('#')]; open(sf,'w').write(''.join(hdr)+str(s)+chr(10)); j=json.load(open(jf)) if os.path.exists(jf) else {}; pr=j.get('session_delta',{}).get('current_session',s-1); j['session_delta']={'current_session':s,'prior_session':pr}; json.dump(j,open(jf,'w'),indent=2); open(ef,'a').write(json.dumps({'ts':datetime.datetime.now().isoformat(),'type':'session','action':'start','session':s})+chr(10)); print(f'Session {s} start logged')"
```

**Changed Code (session-start):**
```bash
# justfile:280-281 - Add governance_events call
session-start session:
    @python -c "import json,os,sys; sys.path.insert(0,'.claude/haios/lib'); from governance_events import log_session_start; sf='.claude/session'; jf='.claude/haios-status.json'; s={{session}}; lines=open(sf).readlines() if os.path.exists(sf) else []; hdr=[l for l in lines if l.startswith('#')]; open(sf,'w').write(''.join(hdr)+str(s)+chr(10)); j=json.load(open(jf)) if os.path.exists(jf) else {}; pr=j.get('session_delta',{}).get('current_session',s-1); j['session_delta']={'current_session':s,'prior_session':pr}; json.dump(j,open(jf,'w'),indent=2); log_session_start(s,'Hephaestus'); print(f'Session {s} start logged')"
```

**Current Code (session-end):**
```bash
# justfile:284-285
session-end session:
    @python -c "import json,datetime; f=open('.claude/haios-events.jsonl','a'); f.write(json.dumps({'ts':datetime.datetime.now().isoformat(),'type':'session','action':'end','session':{{session}}})+'\n'); print('Session {{session}} end logged')"
```

**Changed Code (session-end):**
```bash
# justfile:284-285 - Call governance_events instead
session-end session:
    @python -c "import sys; sys.path.insert(0,'.claude/haios/lib'); from governance_events import log_session_end; log_session_end({{session}},'Hephaestus'); print('Session {{session}} end logged')"
```

### Call Chain Context

```
ColdstartOrchestrator._check_for_orphans()
    |
    +-> detect_orphan_session()
    |       Reads: .claude/haios/governance-events.jsonl
    |       Expects: {type: "SessionStarted"/"SessionEnded", session, agent, timestamp}
    |
    +-> NOW POPULATED BY:
            just session-start -> log_session_start() -> governance-events.jsonl
            just session-end -> log_session_end() -> governance-events.jsonl
```

### Function/Component Signatures

```python
# governance_events.py:96-114
def log_session_start(session_number: int, agent: str) -> dict:
    """Log session start event to governance-events.jsonl."""

# governance_events.py:117-135
def log_session_end(session_number: int, agent: str) -> dict:
    """Log session end event to governance-events.jsonl."""
```

### Behavior Logic

**Current Flow (broken):**
```
just session-start → writes to .claude/haios-events.jsonl (wrong file)
                   → detect_orphan_session() reads governance-events.jsonl (no events)
                   → Orphan detection never works
```

**Fixed Flow:**
```
just session-start → log_session_start() → .claude/haios/governance-events.jsonl
                   → detect_orphan_session() reads governance-events.jsonl (events present)
                   → Orphan detection works correctly
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Hardcode agent as "Hephaestus" | Yes | Agent name is consistent across sessions; no need for dynamic lookup |
| Keep session file update logic | Yes | Still need to write session number to .claude/session and update haios-status.json |
| Use sys.path.insert | Yes | Consistent with other justfile recipes (e.g., set-cycle at line 290) |

### Input/Output Examples

**Before Fix:**
```bash
$ just session-start 246
Session 246 start logged
$ cat .claude/haios/governance-events.jsonl | grep "SessionStarted" | wc -l
0  # No events!
```

**After Fix:**
```bash
$ just session-start 246
Session 246 start logged
$ cat .claude/haios/governance-events.jsonl | tail -1
{"type": "SessionStarted", "session": 246, "agent": "Hephaestus", "timestamp": "2026-01-26T22:25:00"}
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| First session (no prior events) | log_session_start handles gracefully | Test 1 |
| governance_events.py import fails | Recipe will error with traceback | N/A - fix path if needed |

### Open Questions

**Q: Should we keep writing to old .claude/haios-events.jsonl for backward compat?**

No - the old file format was never used by any consumer. detect_orphan_session() expects the governance-events.jsonl format. Clean break.

---

## Open Decisions (MUST resolve before implementation)

**No open decisions.** Design is straightforward - wire justfile recipes to existing governance_events functions.

---

## Implementation Steps

### Step 1: Modify session-start Recipe
- [ ] Edit justfile line 281 to call log_session_start()
- [ ] Keep session file and haios-status.json update logic
- [ ] Test: `just session-start 999` and verify event in governance-events.jsonl

### Step 2: Modify session-end Recipe
- [ ] Edit justfile line 285 to call log_session_end()
- [ ] Remove old haios-events.jsonl write
- [ ] Test: `just session-end 999` and verify event in governance-events.jsonl

### Step 3: Verify Orphan Detection Works
- [ ] Run detect_orphan_session() after creating events
- [ ] Verify it finds the expected orphan pattern

### Step 4: Full Integration Test
- [ ] Run `just session-start 247` to simulate start of new session
- [ ] Check `.claude/haios/governance-events.jsonl` for SessionStarted event
- [ ] Run coldstart orchestrator, verify no false orphan warnings

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Import failure in justfile | Medium | Use sys.path.insert pattern consistent with other recipes |
| Session number mismatch | Low | Agent name is hardcoded, session from parameter |
| Old events file orphaned | Low | Can clean up later; not breaking anything |

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

**MUST** read `docs/work/active/E2-306/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Modify `just session-start` to call `log_session_start()` | [ ] | Grep justfile for log_session_start |
| Modify `just session-end` to call `log_session_end()` | [ ] | Grep justfile for log_session_end |
| Verify events appear in governance-events.jsonl | [ ] | Cat file and check for SessionStarted/SessionEnded |
| Test: coldstart after session with events | [ ] | Run coldstart, no false orphan detection |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `justfile` | session-start calls log_session_start | [ ] | |
| `justfile` | session-end calls log_session_end | [ ] | |
| `.claude/haios/governance-events.jsonl` | Contains SessionStarted/SessionEnded events | [ ] | |

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

- @docs/work/active/E2-236/plans/PLAN.md (Step 5: Wire Session Logging)
- @.claude/haios/lib/governance_events.py (log_session_start, log_session_end functions)
- @docs/work/active/E2-305/WORK.md (mitigation that renamed this from E2-294)
- Memory 82302: "justfile recipes -> cli.py -> modules is the correct layer stack"

---
