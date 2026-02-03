# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:00:49
# Arc: Lifecycles

## Definition

**Arc ID:** lifecycles
**Epoch:** E2.5
**Theme:** Implement CycleRunner with pure function semantics
**Status:** Planned

---

## Purpose

Transform CycleRunner from implicit-chaining to pure-function semantics per REQ-LIFECYCLE-001 to 004.

---

## Requirements Implemented

| Requirement | Description |
|-------------|-------------|
| REQ-LIFECYCLE-001 | Lifecycles are pure functions, independently completable |
| REQ-LIFECYCLE-002 | Pause points are valid completion states (S27) |
| REQ-LIFECYCLE-003 | Batch mode: multiple items in same phase |
| REQ-LIFECYCLE-004 | Chaining is caller choice, not callee side-effect |

---

## Chapters

| CH-ID | Title | Requirements | Dependencies |
|-------|-------|--------------|--------------|
| CH-001 | LifecycleSignature | REQ-LIFECYCLE-001 | None |
| CH-002 | PauseSemantics | REQ-LIFECYCLE-002 | CH-001 |
| CH-003 | BatchMode | REQ-LIFECYCLE-003 | CH-001 |
| CH-004 | CallerChaining | REQ-LIFECYCLE-004 | CH-001, CH-002 |
| CH-005 | PhaseTemplateContracts | REQ-TEMPLATE-001 | CH-001 |
| CH-006 | TemplateFracturing | REQ-TEMPLATE-002 | CH-005 |

---

## Exit Criteria

- [ ] CycleRunner.run() returns output, does not auto-chain
- [ ] "Complete without spawn" accepted by close-work-cycle
- [ ] Pause points (per S27) recognized as valid completion
- [ ] Batch mode tested (3+ items in same phase)
