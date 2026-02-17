---
template: work_item
id: WORK-160
title: "Ceremony Automation"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-17
spawned_by: Session-394-decomposition
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: high
effort: large
traces_to:
  - REQ-CEREMONY-002
requirement_refs: []
source_files:
  - .claude/skills/implementation-cycle/SKILL.md
  - .claude/skills/close-work-cycle/SKILL.md
  - .claude/skills/retro-cycle/SKILL.md
  - .claude/hooks/PreToolUse/governance-state.md
acceptance_criteria:
  - "At least 3 mechanical ceremony phases migrated from SKILL.md to hooks/modules"
  - "Session-end ceremony runs automatically via hook (not agent-read skill)"
  - "Checkpoint population automated for standard fields"
  - "cycle_phase advancement automated via PostToolUse hook"
  - "Zero regression in existing ceremony behavior"
blocked_by:
  - WORK-101
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-02-17T22:08:08
    exited: null
artifacts: []
cycle_docs: {}
memory_refs:
  - 85390
  - 84857
  - 85607
extensions:
  epoch: E2.8
  depends_on_design: WORK-101
version: "2.0"
generated: 2026-02-17
last_updated: 2026-02-17T22:08:08
---
# WORK-160: Ceremony Automation

---

## Context

Ceremony skills (SKILL.md) consume 100% agent tokens because the agent is the runtime — it reads the markdown and executes the instructions. Full ceremony chain = ~104% of 200k context budget (mem:85390). Ceremony skills are markdown; the agent is the runtime (mem:84857).

This work item migrates mechanical (judgment-free) ceremony phases from Tier 3 (SKILL.md, agent reads) to Tier 1/2 (hooks/modules, auto-execute). Phases requiring judgment remain as skills.

**Depends on WORK-101 (Proportional Governance Design)** which defines the criteria for which phases are mechanical vs judgment-requiring.

**Prototype exists:** Retro-cycle Phase 0 (mem:85607, 85363) uses computable predicates to skip retro for trivial items. This pattern extends to other ceremonies.

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning)

     These checkboxes are the SOURCE OF TRUTH for work completion.

     During CHECK phase of implementation-cycle:
     - Agent MUST read this section
     - Agent MUST verify EACH checkbox can be marked complete
     - If ANY deliverable is incomplete, work is NOT done

     "Tests pass" ≠ "Deliverables complete"
     Tests verify code works. Deliverables verify scope is complete.

     NOTE (WORK-001): Acceptance criteria are in frontmatter (machine-parseable).
     Deliverables are implementation outputs, not requirements.
-->

- [ ] Identify all mechanical ceremony phases (audit of SKILL.md files)
- [ ] Migrate session-end ceremony to PostToolUse/Stop hook
- [ ] Automate checkpoint standard field population
- [ ] Automate cycle_phase advancement via hook
- [ ] Tests for each migrated phase
- [ ] Documentation of which phases remain as skills and why

---

## History

### 2026-02-17 - Created (Session 394)
- Spawned during E2.8 arc decomposition
- CH-059 CeremonyAutomation, depends on CH-058 design

---

## References

- @.claude/haios/epochs/E2_8/arcs/call/ARC.md
- @docs/work/active/WORK-101/WORK.md (prerequisite design)
- @.claude/skills/retro-cycle/SKILL.md (Phase 0 prototype)
- Memory: 85390 (104% problem), 84857 (ceremony=markdown), 85607 (retro Phase 0)
