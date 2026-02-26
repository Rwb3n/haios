---
template: investigation
status: complete
date: 2026-02-26
backlog_id: WORK-236
title: "context_pct Governance Event Consumer Design"
author: Hephaestus
session: 460
lifecycle_phase: conclude
spawned_by: WORK-233
related:
- WORK-233
- WORK-235
memory_refs:
- 89083
- 89084
- 89085
- 89086
- 89087
version: "2.0"
generated: 2026-02-26
last_updated: 2026-02-26
---
# Investigation: context_pct Governance Event Consumer Design

---

## Context

**Trigger:** WORK-233 (S459) added optional `context_pct` parameter to all governance event log functions. ADR-033 requires runtime consumers exist before closure. No caller currently populates this field.

**Problem Statement:** Where and how should `context_pct` be populated in governance events so that post-hoc analysis can determine context consumption per ceremony/phase?

**Prior Observations:**
- S458 observed ~60k tokens burned on close ceremony with no visibility
- Memory concepts 85989, 84897, 86041, 86021, 88223 converge on "context budget dashboard" need
- `_get_context_usage()` in UserPromptSubmit hook already parses transcript for accurate context %

---

## Prior Work Query

**Memory Query:** `memory_search_with_experience` with query: "context_pct governance events context window remaining percentage hook injection"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 85989 | "How much context has been spent on governance vs implementation?" | Direct: the question context_pct answers |
| 84897 | "Governance ceremonies consumed significant context" | Confirms the problem |
| 86041 | "Context budget dashboard — real-time governance% vs implementation%" | Vision for how data would be used |
| 88223 | "Add context budget tracking mechanism for multi-ceremony closure chains" | Downstream consumer desire |
| 88175 | "Governance layer has opportunity to estimate context consumption" | Identifies governance_layer.py as possible injection point |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] No prior investigation on context_pct injection; WORK-235 is parent investigation on ceremony token efficiency

---

## Objective

Where should context_pct be injected into governance events, and what is the cheapest correct approach given hook data availability constraints?

---

## Scope

### In Scope
- Which runtime callers should pass context_pct to log_* functions
- How to obtain context percentage in each caller's execution context
- Token cost of context_pct calculation per call site
- Design for implementation work item

