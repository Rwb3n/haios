# Schema Registry

Central registry for all enum and schema definitions used across HAIOS.

**WORK-147** | REQ-REFERENCE-002 | Session 369

## Purpose

Single source of truth for enum values. Eliminates duplication where the same enum
(e.g., work item status) was defined in 3+ places with different values.

## Structure

```
schemas/
  core/           # Portable to any project (TRD-defined enums)
    work_item.yaml   # status, type, priority, effort
    queue.yaml       # queue_position, queue transitions
    lifecycle.yaml   # cycle_phase, lifecycles, cycle transitions
  project/        # HAIOS-specific (not portable)
    (empty - add project-specific schemas here)
```

**Core** schemas come from TRD-WORK-ITEM-UNIVERSAL and are portable across projects.
**Project** schemas are HAIOS-specific (activities, ceremonies, observations, etc.).

## Schema File Format

Each schema file is YAML with this convention:

```yaml
version: "2.0"
source: TRD-WORK-ITEM-UNIVERSAL  # Where values are authoritative

enums:
  status:
    values: [active, blocked, complete, archived]
    default: active

  type:
    values: [feature, investigation, bug, chore, spike]
    default: feature

transitions:
  cycle_phase:
    backlog: [plan]
    plan: [backlog, implement]
```

Required sections: at least one of `enums` or `transitions` (files without either are skipped).

## Accessing Schemas

### From Python (runtime)

```python
from config import ConfigLoader

config = ConfigLoader.get()

# Get all loaded schemas
schemas = config.schemas  # Dict[str, Dict]

# Get specific enum entry
status = config.get_schema("work_item", "status")
# Returns: {"values": ["active", "blocked", "complete", "archived"], "default": "active"}

# Get transitions
transitions = config.get_schema("lifecycle", "transitions")
```

### From Templates (scaffold time)

Use `{{schema:domain.key}}` syntax in template files. Resolved by `substitute_variables()`
at scaffold time to pipe-delimited values.

#### Correct Examples

```
type: {{schema:work_item.type}}
# Resolves to: type: feature|investigation|bug|chore|spike

status: {{schema:work_item.status}}
# Resolves to: status: active|blocked|complete|archived

priority: {{schema:work_item.priority}}
# Resolves to: priority: critical|high|medium|low

queue_position: {{schema:queue.queue_position}}
# Resolves to: queue_position: parked|backlog|ready|working|done

cycle_phase: {{schema:lifecycle.cycle_phase}}
# Resolves to: cycle_phase: backlog|plan|implement|check|done
```

#### Incorrect Examples (Common Mistakes)

```
# WRONG: Missing dot separator
{{schema:work_item_type}}        # Not matched by regex

# WRONG: Wrong domain name
{{schema:work.type}}             # KeyError - domain is "work_item" not "work"

# WRONG: Wrong key name
{{schema:work_item.statuses}}    # KeyError - key is "status" not "statuses"

# WRONG: Extra nesting
{{schema:core.work_item.type}}   # Not matched - only domain.key, no tier prefix

# WRONG: Spaces
{{schema: work_item.type}}       # Not matched - no spaces allowed
```

## Adding New Schemas

1. Create a YAML file in `core/` (portable) or `project/` (HAIOS-specific)
2. Include `version`, `source`, and at least one of `enums` or `transitions`
3. ConfigLoader picks it up automatically on next `ConfigLoader.reset()` / init
4. Domain name = filename without extension (e.g., `queue.yaml` -> domain `queue`)

## Discovery

Schemas are discovered via `haios.yaml`:

```yaml
paths:
  schemas: ".claude/haios/schemas"
```

ConfigLoader reads this path and scans all `*.yaml` files in `core/` and `project/` subdirectories.

## References

- @docs/work/active/WORK-067/WORK.md (investigation: schema architecture)
- @docs/work/active/WORK-147/WORK.md (implementation)
- @.claude/haios/lib/config.py (ConfigLoader.get_schema)
- @.claude/haios/lib/scaffold.py (substitute_variables schema resolution)
