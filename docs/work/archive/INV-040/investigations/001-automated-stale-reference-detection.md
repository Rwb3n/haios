---
template: investigation
status: active
date: 2025-12-29
backlog_id: INV-040
title: Automated Stale Reference Detection
author: Hephaestus
session: 143
lifecycle_phase: conclude
spawned_by: E2-212
related:
- E2-228
- E2-212
memory_refs:
- 80230
- 80231
- 80232
- 80233
- 80234
- 80235
- 80236
- 80237
- 80238
version: '2.0'
generated: 2025-12-22
last_updated: '2025-12-29T10:57:09'
---
# Investigation: Automated Stale Reference Detection

@docs/README.md
@docs/epistemic_state.md

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

**Trigger:** E2-212 (Work Directory Structure Migration) was closed with Phase 4.3 (Consumer Verification) incomplete. Session 132 discovered 10+ files with stale `docs/plans/PLAN-{id}-*.md` path references after closure.

**Problem Statement:** The close workflow has no automated gate to verify zero stale references before allowing closure - consumer verification is manual and easily skipped.

**Prior Observations:**
- E2-212 plan had MUST requirement "Verify zero stale references" that wasn't enforced
- Pattern: migrations change path patterns but consumer files (skills, agents, commands) lag behind
- "Ceremonial Completion" anti-pattern - code migrated but consumers not updated (Memory 77088)

---

## Prior Work Query

<!-- MUST query memory before starting investigation -->

**Memory Query:** `memory_search_with_experience` with query: "stale reference detection consumer verification path migration"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 77093 | "Future migrations MUST grep for old paths/names and update all consumers before closure" | Direct guidance - establishes pattern |
| 77088 | "Ceremonial Completion anti-pattern - code was migrated but consumers weren't updated" | Root cause pattern |
| 77164 | "Consumer Verification Gap Pattern" | Named pattern to address |
| 79855 | "Without consumer verification, cycles and agents would point to non-existent paths" | Impact statement |
| 80035 | "Can proactively validate references. Foundation for /status integration" | Prior solution direction |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] No direct prior investigation found, but related learnings from E2-120 (PowerShell migration) and E2-212 (work directory migration)

---

## Objective

<!-- One clear question this investigation will answer -->

What is the best integration point and mechanism for automated stale reference detection to prevent "Ceremonial Completion" gaps?

---

## Scope

### In Scope
- Current stale reference patterns in HAIOS codebase
- Existing detection mechanisms (test_dependencies.py, grep patterns)
- Integration points: close-work-cycle, commit-close, PreToolUse hook, just audit
- Blocking vs warning behavior design

### Out of Scope
- CI/CD integration (no CI currently)
- Pre-commit hook (not using git hooks currently)
- Reference tracking in memory system (separate concern)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | 5-8 | close-work-cycle, test_dependencies.py, commit-close recipe |
| Hypotheses to test | 3 | Listed below |
| Expected evidence sources | 2 | Codebase + Memory |
| Estimated complexity | Low | Pattern is known, just need integration point |

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define BEFORE exploring
     Each hypothesis MUST have confidence and test method -->

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | test_dependencies.py already provides stale reference detection that can be integrated into close workflow | High | Read test_dependencies.py, check what patterns it detects | 1st |
| **H2** | close-work-cycle VALIDATE phase is the right integration point (runs before archival) | Med | Read close-work-cycle, check if VALIDATE phase exists and has validation pattern | 2nd |
| **H3** | A separate `just validate-refs` recipe is better than embedding in close (flexibility) | Low | Compare close integration vs standalone recipe pros/cons | 3rd |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [x] Read test_dependencies.py to understand current detection patterns
2. [x] Read close-work-cycle SKILL.md to understand current validation flow
3. [x] Check justfile for existing validation recipes

### Phase 2: Hypothesis Testing
4. [x] Test H1: Run test_dependencies.py and examine output format
5. [x] Test H2: Identify where in close-work-cycle validation could be inserted
6. [x] Test H3: Evaluate pros/cons of standalone recipe vs embedded

