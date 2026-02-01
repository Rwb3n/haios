# generated: 2026-01-30
# System Auto: last updated on: 2026-01-30T23:23:11
# Chapter: StateDefinitions

## Definition

**Chapter ID:** CH-002
**Arc:** activities
**Status:** Draft
**Depends:** CH-001 ActivityMatrix (defines what states govern)
**Enables:** CH-003 GovernanceRules (rules need formal state definitions)

---

## Problem

CH-001 ActivityMatrix defines states at a high level but lacks formal specifications needed for implementation. To implement state-aware governance in GovernanceLayer, we need:
1. **Formal state object schema** - What fields define a state?
2. **Entry/exit conditions** - What must be true to enter/exit each state?
3. **State transition rules** - Valid transitions, forbidden transitions
4. **State detection logic** - How does `get_activity_state()` determine current state?
5. **Failure mode handling** - What happens when state cannot be determined?

---

## State Object Schema

Each state MUST have the following fields:

```yaml
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

---

## State Definitions

### EXPLORE

```yaml
EXPLORE:
  name: EXPLORE
  posture: permissive
  purpose: "Gather information freely without commitment"
  entry_conditions:
    - "No preconditions (can enter from any permissive state)"
    - "Default state when no cycle active"
  exit_conditions:
    - "Discovery objectives satisfied"
    - "Ready to commit to design direction"
  valid_transitions_to:
    - DESIGN
  allowed_activities:
    - explore-read
    - explore-search
    - explore-memory
    - capture-notes
    - web-fetch
    - web-search
    - task-spawn
    - skill-invoke
    - user-query
    - memory-search
  blocked_activities: []
```

### DESIGN

```yaml
DESIGN:
  name: DESIGN
  posture: permissive
  purpose: "Define what to build (requirements to specification)"
  entry_conditions:
    - "EXPLORE phase complete or skipped with rationale"
    - "Requirements understood"
  exit_conditions:
    - "Specification document created"
    - "Design decisions documented with rationale"
  valid_transitions_to:
    - EXPLORE  # Backtrack allowed
    - PLAN
  allowed_activities:
    - requirements-read
    - spec-write
    - critique-invoke
    - explore-read
    - explore-search
    - explore-memory
    - user-query
    - memory-search
    - web-fetch
    - web-search
  blocked_activities: []
```

### PLAN

```yaml
PLAN:
  name: PLAN
  posture: permissive
  purpose: "Define how to build (specification to implementation plan)"
  entry_conditions:
    - "DESIGN phase complete"
    - "Specification exists and is stable"
  exit_conditions:
    - "Implementation plan created with steps"
    - "Critique verdict = PROCEED (hard gate)"
  valid_transitions_to:
    - DESIGN  # Backtrack allowed
    - DO
  allowed_activities:
    - scope-read
    - plan-write
    - critique-invoke
    - explore-read
    - explore-search
    - user-query
    - memory-search
  blocked_activities: []
```

### DO

```yaml
DO:
  name: DO
  posture: restrictive
  purpose: "Execute the plan (plan to artifact)"
  entry_conditions:
    - "PLAN phase complete"
    - "Plan has status: approved"
    - "Critique verdict = PROCEED (hard gate)"
    - "Preflight check passed"
  exit_conditions:
    - "All implementation steps complete"
    - "Artifacts created per plan"
  valid_transitions_to:
    - PLAN   # Backtrack to revise plan if needed
    - CHECK
  allowed_activities:
    - spec-read
    - artifact-write
    - artifact-edit
    - build-execute
    - test-execute
    - task-spawn
  blocked_activities:
    - user-query          # "Spec should be complete - no user queries"
    - memory-search       # "Discovery phase is over"
    - web-fetch           # "No external exploration"
    - web-search          # "No external exploration"
    - explore-read        # "Discovery phase is over"
    - explore-search      # "Discovery phase is over"
    - explore-memory      # "Discovery phase is over"
    - spec-write          # "Design is frozen"
    - critique-invoke     # "Design-phase skill"
