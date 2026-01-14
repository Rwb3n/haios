---
template: investigation
status: active
date: 2025-12-22
backlog_id: INV-023
title: "Investigation: ReasoningBank Feedback Loop Architecture"
author: Hephaestus
session: 98
lifecycle_phase: discovery
spawned_by: Session-98
related: [INV-020, ADR-037, E2-083, INV-014, INV-015]
milestone: M4-Research
version: "1.2"
generated: 2025-12-22
last_updated: 2025-12-23T11:00:47
---
# Investigation: ReasoningBank Feedback Loop Architecture

@docs/README.md
@docs/epistemic_state.md
@.claude/REFS/GOVERNANCE.md

---

## Context

**Trigger:** Session 98 observation during E2-113 planning.

**What Happened:**
1. Agent queried `memory_search_with_experience` for implementation strategies
2. Memory returned relevant concept (76839 - E2-097 event logging pattern)
3. Memory also returned `relevant_strategies` in reasoning section
4. Agent noted the concept, then proceeded without explicitly applying it
5. **No feedback was sent to memory system indicating the result was useful**

**Operator Insight:**
> "How do we leverage ReasoningBank and loop back to the memory system as that specific memory being good for what we are about to do now? Is it deep down that you know 90% of those queries are noise and therefore hard work to action on because of this?"

**The Core Problem:**

```
Current Flow:
  Store → Embed → Query → Retrieve → (maybe use) → END
                                            ↑
                                   No feedback loop

Missing:
  Store → Embed → Query → Retrieve → USE → FEEDBACK → Improved retrieval
```

ReasoningBank is **write-heavy, read-weak**:
- Significant effort into capturing learnings (ingester_ingest, stop hook)
- Retrieval works (embedding similarity finds related concepts)
- But no mechanism to improve retrieval based on actual usefulness
- No "click-through" equivalent - system can't learn what was helpful

---

## Objective

Investigate how to close the ReasoningBank feedback loop so that:
1. Useful retrievals are reinforced (improve future retrieval)
2. Noise is identified and deprioritized
3. Agent is incentivized to actually USE retrieved strategies
4. Cross-pollination happens automatically (good matches strengthen connections)

---

## Scope

### In Scope
- Current ReasoningBank architecture analysis
- Feedback mechanisms design
- Signal-to-noise improvement strategies
- Integration with existing memory tools
- Connection to INV-020 (LLM Energy Channeling)

### Out of Scope
- Major embedding model changes
- Database schema redesign
- Synthesis algorithm changes (separate concern)

---

## Hypotheses

| # | Hypothesis | Test Method | Priority | Prior Testing |
|---|------------|-------------|----------|---------------|
| **H1** | Agent has learned to discount memory results due to low signal-to-noise | Analyze agent behavior across sessions when memory is retrieved | 1st | Observation-based |
| **H2** | Strategies returned are often meta/generic rather than task-specific | Categorize strategies by type, measure specificity | 2nd | **CONFIRMED by INV-014 H3** |
| **H3** | Embedding similarity ≠ task relevance (fundamental mismatch) | Compare embedding distance vs actual usefulness | 3rd | **Researched by INV-015** |
| **H4** | Explicit feedback would improve retrieval over time | Design feedback mechanism, simulate improvement | 4th | **Options A-E from INV-015** |
| **H5** | Implicit signals (references in output) could substitute for explicit feedback | Analyze checkpoint memory_refs, correlate with task success | 5th | Untested |

---

## Investigation Steps

### Phase 1: Problem Analysis (Session 98) - COMPLETE

1. [x] Document the observed behavior (query → retrieve → ignore)
2. [x] Identify the feedback loop gap
3. [x] Capture operator insight about learned discounting
4. [x] Add to epistemic_state.md as Active Knowledge Gap
5. [x] Create this investigation

### Phase 2: Current State Analysis (Future)

6. [ ] Audit `memory_search_with_experience` response structure
7. [ ] Categorize `relevant_strategies` by type (meta vs task-specific)
8. [ ] Measure how often retrieved concepts are actually referenced in output
9. [ ] Identify what would constitute "useful" vs "noise"

### Phase 3: Feedback Mechanism Design (Future)

10. [ ] Design explicit feedback options:
    - `memory_reinforce(concept_id, task_id, relevance_score)`
    - `memory_flag_noise(concept_id, reason)`
11. [ ] Design implicit feedback options:
    - Track concept_id when referenced in plan/checkpoint
    - Correlate with task completion success
12. [ ] Evaluate cross-pollination strategies:
    - Store "concept X was useful for task type Y"
    - Create semantic bridges between related concepts

### Phase 4: Integration Design (Future)

13. [ ] How does feedback integrate with current ingester/retrieval?
14. [ ] What schema changes (if any) are needed?
15. [ ] How to surface reinforced concepts in future queries?

---

## Findings

### Session 98 Findings (Phase 1)

**Observed Behavior Pattern:**
1. Agent queries memory before complex tasks (E2-083 pattern)
2. Results include relevant concepts AND strategies
3. Agent notes the best result in response
4. Agent proceeds without explicit application
5. No feedback sent to memory

**Root Cause Analysis:**

