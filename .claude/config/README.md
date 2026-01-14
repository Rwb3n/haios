# generated: 2025-12-23
# System Auto: last updated on: 2025-12-28T11:03:45
# HAIOS Configuration

Configuration files for the HAIOS plugin. These files define configurable behavior without code changes.

## Files

| File | Purpose | Reference |
|------|---------|-----------|
| `invariants.md` | Core philosophical and operational invariants for L1 context | INV-037, E2-200 |
| `node-cycle-bindings.yaml` | Maps lifecycle nodes to scaffold and exit requirements | E2-154, E2-155, INV-022 |

## Node-Cycle Bindings

The `node-cycle-bindings.yaml` file defines:
- Which skill (cycle) guides each node's workflow
- What documents to scaffold when entering each node (E2-154)
- Exit criteria to check when leaving each node (E2-155)
- Glob patterns to check for existing documents

### Usage

When a work file's `current_node` field changes, the PostToolUse hook (Part 8):
1. Looks up the binding for the new node
2. Checks if required scaffold documents exist
3. Returns a message suggesting `/new-*` commands for missing docs

### Schema

```yaml
nodes:
  <node_name>:
    cycle: <skill_name>|null    # Skill that guides this node
    scaffold:                    # Documents to create on entry (E2-154)
      - type: <template_type>    # Template name (plan, investigation, etc.)
        command: '/new-* ...'    # Slash command with {id} and {title} placeholders
        pattern: 'path/PATTERN-{id}-*.md'  # Glob pattern to check existence
    exit_criteria:               # Conditions to check on exit (E2-155)
      - type: file_status        # Check frontmatter field value
        pattern: 'path/{id}-*.md'
        field: status
        value: complete
        message: "Status not complete"
      - type: section_content    # Check section has content
        pattern: 'path/{id}-*.md'
        section: "## Findings"
        min_length: 50
        message: "Findings section empty"
```

### Example

```yaml
nodes:
  plan:
    cycle: plan-cycle
    scaffold:
      - type: plan
        command: '/new-plan {id} "{title}"'
        pattern: "docs/work/active/{id}/plans/PLAN.md"
    exit_criteria:
      - type: file_status
        pattern: "docs/work/active/{id}/plans/PLAN.md"
        field: status
        value: approved
        message: "Plan status not approved"
```

## Reference

- **E2-154:** Scaffold-on-Entry Hook (PostToolUse)
- **E2-155:** Node Exit Gates (PreToolUse)
- **INV-022:** Work-Cycle-DAG Unified Architecture
- **Library:** `.claude/lib/node_cycle.py`