```

### CHECK

```yaml
CHECK:
  name: CHECK
  posture: permissive
  purpose: "Verify correctness (artifact to verdict)"
  entry_conditions:
    - "DO phase complete"
    - "Artifacts exist to verify"
  exit_conditions:
    - "All tests pass"
    - "Ground truth verification complete"
    - "All WORK.md deliverables verified"
  valid_transitions_to:
    - DO     # Return to fix issues
    - DONE
  allowed_activities:
    - verify-read
    - test-execute
    - verdict-write
    - explore-read
    - explore-search
    - user-query
    - memory-search
  blocked_activities: []
```

### DONE

```yaml
DONE:
  name: DONE
  posture: permissive
  purpose: "Closure (archive and memory)"
  entry_conditions:
    - "CHECK phase complete"
    - "All verification criteria met"
  exit_conditions:
    - "WHY captured to memory"
    - "Work item closed"
  valid_transitions_to: []  # Terminal state
  allowed_activities:
    - learning-capture
    - archive-update
    - memory-store
    - explore-read
  blocked_activities: []
```

---

## State Transition Diagram

### Implementation Flow

```
EXPLORE ──→ DESIGN ──→ PLAN ──→ DO ──→ CHECK ──→ DONE
   ↑          ↑         ↑       │       │
   └──────────┴─────────┴───────┘       │
          (backtrack allowed)           │
                                        ↓
                                    [terminal]
```

**Critique Hard Gates:**
- DESIGN → PLAN: Critique verdict must = PROCEED
- PLAN → DO: Critique verdict must = PROCEED
- Revise until no blocking critique

### Investigation Flow

```
EXPLORE ──→ HYPOTHESIZE ──→ VALIDATE ──→ CONCLUDE
   ↑              │
   └──────────────┘
    (iteration allowed)
```

Note: Investigation uses EXPLORE-FIRST pattern (E2.4 Decision). HYPOTHESIZE maps to DESIGN state, VALIDATE maps to CHECK state, CONCLUDE maps to DONE state.

### Forbidden Transitions

| From | To | Reason |
|------|-----|--------|
| DO | EXPLORE | Can't restart discovery mid-implementation - design is frozen |
| DONE | any | Terminal state - no transitions out |
| any | DO | Must pass through PLAN first (must have approved plan) |

---

## State Detection Logic

### Algorithm: get_activity_state()

```python
def get_activity_state() -> str:
    """
    Determine current ActivityMatrix state from cycle phase.

    Returns:
        State name: EXPLORE, DESIGN, PLAN, DO, CHECK, or DONE
    """
    # 1. Get current cycle/phase from session state
    cycle_info = run_command("just get-cycle")  # Returns "cycle/phase/work_id"

    # 2. Handle failure modes (fail-permissive)
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

### Phase-to-State Mapping

```yaml
phase_to_state_mapping:
  # implementation-cycle
  implementation-cycle/PLAN: PLAN
  implementation-cycle/DO: DO
  implementation-cycle/CHECK: CHECK
  implementation-cycle/DONE: DONE

  # investigation-cycle (EXPLORE-FIRST per E2.4)
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

  # checkpoint-cycle
  checkpoint-cycle/SCAFFOLD: DESIGN
  checkpoint-cycle/FILL: DO
  checkpoint-cycle/VERIFY: CHECK
  checkpoint-cycle/CAPTURE: DONE
  checkpoint-cycle/COMMIT: DONE

  # survey-cycle
  survey-cycle/GATHER: EXPLORE
  survey-cycle/ASSESS: DESIGN
  survey-cycle/OPTIONS: DESIGN
  survey-cycle/CHOOSE: PLAN
  survey-cycle/ROUTE: DONE

  # ground-cycle
  ground-cycle/PROVENANCE: EXPLORE
  ground-cycle/ARCHITECTURE: EXPLORE
  ground-cycle/MEMORY: EXPLORE
  ground-cycle/CONTEXT_MAP: EXPLORE

  # plan-validation-cycle
  plan-validation-cycle/GATE1: CHECK
  plan-validation-cycle/GATE2: CHECK
  plan-validation-cycle/GATE3: CHECK
  plan-validation-cycle/GATE4: CHECK
```

