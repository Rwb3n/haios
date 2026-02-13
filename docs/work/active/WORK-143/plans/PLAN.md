---
template: implementation_plan
status: complete
date: 2026-02-13
backlog_id: WORK-143
title: "Retro-Triage Consumer Update for Memory-Based Provenance Tags"
author: Hephaestus
lifecycle_phase: plan
session: 363
version: "1.5"
generated: 2026-02-13
last_updated: 2026-02-13T19:58:58
---
# Implementation Plan: Retro-Triage Consumer Update for Memory-Based Provenance Tags

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

After this plan is complete, the observation-triage-cycle skill will be able to query memory for retro-cycle outputs by content patterns (KSS directives as type=Directive with KEEP-/STOP-/START- prefixes, bug/feature candidates as type=Critique with BUG/FEATURE prefixes), aggregate K/S/S directive frequency across work items, and surface bug/feature candidates with confidence tags for operator disposition.

**Critique-Driven Revision (A1):** `ingester_ingest` source_path does NOT persist as `source_adr` in DB. Actual data uses type=Directive with `KEEP-N:` content prefixes and type=Critique with `BUG (confidence):` content prefixes. Query strategy revised to content-pattern matching. Follow-up: fix producer pipeline for proper provenance tags.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `.claude/haios/lib/observations.py`, `.claude/skills/observation-triage-cycle/SKILL.md` |
| Lines of code affected | ~100 | New functions in observations.py |
| New files to create | 0 | All changes in existing files |
| Tests to write | 10 | See Tests First section |
| Dependencies | 1 | MCP haios-memory (db_query for SQL reads) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Only observations.py + skill SKILL.md |
| Risk of regression | Low | New functions, existing tests untouched |
| External dependencies | Low | Memory DB read-only queries via db_query MCP tool |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Tests | 20 min | High |
| Implementation | 30 min | High |
| Skill update | 15 min | High |
| **Total** | ~65 min | |

---

## Current State vs Desired State

### Current State

```python
# .claude/haios/lib/observations.py:298-336
def scan_archived_observations(base_path=None):
    """Scan archived work items for untriaged observations."""
    # Scans docs/work/archive/*/observations.md files
    # Filters by triage_status field in frontmatter
    # Returns list of {work_id, path, observations} dicts
```

**Behavior:** Triage cycle scans filesystem for `observations.md` files with `triage_status: pending` in archived work items. It parses markdown checkbox items from those files.

**Result:** Retro-cycle outputs (stored to memory via `ingester_ingest`) land as type=Directive (K/S/S) and type=Critique (bugs/features) with content prefixes like `KEEP-N:`, `BUG (confidence):`. No downstream consumer queries these patterns.

### Desired State

```python
# .claude/haios/lib/observations.py - NEW FUNCTIONS
def query_retro_kss(db_query_fn=None) -> list[dict]:
    """Query memory for K/S/S directive entries."""
    # SELECT id, content FROM concepts WHERE type = 'Directive'
    # AND (content LIKE 'KEEP-%' OR content LIKE 'STOP-%' OR content LIKE 'START-%')

def query_retro_bugs(db_query_fn=None) -> list[dict]:
    """Query memory for bug candidate entries."""
    # SELECT id, content FROM concepts WHERE type = 'Critique'
    # AND content LIKE 'BUG %'

def query_retro_features(db_query_fn=None) -> list[dict]:
    """Query memory for feature candidate entries."""
    # SELECT id, content FROM concepts WHERE type = 'Critique'
    # AND content LIKE 'FEATURE %'

def aggregate_kss_frequency(kss_entries: list[dict]) -> dict:
    """Aggregate K/S/S directives by frequency across entries."""
    # Parse KEEP-N:/STOP-N:/START-N: prefixes from content
    # Count frequency of convergent directives (normalized)
    # Return {keep: [...], stop: [...], start: [...]} ranked by frequency

def surface_bug_candidates(bug_entries: list[dict]) -> list[dict]:
    """Parse BUG (confidence): content into structured candidates."""
    # Extract confidence tag and description
    # Return sorted by confidence (high > medium > low)

def surface_feature_candidates(feature_entries: list[dict]) -> list[dict]:
    """Parse FEATURE (confidence): content into structured candidates."""
    # Extract confidence tag and description
    # Return sorted by confidence
```

