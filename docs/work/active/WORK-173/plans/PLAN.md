---
template: implementation_plan
status: complete
date: 2026-02-19
backlog_id: WORK-173
title: "Blocked_by Cascade on Work Closure"
author: Hephaestus
lifecycle_phase: plan
session: 406
version: "1.5"
generated: 2026-02-19
last_updated: 2026-02-19T22:10:00
---
# Implementation Plan: Blocked_by Cascade on Work Closure

---

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Done: 5+ convergent entries (mem:86603, 86632, 86643, 86666, 86680) |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

When a work item closes, all downstream WORK.md files referencing it in `blocked_by` are automatically updated to remove the reference, with failures logged to governance-events.jsonl (never blocking closure).

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | lib/blocked_by_cascade.py (new), modules/cli.py, justfile |
| Lines of code affected | ~80 new | New lib function + cli integration |
| New files to create | 2 | lib/blocked_by_cascade.py, tests/test_blocked_by_cascade.py |
| Tests to write | 7 | Based on test strategy below |
| Dependencies | 2 | yaml (stdlib-like), governance_events.py (for event logging) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Single call site: justfile close-work recipe |
| Risk of regression | Low | New function, existing close path unchanged |
| External dependencies | Low | Only filesystem (WORK.md files) |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 15 min | High |
| Implementation | 20 min | High |
| Integration + verification | 10 min | High |
| **Total** | **45 min** | |

---

## Current State vs Desired State

### Current State

```python
# justfile:68-71 — close-work recipe
close-work id:
    python .claude/haios/modules/cli.py close {{id}}
    just cascade {{id}} complete
    just update-status
```

**Behavior:** `cli.py close` sets status=complete/closed date via WorkEngine.close(). `just cascade` runs CascadeEngine which **reports** unblocked items but does NOT modify their blocked_by fields. Items remain with stale blocked_by references.

**Result:** WORK-169 still has `blocked_by: [WORK-167]` even though WORK-167 is complete. Manual cleanup required.

### Desired State

```python
# justfile:68-72 — close-work recipe with blocked_by cascade
close-work id:
    python .claude/haios/modules/cli.py close {{id}}
    just cascade {{id}} complete
    python .claude/haios/modules/cli.py clear-blocked-by {{id}}
    just update-status
```

**Behavior:** After cascade reporting, a new `clear-blocked-by` command removes the closed ID from all downstream WORK.md blocked_by fields. Failures are logged but never block closure.

**Result:** WORK-169's blocked_by is automatically cleared to `[]` when WORK-167 closes.

---

## Tests First (TDD)

### Test 1: Clears single blocked_by reference
```python
def test_clear_blocked_by_removes_reference(tmp_path):
    """When WORK-A closes, WORK-B's blocked_by: [WORK-A] becomes blocked_by: []"""
    # Setup: WORK-B with blocked_by: [WORK-A]
    # Action: clear_blocked_by("WORK-A", base_path=tmp_path)
    # Assert: WORK-B frontmatter blocked_by == []
```

### Test 2: Clears from multi-item blocked_by list
```python
def test_clear_blocked_by_preserves_other_blockers(tmp_path):
    """When WORK-A closes, WORK-C's blocked_by: [WORK-A, WORK-B] becomes [WORK-B]"""
    # Setup: WORK-C with blocked_by: [WORK-A, WORK-B]
    # Action: clear_blocked_by("WORK-A", base_path=tmp_path)
    # Assert: WORK-C frontmatter blocked_by == ["WORK-B"]
```

### Test 3: No-op when no references exist
```python
def test_clear_blocked_by_noop_when_not_referenced(tmp_path):
    """When WORK-X closes but nothing references it, returns empty list"""
    # Setup: WORK-D with blocked_by: [WORK-Z] (not WORK-X)
    # Action: clear_blocked_by("WORK-X", base_path=tmp_path)
    # Assert: result.cleared == [], WORK-D unchanged
```

### Test 4: Fail-permissive on corrupt file
```python
def test_clear_blocked_by_skips_corrupt_file(tmp_path):
    """Corrupt WORK.md is skipped, not crash — fail-permissive"""
    # Setup: one valid WORK.md with blocked_by ref, one corrupt file
    # Action: clear_blocked_by("WORK-A", base_path=tmp_path)
    # Assert: valid file updated, corrupt file skipped, no exception
```

