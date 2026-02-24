---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-24
backlog_id: WORK-165
title: "Infrastructure Ceremonies"
author: Hephaestus
lifecycle_phase: plan
session: 445
generated: 2026-02-24
last_updated: 2026-02-24T20:18:55

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-165/WORK.md"
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
# Implementation Plan: Infrastructure Ceremonies

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification. -->

---

## Goal

Build `ceremony_cards.py` in `.claude/haios/lib/` that enables programmatic discovery of ceremony skills by parsing YAML frontmatter from `.claude/skills/*/SKILL.md` files where `type: ceremony`, following the exact same pattern as `agent_cards.py` (WORK-164), then verify the open-epoch-ceremony skill is functional and the ceremony loop (open/close pairs for epoch, arc, chapter) is complete and standardized.

---

## Open Decisions

No operator_decisions in work item frontmatter. No open decisions to track.

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Discovery scope | `*-ceremony/*.md` glob vs `type: ceremony` field filter | `type: ceremony` field filter | close-work-cycle has `type: ceremony` but name doesn't match `*-ceremony` pattern. Field-based filtering is more robust and consistent with agent_cards.py `type: agent` convention |
| close-work-cycle inclusion | Include or exclude from ceremony_cards | Include | It has `type: ceremony` in frontmatter and IS a ceremony per functional_requirements.md; the name divergence is a naming artifact, not a category difference |

---

## Layer 0: Inventory

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/haios/lib/ceremony_cards.py` | CREATE | 2 |
| `.claude/haios/lib/README.md` | MODIFY | 2 |

### Consumer Files

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `.claude/haios/lib/README.md` | Registry table — add ceremony_cards.py row | ~105 | UPDATE |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_ceremony_cards.py` | CREATE | New test file for ceremony_cards.py module |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 2 | `ceremony_cards.py` + `tests/test_ceremony_cards.py` |
| Files to modify | 1 | `README.md` registry table |
| Tests to write | 13 | See Layer 1 Tests section |
| Total blast radius | 3 | Sum of unique files above |

---

## Layer 1: Specification

### Current State

```python
# .claude/haios/lib/ — no ceremony_cards.py exists
# Discovery of ceremonies is NOT currently possible via infrastructure.
# Agents must memorize skill names from CLAUDE.md or documentation.
# The ceremony loop is not verifiable without manual enumeration.
```

**Behavior:** Ceremonies are undiscoverable. Agents invoke ceremonies by name from memory/docs.
**Problem:** REQ-DISCOVER-003 requires programmatic discovery. No infrastructure enforces the ceremony loop. CLAUDE.md listing goes stale silently.

```python
# .claude/skills/*-ceremony/SKILL.md — ceremony skill frontmatter (representative)
# open-epoch-ceremony SKILL.md frontmatter:
name: open-epoch-ceremony
type: ceremony
description: "Initialize a new epoch with directory structure, config transition, work item triage, and arc decomposition."
category: closure
input_contract:
  - field: epoch_id
    type: string
    required: true
    description: "New epoch ID (e.g., E2.8)"
  - field: prior_epoch_id
    type: string
    required: true
    description: "Just-closed epoch ID (e.g., E2.7)"
output_contract:
  - field: success
    type: boolean
    guaranteed: always
    description: "Whether all phases completed"
side_effects:
  - "Create epoch directory structure"
  - "Update haios.yaml epoch config"
```

### Desired State

```python
# .claude/haios/lib/ceremony_cards.py — complete new module

"""Ceremony card discovery module (REQ-DISCOVER-003).

Provides programmatic access to ceremony capability cards by parsing
YAML frontmatter from .claude/skills/*/SKILL.md files where type == 'ceremony'.

Public API:
    list_ceremonies() -> list[CeremonyCard]
    get_ceremony(name) -> CeremonyCard | None
    filter_ceremonies(category) -> list[CeremonyCard]
"""

# After this file exists:
ceremonies = list_ceremonies()
# Returns all skills with type: ceremony, sorted by name
# Currently: close-arc-ceremony, close-chapter-ceremony, close-epoch-ceremony,
#            close-work-cycle, memory-commit-ceremony, open-epoch-ceremony,
#            session-end-ceremony, session-start-ceremony, spawn-work-ceremony
# (all skills with type: ceremony in their SKILL.md frontmatter)

epoch_ceremonies = filter_ceremonies(category="closure")
# Returns subset with category: closure

card = get_ceremony("open-epoch-ceremony")
# Returns CeremonyCard with all frontmatter fields populated
```

