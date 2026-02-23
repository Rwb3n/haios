---
template: implementation_plan
subtype: design
status: complete
date: 2026-02-23
backlog_id: WORK-102
title: "Session and Process Review Ceremonies"
author: Hephaestus
lifecycle_phase: plan
session: 435
version: "1.5"
generated: 2026-02-23
last_updated: 2026-02-23T17:45:03
---
# Design Plan: Session and Process Review Ceremonies

---

## Goal

Define input/output contracts, trigger conditions, and skill specifications for two new ceremonies: Session Review (per-session execution quality reflection) and Process Review (system evolution reflection).

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | session-end-ceremony SKILL.md (add session-review reference) |
| New files to create | 2 | `session-review-cycle/SKILL.md`, `process-review-cycle/SKILL.md` |
| Dependencies | 3 | session-end-ceremony, retro-cycle, functional_requirements.md |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| SPECIFY (author skill files) | 30 min | High |
| CRITIQUE (review design) | 10 min | High |
| COMPLETE (update references) | 10 min | High |
| **Total** | **50 min** | |

---

## Current State vs Desired State

### Current State

**What exists now:** The feedback chain covers bottom-up scope reviews: work (retro-cycle) -> chapter (close-chapter) -> arc (close-arc) -> epoch (close-epoch) -> requirements. Session-end-ceremony handles mechanical session finalization (orphan check, event log). No ceremony addresses "how did this session go?" or "what should change in the system?"

**Problem:** Two natural review patterns observed in S314 have no formal ceremony:
1. **Session Review** ("what went well / could've gone better") — cross-work-item session-level reflection is lost. Retro-cycle reflects per-work-item; nothing aggregates across the session.
2. **Process Review** ("keep doing / should be doing / stop doing") — operator-initiated system evolution has no structured ceremony. Changes to L3/L4/config happen ad-hoc.

### Desired State

**What should exist:** Two ceremony skills with explicit contracts, proportional triggers, and clear composition with existing ceremonies.

**Outcome:** The feedback chain becomes complete — from per-work-item (retro) through per-session (session review) to system evolution (process review). Operator reflections become structured, traceable, and stored to memory.

---

## Detailed Design

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Session Review trigger | Conditional automatic (computable predicate) | Operator decision S435. Run only when substantial work completed — avoids ceremony overhead for trivial sessions (mem:85605) |
| Process Review composition | Both modes (standalone + chained) | Operator decision S435. Standalone enables ad-hoc operator reflection; chained mode consumes Session Review output when available |
| Session Review scope | Per-session, cross-work-item | Distinct from retro-cycle (per-work-item) and session-end (mechanical). Aggregates across all work touched in session |
| Process Review output | Proposed L3/L4/config modifications | Not just memory — produces actionable system change proposals for operator approval |
| Session Review placement | Before session-end-ceremony, after all retro-cycles | Consumes retro outputs and session event log; session-end is mechanical (no judgment needed after) |
| Proportional scaling | Reuse retro-cycle's Phase 0 pattern | Computable predicate decides ceremony depth. Consistent with E2.8 theme |
| No auto-apply for Process Review | Proposals require operator approval | System evolution is irreversible — operator MUST approve L3/L4 changes (REQ-GOVERN-002) |

### Design Content

#### 1. Session Review Ceremony

**Identity:** Per-session execution quality reflection. Aggregates across all work items touched in a session. Answers: "How did execution go?"

**Trigger:** Conditional automatic. Computable predicate checks:
- At least 1 work item CLOSED this session (retro-cycle completed, `WorkClosed` event in session-log.jsonl)
- OR at least 2 `RetroCycleCompleted` events in governance-events.jsonl for this session
- If predicate fails: skip with governance event `SessionReviewSkipped`
- **Note:** The predicate requires retro-cycle completion, not just CHECK/DONE phase, because retro output is the primary evidence source for ASSESS phase (critique A4)

**Input Contract:**

