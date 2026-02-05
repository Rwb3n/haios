# generated: 2026-01-24
# System Auto: last updated on: 2026-02-05T19:05:36
# L4: Functional Requirements

Level: L4
Status: DYNAMIC (evolves with implementation)
Derived from: L3 principles + agent_user_requirements.md

---

## Requirement ID Registry (Master)

*All L4 requirements with bidirectional traceability to L3*

| ID | Domain | Description | Derives From | Implemented By |
|----|--------|-------------|--------------|----------------|
| REQ-TRACE-001 | Traceability | Work items include `traces_to:` field | L3.7, L3.11 | WORK.md template |
| REQ-TRACE-002 | Traceability | Work creation validates `traces_to:` | L3.7, L3.15, L3.18 | work-creation-cycle |
| REQ-TRACE-003 | Traceability | Close validates requirement addressed | L3.7, L3.18 | close-work-cycle |
| REQ-TRACE-004 | Traceability | Work items MUST trace to existing chapter file | L3.7, L3.11 | WorkEngine.get_ready() |
| REQ-TRACE-005 | Traceability | Full chain: L4 → Epoch → Arc → Chapter → Work | L3.7 | work-creation-cycle |
| REQ-CONTEXT-001 | Context | Coldstart MUST inject prior session context | L3.3, L3.16 | ColdstartOrchestrator |
| REQ-CONTEXT-002 | Context | Files are context windows for next node | L3.3 | Gate output files |
| REQ-CONTEXT-003 | Context | Memory refs MUST be queried on document load | L3.3, L3.14 | Memory refs rule |
| REQ-GOVERN-001 | Governance | Gates MUST block invalid transitions | L3.1, L3.15 | GovernanceLayer |
| REQ-GOVERN-002 | Governance | Irreversible actions require explicit permission | L3.5, L3.8 | PreToolUse hooks |
| REQ-GOVERN-003 | Governance | SQL queries MUST use schema-verifier | L3.2, L3.13 | PreToolUse hook |
| REQ-MEMORY-001 | Memory | Store learnings with provenance | L3.3, L3.7 | MemoryBridge |
| REQ-MEMORY-002 | Memory | Query before deciding (retrieval over generation) | L3.2, L3.14 | memory-agent skill |
| REQ-WORK-001 | Work | Work items track state via four dimensions (status, queue_position, cycle_phase, activity_state) | L3.1, L3.7 | WorkEngine |
| REQ-WORK-002 | Work | Status over location (ADR-041) | L3.1 | Work item structure |
| REQ-VALID-001 | Validation | Work creation MUST validate ID availability against terminal statuses | L3.1, L3.5 | WorkEngine, scaffold.py |
| REQ-VALID-002 | Validation | Scaffold templates MUST produce files with all required fields populated | L3.2 | scaffold.py |
| REQ-VALID-003 | Validation | Plan validation MUST check for unresolved decisions before Implementation lifecycle | L3.1, L3.15 | plan-validation-cycle Gate 4 |
| REQ-ACTIVITY-001 | Activities | Governed activities MUST be state-aware (Primitive × State × Rules) | L3.4, L3.15 | PreToolUse hook |
| REQ-ACTIVITY-002 | Activities | DO phase (Implementation lifecycle) MUST block AskUser, explore-*, spec-write | L3.4, L3.15 | PreToolUse hook |
| REQ-FLOW-001 | Flow | Implementation lifecycle: PLAN→DO→CHECK→DONE | L3.1, L3.7 | CycleRunner |
| REQ-FLOW-002 | Flow | Investigation lifecycle: EXPLORE→HYPOTHESIZE→VALIDATE→CONCLUDE | L3.1, L3.7 | CycleRunner |
| REQ-FLOW-003 | Flow | Design lifecycle: EXPLORE→SPECIFY→CRITIQUE→COMPLETE | L3.1, L3.7 | CycleRunner |
| REQ-CRITIQUE-001 | Critique | Critique MUST be hard gate within Design lifecycle | L3.2, L3.15 | GovernanceLayer |
| REQ-CRITIQUE-002 | Critique | COMPLETE phase requires critique verdict = PROCEED | L3.2, L3.15 | GovernanceLayer |
| REQ-TEMPLATE-001 | Templates | Phase templates MUST have input/output contracts | L3.2, L3.7 | Template validation |
| REQ-TEMPLATE-002 | Templates | Templates MUST be fractured by phase (~30-50 lines each) | L3.6 | Template structure |
| REQ-DOD-001 | DoD | Chapter closure MUST verify all work complete + implements_decisions | L3.7, L3.18 | close-chapter-ceremony |
| REQ-DOD-002 | DoD | Arc closure MUST verify all chapters complete + no orphan decisions | L3.7, L3.18 | close-arc-ceremony |
| REQ-LIFECYCLE-001 | Lifecycle | Lifecycles are pure functions: Input → Output, independently completable | L3.4, L3.6 | CycleRunner |
| REQ-LIFECYCLE-002 | Lifecycle | Pause points are valid completion states (S27 Breath Model) | L3.4, L3.5 | WorkEngine |
| REQ-LIFECYCLE-003 | Lifecycle | Batch mode: multiple items in same lifecycle phase simultaneously | L3.6 | WorkEngine |
| REQ-LIFECYCLE-004 | Lifecycle | Chaining is caller choice, not callee side-effect | L3.4, L3.5 | CycleRunner |
| REQ-QUEUE-001 | Queue | Queue position is orthogonal to lifecycle phase | L3.4 | WorkEngine |
| REQ-QUEUE-002 | Queue | "Complete without spawn" is valid terminal state | L3.4, L3.5 | close-work-cycle |
| REQ-QUEUE-003 | Queue | Queue has own lifecycle (parked→backlog→ready→active→done) | L3.4 | WorkEngine |
| REQ-QUEUE-004 | Queue | Queue ceremonies govern queue state transitions | L3.4, L3.7 | Queue ceremonies |
| REQ-QUEUE-005 | Queue | Parked items are excluded from current epoch scope | L3.4, L3.6 | WorkEngine.get_queue() |
| REQ-CEREMONY-001 | Ceremony | Ceremonies govern side-effects (commits, state changes) | L3.7 | Ceremony skills |
| REQ-CEREMONY-002 | Ceremony | Each ceremony has explicit input/output contract | L3.2, L3.7 | Ceremony skills |
| REQ-CEREMONY-003 | Ceremony | Ceremonies distinct from lifecycles (WHEN vs WHAT) | L3.4 | Architecture |
| REQ-FEEDBACK-001 | Feedback | Work completion triggers Chapter Review ceremony | L3.1, L3.3 | close-work-cycle |
| REQ-FEEDBACK-002 | Feedback | Chapter completion triggers Arc Review ceremony | L3.1, L3.3 | close-chapter-ceremony |
| REQ-FEEDBACK-003 | Feedback | Arc completion triggers Epoch Review ceremony | L3.1, L3.3 | close-arc-ceremony |
| REQ-FEEDBACK-004 | Feedback | Epoch completion triggers Requirements Review ceremony | L3.1, L3.3 | close-epoch-ceremony |
| REQ-FEEDBACK-005 | Feedback | Reviews MAY update parent scope (not just status) | L3.1, L3.3 | Review ceremonies |
| REQ-ASSET-001 | Asset | Each lifecycle produces typed, immutable asset | L3.1, L3.7 | Lifecycle output |
| REQ-ASSET-002 | Asset | Assets are versioned, not edited (append-only) | L3.1, L3.5 | Asset storage |
| REQ-ASSET-003 | Asset | Assets can be piped to next lifecycle OR stored | L3.4, L3.6 | Lifecycle chaining |
| REQ-ASSET-004 | Asset | Asset schema is lifecycle-specific | L3.2 | Asset validation |
| REQ-ASSET-005 | Asset | Assets have provenance (source lifecycle, timestamp, author) | L3.7 | Asset metadata |
| REQ-CONFIG-001 | Config | All paths defined in haios.yaml, accessed via ConfigLoader | L3.3, L3.6 | ConfigLoader.get_path() |
| REQ-CONFIG-002 | Config | Behavior config is YAML, not hardcoded | L3.6 | critique_frameworks/, loaders/ |
| REQ-CONFIG-003 | Config | Config follows single-source-of-truth principle | L3.3 | No duplicate constants |
| REQ-CONFIG-004 | Config | Config is portable (relative paths, no machine-specific) | L3.6 | .claude/haios/ is self-contained |
| REQ-CONFIG-005 | Config | Frameworks are pluggable (critique, loaders, corpus) | L3.6 | YAML + code pattern |
| REQ-OBSERVE-001 | Observability | All state transitions logged to events file | L3.7 | governance-events.jsonl |
| REQ-OBSERVE-002 | Observability | Session state visible via hooks (PreToolUse context) | L3.7 | additionalContext injection |
| REQ-OBSERVE-003 | Observability | System health queryable (just status, haios-status.json) | L3.7 | Status file maintained |
| REQ-OBSERVE-004 | Observability | Drift detection on coldstart | L3.1, L3.7 | ColdstartOrchestrator warnings |