### Out of Scope
- Implementing the actual injection (that's the spawned work)
- Dashboard/visualization of context_pct data
- Changing the governance_events.py API (already done in WORK-233)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | 8 | Runtime callers of log_* functions |
| Hypotheses to test | 3 | Listed below |
| Expected evidence sources | 3 | Codebase (hooks, lib, modules) |
| Estimated complexity | Low | Small effort investigation |

---

## Hypotheses

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | UserPromptSubmit hook should write context_pct to a shared file (e.g., haios-status-slim.json) and all log_* callers should read it from there | Med | Check if slim is already read by callers; assess I/O cost | 1st |
| **H2** | Only phase-transition events (CyclePhaseEntered) need context_pct, and cycle_state.py + MCP cycle_set should inject it via transcript parsing | Med | Check if cycle_state.py has access to transcript_path or slim; assess frequency | 2nd |
| **H3** | context_pct should be injected only at session-level events (SessionStarted/SessionEnded) since per-event tracking is excessive overhead for the analysis value | Low | Assess whether session-only granularity answers the governance % question | 3rd |

---

## Evidence Collection

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| `transcript_path` NOT in PostToolUse/PreToolUse hook_data | `post_tool_use.py:30-34`, `pre_tool_use.py:1-20` | H1 | Direct transcript parsing impossible in these hooks |
| `_get_context_usage()` parses transcript JSONL for real token count | `user_prompt_submit.py:331-388` | H1 | Accurate source, runs on every prompt already |
| UserPromptSubmit already computes context_usage string | `user_prompt_submit.py:92-95` | H1 | Could extract float and write to slim |
| `_read_slim()` already reads haios-status-slim.json | `user_prompt_submit.py:149-163` | H1 | Slim pattern already established |
| `cycle_state.py` calls `log_phase_transition` inside PostToolUse context | `cycle_state.py:120-123` | H2 | No transcript_path available |
| `session_mgmt.py` calls `log_session_start` from MCP tool | `session_mgmt.py:89-91` | H2, H3 | MCP tool has no transcript access |
| `session_end_actions.py` calls `log_session_end` from Stop hook | `session_end_actions.py:72-74` | H3 | Stop hook HAS transcript_path |
| 12 runtime call sites across 8 files | grep results above | H1, H2 | Modifying all is O(12) edits |
| `_append_event()` already conditionally includes context_pct | `governance_events.py:494-495` | All | Only writes when not None — backward compatible |
| haios-status-slim.json is read by UserPromptSubmit on every prompt | `user_prompt_submit.py:77` | H1 | File is already hot in filesystem cache |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 85989 | Governance vs implementation context split question | H1, H2 | Per-event granularity needed to answer this |
| 88223 | Context budget tracking for multi-ceremony chains | H2 | Phase transitions are key measurement points |

---

## Findings

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1: Shared file (slim) as context_pct relay | **Confirmed** | UserPromptSubmit already computes context %, slim is already read everywhere, transcript_path absent from other hooks. This is the only viable relay mechanism. | High |
| H2: Only phase-transition events need context_pct | **Refuted** | Phase transitions are valuable, but session start/end and gate violations also need context_pct for complete governance-vs-implementation analysis. Selective injection would leave gaps. | Med |
| H3: Session-level events only | **Refuted** | Session-level only gives start/end snapshots. Cannot answer "how much context did the close ceremony consume?" which requires per-phase-transition deltas. | High |

### Detailed Findings

#### Finding 1: transcript_path Availability Constraint

**Evidence:**
- UserPromptSubmit hook_data includes `transcript_path` (`user_prompt_submit.py:61`)
- Stop hook_data includes `transcript_path` (`stop.py:31`)
- PostToolUse hook_data does NOT include `transcript_path` (`post_tool_use.py:30-34`)
- PreToolUse hook_data does NOT include `transcript_path` (confirmed by grep)

**Analysis:** Most governance event callers execute in PostToolUse or PreToolUse context (cycle_state, tier_detector, critique_injector, pre_tool_use). They cannot directly parse the transcript for context percentage.

**Implication:** A relay mechanism is needed. The UserPromptSubmit hook must compute context_pct and write it to a shared location that other hooks can read.

#### Finding 2: Slim File as Natural Relay

**Evidence:**
- `haios-status-slim.json` is already read by UserPromptSubmit on every prompt (`user_prompt_submit.py:77`)
- `_get_context_usage()` already computes remaining % from transcript (`user_prompt_submit.py:331-388`)
- The slim file already contains `session_state` with `active_cycle`, `current_phase`, `work_id`

**Analysis:** Adding a `context_pct` field to the slim file is the natural extension. UserPromptSubmit writes it (already computes the value); other callers read it (already read slim for session_state). Zero new file I/O paths.

**Implication:** Design: UserPromptSubmit writes `context_pct` into slim. All `log_*` callers read `context_pct` from slim via a shared helper.

#### Finding 3: Call Site Injection Strategy

**Evidence:**
12 runtime call sites across 8 files:

| Caller | File | Function Called | Hook Context |
|--------|------|-----------------|--------------|
| cycle_state.advance_cycle_phase | cycle_state.py:120 | log_phase_transition | PostToolUse |
| cycle_state.write_cycle_state | cycle_state.py:264 | log_phase_transition | MCP tool |
| session_mgmt.start_session | session_mgmt.py:89 | log_session_start | MCP tool |
| session_end_actions.log_session_ended | session_end_actions.py:72 | log_session_end | Stop hook |
| tier_detector.detect_and_log_tier | tier_detector.py:97 | log_tier_detected | PreToolUse |
| critique_injector | critique_injector.py:185,194 | log_critique_injected, log_gate_violation | PreToolUse |
| governance_layer.validate_* | governance_layer.py:110,216 | log_validation_outcome | Module (any) |
| ceremony_runner.run_ceremony | ceremony_runner.py:136 | log_phase_transition | Module (any) |
| cycle_runner.* | cycle_runner.py:203,236,275,480 | log_phase_transition, log_validation_outcome | Module (any) |
| pre_tool_use._log_gate_violation | pre_tool_use.py:548 | log_gate_violation | PreToolUse |
| mcp_server._log_governance_gate | mcp_server.py:123 | _append_event | MCP server |
| coldstart_orchestrator | coldstart_orchestrator.py:107 | log_session_end | MCP tool |

**Analysis:** Rather than modifying all 12 call sites, inject context_pct inside `_append_event()` itself by reading slim. This is a single-point change. The per-function `context_pct` parameter from WORK-233 becomes the override mechanism (callers CAN pass explicit value), while `_append_event` auto-populates from slim when not explicitly provided.

**Implication:** Two-change implementation:
1. UserPromptSubmit: write `context_pct` float to slim after computing it
2. `_append_event()`: auto-read `context_pct` from slim when caller doesn't provide it

---

## Design Outputs

### Mechanism Design

```
TRIGGER: Every UserPromptSubmit hook invocation

ACTION:
    1. UserPromptSubmit._get_context_usage() computes remaining % (already exists)
    2. NEW: Extract float from string, write to slim["context_pct"]
    3. Any log_* function is called by any hook/module
    4. _append_event() reads slim["context_pct"] if caller didn't pass explicit value
    5. Event written to governance-events.jsonl with context_pct field

OUTCOME: All governance events carry context_pct automatically
```

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Relay via slim, not transcript | Slim file | transcript_path unavailable in PostToolUse/PreToolUse; slim already shared |
| Auto-inject in _append_event, not per caller | Single injection point | 1 change vs 12; WORK-233 kwargs become override only |
| context_pct as float 0-100 representing remaining % | Remaining %, not used % | Aligns with existing `_get_context_usage` output and `[CONTEXT: X% remaining]` format |
| Staleness acceptable | Read last-written value | Slim written on each prompt; events between prompts use prior value. Acceptable because: (a) context doesn't change between prompts (only API calls consume context), (b) analysis wants approximate phase-level granularity, not per-token |

---

## Spawned Work Items

### Immediate (Can implement now)

- [x] **WORK-237: Implement context_pct Auto-Injection via Slim Relay**
  - Description: (1) UserPromptSubmit writes `context_pct` float to slim, (2) `_append_event()` reads from slim when not explicitly provided
  - Fixes: WORK-233 dead infrastructure — makes context_pct field actually populated
  - Effort: small (2 file changes + tests)
  - Spawned via: `scaffold_work` with `spawned_by: WORK-236`

### Not Spawned Rationale (if no items)

N/A — one work item spawned.

---

## Session Progress Tracker

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 460 | 2026-02-26 | EXPLORE→HYPOTHESIZE→VALIDATE | Complete | Full investigation in single session |

---

## Ground Truth Verification

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-H3 have verdict | [x] | H1 confirmed, H2/H3 refuted |
| Evidence has sources | All findings have file:line | [x] | All codebase evidence cited |
| Spawned items created | Items created via scaffold_work | [x] | WORK-237 created |
| Memory stored | ingester_ingest called | [x] | concept_ids: 89083-89087 |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | No | Small effort investigation; main agent explored freely per investigation-cycle EXPLORE phase guidance (Session 262 pattern) |
| Are all evidence sources cited with file:line or concept ID? | Yes | |
| Were all hypotheses tested with documented verdicts? | Yes | |
| Are spawned items created (not just listed)? | Yes | WORK-237 |
| Is memory_refs populated in frontmatter? | Yes | 89083-89087 (auto-linked by hook) |

---

## References

- Spawned by: WORK-233 (Add context_pct Field to Governance Events)
- Parent investigation: WORK-235 (Post-Work Ceremony Token Efficiency)
- @.claude/haios/lib/governance_events.py (target infrastructure)
- @.claude/hooks/hooks/user_prompt_submit.py (context_pct source)
- @.claude/hooks/hooks/post_tool_use.py (hook data constraints)

---