| Field | Required | Source | Description |
|-------|----------|--------|-------------|
| session_number | MUST | `.claude/session` | Current session number |
| session_events | MUST | `.claude/haios/session-log.jsonl` | Structured session event log |
| retro_outputs | SHOULD | Memory query: `source_adr LIKE 'retro-reflect:%'` filtered to work IDs from session events | Per-work-item retro findings. **Degradation:** If query returns zero results, log `SessionReviewDegradedNoRetroData` and proceed with session events only. ASSESS phase operates in lightweight mode |
| work_items_touched | MUST | Session events (phase, close, spawn events) | List of work IDs active this session |

**Phases:**

| Phase | Pressure | Function |
|-------|----------|----------|
| GATHER | Collection | Read session events, retro outputs, work items touched |
| ASSESS | Synthesis | Cross-work-item patterns ONLY. **Exclusion rule:** Do not restate individual work-item findings already captured in retro. Identify patterns that emerge from viewing the session as a whole — execution flow quality, cross-item dependencies, session-level decisions, tooling friction. If only 1 work item was closed, focus on session execution quality (time allocation, ceremony overhead, context management) rather than work-item content |
| STORE | Persistence | Store to memory with `session-review:{session}` provenance |

**Output Contract:**

| Field | Guaranteed | Description |
|-------|------------|-------------|
| success | Always | Whether ceremony completed |
| session_insights | On success | Cross-work-item observations (distinct from per-item retro) |
| execution_quality | On success | Brief assessment: smooth / friction / blocked |
| process_proposals | On success | Proposed process changes (input for Process Review if chained) |
| memory_concept_ids | On success | Stored concept IDs |

**Side Effects:**
- Store session-level insights to memory (`session-review:{session}` provenance)
- Log `SessionReviewCompleted` governance event

**Proportional Scaling:**

| Scale | Behavior |
|-------|----------|
| Single work item completed | Lightweight: 1-2 session-level observations beyond what retro already captured |
| Multiple work items / complex session | Full: cross-item patterns, execution quality assessment, process proposals |

**Escape Hatch:** `--skip-session-review` flag. Logs `SessionReviewSkipped`, returns early. Never blocks session-end.

---

#### 2. Process Review Ceremony

**Identity:** System evolution reflection. Answers: "What should change in the system?" Produces proposed modifications to L3/L4/config/ceremonies.

**Trigger:** Two modes:
1. **Chained from Session Review:** When Session Review's STORE phase completes and `process_proposals` is non-empty, the agent prints a formatted offer block: "Session Review surfaced {N} process proposals. Run Process Review? (Y/N or /process-review later)". The agent waits for operator response via `AskUserQuestion`. If declined, proposals remain in memory for future standalone invocation. Session-end-ceremony proceeds regardless of operator response.
2. **Standalone (operator-invoked):** `/process-review` command. Gathers evidence independently from memory

**Input Contract:**

| Field | Required | Source | Description |
|-------|----------|--------|-------------|
| session_review_output | MAY | Session Review output (if chained) | Session-level insights and proposals |
| accumulated_observations | SHOULD | Memory query (retro-kss, session-review provenance, recent epochs) | Cross-session K/S/S patterns |
| scope | SHOULD | Operator or default "session" | Review scope determines EVIDENCE phase query depth. "session": query retro/session-review provenance from current session work IDs only. "chapter": query all retro/session-review provenance for work IDs in the active chapter. "arc": query all provenance for work IDs across all chapters in the active arc. "epoch": query all provenance across the current epoch. Default: "session" |

**Phases:**

| Phase | Pressure | Function |
|-------|----------|----------|
| EVIDENCE | Collection | Gather inputs: session review output, accumulated observations, K/S/S patterns from memory. **Minimum viable input:** In standalone mode with no memory results and no session-review output, EVIDENCE phase requires operator to provide at least one observation prompt (via `AskUserQuestion`: "What process concern would you like to review?"). If operator declines, ceremony ends with `ProcessReviewAbortedNoEvidence` governance event. In chained mode, session-review output satisfies the minimum |
| DIAGNOSE | Analysis | Identify systemic patterns vs one-off issues. What's recurring? What's new? |
| PROPOSE | Prescription | Generate typed proposals: L3 principle change, L4 requirement change, config change, ceremony change, new work item |
| APPROVE | Gate | Present proposals to operator via `AskUserQuestion`. Operator approves/rejects each. For each approved proposal, log a distinct governance event `ProcessReviewApproved: {proposal_id}, target: {file_path}, scope: {l3/l4/config/ceremony/work}` BEFORE executing the Write call. For rejected proposals, log `ProcessReviewRejected: {proposal_id}, rationale: {operator_reason}`. No auto-apply without per-proposal governance event |