*Registry grows as requirements are enumerated from L3 principles.*

---

## Traceability Requirements

*Derived from L3.7 (Traceability) + L3 LLM Nature (enforcement principle)*

| ID | Requirement | Derives From | Acceptance Test |
|----|-------------|--------------|-----------------|
| **REQ-TRACE-001** | Work items MUST include `traces_to:` field in frontmatter | L3.7, L3.11 | WORK.md template includes field |
| **REQ-TRACE-002** | Work creation MUST validate `traces_to:` references a valid requirement ID | L3.7, L3.15, L3.18 | `work-creation-cycle` blocks on empty/invalid `traces_to:` |
| **REQ-TRACE-003** | Close-work-cycle MUST verify the traced requirement was addressed | L3.7, L3.18 | DoD validation includes requirement satisfaction check |
| **REQ-TRACE-004** | Work items MUST trace to an existing chapter file. No chapter → BLOCKED. | L3.7, L3.11 | `WorkEngine.get_ready()` filters items without chapter file |
| **REQ-TRACE-005** | Full traceability chain MUST exist: L4 Requirement → Epoch → Arc → Chapter → Work Item | L3.7 | `work-creation-cycle` validates chain before READY |

**Invariants:**
- Traceability is governance, not documentation (enforcement over enablement)
- Invalid requirement IDs MUST block, not warn
- Requirement IDs follow pattern: `REQ-{DOMAIN}-{NNN}` (e.g., `REQ-TRACE-001`)
- **No chapter file → work item BLOCKED** (REQ-TRACE-004)
- **Orphan work items are invalid** - every work item must trace up to L4 (REQ-TRACE-005)

---

## Validation Requirements

*Derived from L3.1 (Certainty Ratchet) + L3.5 (Reversibility) + L3.2 (Evidence Over Assumption)*

