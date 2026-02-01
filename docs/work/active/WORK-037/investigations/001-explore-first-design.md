---
template: investigation
status: active
date: 2026-02-01
backlog_id: WORK-037
title: EXPLORE-FIRST Investigation Cycle Design
author: Hephaestus
session: 271
lifecycle_phase: conclude
spawned_by: WORK-036
related:
- WORK-036
memory_refs:
- 82646
- 82647
- 82648
- 82649
- 82650
- 82651
- 82652
- 82653
- 82654
- 82655
- 82656
- 82721
- 82722
- 82723
- 82829
- 82830
- 82831
- 82832
- 82833
- 82834
- 82835
- 82836
- 82837
version: '2.0'
generated: 2026-02-01
last_updated: '2026-02-01T15:20:05'
---
# Investigation: EXPLORE-FIRST Investigation Cycle Design

@docs/work/active/WORK-036/investigations/001-investigation-template-vs-explore-agent-effectiveness.md
@.claude/skills/investigation-cycle/SKILL.md
@.claude/haios/epochs/E2_4/EPOCH.md
@.claude/haios/epochs/E2_4/arcs/templates/ARC.md

---

## Context

**L4 Decision (Session 265):** Investigation cycle should invert from `HYPOTHESIZE → EXPLORE → CONCLUDE` to `EXPLORE → HYPOTHESIZE → VALIDATE → CONCLUDE`. This is a done decision, not under evaluation.

**Design Mandate:**
1. Design the four-phase structure and contracts
2. Integrate with E2.4 fractured templates paradigm
3. Define governed activities per phase
4. Create migration path for existing patterns

**Prior Work:**
- WORK-036 established the Template Tax problem (25 MUST + 27 checkboxes)
- Memory concepts 82721-82723 capture the L4 decision
- Templates arc (E2.4) defines phase template contracts

---

## Prior Work Query

**Memory Query:** Session 265 L4 decisions already loaded during HYPOTHESIZE phase.

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 82721 | L4 Decision: Investigation Flow (EXPLORE-FIRST) | Core decision |
| 82722 | Inverts HYPOTHESIZE → EXPLORE → CONCLUDE | Cycle structure |
| 82723 | Rationale: Open exploration produces depth | Why |
| 82724-82728 | Fractured templates with contracts | How templates integrate |
| 82646-82656 | WORK-036 Template Tax findings | Problem evidence |

---

## Objective

**Primary Question:** What is the design specification for the EXPLORE-FIRST investigation cycle?

**Deliverables:**
1. Phase definitions (input/output contracts for each phase)
2. Governed activities matrix (which primitives allowed per phase)
3. Skill update specification (changes to investigation-cycle/SKILL.md)
4. Migration path for existing investigations

---

## Scope

### In Scope
- Four-phase flow: EXPLORE → HYPOTHESIZE → VALIDATE → CONCLUDE
- Phase contracts (input/output per phase)
- Governed activities per phase (integration with Activities arc)
- Changes to investigation-cycle skill
- Fractured template integration (one template per phase)

