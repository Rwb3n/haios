# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:30:45
# Chapter: Queue Ceremonies

## Definition

**Chapter ID:** CH-010
**Arc:** queue
**Status:** Planned
**Implementation Type:** CREATE NEW
**Depends:** CH-009
**Work Items:** None

---

## Current State (Verified)

**Source:** `.claude/skills/`

No queue ceremony skills exist:
- No `queue-intake.md`
- No `queue-prioritize.md`
- No `queue-commit.md`
- No `queue-release.md`

**Related existing skills:**
- `work-creation-cycle` - creates work items (similar to Intake)
- `survey-cycle` - selects work from queue (similar to Commit)
- `close-work-cycle` - closes work (IS the Release ceremony per CH-008)

**What exists:**
- work-creation-cycle creates work items
- survey-cycle selects from `just ready`
- close-work-cycle IS the Release ceremony (CH-008 decision)
- governance-events.jsonl logs events

**What doesn't exist:**
- Formal Intake ceremony (work-creation doesn't set queue_position)
- Prioritize ceremony (backlog→ready transition)
- Commit ceremony (ready→working transition)
- QueueCeremony event type in governance-events

---

## Problem

Queue transition ceremonies don't exist as formal skills. work-creation, survey, and close-work serve similar purposes but don't track queue_position transitions.

---

## Agent Need

> "I need ceremonies for each queue transition so queue state changes are governed, logged, and accountable like other state changes."

---

## Requirements

### R1: Four Queue Ceremonies (REQ-QUEUE-004)

Each queue transition has a ceremony:

| Ceremony | Transition | Signature | Implementation |
|----------|------------|-----------|----------------|
| Intake | → backlog | `Idea → BacklogItem` | Extend work-creation-cycle |
| Prioritize | backlog → ready | `[BacklogItems] → [ReadyItems]` | NEW skill |
| Commit | ready → working | `ReadyItem → WorkingItem` | Extend survey-cycle |
| Release | working → done | `WorkingItem → DoneItem` | **IS close-work-cycle** (CH-008) |

**NOTE:** Per CH-008 decision, Release ceremony IS close-work-cycle. No separate Release skill needed.

### R2: Ceremony Contracts

Each ceremony has input/output contract per REQ-CEREMONY-002:

**Intake:**
- Input: idea description, traces_to requirement
- Output: WORK.md at queue_position=backlog

**Prioritize:**
- Input: list of backlog items
- Output: updated queue_positions, priority rationale

**Commit:**
- Input: ready item ID
- Output: active item, work session started

**Release:**
- Input: active item ID, completion evidence
- Output: done item, DoD verified

### R3: Ceremony Logging

All ceremonies log to governance-events.jsonl:

```jsonl
{"type": "QueueCeremony", "ceremony": "Prioritize", "items": ["WORK-001"], "from": "backlog", "to": "ready", ...}
```

---

## Interface

### Ceremony Skills

```
skills/
  queue-intake.md       # Create work item at backlog
  queue-prioritize.md   # Move items backlog → ready
  queue-commit.md       # Move item ready → active
  queue-release.md      # Move item active → done
```

### queue-intake Skill

```yaml
---
name: queue-intake
triggers: ["intake", "capture idea"]
---

## Input Contract
- description: What is the idea/work?
- traces_to: Which requirement does this trace to?

## Ceremony Steps
1. Validate traces_to exists
2. Create WORK.md with queue_position=backlog
3. Log IntakeEvent

## Output Contract
- work_id: Created WORK-XXX
- queue_position: backlog
```

### queue-prioritize Skill

```yaml
---
name: queue-prioritize
triggers: ["prioritize", "triage backlog"]
---

## Input Contract
- items: List of backlog work IDs to prioritize

## Ceremony Steps
1. Review each item
2. Assess dependencies
3. Update queue_position to ready
4. Log PrioritizeEvent with rationale

## Output Contract
- prioritized: List of work IDs now ready
- rationale: Why these items, in this order
```

---

## Success Criteria

- [ ] 4 queue ceremony skills created
- [ ] Each ceremony has input/output contract
- [ ] Ceremonies log to governance-events.jsonl
- [ ] Intake creates work at backlog
- [ ] Prioritize moves backlog → ready
- [ ] Commit moves ready → active
- [ ] Release moves active → done
- [ ] Unit tests for each ceremony
- [ ] Integration test: full queue lifecycle via ceremonies

---

## Non-Goals

- Automated prioritization (ceremonies are manual)
- Priority scoring algorithms (future work)
- Queue capacity management (not needed)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-QUEUE-004, REQ-CEREMONY-002)
- @.claude/haios/epochs/E2_5/arcs/queue/CH-009-QueueLifecycle.md (lifecycle definition)
- @.claude/haios/epochs/E2_5/arcs/ceremonies/CH-011-CeremonyContracts.md (contract pattern)
