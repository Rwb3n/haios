---
template: observations
work_id: INV-019
captured_session: '241'
generated: '2026-01-25'
last_updated: '2026-01-25T22:15:39'
---
# Observations: INV-019

## What surprised you?

<!--
- Unexpected behaviors, bugs encountered
- Things easier or harder than anticipated
- Assumptions that proved wrong
- Principles revealed through the work
- Operator insights that shifted understanding
-->

The investigation was narrower than expected because requirements already exist in multiple mature formats. L4/functional_requirements.md already has 13 formal requirements with the REQ-{DOMAIN}-{NNN} pattern and bidirectional traceability (derives_from L3, implemented_by components). S26 Pipeline Architecture already defines a RequirementSet schema at `.claude/haios/epochs/E2/architecture/S26-pipeline-architecture.md:52-63`. The surprise: we don't need to invent a requirements framework - we need to unify and extract from existing patterns.

Also surprising: the ID collision issue. An old investigation file (Session 88, `docs/investigations/INVESTIGATION-INV-019-synthesis-coverage-gap-query-ordering-bug.md`) incorrectly claimed INV-019, which blocked creating the proper investigation document. This revealed that early sessions created investigations without checking for ID collisions - the work item structure has evolved but legacy files weren't migrated. Fixed by setting `backlog_id: null` on the orphan file.

## What's missing?

<!--
- Gaps in tooling, docs, or infrastructure
- Features that would have helped
- AgentUX friction points
- Schema or architectural concepts not yet codified
- Patterns that should exist but don't
-->

**No "Requirement" concept type in memory.** The memory system has Decision, Directive, Proposal, and Critique types, but extracted requirements would benefit from their own dedicated type for targeted retrieval. Currently requirements are scattered across Decision/Directive types, making it harder to query "what are all the requirements for X?"

**No unified extraction tool.** Requirements are manually enumerated in L4/functional_requirements.md, not auto-extracted from TRDs/ADRs. The Pipeline arc CH-002 (RequirementExtractor) would fill this gap, but it's not yet implemented. This investigation provides the design for that implementation.

**Format inconsistency across document types.** TRDs use R0-R8 tables with ID/Description/Strength columns. Manifesto uses REQ-{DOMAIN}-{NNN} with derives_from traceability. Natural language docs (agent_user_requirements.md) use "must allow" statements. A multi-parser architecture is needed to handle all formats.

## What should we remember?

<!--
- Learnings for future work
- Patterns worth reusing or naming
- Warnings for similar tasks
- Decisions that should become ADRs
- Principles worth adding to L3/L4
-->

**Extend, don't reinvent.** S26 already defines a RequirementSet schema. L4/functional_requirements.md demonstrates a working pattern with bidirectional traceability. For CH-002 implementation, the task is synthesis and extraction from these existing patterns, not schema design from scratch.

**Traceability model is critical for pipeline validation:** L3 Principles → L4 Requirements → Work Items → Artifacts → Memory. This chain enables the ValidatorAgent (CH-005) to check outputs against source requirements. The `derives_from` and `implemented_by` fields in L4 already implement this pattern.

**Terminal status filtering must be consistent.** When `plan_tree.py` filtered by `status == "complete"` while WorkEngine filtered by the full terminal set (complete, archived, dismissed, invalid, deferred), `just ready` showed 56 items while `just queue` showed 11. Fixed by adding the terminal_statuses set to plan_tree.py. Future: any component checking "is this item active?" should use the same status set.

## What drift did you notice?

<!--
- Reality vs documented behavior
- Code vs spec misalignment
- Principles violated or bent
- Patterns that have evolved past their docs
-->

**plan_tree.py vs WorkEngine terminal status filtering.** The script at `scripts/plan_tree.py:99-101` only filtered `status == "complete"`, not the full terminal set that WorkEngine uses (complete, archived, dismissed, invalid, deferred). This caused `just ready` to show 56 items while `just queue` showed 11. Fixed this session by adding the terminal_statuses set to plan_tree.py:97-98. Also added deprecation notice since plan_tree.py duplicates WorkEngine logic.

**docs/investigations/ contains orphan files.** The old `INVESTIGATION-INV-019-synthesis-coverage-gap-query-ordering-bug.md` file (Session 88) had `backlog_id: INV-019` but that work item has a completely different title and purpose (Requirements Synthesis). This suggests early investigation files were created without checking for ID collisions. The PreToolUse hook now catches duplicates, but legacy files predate this check. Consider an audit of docs/investigations/ for orphan or mislinked backlog_ids.