### Default State

When `just get-cycle` returns empty or error: **State = EXPLORE** (permissive fallback)

Rationale: No cycle active = discovery mode. Agent can explore freely.

---

## Failure Mode Handling

| Failure Mode | Detection | Behavior | Rationale |
|--------------|-----------|----------|-----------|
| `just get-cycle` returns empty | `result.strip() == ""` | State = EXPLORE | No cycle = discovery mode |
| `just get-cycle` returns malformed | Parse fails | State = EXPLORE + log warning | Fail-permissive, don't halt work |
| Phase not in mapping table | Lookup returns None | State = EXPLORE + log warning | Unknown phase = treat as exploration |
| Work file missing/corrupted | File read fails | State = EXPLORE + log warning | Can't determine context, allow exploration |
| Subprocess timeout | Command hangs | State = EXPLORE + log warning | Don't block on infrastructure |

**Design Principle:** Fail-permissive on state detection errors. Blocking on unknown state would halt all work.

---

## Investigation Variant Mapping

Investigation cycle uses different phase names but maps to ActivityMatrix states:

| Investigation Phase | ActivityMatrix State | Rationale |
|--------------------|--------------------|-----------|
| EXPLORE | EXPLORE | Direct mapping - discovery phase |
| HYPOTHESIZE | DESIGN | Hypothesis is a spec-like output |
| VALIDATE | CHECK | Evidence gathering and verification |
| CONCLUDE | DONE | Terminal with findings capture |

Note: E2.4 Decision - Investigation is EXPLORE-FIRST. Hypothesis comes after initial exploration, not before.

---

## Clarifications

### Subagent State (v1 Limitation)

Subagents spawned via `Task()` do NOT inherit parent state. They run in isolated context. If state-aware governance is needed in subagents, the parent must pass state explicitly in the prompt.

This is a known v1 limitation. Future enhancement may add state propagation.

### Entry/Exit Condition Enforcement (v1)

Entry and exit conditions in the state schema are **documentation only** for v1. They inform human understanding and future validation. They are NOT enforced at runtime.

Future enhancement may add:
- Soft gates (warning) for condition violations
- Hard gates (block) for critical transitions

---

## Exit Criteria

- [x] State Object Schema defined
- [x] All 6 states formally defined (EXPLORE, DESIGN, PLAN, DO, CHECK, DONE)
- [x] State Transition Diagram documented (implementation + investigation flows)
- [x] Forbidden transitions documented with rationale
- [x] State Detection Logic algorithm provided
- [x] Phase-to-State Mapping complete (10 cycles covered)
- [x] Failure Mode Handling defined (5 modes)
- [x] Investigation Variant mapping documented
- [x] Clarifications for v1 limitations

---

## Memory Refs

Session 265 governed activities decision: 82706-82710
Session 266 ActivityMatrix design: 82745-82751
Session 267 plan authoring: 82777-82782
Session 268 state definitions: (to be added after ingester_ingest)

---

## References

- @.claude/haios/epochs/E2_4/arcs/activities/CH-001-ActivityMatrix.md (source spec)
- @.claude/haios/epochs/E2_4/arcs/activities/ARC.md (parent arc)
- @.claude/haios/epochs/E2_4/EPOCH.md (epoch decisions)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-ACTIVITY-001, REQ-FLOW-001, REQ-FLOW-002)
- @docs/work/active/WORK-040/WORK.md (work item)
- @docs/work/active/WORK-040/plans/PLAN.md (implementation plan)
