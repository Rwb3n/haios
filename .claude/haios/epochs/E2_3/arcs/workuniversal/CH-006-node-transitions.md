---
id: CH-006
arc: workuniversal
name: NodeTransitionsInvestigation
status: Active
created: 2026-01-26
spawned_from:
- obs-244-01
- obs-230-001
generated: '2026-01-26'
last_updated: '2026-01-26T19:29:12'
---
# Chapter: Node Transitions Investigation

## Purpose

Investigate whether `current_node` and `node_history` fields in work items provide value, or should be removed (YAGNI).

## Context

Multiple observations (obs-244-01, obs-230-001) report that `current_node` stays stuck at `backlog` despite work items completing full lifecycle. The `status` field is authoritative per ADR-041.

## Questions to Answer

1. Are `current_node` and `node_history` used by any code?
2. Do they provide value for debugging/auditing?
3. Should cycles wire transitions, or remove the fields entirely?

## Success Criteria

- [ ] INV document with findings
- [ ] Decision: wire transitions OR remove fields
- [ ] If wire: spawn work item for implementation

## References

- obs-244-01: WORK-015 closure drift
- obs-230-001: CH-005 closure drift
- ADR-041: Status over location
