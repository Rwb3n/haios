---
template: observations
work_id: WORK-070
captured_session: '285'
generated: '2026-02-02'
last_updated: '2026-02-02T11:59:53'
---
# Observations: WORK-070

## What surprised you?

**ARC.md already had CH-010 listed.** The plan's Step 4 said "Add CH-010 to Chapters table" but the critique agent discovered it was already present at line 66 of `.claude/haios/epochs/E2_4/arcs/flow/ARC.md`. This was added during Session 284's decomposition work. The lesson: plans authored in prior sessions may have partial implementation already done - always verify state before editing. The critique-agent's A3 finding caught this accurately.

**PostToolUse hook auto-linked memory_refs.** After calling `ingester_ingest` with concepts 83137-83139, the new IDs automatically appeared in WORK-070's frontmatter without manual editing. This confirms the memory auto-link infrastructure (PostToolUse hook) is working correctly for work items.

## What's missing?

**Audit-decision-coverage partial assignment reporting.** D8 is assigned to three chapters (CH-009, CH-010, CH-011) but CH-011 doesn't exist yet (it's for WORK-071). The `just audit-decision-coverage` script reports D8 as "orphan" without distinguishing between "fully orphan" (no chapters claim it) and "partially orphan" (some chapters claim it but not all assigned ones exist). A more nuanced status would help: "D8: 2/3 chapters implemented (missing: CH-011)".

**blocked_by field doesn't auto-clear when blocker closes.** WORK-070's frontmatter still shows `blocked_by: [WORK-069]` even though WORK-069 has `status: complete`. The dependency is functionally satisfied but the field persists. This could confuse `just ready` or similar queries. Consider: should close-work-cycle update dependent items' blocked_by fields?

## What should we remember?

**Decomposition pattern works well for scope control.** The >3 file preflight rule (preflight-checker) forced WORK-070 to be split into parent (design artifacts: requirements, chapter file) + children (ceremony skill implementations: WORK-076/077/078). This kept the parent work item verifiable in a single session (~45 minutes) while preserving full traceability to child work items. The pattern: when preflight blocks on file count, spawn child work items rather than forcing all files into one work item.

**Test scope must match decomposition.** The plan's Tests First section (lines 133-190) included tests for ceremony skills that were decomposed to separate work items. During implementation, Test 2 (ceremony skill tests) was correctly skipped per critique finding A6. Lesson: when decomposing work items, the plan's test manifest should be updated to reflect reduced scope, or implementer must recognize which tests belong to decomposed children.

## What drift did you notice?

- [x] None observed - Implementation matched the plan's Detailed Design. Specifications (ADR-033, CH-009 pattern, close-work-cycle pattern) were followed correctly.
