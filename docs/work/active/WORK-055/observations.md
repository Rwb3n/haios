---
template: observations
work_id: WORK-055
captured_session: '279'
generated: '2026-02-01'
last_updated: '2026-02-01T23:08:13'
---
# Observations: WORK-055

## What surprised you?

**The decomposition leakage pattern is self-referential.** This investigation (WORK-055) itself demonstrates the problem it documents: WORK-055 has no `chapter:` or `arc:` assignment in its frontmatter - it's an orphan investigation spawned from an observation. The very gap we identified (epoch decisions without chapter assignment) applies to the investigation that found the gap. This validates that the pattern is pervasive and not hypothetical.

**Memory already knew this.** Memory ID 82455 explicitly stated "The requirements traceability loop from L4 -> Epoch -> Arc -> Chapter -> Work -> Close -> Memory is incomplete." This was stored in a prior session but never acted upon. The investigation pattern of "query memory first" (EXPLORE phase) surfaced this - validating that memory queries at investigation start catch prior unactioned findings.

## What's missing?

**No schema enforcement for decision-to-chapter links.** EPOCH.md decisions are free-form prose with no structured `assigned_to` field. The template allows orphan decisions by default. A schema change plus validation would prevent this.

**No arc-level DoD.** ADR-033 defines work item DoD but there's no ceremony for "is this arc complete?" The close-work-cycle operates at work item granularity. A close-arc or close-epoch ceremony doesn't exist.

**No pre-decomposition critique pattern.** The critique-agent operates at plan level. There's no "arc decomposition critique" that verifies chapter tables cover all epoch decisions before chapter work begins.

## What should we remember?

**Pattern: Governance gaps exist at branch nodes, not just leaves.** We govern work items well but chapters/arcs/epochs have implicit-only governance. This is a systemic blind spot - when adding governance, check ALL hierarchy levels.

**Pattern: Self-referential validation.** When investigating a gap, check if the investigation itself exhibits the gap. WORK-055 having no chapter assignment proved the pattern is real.

**Decision: Multi-level DoD cascade is needed.** Work Item DoD -> Chapter DoD -> Arc DoD -> Epoch DoD. Each level verifies the level below is complete AND level-specific objectives are met.

## What drift did you notice?

**REQ-TRACE-005 claims full traceability but doesn't deliver it.** The requirement states "Full traceability chain MUST exist: L4 Requirement -> Epoch -> Arc -> Chapter -> Work Item" but this traces containment, not decision coverage. The requirement is misleading - it should be split into REQ-TRACE-005 (structural hierarchy) and REQ-TRACE-006 (decision coverage).

**Investigation spawned from observation but observation triage didn't create chapter assignment.** The obs-268-1.md was triaged and promoted to WORK-055, but the observation-triage-cycle doesn't enforce chapter assignment for spawned work. This is drift from REQ-TRACE-004 intent.
