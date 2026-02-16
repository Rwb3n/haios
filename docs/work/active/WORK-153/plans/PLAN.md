---
template: implementation_plan
status: complete
date: 2026-02-16
backlog_id: WORK-153
title: "E2.7 Bug Batch: Ceremony Stubs, Doc Drift, Code Duplication"
author: Hephaestus
lifecycle_phase: plan
session: 384
version: "1.5"
generated: 2026-02-16
last_updated: 2026-02-16T19:21:58
---
# Implementation Plan: E2.7 Bug Batch: Ceremony Stubs, Doc Drift, Code Duplication

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

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

Resolve 6 bugs from E2.6 triage: fix doc drift, deduplicate code, update stale counts, and document accepted gaps.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 3 | close.md, observations.py, MEMORY.md |
| Lines of code affected | ~40 | 1 line close.md + ~36 lines observations.py + 1 line MEMORY.md |
| New files to create | 0 | Bug fixes only |
| Tests to write | 1 | _db_query deduplication verification |
| Dependencies | 0 | No downstream imports affected |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Each bug is independent |
| Risk of regression | Low | observations.py CLI __main__ block, not library API |
| External dependencies | Low | No external APIs or services |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Implementation | 15 min | High |
| Verification | 10 min | High |
| **Total** | 25 min | |

---

## Current State vs Desired State

### Bug 1: spawn-work-ceremony stub:true
- **Current:** Already has `stub: true` at SKILL.md:6. No fix needed.
- **Status:** Already resolved.

### Bug 2: close.md MEMORY reference
- **Current:** `.claude/commands/close.md:65` says "VALIDATE -> ARCHIVE -> MEMORY"
- **Desired:** "VALIDATE -> ARCHIVE -> CHAIN" (MEMORY absorbed by retro-cycle COMMIT per WORK-142)

### Bug 3: observations.py _db_query duplication
- **Current:** `observations.py:769-780`, `793-804`, `817-828` — identical `_db_query` function defined 3 times
- **Desired:** Single `_db_query` defined once at top of `__main__` block, referenced by all 3 CLI handlers

### Bug 4: MEMORY.md test counts
- **Current:** "1383 passed, 16 failed, 4 skipped (as of S371)"
- **Desired:** "1360 passed, 9 failed, 4 skipped (as of S384)"

### Bug 5: cycle_phase staleness
- **Current:** cycle_phase stays "backlog" when items skip plan-authoring
- **Root cause:** No cascade engine exists — WORK-034 scope. Document as accepted gap.

### Bug 6: CONCLUDE.md timestamp
- **Current:** Template last_updated stays stale
- **Status:** Already documented as accepted gap (Memory 85449). No fix needed.

---

## Tests First (TDD)

### Test 1: observations.py _db_query defined once in __main__
```python
def test_observations_db_query_not_duplicated():
    """Verify _db_query helper is defined only once in observations.py __main__ block."""
    import re
    from pathlib import Path
    content = Path(".claude/haios/lib/observations.py").read_text()
    # Find __main__ block
    main_block = content[content.index("if __name__"):]
    # Count _db_query definitions
    definitions = re.findall(r"def _db_query\(", main_block)
    assert len(definitions) == 1, f"Expected 1 _db_query def, found {len(definitions)}"
```

### Test 2: Regression — existing tests still pass
- Run `pytest tests/ -q --tb=short` — 1360 passing tests must still pass

---

## Detailed Design

### Bug 2: close.md line 65

**File:** `.claude/commands/close.md:65`

**Diff:**
```diff
-The skill guides through VALIDATE -> ARCHIVE -> MEMORY phases.
+The skill guides through VALIDATE -> ARCHIVE -> CHAIN phases.
```

### Bug 3: observations.py _db_query deduplication

**File:** `.claude/haios/lib/observations.py:768-828`

Extract the 3 identical `_db_query` definitions into a single definition at the top of `__main__`. The function body is identical across all 3 — connects to DB via haios_etl.database.DatabaseManager.

**Current (3 copies at lines 769, 794, 818):**
```python
    elif command == "retro-kss":
        def _db_query(sql):
            ...  # identical body
        entries = query_retro_kss(db_query_fn=_db_query)
```

