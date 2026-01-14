# generated: 2025-12-24
# System Auto: last updated on: 2025-12-24T20:07:47
# Milestone Tree

Show milestone progress and plan tree for current work.

## Usage

```
/tree
```

## What It Shows

1. **Milestone Progress**: Current milestone completion percentage
2. **Active Plans**: Plans in progress with their status
3. **Work Item Distribution**: How items are distributed across nodes

## Execution

Run the tree recipe:

```bash
just tree
```

## Example Output

```
Milestone: M7a-Recipes (83%)
├── Complete: E2-162, E2-143, E2-167, E2-168, E2-169
└── Active: E2-090

Plan Tree:
├── PLAN-E2-090 (draft)
└── ...
```

## Related

- `/ready` - What's ready to work on
- `/workspace` - Outstanding work summary
- `/status` - Full system status