| ID | Requirement | Derives From | Acceptance Test |
|----|-------------|--------------|-----------------|
| **REQ-VALID-001** | Work creation MUST validate ID availability against terminal statuses (complete/archived) | L3.1, L3.5 | `create_work()` raises on ID with terminal status |
| **REQ-VALID-002** | Scaffold templates MUST produce files with all required fields populated (no `{{PLACEHOLDER}}` in output) | L3.2 | Scaffolded files pass template validation |
| **REQ-VALID-003** | Plan validation MUST check Open Decisions for `[BLOCKED]` entries before DO phase | L3.1, L3.15 | plan-validation-cycle Gate 4 blocks on unresolved decisions |

**Invariants:**
- Validation is enforcement, not documentation (L3.15: enforcement over enablement)
- Terminal status collision MUST block, not warn (data loss is irreversible)
- REQ-VALID-002 supersedes scaffold recipes — `/new-*` commands are the governed path

---

## Activity Requirements (E2.4 - Session 265)

*Derived from L3.4 (Duties Are Separated) + L3.15 (Enforcement over Enablement)*

| ID | Requirement | Derives From | Acceptance Test |
|----|-------------|--------------|-----------------|
| **REQ-ACTIVITY-001** | Governed activities MUST be state-aware: same primitive has different rules per state | L3.4, L3.15 | PreToolUse checks current state before allowing primitive |
| **REQ-ACTIVITY-002** | DO state MUST block: AskUser, explore-*, spec-write | L3.4, L3.15 | Attempting blocked activity in DO returns error |

**Invariants:**
- State determines governance envelope, not agent role
- Blocked activities return clear error with current state and blocked reason
- State transitions logged for audit

---

## Flow Requirements (E2.4 - Session 265, updated E2.5 - Session 294)

*Derived from L3.1 (Certainty Ratchet) + L3.7 (Traceability)*

*E2.5 Update: Flows are per-lifecycle, not cross-lifecycle chains. See REQ-LIFECYCLE-001.*

| ID | Requirement | Derives From | Acceptance Test |
|----|-------------|--------------|-----------------|
| **REQ-FLOW-001** | Implementation lifecycle phases: PLAN → DO → CHECK → DONE | L3.1, L3.7 | CycleRunner enforces phase sequence within lifecycle |
| **REQ-FLOW-002** | Investigation lifecycle phases: EXPLORE → HYPOTHESIZE → VALIDATE → CONCLUDE | L3.1, L3.7 | Investigation cycle enforces EXPLORE-FIRST |
| **REQ-FLOW-003** | Design lifecycle phases: EXPLORE → SPECIFY → CRITIQUE → COMPLETE | L3.1, L3.7 | Design cycle is independent, not front of implementation |

**S27 Breath Model (Session 292):**

```
EXPLORE    [inhale] → SYNTHESIZE [exhale] → [pause: safe to stop]
```

Each lifecycle follows inhale→exhale→pause rhythm. Pause = valid completion point.

**Invariants:**
- Phases cannot be skipped within a lifecycle (though can be lightweight)
- Phase transitions logged with timestamp
- Output of phase N is input contract of phase N+1 *within same lifecycle*
- Cross-lifecycle chaining is explicit operator choice (REQ-LIFECYCLE-004)

---

## Critique Requirements (E2.4 - Session 265)

*Derived from L3.2 (Evidence Over Assumption) + L3.15 (Enforcement over Enablement)*

| ID | Requirement | Derives From | Acceptance Test |
|----|-------------|--------------|-----------------|
| **REQ-CRITIQUE-001** | Critique MUST be invoked as hard gate at DESIGN→PLAN and PLAN→DO transitions | L3.2, L3.15 | Transition blocked without critique invocation |
| **REQ-CRITIQUE-002** | DO phase entry MUST require critique verdict = PROCEED | L3.2, L3.15 | BLOCK or REVISE verdict prevents DO entry |

**Invariants:**
- Critique loop: invoke → read → revise (if needed) → re-invoke until PROCEED
- Critique findings stored to memory for future reference
- "If there's a critique, revise until there is no critique"

---

## Template Requirements (E2.4 - Session 265)

*Derived from L3.2 (Evidence Over Assumption) + L3.6 (Graceful Degradation)*

| ID | Requirement | Derives From | Acceptance Test |
|----|-------------|--------------|-----------------|
| **REQ-TEMPLATE-001** | Phase templates MUST have explicit input/output contracts | L3.2, L3.7 | Template includes Input Contract and Output Contract sections |
| **REQ-TEMPLATE-002** | Templates MUST be fractured by phase (~30-50 lines each) | L3.6 | No single template exceeds 100 lines |

**Invariants:**
- One template per phase (not monolithic)
- Input contract is gate for phase entry
- Output contract is gate for phase exit
- Governance through activities layer, not template checkboxes

---

## DoD Requirements (E2.4 - Session 285)

*Derived from L3.7 (Traceability) + L3.18 (DoD requirement)*

| ID | Requirement | Derives From | Acceptance Test |
|----|-------------|--------------|-----------------|
| **REQ-DOD-001** | Chapter closure MUST verify all work items complete + implements_decisions match claimed decisions | L3.7, L3.18 | close-chapter-ceremony blocks on incomplete work or unimplemented decisions |
| **REQ-DOD-002** | Arc closure MUST verify all chapters complete + no epoch decisions unassigned to arc | L3.7, L3.18 | close-arc-ceremony blocks on incomplete chapters or orphan decisions |

