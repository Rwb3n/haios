---
template: implementation_plan
status: complete
date: 2025-12-22
backlog_id: E2-112
title: "Investigation Agent"
author: Hephaestus
lifecycle_phase: done
session: 99
spawned_by: INV-017
memory_refs: [77152, 77153, 77154, 77155, 77156, 77157, 77158, 77159, 77160, 77161, 77162, 77163]
version: "1.5"
generated: 2025-12-21
last_updated: 2025-12-22T19:54:01
---
# Implementation Plan: Investigation Agent

@docs/README.md
@docs/epistemic_state.md
@docs/investigations/INVESTIGATION-INV-022-work-cycle-dag-unified-architecture.md

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: New feature, no existing code to show current state"
     - "SKIPPED: Pure documentation task, no code changes"
     - "SKIPPED: Trivial fix, single line change doesn't warrant detailed design"

     This prevents silent section deletion and ensures conscious decisions.
-->

---

## Goal

A phase-aware subagent that operates within the investigation-cycle, understanding its current phase (HYPOTHESIZE/EXPLORE/CONCLUDE) and producing structured outputs appropriate for each phase.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/settings.local.json` (agent registration) |
| Lines of code affected | ~10 | Agent definition in settings |
| New files to create | 1 | `.claude/agents/investigation-agent.md` |
| Tests to write | 0 | Agent definitions are declarative, not code |
| Dependencies | 1 | investigation-cycle skill references this agent |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | Skill + settings + system prompt |
| Risk of regression | Low | New agent, doesn't modify existing |
| External dependencies | Low | Just Claude Code Task tool |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Agent definition | 20 min | High |
| Skill integration | 10 min | High |
| Testing/verification | 15 min | Medium |
| **Total** | 45 min | High |

---

## Current State vs Desired State

### Current State

**No investigation-specific agent exists.** Research tasks use:
- `Explore` agent (codebase-focused, no memory integration)
- Manual queries (memory_search, web search)
- No phase awareness

Existing agents in `.claude/agents/`:
- preflight-checker (plan validation)
- schema-verifier (database schema)
- test-runner (pytest execution)
- why-capturer (learning extraction)

### Desired State

New agent at `.claude/agents/investigation-agent.md`:

```yaml
---
name: investigation-agent
description: Phase-aware research agent for HAIOS investigations. Use during investigation-cycle to conduct hypothesis testing, evidence gathering, and synthesis. Queries memory first, understands current phase (HYPOTHESIZE/EXPLORE/CONCLUDE).
tools: Read, Grep, Glob, WebSearch, WebFetch, mcp__haios-memory__memory_search_with_experience
---
```

**Behavior:** Conducts research within investigation-cycle context, producing phase-appropriate outputs.

**Result:** Structured findings that integrate into investigation documents.

---

## Tests First (TDD)

**SKIPPED:** Agent definitions are declarative markdown, not code. Verification is manual invocation testing.

### Verification Tests (Manual)

1. **Agent Discovery Test**
   - After creating file, run `just update-status-slim`
   - Check that `investigation-agent` appears in agents list

2. **HYPOTHESIZE Phase Test**
   ```
   Task(prompt='HYPOTHESIZE phase for INV-023: What do we know about ReasoningBank feedback loops?',
        subagent_type='investigation-agent')
   ```
   - Expected: Returns memory search results + hypothesis list

3. **EXPLORE Phase Test**
   ```
   Task(prompt='EXPLORE: Test hypothesis that retrieval results are too generic',
        subagent_type='investigation-agent')
   ```
   - Expected: Returns evidence from codebase + web research

4. **CONCLUDE Phase Test**
   ```
   Task(prompt='CONCLUDE: Synthesize findings and suggest spawned work items',
        subagent_type='investigation-agent')
   ```
   - Expected: Returns structured summary + spawn recommendations

---

## Detailed Design

### Agent File: `.claude/agents/investigation-agent.md`

```markdown
---
name: investigation-agent
description: Phase-aware research agent for HAIOS investigations. Use during investigation-cycle to conduct hypothesis testing, evidence gathering, and synthesis. Queries memory first, understands current phase (HYPOTHESIZE/EXPLORE/CONCLUDE).
tools: Read, Grep, Glob, WebSearch, WebFetch, mcp__haios-memory__memory_search_with_experience
---
# Investigation Agent

Phase-aware research agent for HAIOS investigations (INV-* documents).

## Architecture Context (INV-022)

This agent operates **within** the investigation-cycle container. Work files traverse nodes, nodes contain cycles, and this agent assists at each phase.

## Requirement Level

**OPTIONAL** but **RECOMMENDED** for complex investigations. The investigation-cycle skill may invoke this agent.

## Phase-Aware Behavior

### HYPOTHESIZE Phase
When prompt contains "HYPOTHESIZE":
1. **Memory First**: Query `memory_search_with_experience` for related investigations, learnings
2. **Form Hypotheses**: Based on memory and context, propose 2-4 testable hypotheses
3. **Output**: Structured list with confidence levels

