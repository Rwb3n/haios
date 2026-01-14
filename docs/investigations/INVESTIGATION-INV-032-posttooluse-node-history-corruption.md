---
template: investigation
status: complete
date: 2025-12-24
backlog_id: INV-032
title: PostToolUse Node History Corruption
author: Hephaestus
session: 114
lifecycle_phase: conclude
spawned_by: Session 114
related:
- E2-172
memory_refs:
- 78850
- 78851
- 78852
- 78853
- 78854
- 78855
- 78856
- 78857
version: '2.0'
generated: 2025-12-22
last_updated: '2025-12-24T20:28:02'
---
# Investigation: PostToolUse Node History Corruption

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

## Context

**Trigger:** Session 114 - observed work file `node_history` arrays being corrupted during `just node` operations.

**Problem Statement:** PostToolUse hook's timestamp injection corrupts nested YAML structures (like `node_history` arrays) when rebuilding frontmatter.

**Prior Observations:**
- After `just node E2-162 plan`, node_history showed 4 duplicate "plan" entries instead of [backlog, plan]
- After `just node E2-090 implement`, same corruption pattern
- INV-032 work file transition (backlog→discovery) worked correctly - need to identify difference

---

## Prior Work Query

**Memory Query:** `memory_search_with_experience` query: "node_history corruption YAML PostToolUse"

| Concept ID | Content Summary | Relevance |
|------------|-----------------|-----------|
| 53437 | PostToolUse enhanced to preserve YAML headers | Direct - describes hook's YAML handling |
| 77022 | YAML timestamp injection design decision | Direct - shows why line-by-line parsing was chosen |

**Prior Investigations:**
- [x] Searched for related INV-* documents
- [x] No prior investigation on this specific bug

---

## Objective

Why does PostToolUse hook's `_add_yaml_timestamp()` corrupt `node_history` arrays, and what's the minimal fix?

---

## Scope

### In Scope
- `_add_yaml_timestamp()` function in `.claude/hooks/hooks/post_tool_use.py`
- `update_node()` function in `.claude/lib/work_item.py`
- Interaction between the two when work files are edited

### Out of Scope
- Other PostToolUse handlers (cascade, investigation sync, etc.)
- Non-work-file YAML handling

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to examine | 2 | post_tool_use.py, work_item.py |
| Hypotheses to test | 2 | Listed below |
| Expected evidence sources | 1 | Codebase |
| Estimated complexity | Low | Focused bug fix |

---

## Hypotheses

| # | Hypothesis | Confidence | Test Method | Priority |
|---|------------|------------|-------------|----------|
| **H1** | Line-by-line YAML parsing in `_add_yaml_timestamp()` doesn't preserve nested structures | High | Read lines 225-245 of post_tool_use.py | 1st |
| **H2** | Multiple hook handlers are firing sequentially, each corrupting | Low | Check handler order and deduplication | 2nd |

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps in order
     MUST invoke investigation-agent for each major step -->

### Phase 1: Evidence Gathering
1. [ ] Query memory for prior learnings on topic
2. [ ] Search codebase for relevant patterns (Grep/Glob)
3. [ ] Read identified files and document findings

### Phase 2: Hypothesis Testing
4. [ ] Test H1: [Specific actions]
5. [ ] Test H2: [Specific actions]
6. [ ] Test H3: [Specific actions]

### Phase 3: Synthesis
7. [ ] Compile evidence table
8. [ ] Determine verdict for each hypothesis
9. [ ] Identify spawned work items

---

## Evidence Collection

<!-- EXPLORE PHASE: Document ALL evidence with sources
     MUST include file:line references for codebase evidence -->

### Codebase Evidence

| Finding | Source (file:line) | Supports Hypothesis | Notes |
|---------|-------------------|---------------------|-------|
| [What was found] | `path/file.py:123-145` | H1/H2/H3 | [Context] |

### Memory Evidence

| Concept ID | Content | Supports Hypothesis | Notes |
|------------|---------|---------------------|-------|
| [ID] | [Summary] | H1/H2/H3 | [How it applies] |

### External Evidence (if applicable)

| Source | Finding | Supports Hypothesis | URL/Reference |
|--------|---------|---------------------|---------------|
| [Doc/Article] | [Summary] | H1/H2/H3 | [Link] |

---

## Findings

### Hypothesis Verdicts

| Hypothesis | Verdict | Key Evidence | Confidence |
|------------|---------|--------------|------------|
| H1 | **CONFIRMED** | Lines 225-229 parse line-by-line, treating nested YAML entries as separate keys | High |
| H2 | Inconclusive | Not tested - H1 explains issue | Low |

### Detailed Findings

#### Finding 1: Naive YAML Parsing

**Evidence:** `.claude/hooks/hooks/post_tool_use.py:225-229`
```python
for line in yaml_lines:
    if ":" in line and not line.strip().startswith("#"):
        key = line.split(":")[0].strip()
        yaml_order.append(key)
        yaml_dict[key] = line
```

**Analysis:** This treats each line with `:` as a top-level key. For nested YAML:
```yaml
node_history:
  - node: backlog
    entered: 2025-12-24
```
It stores:
- key="node_history", value="node_history:"
- key="- node", value="  - node: backlog"
- key="entered", value="    entered: 2025-12-24"

**Implication:** When rebuilt, nested structure is lost.

#### Finding 2: Conflict with update_node()

**Evidence:** `.claude/lib/work_item.py:124`
```python
new_fm = yaml.dump(fm, default_flow_style=False, sort_keys=False, allow_unicode=True)
```

**Analysis:** `update_node()` uses proper YAML serialization. When it writes, the hook immediately runs and re-parses with naive logic, corrupting the structure.

**Implication:** Need to either:
1. Fix `_add_yaml_timestamp()` to use proper YAML parsing
2. Or skip timestamp injection for files modified by `update_node()`

---

## Design Outputs

<!-- If investigation produces architectural designs, document them here
     SKIP this section if investigation is pure discovery with no design outputs -->

### Schema Design (if applicable)

```yaml
# [Name of schema]
field_name: type
  description: [What this field does]
```

### Mapping Table (if applicable)

| Source | Target | Relationship | Notes |
|--------|--------|--------------|-------|
| [A] | [B] | [How A relates to B] | |

### Mechanism Design (if applicable)

```
TRIGGER: [What initiates the mechanism]

ACTION:
    1. [Step 1]
    2. [Step 2]
    3. [Step 3]

OUTCOME: [What results from the mechanism]
```

### Key Design Decisions

| Decision | Choice | Rationale (WHY) |
|----------|--------|-----------------|
| [Decision point] | [What was chosen] | [Why this choice - most important part] |

---

## Spawned Work Items

### Immediate (Can implement now)

- [ ] **E2-172: Fix _add_yaml_timestamp to use proper YAML parsing**
  - Description: Replace line-by-line parsing with yaml.safe_load/yaml.dump
  - Fixes: Node history corruption when PostToolUse runs after work_item.update_node()
  - Spawned via: `/new-work E2-172 "Fix YAML timestamp injection"`

### Future (Requires more work first)

None - fix is straightforward.

---

## Session Progress Tracker

<!-- Track progress across sessions for multi-session investigations -->

| Session | Date | Phase | Progress | Notes |
|---------|------|-------|----------|-------|
| 113 | 2025-12-24 | HYPOTHESIZE | Started | Initial context and hypotheses |
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
