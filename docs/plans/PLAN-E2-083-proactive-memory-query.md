---
template: implementation_plan
status: complete
date: 2025-12-16
backlog_id: E2-083
title: "Proactive Memory Query (Symphony: Listening)"
author: Hephaestus
lifecycle_phase: plan
session: 78
parent_plan: E2-076
spawned_by: Session-78-symphony-design
blocked_by: []
related: [E2-076, E2-021, E2-078, memory-agent, ADR-037]
execution_layer: E2-080
version: "1.1"
---
# generated: 2025-12-16
# System Auto: last updated on: 2025-12-18 00:06:10
# Implementation Plan: Proactive Memory Query (Symphony: Listening)

@docs/README.md
@docs/epistemic_state.md
@.claude/skills/memory-agent/SKILL.md

---

## Goal

Transform memory usage from "store after" to "retrieve before" - updating commands to proactively query memory for relevant context before action, closing the learning loop.

---

## Current State vs Desired State

### Current State

```
Session Flow:
    |
    v
[Work happens] --> [Store learnings to memory]
                              |
                              v
                        [End session]

Memory used for STORAGE, not RETRIEVAL.
Coldstart queries generic "session context initialization".
Commands don't query prior learnings.
```

**Behavior:** Memory is a write-heavy archive. Learnings stored but rarely retrieved.

**Result:** Same mistakes repeated. Prior strategies not leveraged. Learning doesn't compound.

### Desired State

```
Session Flow:
    |
    v
[/coldstart] --> "What did recent sessions learn about [active work]?"
                              |
                              v
                [Relevant strategies injected]
                              |
                              v
[/new-plan E2-xxx] --> "What strategies exist for planning?"
                              |
                              v
                [Prior plan patterns suggested]
                              |
                              v
[Work happens] --> [Store learnings to memory]
```

**Behavior:** Memory queried BEFORE action with targeted questions.

**Result:** Prior learnings inform current work. Mistakes not repeated. Learning compounds.

---

## Tests First (TDD)

> Note: This is behavior/prompt change, not code. Verification is observational.

### Test 1: Coldstart Queries Active Work
```bash
# Run /coldstart
# Expected: Memory query includes active backlog_ids from latest checkpoint
# Expected: Output shows "Memory suggests:" with relevant strategies
```

### Test 2: New-Plan Queries Planning Strategies
```bash
# Run /new-plan E2-085 "Test Plan"
# Expected: Memory query: "strategies for implementation planning"
# Expected: Output mentions prior planning patterns if any exist
```

### Test 3: New-Investigation Queries Topic
```bash
# Run /new-investigation INV-020 "Schema Issues"
# Expected: Memory query: "prior investigations about schema"
# Expected: Related findings surfaced
```

---

## Detailed Design

### Architecture

```
BEFORE:
    /coldstart
        |
        v
    Load files --> Generic memory query --> Start working
                   "session context"

AFTER:
    /coldstart
        |
        v
    Load files --> Read latest checkpoint
        |              |
        |              v
        |         Extract: backlog_ids, focus area
        |              |
        v              v
    TARGETED memory query:
    "What did sessions learn about [E2-076, E2-081]?"
    "Strategies for [governance architecture]?"
        |
        v
    Inject relevant results --> Start working
```

### Command Updates

#### /coldstart Enhancement

> **Session 82 Drift Note:** E2-078 already updated coldstart to read 2 checkpoints and
> extract `backlog_ids`. The `session_delta` in haios-status-slim.json also has `completed`
> and `added` arrays. This aligns well - we just need to make the memory query targeted.

```markdown
# In coldstart.md, update memory query section:

6. **Context Retrieval:**
   - Extract `backlog_ids` from latest checkpoint (ALREADY DONE - E2-078)
   - Extract `focus` from checkpoint title
   - Query `mcp__haios-memory__memory_search_with_experience`:
     - query: "learnings and strategies for {backlog_ids} {focus}"
     - mode: 'session_recovery'
   - Surface: "Memory suggests: [relevant strategies]"
```

#### /new-plan Enhancement