**Invariants:**
- DoD cascade: Work -> Chapter -> Arc -> Epoch
- Lower level must complete before higher level can close
- Orphan decisions (assigned but not implemented) block closure

---

## Lifecycle Requirements (E2.5 - Session 294)

*Derived from L3.4 (Duties Are Separated) + L3.5 (Reversibility) + L3.6 (Graceful Degradation)*

*Anti-pattern corrections: removing implicit coupling that violated FP/OOP principles.*

| ID | Requirement | Derives From | Acceptance Test |
|----|-------------|--------------|-----------------|
| **REQ-LIFECYCLE-001** | Lifecycles are pure functions (Input → Output), independently completable without chaining | L3.4, L3.6 | Design lifecycle completes without spawning implementation |
| **REQ-LIFECYCLE-002** | Pause points (per S27 Breath Model) are valid completion states, not just gates | L3.4, L3.5 | Work item can close at pause without "incomplete" status |
| **REQ-LIFECYCLE-003** | Batch mode: multiple items in same lifecycle phase simultaneously | L3.6 | `design(A), design(B), design(C)` all in DESIGN phase concurrently |
| **REQ-LIFECYCLE-004** | Chaining is caller choice, not callee side-effect. Lifecycle returns output, caller decides next action. | L3.4, L3.5 | Cycle completion prompts "spawn next?" not auto-chains |

**Work Lifecycle Definitions (as pure functions):**

| Lifecycle | Signature | Phases | Output |
|-----------|-----------|--------|--------|
| Investigation | `Question → Findings` | EXPLORE → HYPOTHESIZE → VALIDATE → CONCLUDE | Findings document |
| Design | `Requirements → Specification` | EXPLORE → SPECIFY → CRITIQUE → COMPLETE | Specification document |
| Implementation | `Specification → Artifact` | PLAN → DO → CHECK → DONE | Working artifact |
| Validation | `Artifact × Spec → Verdict` | VERIFY → JUDGE → REPORT | Pass/fail verdict |
| Triage | `[Items] → [PrioritizedItems]` | SCAN → ASSESS → RANK → COMMIT | Prioritized list |

**Invariants:**
- Each lifecycle is a complete unit (S27: inhale→exhale→pause)
- Pause = safe return point, not "stuck"
- Output of lifecycle N can be input to lifecycle N+1, but doesn't require it
- "Complete without spawn" is valid (batch design period, research-only investigation)

---

## Queue Requirements (E2.5 - Session 294)

*Derived from L3.4 (Duties Are Separated) - corrects conflation identified in WORK-065.*

| ID | Requirement | Derives From | Acceptance Test |
|----|-------------|--------------|-----------------|
| **REQ-QUEUE-001** | Queue position is orthogonal to lifecycle phase. Separate tracking dimensions. | L3.4 | Work item in `queue: done` can have any lifecycle phase |
| **REQ-QUEUE-002** | "Complete without spawn" is valid terminal state. No forced chaining. | L3.4, L3.5 | close-work-cycle accepts completion without spawn_next |
| **REQ-QUEUE-003** | Queue has its own lifecycle (parked → backlog → ready → active → done) | L3.4 | Queue transitions independent of work lifecycle |
| **REQ-QUEUE-004** | Queue ceremonies govern queue state transitions | L3.4, L3.7 | Each transition has ceremony |
| **REQ-QUEUE-005** | Parked items are excluded from current epoch scope. Parked ≠ blocked. | L3.4, L3.6 | `WorkEngine.get_queue()` excludes parked items; `just ready` never shows parked |

**Queue Lifecycle:**

```
parked ──→ backlog ──→ ready ──→ active ──→ done
   │          │          │          │
   └── Unpark └── Intake └── Commit └── Release (ceremonies)
```

| Phase | Meaning | Entry Ceremony | Exit Ceremony |
|-------|---------|----------------|---------------|
| parked | Out of scope for current epoch | - | Unpark |
| backlog | Captured, not prioritized | Intake | Prioritize |
| ready | Prioritized, dependencies clear | Prioritize | Commit |
| active | Being worked | Commit | Release |
| done | Work complete | Release | - |

**Parked vs Blocked (Session 314 finding):**

| | Parked | Blocked |
|---|---|---|
| Meaning | Out of scope (future epoch) | Has unresolved dependency |
| Field | `queue_position: parked` | `status: blocked` + `blocked_by: [...]` |
| Visibility | Excluded from all queues | Visible but not selectable |
| Resolution | Operator decision to unpark | Dependency completion |
| Example | WORK-101 (E2.6 design work during E2.5) | WORK-091 (blocked by WORK-098) |

**Two Parallel State Machines:**

```
Queue:     parked ──→ backlog ──→ ready ──→ active ──→ done
                                    │
Work:                               └──→ [lifecycle phases] ──→ complete
```

Work lifecycle runs *while* queue position is `active`. They are orthogonal.
Parked items never enter work lifecycle until unparked.

**Four Orthogonal Dimensions (WORK-065 finding):**

| Dimension | Field | Values | Purpose |
|-----------|-------|--------|---------|
| Lifecycle | `status` | active/blocked/complete/archived | ADR-041 authoritative |
| Queue | `queue_position` | parked/backlog/ready/active/done | Selection pipeline |
| Cycle | `cycle_phase` | per-lifecycle phases | Current phase within lifecycle |
| Activity | `activity_state` | EXPLORE/DESIGN/etc. | Governed activity state |

