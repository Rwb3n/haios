# generated: 2025-12-30
# System Auto: last updated on: 2025-12-30T23:10:37
# Section 5: Session Number Computation

Generated: 2025-12-30 (Session 151)
Purpose: Document how session numbers are derived from checkpoint filenames
Status: COMPLETE

---

## Overview

Session numbers are derived from checkpoint filenames, not stored in a central registry. The `status.py::get_session_delta()` function computes current and prior session by parsing checkpoint files.

---

## Gaps Identified (S152 Analysis)

| Gap | Description | Target Fix |
|-----|-------------|------------|
| **Legacy paths in _find_completed_items** | Still checks `docs/plans/` and `docs/pm/backlog.md` | Check `docs/work/archive/` for `status: complete` |
| **No session binding to WORK.md** | Session touches work via checkpoint.backlog_ids, but WORK.md doesn't know which session touched it | Add `session` field to `node_history` entries |
| **Duplicate session numbers possible** | Multiple checkpoints can exist for same session (e.g., SESSION-94 appears 3x) | Current algorithm takes most recent - acceptable |

---

## Target Architecture

### Session ↔ Work Item Bidirectional Link

```yaml
# Current: Checkpoint knows work items
# docs/checkpoints/SESSION-151-*.md
backlog_ids: [E2-150, INV-052]

# Target: Work item knows sessions (from SECTION-3)
# docs/work/active/E2-150/WORK.md
node_history:
  - node: implement
    session: 151           # ← BIDIRECTIONAL LINK
    entered: 2025-12-30T...
```

**Portable location:** `.claude/haios/state/session-registry.yaml` (derived, not authoritative)

---

## Source of Truth

```
docs/checkpoints/YYYY-MM-DD-NN-SESSION-{N}-{title}.md
                                    ↑
                              Session number extracted via regex
```

**Pattern:** `SESSION-(\d+)-` in filename

---

## Key Function: `get_session_delta()`

**Location:** `.claude/lib/status.py:260`

```python
def get_session_delta() -> dict[str, Any]:
    """Compare last 2 checkpoints to calculate momentum delta.

    Returns:
        Dict with prior_session, current_session, completed, added, etc.
    """
```

### Algorithm

1. List all `docs/checkpoints/*.md` files
2. Filter out README.md and files without `SESSION-` in name
3. Sort by filename (descending) - date + session in filename ensures correct order
4. Take first 2 files: `current_file` (most recent), `prior_file`
5. Parse YAML frontmatter from each:
   - `session: N` - Session number
   - `date: YYYY-MM-DD` - Session date
   - `backlog_ids: [...]` - Work items touched
6. Compute delta:
   - `added = current_ids - prior_ids`
   - `completed = items from prior that are now complete`

### Return Structure

```python
{
    "prior_session": 149,
    "current_session": 150,
    "prior_date": "2025-12-29",
    "completed": ["E2-232", "E2-233"],
    "completed_count": 2,
    "added": ["E2-234", "E2-235"],
    "added_count": 2,
    "milestone_delta": null
}
```

---

## Filename Convention

```
YYYY-MM-DD-NN-SESSION-{N}-{title}.md
│          │         │    │
│          │         │    └── Kebab-case title
│          │         └─────── Session number (monotonic)
│          └───────────────── Sequence within day (01, 02, ...)
└──────────────────────────── ISO date
```

**Example:** `2025-12-30-01-SESSION-150-inv-052-architecture-redesign.md`

---

## Edge Cases

| Scenario | Behavior |
|----------|----------|
| No checkpoints exist | Returns empty delta |
| Only 1 checkpoint | Returns empty delta (need 2 to compare) |
| Checkpoint has no session in frontmatter | Extracted from filename pattern |
| Gap in session numbers | No issue - uses most recent 2 files |
| Multiple checkpoints same session | Sorted by filename, takes first |

---

## Implications for Architecture

### Current Model (Events-Based)
- `just session-start N` logs to haios-events.jsonl
- Session number must be manually computed: `current_session + 1`
- Crash leaves orphaned session (no end event)

### Target Model (Work-Based - INV-052)
- Session number still derived from checkpoints (unchanged)
- But work state lives in WORK.md, survives crashes
- Checkpoint is capture ceremony, not state

### Why Not Store Session in Registry?

| Approach | Pros | Cons |
|----------|------|------|
| Filename derivation | Self-documenting, no sync issues | Requires file scan |
| Registry file | O(1) lookup | Sync risk, corruption risk |
| Database | Queryable | Overkill, adds dependency |

**Decision:** Keep filename derivation. Cost is negligible (glob + regex).

---

## Related Functions

| Function | Purpose |
|----------|---------|
| `_parse_checkpoint_yaml()` | Extract frontmatter from checkpoint |
| `_find_completed_items()` | Check if prior items are now complete |
| `generate_slim_status()` | Orchestrator that calls get_session_delta() |

---

*Populated Session 151*