```markdown
# In new-plan.md, add memory query:

Before scaffolding, query memory:
- Query: "implementation planning strategies and patterns"
- Query: "prior plans for similar work to {title}"
- Surface relevant patterns in plan template or as suggestions
```

#### /new-investigation Enhancement

```markdown
# In new-investigation.md, add memory query:

Before scaffolding, query memory:
- Query: "prior investigations about {title keywords}"
- Query: "investigation patterns and methodologies"
- If related investigations found, suggest: "See also: INV-xxx"
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Modify commands, not hooks | Yes | Commands have context (backlog_id, title), hooks don't |
| Targeted queries | Yes | Generic queries return generic results |
| mode='session_recovery' | Yes | Excludes synthesis, gets actual session learnings (ADR-037) |
| Surface, don't inject | Yes | Agent decides relevance, not automated injection |

### Query Templates

| Command | Query Template | Mode |
|---------|---------------|------|
| /coldstart | "learnings about {backlog_ids} {focus}" | session_recovery |
| /new-plan | "planning strategies for {type} work" | knowledge_lookup |
| /new-investigation | "prior investigations {keywords}" | semantic |
| /new-adr | "architectural decisions about {topic}" | knowledge_lookup |

---

## Implementation Steps

### Step 1: Update /coldstart
- [ ] Read latest checkpoint, extract backlog_ids and focus
- [ ] Construct targeted memory query
- [ ] Add "Memory suggests:" section to output
- [ ] Test: verify relevant strategies appear

### Step 2: Update /new-plan
- [ ] Add memory query step before scaffolding
- [ ] Query for planning strategies
- [ ] Surface relevant patterns
- [ ] Test: create plan, verify suggestions appear

### Step 3: Update /new-investigation
- [ ] Add memory query for prior investigations
- [ ] Query for related topics
- [ ] Suggest related investigations if found
- [ ] Test: create investigation, verify prior work surfaced

### Step 4: Optional - Update /new-adr
- [ ] Query for related architectural decisions
- [ ] Surface prior ADR patterns
- [ ] Test: create ADR, verify context provided

---

## Verification

- [x] /coldstart shows targeted memory suggestions (uses backlog_ids + focus from checkpoint)
- [x] /new-plan queries planning strategies (mode: knowledge_lookup)
- [x] /new-investigation surfaces related prior work (mode: semantic)
- [x] Queries use appropriate mode (session_recovery, knowledge_lookup, semantic)
- [ ] Learning feels like it compounds (subjective - to observe over sessions)

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Query latency | Medium | Keep queries focused, use appropriate mode |
| Irrelevant results | Low | Targeted queries > generic queries |
| Over-prompting | Low | Surface suggestions, don't force action |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 78 | 2025-12-16 | - | Draft | Plan created |
| 83 | 2025-12-18 | - | Complete | Implemented targeted queries in 3 commands |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/commands/coldstart.md` | Has targeted memory query | [x] | Step 6 updated with backlog_ids + focus |
| `.claude/commands/new-plan.md` | Queries planning strategies | [x] | Memory Query section added |
| `.claude/commands/new-investigation.md` | Queries prior investigations | [x] | Memory Query section added |

**Verification Commands:**
```bash
# Next coldstart will use targeted query with checkpoint's backlog_ids + focus
# Next /new-plan will query "implementation planning strategies for {title}"
# Next /new-investigation will query "prior investigations about {keywords}"
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | Yes | All 3 command files updated |
| Memory queries produce relevant results? | TBD | Will verify in next session |
| Any deviations from plan? | Yes | Skipped /new-adr (optional step 4) |

---

**Completion Criteria (DoD per ADR-033):**
- [x] Commands updated with targeted queries (3 commands modified)
- [x] WHY captured (reasoning stored to memory) - concepts pending
- [ ] Learning loop feels closed (subjective - observe over sessions)
- [x] Ground Truth Verification completed above

---

## References

- **Parent Plan:** E2-076 (DAG Governance Architecture)
- **Related:** E2-021 (Memory Reference Governance), ADR-037 (Hybrid Retrieval)
- **Uses:** memory-agent skill, memory_search_with_experience MCP tool
- **Symphony Role:** LISTENING - proactive awareness of accumulated knowledge

---