**Invariants:**
- Queue tracks "where in selection pipeline" - not "what lifecycle phase"
- Lifecycle tracks "what transformation is happening" - not "will it chain"
- A work item can be `queue: done` + `status: complete` without spawning anything
- Parked items are invisible to survey-cycle and `just ready` (REQ-QUEUE-005)
- Parked ≠ blocked: parked is scope decision, blocked is dependency (Session 314)
- 94% stuck at backlog (WORK-065) was symptom of conflation - these requirements fix root cause

---

## Ceremony Requirements (E2.5 - Session 294)

*Derived from L3.7 (Traceability) + Five-Layer Hierarchy (CEREMONIES = WHEN layer)*

*Ceremonies are side-effect boundaries. They govern state transitions, not transformations.*

| ID | Requirement | Derives From | Acceptance Test |
|----|-------------|--------------|-----------------|
| **REQ-CEREMONY-001** | Ceremonies govern side-effects (commits, state changes, transitions) | L3.7 | State changes only occur within ceremony boundaries |
| **REQ-CEREMONY-002** | Each ceremony has explicit input/output contract | L3.2, L3.7 | Ceremony skill documents contracts |
| **REQ-CEREMONY-003** | Ceremonies are distinct from lifecycles (WHEN vs WHAT) | L3.4 | Ceremony does not transform work, only transitions state |

**Ceremony Definitions:**

| Category | Ceremony | Signature | Side Effects |
|----------|----------|-----------|--------------|
| **Queue** | Intake | `Idea → BacklogItem` | Create work item |
| **Queue** | Prioritize | `[BacklogItems] → [ReadyItems]` | Update queue_position |
| **Queue** | Commit | `ReadyItem → ActiveItem` | Start work, log event |
| **Queue** | Release | `ActiveItem → DoneItem` | Complete work, log event |
| **Session** | Session Start | `Config → SessionState` | Log event, load context |
| **Session** | Session End | `SessionState → Log` | Log event, orphan check |
| **Session** | Checkpoint | `SessionState → CheckpointDoc` | Write doc, git commit |
| **Closure** | Close Work | `WorkItem → ClosedWorkItem` | Status change, memory commit |
| **Closure** | Close Chapter | `Chapter → ClosedChapter` | DoD verify, status change |
| **Closure** | Close Arc | `Arc → ClosedArc` | Decision verify, status change |
| **Closure** | Close Epoch | `Epoch → ClosedEpoch` | Archive, config transition |
| **Memory** | Observation Capture | `Experience → Observations` | Write observations |
| **Memory** | Observation Triage | `[Observations] → [Actions]` | Promote or close |
| **Memory** | Memory Commit | `Learnings → ConceptIDs` | Store to memory |
| **Spawn** | Spawn Work | `WorkItem → NewWorkItem` | Create linked work item |
| **Feedback** | Chapter Review | `CompletedWork + Chapter → Chapter?` | Maybe update chapter scope |
| **Feedback** | Arc Review | `CompletedChapter + Arc → Arc?` | Maybe update arc direction |
| **Feedback** | Epoch Review | `CompletedArc + Epoch → Epoch?` | Maybe update epoch goals |
| **Feedback** | Requirements Review | `CompletedEpoch + L4 → L4?` | Maybe update requirements |

**Invariants:**
- Ceremonies produce side-effects; lifecycles produce artifacts
- Every state transition must occur within a ceremony
- Ceremonies log events for audit (L3.7 traceability)
- Ceremonies can be invoked from lifecycle pause points

---

## Feedback Requirements (E2.5 - Session 294)

*Derived from L3.1 (Certainty Ratchet) + L3.3 (Context Must Persist)*

*Learnings flow upward. The system learns from completed work.*

| ID | Requirement | Derives From | Acceptance Test |
|----|-------------|--------------|-----------------|
| **REQ-FEEDBACK-001** | Work completion triggers Chapter Review ceremony | L3.1, L3.3 | close-work-cycle chains to chapter-review |
| **REQ-FEEDBACK-002** | Chapter completion triggers Arc Review ceremony | L3.1, L3.3 | close-chapter-ceremony chains to arc-review |
| **REQ-FEEDBACK-003** | Arc completion triggers Epoch Review ceremony | L3.1, L3.3 | close-arc-ceremony chains to epoch-review |
| **REQ-FEEDBACK-004** | Epoch completion triggers Requirements Review ceremony | L3.1, L3.3 | close-epoch-ceremony chains to requirements-review |
| **REQ-FEEDBACK-005** | Reviews MAY update parent scope (not just propagate status) | L3.1, L3.3 | Review ceremony can edit parent document |

**Feedback Loop:**

```
L4 Requirements ←───────────────────────────────────────┐
      ↓ (decompose)                                     │
    Epoch ←─────────────────────────────────┐           │
      ↓                                     │           │
    Arc ←───────────────────────┐           │           │
      ↓                         │           │           │
    Chapter ←───────┐           │           │           │
      ↓             │           │           │           │
    Work Item       │           │           │           │
      ↓             │           │           │           │
    [lifecycle]     │           │           │           │
      ↓             │           │           │           │
    Complete ──→ Chapter    Arc         Epoch      Requirements
                 Review ──→ Review ──→  Review ──→  Review
```

**Review Ceremonies:**

| Ceremony | Trigger | Input | Output |
|----------|---------|-------|--------|
| Chapter Review | Work closes | `CompletedWork + Chapter` | `Chapter (maybe updated)` |
| Arc Review | Chapter closes | `CompletedChapter + Arc` | `Arc (maybe updated)` |
| Epoch Review | Arc closes | `CompletedArc + Epoch` | `Epoch (maybe updated)` |
| Requirements Review | Epoch closes | `CompletedEpoch + L4` | `L4 (maybe updated)` |

