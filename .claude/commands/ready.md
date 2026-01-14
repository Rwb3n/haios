# generated: 2025-12-24
# System Auto: last updated on: 2025-12-24T20:08:16
# Ready to Work

Show what's ready to work on - unblocked items that can be started now.

## Usage

```
/ready
```

## What It Shows

1. **Unblocked Items**: Work items with no blockers
2. **Priority Order**: Sorted by priority (high → medium → low)
3. **Current Node**: Where each item is in the workflow

## Execution

Run the ready recipe:

```bash
just ready
```

## Example Output

```
Ready to Work (5 items):

HIGH:
- E2-152: Work-Item Tooling Cutover (backlog)

MEDIUM:
- E2-160: Work File Prerequisite Gate (plan)
- E2-090: Script-to-Skill Migration (implement)
...
```

## Related

- `/tree` - Milestone progress view
- `/workspace` - Full outstanding work summary
- `/implement <id>` - Start working on an item
