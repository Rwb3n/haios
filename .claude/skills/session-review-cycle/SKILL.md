---
name: session-review-cycle
type: ceremony
description: "Per-session execution quality reflection. Aggregates across all work items
  touched in a session to surface cross-item patterns. Conditional automatic — runs
  only when substantial work was completed."
category:
  - feedback
  - session
input_contract:
  - field: session_number
    type: integer
    required: true
    description: "Current session number from .claude/session"
  - field: session_events
    type: list
    required: true
    description: "Structured events from .claude/haios/session-log.jsonl"
  - field: retro_outputs
    type: list
    required: false
    description: "Per-work-item retro findings from memory (retro-reflect/retro-kss provenance). Queried by work IDs from session events. Degradation: if query returns zero results, log SessionReviewDegradedNoRetroData and proceed with session events only."
  - field: work_items_touched
    type: list
    required: true
    description: "List of work IDs active this session, derived from session events (phase, close, spawn events)"
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: "Whether ceremony completed"
  - field: session_insights
    type: list
    guaranteed: on_success
    description: "Cross-work-item observations (distinct from per-item retro)"
  - field: execution_quality
    type: string
    guaranteed: on_success
    description: "Brief assessment: smooth / friction / blocked"
  - field: process_proposals
    type: list
    guaranteed: on_success
    description: "Proposed process changes (input for Process Review if chained)"
  - field: memory_concept_ids
    type: list
    guaranteed: on_success
    description: "Concept IDs from STORE phase"
  - field: error
    type: string
    guaranteed: on_failure
    description: "Error description"
side_effects:
  - "Store session-level insights to memory (session-review:{session} provenance)"
  - "Log SessionReviewCompleted governance event"
  - "Offer Process Review to operator if process_proposals is non-empty"
generated: 2026-02-23
last_updated: 2026-02-23
---
# Session Review Cycle

Per-session execution quality reflection. Aggregates across all work items touched in a session. Answers: "How did execution go?"

## When to Use

**Conditional automatic** — triggered at session end when computable predicate passes.
**Manual invocation:** `Skill(skill="session-review-cycle")` for explicit operator-initiated review.

---

## Trigger Predicate

Computable predicate checks (OR logic):
- At least 1 work item CLOSED this session (retro-cycle completed, `WorkClosed` event in session-log.jsonl)
- OR at least 2 `RetroCycleCompleted` events in governance-events.jsonl for this session

If predicate fails: skip with governance event `SessionReviewSkipped`. Never blocks session-end.

**Note:** The predicate requires retro-cycle completion, not just CHECK/DONE phase entry, because retro output is the primary evidence source for the ASSESS phase.

---

## The Cycle

```
session-end flow
  |
  +-> [Trigger predicate check]
  |     fails? -> SessionReviewSkipped, skip to session-end-ceremony
  |     passes? -> continue
  |
  +-> Phase 1: GATHER
  |     Read session events, query retro outputs, identify work items touched
  |
  +-> Phase 2: ASSESS
  |     Cross-item pattern synthesis (exclusion rule: no per-item restating)
  |
  +-> Phase 3: STORE
  |     Persist to memory, log governance event
  |
  +-> [Process Review offer if proposals non-empty]
  |     Operator accepts? -> process-review-cycle
  |     Operator declines? -> continue to session-end
  |
  +-> session-end-ceremony (mechanical)
```

---

## Phase 1: GATHER

Collect evidence sources for this session.

### Evidence Sources

1. **Session events:** Read `.claude/haios/session-log.jsonl` for structured event history (phase transitions, commits, test results, work spawns, closures)
2. **Retro outputs:** Query memory for `retro-reflect:{work_id}` and `retro-kss:{work_id}` provenance, where work_id comes from session events. Use `source_adr LIKE 'retro-reflect:%'` filtered to work IDs from session events.
3. **Work items touched:** Extract from session events — any work ID that appears in phase, close, or spawn events

### Degradation

- If session-log.jsonl is empty or missing: log `SessionReviewDegradedNoSessionLog`, ceremony aborts (session events are MUST)
- If retro outputs query returns zero results: log `SessionReviewDegradedNoRetroData`, proceed with session events only. ASSESS phase operates in lightweight mode
- If work_items_touched is empty (no work events): predicate should have caught this; abort as safety net

---

## Phase 2: ASSESS

