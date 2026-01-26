---
id: CH-007
arc: workuniversal
name: EpochFieldOnWorkItems
status: Active
created: 2026-01-26
spawned_from:
- obs-214-003
generated: '2026-01-26'
last_updated: '2026-01-26T19:29:15'
---
# Chapter: Epoch Field on Work Items

## Purpose

Add `epoch` field to work item schema to prevent epoch drift.

## Context

obs-214-003 documented that Session 214 loaded E2.3 context but spent entire session on E2-179 (legacy E2 work). No gate caught this drift because work items have no epoch field.

## Deliverables

1. Update TRD-WORK-ITEM-UNIVERSAL with `epoch` field
2. Update work_item.md template
3. Update scaffold.py to inject epoch from haios.yaml
4. Update survey-cycle to warn on epoch-misaligned work

## Success Criteria

- [ ] Epoch field in schema
- [ ] Survey-cycle warns on cross-epoch selection
- [ ] New work items auto-populate epoch

## References

- obs-214-003: Work items lack epoch field
- TRD-WORK-ITEM-UNIVERSAL.md
- WorkUniversal arc