**Behavior:** Triage cycle queries memory by content patterns matching retro-cycle LLM-extracted output (Directive type for K/S/S, Critique type for bugs/features), aggregates K/S/S frequency, and surfaces typed candidates.

**Result:** Retro-cycle outputs have a downstream consumer. Content-pattern matching works with current ingestion pipeline. Follow-up work item to fix producer for proper provenance tags.

---

## Tests First (TDD)

<!-- Write tests BEFORE implementation. Each test should have:
     - Descriptive name
     - Setup (if needed)
     - Assertion that defines success -->

### Test 1: Query KSS directives from memory
```python
def test_query_retro_kss_returns_directive_entries():
    def mock_db(sql):
        return {
            "rows": [
                [85109, "KEEP-1: TDD RED-GREEN approach across sessions"],
                [85111, "STOP-1: Leaving unquoted YAML description fields with colons"],
            ],
            "columns": ["id", "content"]
        }
    result = query_retro_kss(db_query_fn=mock_db)
    assert len(result) == 2
    assert result[0]["id"] == 85109
    assert "KEEP-1:" in result[0]["content"]
```

### Test 2: Query bug candidates from memory
```python
def test_query_retro_bugs_returns_critique_entries():
    def mock_db(sql):
        return {
            "rows": [[85097, "BUG (medium): spawn-work-ceremony missing stub: true"]],
            "columns": ["id", "content"]
        }
    result = query_retro_bugs(db_query_fn=mock_db)
    assert len(result) == 1
    assert "BUG" in result[0]["content"]
```

### Test 3: Query feature candidates from memory
```python
def test_query_retro_features_returns_critique_entries():
    def mock_db(sql):
        return {
            "rows": [[85098, "FEATURE (high): WORK-143 triage consumer update"]],
            "columns": ["id", "content"]
        }
    result = query_retro_features(db_query_fn=mock_db)
    assert len(result) == 1
    assert "FEATURE" in result[0]["content"]
```

### Test 4: KSS frequency aggregation ranks by count
```python
def test_aggregate_kss_frequency_ranks_by_count():
    entries = [
        {"id": 1, "content": "KEEP-1: TDD RED-GREEN"},
        {"id": 2, "content": "STOP-1: Hardcoding epochs"},
        {"id": 3, "content": "KEEP-1: TDD RED-GREEN"},  # duplicate from another session
        {"id": 4, "content": "START-1: Scaffold lint"},
    ]
    result = aggregate_kss_frequency(entries)
    assert result["keep"][0]["directive"] == "TDD RED-GREEN"
    assert result["keep"][0]["count"] == 2
    assert len(result["stop"]) == 1
    assert len(result["start"]) == 1
```

### Test 5: KSS aggregation with empty input
```python
def test_aggregate_kss_frequency_empty_input():
    result = aggregate_kss_frequency([])
    assert result == {"keep": [], "stop": [], "start": []}
```

### Test 6: Surface bug candidates parses confidence
```python
def test_surface_bug_candidates_parses_confidence():
    entries = [
        {"id": 1, "content": "BUG (high): YAML parsing breaks on colons"},
        {"id": 2, "content": "BUG (low): minor doc drift in close.md"},
    ]
    result = surface_bug_candidates(entries)
    assert len(result) == 2
    assert result[0]["confidence"] == "high"  # sorted high first
    assert result[1]["confidence"] == "low"
    assert "YAML parsing" in result[0]["description"]
```

### Test 7: Surface feature candidates parses confidence
```python
def test_surface_feature_candidates_parses_confidence():
    entries = [
        {"id": 1, "content": "FEATURE (high): triage consumer update"},
        {"id": 2, "content": "FEATURE (medium): auto-lint scaffold output"},
    ]
    result = surface_feature_candidates(entries)
    assert len(result) == 2
    assert result[0]["confidence"] == "high"
    assert result[1]["confidence"] == "medium"
```

### Test 8: Query functions handle db error gracefully
```python
def test_query_retro_kss_handles_db_error():
    def mock_db(sql):
        return {"error": "no such table: concepts"}
    result = query_retro_kss(db_query_fn=mock_db)
    assert result == []
```