### Test 5: Logs warning event on failure
```python
def test_clear_blocked_by_logs_warning_on_failure(tmp_path):
    """When cascade encounters an error, it logs a warning event"""
    # Setup: WORK.md with blocked_by ref but read-only (or simulate error)
    # Action: clear_blocked_by("WORK-A", base_path=tmp_path)
    # Assert: governance-events.jsonl contains BlockedByCascadeWarning event
```

### Test 6: Handles YAML list format (block style)
```python
def test_clear_blocked_by_handles_yaml_list_format(tmp_path):
    """blocked_by in YAML block style (- WORK-A on separate line) is handled"""
    # Setup: WORK.md with blocked_by in block style (- WORK-A\n- WORK-B)
    # Action: clear_blocked_by("WORK-A", base_path=tmp_path)
    # Assert: blocked_by is [WORK-B] after round-trip via yaml.safe_load
    # MUST verify parsed type is list, not string (catches A6 bug)
```

### Test 7: CLI dispatch returns 0 even on error
```python
def test_cmd_clear_blocked_by_returns_zero(tmp_path, monkeypatch):
    """CLI entry point always returns 0 (fail-permissive for justfile)"""
    # Setup: monkeypatch sys.argv and project paths
    # Action: call cmd_clear_blocked_by("WORK-NONEXISTENT")
    # Assert: return code is 0 (not 1, even for missing items)
```

---

## Detailed Design

<!-- REVISED after critique pass 1: A1 (block-style YAML), A6 (str() bug) -->

### Exact Code Change

**File:** `.claude/haios/lib/blocked_by_cascade.py` (NEW)