**Behavior:** Ceremonies are discoverable via infrastructure. loop completeness is verifiable programmatically.
**Result:** REQ-DISCOVER-003 satisfied for ceremonies. Ceremony loop (open/close pairs) verifiable via filter.

### Tests

**Import block (required at top of `tests/test_ceremony_cards.py` — critique A3):**
```python
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
from ceremony_cards import CeremonyCard, list_ceremonies, get_ceremony, filter_ceremonies, SKILLS_DIR
```

#### Test 1: CeremonyCard minimal construction
- **file:** `tests/test_ceremony_cards.py`
- **function:** `test_minimal_construction()`
- **setup:** Construct `CeremonyCard(name="test-ceremony", description="A test", category="closure")`
- **assertion:** `card.name == "test-ceremony"`, `card.description == "A test"`, `card.category == "closure"`

#### Test 2: CeremonyCard optional fields have defaults
- **file:** `tests/test_ceremony_cards.py`
- **function:** `test_optional_fields_have_defaults()`
- **setup:** Construct minimal CeremonyCard
- **assertion:** `card.input_contract == []`, `card.output_contract == []`, `card.side_effects == []`

#### Test 3: list_ceremonies returns list
- **file:** `tests/test_ceremony_cards.py`
- **function:** `test_list_ceremonies_returns_list()`
- **setup:** Call `list_ceremonies()` against real skills directory
- **assertion:** `isinstance(result, list)` is True

#### Test 4: list_ceremonies returns CeremonyCard instances
- **file:** `tests/test_ceremony_cards.py`
- **function:** `test_list_ceremonies_returns_ceremony_cards()`
- **setup:** Call `list_ceremonies()`
- **assertion:** Each item is a `CeremonyCard` instance

#### Test 5: list_ceremonies ceremony count
- **file:** `tests/test_ceremony_cards.py`
- **function:** `test_ceremony_count()`
- **setup:** Call `list_ceremonies()` against real skills directory
- **assertion:** `len(result) >= 9` (at least 9 skills with `type: ceremony` in SKILL.md as of S445: close-arc-ceremony, close-chapter-ceremony, close-epoch-ceremony, close-work-cycle, memory-commit-ceremony, open-epoch-ceremony, session-end-ceremony, session-start-ceremony, spawn-work-ceremony; uses >= to tolerate future ceremony additions without breaking — critique A1)

#### Test 6: list_ceremonies excludes non-ceremony skills
- **file:** `tests/test_ceremony_cards.py`
- **function:** `test_excludes_non_ceremony_skills()`
- **setup:** Call `list_ceremonies()`
- **assertion:** No card has name in `{"implementation-cycle", "plan-authoring-cycle", "retro-cycle"}` (these are `type: lifecycle`, not `type: ceremony`)

#### Test 7: known ceremonies present
- **file:** `tests/test_ceremony_cards.py`
- **function:** `test_known_ceremonies_present()`
- **setup:** Call `list_ceremonies()`
- **assertion:** `{"open-epoch-ceremony", "close-epoch-ceremony", "close-arc-ceremony", "close-chapter-ceremony", "close-work-cycle"}` is subset of names

#### Test 8: get_ceremony known name
- **file:** `tests/test_ceremony_cards.py`
- **function:** `test_get_ceremony_known_name()`
- **setup:** Call `get_ceremony("open-epoch-ceremony")`
- **assertion:** `result is not None`, `result.name == "open-epoch-ceremony"`

#### Test 9: get_ceremony unknown name returns None
- **file:** `tests/test_ceremony_cards.py`
- **function:** `test_get_ceremony_unknown_returns_none()`
- **setup:** Call `get_ceremony("nonexistent-ceremony")`
- **assertion:** `result is None`