### Test 9: Query functions handle None db_query_fn
```python
def test_query_retro_kss_none_returns_empty():
    result = query_retro_kss(db_query_fn=None)
    assert result == []
```

### Test 10: Backward compatibility - existing scan still works
```python
def test_scan_archived_observations_unchanged(tmp_path):
    """Existing filesystem scan behavior is preserved."""
    work_dir = tmp_path / "docs" / "work" / "archive" / "E2-TEST"
    work_dir.mkdir(parents=True)
    obs_file = work_dir / "observations.md"
    obs_file.write_text("---\ntriage_status: pending\n---\n## Gaps\n- [x] Test gap")
    result = scan_archived_observations(base_path=tmp_path)
    assert len(result) == 1
```

---

## Detailed Design

<!-- REQUIRED: Document HOW the implementation works, not just WHAT it does.
     Future agents should be able to implement from this section alone.
     This section bridges the gap between tests (WHAT) and steps (HOW).

     MUST INCLUDE (per Session 88 enhancement):
     1. Actual current code that will be changed (copy from source)
     2. Exact diff/change to be made
     3. Function signature details with context
     4. Input/output examples with REAL data from the system

     PATTERN VERIFICATION (E2-255 Learning):
     IF creating a new module that imports from siblings:
       - MUST read at least one sibling module for import/error patterns
       - Verify: try/except conditional imports? sys.path manipulation? error types?
       - Use the SAME patterns as existing siblings (consistency > preference)

     IF modifying existing module:
       - Follow existing patterns in that file

     IF creating module with no siblings (new directory):
       - Document chosen patterns in Key Design Decisions with rationale -->

### Exact Code Change

**File:** `.claude/haios/lib/observations.py`
**Location:** After line 473 (end of threshold functions), add new retro-triage section

**Critique Revisions Applied:**
- A1: Query by content patterns (type=Directive + KEEP-/STOP-/START- prefix, type=Critique + BUG/FEATURE prefix), NOT source_adr
- A3: Strip `"- "` list prefix and `KEEP-N:` numbered prefix before parsing KSS
- A4: Add CLI entry points (`retro-kss`, `retro-bugs`, `retro-features`) for runtime invocation
- A6: Dedup is known limitation — identical content returns existing row ID. Mitigated by LLM extraction producing varied phrasing. Follow-up: fix producer pipeline.
- A7: Add JSON string parse guard for db_query_fn returns