```python
"""
Blocked-by cascade on work closure (WORK-173).

When a work item closes, removes its ID from all active WORK.md
blocked_by fields. Fail-permissive: errors log warnings but never
block closure.

Note: This lib function writes directly to WORK.md files, following
the precedent set by cycle_state.py:sync_work_md_phase(). Targeted
field replacement (not full YAML re-serialization) minimizes mutation.
If WorkEngine's L4 invariant is ever code-enforced, this is a known
deviation to address.

Usage:
    from blocked_by_cascade import clear_blocked_by
    result = clear_blocked_by("WORK-101", base_path=Path("."))
    # result = {"cleared": ["WORK-160"], "errors": [], "skipped": []}
"""
import json
import re
import yaml
from datetime import datetime
from pathlib import Path
from typing import List, Optional


def _format_blocked_by(items: List[str]) -> str:
    """Format blocked_by list as YAML flow sequence.

    Uses manual formatting (not str() which produces Python syntax).
    YAML flow: [WORK-A, WORK-B] — no quotes needed for bare scalars.
    Python str(): ['WORK-A', 'WORK-B'] — single quotes break YAML parsing.
    """
    if not items:
        return "[]"
    return "[" + ", ".join(items) + "]"


def _replace_blocked_by_block(content: str, new_value: str) -> str:
    """Replace the entire blocked_by field in WORK.md content.

    Handles both YAML formats found in production files:
      Flow:  blocked_by: [WORK-A, WORK-B]      (single line)
      Block: blocked_by:\\n- WORK-A\\n- WORK-B  (multi-line)

    Uses line-scanning to find the block boundary, then replaces
    the entire range with a single flow-style line.
    """
    lines = content.split("\n")
    start_idx = None
    end_idx = None

    for i, line in enumerate(lines):
        if start_idx is None:
            if re.match(r"^blocked_by:", line):
                start_idx = i
                if re.match(r"^blocked_by:\s*\[", line):
                    end_idx = i + 1  # Flow style: single line
                    break
                # Block style: continue scanning for "- " lines
                continue
        else:
            if re.match(r"^[\s]*-\s", line):
                end_idx = i + 1  # Extend block through list items
            else:
                if end_idx is None:
                    end_idx = start_idx + 1  # Empty block
                break

    if start_idx is None:
        return content
    if end_idx is None:
        end_idx = start_idx + 1

    lines[start_idx:end_idx] = [f"blocked_by: {new_value}"]
    return "\n".join(lines)


def clear_blocked_by(
    closed_id: str,
    base_path: Optional[Path] = None,
    events_file: Optional[Path] = None,
) -> dict:
    """Remove closed_id from blocked_by in all active WORK.md files.

    Reads blocked_by via yaml.safe_load (reliable for both flow and block
    styles), then writes back using targeted line replacement (avoids full
    YAML re-serialization which corrupts multiline strings and quoting).

    Args:
        closed_id: The work item ID being closed (e.g., "WORK-101")
        base_path: Project root. Defaults to 4 levels up from __file__.
        events_file: Governance events file. Defaults to standard location.

    Returns:
        {"cleared": [ids], "errors": [ids], "skipped": [ids]}
    """
    root = base_path or Path(__file__).parent.parent.parent.parent
    events = events_file or (root / ".claude" / "haios" / "governance-events.jsonl")
    active_dir = root / "docs" / "work" / "active"

    cleared = []
    errors = []
    skipped = []

    if not active_dir.exists():
        return {"cleared": cleared, "errors": errors, "skipped": skipped}

    for work_dir in sorted(active_dir.iterdir()):
        if not work_dir.is_dir():
            continue
        work_file = work_dir / "WORK.md"
        if not work_file.exists():
            continue

        try:
            content = work_file.read_text(encoding="utf-8")
            parts = content.split("---", 2)
            if len(parts) < 3:
                skipped.append(work_dir.name)
                continue

            fm = yaml.safe_load(parts[1]) or {}
            blocked_by = fm.get("blocked_by", []) or []

            if closed_id not in blocked_by:
                continue

            # Remove closed_id, format as YAML flow sequence
            new_blocked = [b for b in blocked_by if b != closed_id]
            new_value = _format_blocked_by(new_blocked)

            # Replace entire blocked_by block (handles flow + block style)
            updated = _replace_blocked_by_block(content, new_value)
            work_file.write_text(updated, encoding="utf-8")

            cleared.append(fm.get("id", work_dir.name))

        except Exception as exc:
            item_id = work_dir.name
            errors.append(item_id)
            _log_warning(events, closed_id, item_id, str(exc))

    return {"cleared": cleared, "errors": errors, "skipped": skipped}


def _log_warning(events_file: Path, closed_id: str, failed_id: str, error: str) -> None:
    """Log a warning event for cascade failure (fail-permissive observability)."""
    try:
        event = {
            "type": "BlockedByCascadeWarning",
            "closed_id": closed_id,
            "failed_id": failed_id,
            "error": error,
            "timestamp": datetime.now().isoformat(),
        }
        events_file.parent.mkdir(parents=True, exist_ok=True)
        with open(events_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")
    except Exception:
        pass  # Even logging failure is fail-permissive
```

**Design decisions addressing critique findings:**

1. **A1 (block-style YAML):** `_replace_blocked_by_block()` uses line-scanning to detect both flow-style and block-style formats. Scans forward through `- ` continuation lines to find block boundary. Entire range replaced with single flow-style line. No orphaned list items.

2. **A6 (Python str() bug):** `_format_blocked_by()` produces correct YAML flow syntax: `[WORK-A, WORK-B]` (no quotes). Never uses `str()` on a Python list.

3. **A4 (L4 invariant):** Module docstring acknowledges deviation, cites cycle_state.py precedent.

4. **No full YAML re-serialization.** Read via `yaml.safe_load`, write via targeted line replacement.

### Call Chain Context

```
just close-work {id}
    |
    +-> cli.py close {id}           # WorkEngine.close() — status/date
    +-> just cascade {id} complete  # CascadeEngine — reports unblocked
    +-> cli.py clear-blocked-by {id}  # NEW — clears blocked_by refs
    +-> just update-status          # Refresh status JSON
```

### Function/Component Signatures

```python
def clear_blocked_by(
    closed_id: str,
    base_path: Optional[Path] = None,
    events_file: Optional[Path] = None,
) -> dict:
    """Remove closed_id from blocked_by in all active WORK.md files.

    Fail-permissive: errors are logged to governance-events.jsonl but
    never raise exceptions or block the calling close-work recipe.

    Args:
        closed_id: Work item ID being closed (e.g., "WORK-101")
        base_path: Project root (injectable for testing)
        events_file: Governance events file (injectable for testing)

    Returns:
        {"cleared": [str], "errors": [str], "skipped": [str]}
    """
```