### Phase 3: Synthesis
7. [x] Compile evidence table with file:line references
8. [x] Determine verdict for each hypothesis
9. [x] Design recommended integration approach
10. [x] Identify spawned implementation item

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| `validate_dependencies()` returns structured result with broken_refs | `.claude/lib/dependencies.py:116-180` | H1 partial | Infrastructure exists |
| Only scans `.claude/skills/*/SKILL.md` - NOT plans, commands, agents | `.claude/lib/dependencies.py:147-148` | H1 partial | Pattern set differs |
| Detects `Skill(skill="...")` and `Task(subagent_type='...')` patterns | `.claude/lib/dependencies.py:26-44, 47-65` | H1 partial | Different from path patterns |
| close-work-cycle has VALIDATE phase with clear structure | `.claude/skills/close-work-cycle/SKILL.md:42-65` | H2 | Right integration point |
| dod-validation-cycle invoked as entry gate before VALIDATE | `.claude/skills/close-work-cycle/SKILL.md:34-38` | H2 | Cascades correctly |
| Ground Truth Verification supports `grep-check` type | `.claude/skills/dod-validation-cycle/SKILL.md:81-85` | H2 | Mechanism exists |
| `just validate` and `just validate-observations` patterns exist | `justfile:16-17, 58-59` | H3 | Consistent pattern |
| No `just validate-refs` currently exists | `justfile` (full search) | H3 | Gap to fill |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| 77093 | "Future migrations MUST grep for old paths" | All | Establishes pattern |
| 77088 | "Ceremonial Completion anti-pattern" | All | Root cause we're addressing |
| 77164 | "Consumer Verification Gap Pattern" | All | Named pattern |

### External Evidence (if applicable)

**SKIPPED:** Pure codebase investigation, no external sources needed

---

## Findings

<!-- EXPLORE PHASE: Document findings as discovered
     CONCLUDE PHASE: Synthesize into coherent narrative

     DoD: This section MUST have actual content, not placeholder text -->

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | **Partial** | dependencies.py validates skill/agent refs, not path patterns. Infrastructure (regex, validation loop) exists but pattern set differs. | High |
| H2 | **Confirmed** | dod-validation-cycle has grep-check mechanism that can validate stale paths. Already invoked by close-work-cycle. | High |
| H3 | **Confirmed** | Justfile has `just validate-*` pattern. Standalone + integration can coexist. | High |

### Detailed Findings

#### Finding 1: test_dependencies.py Only Validates Skill/Agent Cross-References

**Evidence:**
```python
# .claude/lib/dependencies.py:147-148
if skills_dir.exists():
    for skill_file in skills_dir.glob("*/SKILL.md"):
        # Only checks references WITHIN skill files
```

**Analysis:** The dependency validator validates that skills and agents reference other existing skills/agents. It does NOT detect stale file path patterns like `docs/plans/PLAN-{id}-*.md` in arbitrary files.

**Implication:** H1 partial - infrastructure exists (regex extraction, validation loop) but pattern set is different. A new function like `validate_stale_paths()` would need to be added.

#### Finding 2: dod-validation-cycle Has grep-check Support

**Evidence:**
```markdown
# .claude/skills/dod-validation-cycle/SKILL.md:81-85
| Type | Tool | Success Criteria |
|------|------|------------------|
| grep-check | Grep(pattern) | Match count matches expectation (0 or >0) |
```

**Analysis:** The Ground Truth Verification mechanism already supports `grep-check` which can detect patterns. Plans can define stale reference patterns to check.

**Implication:** H2 confirmed - integration point exists at dod-validation-cycle (invoked by close-work-cycle). The grep-check mechanism is the right tool.

#### Finding 3: Standalone Recipe Provides Flexibility

**Evidence:**
```bash
# justfile:16-17 - template validation pattern
validate file:
    python -c "... from validate import validate_template ..."

# justfile:58-59 - observation validation pattern
validate-observations id:
    python -c "... from observations import validate_observations ..."
```

**Analysis:** The justfile follows consistent pattern: `just validate-*` recipes for different validation types. A `just validate-refs` recipe would follow this pattern.

**Implication:** H3 confirmed - standalone recipe provides flexibility while dod-validation-cycle provides enforcement. Both can coexist.

---

## Design Outputs

### Recommended Integration: Layered Approach