**New Code:**
```python
# =============================================================================
# RETRO-TRIAGE FUNCTIONS (WORK-143)
# =============================================================================
# Query retro-cycle outputs from memory by content patterns.
# ingester_ingest stores retro outputs as:
#   - type=Directive, content="KEEP-N: ..." / "STOP-N: ..." / "START-N: ..."
#   - type=Critique, content="BUG (confidence): ..." / "FEATURE (confidence): ..."
# source_adr does NOT contain provenance tags (A1 critique finding).
# Follow-up: fix producer pipeline for proper provenance tags.

import json as _json


def _ensure_parsed(result) -> dict:
    """Ensure db_query result is a parsed dict, not a JSON string (A7)."""
    if isinstance(result, str):
        try:
            return _json.loads(result)
        except (ValueError, TypeError):
            return {"error": result}
    return result


def _rows_to_dicts(rows: list, columns: list) -> list[dict]:
    """Convert DB rows + columns into list of dicts."""
    return [dict(zip(columns, row)) for row in rows]


def query_retro_kss(db_query_fn=None) -> list[dict]:
    """Query memory for K/S/S directive entries (retro-cycle DERIVE output).

    Queries concepts table for type=Directive with KEEP-/STOP-/START- content
    prefixes, which is how ingester_ingest stores retro-kss output after
    LLM extraction.

    Args:
        db_query_fn: Callable(sql) -> {columns, rows} or JSON string.
                     If None, returns empty list.

    Returns:
        List of dicts with id, content keys.
    """
    if db_query_fn is None:
        return []
    result = _ensure_parsed(db_query_fn(
        "SELECT id, content FROM concepts WHERE type = 'Directive' "
        "AND (content LIKE 'KEEP-%' OR content LIKE 'STOP-%' OR content LIKE 'START-%') "
        "ORDER BY id"
    ))
    if "error" in result:
        return []
    return _rows_to_dicts(result["rows"], result["columns"])


def query_retro_bugs(db_query_fn=None) -> list[dict]:
    """Query memory for bug candidate entries (retro-cycle EXTRACT output).

    Queries concepts table for type=Critique with BUG prefix in content.

    Args:
        db_query_fn: Callable(sql) -> {columns, rows} or JSON string.

    Returns:
        List of dicts with id, content keys.
    """
    if db_query_fn is None:
        return []
    result = _ensure_parsed(db_query_fn(
        "SELECT id, content FROM concepts WHERE type = 'Critique' "
        "AND content LIKE 'BUG %' ORDER BY id DESC"
    ))
    if "error" in result:
        return []
    return _rows_to_dicts(result["rows"], result["columns"])


def query_retro_features(db_query_fn=None) -> list[dict]:
    """Query memory for feature candidate entries (retro-cycle EXTRACT output).

    Queries concepts table for type=Critique with FEATURE prefix in content.

    Args:
        db_query_fn: Callable(sql) -> {columns, rows} or JSON string.

    Returns:
        List of dicts with id, content keys.
    """
    if db_query_fn is None:
        return []
    result = _ensure_parsed(db_query_fn(
        "SELECT id, content FROM concepts WHERE type = 'Critique' "
        "AND content LIKE 'FEATURE %' ORDER BY id DESC"
    ))
    if "error" in result:
        return []
    return _rows_to_dicts(result["rows"], result["columns"])


def _normalize_directive(text: str) -> str:
    """Normalize a K/S/S directive for frequency comparison."""
    return re.sub(r'\s+', ' ', text.strip().lower())


def _parse_kss_content(content: str) -> tuple[str, str]:
    """Parse a KSS directive content like 'KEEP-1: TDD RED-GREEN...' into (category, directive).

    Handles formats:
      - 'KEEP-1: directive text'  (numbered, from retro-cycle)
      - 'Keep: directive text'     (unnumbered)
      - '- KEEP-1: directive text' (list-prefixed, A3 fix)

    Returns:
        (category, directive) tuple where category is 'keep'/'stop'/'start',
        or ('', '') if not parseable.
    """
    line = content.strip()
    # Strip list prefix (A3)
    if line.startswith("- "):
        line = line[2:]
    # Match KEEP-N: or Keep: patterns
    match = re.match(r'^(KEEP|STOP|START)(?:-\d+)?:\s*(.+)', line, re.IGNORECASE)
    if match:
        return (match.group(1).lower(), match.group(2).strip())
    return ('', '')


def aggregate_kss_frequency(kss_entries: list[dict]) -> dict:
    """Aggregate K/S/S directives by frequency across entries.

    Each entry is a DB row with 'content' like 'KEEP-1: TDD RED-GREEN'.
    Counts frequency of convergent directives (normalized for comparison),
    returns ranked by count descending.

    Args:
        kss_entries: List from query_retro_kss(). Each has 'id' and 'content'.

    Returns:
        {"keep": [...], "stop": [...], "start": [...]}
        Each item: {"directive": str, "count": int, "memory_ids": list[int]}
    """
    buckets = {"keep": {}, "stop": {}, "start": {}}

    for entry in kss_entries:
        content = entry.get("content", "")
        memory_id = entry.get("id")

        category, directive = _parse_kss_content(content)
        if not category:
            continue

        key = _normalize_directive(directive)
        if key not in buckets[category]:
            buckets[category][key] = {
                "directive": directive,  # preserve first occurrence casing
                "count": 0,
                "memory_ids": []
            }
        buckets[category][key]["count"] += 1
        if memory_id is not None:
            buckets[category][key]["memory_ids"].append(memory_id)

    # Sort each bucket by count descending
    result = {}
    for category, items in buckets.items():
        sorted_items = sorted(items.values(), key=lambda x: x["count"], reverse=True)
        result[category] = sorted_items

    return result


def _parse_bug_feature_content(content: str) -> dict:
    """Parse 'BUG (confidence): description' or 'FEATURE (confidence): description'.

    Real examples from memory:
      - 'BUG (medium): spawn-work-ceremony missing stub: true in frontmatter.'
      - 'FEATURE (high): WORK-143 -- triage consumer update needed.'

    Returns:
        {"type": "bug"|"feature", "confidence": str, "description": str}
        or empty dict if not parseable.
    """
    match = re.match(r'^(BUG|FEATURE)\s*\((\w+)\):\s*(.+)', content.strip(), re.IGNORECASE)
    if match:
        return {
            "type": match.group(1).lower(),
            "confidence": match.group(2).lower(),
            "description": match.group(3).strip()
        }
    return {}


def surface_bug_candidates(bug_entries: list[dict]) -> list[dict]:
    """Parse bug entries into structured candidates sorted by confidence.

    Args:
        bug_entries: List from query_retro_bugs(). Each has 'id' and 'content'.

    Returns:
        List of dicts with type, confidence, description, memory_id.
        Sorted by confidence (high > medium > low).
    """
    confidence_order = {"high": 0, "medium": 1, "low": 2}
    bugs = []
    for entry in bug_entries:
        parsed = _parse_bug_feature_content(entry.get("content", ""))
        if parsed.get("type") == "bug":
            parsed["memory_id"] = entry.get("id")
            bugs.append(parsed)
    bugs.sort(key=lambda x: confidence_order.get(x.get("confidence", "low"), 3))
    return bugs


def surface_feature_candidates(feature_entries: list[dict]) -> list[dict]:
    """Parse feature entries into structured candidates sorted by confidence.

    Args:
        feature_entries: List from query_retro_features(). Each has 'id' and 'content'.

    Returns:
        List of dicts with type, confidence, description, memory_id.
        Sorted by confidence (high > medium > low).
    """
    confidence_order = {"high": 0, "medium": 1, "low": 2}
    features = []
    for entry in feature_entries:
        parsed = _parse_bug_feature_content(entry.get("content", ""))
        if parsed.get("type") == "feature":
            parsed["memory_id"] = entry.get("id")
            features.append(parsed)
    features.sort(key=lambda x: confidence_order.get(x.get("confidence", "low"), 3))
    return features
```

