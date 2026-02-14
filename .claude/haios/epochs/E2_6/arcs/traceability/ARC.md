# generated: 2026-02-14
# System Auto: last updated on: 2026-02-14T12:50:00
# Arc: Traceability

## Definition

**Arc ID:** traceability
**Epoch:** E2.6
**Theme:** Bidirectional tracing from L4 requirements to artifacts, with governance violation logging
**Status:** Planning

---

## Purpose

The traceability chain (L4 -> Epoch -> Arc -> Chapter -> Work Item -> Artifact) exists in principle but is not verifiable. Plan decomposition loses provenance. Governance gate violations are invisible. This arc closes those gaps.

---

## Requirements Implemented

| Requirement | Description |
|-------------|-------------|
| REQ-ASSET-003 | Assets can be piped to next lifecycle OR stored |
| REQ-LIFECYCLE-001 | Lifecycles are pure functions, independently completable |
| REQ-TRACE-005 | Full traceability chain L4 -> Epoch -> Arc -> Chapter -> Work |
| REQ-OBSERVE-005 | MUST gate violations logged to governance events |

---

## Chapters

| CH-ID | Title | Work Items | Requirements | Dependencies |
|-------|-------|------------|--------------|--------------|
| CH-038 | DecompositionAndMappings | WORK-097, WORK-104 | REQ-ASSET-003, REQ-LIFECYCLE-001 | None |
| CH-039 | L4CoverageAudit | WORK-075 | REQ-TRACE-005 | None (blockers WORK-069/070 resolved) |
| CH-040 | GateSkipLogging | WORK-146 | REQ-OBSERVE-005 | None |

---

## Exit Criteria

- [ ] Plan decomposition pattern documented with WORK.md/plan.md fields
- [ ] Activity matrix has validation-cycle and triage-cycle phase mappings
- [ ] L4 requirements bidirectionally traceable to work items and artifacts
- [ ] MUST gate violations logged to governance-events.jsonl
- [ ] Gap analysis produced (unimplemented requirements/decisions)

---

## Notes

- CH-038 merges WORK-097 (decomposition pattern, medium) with WORK-104 (activity matrix mappings, small) — both traceability pattern work
- WORK-075 was previously blocked by WORK-069/070; both now complete (verified S366)

---

## References

- @docs/work/active/WORK-075/WORK.md
- @docs/work/active/WORK-097/WORK.md
- @docs/work/active/WORK-104/WORK.md
- @docs/work/active/WORK-146/WORK.md
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-TRACE-*, REQ-OBSERVE-005)
