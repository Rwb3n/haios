---
template: investigation
status: active
date: 2026-01-27
backlog_id: INV-069
title: PostToolUse Timestamp Hook Value Assessment
author: Hephaestus
session: 247
lifecycle_phase: hypothesize
spawned_by: null
related: []
memory_refs: []
version: '2.0'
generated: 2025-12-22
last_updated: '2026-01-27T21:54:36'
---
# Investigation: PostToolUse Timestamp Hook Value Assessment

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

**Trigger:** Session 250 WORK-027 batch edit friction. PostToolUse timestamp hook caused ~30% of edit calls to fail with "file modified since read."

**Problem Statement:** Does the PostToolUse timestamp hook (`last_updated` injection) provide net value, or should it be removed/toggled?

**Prior Observations:**
- obs-250-01: 20 pre-existing test failures (related hook infrastructure)
- obs-250-02: mcp_server import chain broken (hooks import from haios/lib)
- WORK-027 observations: batch edit friction from linter timestamp hook

---

## Prior Work Query

**SKIPPED:** Direct codebase investigation - the hook file itself is the primary source. No prior INV-* documents on this topic.

---

## Objective

Should the `last_updated` timestamp injection in PostToolUse be kept, removed, or made conditional? Answer with evidence of consumers and cost.

---

## Scope

### In Scope
- All 8 behaviors of PostToolUse hook (read from source)
- All consumers of `last_updated` and `generated` fields
- Friction cost during batch operations
- Toggle mechanism feasibility

### Out of Scope
- Rewriting the hook architecture
- Other hooks (PreToolUse, UserPromptSubmit, Stop)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | 1 primary + consumers | post_tool_use.py + grep |
| Hypotheses to test | 3 | Listed below |
| Expected evidence sources | Codebase | Grep for consumers |
| Estimated complexity | Low | Single file analysis |

---

## Hypotheses

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | `last_updated` is not consumed by any runtime logic | High | Grep for `last_updated` usage outside the hook itself | 1st |
| **H2** | The timestamp hook is the primary cause of batch edit friction | High | Analyze hook execution path - does it rewrite the file on every Edit/Write? | 2nd |
| **H3** | Other PostToolUse behaviors (validation, status refresh, cycle logging) provide high value and should be preserved | Med | Review each behavior's consumer and trigger frequency | 3rd |

---

## Exploration Plan

### Phase 1: Evidence Gathering
1. [ ] Catalog all 8 PostToolUse behaviors with their trigger conditions
2. [ ] Grep for `last_updated` consumers (code that reads the field)
3. [ ] Grep for `generated` consumers
4. [ ] Check if any loader, module, or skill reads these timestamp fields

### Phase 2: Hypothesis Testing
5. [ ] H1: Identify runtime consumers of `last_updated` (not just the writer)
6. [ ] H2: Trace the file-rewrite path - confirm the hook writes the file on every Edit/Write
7. [ ] H3: For each non-timestamp behavior, identify its consumer and value

### Phase 3: Synthesis
8. [ ] Build value matrix: behavior × consumer × frequency × value
9. [ ] Recommend: keep / remove / toggle for each behavior
10. [ ] Identify spawned work items

---

## Evidence Collection

### Codebase Evidence

| Finding | Source (file:line) | Supports | Notes |
|---------|-------------------|----------|-------|
| `_add_timestamp` calls `path.write_text()` on every Edit/Write | `post_tool_use.py:246,266,323` | H2 | This is what causes "file modified since read" |
| `get_stale_items()` reads `last_updated` from frontmatter | `status.py:636` | H1 (refutes) | Used in workspace summary |
| `get_stale_items` called by `get_workspace_summary()` and `generate_full_status()` | `status.py:667,854` | H1 | Consumed in status reports |
| `portal_manager.py` writes `last_updated` independently | `portal_manager.py:89,126` | H1 | Not dependent on hook |
| 7 other behaviors in PostToolUse provide real value | `post_tool_use.py:48-110` | H3 | Error capture, auto-link, refresh, etc. |
| Hook triggers on ALL Edit/Write/MultiEdit operations | `post_tool_use.py:61` | H2 | No file-type filtering before timestamp |

### Memory Evidence

**SKIPPED:** No prior memory concepts on this topic.

### External Evidence

**SKIPPED:** Internal codebase investigation only.

---

## Findings

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | **Partially refuted** | `get_stale_items()` reads `last_updated` (status.py:636), but could use git timestamps instead | High |
| H2 | **Confirmed** | `_add_timestamp` calls `path.write_text()` on every Edit/Write, causing file-modified-since-read errors | High |
| H3 | **Confirmed** | Error capture, memory auto-link, discoverable artifact refresh are high-value; timestamp is the only problematic behavior | High |