Also update the CLI entry point at the end of `observations.py`:

```python
# Add to if __name__ == "__main__" block:
    elif command == "retro-kss":
        import json as json_mod
        def db_query(sql):
            # Import from haios_etl if available, else stub
            try:
                from haios_etl.database import DatabaseManager
                db = DatabaseManager()
                return db.execute_query(sql)
            except ImportError:
                return {"error": "haios_etl not available"}
        entries = query_retro_kss(db_query_fn=db_query)
        agg = aggregate_kss_frequency(entries)
        for cat in ("keep", "stop", "start"):
            if agg[cat]:
                print(f"\n{cat.upper()}:")
                for item in agg[cat]:
                    print(f"  [{item['count']}x] {item['directive']}")

    elif command == "retro-bugs":
        # Similar pattern for bugs
        entries = query_retro_bugs(db_query_fn=db_query)
        bugs = surface_bug_candidates(entries)
        for bug in bugs:
            print(f"  [{bug['confidence']}] {bug['description']}")

    elif command == "retro-features":
        # Similar pattern for features
        entries = query_retro_features(db_query_fn=db_query)
        features = surface_feature_candidates(entries)
        for feat in features:
            print(f"  [{feat['confidence']}] {feat['description']}")
```

### Call Chain Context

```
observation-triage-cycle SKILL.md (agent instructions)
    |
    +-> SCAN phase: query_retro_kss(db_query_fn)       # NEW - K/S/S directives
    |   +-> query_retro_bugs(db_query_fn)                # NEW - bug candidates
    |   +-> query_retro_features(db_query_fn)             # NEW - feature candidates
    |
    +-> TRIAGE phase: aggregate_kss_frequency(entries)   # NEW - frequency ranking
    |   +-> surface_bug_candidates(entries)                # NEW - parse + sort
    |   +-> surface_feature_candidates(entries)            # NEW - parse + sort
    |
    +-> PROMOTE phase: (existing - spawn:WORK, memory, dismiss, etc.)
    |
    +-> (existing) scan_archived_observations()  # UNCHANGED, backward compat
```

Also CLI entry points:
```
python observations.py retro-kss       → prints aggregated K/S/S with counts
python observations.py retro-bugs      → prints bug candidates with confidence
python observations.py retro-features  → prints feature candidates with confidence
```

### Function/Component Signatures