**Review Questions (per level):**

| Level | Question |
|-------|----------|
| Chapter Review | Did this work change our understanding of chapter scope? |
| Arc Review | Did this chapter reveal new work needed in this arc? |
| Epoch Review | Did this arc change our understanding of epoch goals? |
| Requirements Review | Did this epoch reveal requirements we missed? |

**Invariants:**
- Reviews are ceremonies, not lifecycles (side-effect: update parent doc)
- "No change needed" is valid review outcome
- Changes must be logged (L3.7 traceability)
- This is how the system learns - certainty ratchets upward

---

## Asset Requirements (E2.5 - Session 294)

*Derived from L3.1 (Certainty Ratchet) + L3.7 (Traceability) + Unix pipe philosophy*

*Assets are the OUTPUT layer. Immutable artifacts produced by lifecycles.*

| ID | Requirement | Derives From | Acceptance Test |
|----|-------------|--------------|-----------------|
| **REQ-ASSET-001** | Each lifecycle produces typed, immutable asset | L3.1, L3.7 | Lifecycle has defined output type |
| **REQ-ASSET-002** | Assets are versioned, not edited (append-only history) | L3.1, L3.5 | Edit creates new version, old preserved |
| **REQ-ASSET-003** | Assets can be piped to next lifecycle OR stored standalone | L3.4, L3.6 | `investigation > file` OR `investigation | design` |
| **REQ-ASSET-004** | Asset schema is lifecycle-specific (typed streams) | L3.2 | Findings ≠ Spec ≠ Artifact |
| **REQ-ASSET-005** | Assets have provenance (source, timestamp, author) | L3.7 | Frontmatter includes provenance |

**Unix Pipe Analogy:**

```bash
# Unix
cmd1 | cmd2 | cmd3 > output.txt

# HAIOS
Investigation | Design | Implementation > artifact
     ↓            ↓           ↓
  findings.md  spec.md    code/
```

**Asset Types (per lifecycle):**

| Lifecycle | Asset Type | Schema | Format |
|-----------|------------|--------|--------|
| Investigation | Findings | `findings_schema` | markdown |
| Design | Specification | `spec_schema` / TRD | markdown |
| Implementation | Artifact | varies (code, config) | mixed |
| Validation | Verdict | `verdict_schema` | markdown |
| Triage | Priority List | `queue_schema` | yaml |

**Asset Composition:**

```
findings.md ──┐
              ├──→ spec.md ──→ artifact/ ──→ verdict.md
requirements ─┘        │
                       │ (stored, not piped)
                       ↓
                   spec_v2.md (batch design, no implementation)
```

**Provenance Frontmatter:**

```yaml
---
asset_type: findings
produced_by: investigation
source_work: WORK-XXX
version: 1
timestamp: 2026-02-02T23:38:00
author: Hephaestus
inputs:
  - question.md
---
```