```python
def cmd_clear_blocked_by(work_id: str) -> int:
    """CLI entry point for blocked_by cascade."""
    # In modules/cli.py
```

### Behavior Logic

**Current Flow:**
```
close-work {id} → cli close → cascade (report only) → update-status
                                                        ↑
                            blocked_by refs remain stale ─┘
```

**Fixed Flow:**
```
close-work {id} → cli close → cascade (report) → clear-blocked-by → update-status
                                                        |
                                      for each active WORK.md:
                                        ├─ has closed_id in blocked_by?
                                        │   ├─ YES → remove via regex, log cleared
                                        │   └─ NO  → skip
                                        ├─ parse error?
                                        │   └─ log warning, continue (fail-permissive)
                                        └─ return {cleared, errors, skipped}
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Separate lib function (not extend status_propagator) | New `blocked_by_cascade.py` | Critique A1 (work item): status_propagator handles chapter/arc cascade, not WORK.md field mutation. Separate concerns. |
| Line-scanning (not single-line regex or full YAML dump) | `_replace_blocked_by_block()` | Critique A1 (plan): block-style YAML is dominant in production. Single-line regex leaves orphaned `- WORK-X` lines. Full yaml.dump corrupts file. Line-scanning handles both formats. |
| YAML flow formatting (not Python str()) | `_format_blocked_by()` | Critique A6: `str(["WORK-B"])` produces `['WORK-B']` (Python syntax, single quotes). YAML reads this as a string, not list. Manual formatting produces `[WORK-B]` (valid YAML flow). |
| yaml.safe_load for reading, line-scan for writing | Hybrid approach | Reading needs reliable list parsing (handles both YAML styles). Writing needs minimal file mutation (no re-serialization). |
| CLI command in modules/cli.py | `cmd_clear_blocked_by` | Follows existing pattern (cmd_close, cmd_cascade). Called from justfile. |
| cmd_clear_blocked_by always returns 0 | Fail-permissive exit code | Critique A3: non-zero exit would abort justfile recipe, preventing `just update-status`. All exceptions caught, return 0 always. |
| Fail-permissive with warning events | Log to governance-events.jsonl | Critique A5 (work item): silent failure defeats purpose. Warning events provide observability without blocking closure. |
| D2 satisfied by WorkEngine.close() | No new close_work_item() lib function | Critique A2: WorkEngine.close() already sets status=complete and closed={date}. AC wording is historical. No duplication needed. |
| Flow-style output for blocked_by | `blocked_by: [WORK-B, WORK-C]` | Normalizes output to single format. Production files have both styles; output is always flow for simplicity. |

### Input/Output Examples

**Before (real data — WORK-169):**
```yaml
# docs/work/active/WORK-169/WORK.md
blocked_by:
  - WORK-167
```
WORK-167 is complete. WORK-169 is stuck because blocked_by was never cleared.

**After (expected):**
```yaml
# docs/work/active/WORK-169/WORK.md
blocked_by: []
```
After `clear_blocked_by("WORK-167")`, the reference is removed.

**Multi-blocker example (real data — WORK-113):**
```yaml
blocked_by:
  - WORK-111
  - WORK-112
```
After `clear_blocked_by("WORK-111")`:
```yaml
blocked_by: [WORK-112]
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Empty blocked_by | Skip (no match) | Test 3 |
| Corrupt WORK.md (no frontmatter) | Skip, log to skipped | Test 4 |
| File write error | Log warning event, continue | Test 5 |
| blocked_by in YAML block style | Regex handles both flow and block style (matches `^blocked_by:.*$` which covers flow; block style is multi-line) | Test 6 |
| blocked_by with mixed ID formats (WORK-xxx, E2-xxx) | Works — string matching is format-agnostic | Covered by Test 1 |

**Block-style YAML edge case detail:**
If blocked_by is in block style:
```yaml
blocked_by:
  - WORK-A
  - WORK-B
```
The regex `^blocked_by:.*$` matches only the first line `blocked_by:` (empty after colon). We need to handle this by reading via yaml.safe_load and then replacing the entire blocked_by block. The implementation will:
1. Read blocked_by via yaml.safe_load (handles both formats)
2. Find the blocked_by field start line
3. Detect if it's flow style (single line) or block style (multi-line)
4. Replace accordingly

