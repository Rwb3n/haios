---
template: investigation
status: complete
date: 2026-01-15
backlog_id: INV-065
title: Session State Cascade Architecture
author: Hephaestus
session: 193
lifecycle_phase: conclude
spawned_by: null
related: []
memory_refs:
- 81383
- 81386
- 81389
- 81392
version: '2.0'
generated: 2025-12-22
last_updated: '2026-01-16T20:46:20'
---
# Investigation: Session State Cascade Architecture

@docs/README.md
@docs/epistemic_state.md

<!-- FILE REFERENCE REQUIREMENTS (MUST - Session 171 Learning)

     1. MUST use full @ paths for prior work:
        CORRECT: @docs/work/active/INV-052/SECTION-17-MODULAR-ARCHITECTURE.md
        WRONG:   INV-052, "See INV-052"

     2. MUST read ALL @ referenced files BEFORE starting EXPLORE phase:
        - Read each @path listed at document top
        - For directory references (@docs/work/active/INV-052/), MUST Glob to find all files
        - Document key findings in Prior Work Query section
        - Do NOT proceed to EXPLORE until references are read

     3. MUST Glob referenced directories:
        @docs/work/active/INV-052/ → Glob("docs/work/active/INV-052/**/*.md")
        Then read key files (SECTION-*.md, WORK.md, investigations/*.md)

     Rationale: Session 171 wasted ~15% context searching for INV-052 in wrong
     location because agent ignored @ references and guessed file locations.
-->

<!-- TEMPLATE GOVERNANCE (v2.0 - E2-144)

     INVESTIGATION CYCLE: HYPOTHESIZE -> EXPLORE -> CONCLUDE

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: Pure discovery, no design outputs needed"
     - "SKIPPED: Single hypothesis, no complex mapping required"
     - "SKIPPED: External research only, no codebase evidence"

     This prevents silent section deletion and ensures conscious decisions.

     SUBAGENT REQUIREMENT (L3):
     For EXPLORE phase, you MUST invoke investigation-agent subagent:
     Task(prompt='EXPLORE: {hypothesis}', subagent_type='investigation-agent')

     Rationale: Session 101 proved L2 ("RECOMMENDED") guidance is ignored ~20% of time.
     L3 enforcement ensures structured evidence gathering.
-->

---

## Discovery Protocol (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Query memory first | SHOULD | Search for prior investigations on topic before starting |
| Document hypotheses | SHOULD | State what you expect to find before exploring |
| Use investigation-agent | MUST | Delegate EXPLORE phase to subagent for structured evidence |
| Capture findings | MUST | Fill Findings section with evidence, not assumptions |

---

## Context

<!-- HYPOTHESIZE PHASE: Describe background before exploring -->

**Trigger:** E2-291 implementation revealed queue context propagation gap - survey-cycle picks a queue but routing-gate doesn't know which queue was used.

**Problem Statement:** Session state in haios-status-slim.json is dead code - the schema exists (E2-286) but nothing writes to it, causing loss of cycle/queue context between skill invocations.

**Prior Observations:**
- E2-286/287/288 built session_state schema and warnings but not the write path
- work_cycle shows stale data (E2-279) despite completing E2-291
- INV-062 found CycleRunner must be stateless (L4 invariant) - hooks are the answer
- Memory 78844: "Verified cascade hook gap - logs events but doesn't invoke just cascade"
- Operator insight: "We have the compute. Latency is not a problem."

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "session state tracking cycle enforcement hooks cascade"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 81329 | CycleRunner must be stateless (L4 invariant), hooks can't track session state | Constraint - hooks must write state, not CycleRunner |
| 81303 | Investigation into session state tracking / CycleRunner wiring (Chariot chapter) | Prior attempt in INV-062 |
| 78844 | Verified cascade hook gap - logs events but doesn't invoke just cascade | Confirms gap exists |
| 68623 | Formalizing session state transitions for robustness | Pattern - formal state transitions |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] Found: INV-062 (Session State Tracking and Cycle Enforcement Architecture) - concluded that hard enforcement requires SDK (E4), but hook cascade is viable for soft enforcement

---

## Objective

<!-- One clear question this investigation will answer -->

**Primary:** How should PostToolUse hook cascade session_state updates on Skill() invocation to enable queue context propagation and cycle observability?

**Secondary:** What extended session_state schema is needed (active_queue, phase_history)?

---

## Scope

### In Scope
- PostToolUse hook modification to detect Skill() and cascade updates
- Extended session_state schema design (active_queue, phase_history)
- Phase update mechanism within cycles
- Survey-cycle → routing-gate context flow

### Out of Scope
- Hard enforcement (requires SDK - Epoch 4)
- CycleRunner modifications (must stay stateless per L4)
- Memory integration changes

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | ~5 | post_tool_use.py, status.py, haios-status-slim.json schema |
| Hypotheses to test | 3 | Listed below |
| Expected evidence sources | 3 | Codebase, Memory, INV-062 |
| Estimated complexity | Medium | Hook modification + schema extension |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | PostToolUse can detect Skill() invocations and extract skill_name from tool_input | High | Read post_tool_use.py, check tool_input structure | 1st |
| **H2** | session_state can be extended with active_queue without breaking existing consumers | High | Grep for session_state consumers, verify schema flexibility | 2nd |
| **H3** | Phase updates require explicit markers (recipe calls in skill prose) since tool patterns are ambiguous | Medium | Analyze what distinguishes PLAN vs DO vs CHECK phases by tool use | 3rd |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [x] Query memory for prior learnings on topic (concepts 78846, 79130, 81303, 81329)
2. [x] Search codebase for relevant patterns (post_tool_use.py, settings.local.json, status.py)
3. [x] Read identified files and document findings

### Phase 2: Hypothesis Testing
4. [x] Test H1: Read post_tool_use.py, settings.local.json hook matcher - Skill NOT in list
5. [x] Test H2: Grep session_state consumers (21 files), verify defensive checks
6. [x] Test H3: Grep skills for "just set-cycle" (no matches), verify phase ambiguity

### Phase 3: Synthesis
7. [x] Compile evidence table
8. [x] Determine verdict for each hypothesis
9. [ ] Identify spawned work items

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| PostToolUse hook matcher excludes Skill | `.claude/settings.local.json:130` | H1 No | Only Edit/Write/Bash/Read/etc. - no Skill |
| INV-062: "No hook fires for Skill tool" | `INV-062:252` | H1 No | Skills are markdown reads, not tool events |
| INV-062: "Skill() is not hookable" | `INV-062:197` | H1 No | Claude reads markdown directly |
| session_state structure exists with nulls | `.claude/haios-status-slim.json:27-32` | H2 Yes | Schema designed for extension |
| status.py generates hardcoded nulls | `.claude/lib/status.py:940-945` | H2 Yes | Write path missing, not schema |
| UserPromptSubmit has defensive check | `.claude/hooks/hooks/user_prompt_submit.py:147-149` | H2 Yes | `if "session_state" not in slim: return None` |
| Skills do NOT contain `just set-cycle` | Grep .claude/skills - no matches | H3 Yes | Design exists but not implemented |
| `just set-cycle` recipe works | `justfile:244-245` | H3 Yes | JSON manipulation via Python |
| EPOCH.md: "recipe call in skill step" | `.claude/haios/epochs/E2/EPOCH.md:240` | H3 Yes | Architecture endorses pattern |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 78846 | PostToolUse cascade detection logs events but never acts | H1 partial | Cascade triggers logged, not actioned |
| 81329 | CycleRunner must be stateless, hooks can't track state | H1 No | Confirms hooks are wrong locus |
| 81303 | Investigation into session state tracking (INV-062) | All | Prior work foundation |
| 80783 | PostToolUse handler can bridge this gap | H3 Yes | But for non-Skill tools |

### External Evidence (if applicable)

**SKIPPED:** Internal architecture investigation, no external sources needed.

---

## Findings

<!-- EXPLORE PHASE: Document findings as discovered
     CONCLUDE PHASE: Synthesize into coherent narrative

     DoD: This section MUST have actual content, not placeholder text -->

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 (PostToolUse detects Skill) | **Refuted** | Skill NOT in hook matcher (`settings.local.json:130`). INV-062 confirmed: "No hook fires for Skill tool" - Skills are markdown reads, not tool events. | High |
| H2 (session_state extensible) | **Confirmed** | Schema exists (`haios-status-slim.json:27-32`), consumers use defensive checks (`user_prompt_submit.py:147-149`). Adding active_queue is safe. | High |
| H3 (Phase needs explicit markers) | **Confirmed** | Skills do NOT call `just set-cycle` (Grep: no matches). INV-062 designed this but never implemented. Tool patterns ambiguous across phases. | High |

### Detailed Findings

#### Finding 1: Skill() Is Fundamentally Unhookable

**Evidence:**
```json
// settings.local.json:128-137
"PostToolUse": [{
  "matcher": "Edit|Write|MultiEdit|Bash|Read|Grep|Glob|mcp__haios-memory__ingester_ingest",
  // Note: NO "Skill" in this list
}]
```

From INV-062:197:
> "Skills are markdown files in .claude/skills/"
> "Skill(skill="X") causes Claude to read the markdown file"
> "No PreToolUse/PostToolUse hook fires for Skill tool"

**Analysis:** Skills are not tools in the Claude Code hook sense. When agent invokes `Skill(skill="implementation-cycle")`, Claude reads the markdown file. This is a Read operation, not a distinct tool event. Hooks cannot distinguish "Read skill file" from "Read any file."

**Implication:** PostToolUse-based cascade is architecturally impossible. Cascade MUST use explicit recipe calls within skill prose.

#### Finding 2: session_state Schema Is Safely Extensible

**Evidence:**
```json
// haios-status-slim.json:27-32 - Current schema
"session_state": {
    "active_cycle": null,
    "current_phase": null,
    "work_id": null,
    "entered_at": null
}
```

```python
# user_prompt_submit.py:147-149 - Defensive consumer
if "session_state" not in slim:
    return None  # Backward compat
```

**Analysis:** session_state schema was designed in E2-286 with nullability built in. All consumers check key existence before access. Adding active_queue or phase_history will not break existing functionality.

**Implication:** Schema extension is safe. Implementation work is adding the write path, not modifying schema.

#### Finding 3: Recipe Calls Are The Only Viable Cascade Mechanism

**Evidence:**
```bash
# justfile:244-245 - Working recipe
set-cycle cycle phase work_id:
    @python -c "import json; from datetime import datetime; p='.claude/haios-status-slim.json'; ..."
```

From EPOCH.md:240:
> "If it needs to reliably happen, make it a recipe call in a skill step"

From INV-062 (designed but NOT implemented):
> "Skill markdown includes Python callout at start: `just set-cycle {cycle_id} {phase} {work_id}`"

**Analysis:** Architecture is sound - just never implemented. Skills need Bash calls to `just set-cycle` at phase entry points. This is "soft enforcement" - relies on Claude following instructions but creates signal path for observability.

**Implication:** Implementation needs to add `just set-cycle` calls to skill prose at skill entry, phase transitions, and skill exit.

---

## Design Outputs

<!-- If investigation produces architectural designs, document them here
     SKIP this section if investigation is pure discovery with no design outputs -->

### Schema Design: Extended session_state

```yaml
# Extended session_state in haios-status-slim.json
session_state:
  active_cycle: string | null     # e.g., "implementation-cycle"
  current_phase: string | null    # e.g., "PLAN", "DO", "CHECK", "DONE"
  work_id: string | null          # e.g., "E2-291"
  entered_at: ISO8601 | null      # When cycle was entered
  active_queue: string | null     # NEW: e.g., "default", "governance"
  phase_history:                  # NEW: Recent phase transitions (last 5)
    - phase: string
      at: ISO8601
```

### Mechanism Design: Skill Prose Recipe Calls

```
TRIGGER: Skill invocation / phase transition

PATTERN FOR CYCLE SKILLS:

# skill-name/SKILL.md

## Entry (always first)
```bash
just set-cycle {skill-name} {first_phase} {work_id}
just set-queue {queue_name}  # if survey-cycle selected a queue
```

## PHASE_1 Phase
[phase content]

**Exit Gate:** [gate criteria]
```bash
just set-cycle {skill-name} {next_phase} {work_id}
```

## PHASE_N Phase (final)
[phase content]

**On Complete:**
```bash
just clear-cycle
```

OUTCOME:
- session_state.active_cycle = "{skill-name}"
- session_state.current_phase = "{current_phase}"
- session_state.active_queue = "{queue}" (if set)
- UserPromptSubmit displays cycle/phase context
- Observability: agents see "currently in X cycle, Y phase"
```

### Mapping Table: Skill Entry Points Needing Recipe Calls

| Skill | Entry Point | Phase Transitions | Exit Point |
|-------|-------------|-------------------|------------|
| coldstart | N/A (utility) | N/A | N/A |
| survey-cycle | After queue selection | GATHER→SELECT | Before routing-gate |
| routing-gate | N/A (bridge) | N/A | N/A |
| implementation-cycle | On invocation | PLAN→DO→CHECK→DONE | After CHAIN or await |
| investigation-cycle | On invocation | HYPOTHESIZE→EXPLORE→CONCLUDE | After CHAIN or await |
| close-work-cycle | On invocation | VALIDATE→OBSERVE→ARCHIVE | After MEMORY |
| work-creation-cycle | On invocation | VERIFY→POPULATE→READY | After READY |

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Cascade via skill prose | Bash `just set-cycle` calls in markdown | PostToolUse cannot intercept Skill() - only viable mechanism |
| Schema extension | Add active_queue, phase_history | Enables queue context propagation (E2-291 gap) and phase observability |
| Phase markers | Explicit in skill prose | Tool patterns ambiguous - same tools in PLAN/DO/CHECK |
| phase_history limit | Last 5 entries | Prevent unbounded growth; enough for debugging |
| Clear-cycle timing | At skill exit or chain | Prevents state accumulation across context windows |
| Soft enforcement | Warn, don't block | Hard enforcement impossible (Skill unhookable); warnings create affordance |

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Immediate (Can implement now)

- [x] **E2-292: Wire set-cycle Recipe Calls into Cycle Skills**
  - Description: Add `just set-cycle`, `just set-queue`, `just clear-cycle` calls to cycle skill prose at entry, phase transitions, and exit
  - Fixes: session_state dead code, queue context propagation, phase observability
  - Created: `docs/work/active/E2-292/WORK.md`

### Future (Requires more work first)

- N/A - all spawned work is immediately implementable

### Not Spawned Rationale (if no items)

N/A - item spawned above.

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 193 | 2026-01-15 | HYPOTHESIZE | Started | Initial context and hypotheses |
| 194 | 2026-01-16 | EXPLORE→CONCLUDE | Complete | Full investigation completed |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-HN have verdict | [x] | H1 Refuted, H2 Confirmed, H3 Confirmed |
| Evidence has sources | All findings have file:line or concept ID | [x] | All evidence sourced |
| Spawned items created | Items exist in backlog or via /new-* | [x] | E2-292 created |
| Memory stored | ingester_ingest called, memory_refs populated | [x] | 81383, 81386, 81389, 81392 |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | Yes | |
| Are all evidence sources cited with file:line or concept ID? | Yes | |
| Were all hypotheses tested with documented verdicts? | Yes | |
| Are spawned items created (not just listed)? | Yes | E2-292 at docs/work/active/E2-292/WORK.md |
| Is memory_refs populated in frontmatter? | Yes | 81383, 81386, 81389, 81392 |

---

## Closure Checklist

<!-- CONCLUDE PHASE: Complete ALL items before /close -->

### Required (MUST complete)
- [x] **Findings synthesized** - Answer to objective documented in Findings section
- [x] **Evidence sourced** - All findings have file:line or concept ID citations
- [x] **Hypotheses resolved** - All hypotheses have Confirmed/Refuted/Inconclusive verdict
- [x] **Spawned items created** - E2-292 created with `spawned_by: INV-065`
- [x] **Memory stored** - `ingester_ingest` called with findings summary
- [x] **memory_refs populated** - Frontmatter updated with concept IDs (81383, 81386, 81389, 81392)
- [x] **lifecycle_phase updated** - Set to `conclude`
- [x] **Ground Truth Verification complete** - All items checked above

### Optional
- [x] Design outputs documented (schema + mechanism design)
- [x] Session progress updated (S193 HYPOTHESIZE, S194 EXPLORE→CONCLUDE)

---

## References

- Spawned by: E2-291 observation (queue context propagation gap)
- @docs/work/archive/INV-062/investigations/001-session-state-tracking-and-cycle-enforcement-architecture.md
- @docs/work/archive/E2-286/WORK.md (session_state schema)
- @docs/work/archive/E2-287/WORK.md (UserPromptSubmit warning)
- @docs/work/archive/E2-288/WORK.md (set-cycle/clear-cycle recipes)
- @.claude/haios/epochs/E2/EPOCH.md (lines 210-227: Soft Enforcement Strategy)

---