#### Test 10: filter_ceremonies by category
- **file:** `tests/test_ceremony_cards.py`
- **function:** `test_filter_by_category_closure()`
- **setup:** Call `filter_ceremonies(category="closure")`
- **assertion:** `"open-epoch-ceremony"` in names, `"close-epoch-ceremony"` in names, `"close-arc-ceremony"` in names

#### Test 11: filter_ceremonies no filters returns all
- **file:** `tests/test_ceremony_cards.py`
- **function:** `test_filter_no_args_returns_all()`
- **setup:** Call `filter_ceremonies()`
- **assertion:** `len(result) >= 9` (same rationale as Test 5 — critique A1)

#### Test 12: SKILLS_DIR constant
- **file:** `tests/test_ceremony_cards.py`
- **function:** `test_skills_dir_exists()`
- **setup:** Import `SKILLS_DIR` from `ceremony_cards`
- **assertion:** `SKILLS_DIR.exists()` is True, `SKILLS_DIR` contains subdirectories with `SKILL.md` files

#### Test 13: filter_ceremonies multi-category (critique A2)
- **file:** `tests/test_ceremony_cards.py`
- **function:** `test_filter_by_secondary_category()`
- **setup:** Call `filter_ceremonies(category="queue")`
- **assertion:** `"close-work-cycle"` in names (close-work-cycle has `category: [closure, queue]`; filtering by secondary category "queue" must still find it)

### Design

#### File 1 (NEW): `.claude/haios/lib/ceremony_cards.py`

