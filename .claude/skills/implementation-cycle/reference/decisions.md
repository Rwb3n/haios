---
type: reference
skill: implementation-cycle
---
# Implementation Cycle — Key Design Decisions

## Related

- **ADR-033:** Work Item Lifecycle (DoD criteria)
- **ADR-038:** M2-Governance Symphony Architecture
- **ADR-048:** Progressive Contracts — Phase-Per-File Skill Fracturing (this fracture)
- **E2-108:** Gate Observability (governance event logging)
- **/implement command:** E2-092 will invoke this skill
- **Preflight Checker:** E2-093 will enforce DO phase guardrails
- **Test Runner:** E2-094 for isolated test execution
- **WHY Capturer:** E2-095 for automated learning capture
- **FORESIGHT Prep:** E2-106 adds optional prediction/calibration fields (Epoch 3 bridge)
- **Epoch 3 Spec:** `epoch3/foresight-spec.md` - SIMULATE, INTROSPECT, ANTICIPATE, UPDATE operations

## Fracturing Decision (ADR-048)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Fracture approach | Phase-per-file (Option A) | Dual hook injection means zero agent cognitive overhead; each file independently maintainable |
| Self-containment rule | No cross-phase references allowed | Agent loads only current phase — cross-refs require loading another file, defeating the purpose |
| Content duplication | Acceptable | Duplication is preferable to requiring multi-file reads (CHAIN routing logic may appear in multiple phases) |
| Slim router size | ~80 lines | Enough for cycle diagram + phase table; delegates behavioral contracts to phase files |
| Unwired templates | Not deleted | `.claude/templates/implementation/` are artifact templates, not orchestration contracts (separate concern) |