### Detailed Findings

#### F1: Timestamp injection is the only behavior that rewrites the edited file

**Evidence:** `_add_timestamp` at `post_tool_use.py:170-324` reads the file, modifies it, and writes it back via `path.write_text()`. All other PostToolUse behaviors either write to different files (events.jsonl, haios-status-slim.json) or only return messages. The timestamp is the sole cause of the "file modified since read" race condition.

**Implication:** Disabling ONLY the timestamp injection would eliminate batch edit friction while preserving all other PostToolUse value.

#### F2: `last_updated` has one runtime consumer, but it's substitutable

**Evidence:** `get_stale_items()` at `status.py:620-657` reads `last_updated` to calculate days since last modification. This feeds `get_workspace_summary()` and `generate_full_status()`. However, this function could use `git log --format=%aI -1 <file>` or file system mtime instead. The frontmatter timestamp is not the only source.

**Implication:** Removing `last_updated` injection requires updating `get_stale_items()` to use an alternative timestamp source. This is a small change.

#### F3: The hook already has a toggle pattern in haios.yaml

**Evidence:** `haios.yaml` already has `toggles.block_powershell: true` for PreToolUse. Adding `toggles.inject_timestamps: false` would follow the established pattern. The hook currently has no toggle check - it always runs.

**Implication:** Simplest fix is adding a toggle. Can be done without architectural changes.

---

## Design Outputs

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Disable timestamp injection | Add `toggles.inject_timestamps: false` to haios.yaml | Only PostToolUse behavior that rewrites the edited file. All other behaviors write to separate files. Eliminates batch edit friction. |
| Update get_stale_items | Use git mtime or file system mtime | `last_updated` frontmatter field becomes stale data without hook. git provides accurate timestamps. |
| Keep all other PostToolUse behaviors | No change | Error capture, auto-link, validation, refresh, cycle logging, investigation sync, scaffold-on-entry all provide high value without file-rewrite side effects. |

### Mechanism Design

```
TRIGGER: haios.yaml toggles.inject_timestamps == false

ACTION:
    1. PostToolUse hook checks toggle before calling _add_timestamp
    2. If false, skip timestamp injection entirely
    3. All other behaviors continue unchanged

OUTCOME: Edit/Write operations no longer trigger file rewrites from hook
```

---

## Spawned Work Items

### Immediate (Can implement now)

- [ ] **E2-305: Disable PostToolUse Timestamp Injection**
  - Description: Add `inject_timestamps` toggle to haios.yaml, check in `_add_timestamp`, default to false
  - Fixes: Batch edit friction from file-modified-since-read errors
  - Also: Update `get_stale_items()` to use file system mtime instead of frontmatter `last_updated`

### Future (Requires more work first)

**None.** The toggle is self-contained.

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 247 | 2026-01-27 | HYPOTHESIZE | Started | Initial context and hypotheses |
| - | - | - | - | No additional sessions yet |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-HN have verdict | [ ] | |
| Evidence has sources | All findings have file:line or concept ID | [ ] | |
| Spawned items created | Items exist in backlog or via /new-* | [ ] | |
| Memory stored | ingester_ingest called, memory_refs populated | [ ] | |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | [Yes/No] | |
| Are all evidence sources cited with file:line or concept ID? | [Yes/No] | |
| Were all hypotheses tested with documented verdicts? | [Yes/No] | |
| Are spawned items created (not just listed)? | [Yes/No] | |
| Is memory_refs populated in frontmatter? | [Yes/No] | |

---

## Closure Checklist

<!-- CONCLUDE PHASE: Complete ALL items before /close -->

### Required (MUST complete)
- [ ] **Findings synthesized** - Answer to objective documented in Findings section
- [ ] **Evidence sourced** - All findings have file:line or concept ID citations
- [ ] **Hypotheses resolved** - All hypotheses have Confirmed/Refuted/Inconclusive verdict
- [ ] **Spawned items created** - Via /new-* commands with `spawned_by` field (or rationale if none)
- [ ] **Memory stored** - `ingester_ingest` called with findings summary
- [ ] **memory_refs populated** - Frontmatter updated with concept IDs
- [ ] **lifecycle_phase updated** - Set to `conclude`
- [ ] **Ground Truth Verification complete** - All items checked above

### Optional
- [ ] Design outputs documented (if applicable)
- [ ] Session progress updated (if multi-session)

---

## References

- [Spawned by: Session/Investigation/Work item that triggered this]
- [Related investigation 1]
- [Related ADR or spec]

---
