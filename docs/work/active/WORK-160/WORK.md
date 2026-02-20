---
template: work_item
id: WORK-160
title: Ceremony Automation
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-17
spawned_by: Session-394-decomposition
spawned_children:
- WORK-167
- WORK-168
- WORK-169
- WORK-170
- WORK-171
chapter: CH-059
arc: call
closed: '2026-02-20'
priority: high
effort: large
traces_to:
- REQ-CEREMONY-002
- REQ-CEREMONY-005
- REQ-LIFECYCLE-005
requirement_refs: []
source_files:
- .claude/skills/implementation-cycle/SKILL.md
- .claude/skills/close-work-cycle/SKILL.md
- .claude/skills/retro-cycle/SKILL.md
- .claude/hooks/hooks/pre_tool_use.py
acceptance_criteria:
- At least 3 mechanical ceremony phases migrated from SKILL.md to hooks/modules
- Session-end ceremony runs automatically via hook (not agent-read skill)
- Checkpoint population automated for standard fields
- cycle_phase advancement automated via PostToolUse hook
- 'Critique-as-hook: PreToolUse detects inhale-to-exhale skill transitions, injects
  critique automatically'
- 'Four critique levels implemented: none (trivial), checklist (hook), full (subagent),
  operator (dialogue)'
- Computable predicate determines critique level from work item type, plan existence,
  transition type
- Zero regression in existing ceremony behavior
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-17 22:08:08
  exited: '2026-02-20T22:24:17.408417'
artifacts: []
cycle_docs: {}
memory_refs:
- 85390
- 84857
- 85607
extensions:
  epoch: E2.8
  depends_on_design: WORK-101 (complete, S398)
version: '2.0'
generated: 2026-02-17
last_updated: '2026-02-20T22:24:17.411968'
queue_history:
- position: done
  entered: '2026-02-20T22:24:17.408417'
  exited: null
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

- [x] Identify all mechanical ceremony phases (audit of SKILL.md files) — WORK-171
- [x] Migrate session-end ceremony to PostToolUse/Stop hook — WORK-161 (S396)
- [x] Automate checkpoint standard field population — WORK-170
- [x] Automate cycle_phase advancement via hook — WORK-168
- [x] Tests for each migrated phase — all children have tests
- [x] Documentation of which phases remain as skills and why — WORK-171 (SKILL.md references lib/ functions)

---

## History

### 2026-02-19 - Decomposed (Session 399)
- Decomposed into 5 children: WORK-167 (Tier Detection), WORK-168 (Cycle Auto-Advance), WORK-169 (Critique-as-Hook), WORK-170 (Checkpoint Auto), WORK-171 (Phase Migration)
- Acceptance criterion #2 (session-end automation) already satisfied by WORK-161 (S396)
- WORK-160 completes when all 5 children complete + #2 (already done)

### 2026-02-17 - Created (Session 394)
- Spawned during E2.8 arc decomposition
- CH-059 CeremonyAutomation, depends on CH-058 design

---

## References

- @.claude/haios/epochs/E2_8/arcs/call/ARC.md
- @docs/work/active/WORK-101/WORK.md (prerequisite design)
- @.claude/skills/retro-cycle/SKILL.md (Phase 0 prototype)
- Memory: 85390 (104% problem), 84857 (ceremony=markdown), 85607 (retro Phase 0)