```python
# generated: 2026-02-24
# Session 445: WORK-165 Ceremony Cards
"""Ceremony card discovery module (REQ-DISCOVER-003).

Provides programmatic access to ceremony capability cards by parsing
YAML frontmatter from .claude/skills/*/SKILL.md files where type == 'ceremony'.

Public API:
    list_ceremonies() -> list[CeremonyCard]
    get_ceremony(name) -> CeremonyCard | None
    filter_ceremonies(category) -> list[CeremonyCard]
"""

from __future__ import annotations

import yaml
from dataclasses import dataclass, field
from pathlib import Path


# Anchored to this file's location, not cwd (same pattern as agent_cards.py)
_LIB_DIR = Path(__file__).resolve().parent
_HAIOS_DIR = _LIB_DIR.parent
_CLAUDE_DIR = _HAIOS_DIR.parent
SKILLS_DIR = _CLAUDE_DIR / "skills"


@dataclass
class CeremonyCard:
    """Structured representation of a ceremony skill's capability card.

    Required fields: name, description, category.
    All other fields are optional with sensible defaults to support
    incremental frontmatter extension.

    Note: category stores the primary (first) category as a string for
    simple filtering. categories stores ALL categories as a list for
    multi-category ceremonies (e.g., close-work-cycle: [closure, queue]).
    filter_ceremonies checks membership in the full categories list.
    """

    # Required fields (always present in ceremony frontmatter)
    name: str
    description: str
    category: str  # Primary category (first element if list)

    # Multi-category support (critique A2: prevent silent data loss)
    categories: list[str] = field(default_factory=list)

    # Optional fields with defaults
    input_contract: list = field(default_factory=list)
    output_contract: list = field(default_factory=list)
    side_effects: list[str] = field(default_factory=list)


def _parse_frontmatter(filepath: Path) -> dict | None:
    """Parse YAML frontmatter from a SKILL.md file.

    Returns None if parsing fails (defensive, mirrors agent_cards.py pattern).
    """
    try:
        content = filepath.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            return None
        return yaml.safe_load(parts[1])
    except Exception:
        return None


def _frontmatter_to_card(fm: dict) -> CeremonyCard | None:
    """Convert frontmatter dict to CeremonyCard.

    Returns None if:
    - type != 'ceremony' (filters out non-ceremony skills)
    - required fields (name, description, category) are missing
    """
    if fm.get("type") != "ceremony":
        return None

    name = fm.get("name")
    description = fm.get("description")
    category = fm.get("category")

    if not name or not description or not category:
        return None

    # category may be a list (close-work-cycle has category: [closure, queue])
    # Preserve ALL categories in categories list; normalize primary to first element
    if isinstance(category, list):
        categories = [str(c) for c in category]
        primary_category = categories[0] if categories else ""
    else:
        categories = [str(category)]
        primary_category = str(category)

    return CeremonyCard(
        name=name,
        description=description,
        category=primary_category,
        categories=categories,
        input_contract=fm.get("input_contract") or [],
        output_contract=fm.get("output_contract") or [],
        side_effects=fm.get("side_effects") or [],
    )


def list_ceremonies(skills_dir: Path | None = None) -> list[CeremonyCard]:
    """List all ceremonies by parsing frontmatter from SKILL.md files.

    Scans all subdirectories of skills_dir for SKILL.md files.
    Only includes skills where type == 'ceremony'.

    Args:
        skills_dir: Override skills directory (for testing). Defaults to SKILLS_DIR.

    Returns:
        List of CeremonyCard instances, sorted by name.
    """
    directory = skills_dir or SKILLS_DIR
    ceremonies = []
    for skill_dir in sorted(directory.iterdir()):
        if not skill_dir.is_dir():
            continue
        skill_file = skill_dir / "SKILL.md"
        if not skill_file.exists():
            continue
        fm = _parse_frontmatter(skill_file)
        if fm is None:
            continue
        card = _frontmatter_to_card(fm)
        if card is not None:
            ceremonies.append(card)
    return ceremonies


def get_ceremony(name: str, skills_dir: Path | None = None) -> CeremonyCard | None:
    """Get a single ceremony by name.

    Args:
        name: Ceremony name (e.g., "open-epoch-ceremony").
        skills_dir: Override skills directory (for testing).

    Returns:
        CeremonyCard if found, None otherwise.
    """
    for ceremony in list_ceremonies(skills_dir):
        if ceremony.name == name:
            return ceremony
    return None


def filter_ceremonies(
    category: str | None = None,
    skills_dir: Path | None = None,
) -> list[CeremonyCard]:
    """Filter ceremonies by frontmatter field values.

    Checks against the full categories list, not just the primary category.
    This means filter_ceremonies(category="queue") will return close-work-cycle
    even though its primary category is "closure" (it has categories: [closure, queue]).

    Args:
        category: Filter by category (closure, queue, session, memory, feedback, spawn).
        skills_dir: Override skills directory (for testing).

    Returns:
        List of matching CeremonyCard instances.
    """
    ceremonies = list_ceremonies(skills_dir)
    if category is not None:
        ceremonies = [c for c in ceremonies if category in c.categories]
    return ceremonies
```

#### File 2 (MODIFY): `.claude/haios/lib/README.md`

**Location:** Module registry table (lines ~88-111)

**Current Code:**
```markdown
| `session_review_predicate.py` | Session Review trigger predicate (WORK-209). ... |
```

**Target Code (add new row after session_review_predicate.py):**
```markdown
| `ceremony_cards.py` | Ceremony skill discovery module (WORK-165, REQ-DISCOVER-003). Programmatic access to ceremony skills by parsing YAML frontmatter from .claude/skills/*/SKILL.md where type=ceremony. Public API: list_ceremonies(), get_ceremony(name), filter_ceremonies(category). Parallel to agent_cards.py. |
```

### Call Chain

