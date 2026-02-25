# generated: 2026-02-19
# System Auto: last updated on: 2026-02-19T08:30:00
# Chapter: ColdstartContextInjection

## Chapter Definition

**Chapter ID:** CH-061
**Arc:** call
**Epoch:** E2.8
**Name:** Coldstart Context Injection
**Status:** In Progress

---

## Purpose

Make coldstart inject ALL operational context so the agent needs zero Read instructions after `/coldstart`. The orchestrator output IS the agent's operating knowledge — standing orders (hooks) are already active, the briefing provides everything else.

**Core insight:** S393/S394 evidence showed a 200k agent failed to operate because coldstart injected WHO and WHAT but not HOW. Agent wrote raw Python imports (4 failures) instead of using `just ready`. Coldstart "succeeded" but produced a non-operational agent (mem:85915-85922, 85923-85924).

**Principle:** Coldstart produces an operational agent, not an informed one.

---

## Work Items

| ID | Title | Status | Type |
|----|-------|--------|------|
| WORK-162 | Coldstart Context Injection (Design) | Complete | design |
| WORK-180 | Implement ADR-047 Tiered Coldstart | Backlog | implementation |
| WORK-231 | Coldstart Token Waste: Remove Agent-Read of config.yaml | Complete | implementation |
| WORK-232 | Inject Memory Schema Hints into Coldstart Orchestrator Output | Complete | implementation |

---

## Exit Criteria

- [ ] Coldstart injects ALL operational context (zero manual Read steps in coldstart skill)
- [ ] Minimum viable context contract enforced: identity + mission + prior + work + operational HOW
- [ ] Agent can execute work immediately after coldstart without reading additional files

---

## Dependencies

| Direction | Target | Reason |
|-----------|--------|--------|
| None | - | No inbound dependencies |
| Blocks | CH-066 (MCPOperationsServer) | MCP server depends on coldstart context being comprehensive |

---

## References

- @.claude/haios/epochs/E2_8/arcs/call/ARC.md (parent arc)
- @.claude/haios/epochs/E2_8/EPOCH.md (parent epoch)
- Memory: 85915-85922 (200k agent bypass observation), 85923-85924 (minimum viable context)