### Out of Scope
- Implementation code (this produces design, not implementation)
- Changes to investigation-agent (separate work item)
- Existing investigation migrations (document path, don't execute)

---

## Hypotheses

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | **EXPLORE phase = unrestricted gathering** - EXPLORE should have minimal constraints: read anything, query memory, no output format. Similar to built-in Explore agent. | High | Analyze what made Session 262 Explore effective. Map to governed activities. | 1st |
| **H2** | **HYPOTHESIZE phase = synthesis from evidence** - After EXPLORE, agent should form hypotheses FROM gathered evidence, not before. This is the inversion. | High | Design phase contract. Input = EXPLORE output. Output = structured hypotheses. | 2nd |
| **H3** | **VALIDATE phase = focused testing** - Each hypothesis gets tested against evidence. This replaces old "test hypothesis" approach but with evidence already gathered. | Medium | Design validation approach. Determine if subagent or main agent. | 3rd |
| **H4** | **CONCLUDE phase = synthesize + spawn** - Combine findings, store to memory, spawn next work. Similar to current CONCLUDE but with richer input. | High | Map to existing CONCLUDE. Identify deltas. | 4th |

---

## Exploration Plan

### Phase 1: Current State Analysis
1. [x] Analyze current investigation-cycle skill structure (lines, MUST gates, phases)
2. [x] Analyze current investigation template structure (overhead documented in WORK-036)
3. [x] Map Session 262 Explore agent behavior to governed activities

### Phase 2: New Phase Design
4. [x] Design EXPLORE phase contract (input/output/activities)
5. [x] Design HYPOTHESIZE phase contract (input/output/activities)
6. [x] Design VALIDATE phase contract (input/output/activities)
7. [x] Design CONCLUDE phase contract (input/output/activities)

### Phase 3: Integration
8. [x] Map phases to governed activities (from Activities arc)
9. [x] Design fractured template structure (one per phase)
10. [x] Draft investigation-cycle skill changes

### Phase 4: Migration
11. [x] Document migration path for existing skill
12. [x] Identify spawned implementation work items

---

## Evidence Collection

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| Current investigation-cycle: 227 lines, 7 MUST requirements | `.claude/skills/investigation-cycle/SKILL.md` | H1 | Moderate overhead |
| Current investigation template: 368 lines, 18 MUST, 27 checkboxes | `.claude/templates/investigation.md` | H1 | High overhead (Template Tax) |
| activity_matrix.yaml has EXPLORE state = minimal restrictions | `.claude/haios/config/activity_matrix.yaml:74-87` | H1 | web-fetch, web-search, memory-search all allowed |
| EXPLORE state blocks only file-write (warn), memory-store (warn) | `.claude/haios/config/activity_matrix.yaml:20-28,121` | H1 | Read-heavy, write-light |
| investigation-agent output format is rigid 4-column table | `.claude/agents/investigation-agent.md:55-65` | H2 | Limits expression |
| Phase-to-state mapping exists for cycles | `.claude/haios/config/activity_matrix.yaml:179-241` | H3, H4 | Can add new phases |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 82721 | L4 Decision: Investigation Flow (EXPLORE-FIRST) | All | Core decision |
| 82722 | Inverts HYPOTHESIZE → EXPLORE → CONCLUDE | All | Structure change |
| 82723 | Rationale: Open exploration produces depth | H1 | Why EXPLORE first |
| 82724-82728 | Fractured templates with contracts | H2-H4 | Template structure |
| 82646 | Template Tax - 25 MUST + 27 checkboxes | H1 | Problem evidence |

---

## Findings

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | **Confirmed** | EXPLORE state in activity_matrix allows web-fetch, web-search, memory-search; only warns on writes. Session 262 Explore agent success. | High |
| H2 | **Confirmed** | Inverting sequence means hypotheses form FROM evidence. investigation-agent table format should be relaxed for synthesis. | High |
| H3 | **Confirmed** | VALIDATE maps to CHECK state. Evidence already gathered, so validation is structured review vs new exploration. | Medium |
| H4 | **Confirmed** | CONCLUDE maps to DONE state. Existing CONCLUDE pattern largely reusable with richer input from 3 prior phases. | High |

### Detailed Findings

#### Finding 1: EXPLORE Phase Design

**Evidence:** The EXPLORE state in activity_matrix.yaml (lines 74-87) already permits the activities needed for open exploration:
- `web-fetch`: allow
- `web-search`: allow
- `memory-search`: allow
- `file-read`: allow (via `_all_states`)
- `content-search`: allow
- `file-write`: warn ("prefer notes over artifacts")

**Conclusion:** The governed activities infrastructure supports unrestricted EXPLORE. The Template Tax came from the template's 27 checkboxes and investigation-agent's rigid output format, not from activity restrictions.

**Design Implication:** EXPLORE phase should:
1. Not require investigation-agent (main agent explores freely)
2. Have minimal template structure (~30 lines max)
3. Output format = free-form notes (no table requirement)

#### Finding 2: HYPOTHESIZE Phase Inversion

**Evidence:** Currently, investigation-agent.md (lines 22-27) describes HYPOTHESIZE as the first phase where agent "proposes 2-4 testable hypotheses" BEFORE exploring. This is backwards for discovery work.

**Conclusion:** In EXPLORE-FIRST, HYPOTHESIZE becomes a synthesis phase:
- Input: Evidence gathered during EXPLORE
- Output: Structured hypotheses with supporting evidence citations
- Activity: DESIGN state (allows writes, synthesis work)

**Design Implication:** HYPOTHESIZE phase should:
1. Run AFTER EXPLORE completes
2. Input = EXPLORE notes
3. Output = hypothesis table with evidence citations (the structure comes after exploration, not before)

#### Finding 3: VALIDATE Phase as Focused Review

**Evidence:** The old EXPLORE phase combined exploration AND hypothesis testing. With EXPLORE-FIRST, exploration is complete before hypotheses form. VALIDATE becomes a focused review:
- Already have evidence (from EXPLORE)
- Already have hypotheses (from HYPOTHESIZE)
- VALIDATE = systematically check each hypothesis against evidence

**Conclusion:** VALIDATE phase should:
1. Map to CHECK state (read-heavy, write-warn)
2. Not gather new evidence (that's EXPLORE's job)
3. Output = verdict per hypothesis (Confirmed/Refuted/Inconclusive)

#### Finding 4: CONCLUDE Phase Largely Unchanged

**Evidence:** Current CONCLUDE (investigation-cycle/SKILL.md lines 114-134) already handles:
- Synthesize findings
- Create spawned work items
- Store to memory
- Mark complete

**Conclusion:** CONCLUDE phase needs minimal changes:
1. Richer input (evidence + hypotheses + verdicts)
2. Same outputs (synthesis + spawns + memory)
3. Maps to DONE state (as currently)

---

## Design Outputs

### Phase Contracts

#### 1. EXPLORE Phase

```yaml
phase: EXPLORE
state: EXPLORE
input:
  - work_item: WORK.md with context section filled
  - memory_refs: Prior related concepts (if any)
output:
  - notes: Free-form exploration notes
  - evidence_log: Optional list of sources examined
activities:
  allowed: [file-read, content-search, file-search, memory-search, web-fetch, web-search, task-spawn]
  warned: [file-write, memory-store]
  blocked: [shell-background, notebook-edit]
template_lines: ~30
must_gates: 2
  - Must query memory for prior work
  - Must document sources examined
```

#### 2. HYPOTHESIZE Phase

```yaml
phase: HYPOTHESIZE
state: DESIGN
input:
  - explore_notes: Output from EXPLORE phase
  - evidence_log: Sources from EXPLORE
output:
  - hypotheses: 2-4 structured hypotheses with evidence citations
  - test_approach: How each hypothesis will be validated
activities:
  allowed: [file-read, file-write, content-search, memory-search]
  blocked: [web-fetch, web-search]  # No new research - use EXPLORE evidence
template_lines: ~30
must_gates: 2
  - Must cite evidence for each hypothesis
  - Must define validation approach
```

#### 3. VALIDATE Phase

```yaml
phase: VALIDATE
state: CHECK
input:
  - hypotheses: From HYPOTHESIZE
  - explore_notes: Evidence from EXPLORE
output:
  - verdicts: Confirmed/Refuted/Inconclusive per hypothesis
  - confidence: High/Medium/Low per verdict
activities:
  allowed: [file-read, content-search, memory-search]
  warned: [file-write, file-edit]
  blocked: [web-fetch, web-search]  # No new research
template_lines: ~30
must_gates: 2
  - Must render verdict for each hypothesis
  - Must cite supporting/refuting evidence
```

#### 4. CONCLUDE Phase

```yaml
phase: CONCLUDE
state: DONE
input:
  - hypotheses: With verdicts
  - explore_notes: Original evidence
output:
  - findings: Synthesized answer to objective
  - spawned_items: Work items created
  - memory_refs: Concepts stored
activities:
  allowed: [file-read, file-write, memory-store, skill-invoke]
template_lines: ~30
must_gates: 3
  - Must synthesize findings
  - Must spawn or justify no spawns
  - Must store to memory
```

### Governed Activities Matrix

| Phase | State | Read | Write | Search | Memory | Web | Execute |
|-------|-------|------|-------|--------|--------|-----|---------|
| EXPLORE | EXPLORE | allow | warn | allow | search: allow, store: warn | allow | warn |
| HYPOTHESIZE | DESIGN | allow | allow | allow | search: allow, store: warn | block | warn |
| VALIDATE | CHECK | allow | warn | allow | search: allow | block | allow |
| CONCLUDE | DONE | allow | allow | allow | allow | allow | warn |

### Phase-to-State Mapping Update

```yaml
# activity_matrix.yaml addition
investigation-cycle/EXPLORE: EXPLORE
investigation-cycle/HYPOTHESIZE: DESIGN
investigation-cycle/VALIDATE: CHECK
investigation-cycle/CONCLUDE: DONE
```

### Skill Update Specification

**File:** `.claude/skills/investigation-cycle/SKILL.md`

**Changes:**
1. Rename phases: HYPOTHESIZE→EXPLORE→CONCLUDE becomes EXPLORE→HYPOTHESIZE→VALIDATE→CONCLUDE
2. Reorder sections to reflect new flow
3. Update phase entry commands (`just set-cycle`)
4. Remove investigation-agent MUST requirement for EXPLORE (now main agent does open exploration)
5. Add VALIDATE phase section (new)
6. Update diagrams and composition map

**Estimated changes:** ~60-80 lines modified, ~20 lines added (VALIDATE section)

### Fractured Template Structure

**Proposed directory:**
```
.claude/templates/investigation/
├── README.md          (~20 lines - explains flow)
├── EXPLORE.md         (~30 lines)
├── HYPOTHESIZE.md     (~30 lines)
├── VALIDATE.md        (~30 lines)
└── CONCLUDE.md        (~30 lines)
```

**Total:** ~140 lines vs current 368 lines (62% reduction)

**MUST gates reduced:** 18 → 9 (50% reduction)

**Checkboxes reduced:** 27 → ~12 (56% reduction)

### Migration Path

1. **Update activity_matrix.yaml** - Add new phase mappings (already prepared above)
2. **Create fractured templates** - New directory with 4 phase templates
3. **Update investigation-cycle skill** - Rename phases, add VALIDATE, update flow
4. **Update investigation-agent** - Relax output format (separate work item)
5. **Deprecate monolithic template** - Add deprecation notice to investigation.md
6. **In-flight investigations** - Complete using old flow (grandfather clause)

---

## Spawned Work Items

### Implementation Work (to spawn)

1. **Update activity_matrix.yaml phase mappings**
   - Add investigation-cycle/EXPLORE, HYPOTHESIZE, VALIDATE, CONCLUDE mappings
   - Effort: Small
   - Arc: flow (E2.4)

2. **Create fractured investigation templates**
   - New directory: `.claude/templates/investigation/`
   - 4 phase templates + README
   - Effort: Medium
   - Arc: templates (E2.4)

3. **Update investigation-cycle skill**
   - Rename/reorder phases
   - Add VALIDATE section
   - Update diagrams
   - Effort: Medium
   - Arc: flow (E2.4)

4. **Update investigation-agent (separate work)**
   - Relax output format
   - Phase-aware behavior for new flow
   - Effort: Medium
   - Arc: templates (E2.4)

**Recommendation:** Spawn a single implementation work item that covers #1-3 (skill + templates + activity matrix update). Item #4 (investigation-agent) can be separate.

### Spawned

- [x] **WORK-061: EXPLORE-FIRST Investigation Cycle Implementation** - Covers activity_matrix.yaml update, fractured templates, and investigation-cycle skill update. Spawned Session 271.

---

## Closure Checklist

### Required (MUST complete)
- [x] **Findings synthesized** - Design spec documented in Design Outputs section
- [x] **Evidence sourced** - All findings have file:line or concept ID citations
- [x] **Hypotheses resolved** - All hypotheses have verdict (H1-H4 Confirmed)
- [x] **Spawned items created** - WORK-061 spawned
- [x] **Memory stored** - `ingester_ingest` called, concepts 82829-82837
- [x] **memory_refs populated** - Frontmatter updated with all concept IDs
- [x] **lifecycle_phase updated** - Set to `conclude`

---

## References

- @docs/work/active/WORK-036/investigations/001-investigation-template-vs-explore-agent-effectiveness.md
- @.claude/skills/investigation-cycle/SKILL.md
- @.claude/haios/epochs/E2_4/EPOCH.md
- @.claude/haios/epochs/E2_4/arcs/templates/ARC.md
- @.claude/haios/epochs/E2_4/arcs/activities/ARC.md
- Memory concepts 82646-82656, 82721-82723
