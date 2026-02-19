# generated: 2026-02-19
# System Auto: last updated on: 2026-02-19T08:30:00
# Chapter: InfrastructureCeremonies

## Chapter Definition

**Chapter ID:** CH-064
**Arc:** discover
**Epoch:** E2.8
**Name:** Infrastructure Ceremonies
**Status:** Planning

---

## Purpose

Make ceremonies discoverable and executable via infrastructure rather than agent-read SKILL.md. Ceremonies become infrastructure — hooks/modules that execute automatically — rather than markdown instructions that consume agent context.

**Core insight:** Ceremony skills are markdown — the agent is the runtime (mem:84857). Moving ceremonies to infrastructure means they execute at the hook/module layer where judgment isn't needed, freeing agent tokens for decisions.

---

## Work Items

| ID | Title | Status | Type |
|----|-------|--------|------|
| WORK-165 | Infrastructure Ceremonies | Backlog | design |

---

## Exit Criteria

- [ ] Ceremonies executable via infrastructure (hooks/modules), not just SKILL.md
- [ ] Open-epoch-ceremony exists as full ceremony loop (already done S393)
- [ ] Ceremony discovery via typed infrastructure queries

---

## Dependencies

| Direction | Target | Reason |
|-----------|--------|--------|
| None | - | No inbound or outbound dependencies |

---

## References

- @.claude/haios/epochs/E2_8/arcs/discover/ARC.md (parent arc)
- @.claude/haios/epochs/E2_8/EPOCH.md (parent epoch)
- Memory: 84857 (ceremony=markdown), 85098/85108 (WORK-143 triage consumer)