### EXPLORE Phase
When prompt contains "EXPLORE":
1. **Test Hypotheses**: Use codebase search (Grep, Glob, Read) for evidence
2. **External Research**: Use WebSearch/WebFetch if needed
3. **Output**: Evidence table with sources and relevance

### CONCLUDE Phase
When prompt contains "CONCLUDE":
1. **Synthesize**: Combine findings into coherent narrative
2. **Identify Gaps**: What remains unknown?
3. **Propose Spawns**: What work items should be created?
4. **Output**: Summary + spawn recommendations

## Output Formats

### HYPOTHESIZE Output
```
## Memory Context
- [Related learnings from memory search]

## Hypotheses
1. **H1** (High confidence): [Hypothesis]
   - Evidence: [Supporting context]
2. **H2** (Medium confidence): [Hypothesis]
   - Evidence: [Supporting context]
```

### EXPLORE Output
```
## Evidence Gathered

| Hypothesis | Evidence | Source | Supports? |
|------------|----------|--------|-----------|
| H1 | [Finding] | [File:line] | Yes/No/Partial |

## Web Research
- [External sources if queried]
```

### CONCLUDE Output
```
## Findings Summary
[2-3 paragraph synthesis]

## Remaining Gaps
- [What we still don't know]

## Spawned Work Recommendations
- E2-XXX: [Proposed implementation]
- INV-XXX: [Follow-up investigation]
```

## Examples

**Input:** "HYPOTHESIZE phase for INV-023: ReasoningBank feedback loop gap"

**Output:**
```
## Memory Context
- Concept 77127-77138 document the gap
- Session 98 captured initial analysis

## Hypotheses
1. **H1** (High): Strategies are too generic because extraction lacks specificity
2. **H2** (Medium): No feedback signal means agent can't learn what's useful
3. **H3** (Low): Retrieval ranking algorithm is suboptimal
```
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Phase detection | Keyword in prompt | Simple, explicit, no state tracking needed |
| Memory first | Always query memory | Leverages existing learnings, avoids rediscovery |
| Tool set | Read, Grep, Glob, WebSearch, WebFetch, memory | Covers codebase + external + memory |
| Output format | Markdown tables/sections | Directly pasteable into investigation docs |

### Edge Cases

| Case | Handling |
|------|----------|
| No phase keyword | Default to EXPLORE behavior |
| Empty memory results | Note "No prior learnings found" and proceed |
| Web search fails | Fall back to codebase-only research |

---

## Implementation Steps

### Step 1: Create Agent File
- [ ] Create `.claude/agents/investigation-agent.md` from Detailed Design
- [ ] Verify YAML frontmatter format matches other agents

### Step 2: Update Status
- [ ] Run `just update-status-slim`
- [ ] Verify `investigation-agent` appears in agents list

### Step 3: Manual Verification
- [ ] Test HYPOTHESIZE phase invocation
- [ ] Test EXPLORE phase invocation
- [ ] Test CONCLUDE phase invocation

### Step 4: Update Investigation-Cycle Skill (Optional)
- [ ] Consider adding reference to investigation-agent in skill docs
- [ ] Document when to use agent vs manual research

### Step 5: README Sync (MUST)
- [ ] **MUST:** Update `.claude/agents/README.md` if it exists
- [ ] **MUST:** Update CLAUDE.md agents list reference

### Step 6: Consumer Verification
**SKIPPED:** New agent, no migrations or renames.

---

## Verification

- [ ] Agent file exists at `.claude/agents/investigation-agent.md`
- [ ] Agent appears in haios-status-slim.json agents list
- [ ] Manual invocation produces phase-appropriate output

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agent not discovered | Medium | Verify status.py discover_agents() finds file |
| Phase detection fails | Low | Simple keyword matching, fallback to EXPLORE |
| Memory query times out | Low | Agent continues with empty results |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 99 | 2025-12-22 | - | draft | Plan created |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/agents/investigation-agent.md` | File exists with correct frontmatter | [x] | Created with phase-aware instructions |
| `.claude/haios-status-slim.json` | `investigation-agent` in agents list | [x] | Confirmed in vitals |
| `.claude/templates/investigation.md` | Updated to v1.2 | [x] | Added phase guidance, memory_refs, closure checklist |

**Verification Commands:**
```bash
just update-status-slim
# Result: investigation-agent in agents list

# Manual test:
Task(prompt='HYPOTHESIZE phase for INV-023...', subagent_type='investigation-agent')
# Result: Comprehensive response with memory context, 4 hypotheses, test methods
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| Agent file created? | Yes | .claude/agents/investigation-agent.md |
| Agent discovered in status? | Yes | Appears in vitals |
| Manual test successful? | Yes | Full HYPOTHESIZE output for INV-023 |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Agent file created
- [x] Agent discovered by status module
- [x] WHY captured (memory refs: 77152-77163)
- [x] Manual invocation verified
- [x] Ground Truth Verification completed above

---

## References

- INV-017: Observability Gap Analysis (spawned this work)
- INV-022: Work-Cycle-DAG Unified Architecture (architecture context)
- E2-111: Investigation Cycle Skill (consumer of this agent)
- E2-093: Preflight Checker (pattern reference)

---
