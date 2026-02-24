---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-24
backlog_id: WORK-214
title: "Governance Event Log Rotation Per Epoch"
author: Hephaestus
lifecycle_phase: plan
session: 447
generated: 2026-02-24
last_updated: 2026-02-24T21:49:41

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-214/WORK.md"
    required: true
  - field: source_files_exist
    verify: "all paths in WORK.md source_files exist on disk"
    required: true

output_contract:
  - field: layer_0_complete
    verify: "Layer 0 tables have no placeholder rows"
  - field: layer_1_complete
    verify: "Layer 1 has concrete code blocks, not pseudocode"
  - field: layer_2_complete
    verify: "every step has input/action/output/verify fields"
  - field: layer_3_complete
    verify: "every verification line has a command and expected output"
---
# Implementation Plan: Governance Event Log Rotation Per Epoch

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification.

     SKIP RATIONALE: If ANY section is omitted, provide one-line rationale:
     **SKIPPED:** [reason] -->

---

## Goal

Add `archive_governance_events(prior_epoch_dir)` to `lib/governance_events.py` that copies `governance-events.jsonl` to a given epoch directory and truncates the live file to empty, then wire this call into the open-epoch-ceremony SCAFFOLD phase so every epoch transition starts with a fresh log.

---

## Open Decisions

<!-- No operator_decisions in WORK.md frontmatter. Design decisions resolved by operator context in work item body (see WORK-214 Context section and parent WORK-212). -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Archive destination | current epoch dir vs prior epoch dir | prior epoch dir | Events accumulated belong to the just-closed epoch. The prior epoch directory is the natural archive home (e.g., `.claude/haios/epochs/E2_8/governance-events.jsonl`). |
| Archive mechanism | copy+truncate vs move vs rename | copy then truncate | Preserves original filename at rest location; truncate (not delete+create) avoids race window where live writers could append to deleted file handle. |
| Integration point | SCAFFOLD phase vs VALIDATE phase | SCAFFOLD phase | Events rotate before new epoch work begins. SCAFFOLD is the first phase and sets up directory structure — archive fits naturally here after verifying epoch directory exists. |

---

## Layer 0: Inventory

<!-- MUST complete before any design work. Map the blast radius.
     Producer: plan-author agent
     Consumer: all downstream agents (DO, CHECK, critique) -->

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/haios/lib/governance_events.py` | MODIFY | 2 |
| `.claude/skills/open-epoch-ceremony/SKILL.md` | MODIFY | 2 |

### Consumer Files

<!-- Files that reference primary files and need updating. -->

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `.claude/haios/lib/README.md` | Module table entry for `governance_events.py` | 90 | UPDATE — add archive function to description |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_governance_events.py` | UPDATE | Add `TestArchiveGovernanceEvents` class with 4 test methods |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 0 | No new files |
| Files to modify | 3 | governance_events.py, open-epoch-ceremony SKILL.md, README.md |
| Tests to write | 6 | TestArchiveGovernanceEvents class (copy, truncate, missing file, missing dir, idempotency guard, 0-byte source) |
| Total blast radius | 4 | 3 modified + 1 test file updated |

---

## Layer 1: Specification

<!-- The contract that the DO agent implements. -->

### Current State

```python
# .claude/haios/lib/governance_events.py — end of file (line 503)
# No archive function exists. EVENTS_FILE is a module-level constant:

EVENTS_FILE = Path(__file__).parent.parent / "governance-events.jsonl"
# resolves to: .claude/haios/governance-events.jsonl

# The file is append-only. read_events() reads all lines every time.
# No rotation, no epoch scoping. File is currently 16,418 lines / 2.6MB.
```

**Behavior:** `governance-events.jsonl` grows unbounded across all epochs. Every call to `read_events()` loads the full file. No way to scope analysis to a single epoch without timestamp filtering.

**Problem:** File will reach 10MB+ by E3. Signal-to-noise degrades as cross-epoch events accumulate. No mechanism to archive on epoch transition.