```python
def query_retro_kss(db_query_fn: Optional[Callable] = None) -> list[dict]:
    """Query type=Directive with KEEP-/STOP-/START- content prefix."""

def query_retro_bugs(db_query_fn: Optional[Callable] = None) -> list[dict]:
    """Query type=Critique with BUG content prefix."""

def query_retro_features(db_query_fn: Optional[Callable] = None) -> list[dict]:
    """Query type=Critique with FEATURE content prefix."""

def aggregate_kss_frequency(kss_entries: list[dict]) -> dict:
    """Aggregate K/S/S directives by frequency. Returns {keep, stop, start} ranked."""

def surface_bug_candidates(bug_entries: list[dict]) -> list[dict]:
    """Parse BUG (confidence): content, sorted by confidence."""

def surface_feature_candidates(feature_entries: list[dict]) -> list[dict]:
    """Parse FEATURE (confidence): content, sorted by confidence."""
```

### Behavior Logic

**Current Flow:**
```
Triage invoked → scan_archived_observations() → filesystem scan → markdown parse → operator triage
```

**New Flow (additive):**
```
Triage invoked → [Source selection?]
                    ├─ Memory: query_retro_*() → aggregate/surface → operator triage
                    └─ Filesystem: scan_archived_observations() → markdown parse → operator triage (unchanged)
```

The skill instructions will guide the agent to query memory FIRST for retro entries, then also run the existing filesystem scan for legacy items. Both feed into the same TRIAGE/PROMOTE phases.

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Content-pattern queries | NOT source_adr queries | A1 critique: source_path not stored in source_adr. LLM extraction produces type=Directive/Critique with structured content prefixes. |
| db_query_fn injection | Functions accept callable | Testable without live DB. Agent passes MCP db_query at runtime. Tests pass mock. |
| Add to observations.py | Not new module | Functions are triage-related, co-locate with existing triage functions. |
| Additive, not replacement | Filesystem scan preserved | Legacy observations.md files still exist in archive. Both sources feed triage. |
| Regex parsing for KSS | `KEEP-N:` / `STOP-N:` / `START-N:` | Matches actual LLM-extracted format (verified: ids 85109-85113). Handles numbered and unnumbered. |
| Regex parsing for bugs/features | `BUG (confidence):` / `FEATURE (confidence):` | Matches actual format (verified: ids 85096-85098). Extracts confidence tag. |
| Normalize for frequency | Case-insensitive, whitespace-collapsed | Independent sessions may phrase same directive differently. |
| Confidence sort order | high > medium > low | High-confidence items surface first for operator attention. |
| CLI entry points | retro-kss, retro-bugs, retro-features | A4 critique: skill agent cannot call Python functions. CLI enables `just retro-triage` recipe. |
| JSON parse guard | _ensure_parsed() | A7 critique: MCP db_query may return JSON string or dict. |

### Input/Output Examples

**Real Example — retro-kss query and aggregation (from actual S362 data):**
```
Memory state:
  concepts table (actual):
    id=85109, type='Directive', content='KEEP-1: TDD RED-GREEN approach across sessions (S361 tests, S362 fixes) — 130/131 first-pass pass rate.'
    id=85110, type='Directive', content='KEEP-2: Layered implementation (L1-L5) with clear dependency ordering'
    id=85111, type='Directive', content='STOP-1: Leaving unquoted YAML description fields with colons'
    id=85112, type='Directive', content='STOP-2: Renumbering phases without grepping for old numbers in test fixtures.'
    id=85113, type='Directive', content='START-1: After any phase renumbering, run grep for old phase number pattern'

After aggregate_kss_frequency():
  {
    "keep": [
      {"directive": "TDD RED-GREEN approach across sessions...", "count": 1, "memory_ids": [85109]},
      {"directive": "Layered implementation (L1-L5)...", "count": 1, "memory_ids": [85110]}
    ],
    "stop": [
      {"directive": "Leaving unquoted YAML description fields...", "count": 1, "memory_ids": [85111]},
      {"directive": "Renumbering phases without grepping...", "count": 1, "memory_ids": [85112]}
    ],
    "start": [
      {"directive": "After any phase renumbering, run grep...", "count": 1, "memory_ids": [85113]}
    ]
  }

After more retro-cycles, identical directives accumulate count > 1 (frequency = signal).
Note: A6 limitation — insert_concept deduplicates by (type, content), so identical text won't accumulate.
      LLM extraction varies phrasing enough that near-duplicates get separate rows.
      Normalization in aggregation catches these near-duplicates for counting.
```

