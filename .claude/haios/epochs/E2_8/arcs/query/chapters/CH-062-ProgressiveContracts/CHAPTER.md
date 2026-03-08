---
id: CH-062
name: Progressive Contracts
arc: query
epoch: E2.8
status: Complete
work_items:
- id: WORK-163
  title: Progressive Contracts
  status: Done
  type: design
- id: WORK-187
  title: Fracture Implementation-Cycle SKILL.md into Phase Files
  status: Done
  type: implementation
- id: WORK-188
  title: Hook Auto-Injection for Phase Contracts
  status: Done
  type: implementation
exit_criteria:
- text: Contracts designed for progressive disclosure (agent reads what it needs,
    not everything)
  checked: true
  evidence: ADR-048, WORK-187 (phase-per-file fracturing), WORK-188 (hook auto-injection). 468-line monolithic SKILL.md -> 80-line router + 5 phase files. PostToolUse injects current phase contract.
- text: Context loading uses engine functions and memory before file reads
  checked: true
  evidence: ColdstartOrchestrator uses engine functions (HierarchyQueryEngine, ConfigLoader). Memory refs queried via memory_search_with_experience. Phase contracts auto-injected by hooks.
- text: Lightweight coldstart variant exists for housekeeping sessions
  checked: true
  evidence: ADR-047, WORK-180 S421. Three tiers - full/light/minimal. Shared with CH-061.
dependencies: []
---
# generated: 2026-02-19
# System Auto: last updated on: 2026-02-19T08:30:00
# Chapter: ProgressiveContracts

## Chapter Definition

**Chapter ID:** CH-062
**Arc:** query
**Epoch:** E2.8
**Name:** Progressive Contracts
**Status:** Planning

---

## Purpose

Design contracts for progressive disclosure — agents read what they need, not everything. Load summary first, details on demand. Engine functions (HierarchyQueryEngine, ConfigLoader) provide the query layer; this chapter extends them for context loading.

**Core insight:** Most tokens are spent on context loading (mem:85459). Contracts that expose summary-first with drill-down capability reduce token spend while maintaining full information availability.

---

## Work Items

| ID | Title | Status | Type |
|----|-------|--------|------|
| WORK-163 | Progressive Contracts | Done | design |
| WORK-187 | Fracture Implementation-Cycle SKILL.md into Phase Files | Active | implementation |
| WORK-188 | Hook Auto-Injection for Phase Contracts | Active | implementation |

---

## Exit Criteria

- [ ] Contracts designed for progressive disclosure (agent reads what it needs, not everything)
- [ ] Context loading uses engine functions and memory before file reads
- [ ] Lightweight coldstart variant exists for housekeeping sessions

---

## Dependencies

| Direction | Target | Reason |
|-----------|--------|--------|
| None | - | No inbound or outbound dependencies |

---

## References

- @.claude/haios/epochs/E2_8/arcs/query/ARC.md (parent arc)
- @.claude/haios/epochs/E2_8/EPOCH.md (parent epoch)
- Memory: 84835, 84836 (coldstart overhead), 85459 (most tokens on context loading), 85815 (context switching)
