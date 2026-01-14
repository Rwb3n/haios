---
template: implementation_plan
status: complete
date: 2025-12-15
backlog_id: E2-078
title: "Coldstart Work Delta from Checkpoints"
author: Hephaestus
lifecycle_phase: plan
session: 76
parent_plan: E2-076d
spawned_by: E2-076d
related: [E2-076, E2-076d, E2-076e, E2-079, E2-080]
execution_layer: E2-080
version: "1.1"
---
# generated: 2025-12-15
# System Auto: last updated on: 2025-12-17 21:54:06
# Implementation Plan: Coldstart Work Delta from Checkpoints

@docs/README.md
@docs/epistemic_state.md
@docs/plans/PLAN-E2-076d-vitals-injection.md

---

## Goal

Enable agent momentum awareness by reading the last 2 checkpoints and calculating work delta (items completed, items added, milestone progress change), surfacing this in coldstart and storing in haios-status-slim.json for vitals consumption.

---

## Current State vs Desired State

### Current State

```markdown
# .claude/commands/coldstart.md
# Loads latest checkpoint only
Read last checkpoint from docs/checkpoints/
```

**Behavior:** Coldstart reads only the most recent checkpoint. Agent knows WHERE we are.

**Result:** Agent lacks sense of momentum - no awareness of HOW MUCH happened since last session.

### Desired State

```markdown
# .claude/commands/coldstart.md
# Loads last 2 checkpoints, calculates delta
Read last 2 checkpoints from docs/checkpoints/
Calculate: items_completed, items_added, milestone_delta
Output: "Since last session: +3 completed, +2 new, M2: 75%->78%"
```

**Behavior:** Coldstart compares 2 checkpoints and surfaces progress delta.

**Result:** Agent feels momentum: "We completed 3 items, added 2, milestone advanced 3%"

---

## Tests First (TDD)

> Note: Coldstart is a markdown command, not Python. Verification is manual.

### Test 1: Delta Appears in Coldstart Output
```bash
# Run /coldstart
# Expected: Output contains "Since last session:" line with delta stats
```

### Test 2: Delta Stored in haios-status-slim.json
```bash
cat .claude/haios-status-slim.json | grep session_delta
# Expected: session_delta field exists with completed, added, milestone_delta
```

### Test 3: Handles Single Checkpoint (First Session)
```bash
# If only 1 checkpoint exists, delta should show "First session" or similar
# No crash, graceful fallback
```

### Test 4: Vitals Displays Delta
```bash
# After coldstart runs, next prompt should show vitals with:
# Milestone: M2-Governance (78%) [+3]
```

---

## Detailed Design

### Architecture: Current State (No Delta)

```
+---------------------------------------------------------------------+
|                         CURRENT COLDSTART                            |
+---------------------------------------------------------------------+

  Session N starts
       |
       v
+--------------+     +--------------+     +--------------+
|  CLAUDE.md   |---->| epistemic_   |---->|   LATEST     |
|              |     | state.md     |     |  checkpoint  |
+--------------+     +--------------+     +--------------+
                                                 |
                                                 v
                                          +--------------+
                                          | haios-status |
                                          |  -slim.json  |
                                          +--------------+
                                                 |
                                                 v
                                          +--------------+
                                          |   memory     |
                                          |   query      |
                                          +--------------+
                                                 |
                                                 v
                                    +------------------------+
                                    |  OUTPUT: "Session 81   |
                                    |  focused on E2-076e"   |
                                    |                        |
                                    |  (No momentum sense)   |
                                    +------------------------+
```

### Architecture: Proposed State (With Delta)

```
+---------------------------------------------------------------------+
|                       PROPOSED COLDSTART                             |
+---------------------------------------------------------------------+

  Session N starts
       |
       v
+--------------+     +--------------+     +--------------------------+
|  CLAUDE.md   |---->| epistemic_   |---->|  LAST 2 CHECKPOINTS      |
|              |     | state.md     |     |  +--------+ +--------+   |
+--------------+     +--------------+     |  | N-1    | |   N    |   |
                                          |  |(prior) | |(latest)|   |
                                          |  +--------+ +--------+   |
                                          +--------------------------+
                                                       |
                                          +------------+------------+
                                          |    DELTA CALCULATION    |
                                          |                         |
                                          |  Compare:               |
                                          |  - backlog_ids arrays   |
                                          |  - milestone %          |
                                          |  - status changes       |
                                          +-------------------------+
                                                       |
                                                       v
                                          +-------------------------+
                                          |   haios-status-slim     |
                                          |   .json (ENHANCED)      |
                                          |                         |
                                          |  + session_delta: {     |
                                          |      completed: [...]   |
                                          |      added: [...]       |
                                          |      milestone_change:  |
                                          |        "55% -> 60%"     |
                                          |    }                    |
                                          +-------------------------+
                                                       |
                                                       v
                                    +--------------------------------+
                                    |  OUTPUT: "Since Session 81:   |
                                    |  +2 completed (E2-076e, E2-084)|
                                    |  +1 new (E2-090)              |
                                    |  M2: 55% -> 60%"              |
                                    |                                |
                                    |  (MOMENTUM VISIBLE!)           |
                                    +--------------------------------+
```