Synthesize cross-work-item patterns from GATHER evidence.

### Exclusion Rule (MUST)

**Do NOT restate individual work-item findings already captured in retro.** Identify patterns that emerge from viewing the session as a whole:
- Execution flow quality (time allocation across work items, context management)
- Cross-item dependencies discovered during session
- Session-level decisions (work selection, priority shifts)
- Tooling friction or ceremony overhead experienced
- Unexpected interactions between work items

If only 1 work item was closed, focus on session execution quality (time allocation, ceremony overhead, context management) rather than work-item content.

### Output Categories

| Category | Question | Example |
|----------|----------|---------|
| Execution quality | How smoothly did the session flow? | "smooth: single work item, TDD first-pass, no ceremony friction" |
| Cross-item insight | What patterns emerged across items? | "Both WORK-102 and WORK-165 needed ceremony contract knowledge — batch these" |
| Process proposal | What should change in the process? | "Session Review trigger should also fire on investigation closure" |

### Proportional Scaling

| Scale | Behavior |
|-------|----------|
| Single work item closed | Lightweight: 1-2 session-level observations, execution quality assessment |
| Multiple work items / complex session | Full: cross-item patterns, execution quality, process proposals |

---

## Phase 3: STORE

Persist session review outputs to memory with typed provenance.

### Storage

```
ingester_ingest(
  content="Session {N} Review\nExecution: {quality}\nInsights:\n{insights}\nProposals:\n{proposals}",
  source_path="session-review:{session_number}",
  content_type_hint="techne"
)
```

### Governance Event

Log ceremony completion:
```
SessionReviewCompleted: session={N}, insights_count={N}, proposals_count={N}, execution_quality={quality}
```

### Process Review Offer

If `process_proposals` is non-empty, present to operator:

```
Session Review surfaced {N} process proposal(s):
{list proposals briefly}

Run Process Review now? (Invoke /process-review later if preferred)
```

Use `AskUserQuestion` to get operator response. If declined, proposals remain in memory for future standalone invocation. Session-end-ceremony proceeds regardless.

### Degradation

- If memory storage fails: log error, continue. Session Review never blocks session-end.
- If operator does not respond to Process Review offer: treat as declined, proceed to session-end.

---

## Escape Hatches

| Escape | Trigger | Behavior |
|--------|---------|----------|
| `--skip-session-review` | Operator passes flag | Log `SessionReviewSkipped`, return early |
| Predicate fails | No closed work / insufficient retro | Skip automatically, log `SessionReviewSkipped` |
| Session log missing | session-log.jsonl not found | Abort, log `SessionReviewDegradedNoSessionLog` |
| Retro data missing | Memory query returns nothing | Degrade to lightweight mode |
| Memory failure | `ingester_ingest` error | Log error, continue |

**Principle:** Session Review never blocks session-end. Every phase degrades gracefully.

---

## Composition

| Predecessor | Relationship | Notes |
|-------------|-------------|-------|
| retro-cycle | Produces per-item evidence consumed by GATHER | retro must complete before session-review triggers |
| session-end-ceremony | Session-review runs BEFORE session-end | session-end is mechanical, needs no review output |
| process-review-cycle | Session-review MAY chain to process-review | Only if proposals exist AND operator accepts |

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Conditional automatic trigger | Computable predicate (closed work OR retro count) | Avoids overhead for trivial sessions (mem:85605) |
| Cross-item only (exclusion rule) | Do not restate retro findings | Retro handles per-item; session-review adds the cross-item layer |
| Predicate requires retro completion | Not just CHECK/DONE phase | Retro output is primary evidence; phase entry without retro produces evidence gaps |
| 3 phases (GATHER/ASSESS/STORE) | Not retro's 4 phases | Session review is simpler — no EXTRACT (that's retro's job). Proportional to ceremony purpose |

---

## Related

- **retro-cycle:** Per-work-item reflection. Session Review aggregates retro outputs across items
- **session-end-ceremony:** Mechanical session finalization. Session Review runs before it
- **process-review-cycle:** System evolution ceremony. Session Review MAY chain to it
- **WORK-206:** Session event log (provides session-log.jsonl input)
- **REQ-FEEDBACK-006:** Session Review ceremony requirement
- **REQ-CEREMONY-001, 002, 005:** Ceremony contracts, proportional scaling
