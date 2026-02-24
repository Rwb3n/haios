---
template: work_item
id: WORK-216
title: Hook Output Trimming for Noise Reduction
type: implementation
status: complete
owner: Hephaestus
created: 2026-02-24
spawned_by: WORK-212
spawned_children: []
chapter: CH-059
arc: call
closed: 2026-02-24
priority: high
effort: small
traces_to:
- REQ-OBSERVE-002
requirement_refs: []
source_files:
- .claude/hooks/hooks/user_prompt_submit.py
acceptance_criteria:
- Phase contract not re-injected on every UserPromptSubmit when phase unchanged since
  last injection
- Phase contract injection fires only on phase transition or first prompt of session
- Existing hook output for date/session/context/warnings unchanged
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: CHAIN
node_history:
- node: backlog
  entered: 2026-02-24 14:43:49
  exited: 2026-02-24 15:55:00
- node: PLAN
  entered: 2026-02-24 15:55:00
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 88284
- 88337
- 88338
- 88339
- 88340
- 88337
- 88338
- 88339
- 88340
- 88350
- 88351
- 88352
- 88353
- 88354
- 88355
- 88356
- 88357
- 88358
- 88359
- 88360
- 88361
- 88362
extensions: {}
version: '2.0'
generated: 2026-02-24
last_updated: '2026-02-24T16:19:09.597425'
queue_history: []
---
# WORK-216: Hook Output Trimming for Noise Reduction

---

## Context

**Spawned from:** WORK-212 (Mechanical Phase Delegation to Haiku Subagents)

**Problem:** The UserPromptSubmit hook re-injects the entire phase contract file (~100+ lines) on every single user prompt via `_get_phase_contract()`. During a multi-turn implementation phase, the same PLAN.md or DO.md content is injected dozens of times, consuming tokens without adding value after the first injection. The phase contract only changes on phase transitions, not between prompts.

**Root cause:** `_get_phase_contract()` in `user_prompt_submit.py` unconditionally reads and injects the phase file whenever an active cycle with a current phase exists. There is no caching or deduplication — no check for whether the phase has changed since the last injection.

**Solution:** Track last-injected phase using a composite cache key `{session_id}/{active_cycle}/{current_phase}` in a lightweight state file. Only inject the phase contract when the cache key differs from the stored value. Session boundary is handled automatically — a new session_id invalidates the cache without needing a SessionStart hook. This preserves ADR-048's compaction recovery intent: after context compaction, the UserPromptSubmit hook's slim status is re-read and if the phase file content has changed (or session changed), re-injection fires. The key insight is that within a single phase of a single session, the contract content is static — re-injecting the same 100+ lines on every prompt adds no value.

**ADR-048 engagement:** ADR-048 "belt-and-suspenders" justifies every-prompt injection for compaction recovery. This change preserves that property for cross-phase and cross-session transitions. Within a single phase, suppression is safe because the contract content is identical. If compaction occurs mid-phase, the agent retains the contract from its initial injection (compaction preserves recent context). The change reduces token cost from O(prompts_per_phase * phase_file_size) to O(1 * phase_file_size) per phase.

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

- [x] `_get_phase_contract()` tracks last-injected phase and skips re-injection when unchanged
- [x] Phase contract injected on first prompt of session and on phase transitions only
- [x] Unit tests covering: first injection fires, repeat injection skipped, phase change re-fires
- [x] Existing hook output (date, session, context, warnings) unchanged

---

## History

### 2026-02-24 - Created (Session 442)
- Initial creation

---

## References

- @docs/work/active/WORK-212/WORK.md (parent — mechanical phase delegation)
- @.claude/hooks/hooks/user_prompt_submit.py (primary implementation target)
- @.claude/haios/epochs/E2_8/arcs/call/chapters/CH-059-CeremonyAutomation/CHAPTER.md (chapter)
- REQ-OBSERVE-002: Session state visible via hooks
