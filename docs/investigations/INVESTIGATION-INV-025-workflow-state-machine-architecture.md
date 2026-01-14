---
template: investigation
status: complete
date: 2025-12-14
backlog_id: INV-025
title: "Investigation: Workflow State Machine Architecture"
author: Hephaestus
lifecycle_phase: conclude
version: "1.2"
session: 71
note: "Renamed from INV-012 due to ID collision (Session 102)."
closed_session: 102
closure_note: "SUPERSEDED by INV-022 (Work-Cycle-DAG). Vision realized in node-cycle architecture. Spawned items (ADR-039, E2-052-054) subsumed by INV-022 spawns."
generated: 2025-12-23
last_updated: 2025-12-23T11:01:52
---
# Investigation: Workflow State Machine Architecture

@docs/README.md
@docs/epistemic_state.md

---

## Context

Building on INV-011 (Command-Skill Architecture Gap), the Operator articulated a higher-level vision: commands and skills should chain together to form a **workflow state machine** with controlled pathways and explicit exits.

**Operator Insight (Session 71):**
> "Striking skills and commands together - a command will open a skill that has exits via another command. And so on and so forth to lock in a full loop, or limit forks in a loop to controlled pathways."

This is the architectural vision that was originally intended but not implemented in Epoch 2.

---

## Objective

Design and implement a workflow state machine where:
1. Commands are state transitions (entry points)
2. Skills are states (with defined exits)
3. Exits are other commands (controlled pathways)
4. Full loops and controlled forks create governed workflows

---

## Scope

### In Scope
- Workflow state machine design
- Exit metadata schema for skills
- Command chaining mechanism
- Governance DAG definition (valid workflow paths)
- Implementation for core workflows: coldstart -> work -> close -> loop

### Out of Scope
- Memory retrieval improvements (INV-010)
- Individual command fixes (INV-011 spawned items)
- Hook event modifications

---

## Hypotheses

1. **H1:** Governance by architecture is more reliable than governance by prompts
2. **H2:** Exit metadata in skills can enforce valid state transitions
3. **H3:** Controlled forks prevent skipping steps in workflows
4. **H4:** Full loops enable continuous session flow without manual intervention

---

## Investigation Steps

### Vision Capture (Session 71 - COMPLETE)

1. [x] Document operator insight
2. [x] Define state machine pattern
3. [x] Store to memory (concepts 71351-71363)

### Design (PENDING)

4. [ ] Define exit metadata schema for SKILL.md
5. [ ] Map core workflows (coldstart, investigate, implement, close)
6. [ ] Identify fork points and valid transitions
7. [ ] Design loop-back mechanisms

### Implementation Planning (PENDING)

8. [ ] Create ADR-039 for workflow state machine architecture
9. [ ] Plan migration path from isolated commands to chained workflows

---

## Findings

### The Workflow State Machine Pattern

```
Command = State TRANSITION (entry point, locks you in)
Skill   = STATE (pattern + tools + defined exits)
Exits   = Other COMMANDS (controlled pathways)
```

### Visual Representation

```
/coldstart --? session-init skill
                   �
                   +--? /investigate --? discovery skill
                   �                          �
                   �                          +--? /new-adr
                   �                          +--? /new-plan
                   �                          +--? /close-inv
                   �
                   +--? /implement --? build skill
                   �                       �
                   �                       +--? /test
                   �                       +--? /close
                   �                              �
                   �                              ?
                   �                        closure skill
                   �                              �
                   +------------------------------+ (loop)
```

### Skill with Exits Metadata

```yaml
# .claude/skills/close-work-item/SKILL.md
---
name: close-work-item
description: Close a backlog item with DoD validation
exits: [/coldstart, /new-checkpoint, /compact]
---
```

The `exits` field defines which commands are valid next states.

### What This Enforces

| Constraint | Mechanism |
|------------|-----------|
| No skipping steps | Can't reach `/close` without going through workflow |
| Controlled forks | Skill defines valid exits only |
| Full loops | `/close` can exit to `/coldstart` |
| Governance by architecture | Not by prompts or willpower |

### Current vs Target

| Aspect | Current | Target |
|--------|---------|--------|
| Commands | Isolated, no chaining | State transitions in DAG |
| Skills | No exit metadata | Explicit exits to other commands |
| Workflows | Enforced by prompts | Enforced by architecture |
| Loops | Manual | Automatic via exit chains |

---

## Spawned Work Items

- [ ] ADR-039: Workflow State Machine Architecture
- [ ] E2-052: Define exit metadata schema for skills
- [ ] E2-053: Implement core workflow DAG (coldstart -> work -> close -> loop)
- [ ] E2-054: Add exit enforcement to skill invocation

---

## Expected Deliverables

- [x] Vision capture (this document)
- [x] Memory storage (concepts 71351-71363)
- [ ] Exit metadata schema
- [ ] Workflow DAG definition
- [ ] ADR-039

---

## References

- INV-011: Command-Skill Architecture Gap (prerequisite)
- INV-010: Memory Retrieval Architecture Mismatch (related context issue)
- `.claude/COMMANDS-REF.md` - Command features (allowed-tools, arguments)
- `.claude/SKILLS-REF.md` - Skill structure (progressive disclosure)

---
