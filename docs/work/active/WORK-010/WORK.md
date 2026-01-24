---
template: work_item
id: WORK-010
title: Work Loader for Coldstart Phase 3
type: feature
status: active
owner: Hephaestus
created: 2026-01-24
spawned_by: null
chapter: CH-006
arc: configuration
closed: null
priority: medium
effort: medium
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-24 19:26:25
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82322
- 82323
- 82324
- 82327
extensions: {}
version: '2.0'
generated: 2026-01-24
last_updated: '2026-01-24T19:29:01'
---
# WORK-010: Work Loader for Coldstart Phase 3

@docs/README.md
@docs/epistemic_state.md

---

## Context

Survey-cycle skill currently performs work extraction inline: runs `just queue`, parses output, checks checkpoint pending, presents options. This is a skill doing what a loader should do.

**Problem:** Agent makes multiple calls to gather work options. No epoch alignment check. Pending items from checkpoint scattered across coldstart steps.

**Root Cause:** Work context extraction not unified into a loader like identity (WORK-007) and session (CH-005).

**Need:** Single invocation that returns formatted work options with epoch alignment warning and pending items included.

**Pattern:** Follow IdentityLoader/SessionLoader pattern:
- `config/loaders/work.yaml` - extraction rules
- `.claude/haios/lib/work_loader.py` - WorkLoader class
- `just work-options` - CLI entry point
- Register in ContextLoader for Phase 3

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

- [ ] `config/loaders/work.yaml` - Work extraction config (queue source, pending source, epoch alignment check)
- [ ] `.claude/haios/lib/work_loader.py` - WorkLoader class following SessionLoader pattern
- [ ] Tests for WorkLoader in `tests/test_work_loader.py`
- [ ] Register WorkLoader in ContextLoader._register_default_loaders()
- [ ] `just work-options` recipe in justfile
- [ ] Epoch alignment warning when queue items from prior epochs
- [ ] Formatted output with top 5 queue items + pending from checkpoint

---

## History

### 2026-01-24 - Created (Session 231)
- Initial creation

---

## References

- @.claude/haios/epochs/E2_3/arcs/configuration/CH-006-work-loader.md (chapter spec)
- @.claude/haios/lib/session_loader.py (pattern to follow)
- @.claude/haios/config/loaders/session.yaml (config pattern)
- WORK-005: Loader Base (dependency)
- WORK-007: Identity Loader (pattern)
- CH-005: Session Loader (prior deliverable)
