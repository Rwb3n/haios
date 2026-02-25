---
template: work_item
id: WORK-234
title: Constrain EXTRACT Phase Haiku Prompt to Eliminate File Reads
type: implementation
status: complete
owner: Hephaestus
created: '2026-02-25'
closed: '2026-02-25'
priority: medium
effort: small
chapter: CH-059
arc: call
traces_to:
- REQ-CEREMONY-002
spawned_by: WORK-235
spawned_children: []
blocked_by: []
blocks: []
enables: []
queue_position: done
cycle_phase: done
current_node: DONE
node_history:
- node: backlog
  entered: '2026-02-25T22:09:00.679441'
  exited: '2026-02-25T22:41:01.688767'
queue_history:
- position: backlog
  entered: '2026-02-25T22:09:00.679441'
  exited: '2026-02-25T22:37:54.037527'
- position: ready
  entered: '2026-02-25T22:37:54.037527'
  exited: '2026-02-25T22:40:14.712041'
- position: working
  entered: '2026-02-25T22:40:14.712041'
  exited: '2026-02-25T22:41:01.688767'
- position: done
  entered: '2026-02-25T22:41:01.688767'
  exited: null
memory_refs: []
requirement_refs: []
source_files:
- .claude/skills/retro-cycle/SKILL.md
acceptance_criteria:
- EXTRACT phase delegation prompt explicitly prohibits file reads (Read tool)
- Prompt states all evidence is provided in reflect_findings_text — no independent
  verification
- EXTRACT haiku subagent produces correct output without file reads (manual verification)
artifacts: []
extensions: {}
version: '2.0'
generated: '2026-02-25'
last_updated: '2026-02-25T22:41:01.693800'
---
# WORK-234: Constrain EXTRACT Phase Haiku Prompt to Eliminate File Reads

---

## Context

S458 observed the EXTRACT phase haiku subagent consuming ~40k tokens, mostly on file reads. The EXTRACT delegation prompt provides `reflect_findings_text` inline but doesn't prohibit file reads. The haiku subagent independently reads WORK.md, PLAN.md, etc. to "verify" observations — redundant work since all evidence is already in the prompt.

Fix: Add explicit constraints to the EXTRACT delegation prompt in `retro-cycle/SKILL.md`:
1. "Do NOT use the Read tool — all evidence is provided in reflect_findings_text"
2. "Classify from provided observations only, do not independently verify"
3. Keep output format requirements unchanged

This is a text-only change to a skill file — no Python code, no tests needed (manual verification via next retro run).

---

## Deliverables

- [ ] EXTRACT phase prompt includes explicit file-read prohibition
- [ ] Prompt states all evidence is in reflect_findings_text

---

## References

- @.claude/skills/retro-cycle/SKILL.md (target file, Phase 4: EXTRACT)
- @docs/work/active/WORK-235/WORK.md (parent investigation)