```
# .claude/skills/open-epoch-ceremony/SKILL.md — SCAFFOLD phase (lines 79-109)
# SCAFFOLD creates epoch directory structure but does NOT call any archive function.
# Side effects list (frontmatter line 37):
#   - "Log OpenEpoch event to governance-events.jsonl"
# No mention of rotating governance-events.jsonl before opening new epoch.
```

**Behavior:** open-epoch-ceremony creates epoch directory, updates config, triages work items, decomposes arcs. It logs one event to the live file but never archives the prior epoch's events.

### Desired State

```python
# .claude/haios/lib/governance_events.py — new function after _append_event()

def archive_governance_events(prior_epoch_dir: Path) -> dict:
    """
    Archive governance-events.jsonl to prior epoch directory and start fresh.

    Called during open-epoch-ceremony SCAFFOLD phase after verifying the
    prior epoch directory exists. Copies the live events file to the epoch
    archive directory, then truncates the live file to empty so the new
    epoch starts with a clean log.

    Args:
        prior_epoch_dir: Path to the just-closed epoch directory.
                         E.g., Path(".claude/haios/epochs/E2_8")
                         Must exist before calling.

    Returns:
        dict with keys:
          - archived: bool — True if archive was written
          - archive_path: str — absolute path of archive file (or "" if skipped)
          - lines_archived: int — line count in archived file (or 0 if skipped)
          - skipped: bool — True if source missing or idempotency guard triggered

    Raises:
        NotADirectoryError: if prior_epoch_dir does not exist or is not a directory
        PermissionError: if archive write or source truncation fails
    """
    prior_epoch_dir = Path(prior_epoch_dir)
    if not prior_epoch_dir.is_dir():
        raise NotADirectoryError(
            f"archive_governance_events: prior_epoch_dir does not exist: {prior_epoch_dir}"
        )

    # Source file may not exist if system never logged any events
    if not EVENTS_FILE.exists():
        return {
            "archived": False,
            "archive_path": "",
            "lines_archived": 0,
            "skipped": True,
        }

    # Destination: <prior_epoch_dir>/governance-events.jsonl
    archive_path = prior_epoch_dir / "governance-events.jsonl"

    # Read source content once (atomic snapshot)
    source_content = EVENTS_FILE.read_bytes()

    # Idempotency guard (A4): if source is empty but archive already has content,
    # skip overwrite to prevent destroying the only durable copy
    if not source_content and archive_path.exists() and archive_path.stat().st_size > 0:
        return {
            "archived": False,
            "archive_path": "",
            "lines_archived": 0,
            "skipped": True,
        }

    lines_archived = source_content.count(b"\n")

    # Write archive (overwrites if re-run with same content)
    archive_path.write_bytes(source_content)

    # Truncate live file to empty (keep file handle alive for any open appenders)
    EVENTS_FILE.write_text("", encoding="utf-8")

    return {
        "archived": True,
        "archive_path": str(archive_path.resolve()),
        "lines_archived": lines_archived,
        "skipped": False,
    }
```

**Behavior:** Copies the full current `governance-events.jsonl` to `<prior_epoch_dir>/governance-events.jsonl`, then truncates the live file to zero bytes. Returns a result dict suitable for ceremony logging. Idempotent: if source is empty but archive already has content, the write is skipped to prevent overwriting the only durable copy (A4 critique guard).

**Result:** Every epoch transition produces an archived copy scoped to that epoch, and the live log starts fresh.

```markdown
<!-- .claude/skills/open-epoch-ceremony/SKILL.md — SCAFFOLD phase, after step 2 -->

#### 3. Archive prior epoch governance events (WORK-214)

Before any new events are logged for the new epoch, archive the prior epoch's
governance log:

```python
import sys
from pathlib import Path
_root = Path(".").resolve()
sys.path.insert(0, str(_root / ".claude/haios/lib"))
from governance_events import archive_governance_events

prior_epoch_dir = _root / ".claude/haios/epochs/{prior_epoch_dir_name}"
result = archive_governance_events(prior_epoch_dir)
if result["archived"]:
    print(f"Archived {result['lines_archived']} events to {result['archive_path']}")
