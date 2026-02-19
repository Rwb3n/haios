---
template: work_item
id: WORK-169
title: "Critique-as-Hook"
type: implementation
status: active
owner: Hephaestus
created: 2026-02-19
spawned_by: WORK-160
spawned_children: []
chapter: CH-059
arc: call
closed: null
priority: medium
effort: medium
traces_to:
  - REQ-CEREMONY-005
  - REQ-LIFECYCLE-005
requirement_refs: []
source_files:
  - .claude/hooks/hooks/pre_tool_use.py
  - .claude/haios/lib/session_end_actions.py
  - .claude/haios/config/activity_matrix.yaml
acceptance_criteria:
  - "PreToolUse detects inhale-to-exhale skill transitions (PLAN->DO, EXPLORE->HYPOTHESIZE)"
  - "Tier-appropriate critique level injected: none (trivial), checklist (small), full subagent (standard), operator dialogue (architectural)"
  - "Checklist content is actionable (not boilerplate)"
  - "Governance event logged with tier and transition type"
  - "Zero regression: existing PreToolUse checks still fire first"
  - "Tests cover all 4 tiers and at least 2 transition types"
blocked_by: []
blocks: []
enables: []
queue_position: backlog
cycle_phase: backlog
current_node: backlog
node_history:
  - node: backlog
    entered: 2026-02-19T00:17:34
    exited: null
artifacts: []
cycle_docs: {}
memory_refs:
  - 85390
  - 85607
extensions:
  epoch: E2.8
  parent: WORK-160
version: "2.0"
generated: 2026-02-19
last_updated: 2026-02-19T00:20:00
---
# WORK-169: Critique-as-Hook

---

## Context

E2.8 EPOCH.md principle: "Critique is the inhale-to-exhale transition gate." Every transition from exploring/planning to committing/executing should have assumption surfacing. Currently, critique is invoked manually by the agent reading implementation-cycle SKILL.md instructions and calling `Task(subagent_type='critique-agent')`. This costs significant agent tokens and is easily skipped.

This work item implements critique injection as a PreToolUse hook. When the agent invokes a skill that would transition from an "inhale" phase (EXPLORE, PLAN) to an "exhale" phase (DO, HYPOTHESIZE), the hook detects the transition, reads the governance tier from `detect_tier()` (WORK-167), and injects tier-appropriate critique guidance via `additionalContext`.

**Four critique levels (REQ-CEREMONY-005):**
- **None (Trivial):** No injection. Allow silently.
- **Checklist (Small):** Inject checklist of items to verify before proceeding.
- **Full (Standard):** Inject instruction to invoke critique-agent subagent.
- **Operator (Architectural):** Inject instruction for critique-agent + operator confirmation.

**Pattern:** Uses existing `_allow_with_context()` from pre_tool_use.py. Not a block — guidance injection.

---

## Deliverables

- [ ] New file `lib/critique_injector.py` with `compute_critique_injection()` function
- [ ] PreToolUse hook handler for inhale-to-exhale transition detection
- [ ] Tier-based critique level injection via additionalContext
- [ ] Governance event logged (CritiqueInjected)
- [ ] Tests in `tests/test_critique_injector.py`

---

## History

### 2026-02-19 - Created (Session 399)
- Spawned from WORK-160 decomposition
- Depends on WORK-167 (Tier Detection)

---

## References

- @docs/work/active/WORK-160/WORK.md (parent)
- @docs/work/active/WORK-167/WORK.md (dependency — tier detection)
- @.claude/hooks/hooks/pre_tool_use.py (target for transition detection)
- @.claude/haios/epochs/E2_8/EPOCH.md (critique principle)
- Memory: 85390 (104% problem), 85607 (retro Phase 0 prototype)
