---
id: CH-005
arc: workuniversal
name: ValidationRules
status: Active
created: 2026-01-27
spawned_from:
- INV-072
generated: '2026-01-27'
last_updated: '2026-01-27T23:15:50'
---
# Chapter: Validation Rules

## Purpose

Implement validation rules for work item creation and lifecycle to prevent data loss and enforce structural integrity.

## Context

CH-005 was originally deferred in ARC.md as "basic validation exists; advanced rules post-migration." INV-072 (Spawn ID Collision) revealed that `create_work()` does not check terminal status before creating, allowing accidental overwrites of completed work. This un-defers the chapter.

## Deliverables

1. Status-aware ID validation in WorkEngine (`_validate_id_available`)
2. Same validation in scaffold.py for work_item templates
3. Test coverage for validation logic
4. Future: additional validation rules as identified

## Work Items

| ID | Title | Status |
|----|-------|--------|
| E2-304 | Add Status-Aware ID Validation to Work Creation | Active |

## Success Criteria

- [ ] `create_work()` blocks on terminal-status ID collision
- [ ] `scaffold_template()` blocks on terminal-status ID collision
- [ ] Tests cover positive (new ID allowed) and negative (terminal ID blocked) cases

## References

- @docs/work/active/INV-072/investigations/001-spawn-id-collision-completed-work-items-reused.md
- @.claude/haios/modules/work_engine.py
- @.claude/lib/scaffold.py
