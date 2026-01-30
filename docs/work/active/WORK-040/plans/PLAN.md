---
template: implementation_plan
status: complete
date: 2026-01-30
backlog_id: WORK-040
title: Design CH-002 StateDefinitions
author: Hephaestus
lifecycle_phase: plan
session: 267
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-30T23:25:43'
---
# Implementation Plan: Design CH-002 StateDefinitions

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

Formally define the 6 ActivityMatrix states (EXPLORE, DESIGN, PLAN, DO, CHECK, DONE) with schemas, transitions, detection logic, and failure modes so GovernanceLayer can implement state-aware governance.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 0 | Design chapter only |
| Lines of code affected | 0 | No code changes - this is a design document |
| New files to create | 1 | `.claude/haios/epochs/E2_4/arcs/activities/CH-002-StateDefinitions.md` |
| Tests to write | 0 | Design document, tests come in CH-003/CH-004 |
| Dependencies | 1 | CH-001 ActivityMatrix (input spec) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Design doc only, no code integration |
| Risk of regression | Low | No code changes |
| External dependencies | Low | Only depends on CH-001 design |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| State Schema Design | 20 min | High |
| Transition Rules | 15 min | High |
| Detection Logic | 15 min | High |
| Investigation Variant | 10 min | High |
| Failure Modes | 10 min | High |
| **Total** | ~70 min | High |

---

## Current State vs Desired State

### Current State

CH-001 ActivityMatrix (lines 91-101) has preliminary state definitions:

```markdown
## State Definitions

| State | Phase | Purpose | Default Posture |
|-------|-------|---------|-----------------|
| `EXPLORE` | Discovery | Gather information freely | Permissive |
| `DESIGN` | Requirements → Spec | Define what to build | Permissive |
| `PLAN` | Spec → Implementation plan | Define how to build | Permissive |
| `DO` | Plan → Artifact | Execute the plan | **Restrictive** |
| `CHECK` | Artifact → Verdict | Verify correctness | Permissive |
| `DONE` | Closure | Archive and memory | Permissive |
```

**Behavior:** States are listed but not formally defined

**Result:** GovernanceLayer cannot implement state-aware governance because:
- No schema for state object (what fields does a state have?)
- No entry/exit conditions (when can we enter/leave a state?)
- No transition rules (what transitions are valid/forbidden?)
- No detection algorithm (how do we determine current state?)

### Desired State

Formal state definitions in YAML schema:

```yaml
# .claude/haios/epochs/E2_4/arcs/activities/CH-002-StateDefinitions.md
# Example state definition schema

states:
  EXPLORE:
    name: EXPLORE
    posture: permissive
    purpose: "Gather information freely"
    entry_conditions:
      - "No preconditions (can enter from any permissive state)"
    exit_conditions:
      - "Discovery objectives satisfied OR moving to design"
    valid_transitions_to: [DESIGN]
    allowed_activities: [explore-read, explore-search, explore-memory, capture-notes]
    blocked_activities: []
```

**Behavior:** Each state has formal schema with entry/exit conditions and allowed transitions

**Result:** GovernanceLayer can implement `get_activity_state()` and `check_activity()` using these definitions

---

## Tests First (TDD)

**SKIPPED:** This is a design document work item (type: design). Tests will be written in CH-003 GovernanceRules and CH-004 PreToolUseIntegration when the state definitions are implemented in code.

**Verification for this design work:**
- Design document review (critique agent)
- Schema completeness check (all 6 states defined)
- Transition graph coverage (all valid paths documented)

---

## Detailed Design

### Deliverable 1: State Object Schema

Each state MUST have the following fields (per memory 78901):

```yaml
# State schema definition
state_schema:
  name: string           # State identifier (EXPLORE, DESIGN, PLAN, DO, CHECK, DONE)
  posture: enum          # permissive | restrictive
  purpose: string        # One-line description of state's role
  entry_conditions:      # List of conditions that MUST be true to enter
    - string
  exit_conditions:       # List of conditions that MUST be true to exit
    - string
  valid_transitions_to:  # States this state can transition to
    - state_name
  allowed_activities:    # Governed activities permitted in this state
    - activity_name
  blocked_activities:    # Governed activities blocked in this state
    - activity_name
```