### Implementation Approach: Hybrid (RECOMMENDED)

```
+--------------------------------------------------------------------+
|  PHASE 1: UpdateHaiosStatus.ps1 calculates & stores delta          |
+--------------------------------------------------------------------+
                                |
         +----------------------+----------------------+
         v                      v                      v
  +-------------+      +-----------------+    +---------------+
  | checkpoint  |      |  checkpoint     |    | haios-status  |
  | SESSION-N   |      |  SESSION-(N-1)  |    | .json (has    |
  | (latest)    |      |  (prior)        |    | last_session) |
  +-------------+      +-----------------+    +---------------+
         |                      |                      |
         |    Parse YAML:       |                      |
         |    - backlog_ids     |                      |
         |    - session #       |                      |
         +----------+-----------+                      |
                    |                                  |
                    v                                  |
         +----------------------+                      |
         |  Compare arrays:     |<---------------------+
         |  completed = items   |
         |    with complete     |
         |    status in plans   |
         |  added = N - (N-1)   |
         +----------------------+
                    |
                    v
         +----------------------------------------------+
         |  haios-status-slim.json                      |
         |                                              |
         |  {                                           |
         |    "session_delta": {                        |
         |      "prior_session": 81,                    |
         |      "current_session": 82,                  |
         |      "completed": ["E2-076e", "E2-084"],    |
         |      "added": ["E2-088", "E2-089", "E2-090"],|
         |      "milestone_delta": "+10%"              |
         |    },                                        |
         |    "milestone": { ... },                     |
         |    ...                                       |
         |  }                                           |
         +----------------------------------------------+

+--------------------------------------------------------------------+
|  PHASE 2: Vitals injection reads & displays delta                  |
+--------------------------------------------------------------------+

         UserPromptSubmit.ps1
                |
                v
         +------------------+
         | Read slim.json   |
         | session_delta    |
         +------------------+
                |
                v
  +-----------------------------------------------------+
  |  --- HAIOS Vitals ---                               |
  |  Milestone: M2-Governance (55%)                     |
  |  Since Session 81: +2 done, +3 new, +10% milestone  |  <-- NEW
  |  Commands: /new-*, /close, /validate, /status       |
  |  ...                                                |
  +-----------------------------------------------------+

+--------------------------------------------------------------------+
|  PHASE 3: coldstart.md surfaces delta prominently                  |
+--------------------------------------------------------------------+

         /coldstart output
                |
                v
  +-----------------------------------------------------+
  |  ## Session 82 Cold Start Summary                   |
  |                                                     |
  |  ### Momentum (Since Session 81)                    |  <-- NEW
  |  - **Completed:** E2-076e, E2-084                  |
  |  - **Added:** E2-088, E2-089, E2-090              |
  |  - **Milestone:** 45% -> 55% (+10%)                |
  |                                                     |
  |  ### Current Phase                                  |
  |  Epoch 2 - Governance Suite (M2: 55%)              |
  |  ...                                                |
  +-----------------------------------------------------+
```

### Delta Calculation Logic (Flowchart)

```
/coldstart triggered
    |
    v
[List checkpoints by date (most recent first)]
    |
    v
[Got >= 2 checkpoints?]
    |-- NO --> Output: "First session - no prior checkpoint"
    |
    YES
    |
    v
[Read checkpoint N (current) and N-1 (prior)]
    |
    v
[Extract from each: backlog_ids, session, date]
    |
    v
[Calculate delta:]
    - completed = items in BOTH where status now complete
    - added = items in N that weren't in N-1
    - milestone_delta = N.milestone_progress - N-1.milestone_progress
    |
    v
[Store delta in haios-status-slim.json]
    |
    v
[Output to coldstart:]
    "Since Session 75: +2 completed, +3 new items, M2: 75%->78%"
```

### Files to Modify

```
+---------------------------------------------------------------------+
|                        FILES TO MODIFY                               |
+---------------------------------------------------------------------+

  1. UpdateHaiosStatus.ps1
     +-- Add: Get-SessionDelta function
     +-- Add: Parse checkpoint YAML for backlog_ids
     +-- Add: Write session_delta to slim.json

  2. haios-status-slim.json (schema change)
     +-- Add: session_delta object

  3. UserPromptSubmit.ps1 (vitals)
     +-- Add: Display delta line if present

  4. coldstart.md
     +-- Add: "Momentum" section instruction
     +-- Add: Read 2 checkpoints instead of 1
```

### Delta Calculation Algorithm

```
  Given:
    checkpoint_N.backlog_ids = [E2-076e, E2-084, E2-088, E2-089, E2-090]
    checkpoint_N-1.backlog_ids = [E2-076d, E2-081, E2-076e, E2-084]

  Calculate:

    completed = items in BOTH checkpoints where status changed to complete
              = items that were in N-1 AND have complete status now
              = [E2-076e, E2-084] (if they show complete in plans/backlog)

    added = items in N but NOT in N-1
          = [E2-088, E2-089, E2-090]

    milestone_delta = slim.milestone.progress - slim.milestone.prior_progress
                    = 55 - 45 = +10%
```

