---
template: implementation_plan
status: ready
date: 2025-12-21
backlog_id: E2-126
title: "Frontmatter Timestamp Migration"
author: Hephaestus
lifecycle_phase: plan
session: 94
spawned_by: E2-120
blocked_by: []
related: [E2-120, post_tool_use.py]
milestone: M5-Plugin
version: "1.3"
generated: 2025-12-21
last_updated: 2025-12-21T14:43:01
---
# Implementation Plan: Frontmatter Timestamp Migration

@docs/plans/PLAN-E2-120-complete-powershell-to-python-migration.md
@.claude/hooks/hooks/post_tool_use.py

---

## Goal

Migrate 87 legacy files with broken timestamp format (comments OUTSIDE frontmatter) to correct format (YAML fields INSIDE frontmatter).

---

## Effort Estimation (Ground Truth)

> Based on Session 93 analysis: 87 affected files identified.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 87 | `grep -l "^# generated:" docs/` |
| Lines of code affected | ~174 | 2 lines per file (generated + System Auto) |
| New files to create | 1 | `scripts/migrate_timestamps.py` |
| Tests to write | 3-5 | Test script behavior |
| Dependencies | 0 | Standalone script |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | One-time migration script |
| Risk of regression | Low | Idempotent, can re-run safely |
| External dependencies | None | Pure file manipulation |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Script development | 30 min | High |
| Testing on sample | 15 min | High |
| Full migration run | 10 min | High |
| Verification | 15 min | High |
| **Total** | ~1 hr | High |

---

## Current State vs Desired State

### Current State (87 files)

```markdown
# generated: 2025-12-15
# System Auto: last updated on: 2025-12-20 14:30:00
---
template: checkpoint
status: complete
session: 90
---
# Session 90 Checkpoint
```

**Behavior:** Comment timestamps appear BEFORE YAML frontmatter opening `---`.

**Result:** YAML parsers skip these lines, timestamps invisible to validation.

### Desired State

```markdown
---
template: checkpoint
status: complete
session: 90
generated: 2025-12-15
last_updated: 2025-12-20T14:30:00
---
# Session 90 Checkpoint
```

**Behavior:** Timestamps are YAML fields INSIDE frontmatter.

**Result:** Standard YAML parsing finds timestamps, validation works correctly.

---

## Tests First (TDD)

### Test 1: Script converts legacy format correctly
```python
def test_migrate_converts_legacy_to_yaml():
    content = """# generated: 2025-12-15
# System Auto: last updated on: 2025-12-20 14:30:00
---
template: test
---
Content here"""
    result = migrate_file_content(content)
    assert "---\ntemplate: test" in result
    assert "generated: 2025-12-15" in result
    assert "last_updated: 2025-12-20T14:30:00" in result
    assert "# generated:" not in result
```

### Test 2: Script handles BOM correctly
```python
def test_migrate_handles_bom():
    content = "\ufeff# generated: 2025-12-15\n---\ntemplate: test\n---"
    result = migrate_file_content(content)
    assert not result.startswith("\ufeff")
    assert "generated: 2025-12-15" in result
```

### Test 3: Script is idempotent
```python
def test_migrate_is_idempotent():
    # Already correct format
    content = """---
template: test
generated: 2025-12-15
last_updated: 2025-12-20T14:30:00
---
Content"""
    result = migrate_file_content(content)
    assert result == content  # No change
```

### Test 4: Script preserves existing frontmatter fields
```python
def test_migrate_preserves_frontmatter_fields():
    content = """# generated: 2025-12-15
# System Auto: last updated on: 2025-12-20 14:30:00
---
template: checkpoint
status: complete
session: 90
backlog_id: E2-120
---"""
    result = migrate_file_content(content)
    assert "template: checkpoint" in result
    assert "status: complete" in result
    assert "session: 90" in result
    assert "backlog_id: E2-120" in result
```

---

## Detailed Design

### Migration Script Logic

**File:** `scripts/migrate_timestamps.py`