```
caller (coldstart / survey / governance hook)
    |
    +-> list_ceremonies()            # scan SKILLS_DIR subdirectories
    |       iterdir() -> SKILL.md files
    |       _parse_frontmatter()     # parse YAML between --- delimiters
    |       _frontmatter_to_card()   # type: ceremony filter + required field check
    |       Returns: list[CeremonyCard] sorted by name
    |
    +-> get_ceremony("open-epoch-ceremony")
    |       Calls list_ceremonies() + linear scan by name
    |       Returns: CeremonyCard | None
    |
    +-> filter_ceremonies(category="closure")
            Calls list_ceremonies() + list comprehension filter
            Returns: list[CeremonyCard]
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Discovery via type field, not glob | `type: ceremony` filter instead of `*-ceremony` glob | close-work-cycle has `type: ceremony` but name doesn't match `*-ceremony`; field filter is declarative and self-documenting |
| category list normalization | Preserve all categories; primary = first element | close-work-cycle has `category: [closure, queue]` (list); `category` field stores primary (first), `categories` field stores full list; `filter_ceremonies` checks membership in full list to prevent silent data loss (critique A2) |
| Parallel module, not extension | New `ceremony_cards.py`, not extending `agent_cards.py` | Ceremonies have different schema (phases, contracts) vs agents (tools, models). Separate modules follow SRP and mirror the parallel structures in HAIOS |
| SKILLS_DIR path anchoring | `Path(__file__).resolve().parent` chain | Identical to agent_cards.py pattern — avoids cwd dependency, works from any call site |
| input_contract/output_contract as list | Raw list of dicts from frontmatter | Ceremonies have structured contract dicts; preserve as-is for caller introspection (contract validation handled by ceremony_contracts.py, not here) |
| No ARTIFACT_VOCABULARY | Omitted vs agent_cards.py | Ceremonies don't produce artifacts directly; the vocabulary concept is agent-specific. Adding it would be speculative scope |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| SKILL.md with `type: lifecycle` (not ceremony) | `_frontmatter_to_card` returns None; filtered out | Test 6 |
| SKILL.md missing required field (name/description/category) | Returns None; defensive skip | Test 9 (implicit via real FS) |
| skill_dir with no SKILL.md | `skill_file.exists()` check skips it | Covered by real FS scan |
| category as list (close-work-cycle) | Preserve all in categories list; primary = first element; filter checks full list | Test 10, Test 13 |
| Malformed YAML frontmatter | `_parse_frontmatter` returns None; defensive skip | Covered by try/except |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Ceremony count changes when new skill added | L | Test 5 uses >= 9 — tolerates future additions without breaking (critique A1) |
| close-work-cycle category normalization breaks filter | M | Test 10 checks category="closure" returns open/close pairs — verifies normalization works |
| SKILLS_DIR path breaks in test environment | M | Tests use `tmp_path` fixture with synthetic SKILL.md files for unit tests; real FS for integration tests |
| New ceremony SKILL.md with non-string category field | L | `_frontmatter_to_card` handles list case explicitly; other types fall through to empty string (non-match) |

---

## Layer 2: Implementation Steps

### Step 1: Write Failing Tests (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Create `tests/test_ceremony_cards.py` with all 13 test specs from Layer 1 Tests section (including import block). Tests import from `ceremony_cards` (not yet created) — all fail with ImportError.
- **output:** `tests/test_ceremony_cards.py` exists, all 13 tests fail
- **verify:** `pytest tests/test_ceremony_cards.py -v 2>&1 | grep -c "ERROR\|FAILED"` equals 13 (or import error count)

### Step 2: Implement ceremony_cards.py (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (NEW)
- **input:** Step 1 complete (tests exist and fail)
- **action:** Create `.claude/haios/lib/ceremony_cards.py` from Layer 1 Design section verbatim
- **output:** All 13 tests pass
- **verify:** `pytest tests/test_ceremony_cards.py -v` exits 0, `13 passed` in output

### Step 3: Verify open-epoch-ceremony Functional
- **spec_ref:** Layer 1 > Specification > Current State (open-epoch-ceremony SKILL.md)
- **input:** Step 2 complete
- **action:** Run `get_ceremony("open-epoch-ceremony")` and verify card fields match SKILL.md frontmatter. Check phases SCAFFOLD->CONFIG->TRIAGE->DECOMPOSE->VALIDATE are documented. Confirm S393 lessons are captured in SKILL.md.
- **output:** open-epoch-ceremony discoverable and verified functional (SKILL.md complete with all phases and lessons)
- **verify:** `python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from ceremony_cards import get_ceremony; c = get_ceremony('open-epoch-ceremony'); print(c.name, c.category)"` prints `open-epoch-ceremony closure`

