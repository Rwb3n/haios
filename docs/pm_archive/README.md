# generated: 2025-12-07
# System Auto: last updated on: 2025-12-07 10:32:20
# Project Management Directory

## Purpose
Central hub for tracking action items, backlog, and project status. Wired into HAIOS self-awareness mechanisms.

## Structure
```
docs/pm/
├── README.md          # This file
├── backlog.md         # Master list of action items (synced to memory)
└── archive/           # Completed items (moved here for reference)
```

## Usage

### Adding Items
Edit `backlog.md` directly. PostToolUse hook syncs changes to memory automatically.

### Querying
```
memory_search_with_experience("active backlog items")
memory_search_with_experience("HAIOS project status")
```

### Self-Awareness Integration
- `/coldstart` loads backlog summary
- `/haios` displays active item count
- Stop hook extracts new items from session

## Item Format
```markdown
### [PRIORITY] ITEM-ID: Title
- **Status:** pending | in_progress | blocked | done
- **Owner:** Hephaestus | Genesis | Operator
- **Created:** yyyy-mm-dd
- **Context:** Brief description
```

## Sync to Memory
Items stored with:
- `content_type`: "techne"
- `source_path`: "pm:backlog"
- Queryable across sessions
