# generated: 2026-02-19
# System Auto: last updated on: 2026-02-19T08:30:00
# Chapter: MCPOperationsServer

## Chapter Definition

**Chapter ID:** CH-066
**Arc:** call
**Epoch:** E2.8
**Name:** MCP Operations Server
**Status:** Active

---

## Purpose

Expose work/hierarchy/session/scaffold operations as an MCP server — the agent-native Tier 2 interface. Replaces `just` recipes for agent use; `just` remains Tier 3 (operator terminal only).

**Core insight:** `just` recipes are shell commands that agents invoke via Bash tool. MCP tools are native to the agent protocol — no shell overhead, typed inputs/outputs, discoverable via infrastructure. Moving Tier 2 operations (queue, scaffold, hierarchy queries) to MCP makes them first-class agent capabilities.

---

## Work Items

| ID | Title | Status | Type |
|----|-------|--------|------|
| ~~WORK-218~~ | MCP Operations Server Investigation | Complete | investigation |
| WORK-219 | Extract State Management Abstractions (Phase 0) | Complete | implementation |
| WORK-220 | MCP Operations Server Core (Phase 1) | Complete | implementation |
| WORK-221 | Investigation Closure Spawn Completeness | Complete | investigation |
| WORK-222 | StatusPropagator Exit Criteria Validation | Active | investigation |
| WORK-223 | MCP Operations Extended Tools (Phase 2) | Complete | implementation |
| WORK-224 | MCP Operations Governance Integration (Phase 3) | Complete | implementation |
| WORK-225 | Migrate Skill Consumers from Just Recipes to MCP Operations Tools | Complete | implementation |
| WORK-226 | MCP Operations Server Phase 4: Scaffold and Query Tools | Complete | implementation |
| WORK-227 | Investigation CONCLUDE Spawn Completeness Enforcement | Active | implementation |
| WORK-228 | Audit Just Recipe Consumers and Migrate to MCP Operations Tools | Complete | investigation |
| WORK-229 | Migrate Remaining Skill cycle_set/clear/ready References to MCP | Complete | implementation |
| WORK-230 | Migrate Scaffold Commands and Agent Files to MCP Operations Tools | Complete | implementation |

---

## Exit Criteria

- [ ] haios-operations MCP server exposes work/hierarchy/session/scaffold tools
- [ ] Just recipes retired for agent use — MCP tools replace Tier 2 operations
- [ ] Just remains Tier 3 (operator terminal only)

---

## Dependencies

| Direction | Target | Reason |
|-----------|--------|--------|
| Blocked by | CH-061 (ColdstartContextInjection) | MCP server depends on coldstart context being comprehensive |
| None | - | No outbound blocks |

---

## References

- @.claude/haios/epochs/E2_8/arcs/call/ARC.md (parent arc)
- @.claude/haios/epochs/E2_8/EPOCH.md (parent epoch)
- @docs/ADR/ADR-045-three-tier-entry-point-architecture.md (Tier 2 definition)
- Memory: REQ-DISCOVER-002, REQ-CONFIG-001