### Deliverable 2: State Transition Diagram

**Implementation Flow:**
```
EXPLORE ──→ DESIGN ──→ PLAN ──→ DO ──→ CHECK ──→ DONE
   ↑          ↑         ↑       │       │
   └──────────┴─────────┴───────┘       │
          (backtrack allowed)           │
                                        ↓
                                    [terminal]
```

**Investigation Flow:** (per CH-001: HYPOTHESIZE→EXPLORE→CONCLUDE)
```
HYPOTHESIZE ──→ EXPLORE ──→ CONCLUDE
      │            │
      └────────────┘
   (iteration allowed)
```
Note: Investigation inverts the flow - hypothesize first, then explore to validate.

**Forbidden Transitions:**
- DO → EXPLORE (can't restart discovery mid-implementation)
- DONE → any (terminal state)
- Any → DO without passing through PLAN (must have plan first)

### Deliverable 3: State Detection Logic

Algorithm for `get_activity_state()`:

```python
def get_activity_state() -> str:
    """
    Determine current ActivityMatrix state from cycle phase.

    Returns:
        State name: EXPLORE, DESIGN, PLAN, DO, CHECK, or DONE
    """
    # 1. Get current cycle/phase from session state
    cycle_info = run_command("just get-cycle")  # Returns "cycle/phase/work_id"

    # 2. Handle failure modes (per CH-001 Critique A1)
    if not cycle_info or cycle_info.strip() == "":
        return "EXPLORE"  # Permissive fallback

    # 3. Parse cycle/phase
    try:
        parts = cycle_info.strip().split("/")
        cycle, phase = parts[0], parts[1]
    except (IndexError, ValueError):
        log_warning(f"Malformed cycle info: {cycle_info}")
        return "EXPLORE"  # Permissive fallback

    # 4. Map to ActivityMatrix state using phase_to_state mapping
    state = PHASE_TO_STATE_MAPPING.get((cycle, phase))

    if state is None:
        log_warning(f"Unknown phase mapping: {cycle}/{phase}")
        return "EXPLORE"  # Permissive fallback

    return state
```

### Deliverable 4: Phase-to-State Mapping Tables

From CH-001 ActivityMatrix (lines 104-153), consolidated:

```yaml
phase_to_state_mapping:
  # implementation-cycle
  implementation-cycle/PLAN: PLAN
  implementation-cycle/DO: DO
  implementation-cycle/CHECK: CHECK
  implementation-cycle/DONE: DONE

  # investigation-cycle (per CH-001: HYPOTHESIZE→EXPLORE→CONCLUDE)
  investigation-cycle/HYPOTHESIZE: DESIGN
  investigation-cycle/EXPLORE: EXPLORE
  investigation-cycle/CONCLUDE: DONE

  # close-work-cycle
  close-work-cycle/VALIDATE: CHECK
  close-work-cycle/OBSERVE: DONE
  close-work-cycle/ARCHIVE: DONE
  close-work-cycle/MEMORY: DONE

  # observation-triage-cycle
  observation-triage-cycle/SCAN: EXPLORE
  observation-triage-cycle/TRIAGE: DESIGN
  observation-triage-cycle/PROMOTE: DONE

  # work-creation-cycle
  work-creation-cycle/VERIFY: CHECK
  work-creation-cycle/POPULATE: DESIGN
  work-creation-cycle/READY: CHECK
  work-creation-cycle/CHAIN: DONE

  # plan-authoring-cycle
  plan-authoring-cycle/AMBIGUITY: DESIGN
  plan-authoring-cycle/ANALYZE: EXPLORE
  plan-authoring-cycle/AUTHOR: DESIGN
  plan-authoring-cycle/VALIDATE: CHECK
  plan-authoring-cycle/CHAIN: DONE

  # checkpoint-cycle (Critique A2 - was missing)
  checkpoint-cycle/SCAFFOLD: DESIGN
  checkpoint-cycle/FILL: DO
  checkpoint-cycle/VERIFY: CHECK
  checkpoint-cycle/CAPTURE: DONE
  checkpoint-cycle/COMMIT: DONE

  # survey-cycle (Critique A2 - was missing)
  survey-cycle/GATHER: EXPLORE
  survey-cycle/ASSESS: DESIGN
  survey-cycle/OPTIONS: DESIGN
  survey-cycle/CHOOSE: PLAN
  survey-cycle/ROUTE: DONE

  # ground-cycle (Critique A2 - was missing)
  ground-cycle/PROVENANCE: EXPLORE
  ground-cycle/ARCHITECTURE: EXPLORE
  ground-cycle/MEMORY: EXPLORE
  ground-cycle/CONTEXT_MAP: EXPLORE

  # plan-validation-cycle (added for completeness)
  plan-validation-cycle/GATE1: CHECK
  plan-validation-cycle/GATE2: CHECK
  plan-validation-cycle/GATE3: CHECK
  plan-validation-cycle/GATE4: CHECK
```

### Deliverable 5: Failure Mode Handling

From CH-001 Critique A1, formalized:

| Failure Mode | Detection | Behavior | Rationale |
|--------------|-----------|----------|-----------|
| `just get-cycle` returns empty | `result.strip() == ""` | State = EXPLORE | No cycle = discovery mode |
| `just get-cycle` returns malformed | Parse fails | State = EXPLORE + log warning | Fail-permissive, don't halt work |
| Phase not in mapping table | Lookup returns None | State = EXPLORE + log warning | Unknown phase = treat as exploration |
| Work file missing/corrupted | File read fails | State = EXPLORE + log warning | Can't determine context, allow exploration |
| Subprocess timeout | Command hangs | State = EXPLORE + log warning | Don't block on infrastructure |

**Design Principle:** Fail-permissive on state detection. Blocking on unknown state halts all work.

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| State stored as data, not code | YAML in chapter file | Data-driven governance is more maintainable than hardcoded rules (per CH-001 line 335-337) |
| Fail-permissive on detection errors | Return EXPLORE on failure | Blocking on unknown state would halt all work (per CH-001 Critique A1) |
| Include phase-to-state mapping upfront | Yes, in design doc | Memory 82772: "Phase-to-state mapping is non-obvious. Include mapping tables upfront." |
| Entry/exit conditions per state | Explicit in schema | Memory 78901: "Each phase SHOULD define entry conditions, guardrails, exit criteria" |
| Investigation maps to ActivityMatrix states | HYPOTHESIZE→DESIGN, EXPLORE→EXPLORE, CONCLUDE→DONE | Reuse existing state definitions rather than create parallel system |

### Edge Cases

| Case | Handling | Documentation |
|------|----------|---------------|
| Multiple cycles active | Not supported - only one cycle at a time | `just get-cycle` returns single value |
| Nested subagent state | Subagents operate independently; state not inherited | Subagents spawned via Task() have fresh context |
| State during checkpoint | DONE (closure activity) | Checkpointing is a closure activity |
| State before coldstart | EXPLORE (default) | No session = discovery mode |

### Clarifications (per Critique A5, A9)

**Subagent State (A5):** Subagents spawned via `Task()` do NOT inherit parent state. They run in isolated context. If state-aware governance is needed in subagents, the parent must pass state explicitly in the prompt. This is a known v1 limitation.

**Entry/Exit Condition Enforcement (A9):** Entry and exit conditions in the state schema are **documentation only** for v1. They inform human understanding and future validation. They are NOT enforced at runtime. Future enhancement may add soft gates (warning) or hard gates (block) based on these conditions.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| N/A | - | - | No unresolved operator decisions in WORK-040 frontmatter |

---

## Implementation Steps

### Step 1: Create Chapter File Structure
- [ ] Create `.claude/haios/epochs/E2_4/arcs/activities/CH-002-StateDefinitions.md`
- [ ] Add standard chapter header (generated timestamp, chapter ID, arc, status)

### Step 2: Define State Object Schema
- [ ] Document schema fields: name, posture, purpose, entry_conditions, exit_conditions, valid_transitions_to, allowed_activities, blocked_activities
- [ ] Provide schema as YAML example

### Step 3: Define All 6 States
- [ ] EXPLORE: entry/exit conditions, allowed transitions, activities
- [ ] DESIGN: entry/exit conditions, allowed transitions, activities
- [ ] PLAN: entry/exit conditions, allowed transitions, activities
- [ ] DO: entry/exit conditions, allowed transitions, activities (restrictive)
- [ ] CHECK: entry/exit conditions, allowed transitions, activities
- [ ] DONE: entry/exit conditions, allowed transitions, activities (terminal)

### Step 4: Document State Transition Diagram
- [ ] Implementation flow: EXPLORE→DESIGN→PLAN→DO→CHECK→DONE
- [ ] Investigation flow: EXPLORE→HYPOTHESIZE→VALIDATE→CONCLUDE
- [ ] Document forbidden transitions with rationale

### Step 5: Document Phase-to-State Mapping
- [ ] Consolidate mappings from CH-001 into single reference table
- [ ] Add plan-authoring-cycle mapping (was missing from CH-001)
- [ ] Document default state when no cycle active

### Step 6: Document State Detection Algorithm
- [ ] Pseudocode for `get_activity_state()`
- [ ] Integration with `just get-cycle`
- [ ] Error handling and fallback behavior

### Step 7: Document Failure Mode Handling
- [ ] Table of failure modes, detection, behavior, rationale
- [ ] Explain fail-permissive principle

### Step 8: Invoke Critique Agent
- [ ] Run critique-agent on completed design
- [ ] Address any blocking assumptions
- [ ] Revise until PROCEED verdict

### Step 9: Update References
- [ ] Add memory_refs from this session
- [ ] Link to CH-001 ActivityMatrix
- [ ] Link to WORK-040

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment with CH-001 | Medium | Reference CH-001 explicitly for all state/activity definitions |
| Missing phase mapping | High | Check all existing cycle skills for phases, add to mapping table |
| Investigation variant incomplete | Medium | Verify against investigation-cycle skill phases |
| Design too abstract for implementation | High | Include concrete pseudocode for `get_activity_state()` |
| Scope creep into implementation | Low | This is design only - implementation is CH-003/CH-004 |

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

**MUST** read `docs/work/active/WORK-040/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| State Object Schema | [ ] | CH-002 contains YAML schema definition |
| State Transition Diagram | [ ] | CH-002 contains implementation + investigation flow diagrams |
| State Detection Logic | [ ] | CH-002 contains `get_activity_state()` algorithm |
| Investigation Variant | [ ] | CH-002 contains EXPLORE→HYPOTHESIZE→VALIDATE→CONCLUDE mapping |
| Failure Mode Handling | [ ] | CH-002 contains failure mode table with behaviors |
| CH-002-StateDefinitions.md | [ ] | File exists at expected path |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/epochs/E2_4/arcs/activities/CH-002-StateDefinitions.md` | Chapter file with all 6 state definitions | [ ] | |
| `docs/work/active/WORK-040/WORK.md` | Deliverables marked complete | [ ] | |

**Verification Commands:**
```bash
# Verify chapter file exists and has content
Read .claude/haios/epochs/E2_4/arcs/activities/CH-002-StateDefinitions.md
# Expected: File with State Definitions header, 6 states defined
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Critique agent invoked and passed? | [Yes/No] | |
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

## Critique Response (Session 267)

| Blocking Issue | Resolution |
|----------------|------------|
| A2: Incomplete phase-to-state mapping | Added 4 missing cycles: checkpoint-cycle, survey-cycle, ground-cycle, plan-validation-cycle |
| A3: Investigation flow inconsistency | Corrected diagram to HYPOTHESIZE→EXPLORE→CONCLUDE per CH-001 |

| Non-Blocking Addressed | Resolution |
|------------------------|------------|
| A5: Subagent state inheritance | Clarified: subagents operate independently, v1 limitation |
| A9: Entry/exit condition enforcement | Clarified: documentation only for v1 |

---

## References

- @.claude/haios/epochs/E2_4/arcs/activities/CH-001-ActivityMatrix.md (source spec)
- @.claude/haios/epochs/E2_4/arcs/activities/ARC.md (parent arc)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-ACTIVITY-001, REQ-FLOW-001, REQ-FLOW-002)
- @.claude/haios/modules/governance_layer.py (consumer module)
- Memory 78901: Phase entry/exit condition pattern
- Memory 82772: Phase-to-state mapping lesson learned

---
