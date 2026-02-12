---
template: work_item
id: WORK-134
title: Investigate coldstart prior_session showing 999
type: investigation
status: complete
owner: Hephaestus
created: 2026-02-12
spawned_by: null
chapter: null
arc: null
closed: 2026-02-12
priority: low
effort: small
traces_to:
- REQ-SESSION-001
requirement_refs: []
source_files: []
acceptance_criteria: []
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: done
node_history:
- node: backlog
  entered: 2026-02-12 19:27:40
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 84997
- 84998
- 84999
- 85000
- 85001
extensions: {}
version: '2.0'
generated: 2026-02-12
last_updated: '2026-02-12T19:31:35.442967'
queue_history: []
---
# WORK-134: Investigate coldstart prior_session showing 999

---

## Context

The coldstart orchestrator's SESSION CONTEXT phase shows `Prior Session: 999` instead of the actual prior session number (should be 353). This was noted in S339 tiny fixes list ("Checkpoint prior_session stale value — Bug fix in scaffold.py") and again in S353 checkpoint pending. The bug affects session continuity tracking — operators see incorrect context about which session preceded the current one.

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

- [x] Root cause identified (where 999 value originates)
- [x] Fix implemented (prior_session shows actual session number)
- [x] Verified via coldstart orchestrator output

---

## History

### 2026-02-12 - Created and Completed (Session 354)
- Root cause: Test checkpoint files (SESSION-999, SESSION-998) in `docs/checkpoints/` from S288 (WORK-079)
- `SessionLoader._find_latest_checkpoint()` picks max SESSION-NNN from filenames → picks 999 over 353
- Fix: `git rm` both test checkpoint files
- Verified: SessionLoader now returns `prior_session: 353`
- EPOCH.md S339 tiny fixes listed this as "Bug fix in scaffold.py" — corrected to actual fix

---

## References

- `session_loader.py:96-113` — `_find_latest_checkpoint()` (affected code)
- EPOCH.md S339 tiny fixes table (updated)
- S288/WORK-079 (origin of test files)
