---
template: work_item
id: WORK-153
title: "E2.7 Bug Batch: Ceremony Stubs, Doc Drift, Code Duplication"
type: bugfix
status: active
owner: Hephaestus
created: 2026-02-16
spawned_by: null
spawned_children: []
chapter: null
arc: null
closed: null
priority: low
effort: small
traces_to:
  - REQ-OBSERVE-005
requirement_refs: []
source_files:
  - .claude/skills/spawn-work-ceremony/SKILL.md
  - .claude/skills/close-work-cycle/SKILL.md
  - .claude/haios/lib/observations.py
acceptance_criteria:
  - "spawn-work-ceremony SKILL.md has stub: true in frontmatter"
  - "close.md line 65 no longer references removed MEMORY phases"
  - "observations.py _db_query helper defined once, not duplicated 3x in __main__"
  - "MEMORY.md pre-existing test failure count updated to current actual"
  - "cycle_phase stale 'backlog' bug documented with root cause analysis"
  - "All existing tests still pass"
blocked_by: []
blocks: []
enables: []
queue_position: backlog  # WORK-105: parked|backlog|ready|working|done
cycle_phase: backlog     # WORK-066: backlog|plan|implement|check|done
current_node: backlog    # DEPRECATED: use cycle_phase
node_history:
  - node: backlog
    entered: 2026-02-16T18:45:11
    exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: "2.0"
generated: 2026-02-16
last_updated: 2026-02-16T18:45:11
---
# WORK-153: E2.7 Bug Batch: Ceremony Stubs, Doc Drift, Code Duplication

---

## Context

Six bugs surfaced during S383 observation triage of E2.6 retro-* provenance tags (sessions 365-382). Two medium confidence, four low confidence. Grouped as batch per validated pattern (memory 84963).

**Medium bugs:**
1. spawn-work-ceremony missing `stub: true` in frontmatter (85097) — causes test_stub_has_stub_marker failure
2. cycle_phase stays "backlog" when items skip plan-authoring (84943) — queue position never updated during impl cycle

**Low bugs:**
3. close.md line 65 references "MEMORY phases" after removal from close-work-cycle (85096)
4. CLI `_db_query` helper duplicated 3 times in observations.py `__main__` block (85131)
5. MEMORY.md pre-existing test failure count stale: 18 vs actual 19 (85412)
6. CONCLUDE.md `last_updated` frontmatter stays stale — no hook for template edits (85445) — documented as accepted (85449)

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

- [ ] Fix spawn-work-ceremony stub:true frontmatter
- [ ] Fix close.md stale MEMORY phase reference
- [ ] Deduplicate _db_query helper in observations.py
- [ ] Update MEMORY.md test failure count
- [ ] Document cycle_phase staleness root cause (may need WORK-034 cascade)
- [ ] CONCLUDE.md timestamp: document as accepted gap (no fix needed)

---

## History

### 2026-02-16 - Created (Session 383)
- Spawned from S383 observation triage cycle (PROMOTE phase)
- 6 bugs grouped as batch: 2 medium, 4 low confidence
- Memory evidence: 85097, 85096, 85131, 85412, 85445, 84943

---

## References

- Memory: 85097, 85096, 85131, 85412, 85445, 84943 (bug evidence)
- Memory: 84963 (batch bug pattern validation)
- WORK-034 (status propagation — may resolve cycle_phase staleness)