**Real Example — bug candidate surfacing (from actual S362 data):**
```
Memory state (actual):
  id=85096, type='Critique', content='BUG (low): close.md line 65 references "MEMORY phases" after MEMORY phase removal'
  id=85097, type='Critique', content='BUG (medium): spawn-work-ceremony missing stub: true in frontmatter.'
  id=85098, type='Critique', content='FEATURE (high): WORK-143 — triage consumer update needed'

After surface_bug_candidates():
  [
    {"type": "bug", "confidence": "medium", "description": "spawn-work-ceremony missing stub: true in frontmatter.", "memory_id": 85097},
    {"type": "bug", "confidence": "low", "description": "close.md line 65 references...", "memory_id": 85096}
  ]

After surface_feature_candidates():
  [
    {"type": "feature", "confidence": "high", "description": "WORK-143 — triage consumer update needed", "memory_id": 85098}
  ]
```

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| No retro entries in memory | Functions return empty lists | Test 5 (empty KSS), Test 9 (None fn) |
| DB query fails | Return empty list (_ensure_parsed handles) | Test 8 |
| Malformed content (no KEEP-/BUG prefix) | _parse_kss_content returns ('',''), _parse_bug_feature_content returns {} | Implicitly filtered |
| Duplicate directive text (A6) | Normalized, counted as 1 per unique DB row | Test 4 |
| db_query_fn is None | Return empty list immediately | Test 9 |
| JSON string from MCP (A7) | _ensure_parsed auto-deserializes | Built into each query fn |
| KEEP without number (legacy format) | Regex handles optional `-\d+` | _parse_kss_content regex |

### Open Questions

**Q: Should the skill support BOTH memory and filesystem triage in a single invocation?**

Yes. The skill will query memory first for retro entries. Then also run the existing filesystem scan for legacy items. Both feed into the same TRIAGE/PROMOTE phases. This is additive — no breaking change.

**Q: What about the dedup limitation (A6)?**

Known limitation. `insert_concept` deduplicates by (type, content). If two retro-cycles produce identical directive text, only one row exists. However, LLM extraction varies phrasing enough that near-duplicates get separate rows. The normalization in `aggregate_kss_frequency` catches these for counting. Follow-up: fix producer pipeline to bypass dedup for retro entries.

---

## Open Decisions (MUST resolve before implementation)

<!-- Decisions from work item's operator_decisions field.
     If ANY row has [BLOCKED] in Chosen column, plan-validation-cycle will BLOCK.

     POPULATE FROM: Work item frontmatter `operator_decisions` field
     - question -> Decision column
     - options -> Options column
     - chosen -> Chosen column (null = [BLOCKED])
     - rationale -> Rationale column (filled when resolved) -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Where to add functions | A: observations.py, B: new retro_triage.py | A: observations.py | Co-locate with existing triage functions. Same module, same domain. No new import paths needed. |
| DB access pattern | A: Direct SQL via injected callable, B: MCP tool calls in skill | A: Injected callable | Testable without live DB. Agent passes MCP db_query at runtime. CLI entry points for skill-level use (A4). |
| Query strategy (A1 revision) | A: source_adr LIKE 'retro-%', B: content-pattern matching | B: content-pattern matching | A1 critique: source_path not stored in source_adr. Content patterns verified against actual data (ids 85096-85113). |

---

## Implementation Steps

<!-- Each step references which tests turn green -->

### Step 1: Write Failing Tests
- [ ] Add `TestRetroTriageQuery`, `TestKSSAggregation`, `TestBugFeatureSurfacing` classes to `tests/test_observations.py`
- [ ] 10 new tests: 3 query fns, KSS aggregation (2), bug surfacing, feature surfacing, error handling, None fn, backward compat
- [ ] Verify all 10 new tests fail (red) — functions don't exist yet

### Step 2: Implement query functions
- [ ] Add `_ensure_parsed()`, `_rows_to_dicts()` helpers to `observations.py`
- [ ] Add `query_retro_kss()`, `query_retro_bugs()`, `query_retro_features()` to `observations.py`
- [ ] Tests 1, 2, 3, 8, 9 pass (green)