**Invariants:**
- Lifecycles produce assets; ceremonies produce state changes
- Assets are immutable - new version, don't overwrite
- Piping is optional - storing is always valid
- Asset type must match lifecycle (can't produce spec from implementation)
- Provenance enables traceability (who made what, from what, when)

---

## Configuration Requirements (E2.5 - Session 294)

*Derived from L3.3 (Context Must Persist) + L3.6 (Graceful Degradation)*

*Configuration is the nervous system. Portable, discoverable, pluggable.*

| ID | Requirement | Derives From | Acceptance Test |
|----|-------------|--------------|-----------------|
| **REQ-CONFIG-001** | All paths defined in haios.yaml, accessed via ConfigLoader | L3.3, L3.6 | No hardcoded paths in modules |
| **REQ-CONFIG-002** | Behavior config is YAML, not hardcoded | L3.6 | Critique frameworks, loaders are YAML |
| **REQ-CONFIG-003** | Config follows single-source-of-truth principle | L3.3 | No duplicate constants |
| **REQ-CONFIG-004** | Config is portable (relative paths, no machine-specific) | L3.6 | .claude/haios/ works on any clone |
| **REQ-CONFIG-005** | Frameworks are pluggable (YAML + code pattern) | L3.6 | Add framework without code change |

**Configuration Hierarchy:**

```
.claude/haios/config/
├── haios.yaml              # Master config (toggles, thresholds, paths)
├── cycles.yaml             # Cycle definitions, node bindings
├── components.yaml         # Component registry
├── coldstart.yaml          # Coldstart phase config
├── activity_matrix.yaml    # Governed activities per state
├── work_queues.yaml        # Queue configuration
├── critique_frameworks/    # Pluggable critique patterns
│   └── {framework}.yaml
├── loaders/                # Pluggable context loaders
│   └── {loader}.yaml
└── corpus/                 # Pluggable document corpora
    └── {corpus}.yaml
```

**Pluggable Framework Pattern (critique_frameworks/):**

```yaml
name: assumption_surfacing
version: "1.0"
description: "Surface implicit assumptions"

categories:
  - id: scope
    label: "Scope Assumptions"
    prompt: "What scope assumptions are implicit?"

verdict_rules:
  BLOCK: "Critical assumption unvalidated"
  REVISE: "Assumptions need clarification"
  PROCEED: "All assumptions explicit"
```

**Path Access Pattern:**

```python
from config import ConfigLoader

config = ConfigLoader.get()
work_path = config.get_path("work_item", id="WORK-080")
# Returns: Path("docs/work/active/WORK-080/WORK.md")
```

**Invariants:**
- haios.yaml is the discovery root
- Modules import ConfigLoader, not define constants
- Framework YAML + Python loader = pluggable behavior
- Portable: no absolute paths, no machine-specific config

---

## Observability Requirements (E2.5 - Session 294)

*Derived from L3.7 (Traceability)*

*Observability is the mirror. The system must see itself.*

| ID | Requirement | Derives From | Acceptance Test |
|----|-------------|--------------|-----------------|
| **REQ-OBSERVE-001** | All state transitions logged to events file | L3.7 | governance-events.jsonl has transition |
| **REQ-OBSERVE-002** | Session state visible via hooks (PreToolUse context) | L3.7 | Agent sees `[STATE: DO]` in context |
| **REQ-OBSERVE-003** | System health queryable (just status) | L3.7 | haios-status.json current |
| **REQ-OBSERVE-004** | Drift detection on coldstart | L3.1, L3.7 | Orchestrator warns on drift |

**Observability Layers:**

| Layer | Mechanism | Output |
|-------|-----------|--------|
| Events | governance-events.jsonl | Append-only log |
| State | session_state in status | Current cycle, phase, work |
| Health | haios-status.json | Tests, memory, validation |
| Context | PreToolUse additionalContext | `[STATE: X] Blocked: ...` |
| Drift | ColdstartOrchestrator | Warnings on load |

**Event Types:**

```jsonl
{"type": "SessionStarted", "session": 294, "agent": "Hephaestus", "timestamp": "..."}
{"type": "CycleTransition", "from_phase": "PLAN", "to_phase": "DO", "work_id": "WORK-080", ...}
{"type": "ValidationOutcome", "gate": "dod", "result": "pass", ...}
{"type": "SessionEnded", "session": 294, ...}
```

**PreToolUse Context Injection:**

```
[STATE: DO] Blocked: user-query, web-fetch, web-search, memory-search, memory-store
```

Agent sees what's blocked BEFORE attempting, reducing wasted attempts.

**Invariants:**
- Events are append-only (never delete, never modify)
- State is queryable at any time
- Drift warnings are prominent, not buried
- Observability enables debugging without reading code

---

## Supersession Log (Append-Only)

*Per FP principles: requirements are never deleted, only superseded.*

| Session | Superseded | By | Reason |
|---------|------------|-----|--------|
| 294 | REQ-FLOW-001 (original: "EXPLORE→DESIGN→PLAN→DO→CHECK→DONE as single chain") | REQ-FLOW-001 (revised) + REQ-LIFECYCLE-001 | Lifecycles are independent, not chained |
| 294 | REQ-CRITIQUE-001 (original: "hard gate at DESIGN→PLAN and PLAN→DO") | REQ-CRITIQUE-001 (revised) | Critique is within Design lifecycle, not cross-lifecycle gate |
| 294 | REQ-CRITIQUE-002 (original: "DO entry requires critique verdict") | REQ-CRITIQUE-002 (revised) | COMPLETE phase (in Design) requires critique, not DO entry |
| 294 | REQ-WORK-001 (original: "track lifecycle via node_history") | REQ-WORK-001 (revised) + REQ-QUEUE-001 | Four dimensions replace single node_history |
| 294 | REQ-VALID-003 (original: "before DO phase") | REQ-VALID-003 (revised) | "DO phase" → "Implementation lifecycle" |
| 294 | REQ-ACTIVITY-002 (original: "DO state") | REQ-ACTIVITY-002 (revised) | Clarify DO is phase within Implementation lifecycle |

**Original Wordings (preserved for history):**

**REQ-FLOW-001 (E2.4 original):**
> Implementation work MUST follow: EXPLORE → DESIGN → PLAN → DO → CHECK → DONE

**REQ-FLOW-001 (E2.5 revised):**
> Implementation lifecycle phases: PLAN → DO → CHECK → DONE

*Reason: EXPLORE and DESIGN are now separate lifecycles, not phases of implementation.*

**REQ-CRITIQUE-001 (E2.4 original):**
> Critique MUST be invoked as hard gate at DESIGN→PLAN and PLAN→DO transitions

**REQ-CRITIQUE-001 (E2.5 revised):**
> Critique MUST be hard gate within Design lifecycle

*Reason: Critique happens in Design lifecycle's CRITIQUE phase, not as cross-lifecycle gate.*

**REQ-CRITIQUE-002 (E2.4 original):**
> DO phase entry MUST require critique verdict = PROCEED

**REQ-CRITIQUE-002 (E2.5 revised):**
> COMPLETE phase requires critique verdict = PROCEED

*Reason: Design lifecycle completes with critique, Implementation lifecycle starts from specification.*

**REQ-WORK-001 (E2.4 original):**
> Work items track lifecycle via node_history

**REQ-WORK-001 (E2.5 revised):**
> Work items track state via four dimensions (status, queue_position, cycle_phase, activity_state)

*Reason: WORK-065 identified node_history conflated queue and cycle. Four orthogonal dimensions replace it.*

**REQ-VALID-003 (E2.4 original):**
> Plan validation MUST check for unresolved decisions before DO phase

**REQ-VALID-003 (E2.5 revised):**
> Plan validation MUST check for unresolved decisions before Implementation lifecycle

*Reason: DO is a phase within Implementation lifecycle, not a standalone concept.*

**REQ-ACTIVITY-002 (E2.4 original):**
> DO state MUST block AskUser, explore-*, spec-write

**REQ-ACTIVITY-002 (E2.5 revised):**
> DO phase (Implementation lifecycle) MUST block AskUser, explore-*, spec-write

*Reason: Clarify DO is a phase within a specific lifecycle, not a global state.*

---

## Module Function Specifications

### GovernanceLayer

**Purpose:** Policy enforcement, gate checks, transition validation.

| Function | Input | Output | Acceptance Test |
|----------|-------|--------|-----------------|
| `check_gate(gate_id, context)` | Gate ID + work context | `GateResult(allowed, reason)` | Returns deny for incomplete DoD |
| `validate_transition(from_node, to_node)` | DAG nodes | `bool` | Blocks invalid transitions (e.g., backlog→complete) |
| `load_handlers(config_path)` | Path to components.yaml | Handler registry | Loads all registered handlers |
| `on_event(event_type, payload)` | Event + data | Side effects | Routes to correct handlers |

**Invariants:**
- MUST NOT modify work files directly (that's WorkEngine's job)
- MUST log all gate decisions for audit
- MUST be stateless (no internal state between calls)

---

### MemoryBridge

**Purpose:** Wrap haios-memory MCP, provide query modes, auto-link.

| Function | Input | Output | Acceptance Test |
|----------|-------|--------|-----------------|
| `query(query, mode)` | Search string + mode | List of concepts | Returns relevant concepts for "session recovery" |
| `store(content, source_path)` | Content + provenance | Concept IDs | Creates concepts with correct classification |
| `auto_link(work_id, concept_ids)` | Work ID + refs | Updated WORK.md | Adds memory_refs to frontmatter |

**Query Modes:**
- `semantic`: Pure similarity search
- `session_recovery`: Excludes synthesis, for coldstart
- `knowledge_lookup`: Filters to episteme/techne

**Invariants:**
- MUST handle MCP timeout gracefully (retry once, then warn)
- MUST parse work_id from source_path for auto-linking
- MUST NOT block on MCP failure (degrade gracefully)

---

### WorkEngine

**Purpose:** Own WORK.md, manage lifecycle, single source of truth.

| Function | Input | Output | Acceptance Test |
|----------|-------|--------|-----------------|
| `get_work(id)` | Work ID | WorkState object | Returns parsed WORK.md |
| `create_work(id, title, ...)` | Work item data | Created file path | Creates directory + WORK.md |
| `transition(id, to_node)` | Work ID + target node | Updated WorkState | Updates current_node, appends node_history |
| `get_ready()` | None | List of unblocked items | Returns items where blocked_by is empty |
| `archive(id)` | Work ID | Archived path | Moves to docs/work/archive/ |

**Invariants:**
- MUST be the ONLY writer to WORK.md files
- MUST validate transitions via GovernanceLayer
- MUST update node_history with timestamps on every transition
- MUST call MemoryBridge.auto_link after memory operations

---

### ConfigLoader

**Purpose:** Unified config loading with domain organization.

| File | Required Sections | Acceptance Test |
|------|-------------------|-----------------|
| `haios.yaml` | manifest, toggles, thresholds | Loads without error, toggles accessible |
| `cycles.yaml` | node_bindings | Node bindings parseable |
| `components.yaml` | skills, agents, hooks | Registries accessible |

**Invariants:**
- MUST be valid YAML (schema validation on load)
- MUST return empty dict on missing files (graceful degradation)

---

### ContextLoader

**Purpose:** Role-based context loading for coldstart and agent bootstrap.

| Function | Input | Output | Acceptance Test |
|----------|-------|--------|-----------------|
| `load_context(role)` | Role name | ContextResult | Returns loaded content for role |
| `register_loader(name, loader_class)` | Loader registration | None | Loader callable for role |

**Invariants:**
- MUST use config-driven loader selection (haios.yaml roles section)
- MUST support custom loaders via registration

---

### CycleRunner

**Purpose:** Phase execution and cycle chaining.

| Function | Input | Output | Acceptance Test |
|----------|-------|--------|-----------------|
| `get_cycle_phases(cycle_id)` | Cycle ID | Phase list | Returns phases for known cycles |
| `set_cycle(cycle, phase, work_id)` | Cycle state | Session state updated | State persists |

**Invariants:**
- MUST be stateless (state stored in session_state, not runner)

---

## Testing Requirements

### Unit Tests (per module)

| Module | Test File | Key Tests |
|--------|-----------|-----------|
| GovernanceLayer | `tests/test_governance_layer.py` | Gate blocking, transition validation |
| MemoryBridge | `tests/test_memory_bridge.py` | Query modes, auto-link parsing |
| WorkEngine | `tests/test_work_engine.py` | CRUD, transitions, node_history |
| Config | `tests/test_config.py` | YAML loading, schema validation |
| ContextLoader | `tests/test_context_loader.py` | Role loading, loader registration |

### Integration Tests

| Test | Modules | Scenario |
|------|---------|----------|
| `test_work_lifecycle.py` | All | Create -> transition -> archive |
| `test_memory_integration.py` | MemoryBridge + WorkEngine | Store -> auto-link -> verify refs |
| `test_governance_gates.py` | GovernanceLayer + WorkEngine | Transition blocked by gate |

### Acceptance Criteria (DoD per module)

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] **Runtime consumer exists** (something outside tests imports/calls the code)
- [ ] Typed interfaces (Protocol classes)
- [ ] Docstrings on public methods

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used.

---

## References

- @agent_user_requirements.md (source)
- @technical_requirements.md (implementation mapping)
