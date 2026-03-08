---
id: CH-061
name: Coldstart Context Injection
arc: call
epoch: E2.8
status: Complete
work_items:
- id: WORK-162
  title: Coldstart Context Injection (Design)
  status: Complete
  type: design
- id: WORK-180
  title: Implement ADR-047 Tiered Coldstart
  status: Complete
  type: implementation
- id: WORK-231
  title: 'Coldstart Token Waste: Remove Agent-Read of config.yaml'
  status: Complete
  type: implementation
- id: WORK-232
  title: Inject Memory Schema Hints into Coldstart Orchestrator Output
  status: Complete
  type: implementation
- id: WORK-251
  title: Coldstart Crash Recovery — Detect Unclosed Sessions
  status: Complete
  type: implementation
exit_criteria:
- text: Coldstart injects ALL operational context (zero manual Read steps in coldstart
    skill)
  checked: true
- text: 'Minimum viable context contract enforced: identity + mission + prior + work
    + operational HOW'
  checked: true
- text: Agent can execute work immediately after coldstart without reading additional
    files
  checked: true
dependencies:
- direction: Blocks
  target: CH-066 (MCPOperationsServer)
  reason: MCP server depends on coldstart context being comprehensive
---
# generated: 2026-02-19
# System Auto: last updated on: 2026-02-19T08:30:00
# Chapter: ColdstartContextInjection

## Chapter Definition

**Chapter ID:** CH-061
**Arc:** call
**Epoch:** E2.8
**Name:** Coldstart Context Injection
**Status:** Complete

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
| WORK-180 | Implement ADR-047 Tiered Coldstart | Complete | implementation |
| WORK-231 | Coldstart Token Waste: Remove Agent-Read of config.yaml | Complete | implementation |
| WORK-232 | Inject Memory Schema Hints into Coldstart Orchestrator Output | Complete | implementation |
| WORK-251 | Coldstart Crash Recovery — Detect Unclosed Sessions | Complete | implementation |

---

## Exit Criteria

- [x] Coldstart injects ALL operational context (zero manual Read steps in coldstart skill) (S480: 6-phase orchestrator delivers all context)
- [x] Minimum viable context contract enforced: identity + mission + prior + work + operational HOW (S480: orchestrator Identity+Session+Work+Epoch+Operations phases)
- [x] Agent can execute work immediately after coldstart without reading additional files (S480: survey cycle runs directly from coldstart output)

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
