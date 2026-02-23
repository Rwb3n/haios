---
name: process-review-cycle
type: ceremony
description: "System evolution reflection. Answers: 'What should change in the system?'
  Produces proposed modifications to L3/L4/config/ceremonies with operator approval gate.
  Two modes: chained from Session Review or standalone operator-invoked."
category:
  - feedback
  - session
input_contract:
  - field: session_review_output
    type: object
    required: false
    description: "Session Review output (if chained). Contains session_insights and process_proposals. In chained mode, this satisfies the minimum viable input floor."
  - field: accumulated_observations
    type: list
    required: false
    description: "Cross-session K/S/S patterns from memory. Queried from retro-kss, session-review provenance."
  - field: scope
    type: string
    required: false
    description: "Review scope determining EVIDENCE phase query depth. Default: 'session'. Options: session (current session work IDs), chapter (all work IDs in active chapter), arc (all chapters in active arc), epoch (all provenance across current epoch)."
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: "Whether ceremony completed"
  - field: proposals
    type: list
    guaranteed: on_success
    description: "List of typed proposals with target artifact and rationale"
  - field: approved_proposals
    type: list
    guaranteed: on_success
    description: "Subset approved by operator"
  - field: rejected_proposals
    type: list
    guaranteed: on_success
    description: "Subset rejected by operator, with rejection rationale. Stored to memory so future Process Reviews are aware of prior rejections."
  - field: applied_changes
    type: list
    guaranteed: on_success
    description: "Files actually modified after operator approval"
  - field: spawned_work_ids
    type: list
    guaranteed: on_success
    description: "Work item IDs created for new_work type proposals"
  - field: memory_concept_ids
    type: list
    guaranteed: on_success
    description: "Concept IDs from all COMMIT stores"
  - field: error
    type: string
    guaranteed: on_failure
    description: "Error description"
side_effects:
  - "Store proposals to memory (process-review:{session} provenance)"
  - "Store rejected proposals with rationale to memory"
  - "Apply approved proposals (file modifications) after per-proposal governance event"
  - "Log ProcessReviewCompleted governance event"
  - "Log per-proposal ProcessReviewApproved/ProcessReviewRejected governance events"
  - "Optionally spawn work items for approved proposals that need implementation"
generated: 2026-02-23
last_updated: 2026-02-23
---
# Process Review Cycle

System evolution reflection. Answers: "What should change in the system?" Produces proposed modifications to L3/L4/config/ceremonies with operator approval gate.

## When to Use

**Two invocation modes:**
1. **Chained from Session Review:** Offered when Session Review produces non-empty `process_proposals`
2. **Standalone (operator-invoked):** `Skill(skill="process-review-cycle")` or `/process-review`

---

## The Cycle

```
[Invocation]
  |
  +-> Phase 1: EVIDENCE
  |     Gather inputs: session review output, accumulated observations, K/S/S from memory
  |     Minimum viable input check
  |
  +-> Phase 2: DIAGNOSE
  |     Systemic patterns vs one-off issues
  |     What's recurring? What's new?
  |
  +-> Phase 3: PROPOSE
  |     Generate typed proposals with target artifact
  |
  +-> Phase 4: APPROVE
  |     Per-proposal operator decision (AskUserQuestion)
  |     Per-proposal governance event BEFORE Write call
  |
  +-> COMMIT
        Store all to memory, log completion
```

---

## Phase 1: EVIDENCE

Gather evidence for process analysis.

### Evidence Sources by Scope

| Scope | Query Depth | Sources |
|-------|-------------|---------|
| session (default) | Current session only | Session review output (if chained) + retro/session-review provenance for current session work IDs |
| chapter | Active chapter | All retro/session-review provenance for work IDs in active chapter |
| arc | Active arc | All provenance for work IDs across all chapters in the active arc |
| epoch | Current epoch | All provenance across the current epoch |

### Evidence Query