### Checkpoint Frontmatter Fields Used

```yaml
# From checkpoint frontmatter:
session: 75
backlog_ids: [E2-076, E2-076a, E2-076b]  # Items worked on
# Plus status from associated backlog items
```

### haios-status-slim.json Delta Structure

```json
{
  "session_delta": {
    "prior_session": 75,
    "prior_date": "2025-12-14",
    "completed_count": 2,
    "completed_items": ["E2-076b", "E2-076d"],
    "added_count": 3,
    "added_items": ["E2-077", "E2-078", "E2-079"],
    "milestone": {
      "id": "M2",
      "prior_progress": 75,
      "current_progress": 78,
      "delta": 3
    }
  }
}
```

### Vitals Consumption (E2-076d)

UserPromptSubmit reads `session_delta` from slim and formats:
```
Milestone: M2-Governance (78%) [+3 from Session 75]
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Compare 2 checkpoints | Yes | More than 2 adds complexity without proportional value |
| Store delta in slim | Yes | Vitals (E2-076d) needs to read it without recalculating |
| Track item IDs | Yes | Agent can see WHAT completed, not just count |
| Handle 0-1 checkpoints | Graceful fallback | First session shouldn't crash |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| 0 checkpoints | Output: "No checkpoints yet" | Test 3 |
| 1 checkpoint | Output: "First session" | Test 3 |
| No milestone defined | Omit milestone line from delta | - |
| No items changed | Output: "No changes since Session N" | - |

---

## Implementation Steps

### Step 1: Update coldstart.md to Read 2 Checkpoints
- [x] Modify `.claude/commands/coldstart.md`
- [x] Add instruction to read 2 most recent checkpoints (by filename sort)
- [x] Extract: session number, backlog_ids, date from each

### Step 2: Create Delta Calculation Helper (Session 82)
- [x] Added Get-SessionDelta function to UpdateHaiosStatus.ps1
- [x] Added Get-CheckpointData helper to parse YAML frontmatter
- [x] Compare backlog_ids between checkpoints
- [x] Identify: completed (status changed), added (new in current)

### Step 3: Update UpdateHaiosStatus.ps1 for Delta Storage
- [x] Add `session_delta` field to haios-status-slim.json output
- [x] Structure per Detailed Design above
- [x] Run on coldstart to populate delta

### Step 4: Update E2-076d Vitals to Read Delta
- [x] UserPromptSubmit reads `session_delta` from slim
- [x] Format: `Since S80: +2 done, +5 new`
- [x] Handle missing delta gracefully (first session)

### Step 5: Integration Verification
- [x] Run UpdateHaiosStatus.ps1 -Verbose - delta calculated: "80 -> 81, +2 done, +5 new"
- [x] Check haios-status-slim.json - session_delta populated with completed/added arrays
- [x] 208 tests passing

---

## Verification

- [x] /coldstart shows delta line (in output summary format)
- [x] haios-status-slim.json has session_delta field
- [x] Vitals shows delta: `Since S80: +2 done, +5 new`
- [x] Edge cases handled (returns empty delta if < 2 checkpoints)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Checkpoint format varies | Medium | Only extract fields we know exist (session, backlog_ids) |
| Large checkpoint count | Low | Only read 2 most recent, not full history |
| Milestone not defined | Low | Omit milestone delta if not present |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 76 | 2025-12-15 | - | Draft | Plan created |
| 82 | 2025-12-17 | SESSION-82 | Complete | Full implementation with design diagrams |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/commands/coldstart.md` | Reads 2 checkpoints, outputs delta | [x] | Updated lines 18-22 |
| `.claude/haios-status-slim.json` | Has session_delta field | [x] | Lines 2-20 contain session_delta |
| `.claude/hooks/UserPromptSubmit.ps1` | Vitals shows milestone delta | [x] | Lines 65-82 |
| `.claude/hooks/UpdateHaiosStatus.ps1` | Get-SessionDelta function | [x] | Lines 568-705 |

**Verification Commands:**
```bash
# Direct verification (run 2025-12-17)
powershell.exe -ExecutionPolicy Bypass -File UpdateHaiosStatus.ps1 -Verbose
# Output: "Session delta: 80 -> 81, +2 done, +5 new"
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | All 4 files verified |
| Delta appears in slim.json? | Yes | session_delta with completed/added arrays |
| Any deviations from plan? | Minor | Added to UpdateHaiosStatus.ps1 instead of separate script |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Tests pass (208 passing)
- [x] WHY captured (concepts 71891-71900, techne classification)
- [x] Documentation current (coldstart.md updated)
- [x] All traced files complete
- [x] Ground Truth Verification completed above

---

## References

- **Parent Plan:** `docs/plans/PLAN-E2-076d-vitals-injection.md`
- **Consumes:** E2-076d (vitals displays delta this plan calculates)
- **Related:** E2-076 (DAG Governance), E2-079 (CLAUDE.md De-bloat)

---