### Step 4: Audit Ceremony Loop Completeness
- **spec_ref:** Layer 0 > Scope Metrics
- **input:** Step 3 complete
- **action:** Verify open/close pairs for epoch, arc, chapter all exist: open-epoch-ceremony + close-epoch-ceremony (epoch pair), close-arc-ceremony (arc close; no open-arc needed — arcs open implicitly via epoch DECOMPOSE), close-chapter-ceremony (chapter close; chapters open implicitly). Confirm these are the standardized pairs per acceptance criteria.
- **output:** Ceremony loop completeness confirmed — epoch has open+close pair, arc has close (no open-arc ceremony needed per design), chapter has close (no open-chapter ceremony needed per design)
- **verify:** `python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from ceremony_cards import filter_ceremonies; cs = filter_ceremonies(category='closure'); print([c.name for c in cs])"` includes all four ceremony names

### Step 5: Update README
- **spec_ref:** Layer 0 > Consumer Files
- **input:** Step 4 complete
- **action:** Add `ceremony_cards.py` row to module registry table in `.claude/haios/lib/README.md`
- **output:** README reflects new module
- **verify:** `grep "ceremony_cards" .claude/haios/lib/README.md` returns 1 match

### Step 6: Full Regression Check
- **spec_ref:** Layer 0 > Scope Metrics (total blast radius)
- **input:** Step 5 complete
- **action:** Run full test suite to confirm no regressions
- **output:** All tests pass, 0 new failures
- **verify:** `pytest tests/ -v 2>&1 | tail -5` shows 0 failed (0 new vs pre-existing baseline)

---

## Ground Truth Verification

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_ceremony_cards.py -v` | 13 passed, 0 failed |
| `pytest tests/ -v` | 0 new failures vs pre-implementation baseline |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| open-epoch-ceremony verified functional | `python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from ceremony_cards import get_ceremony; c = get_ceremony('open-epoch-ceremony'); assert c is not None; print('OK')"` | `OK` |
| Ceremonies discoverable via infrastructure | `python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from ceremony_cards import list_ceremonies; cs = list_ceremonies(); print(len(cs))"` | `>= 9` (currently 9) |
| Ceremony loop standardized | `python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); from ceremony_cards import filter_ceremonies; cs = filter_ceremonies(category='closure'); names = [c.name for c in cs]; assert 'open-epoch-ceremony' in names and 'close-epoch-ceremony' in names; print('OK')"` | `OK` |
| Tests for ceremony discovery | `pytest tests/test_ceremony_cards.py -v` | 13 passed |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| ceremony_cards importable | `python -c "import sys; sys.path.insert(0, '.claude/haios/lib'); import ceremony_cards; print('OK')"` | `OK` |
| README updated | `grep "ceremony_cards" .claude/haios/lib/README.md` | 1+ match |
| No stale references | `grep "ceremony_cards" . -r --include="*.py" --include="*.md" 2>/dev/null` | Only new files (no orphan references) |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 2 verify: `pytest tests/test_ceremony_cards.py -v` → 13 passed)
- [ ] All WORK.md deliverables verified (table above)
- [ ] ceremony_cards.py importable from real skills directory (Consumer Integrity)
- [ ] README updated (Consumer Integrity)
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- `.claude/haios/lib/agent_cards.py` — reference implementation (WORK-164 pattern)
- `tests/test_agent_cards.py` — reference test file (test pattern to follow)
- `.claude/skills/open-epoch-ceremony/SKILL.md` — ceremony frontmatter schema source
- `.claude/skills/close-epoch-ceremony/SKILL.md` — ceremony frontmatter schema source
- `.claude/skills/close-arc-ceremony/SKILL.md` — ceremony frontmatter schema source
- `.claude/skills/close-chapter-ceremony/SKILL.md` — ceremony frontmatter schema source
- `.claude/skills/close-work-cycle/SKILL.md` — ceremony with non-standard name (type: ceremony, name != *-ceremony)
- `docs/ADR/ADR-048-progressive-contracts-phase-per-file-skill-fracturing.md`
- Memory refs: 85098, 85108 (WORK-143 triage consumer)

---