### Step 3: Implement aggregation and surfacing
- [ ] Add `_normalize_directive()`, `_parse_kss_content()`, `aggregate_kss_frequency()` to `observations.py`
- [ ] Add `_parse_bug_feature_content()`, `surface_bug_candidates()`, `surface_feature_candidates()` to `observations.py`
- [ ] Tests 4, 5, 6, 7 pass (green)

### Step 4: Verify backward compatibility
- [ ] Test 10 passes (existing scan_archived_observations unchanged)
- [ ] Run full `tests/test_observations.py` — all tests pass (no regressions)

### Step 5: Add CLI entry points
- [ ] Add `retro-kss`, `retro-bugs`, `retro-features` commands to `observations.py` `__main__` block
- [ ] Verify CLI invocation works (manual test)

### Step 6: Update observation-triage-cycle SKILL.md
- [ ] Add retro-triage SCAN phase instructions (query memory via CLI or MCP before filesystem)
- [ ] Add retro-triage TRIAGE phase instructions (KSS aggregation, candidate surfacing)
- [ ] Update input_contract to include optional `source: memory|filesystem|both` field
- [ ] Update output_contract to include `retro_entries_count`, `kss_aggregation`, `bug_candidates`, `feature_candidates`

### Step 7: Integration Verification
- [ ] All tests pass: `pytest tests/test_observations.py -v`
- [ ] Run full test suite (no regressions): `pytest tests/ -v`

### Step 8: Consumer Verification
- [ ] Grep for imports from observations.py to verify no breakage
- [ ] Verify `just triage-observations` still works (if recipe exists)

---

## Verification

- [ ] Tests pass (`pytest tests/test_observations.py -v`)
- [ ] Full suite no regressions (`pytest tests/ -v`)
- [ ] **MUST:** observation-triage-cycle SKILL.md updated with retro-triage instructions
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| No retro-* data in memory yet | Low | Functions handle empty results gracefully. S362 data already exists (ids 85096-85113). |
| Content format drift in retro-cycle output | Medium | Regex parsers match verified patterns. If LLM extraction changes format, parsers return empty (fail safe). |
| MCP db_query unavailable at skill runtime | Low | db_query_fn=None returns empty list. Filesystem scan still works as fallback. CLI entry points provide alternative. |
| Dedup prevents frequency signal (A6) | Medium | Known limitation. LLM extraction varies phrasing, so near-duplicates get separate rows. Normalization in aggregation catches them. Follow-up: fix producer pipeline. |
| source_path not in source_adr (A1) | N/A (mitigated) | Addressed by content-pattern queries. Follow-up work item to fix ingester pipeline for proper provenance. |

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

**MUST** read `docs/work/active/WORK-143/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| Triage skill updated to query memory by retro-* provenance tags | [ ] | SKILL.md SCAN phase references query_retro_*() |
| K/S/S frequency aggregation across directives | [ ] | aggregate_kss_frequency() tested and callable |
| Bug candidate surfacing with confidence tags | [ ] | surface_bug_candidates() tested and callable |
| Feature candidate surfacing for epoch triage | [ ] | surface_feature_candidates() tested and callable |
| Integration test: retro outputs consumable by triage | [ ] | Test 8 + query tests pass |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/lib/observations.py` | 6 new public functions + 5 private helpers + 3 CLI commands | [ ] | |
| `tests/test_observations.py` | 10 new tests in 3 new classes, all passing | [ ] | |
| `.claude/skills/observation-triage-cycle/SKILL.md` | SCAN phase updated with retro-triage instructions | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest [test_file] -v
# Expected: X tests passed
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

- WORK-142: Retro-cycle design and implementation (parent)
- `.claude/skills/retro-cycle/SKILL.md`: Retro-cycle spec (provenance tag format)
- `.claude/skills/observation-triage-cycle/SKILL.md`: Current triage consumer
- `.claude/haios/lib/observations.py`: Implementation target
- REQ-CEREMONY-002: Explicit input/output contract per ceremony
- REQ-LIFECYCLE-004: Chaining is caller choice (no auto-spawn)
- Memory 85108: "WORK-143 triage consumer update needed to read retro-* provenance tags"

---
