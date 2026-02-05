---
template: work_item
id: WORK-102
title: Session and Process Review Ceremonies
type: design
status: blocked
owner: Hephaestus
created: 2026-02-05
spawned_by: Session-314-review
chapter: null
arc: feedback
closed: null
priority: medium
effort: small
traces_to:
- REQ-FEEDBACK-001
- REQ-CEREMONY-002
requirement_refs: []
source_files:
- .claude/haios/manifesto/L4/functional_requirements.md
- .claude/skills/close-work-cycle/SKILL.md
- .claude/skills/observation-capture-cycle/SKILL.md
acceptance_criteria:
- Session Review ceremony defined with input/output contract
- Process Review ceremony defined with input/output contract
- Both added to Feedback category in ceremonies arc
- Skills created for both ceremonies
blocked_by: []
blocks: []
enables: []
queue_position: parked
cycle_phase: backlog
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-05 18:52:07
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  epoch: E2.6
  parked_for: E2.6
  parked_reason: New design work - includes operator-initiated system evolution ceremony
    which is out of E2.5 implementation scope
version: '2.0'
generated: 2026-02-05
last_updated: '2026-02-05T21:35:31'
---
# WORK-102: Session and Process Review Ceremonies

---

## Context

Session 314 demonstrated two natural review patterns that aren't formalized as ceremonies:

**1. Session Review** ("what went well / could've gone better")
- Retrospective on execution quality of a single session
- Input: session transcript, completed work
- Output: learnings stored to memory
- Distinct from observation-capture which is per-work-item, not per-session

**2. Process Review** ("keep doing / should be doing / stop doing")
- Retrospective on the process itself
- Input: Session Review findings + accumulated observations
- Output: L3/L4/arc/chapter modifications (system evolution)
- This IS the Requirements Review ceremony (REQ-FEEDBACK-004) but scoped to session-level rather than epoch-level

Currently observation-capture answers "what did I notice about this work item?" These ceremonies answer "how well did the system perform?" and "what should change?" - meta-level questions that produce system modifications.

**Key distinction:**

| | Observation Capture | Session Review | Process Review |
|---|---|---|---|
| Scope | Per work item | Per session | Per session (or accumulated) |
| Question | What did I notice? | How did execution go? | How should the system change? |
| Output | Memory entries | Learnings | L3/L4 modifications |

---

## Deliverables

- [ ] Session Review ceremony defined (input contract, output contract, trigger)
- [ ] Process Review ceremony defined (input contract, output contract, trigger)
- [ ] Both added to ceremonies arc Feedback category
- [ ] Skill files created for both
- [ ] Determine trigger: every session? operator-invoked? every N sessions?

---

## History

### 2026-02-05 - Created (Session 314)
- Operator asked "what went well / could've gone better" and "keep / should / stop"
- These natural review patterns recognized as missing ceremonies
- Operator confirmed: "these should be ceremonies"
- Further discussion revealed the ceremony chain is incomplete: Session Review and Process Review produce proposed changes, but there's no ceremony governing HOW upstream L3/L4 modifications get approved and applied
- The feedback arc assumes bottom-up flow (work -> chapter -> arc -> epoch -> requirements) but this session demonstrated top-down flow (operator reflection -> requirements change -> trickle down)
- Missing: "operator-initiated system evolution" ceremony with governance for deciding whether a finding becomes a memory note, observation, work item, or immediate L3/L4 modification
- Parked for E2.6: this is new design work, not E2.5 implementation scope

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-FEEDBACK-001 to 005)
- @.claude/haios/epochs/E2_5/arcs/feedback/ARC.md
- @.claude/haios/epochs/E2_5/arcs/ceremonies/ARC.md
- @.claude/skills/observation-capture-cycle/SKILL.md (existing per-work-item reflection)