### Open Questions

**Q: Should we backfill existing stale blocked_by refs (e.g., WORK-169)?**
No — this is a forward-looking cascade. Backfill is a separate housekeeping task. The function can be called manually for backfill if desired: `clear_blocked_by("WORK-167")`.

---

## Open Decisions (MUST resolve before implementation)

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| None | - | - | All decisions resolved during design |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Create `tests/test_blocked_by_cascade.py` with 7 tests
- [ ] Verify all tests fail (red) — import error since module doesn't exist yet

### Step 2: Implement clear_blocked_by lib function
- [ ] Create `.claude/haios/lib/blocked_by_cascade.py`
- [ ] Implement `clear_blocked_by()` with targeted regex approach
- [ ] Implement `_log_warning()` for fail-permissive event logging
- [ ] Tests 1-7 pass (green)

### Step 3: Add CLI command
- [ ] Add `cmd_clear_blocked_by(work_id)` to `.claude/haios/modules/cli.py`
- [ ] Add dispatch entry in cli.py's main dispatch

### Step 4: Integrate into justfile
- [ ] Add `clear-blocked-by` line to `close-work` recipe in `justfile`

### Step 5: Update close-work-cycle SKILL.md
- [ ] Add blocked_by cascade step to ARCHIVE phase documentation

### Step 6: Integration Verification
- [ ] All tests pass
- [ ] Run full test suite (no regressions)
- [ ] Demo: manually call `clear_blocked_by("WORK-167")` to fix live WORK-169

### Step 7: README Sync (MUST)
- [ ] Update `.claude/haios/lib/README.md` with new module
- [ ] Verify README content matches actual file state

### Step 8: Consumer Verification
- [ ] Grep for `blocked_by` references to confirm no stale patterns
- [ ] Verify justfile close-work recipe includes new step

---

## Verification

- [ ] Tests pass (7 tests)
- [ ] Full test suite — no regressions
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| YAML block-style blocked_by not handled by regex | Medium | Test 6 covers this; implementation detects and handles both formats |
| Full YAML re-serialization corrupts files | High | Avoided by design — using targeted regex, not yaml.dump |
| Cascade failure blocks work closure | High | Fail-permissive pattern — all exceptions caught, warnings logged |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 406 | 2026-02-19 | - | Plan authored | - |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

**MUST** read `docs/work/active/WORK-173/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| blocked_by cascade function in lib/ (fail-permissive) | [ ] | Read lib/blocked_by_cascade.py |
| close_work_item(work_id) lib function: sets status/closed fields | [ ] | Note: This is already done by WorkEngine.close() — verify AC is satisfied |
| Integration into close-work recipe or status_propagator | [ ] | Read justfile close-work recipe |
| Tests verifying cascade clears references | [ ] | pytest output |
| Tests verifying close_work_item writes status | [ ] | Already covered by existing WorkEngine tests |
| close-work-cycle SKILL.md updated to reference lib/ functions | [ ] | Read SKILL.md ARCHIVE phase |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/blocked_by_cascade.py` | clear_blocked_by() + _log_warning() | [ ] | |
| `tests/test_blocked_by_cascade.py` | 6 tests, all passing | [ ] | |
| `.claude/haios/modules/cli.py` | cmd_clear_blocked_by added | [ ] | |
| `justfile` | close-work includes clear-blocked-by | [ ] | |
| `.claude/skills/close-work-cycle/SKILL.md` | ARCHIVE phase references cascade | [ ] | |
| `.claude/haios/lib/README.md` | blocked_by_cascade.py documented | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_blocked_by_cascade.py -v
# Expected: 7 tests passed
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
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] **Runtime consumer exists** (justfile close-work calls clear-blocked-by)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- @.claude/haios/lib/status_propagator.py (pattern template — fail-permissive, injectable)
- @.claude/haios/lib/cycle_state.py (sync_work_md_phase — targeted regex pattern)
- @.claude/haios/modules/cascade_engine.py (existing cascade — reports but doesn't modify)
- @.claude/haios/modules/cli.py (CLI dispatch pattern)
- @.claude/skills/close-work-cycle/SKILL.md (consumer: ARCHIVE phase)
- Memory: 86603, 86632, 86643, 86666, 86680 (5+ convergent retro entries)

---