**Fixed (1 definition, 3 references):**
```python
    # Define shared DB query helper for retro commands
    def _db_query(sql):
        try:
            from haios_etl.database import DatabaseManager
            db = DatabaseManager()
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute(sql)
            columns = [desc[0] for desc in cursor.description]
            rows = cursor.fetchall()
            return {"columns": columns, "rows": [list(r) for r in rows]}
        except Exception as e:
            return {"error": str(e)}

    elif command == "retro-kss":
        entries = query_retro_kss(db_query_fn=_db_query)
        ...
```

Place the single `_db_query` definition after the `command = sys.argv[1]` line and before the first `elif` that uses it.

### Bug 4: MEMORY.md test counts

**File:** MEMORY.md line containing test counts

**Diff:**
```diff
-- Full suite: 1383 passed, 16 failed, 4 skipped (as of S371)
+- Full suite: 1360 passed, 9 failed, 4 skipped (as of S384)
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| _db_query placement | After `command = sys.argv[1]`, before first retro elif | Defined once, in scope for all 3 retro handlers. Avoids conditional nesting. |
| Bug 1 and 6 | No-op, mark resolved | Already fixed/documented. No code change needed. |
| Bug 5 | Document root cause, no code fix | Proper fix requires WORK-034 cascade engine. Premature to patch. |

---

## Open Decisions (MUST resolve before implementation)

**SKIPPED:** No open decisions. All 6 bugs have clear fix/no-fix dispositions from triage evidence.

---

## Implementation Steps

### Step 1: Write test for Bug 3 (RED)
- [ ] Add `test_observations_db_query_not_duplicated` to test file
- [ ] Verify test fails (currently 3 definitions)

### Step 2: Fix Bug 2 — close.md MEMORY reference
- [ ] Edit `.claude/commands/close.md:65` — MEMORY -> CHAIN

### Step 3: Fix Bug 3 — deduplicate _db_query
- [ ] Extract single `_db_query` definition in observations.py `__main__` block
- [ ] Remove 3 inline definitions
- [ ] Test passes (GREEN)

### Step 4: Fix Bug 4 — MEMORY.md test counts
- [ ] Update count line to "1360 passed, 9 failed, 4 skipped (as of S384)"

### Step 5: Document Bug 5 — cycle_phase root cause
- [ ] Add root cause note to WORK-153/WORK.md History section

### Step 6: Verify Bugs 1 and 6 resolved
- [ ] Confirm spawn-work-ceremony has `stub: true`
- [ ] Confirm CONCLUDE.md timestamp is documented as accepted gap

### Step 7: Full regression test
- [ ] Run `pytest tests/ -q --tb=short` — no new failures

### README Sync
**SKIPPED:** No new files created, no structural changes. Bug fixes to existing files only.

---

## Verification

- [ ] Tests pass (new + regression)
- [ ] close.md line 65 reads "CHAIN" not "MEMORY"
- [ ] observations.py has exactly 1 `_db_query` definition in `__main__`
- [ ] MEMORY.md counts match pytest output

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| observations.py CLI broken after dedup | Low | Run CLI help to verify; function body unchanged |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.
> This forces actual verification - not claims, but evidence.

### WORK.md Deliverables Check (MUST - Session 192)

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Fix spawn-work-ceremony stub:true | [ ] | Already present at SKILL.md:6 |
| Fix close.md stale MEMORY reference | [ ] | Read line 65 after edit |
| Deduplicate _db_query in observations.py | [ ] | Test + grep count |
| Update MEMORY.md test failure count | [ ] | Compare with pytest output |
| Document cycle_phase staleness root cause | [ ] | Read WORK.md History |
| All existing tests still pass | [ ] | pytest output |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/commands/close.md` | Line 65: "CHAIN" not "MEMORY" | [ ] | |
| `.claude/haios/lib/observations.py` | 1 _db_query def in __main__ | [ ] | |
| MEMORY.md | Test counts: 1360/9/4 | [ ] | |
| `WORK-153/WORK.md` | Bug 5 root cause documented | [ ] | |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] Tests pass
- [ ] **MUST:** All WORK.md deliverables verified complete (Session 192)
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.
> **E2-290 Learning (Session 192):** "Tests pass" ≠ "Deliverables complete". Agent declared victory after tests passed but skipped 2 of 7 deliverables.

---

## References

- Memory: 85097, 85096, 85131, 85412, 85445, 84943 (bug evidence)
- Memory: 84963 (batch bug pattern validation)
- WORK-034 (status propagation — root cause for Bug 5)
- WORK-142 (retro-cycle absorbed MEMORY phase — context for Bug 2)

---
