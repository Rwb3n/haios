---
template: work_item
id: WORK-200
title: Implement Proportional Close Ceremony
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-23
spawned_by: WORK-199
spawned_children: []
chapter: CH-059
arc: call
closed: '2026-02-23'
priority: medium
effort: medium
traces_to:
- REQ-LIFECYCLE-005
- REQ-CEREMONY-005
requirement_refs: []
source_files:
- .claude/commands/close.md
- .claude/skills/close-work-cycle/SKILL.md
- .claude/skills/dod-validation-cycle/SKILL.md
- .claude/skills/checkpoint-cycle/SKILL.md
acceptance_criteria:
- effort=small items use inline DoD checklist instead of dod-validation-cycle 3-phase
  bridge
- close-work-cycle VALIDATE merged into inline checklist for effort=small
- checkpoint-cycle VERIFY uses inline field check (no subagent) for effort=small
- Full close path preserved unchanged for effort=standard+ items
- Pytest hard gate remains tier-independent (invariant)
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: CHAIN
current_node: CHAIN
node_history:
- node: backlog
  entered: 2026-02-23 11:42:45
  exited: '2026-02-23T12:22:39.787164'
artifacts: []
cycle_docs: {}
memory_refs:
- 87764
extensions: {}
version: '2.0'
generated: 2026-02-23
last_updated: '2026-02-23T12:22:39.789694'
queue_history:
- position: done
  entered: '2026-02-23T12:22:39.787164'
  exited: null
---
# WORK-200: Implement Proportional Close Ceremony

---

## Context

WORK-199 investigation found that the close ceremony pipeline (retro-cycle → dod-validation-cycle → close-work-cycle → checkpoint-cycle) runs 14 discrete steps regardless of work item effort tier. For effort=small items (1-2 files, no plan, no ADR), this consumes ~15,000-25,000 tokens on ceremony vs ~5,000-10,000 on actual work.

REQ-LIFECYCLE-005 defines fast-path: "phases are lightweight, not skipped." REQ-CEREMONY-005 defines 4-tier scaling (None→Checklist→Full→Operator). The close pipeline doesn't implement either yet. retro-cycle Phase 0 is the only existing scaling mechanism.

**Implementation:** Add tier-aware branching to `/close` command and close-work-cycle skill. Tier detection uses prospective predicates from WORK.md frontmatter (`effort:` field + `source_files:` count) per REQ-LIFECYCLE-005, not retrospective git diff. When effort=small AND source_files <= 3:
1. Replace dod-validation-cycle 3-phase bridge with inline DoD checklist
2. Merge close-work-cycle VALIDATE into the inline checklist
3. Replace checkpoint-cycle VERIFY subagent with inline field check
4. Preserve all invariants (pytest gate, ARCHIVE, COMMIT)

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

- [ ] `/close` command detects effort tier and branches to lightweight or full path
- [ ] close-work-cycle SKILL.md updated with lightweight VALIDATE path for effort=small
- [ ] dod-validation-cycle SKILL.md updated with inline checklist alternative
- [ ] checkpoint-cycle SKILL.md updated with lightweight VERIFY for effort=small
- [ ] Content-assertion test verifying lightweight path patterns present in modified files
- [ ] Full close path unchanged for effort=standard+ items

---

## History

### 2026-02-23 - Created (Session 429)
- Spawned from WORK-199 investigation (Proportional Close Ceremony)
- All 4 hypotheses confirmed: 3 independently scalable segments, dod-validation collapsible, checkpoint VERIFY reducible, VALIDATE overlap mergeable

---

## References

- @docs/work/active/WORK-199/WORK.md (investigation source)
- @.claude/skills/close-work-cycle/SKILL.md (primary target)
- @.claude/skills/dod-validation-cycle/SKILL.md (inline replacement)
- @.claude/skills/checkpoint-cycle/SKILL.md (VERIFY reduction)
- @.claude/commands/close.md (entry point)
- @.claude/haios/lib/retro_scale.py (tier detection prototype)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-LIFECYCLE-005, REQ-CEREMONY-005)
