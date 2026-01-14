# generated: 2025-12-30
# System Auto: last updated on: 2025-12-30T23:46:37
# Section 10: Skills Taxonomy

Generated: 2025-12-30 (Session 151)
Purpose: Categorize all skills by type, invocation pattern, and memory integration
Status: COMPLETE

---

## Gaps Identified (S152 Analysis)

| Gap | Description | Target Fix |
|-----|-------------|------------|
| **Category is documentation, not code** | 7+3+5 split exists only in docs, not enforced | Add `category` field to SKILL.md frontmatter |
| **Bridge vs Cycle unclear in code** | Same structure, conceptual distinction only | Formalize in skill-manifest.yaml |
| **routing-gate is bridge behavior** | Listed as utility but invoked BY cycles | Reclassify or document as "special" |

---

## Target Architecture: Skill Manifest

```yaml
# .claude/haios/config/skill-manifest.yaml
skills:
  implementation-cycle:
    category: cycle
    phases: [PLAN, DO, CHECK, DONE, CHAIN]
    node_binding: implement
    memory:
      query_at: [DO]
      store_at: [DONE]
    gates:
      PLAN: [plan-validation-cycle, preflight-checker]
      DO: [design-review-validation]
    chain:
      terminal: false
      routing: routing_gate

  plan-validation-cycle:
    category: bridge
    invoked_by: [implementation-cycle]
    standalone: false
    blocking: true

  routing-gate:
    category: bridge  # Actually bridge, not utility
    invoked_by: [implementation-cycle, investigation-cycle, close-work-cycle, plan-authoring-cycle, work-creation-cycle]
    standalone: false
    note: "Exception: work-creation-cycle uses confidence_based instead"

  memory-agent:
    category: utility
    standalone: true
    memory:
      query_at: [always]
```

**Portable:** Skills are Claude CLI native. Manifest in `.claude/haios/config/` for LLM-agnostic orchestration.

---

## Overview

Skills are prompt-based orchestration units. They live in `.claude/skills/<name>/SKILL.md` and are invoked via `Skill(skill="<name>")`.

**Location:** `.claude/skills/` (15 skill directories)
**Invocation:** `Skill(skill="<name>")`

---

## Skill Categories

### Category 1: Cycles (7)
Multi-phase prompt sequences with gates. Each phase injects context that drives completion.

| Skill | Phases | Node Binding | Memory |
|-------|--------|--------------|--------|
| `implementation-cycle` | PLAN→DO→CHECK→DONE→CHAIN | implement | Query (DO) |
| `investigation-cycle` | HYPOTHESIZE→EXPLORE→CONCLUDE→CHAIN | discovery | Query (start), Store (end) |
| `close-work-cycle` | VALIDATE→OBSERVE→ARCHIVE→MEMORY→CHAIN | close | Store (MEMORY) |
| `work-creation-cycle` | VERIFY→POPULATE→READY→CHAIN | backlog | Query (VERIFY) |
| `checkpoint-cycle` | SCAFFOLD→FILL→VERIFY→CAPTURE→COMMIT | (none) | Store (CAPTURE) |
| `observation-triage-cycle` | SCAN→TRIAGE→PROMOTE | (none) | - |
| `plan-authoring-cycle` | ANALYZE→AUTHOR→VALIDATE→CHAIN | plan | Query (ANALYZE) |

### Category 2: Bridges (3)
Blocking validators. Must pass to continue. Gate the prompt cascade.

| Skill | Purpose | Invoked By |
|-------|---------|------------|
| `plan-validation-cycle` | Pre-DO plan quality check | implementation-cycle PLAN |
| `design-review-validation` | During-DO design alignment | implementation-cycle DO |
| `dod-validation-cycle` | Post-DO DoD criteria check | implementation-cycle CHECK |

### Category 3: Routers (1)
Continuation selectors. Choose which prompt gets injected next. The decision point for autonomous work loops.

| Skill | Purpose | Invoked By |
|-------|---------|------------|
| `routing-gate` | Select next cycle based on work type + state | 5/7 cycles at CHAIN phase |

**The emergence:** routing-gate doesn't validate or compute - it **decides what prompt to inject next**. This is the continuation trigger that enables autonomous work loops via prompt chaining.

**Exception:** `work-creation-cycle` uses `confidence_based` routing (prefix-based: INV-* → investigation, else → implementation) instead of routing-gate.

### Category 4: Utilities (4)
One-shot capabilities. Stateless helpers.