```python
#!/usr/bin/env python3
"""Migrate legacy timestamp format to YAML frontmatter fields.

E2-126: Fix 87 files with broken timestamp format from legacy PostToolUse.ps1.

Usage:
    python scripts/migrate_timestamps.py --dry-run  # Preview changes
    python scripts/migrate_timestamps.py            # Apply changes
"""

import re
from pathlib import Path
from datetime import datetime

def migrate_file_content(content: str) -> str:
    """
    Convert legacy timestamp comments to YAML frontmatter fields.

    Input format:
        # generated: 2025-12-15
        # System Auto: last updated on: 2025-12-20 14:30:00
        ---
        template: checkpoint
        ---

    Output format:
        ---
        template: checkpoint
        generated: 2025-12-15
        last_updated: 2025-12-20T14:30:00
        ---
    """
    # Handle BOM
    if content.startswith('\ufeff'):
        content = content[1:]

    lines = content.split('\n')

    # Extract legacy timestamps
    generated_date = None
    last_updated = None
    content_start = 0

    for i, line in enumerate(lines):
        if match := re.match(r'^#\s*generated:\s*(\d{4}-\d{2}-\d{2})', line):
            generated_date = match.group(1)
            content_start = i + 1
        elif match := re.match(r'^#\s*System Auto:.*last updated on:\s*(.+)', line):
            timestamp_str = match.group(1).strip()
            # Normalize to ISO format
            last_updated = normalize_timestamp(timestamp_str)
            content_start = i + 1
        elif line.strip() == '---':
            break

    # If no legacy timestamps found, return unchanged
    if generated_date is None and last_updated is None:
        return content

    # Find YAML frontmatter
    remaining = '\n'.join(lines[content_start:])

    if not remaining.strip().startswith('---'):
        return content  # No frontmatter to update

    # Parse frontmatter
    yaml_match = re.match(r'^---\s*\n(.*?)\n---', remaining, re.DOTALL)
    if not yaml_match:
        return content

    yaml_content = yaml_match.group(1)
    after_frontmatter = remaining[yaml_match.end():]

    # Add timestamps to YAML
    yaml_lines = yaml_content.split('\n')

    # Check if timestamps already exist
    has_generated = any('generated:' in line for line in yaml_lines)
    has_last_updated = any('last_updated:' in line for line in yaml_lines)

    if not has_generated and generated_date:
        yaml_lines.append(f'generated: {generated_date}')
    if not has_last_updated and last_updated:
        yaml_lines.append(f'last_updated: {last_updated}')

    # Rebuild file
    new_yaml = '\n'.join(yaml_lines)
    return f'---\n{new_yaml}\n---{after_frontmatter}'


def normalize_timestamp(ts: str) -> str:
    """Normalize timestamp to ISO format."""
    # Handle "2025-12-20 14:30:00" -> "2025-12-20T14:30:00"
    if ' ' in ts and 'T' not in ts:
        return ts.replace(' ', 'T')
    return ts
```

### Call Chain Context

```
migrate_timestamps.py (one-time script)
    |
    +-> find_affected_files()   # Glob docs/**/*.md with legacy format
    |
    +-> migrate_file_content()  # Transform each file
    |
    +-> write_file()            # Save with UTF-8 encoding
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Standalone script | Not a hook | One-time migration, not runtime |
| Dry-run mode | Default preview | Safety for 87-file change |
| Idempotent | Skip if already migrated | Safe to re-run |
| Preserve field order | Append timestamps at end | Don't disturb existing fields |

### Input/Output Examples

**Real file before (docs/checkpoints/2025-12-13-01-SESSION-64-...md):**
```markdown
# generated: 2025-12-13
# System Auto: last updated on: 2025-12-13 21:30:00
---
template: checkpoint
status: complete
session: 64
backlog_id: E2-FIX-002
---
# Session 64: E2-FIX-002 Ingester Embedding Fix
```

**After migration:**
```markdown
---
template: checkpoint
status: complete
session: 64
backlog_id: E2-FIX-002
generated: 2025-12-13
last_updated: 2025-12-13T21:30:00
---
# Session 64: E2-FIX-002 Ingester Embedding Fix
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| File has BOM | Strip BOM before processing | Test 2 |
| Already migrated | Skip (idempotent) | Test 3 |
| No frontmatter | Skip (not a governed file) | N/A |
| Missing generated date | Only add last_updated | N/A |
| Timestamp format variations | Normalize to ISO | Test 1 |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_migrate_timestamps.py`
- [ ] Add 4 tests above
- [ ] Verify all tests fail (red)

### Step 2: Implement Migration Function
- [ ] Create `scripts/migrate_timestamps.py`
- [ ] Implement `migrate_file_content()`
- [ ] Implement `normalize_timestamp()`
- [ ] Tests pass (green)

### Step 3: Add CLI Interface
- [ ] Add `--dry-run` flag
- [ ] Add file discovery (glob docs/**/*.md)
- [ ] Add progress reporting

### Step 4: Dry Run Verification
- [ ] Run `python scripts/migrate_timestamps.py --dry-run`
- [ ] Verify 87 files identified
- [ ] Spot-check 3-5 files

### Step 5: Full Migration
- [ ] Run `python scripts/migrate_timestamps.py`
- [ ] Verify all files updated
- [ ] Run `just validate` on sample files

### Step 6: Enable Skipped Test
- [ ] Update `tests/test_lib_validate.py` - remove skip from timestamp test
- [ ] Verify all tests pass (322 + 1 = 323)

### Step 7: README Sync (MUST)
- [ ] **MUST:** Update `scripts/README.md` with new script
- [ ] **MUST:** Verify README content matches actual file state

---

## Verification

- [ ] Tests pass (323 total after enabling skipped test)
- [ ] **MUST:** All READMEs current
- [ ] Sample files have correct format

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Malformed YAML | Medium | Validate after migration |
| Encoding issues | Low | UTF-8 read/write with BOM handling |
| Git history noise | Low | Single commit with clear message |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `scripts/migrate_timestamps.py` | Script exists, runs | [ ] | |
| `tests/test_migrate_timestamps.py` | 4+ tests pass | [ ] | |
| `docs/checkpoints/*.md` | No `# generated:` lines | [ ] | |
| `docs/plans/*.md` | No `# generated:` lines | [ ] | |
| `scripts/README.md` | Documents script | [ ] | |

**Verification Commands:**
```bash
# Check no legacy format remains
grep -r "^# generated:" docs/ | wc -l
# Expected: 0

# Check all tests pass
pytest tests/ -v
# Expected: 323 passed
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
- [ ] **MUST:** READMEs updated in all modified directories
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- **E2-120 Phase 3:** Fixed PostToolUse to inject correct format (Session 94)
- **Session 93 Checkpoint:** Identified 87 affected files
- **post_tool_use.py:94-192:** New timestamp injection logic

---