elif result["skipped"]:
    print("governance-events.jsonl empty or missing — skipped archive")
```

Replace `{prior_epoch_dir_name}` with the actual prior epoch directory (e.g., `E2_8`).

**Exit Criteria addition:**
- [ ] governance-events.jsonl archived to prior epoch directory
- [ ] Live governance-events.jsonl is empty (0 bytes or 0 lines)
```

### Tests

<!-- Write test specs BEFORE implementation code. -->

**Fixture note (A6 critique):** All tests in `TestArchiveGovernanceEvents` MUST use `monkeypatch.setattr(governance_events, "EVENTS_FILE", tmp_path / "governance-events.jsonl")` to patch the module-level constant. Do NOT use `with patch(...)` at the wrong scope — use monkeypatch or the existing fixture pattern in the test file to guarantee module-level patching.

#### Test 1: Archive Copies File to Epoch Directory
- **file:** `tests/test_governance_events.py`
- **function:** `test_archive_governance_events_copies_to_epoch_dir(tmp_path, monkeypatch)`
- **setup:**
  - Create `tmp_path / "governance-events.jsonl"` with 3 JSON lines
  - Create `tmp_path / "epochs" / "E2_8"` directory
  - `monkeypatch.setattr(governance_events, "EVENTS_FILE", tmp_path / "governance-events.jsonl")`
- **assertion:**
  - Call `archive_governance_events(tmp_path / "epochs" / "E2_8")`
  - Assert `(tmp_path / "epochs" / "E2_8" / "governance-events.jsonl").exists()` is True
  - Assert archive file content equals original 3-line content
  - Assert `result["archived"]` is True
  - Assert `result["lines_archived"]` == 3

#### Test 2: Archive Truncates Live File
- **file:** `tests/test_governance_events.py`
- **function:** `test_archive_governance_events_truncates_live_file(tmp_path, monkeypatch)`
- **setup:**
  - Create `tmp_path / "governance-events.jsonl"` with 3 JSON lines (non-empty)
  - Create `tmp_path / "epochs" / "E2_8"` directory
  - `monkeypatch.setattr(governance_events, "EVENTS_FILE", tmp_path / "governance-events.jsonl")`
- **assertion:**
  - Call `archive_governance_events(tmp_path / "epochs" / "E2_8")`
  - Assert live events file (`tmp_path / "governance-events.jsonl"`) exists
  - Assert live events file size is 0 bytes (truncated to empty)

#### Test 3: Archive Returns Skipped When Source Missing
- **file:** `tests/test_governance_events.py`
- **function:** `test_archive_governance_events_skips_when_source_missing(tmp_path, monkeypatch)`
- **setup:**
  - Do NOT create the events file (source does not exist)
  - Create `tmp_path / "epochs" / "E2_8"` directory
  - `monkeypatch.setattr(governance_events, "EVENTS_FILE", tmp_path / "governance-events.jsonl")`
- **assertion:**
  - Call `archive_governance_events(tmp_path / "epochs" / "E2_8")`
  - Assert `result["skipped"]` is True
  - Assert `result["archived"]` is False
  - Assert `result["lines_archived"]` == 0
  - Assert no archive file was created in epoch dir

#### Test 4: Archive Raises NotADirectoryError for Missing Epoch Dir
- **file:** `tests/test_governance_events.py`
- **function:** `test_archive_governance_events_raises_for_missing_epoch_dir(tmp_path, monkeypatch)`
- **setup:**
  - Create `tmp_path / "governance-events.jsonl"` with 1 JSON line
  - Do NOT create the epoch directory
  - `monkeypatch.setattr(governance_events, "EVENTS_FILE", tmp_path / "governance-events.jsonl")`
- **assertion:**
  - Call `archive_governance_events(tmp_path / "nonexistent_epoch")` inside `pytest.raises(NotADirectoryError)`
  - Assert exception message contains "prior_epoch_dir does not exist"