| Skill | Purpose | Memory |
|-------|---------|--------|
| `memory-agent` | Strategy retrieval before complex tasks | Query |
| `audit` | Find gaps, drift, stale items | - |
| `schema-ref` | Database schema lookup | - |
| `extract-content` | Entity/concept extraction | Store |

---

## Cycle Phases (Normalized from SECTION-2E)

All cycles follow a similar structure:

```
ENTRY → [Phase 1] → [Phase 2] → ... → [Phase N] → CHAIN → EXIT
         ↑                               ↑
      entry_criteria              exit_criteria
      (prerequisites)             (completion gates)
```

### Phase Structure

| Component | Purpose |
|-----------|---------|
| `name` | Phase identifier (e.g., "PLAN", "DO") |
| `description` | What happens in this phase |
| `entry_criteria` | Prerequisites to enter (optional) |
| `exit_criteria` | Gates to pass before proceeding |
| `actions` | What the agent should do |

---

## Memory Integration Patterns

### Pattern 1: Query at Start
```python
# investigation-cycle HYPOTHESIZE, work-creation-cycle VERIFY
memory_search_with_experience(query="prior work on {topic}", mode='semantic')
```

### Pattern 2: Store at End
```python
# checkpoint-cycle CAPTURE, close-work-cycle MEMORY
ingester_ingest(content="Learning: {insight}", source_path="...")
```

### Pattern 3: Query During
```python
# implementation-cycle DO, memory-agent
memory_search_with_experience(query="strategies for {task}")
```

### Memory Integration by Skill

| Skill | Query | Store | Mode |
|-------|-------|-------|------|
| implementation-cycle | DO phase | - | semantic |
| investigation-cycle | HYPOTHESIZE | CONCLUDE | session_recovery |
| close-work-cycle | - | MEMORY phase | techne |
| work-creation-cycle | VERIFY | - | semantic |
| checkpoint-cycle | - | CAPTURE | episteme |
| plan-authoring-cycle | ANALYZE | - | semantic |
| memory-agent | Always | - | varies |
| extract-content | - | Always | - |
| observation-triage-cycle | - | - | - |
| audit | - | - | - |
| routing-gate | - | - | - |
| bridges | - | - | - |

---

## Skill Structure

### Directory Layout
```
.claude/skills/<name>/
├── SKILL.md          ← Main prompt (required)
├── README.md         ← Usage documentation (optional)
└── (supporting files)
```

### SKILL.md Anatomy

```markdown
---
name: implementation-cycle
description: PLAN-DO-CHECK-DONE workflow with MUST gates
generated: 2025-12-25
last_updated: 2025-12-28
---

# Implementation Cycle

## When to Use
[Triggering conditions]

## The Cycle
[Phase diagram]

### 1. PLAN Phase
**Goal:** [Phase objective]
**Actions:** [What to do]
**Exit Criteria:** [Gates to pass]

### 2. DO Phase
...

## Composition Map
[Tools, memory, commands per phase]
```

---

## Invocation Patterns

### Human-Invoked (via Slash Command)
```
User: /new-plan E2-123 "My Feature"
→ Command loads
→ Skill(skill="plan-authoring-cycle")
```

### Agent-Invoked (Direct)
```
Skill(skill="memory-agent")
Skill(skill="implementation-cycle")
```

### Cycle-Invoked (CHAIN Phase)
```
investigation-cycle CHAIN
    ↓
routing-gate
    ↓
implementation-cycle (if has_plan)
```

---

## Bridge vs Cycle

| Aspect | Cycle | Bridge |
|--------|-------|--------|
| Phases | Multiple (4-5) | Single-purpose |
| Node binding | Yes | No |
| CHAIN phase | Yes | No |
| Standalone | Yes | No (invoked by cycle) |
| Memory integration | Often | Rarely |

**Example:** `plan-validation-cycle` is a bridge because it:
- Has no node binding
- Is invoked by implementation-cycle
- Doesn't chain to next work
- Just validates and returns

---

## Utility vs Cycle

| Aspect | Cycle | Utility |
|--------|-------|---------|
| Phases | Defined | Stateless |
| State management | Current phase tracked | No state |
| Exit criteria | Per-phase gates | Single output |
| Purpose | Orchestrate work | Provide capability |

**Example:** `memory-agent` is a utility because it:
- Has no phases
- Just queries memory and returns
- Doesn't manage work state

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Cycles have CHAIN | All cycles end with routing | Autonomous work loop |
| Bridges are gatekeepers | Block until criteria met | Quality enforcement |
| Utilities are stateless | No phase tracking | Reusable anywhere |
| Memory patterns vary | Query/Store/Both/None | Match skill purpose |

---

*Populated Session 151*
