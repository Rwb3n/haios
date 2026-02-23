---
template: work_item
id: WORK-203
title: "Session Event Log for Agent Ambient Visibility"
type: investigation
status: active
owner: Hephaestus
created: 2026-02-23
spawned_by: null
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: small
traces_to:
  - REQ-CEREMONY-001
requirement_refs: []
source_files:
  - .claude/hooks/
  - .claude/haios/governance-events.jsonl
acceptance_criteria:
  - "Analysis of what session events are worth persisting (commits, phase transitions, spawns, test results)"
  - "Proposed injection points: which hooks already fire at the right moments"
  - "Format design: append-only log vs structured file, retention policy"
  - "Consumption design: coldstart summary, on-demand command, phase-transition injection"
  - "Token cost analysis: writing cost vs reading cost vs current reconstruction-from-memory cost"
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-02-23T13:10:20
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-23
last_updated: 2026-02-23T13:10:20
---
# WORK-203: Session Event Log for Agent Ambient Visibility

---

## Context

During S430, the agent (Hephaestus) was asked about ambient visibility of session state. The current hook system injects per-prompt status (time, session, working item, context %). But the agent has no durable record of *session history* — commits made, phases traversed, work spawned, tests run. This information exists transiently in context but is lost on compaction.

The agent reconstructed a full session summary from working memory, but noted: "If this session had compacted, I'd lose the details."

**The gap:** Hooks fire at the right moments (phase transitions, tool use, session events) but don't persist a session trace. The agent carries session history in volatile context, not durable storage.

**Proposed concept:** A lightweight append-only session event log that hooks write to automatically. Key events:
- Cycle/phase transitions (already detected by set-cycle)
- Git commits (already detected by PostToolUse on Bash)
- Test results (already detected by PostToolUse on Bash)
- Work spawns (detectable from scaffold calls)
- Ceremony completions (detectable from skill invocations)

**Consumption points (3 natural injection moments):**
1. **Coldstart** — "Here's what happened last session" (replaces lossy checkpoint pending field)
2. **Phase transitions** — "Here's what the prior phase produced" (catches context loss between phases)
3. **On demand** — `/dashboard` or `/session-status` command (zero cost when unused)

**Relationship to existing infrastructure:**
- governance-events.jsonl already logs some events but may have gaps (see WORK-201)
- Checkpoint manifests capture end-of-session state but not the trace
- CH-066 (MCP operations server) may be the natural home for this capability

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning) -->

- [ ] Investigation document with findings and recommendations
- [ ] Event taxonomy: which events, what data, what format
- [ ] Injection point analysis: which hooks, what cost
- [ ] Consumption design: when to read, how to summarize

---

## History

### 2026-02-23 - Created (Session 430)
- Operator asked about agent ambient visibility during post-closure conversation
- Agent identified the gap between per-prompt status injection and session-level history
- Natural fit for Arc 1 (call) CH-059 ceremony automation

---

## References

- @.claude/hooks/ (existing hook infrastructure)
- @.claude/haios/governance-events.jsonl (existing event log, possibly incomplete per WORK-201)
- @docs/work/active/WORK-201/WORK.md (related: governance events gap)
- CH-066 (MCP operations server — potential home for this capability)
