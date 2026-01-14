---
template: implementation_plan
status: complete
date: 2025-12-24
backlog_id: E2-170
title: "Backfill Work Items from Archived Backlog"
author: Hephaestus
lifecycle_phase: plan
session: 110
version: "1.5"
generated: 2025-12-21
last_updated: 2025-12-24T11:57:50
---
# Implementation Plan: Backfill Work Items from Archived Backlog

@docs/README.md
@docs/epistemic_state.md

---

<!-- TEMPLATE GOVERNANCE (v1.4)

     SKIP RATIONALE REQUIREMENT:
     If ANY section below is omitted or marked N/A, you MUST provide rationale.

     Format for skipped sections:

     ## [Section Name]

     **SKIPPED:** [One-line rationale explaining why this section doesn't apply]

     Examples:
     - "SKIPPED: New feature, no existing code to show current state"
     - "SKIPPED: Pure documentation task, no code changes"
     - "SKIPPED: Trivial fix, single line change doesn't warrant detailed design"

     This prevents silent section deletion and ensures conscious decisions.
-->

---

## Goal

Work files will contain complete content (Context, Deliverables, Milestone, spawned_by) parsed from backlog.md and backlog_archive.md, enabling work files to be the source of truth.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | ~73 | `docs/work/active/*.md` |
| Lines of code affected | ~200 | New script in `.claude/lib/` |
| New files to create | 2 | `backfill.py`, test file |
| Tests to write | 4 | Parse + update + edge cases |
| Dependencies | 0 | Self-contained |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only reads backlog, writes work files |
| Risk of regression | Low | New script, no existing code touched |
| External dependencies | Low | Pure Python, file I/O only |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Script development | 45 min | High |
| Just recipe | 5 min | High |
| Testing + verification | 15 min | High |
| **Total** | 65 min | High |

---

## Current State vs Desired State

### Current State

Work files have placeholder content:
```markdown
# docs/work/active/WORK-E2-021-*.md
## Context
[Problem and root cause]

## Deliverables
- [ ] [Deliverable 1]
- [ ] [Deliverable 2]
```

**Behavior:** E2-151 migration script scaffolded files but didn't parse backlog content.

**Result:** Work files are useless as source of truth - all context is in backlog.md.

### Desired State

Work files contain parsed content from backlog:
```markdown
# docs/work/active/WORK-E2-021-*.md
## Context
**Problem:** Backlog items inconsistently link to memory concepts. No closed learning loop.
**Vision:** APIP Memory Linkage Pattern...

## Deliverables
- [ ] Add memory-specific MUST/SHOULD rules to CLAUDE.md
- [ ] Add `memory_refs` field to backlog_item template
...
```

**Behavior:** Backfill script parses backlog entries and updates work file content.

**Result:** Work files become the single source of truth for work item details.

---

## Tests First (TDD)

### Test 1: Parse Backlog Entry
```python
def test_parse_backlog_entry_extracts_fields():
    """Parse a backlog entry and extract key fields."""
    entry = parse_backlog_entry("E2-021", backlog_content)
    assert entry["context"] is not None
    assert "memory" in entry["context"].lower()
    assert entry["milestone"] is not None or entry["milestone"] == ""
    assert len(entry["deliverables"]) > 0
```

### Test 2: Parse Archive Entry
```python
def test_parse_archive_entry():
    """Parse archive entry with different format (has Closed, Resolution)."""
    entry = parse_backlog_entry("E2-010", archive_content)
    assert entry["status"] == "closed"
    assert entry["closed_date"] is not None
```

### Test 3: Update Work File Content
```python
def test_update_work_file_content():
    """Update work file Context and Deliverables sections."""
    result = update_work_file("E2-021", parsed_entry)
    assert "[Problem and root cause]" not in result
    assert "Backlog items inconsistently link" in result
```

### Test 4: Update Work File Frontmatter
```python
def test_update_work_file_frontmatter():
    """Update milestone, spawned_by, related in frontmatter."""
    result = update_work_file_frontmatter(work_content, parsed_entry)
    assert "milestone: M4-Research" in result or "milestone: null" in result
```

---

## Detailed Design

### New File: `.claude/lib/backfill.py`

```python
"""Backfill work files from backlog entries."""

import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent


def parse_backlog_entry(backlog_id: str, content: str) -> dict | None:
    """Parse a backlog entry and extract key fields.

    Args:
        backlog_id: ID like "E2-021", "INV-015"
        content: Full backlog.md or backlog_archive.md content

    Returns:
        Dict with: context, deliverables, milestone, session, spawned_by, related
        or None if not found.
    """
    # Find entry by pattern: ### [STATUS] {backlog_id}:
    pattern = rf"^### \[.*?\] {re.escape(backlog_id)}:.*?(?=^### |\Z)"
    match = re.search(pattern, content, re.MULTILINE | re.DOTALL)
    if not match:
        return None

    entry_text = match.group(0)
    result = {
        "context": "",
        "deliverables": [],
        "milestone": None,
        "session": None,
        "spawned_by": None,
        "related": [],
        "status": None,
        "closed_date": None,
    }

    # Extract fields using regex
    # Context comes from **Context:** line
    ctx_match = re.search(r"\*\*Context:\*\*\s*(.+?)(?=\n- \*\*|\n\n|$)", entry_text, re.DOTALL)
    if ctx_match:
        result["context"] = ctx_match.group(1).strip()

    # Milestone
    mile_match = re.search(r"\*\*Milestone:\*\*\s*(\S+)", entry_text)
    if mile_match:
        result["milestone"] = mile_match.group(1)

    # Session
    sess_match = re.search(r"\*\*Session:\*\*\s*(.+?)(?=\n|$)", entry_text)
    if sess_match:
        result["session"] = sess_match.group(1).strip()

    # Spawned By
    spawn_match = re.search(r"\*\*Spawned By:\*\*\s*(.+?)(?=\n|$)", entry_text)
    if spawn_match:
        result["spawned_by"] = spawn_match.group(1).strip()

    # Deliverables - find checklist items
    deliverables = re.findall(r"^\s*-\s*\[[ x]\]\s*(.+)$", entry_text, re.MULTILINE)
    result["deliverables"] = deliverables

    # Status from header
    status_match = re.search(r"^### \[(\w+)\]", entry_text)
    if status_match:
        result["status"] = status_match.group(1).lower()

    # Closed date (for archive)
    closed_match = re.search(r"\*\*Closed:\*\*\s*(.+?)(?=\n|$)", entry_text)
    if closed_match:
        result["closed_date"] = closed_match.group(1).strip()

    return result


def update_work_file(work_path: Path, parsed: dict) -> str:
    """Update work file with parsed backlog content.

    Updates:
    - Context section with parsed context
    - Deliverables section with checklist items
    - Frontmatter: milestone, spawned_by
    """
    content = work_path.read_text(encoding="utf-8")

    # Update Context section
    if parsed["context"] and "[Problem and root cause]" in content:
        content = content.replace(
            "[Problem and root cause]",
            f"**Problem:** {parsed['context']}"
        )

    # Update Deliverables section
    if parsed["deliverables"]:
        old_deliverables = "- [ ] [Deliverable 1]\n- [ ] [Deliverable 2]"
        new_deliverables = "\n".join(f"- [ ] {d}" for d in parsed["deliverables"])
        content = content.replace(old_deliverables, new_deliverables)

    # Update frontmatter
    if parsed["milestone"]:
        content = re.sub(r"milestone: null", f"milestone: {parsed['milestone']}", content)

    if parsed["spawned_by"]:
        content = re.sub(r"spawned_by: null", f"spawned_by: {parsed['spawned_by']}", content)

    return content


def backfill_work_item(backlog_id: str) -> bool:
    """Backfill a single work item from backlog sources."""
    # Find work file
    work_dir = PROJECT_ROOT / "docs" / "work" / "active"
    matches = list(work_dir.glob(f"WORK-{backlog_id}-*.md"))
    if not matches:
        return False

    work_path = matches[0]

    # Try backlog.md first, then archive
    backlog_path = PROJECT_ROOT / "docs" / "pm" / "backlog.md"
    archive_path = PROJECT_ROOT / "docs" / "pm" / "backlog_archive.md"

    parsed = None
    for source in [backlog_path, archive_path]:
        if source.exists():
            content = source.read_text(encoding="utf-8")
            parsed = parse_backlog_entry(backlog_id, content)
            if parsed:
                break

    if not parsed:
        return False

    # Update work file
    new_content = update_work_file(work_path, parsed)
    work_path.write_text(new_content, encoding="utf-8")
    return True
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Regex parsing | Pattern-based extraction | Backlog format is semi-structured markdown - regex handles it well |
| Partial update | Only replace placeholders | Preserve any manual edits already made to work files |
| Backlog priority | Try backlog.md before archive | Active items more likely in main file |

### Input/Output Example

**Input (E2-021 in backlog.md):**
```markdown
### [HIGH] E2-021: Memory Reference Governance + Rhythm
- **Context:** Backlog items inconsistently link to memory concepts...
- **Milestone:** M4-Research
- **Spawned By:** Session 50
  - [ ] Add memory-specific MUST/SHOULD rules
  - [ ] Add `memory_refs` field to template
```

**Output (WORK-E2-021-*.md after backfill):**
```yaml
# Frontmatter
milestone: M4-Research
spawned_by: Session 50
```
```markdown
## Context
**Problem:** Backlog items inconsistently link to memory concepts...

## Deliverables
- [ ] Add memory-specific MUST/SHOULD rules
- [ ] Add `memory_refs` field to template
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| ID not found in backlog | Return False, no changes | Test 2 |
| Work file already has content | Skip if placeholder text not present | Implicit |
| Archive format differences | Parse Closed, Resolution fields | Test 2 |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_backfill.py`
- [ ] Add Test 1-4 from TDD section
- [ ] Verify all tests fail (red) - module doesn't exist yet

### Step 2: Implement backfill.py
- [ ] Create `.claude/lib/backfill.py` with parse_backlog_entry()
- [ ] Tests 1, 2 pass (green)
- [ ] Add update_work_file() function
- [ ] Tests 3, 4 pass (green)
- [ ] Add backfill_work_item() orchestrator

### Step 3: Add Just Recipe
- [ ] Add `just backfill <id>` recipe to justfile
- [ ] Add `just backfill-all` for batch processing

### Step 4: Run Backfill
- [ ] Test on single item: `just backfill E2-021`
- [ ] Verify work file updated correctly
- [ ] Run `just backfill-all` for all items
- [ ] Spot check 5 random work files

### Step 5: README Sync (MUST)
- [ ] **MUST:** Update `.claude/lib/README.md` with backfill.py
- [ ] **MUST:** Update `scripts/README.md` if recipes added there

### Step 6: Consumer Verification
- [ ] N/A - new standalone script, no migrations

---

## Verification

- [ ] Tests pass (4 tests in test_backfill.py)
- [ ] **MUST:** `.claude/lib/README.md` updated
- [ ] Code review: spot check 5 work files

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Regex doesn't match all formats | Medium | Test with diverse entries, iterate regex |
| Overwrite manual edits | Medium | Only replace placeholder text |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 110 | 2025-12-24 | - | In Progress | Plan created |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/backfill.py` | Functions parse_backlog_entry, update_work_file, backfill_work_item | [ ] | |
| `tests/test_backfill.py` | 4 tests covering parse + update | [ ] | |
| `.claude/lib/README.md` | Lists backfill.py | [ ] | |
| `docs/work/active/WORK-E2-021-*.md` | Context not "[Problem and root cause]" | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_backfill.py -v
# Expected: 4 tests passed
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated
- [ ] All work files backfilled

---

## References

- E2-151: Original migration that created placeholders
- ADR-039: Work Item as File Architecture

---