#### Test 5: Idempotency Guard — Second Call Does Not Overwrite Non-Empty Archive
- **file:** `tests/test_governance_events.py`
- **function:** `test_archive_governance_events_idempotency_guard(tmp_path, monkeypatch)`
- **setup:**
  - Create `tmp_path / "governance-events.jsonl"` with 3 JSON lines
  - Create `tmp_path / "epochs" / "E2_8"` directory
  - `monkeypatch.setattr(governance_events, "EVENTS_FILE", tmp_path / "governance-events.jsonl")`
  - Call `archive_governance_events(tmp_path / "epochs" / "E2_8")` — first call (archives + truncates)
- **assertion:**
  - Call `archive_governance_events(tmp_path / "epochs" / "E2_8")` — second call
  - Assert `result["skipped"]` is True (source empty, archive non-empty)
  - Assert `result["archived"]` is False
  - Assert archive file still contains original 3-line content (not overwritten with empty)

#### Test 6: Zero-Byte Source File — Archives Empty File
- **file:** `tests/test_governance_events.py`
- **function:** `test_archive_governance_events_empty_source_archives(tmp_path, monkeypatch)`
- **setup:**
  - Create `tmp_path / "governance-events.jsonl"` as 0-byte file (`write_text("")`)
  - Create `tmp_path / "epochs" / "E2_8"` directory (no pre-existing archive)
  - `monkeypatch.setattr(governance_events, "EVENTS_FILE", tmp_path / "governance-events.jsonl")`
- **assertion:**
  - Call `archive_governance_events(tmp_path / "epochs" / "E2_8")`
  - Assert `result["archived"]` is True (file exists, even though empty — idempotency guard does NOT fire because no pre-existing archive with content)
  - Assert `result["lines_archived"]` == 0
  - Assert archive file exists and is 0 bytes

### Design

#### File 1 (MODIFY): `.claude/haios/lib/governance_events.py`

**Location:** After `_append_event()` function (line 489), before `_check_repeated_failure()` (line 492).

**Current Code (lines 484-490):**
```python
def _append_event(event: dict) -> None:
    """Append event to JSONL file, injecting session_id."""
    event["session_id"] = _read_session_id()
    EVENTS_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EVENTS_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(event) + "\n")


def _check_repeated_failure(gate: str, work_id: str) -> None:
```

**Target Code — insert after line 490 (blank line after `_append_event`):**
```python
def archive_governance_events(prior_epoch_dir: Path) -> dict:
    """
    Archive governance-events.jsonl to prior epoch directory and start fresh.

    Called during open-epoch-ceremony SCAFFOLD phase after verifying the
    prior epoch directory exists. Copies the live events file to the epoch
    archive directory, then truncates the live file to empty so the new
    epoch starts with a clean log.

    Idempotency: if source is empty but archive already has content, the
    write is skipped to prevent overwriting the only durable copy (A4).

    Args:
        prior_epoch_dir: Path to the just-closed epoch directory.
                         E.g., Path(".claude/haios/epochs/E2_8")
                         Must exist before calling.

    Returns:
        dict with keys:
          - archived: bool — True if archive was written
          - archive_path: str — absolute path of archive file (or "" if skipped)
          - lines_archived: int — count of newline characters in archived file (or 0)
          - skipped: bool — True if source missing or idempotency guard triggered

    Raises:
        NotADirectoryError: if prior_epoch_dir does not exist or is not a directory
    """
    prior_epoch_dir = Path(prior_epoch_dir)
    if not prior_epoch_dir.is_dir():
        raise NotADirectoryError(
            f"archive_governance_events: prior_epoch_dir does not exist: {prior_epoch_dir}"
        )

    # Source file may not exist if system never logged any events
    if not EVENTS_FILE.exists():
        return {
            "archived": False,
            "archive_path": "",
            "lines_archived": 0,
            "skipped": True,
        }

    # Destination: <prior_epoch_dir>/governance-events.jsonl
    archive_path = prior_epoch_dir / "governance-events.jsonl"

    # Read source content once (atomic snapshot)
    source_content = EVENTS_FILE.read_bytes()

    # Idempotency guard (A4): if source is empty but archive already has content,
    # skip overwrite to prevent destroying the only durable copy
    if not source_content and archive_path.exists() and archive_path.stat().st_size > 0:
        return {
            "archived": False,
            "archive_path": "",
            "lines_archived": 0,
            "skipped": True,
        }

    lines_archived = source_content.count(b"\n")

    # Write archive (overwrites if re-run with same content)
    archive_path.write_bytes(source_content)

    # Truncate live file to empty (keep file handle; write empty string)
    EVENTS_FILE.write_text("", encoding="utf-8")

    return {
        "archived": True,
        "archive_path": str(archive_path.resolve()),
        "lines_archived": lines_archived,
        "skipped": False,
    }
```

 def _check_repeated_failure(gate: str, work_id: str) -> None:

#### File 2 (MODIFY): `.claude/skills/open-epoch-ceremony/SKILL.md`

**Location:** SCAFFOLD phase Actions section (lines 82-95), after step 2 (create subdirectories).

**Current Code (lines 82-95):**
```markdown
**Actions:**
1. Create epoch directory: `.claude/haios/epochs/E{X}_{Y}/`
2. Create subdirectories:
   - `arcs/` — arc definitions (populated in DECOMPOSE)
   - `architecture/` — architecture docs (may carry forward)
   - `observations/` — session observations
3. If EPOCH.md doesn't exist, scaffold it:
```

**Target Code — insert step 3 (archive) after step 2, renumber subsequent steps:**
```markdown
**Actions:**
1. Create epoch directory: `.claude/haios/epochs/E{X}_{Y}/`
2. Create subdirectories:
   - `arcs/` — arc definitions (populated in DECOMPOSE)
   - `architecture/` — architecture docs (may carry forward)
   - `observations/` — session observations
3. Archive prior epoch governance events (WORK-214):
   ```python
   import sys
   from pathlib import Path
   _root = Path(".").resolve()
   sys.path.insert(0, str(_root / ".claude/haios/lib"))
   from governance_events import archive_governance_events

   prior_epoch_dir = _root / ".claude/haios/epochs/{prior_epoch_dir_name}"
   result = archive_governance_events(prior_epoch_dir)
   if result["archived"]:
       print(f"Archived {result['lines_archived']} events to {result['archive_path']}")
   elif result["skipped"]:
       print("governance-events.jsonl empty or missing — skipped archive")
   ```
   Replace `{prior_epoch_dir_name}` with the actual prior epoch directory (e.g., `E2_8`).
4. If EPOCH.md doesn't exist, scaffold it:
```

**Exit Criteria addition (append to SCAFFOLD Exit Criteria list):**
```markdown
- [ ] governance-events.jsonl archived to prior epoch directory (or skipped if source missing)
- [ ] Live governance-events.jsonl is empty (new epoch starts clean)
```

**Side effects addition (frontmatter):**
Add to `side_effects` list:
```yaml
  - "Archive prior-epoch governance-events.jsonl to epoch directory"
  - "Truncate live governance-events.jsonl to empty for new epoch"
```

#### File 3 (MODIFY): `.claude/haios/lib/README.md`

**Location:** Module table row for `governance_events.py` (line 90).

**Current:**
```
| `governance_events.py` | Governance event logging |
```

**Target:**
```
| `governance_events.py` | Governance event logging and epoch log rotation. `archive_governance_events(prior_epoch_dir)` copies live log to epoch directory and truncates for new epoch (WORK-214). |
```

### Call Chain