```
LAYER 1: just validate-refs (standalone)
    - Add validate_stale_refs() to .claude/lib/dependencies.py
    - Define common stale patterns (legacy paths)
    - Expose via just validate-refs for ad-hoc use

LAYER 2: Plan-specific grep-check (already exists)
    - Plans with migrations define Ground Truth Verification entries
    - dod-validation-cycle VALIDATE phase executes grep-check items
    - No changes needed - just ensure migration plans include patterns

LAYER 3: Automated enforcement (future, optional)
    - Could add validate_stale_refs() to dod-validation-cycle as universal check
    - Would catch patterns even when plan doesn't explicitly list them
```

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| Layered vs single integration | Layered | Standalone for flexibility, dod for enforcement - covers all use cases |
| Blocking vs warning | Warning first | Avoid false positives; can escalate to blocking after confidence builds |
| Extend dependencies.py vs new module | Extend | Infrastructure (regex, validation loop) already exists |
| Pattern storage | Hardcoded list initially | Known patterns are few; config file is overengineering for now |

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create items via /new-* commands
     Each item MUST have spawned_by: {this_investigation_id}

     DoD: This section MUST have entries, not "None yet"
     If truly no spawns, explain why in rationale -->

### Immediate (Can implement now)

- [x] **E2-231: Add just validate-refs Recipe**
  - Description: Add `validate_stale_refs()` to dependencies.py, expose via `just validate-refs`
  - Fixes: Consumer Verification Gap Pattern - prevents Ceremonial Completion
  - Spawned via: `/new-work E2-231 "Add just validate-refs Recipe"`

### Future (Requires more work first)

None - implementation path is clear.

### Related Existing Work

- **E2-228: Add just validate-deps Recipe** - Different scope (skill/agent refs, not path patterns)

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 143 | 2025-12-29 | HYPOTHESIZE | Complete | Context, hypotheses, scope defined |
| 143 | 2025-12-29 | EXPLORE | Complete | Evidence gathered via investigation-agent |
| 143 | 2025-12-29 | CONCLUDE | Complete | Findings synthesized, E2-231 spawned |

---

## Ground Truth Verification

<!-- CONCLUDE PHASE: Verify findings before closing
     MUST read/check each item, not just claim -->

| Item to Verify | Expected State | Verified | Notes |
|----------------|---------------|----------|-------|
| Hypothesis verdicts documented | All H1-HN have verdict | [x] | H1 partial, H2/H3 confirmed |
| Evidence has sources | All findings have file:line or concept ID | [x] | See Evidence Collection table |
| Spawned items created | Items exist in backlog or via /new-* | [x] | E2-231 created |
| Memory stored | ingester_ingest called, memory_refs populated | [x] | See below |

**Binary Verification (Yes/No):**

| Question | Answer | If NO, explain |
|----------|--------|----------------|
| Did you invoke investigation-agent for EXPLORE phase? | Yes | Subagent gathered all evidence |
| Are all evidence sources cited with file:line or concept ID? | Yes | 8 codebase refs, 3 memory refs |
| Were all hypotheses tested with documented verdicts? | Yes | H1 partial, H2/H3 confirmed |
| Are spawned items created (not just listed)? | Yes | E2-231 in docs/work/active/ |
| Is memory_refs populated in frontmatter? | Yes | After ingestion below |

---

## Closure Checklist

<!-- CONCLUDE PHASE: Complete ALL items before /close -->

### Required (MUST complete)
- [x] **Findings synthesized** - Answer to objective documented in Findings section
- [x] **Evidence sourced** - All findings have file:line or concept ID citations
- [x] **Hypotheses resolved** - All hypotheses have Confirmed/Refuted/Inconclusive verdict
- [x] **Spawned items created** - Via /new-* commands with `spawned_by` field (or rationale if none)
- [x] **Memory stored** - `ingester_ingest` called with findings summary
- [x] **memory_refs populated** - Frontmatter updated with concept IDs
- [x] **lifecycle_phase updated** - Set to `conclude`
- [x] **Ground Truth Verification complete** - All items checked above

### Optional
- [x] Design outputs documented (if applicable)
- [x] Session progress updated (if multi-session)

---

## References

- [Spawned by: Session/Investigation/Work item that triggered this]
- [Related investigation 1]
- [Related ADR or spec]

---