**Output Contract:**

| Field | Guaranteed | Description |
|-------|------------|-------------|
| success | Always | Whether ceremony completed |
| proposals | On success | List of typed proposals with target artifact and rationale |
| approved_proposals | On success | Subset approved by operator |
| rejected_proposals | On success | Subset rejected by operator, with rejection rationale. Stored to memory so future Process Reviews are aware of prior rejections |
| applied_changes | On success | Files actually modified (after operator approval) |
| spawned_work_ids | On success | Work item IDs created for `new_work` type proposals (distinct from file modifications) |
| memory_concept_ids | On success | Stored concept IDs |

**Proposal Types:**

| Type | Target | Example |
|------|--------|---------|
| l3_principle | `.claude/haios/manifesto/L3/` | "Add L3.21: Ceremony depth should scale with session complexity" |
| l4_requirement | `.claude/haios/manifesto/L4/functional_requirements.md` | "Add REQ-FEEDBACK-006: Session Review ceremony" |
| config_change | `.claude/haios/config/haios.yaml` | "Add session_review threshold to toggles" |
| ceremony_change | `.claude/skills/*/SKILL.md` | "Modify session-end to chain Session Review" |
| new_work | Work item creation | "Create WORK-XXX for implementing Session Review automation" |

**Side Effects:**
- Store proposals to memory (`process-review:{session}` provenance)
- Apply approved proposals (file modifications)
- Log `ProcessReviewCompleted` governance event
- Optionally spawn work items for approved proposals that need implementation

**Escape Hatches:**
- Operator can exit at APPROVE phase with zero approvals. Proposals still stored to memory for future reference.
- EVIDENCE phase with zero evidence in standalone mode: operator prompted for observation; if declined, `ProcessReviewAbortedNoEvidence` logged, ceremony returns early.
- Memory system unavailable: degrade to operator-provided observations only. Log `ProcessReviewDegradedNoMemory`.

---

#### 3. Composition with Existing Ceremonies

```
Session work complete
  |
  +-> retro-cycle (per work item, invoked by /close)
  |     Output: retro-reflect, retro-kss, retro-extract
  |
  +-> session-review-cycle (conditional automatic)
  |     Input: session events + retro outputs
  |     Output: session insights + process proposals
  |
  +-> process-review-cycle (optional, operator-offered if proposals exist)
  |     Input: session review output OR standalone evidence
  |     Output: approved system modifications
  |
  +-> session-end-ceremony (mechanical)
        Orphan check, git status, event log
```

The chain is: retro (per-item) -> session-review (per-session) -> process-review (system evolution) -> session-end (mechanical). Each step is independently completable (REQ-LIFECYCLE-001). Chaining is caller choice (REQ-LIFECYCLE-004).

### Open Questions

**Q: Should Session Review query memory for cross-session patterns, or leave that to Process Review?**

Session Review should focus on THIS session only. Cross-session pattern analysis belongs to Process Review, which has the broader scope mandate.

**Q: Where do the SKILL.md files go?**

`.claude/skills/session-review-cycle/SKILL.md` and `.claude/skills/process-review-cycle/SKILL.md`, following existing convention.

**Q: Should Process Review proposals be stored as ADRs?**

No. Proposals are stored to memory. If a proposal is significant enough (architectural), the operator can invoke `/new-adr` as a follow-up. Process Review should not auto-create ADRs — that conflates the ceremony with the artifact lifecycle.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Session Review trigger predicate | work item CLOSED (retro completed), or RetroCycleCompleted count >= 2 | Both (OR) | Requires retro completion, not just phase entry — retro output is the primary evidence source for ASSESS |
| Process Review scope default | "session" vs "chapter" | "session" | Most common invocation is end-of-session; broader scope is explicit opt-in |

