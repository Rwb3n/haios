# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:33:20
# Chapter: Spawn Ceremony

## Definition

**Chapter ID:** CH-017
**Arc:** ceremonies
**Status:** Planned
**Implementation Type:** CREATE NEW
**Depends:** CH-011
**Work Items:** None

---

## Current State (Verified)

**Source:** `.claude/skills/work-creation-cycle/`, `.claude/haios/modules/work_engine.py`

Work creation exists but without lineage:

```python
# WorkEngine.create_work() - no spawned_from parameter
def create_work(self, work_id: str, title: str, ...) -> WorkState:
    """Create new work item. No lineage tracking."""
```

**Source:** `.claude/templates/work_item.md`

Template has `spawned_by` field but no `spawned_from` or `spawned_children`:

```yaml
# From work_item.md template
spawned_by: null  # Which chapter spawned this
```

**What exists:**
- work-creation-cycle creates work items
- `spawned_by` field in template (chapter reference, not work item)
- PortalManager tracks some relationships

**What doesn't exist:**
- `spawned_from` field (parent work item)
- `spawned_children` field (child work items)
- Spawn ceremony skill
- get_work_lineage() method
- SpawnedWork event type

---

## Problem

Work creation doesn't track parent-child work relationships. `spawned_by` references chapters, not work items. No lineage query capability.

---

## Agent Need

> "I need a spawn ceremony to create new work items from existing ones so the lineage is explicit, governed, and traceable."

---

## Requirements

### R1: Spawn Ceremony Definition

```yaml
name: spawn-work
category: spawn
signature: WorkItem → NewWorkItem
```

Creates new work item linked to parent.

### R2: Spawn Contract

```yaml
input_contract:
  - field: parent_work_id
    type: string
    required: true
  - field: new_work_title
    type: string
    required: true
  - field: lifecycle
    type: string
    required: true
    enum: [investigation, design, implementation, validation, triage]
  - field: traces_to
    type: string
    required: true
output_contract:
  - field: new_work_id
    type: string
  - field: work_path
    type: path
side_effects:
  - "Create WORK.md for new item"
  - "Update parent's spawned_children field"
  - "Log SpawnedWork event"
```

### R3: Lineage Tracking

Parent and child both track relationship:

```yaml
# Parent WORK.md
spawned_children:
  - WORK-002  # Design spawned from investigation

# Child WORK.md
spawned_from: WORK-001  # Parent investigation
```

### R4: Spawn vs Intake

| Ceremony | When to Use | Lineage |
|----------|-------------|---------|
| Intake | New idea, no parent | spawned_from: null |
| Spawn | Derived from existing work | spawned_from: WORK-XXX |

---

## Interface

### Spawn Ceremony Skill

```markdown
---
name: spawn-work
category: spawn
input_contract: [...]
output_contract: [...]
---

# Spawn Work Ceremony

## Purpose
Create new work item derived from existing work.

## Input Contract
- parent_work_id: Existing work item to spawn from
- new_work_title: Title for new work
- lifecycle: investigation|design|implementation|validation|triage
- traces_to: Requirement this traces to

## Ceremony Steps
1. Validate parent exists and is at valid spawn point
2. Create new WORK.md with spawned_from
3. Update parent's spawned_children
4. Log SpawnedWork event

## Output Contract
- new_work_id: Created WORK-XXX
- work_path: Path to new WORK.md
```

### Invocation

```python
# From close-work with spawn choice
result = ceremony_runner.invoke("spawn-work",
    parent_work_id="WORK-001",
    new_work_title="Implement lifecycle signatures",
    lifecycle="implementation",
    traces_to="REQ-LIFECYCLE-001"
)
new_id = result.new_work_id  # WORK-002
```

### Lineage Query

```python
def get_work_lineage(work_id: str) -> Lineage:
    """Get parent and children of work item."""
    work = work_engine.get_work(work_id)
    return Lineage(
        parent=work.spawned_from,
        children=work.spawned_children
    )
```

---

## Success Criteria

- [ ] Spawn ceremony skill created
- [ ] Input/output contract defined
- [ ] spawned_from field in child WORK.md
- [ ] spawned_children field in parent WORK.md
- [ ] SpawnedWork event logged
- [ ] Lineage queryable via WorkEngine
- [ ] Spawn distinct from Intake (new work)
- [ ] Unit tests for spawn ceremony
- [ ] Integration test: work → spawn → verify lineage

---

## Non-Goals

- Multi-parent spawn (one parent only)
- Automatic spawn suggestions (caller decides)
- Spawn cascades (spawn creates one item, not chain)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-CEREMONY-001)
- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-004-CallerChaining.md (chaining context)
- @.claude/haios/epochs/E2_5/arcs/queue/CH-010-QueueCeremonies.md (intake ceremony)