```
open-epoch-ceremony SKILL.md (SCAFFOLD phase, step 3)
    |
    +-> archive_governance_events(prior_epoch_dir)    # NEW — governance_events.py
    |       Reads: EVENTS_FILE (.claude/haios/governance-events.jsonl)
    |       Writes: <prior_epoch_dir>/governance-events.jsonl
    |       Truncates: EVENTS_FILE to empty
    |       Returns: dict {archived, archive_path, lines_archived, skipped}
    |
    +-> [continues to step 4: scaffold EPOCH.md]
    |
    +-> [VALIDATE phase, step 4]
    |
    +-> log OpenEpoch event to governance-events.jsonl (now fresh file)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Function lives in `lib/governance_events.py` | Extend existing module | All event I/O is already in this module. `EVENTS_FILE` constant is defined here — archive logic has natural access without import gymnastics. Alternative (new `log_rotation.py`) would split tightly coupled logic. |
| Archive to prior epoch directory | `<prior_epoch_dir>/governance-events.jsonl` | Events accumulated belong to the just-closed epoch. Epoch directories already exist as long-lived archives. Discoverable by anyone navigating epoch history. Alternative (archive/ subdir in haios/) would require new directory convention. |
| Copy-then-truncate vs rename/move | Copy bytes, then `write_text("")` | Rename would break the module-level `EVENTS_FILE` constant that open file handles and other callers use. Copy-then-truncate keeps the inode stable. Any append in progress between copy and truncate loses at most one event — acceptable for this low-frequency ceremony. |
| Return dict, not bool | `dict {archived, archive_path, lines_archived, skipped}` | Ceremony skill needs structured output for reporting. Richer than bool, no exception for expected no-op (skipped) case. Follows existing module pattern (all log_* functions return event dict). |
| Integration in SCAFFOLD phase | Before CONFIG, TRIAGE, DECOMPOSE | Archive happens before any new epoch events are written. CONFIG logs nothing. TRIAGE and DECOMPOSE produce governance events that should belong to the new epoch. VALIDATE logs OpenEpoch. Earliest safe integration point is SCAFFOLD step 3. |
| `NotADirectoryError` for bad epoch dir | Raise on missing dir | Missing epoch dir is a programming error (SCAFFOLD should have created it in step 1). Raise rather than skip so caller sees the bug. Missing source file (governance-events.jsonl) returns `skipped: True` — that is an expected no-op. |
| No memory query yielded prior pattern | Document: no prior patterns found | Memory context provided by operator (87845, 88196, 88318) describes the problem space, not a prior implementation. No comparable archive/rotation function exists in the codebase. |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| Source file does not exist (fresh install) | Return `skipped: True`, no-op | Test 3 |
| Prior epoch directory does not exist | Raise `NotADirectoryError` | Test 4 |
| Archive exists + source non-empty (re-run before truncation) | `write_bytes` overwrites archive with same content | Test 1 covers write path |
| Archive exists + source empty (re-run after truncation) | Idempotency guard fires, returns `skipped: True`, archive preserved | Test 5 |
| Events appended between read and truncate | At most 1 event lost; acceptable for ceremony | No test — race window too small to trigger deterministically |
| Epoch dir provided as string not Path | `Path(prior_epoch_dir)` coercion at function entry | Covered by test structure (tmp_path is Path; callers may pass str) |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Archive called before epoch dir created | H — raises NotADirectoryError mid-ceremony | Step ordering: step 1 creates epoch dir, step 3 archives. DO agent must follow step order. |
| Live file truncated before archive written | H — data loss | Implementation reads source into memory first, writes archive, then truncates. No risk unless process killed between write and truncate. |
| Archive overwrites existing file on re-run | L — idempotency guard prevents overwriting non-empty archive with empty source (A4) | Guard returns `skipped: True` if source is empty but archive has content. Test 5 verifies. |
| SKILL.md update breaks ceremony parsing | L — SKILL.md is prose, not machine-parsed by a schema | Read SKILL.md before editing; use exact markdown structure as existing steps. |
| Import path in SKILL.md snippet | M — wrong sys.path means ImportError during ceremony | Snippet uses `.resolve()` for absolute path; matches pattern in governance_layer.py lines 37-39. |

---

## Layer 2: Implementation Steps

<!-- Ordered steps. Each step is a sub-agent delegation unit. -->

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Add `TestArchiveGovernanceEvents` class to `tests/test_governance_events.py` with 6 test methods (copy, truncate, missing source, missing epoch dir, idempotency guard, 0-byte source). Run pytest to confirm all 6 FAIL (function does not exist yet).
- **output:** 6 new failing tests in `tests/test_governance_events.py`
- **verify:** `pytest tests/test_governance_events.py::TestArchiveGovernanceEvents -v 2>&1 | grep -c "FAILED\|ERROR"` equals 6

### Step 2: Implement `archive_governance_events` (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (MODIFY)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Insert `archive_governance_events()` function into `.claude/haios/lib/governance_events.py` after `_append_event()` (after line 490) per Layer 1 Design exact code
- **output:** All 6 tests pass
- **verify:** `pytest tests/test_governance_events.py::TestArchiveGovernanceEvents -v` exits 0, `6 passed` in output

### Step 3: Verify Full Suite Green
- **spec_ref:** Layer 0 > Test Files
- **input:** Step 2 complete
- **action:** Run full test suite to confirm no regressions
- **output:** 0 new failures vs pre-existing baseline
- **verify:** `pytest tests/ -v 2>&1 | tail -5` shows `passed` with 0 failed

### Step 4: Integrate into open-epoch-ceremony SKILL.md
- **spec_ref:** Layer 1 > Design > File 2 (MODIFY)
- **input:** Step 3 complete (function tested and green)
- **action:** Edit `.claude/skills/open-epoch-ceremony/SKILL.md` to add step 3 (archive call) in SCAFFOLD phase Actions, renumber existing step 3 to step 4 and step 4 to step 5. Add Exit Criteria bullets and side_effects entries in frontmatter
- **output:** SKILL.md contains archive step with Python snippet
- **verify:** `grep "archive_governance_events" .claude/skills/open-epoch-ceremony/SKILL.md` returns 1+ match

### Step 5: Update README
- **spec_ref:** Layer 0 > Consumer Files
- **input:** Step 4 complete
- **action:** Update `.claude/haios/lib/README.md` module table row for `governance_events.py` per Layer 1 Design File 3
- **output:** README reflects new archive function
- **verify:** `grep "archive_governance_events" .claude/haios/lib/README.md` returns 1 match

---

## Ground Truth Verification

<!-- Computable verification protocol. -->

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_governance_events.py::TestArchiveGovernanceEvents -v` | 6 passed, 0 failed |
| `pytest tests/ -v 2>&1 \| tail -5` | 0 new failures vs pre-existing baseline |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| Archive function in lib/ | `grep "def archive_governance_events" .claude/haios/lib/governance_events.py` | 1 match |
| open-epoch-ceremony calls archive function | `grep "archive_governance_events" .claude/skills/open-epoch-ceremony/SKILL.md` | 1+ match |
| Fresh governance-events.jsonl after archive | Function contract: `EVENTS_FILE.write_text("", encoding="utf-8")` | Test 2 verifies via `read_events() == []` |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| Function importable from lib | `python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from governance_events import archive_governance_events; print('OK')"` | `OK` printed, exit 0 |
| SKILL.md archive step present | `grep "archive_governance_events" .claude/skills/open-epoch-ceremony/SKILL.md` | 1+ match |
| README updated | `grep "archive_governance_events" .claude/haios/lib/README.md` | 1 match |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 2 verify: 6 passed)
- [ ] All WORK.md deliverables verified (table above)
- [ ] Runtime consumer exists: open-epoch-ceremony SKILL.md calls `archive_governance_events`
- [ ] No stale references (no old function name patterns)
- [ ] READMEs updated (lib/README.md)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- `docs/work/active/WORK-214/WORK.md` — work item (traces_to REQ-OBSERVE-001)
- `docs/work/active/WORK-212/WORK.md` — parent work item (spawned_by)
- `.claude/haios/lib/governance_events.py` — primary source file to modify
- `.claude/skills/open-epoch-ceremony/SKILL.md` — integration point
- Memory 87845: session-scoped event log justified (problem statement)
- Memory 88196: archiving reduces signal-to-noise (motivation)
- Memory 88318: WORK-215 added session_id field (companion work, context)

---