In standalone mode:
1. Query memory for `retro-kss` provenance (K/S/S directives) scoped per above
2. Query memory for `session-review` provenance (session-level insights) scoped per above
3. Query memory for `process-review` provenance (prior proposals, including rejections)
4. Read recent governance events for pattern detection

In chained mode:
- `session_review_output` provides session insights and process proposals directly
- Memory queries supplement but are not required

### Minimum Viable Input

**Chained mode:** `session_review_output` satisfies the minimum. No further evidence required (though memory queries enrich analysis).

**Standalone mode:** If memory queries return zero results AND no session_review_output is provided:
1. Prompt operator via `AskUserQuestion`: "No accumulated observations found. What process concern would you like to review?"
2. If operator provides a concern: use that as the evidence seed for DIAGNOSE
3. If operator declines: log `ProcessReviewAbortedNoEvidence` governance event, return early with `success: true`, empty proposals

### Degradation

- Memory system unavailable: degrade to operator-provided observations only. Log `ProcessReviewDegradedNoMemory`
- Prior rejection data unavailable: proceed without awareness of prior rejections (acceptable for first invocation)

---

## Phase 2: DIAGNOSE

Analyze evidence to identify systemic patterns.

### Analysis Framework

| Question | Purpose | Example Output |
|----------|---------|----------------|
| What's recurring? | Patterns across multiple retros/sessions | "Ceremony overhead mentioned in 5 of last 8 retro-kss entries" |
| What's new? | First-time observations not seen before | "Session Review trigger predicate is a new design — no prior feedback" |
| What's systemic vs one-off? | Filter noise from signal | "Test fixture staleness is systemic (3 chapters); YAML quoting was one-off" |
| What has operator context? | Leverage process-review history | "Operator rejected L3 change for X in S420 — don't re-propose without new evidence" |

### Prior Rejection Awareness

If EVIDENCE phase found prior `ProcessReviewRejected` entries:
- Note which proposals were previously rejected and why
- Do NOT re-propose rejected items unless new evidence contradicts the rejection rationale
- If new evidence exists, explicitly state: "Previously rejected in S{N} because {reason}. New evidence: {evidence}"

---

## Phase 3: PROPOSE

Generate typed proposals from DIAGNOSE output.

### Proposal Types

| Type | Target | Example | Governance |
|------|--------|---------|------------|
| `l3_principle` | `.claude/haios/manifesto/L3/` | "Add L3.21: Ceremony depth scales with session complexity" | Highest — architectural |
| `l4_requirement` | `.claude/haios/manifesto/L4/functional_requirements.md` | "Add REQ-FEEDBACK-006: Session Review ceremony" | High — requirement |
| `config_change` | `.claude/haios/config/haios.yaml` | "Add session_review threshold to toggles" | Medium — configuration |
| `ceremony_change` | `.claude/skills/*/SKILL.md` | "Modify session-end to chain Session Review" | Medium — ceremony |
| `new_work` | Work item creation | "Create WORK-XXX for implementing X" | Low — spawns governed work |

### Proposal Format

For each proposal:
```yaml
- id: P{N}
  type: l3_principle|l4_requirement|config_change|ceremony_change|new_work
  title: "Brief description"
  target_file: "path/to/file" (or "new work item" for new_work)
  rationale: "Why this change — grounded in DIAGNOSE evidence"
  evidence: "Source observations/patterns from DIAGNOSE"
  diff_preview: "What the change looks like (approximate for operator review)"
  prior_rejection: null | "Rejected in S{N}: {reason}. New evidence: {evidence}"
```

---

## Phase 4: APPROVE

Per-proposal operator decision gate. This is a conversational gate backed by machine-verifiable governance events.

### Approval Process

1. Present all proposals to operator in a summary table
2. For each proposal, use `AskUserQuestion` with options: Approve / Reject / Modify
3. For **Approve**: log governance event BEFORE executing Write call:
   ```
   ProcessReviewApproved: {proposal_id}, target: {file_path}, scope: {type}, session: {N}
   ```