| Issue | Evidence | Impact |
|-------|----------|--------|
| **Learned discounting** | Agent skims and moves on | Low utilization of memory |
| **Strategy-task mismatch** | Strategies are about "searching" not "implementing" | Retrieved guidance not actionable |
| **No reinforcement signal** | Memory can't learn what was useful | No improvement over time |
| **Embedding ≠ relevance** | "investigation events" matches "lifecycle_phase" but also matches unrelated concepts | Noise in results |

**The Deeper Problem:**

ReasoningBank is like a search engine with no click-through data:
- It indexes content by embedding similarity
- It retrieves by semantic distance
- But it has no signal for "this result was actually helpful"
- So it can't improve its rankings over time

---

## Prior Work Consolidated (Session 102)

> **Note:** Findings from INV-014 and INV-015 (Sessions 72-73) consolidated here to advance this investigation.

### From INV-014: Memory Context Injection Architecture

**Confirmed Findings:**

| Finding | Status | Relevance to INV-023 |
|---------|--------|---------------------|
| **Truncation hardcoded at 150 chars** | UNRESOLVED | Low priority - injection disabled |
| **Mode parameter not used** | RESOLVED | `session_recovery` mode now active |
| **Strategies are meta-level** | CONFIRMED | **Directly supports H2** |
| **No type filtering** | PARTIALLY RESOLVED | session_recovery excludes SynthesizedInsight |
| **Format readability (semicolons)** | UNRESOLVED | Low priority - injection disabled |

**Key Evidence for H2:**
> Observed strategies: "Leverage Hybrid Search", "Evaluate Synthesis Quality from Context", "Clarify Scope for Ambiguous Queries" - all about HOW the system searches, not WHAT the user should do.

**Root Cause:** Strategy extraction in `extraction.py` captures patterns about system behavior, not domain knowledge.

### From INV-015: Retrieval Algorithm Intelligence

**RAG Technique Research (Options for H4):**

| Option | Technique | Complexity | Impact | Status |
|--------|-----------|------------|--------|--------|
| **A** | Query Rewriting | Low | High | **COMPLETE (E2-063)** |
| **B** | Cross-Encoder Rerank | Medium | High | Design available |
| **C** | Task-Type Classification | Medium | Medium | Design available |
| **D** | Feedback Loop | High | High | **THIS INVESTIGATION** |
| **E** | Time-Decay Ranking | Low | Medium | Not started |

**Recommended Sequence (from INV-015):**
1. A (Query Rewriting) - **DONE**
2. E (Time-Decay) - Low effort add
3. B (Cross-Encoder) - Significant accuracy boost
4. C (Task-Type) - Enables contextual queries
5. D (Feedback) - **INV-023 focus**

### Current System Decision

**Memory Injection Disabled (concept 71845):**
> "TRADE-OFF: Disabled automatic memory injection. Memory strategies still available via memory-agent skill but require explicit invocation."

**Reason (concept 71323):**
> "PROBLEM: Coldstart memory injection consumes ~60k tokens but returns philosophically-related rather than task-relevant content."

**Implication for INV-023:**
- Must fix signal-to-noise before re-enabling injection
- Feedback loop is the key missing piece
- Options B-E from INV-015 provide additional improvement paths

---

## Spawned Work Items

- [ ] E2-xxx: Implement `memory_reinforce` MCP tool (if investigation supports)
- [ ] E2-xxx: Add implicit usage tracking to post_tool_use hook
- [ ] E2-xxx: Strategy categorization and filtering
- [ ] ADR-04x: ReasoningBank Feedback Architecture (if investigation supports)

---

## Expected Deliverables

- [x] Problem documentation (this document)
- [x] epistemic_state.md update
- [ ] Current state analysis (Phase 2)
- [ ] Feedback mechanism design (Phase 3)
- [ ] Integration recommendation (Phase 4)
- [ ] ADR draft (if viable)
- [ ] Memory storage (concepts)

---

## Connection to INV-020

**INV-020** (LLM Energy Channeling Patterns) investigates how environmental constraints channel LLM behavior:
- Blockers > suggestions
- Subagents with isolated context prevent scope creep
- TodoWrite visible checkpointing improves task completion

**INV-023** extends this to memory retrieval:
- Retrieved strategies are "suggestions" - easily ignored
- No blocker mechanism for "you must apply this strategy"
- Feedback loop would create implicit reinforcement

**Shared Insight:** Information availability ≠ information usage. Both investigations address the "last mile" problem of getting agents to actually use available guidance.

---

## References

- **INV-020:** LLM Energy Channeling Patterns (related - channeling problem)
- **INV-014:** Memory Context Injection Architecture (findings consolidated Session 102)
- **INV-015:** Retrieval Algorithm Intelligence (findings consolidated Session 102)
- **ADR-037:** Hybrid Retrieval Architecture (current retrieval design)
- **E2-063:** Query Rewriting Layer (Option A from INV-015 - complete)
- **E2-083:** Proactive Memory Query (when queries happen)
- **epistemic_state.md:** Active Knowledge Gaps (INV-023 listed)
- **Memory:** Concepts 71323, 71845, 76839, 77127

---