---

## Implementation Steps

### Step 1: Author Session Review Skill
- [ ] Create `.claude/skills/session-review-cycle/SKILL.md` with full ceremony contract
- [ ] Include: frontmatter (input/output contracts), phases, scaling, escape hatches
- [ ] Follow retro-cycle SKILL.md as structural template

### Step 2: Author Process Review Skill
- [ ] Create `.claude/skills/process-review-cycle/SKILL.md` with full ceremony contract
- [ ] Include: frontmatter, phases, proposal types, approval gate
- [ ] Follow retro-cycle SKILL.md as structural template

### Step 3: Update References
- [ ] **MUST:** Add both ceremonies to CLAUDE.md ceremonies table
- [ ] **MUST:** Add REQ-FEEDBACK-006 and REQ-FEEDBACK-007 to functional_requirements.md
- [ ] **MUST:** Update session-end-ceremony SKILL.md pre-conditions to reference session-review-cycle (consumer update, critique A6)
- [ ] Update CH-064 chapter manifest with completion status

---

## Verification

- [ ] Both SKILL.md files exist with complete contracts
- [ ] Input/output contracts are explicit (no ambiguous fields)
- [ ] Composition with existing ceremonies is clear
- [ ] Requirements trace: REQ-FEEDBACK-006 -> Session Review, REQ-FEEDBACK-007 -> Process Review
- [ ] **MUST:** All READMEs current

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Ceremony overhead for lightweight sessions | Medium | Computable predicate skips trivially (Phase 0 pattern) |
| Process Review proposals not actionable | Medium | Typed proposals with target artifact — not vague suggestions |
| Session Review duplicates retro-cycle | Low | Distinct scope: retro = per-item, session review = cross-item |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 435 | 2026-02-23 | - | In progress | Design plan authored |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-102/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Session Review ceremony defined with input/output contract | [x] | `.claude/skills/session-review-cycle/SKILL.md` — full frontmatter + 3-phase ceremony |
| Process Review ceremony defined with input/output contract | [x] | `.claude/skills/process-review-cycle/SKILL.md` — full frontmatter + 4-phase ceremony |
| Both added to Feedback category in ceremonies arc | [x] | `CLAUDE.md:86` — Feedback row includes Session Review, Process Review |
| Skills created for both ceremonies | [x] | Both paths verified via Glob |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/skills/session-review-cycle/SKILL.md` | Exists, contract complete | [x] | 3 phases, trigger predicate, scaling, escape hatches |
| `.claude/skills/process-review-cycle/SKILL.md` | Exists, contract complete | [x] | 4 phases, proposal types, APPROVE gate, per-proposal governance events |
| `.claude/haios/manifesto/L4/functional_requirements.md` | REQ-FEEDBACK-006, 007 added | [x] | Both in registry (line 63-64) and detailed section (line 475-476) |
| `.claude/skills/session-end-ceremony/SKILL.md` | Pre-conditions updated to reference session-review-cycle | [x] | Line 97 |
| `CLAUDE.md` | Ceremonies table updated | [x] | Line 86 |

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | All 5 files verified via Grep |
| Any deviations from plan? | No | |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Design artifact complete
- [x] **MUST:** All WORK.md deliverables verified complete
- [ ] WHY captured (reasoning stored to memory)
- [x] **MUST:** READMEs updated in all modified directories (no README files in skill dirs)

---

## References

- REQ-FEEDBACK-001 to 005 (existing feedback chain)
- REQ-CEREMONY-001, 002, 005 (ceremony contracts, proportional scaling)
- retro-cycle SKILL.md (structural template, per-item reflection)
- session-end-ceremony SKILL.md (mechanical session finalization)
- WORK-206 (session event log — provides session-log.jsonl input)
- Memory: 85235 (original E2.9 scoping), 85605 (ceremony overhead signal), 85945 (ceremonies as pattern instances)

---