4. For **Reject**: log governance event with operator rationale:
   ```
   ProcessReviewRejected: {proposal_id}, rationale: {operator_reason}, session: {N}
   ```
5. For **Modify**: operator provides amended text, then treat as Approve with modified content

### Execution Order

Apply approved proposals in dependency order:
1. L3 principles first (highest level)
2. L4 requirements (derived from L3)
3. Config changes
4. Ceremony changes
5. New work items (spawned last)

### No Auto-Apply

No proposal is applied without:
1. Explicit operator approval via `AskUserQuestion`
2. Logged `ProcessReviewApproved` governance event
3. Both conditions met BEFORE the Write call executes

This ensures L3/L4 changes — the highest governance artifacts — are auditable post-hoc via governance-events.jsonl.

---

## COMMIT

Store all outputs to memory after APPROVE phase completes.

### Storage

**Approved proposals:**
```
ingester_ingest(
  content="Process Review S{N}\nScope: {scope}\nApproved:\n{approved_proposals_detail}",
  source_path="process-review:{session_number}",
  content_type_hint="techne"
)
```

**Rejected proposals (stored separately for future awareness):**
```
ingester_ingest(
  content="Process Review S{N} Rejections:\n{rejected_proposals_with_rationale}",
  source_path="process-review-rejected:{session_number}",
  content_type_hint="techne"
)
```

### Governance Event

Log ceremony completion:
```
ProcessReviewCompleted: session={N}, scope={scope}, proposed={N}, approved={N}, rejected={N}, spawned_work={list}
```

---

## Escape Hatches

| Escape | Trigger | Behavior |
|--------|---------|----------|
| No evidence (standalone) | Memory empty, operator declines to provide | `ProcessReviewAbortedNoEvidence`, return early |
| Memory unavailable | MCP/db down | Degrade to operator input, `ProcessReviewDegradedNoMemory` |
| Zero approvals | Operator rejects all proposals | Store rejections to memory, `ProcessReviewCompleted` with approved=0 |
| Operator exits early | Operator wants to stop mid-APPROVE | Store partial results, log what was decided |

**Principle:** Process Review never blocks session-end. Proposals stored to memory are never lost, even if operator defers action.

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Two invocation modes | Chained + standalone | Operator decision S435. Chained leverages session-review output; standalone enables ad-hoc reflection |
| Per-proposal governance events | ProcessReviewApproved/Rejected before Write | L3/L4 are highest governance artifacts — conversational approval alone is insufficient for audit trail (critique A9) |
| Rejected proposals stored to memory | Separate provenance tag | Prevents re-proposal without new evidence. Frequency of rejection IS signal (parallel to retro no-dedup) |
| Scope-conditional evidence | session/chapter/arc/epoch query depth | Scope must drive evidence gathering, not be cosmetic (critique A10) |
| No auto-apply | Operator MUST approve each proposal | System evolution is irreversible — REQ-GOVERN-002 |
| No auto-ADR creation | Proposals stored to memory, not as ADRs | Conflates ceremony with artifact lifecycle. Operator can invoke /new-adr as follow-up |
| Typed proposals | 5 types with target artifact | Different types flow differently: L3 changes need architectural review, new_work needs queue intake |

---

## Related

- **session-review-cycle:** Per-session reflection. Process Review may consume its output (chained mode)
- **retro-cycle:** Per-work-item reflection. Process Review aggregates retro K/S/S across sessions
- **session-end-ceremony:** Mechanical finalization. Process Review runs before it (if chained)
- **observation-triage-cycle:** Downstream consumer of retro extracts. Process Review is upstream (system evolution)
- **REQ-FEEDBACK-007:** Process Review ceremony requirement
- **REQ-GOVERN-002:** Irreversible actions require explicit permission
- **REQ-CEREMONY-001, 002, 005:** Ceremony contracts, proportional scaling
- Memory: 85235 (original E2.9 scoping), 85605 (ceremony overhead signal)
