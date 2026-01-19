---
template: implementation_plan
status: complete
date: 2026-01-19
backlog_id: WORK-001
title: Implement Universal Work Item Structure
author: Hephaestus
lifecycle_phase: plan
session: 210
version: '1.5'
generated: 2025-12-21
last_updated: '2026-01-19T16:42:40'
---
# Implementation Plan: Implement Universal Work Item Structure

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

## Pre-Implementation Checklist (RFC 2119)

| Requirement | Level | Action |
|-------------|-------|--------|
| Tests before code | MUST | Write failing tests in "Tests First" section before implementation |
| Query prior work | SHOULD | Search memory for similar implementations before designing |
| Document design decisions | MUST | Fill "Key Design Decisions" table with rationale |
| Ground truth metrics | MUST | Use real file counts from Glob/wc, not guesses |

---

## Goal

Work items will use a universal structure with sequential IDs (WORK-XXX), type as a field, pipeline traceability fields (requirement_refs, source_files, artifacts), and acceptance_criteria in frontmatter only - enabling portability across projects.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 4 | `.claude/templates/work_item.md`, `.claude/haios/modules/work_engine.py`, `.claude/lib/scaffold.py`, `.claude/lib/validate.py` |
| Lines of code affected | ~2024 total | `wc -l`: template (83), work_engine (720), scaffold (458), validate (763) |
| New files to create | 0 | Modifying existing files only |
| Tests to write | 5 | New field parsing, ID generation, validation rules |
| Dependencies | 2 | scaffold.py imports work_engine indirectly; validate.py standalone |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Medium | Template, WorkEngine, scaffold, validate all interact |
| Risk of regression | Medium | Existing tests cover current structure; backward compat needed |
| External dependencies | Low | No external APIs, pure file operations |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Template update | 15 min | High |
| WorkEngine update | 30 min | Medium |
| Scaffold ID generation | 20 min | High |
| Validation rules | 15 min | High |
| Tests + verification | 30 min | Medium |
| **Total** | ~2 hr | Medium |

---

## Current State vs Desired State

### Current State

```yaml
# .claude/templates/work_item.md - Current frontmatter
id: {{BACKLOG_ID}}           # E2-XXX or INV-XXX (type in ID)
category: implementation      # Instead of type field
milestone: null              # HAIOS-specific
spawned_by: null             # HAIOS-specific
spawned_by_investigation: null # HAIOS-specific
operator_decisions: []        # HAIOS-specific
documents:                    # HAIOS-specific structure
  investigations: []
  plans: []
version: "1.0"
```

**Behavior:** Work items use HAIOS-specific structure with type encoded in ID prefix.

**Result:** Not portable to other projects; no pipeline traceability fields.

### Desired State

```yaml
# .claude/templates/work_item.md - Universal frontmatter
id: WORK-{{NEXT_SEQ}}         # Sequential, no type in ID
type: {{TYPE}}                # feature|investigation|bug|chore|spike
requirement_refs: []          # Links to source requirements
source_files: []              # Provenance: where requirement came from
acceptance_criteria: []       # Verifiable statements (ONLY in frontmatter)
artifacts: []                 # Build outputs
extensions: {}                # Project-specific fields
version: "2.0"
```

**Behavior:** Work items use universal structure with type as field, pipeline traceability.

**Result:** Portable across projects; supports doc-to-product pipeline.

---

## Tests First (TDD)

### Test 1: WorkState parses new universal fields
```python
def test_workstate_parses_universal_fields():
    """WorkState should parse type, requirement_refs, source_files, artifacts, extensions."""
    content = """---
id: WORK-001
title: Test
type: feature
requirement_refs: [REQ-001]
source_files: [specs/auth.md]
acceptance_criteria: [AC1, AC2]
artifacts: []
extensions: {}
current_node: backlog
status: active
---"""
    work = engine._parse_work_file(path_with_content)
    assert work.type == "feature"
    assert work.requirement_refs == ["REQ-001"]
    assert work.acceptance_criteria == ["AC1", "AC2"]
```

### Test 2: get_next_work_id returns sequential WORK-XXX
```python
def test_get_next_work_id_sequential():
    """Next ID should be WORK-XXX where XXX is max+1."""
    # Given: WORK-001, WORK-003 exist (gap is OK)
    # When: get_next_work_id()
    # Then: returns "WORK-004"
    assert get_next_work_id() == "WORK-004"
```

### Test 3: validate_work_item checks new required fields
```python
def test_validate_work_item_requires_type():
    """Validation should warn if type field is missing."""
    result = validate_template(work_without_type)
    assert "type" in result.warnings
```

### Test 4: Backward compatibility with E2-XXX IDs
```python
def test_existing_e2_ids_still_work():
    """Existing E2-XXX work items should still parse correctly."""
    work = engine.get_work("E2-179")
    assert work.id == "E2-179"
    assert work.status == "active"
```

### Test 5: create_work uses universal template
```python
def test_create_work_uses_universal_fields():
    """New work items should have type, requirement_refs, etc."""
    path = engine.create_work("WORK-002", "Test", type="bug")
    content = path.read_text()
    assert "type: bug" in content
    assert "requirement_refs:" in content
```

---

## Detailed Design

### Change 1: Template Update

**File:** `.claude/templates/work_item.md`

**Current frontmatter (lines 1-35):**
```yaml
id: {{BACKLOG_ID}}
milestone: null
category: implementation
spawned_by: null
spawned_by_investigation: null
operator_decisions: []
documents:
  investigations: []
  plans: []
version: "1.0"
```

**New frontmatter:**
```yaml
id: {{BACKLOG_ID}}
type: {{TYPE}}                    # NEW: feature|investigation|bug|chore|spike
requirement_refs: []              # NEW: Links to source requirements
source_files: []                  # NEW: Provenance
acceptance_criteria: []           # NEW: Verifiable statements (frontmatter only)
blocked_by: []
blocks: []
enables: []
artifacts: []                     # NEW: Build outputs
cycle_docs: {}
extensions: {}                    # NEW: Project-specific fields
version: "2.0"                    # Bumped
```

**Body changes:**
- Remove `## Acceptance Criteria` section with checkboxes (now frontmatter-only)
- Keep `## Deliverables` section (implementation outputs, not requirements)

### Change 2: WorkState dataclass extension

**File:** `.claude/haios/modules/work_engine.py:80-92`

**Current:**
```python
@dataclass
class WorkState:
    id: str
    title: str
    status: str
    current_node: str
    blocked_by: List[str] = field(default_factory=list)
    node_history: List[Dict[str, Any]] = field(default_factory=list)
    memory_refs: List[int] = field(default_factory=list)
    path: Optional[Path] = None
    priority: str = "medium"
```

**New:**
```python
@dataclass
class WorkState:
    id: str
    title: str
    status: str
    current_node: str
    type: str = "feature"                                    # NEW
    blocked_by: List[str] = field(default_factory=list)
    node_history: List[Dict[str, Any]] = field(default_factory=list)
    memory_refs: List[int] = field(default_factory=list)
    requirement_refs: List[str] = field(default_factory=list)  # NEW
    source_files: List[str] = field(default_factory=list)      # NEW
    acceptance_criteria: List[str] = field(default_factory=list)  # NEW
    artifacts: List[str] = field(default_factory=list)         # NEW
    extensions: Dict[str, Any] = field(default_factory=dict)   # NEW
    path: Optional[Path] = None
    priority: str = "medium"
```

### Change 3: _parse_work_file update

**File:** `.claude/haios/modules/work_engine.py:570-588`

**Add field parsing:**
```python
return WorkState(
    id=fm.get("id", ""),
    title=fm.get("title", ""),
    status=fm.get("status", ""),
    current_node=fm.get("current_node", "backlog"),
    type=fm.get("type", fm.get("category", "feature")),  # NEW: fallback to category
    blocked_by=fm.get("blocked_by", []) or [],
    node_history=fm.get("node_history", []),
    memory_refs=fm.get("memory_refs", []) or [],
    requirement_refs=fm.get("requirement_refs", []) or [],  # NEW
    source_files=fm.get("source_files", []) or [],          # NEW
    acceptance_criteria=fm.get("acceptance_criteria", []) or [],  # NEW
    artifacts=fm.get("artifacts", []) or [],                # NEW
    extensions=fm.get("extensions", {}) or {},              # NEW
    path=path,
    priority=fm.get("priority", "medium"),
)
```

### Change 4: Scaffold ID generation

**File:** `.claude/lib/scaffold.py`

**Add function:**
```python
def get_next_work_id() -> str:
    """Generate next sequential WORK-XXX ID.

    Scans docs/work/active/ for highest WORK-NNN and returns WORK-(N+1).
    """
    work_dir = PROJECT_ROOT / "docs" / "work" / "active"
    max_num = 0
    for subdir in work_dir.iterdir():
        if subdir.is_dir() and subdir.name.startswith("WORK-"):
            try:
                num = int(subdir.name.split("-")[1])
                max_num = max(max_num, num)
            except (ValueError, IndexError):
                pass
    return f"WORK-{max_num + 1:03d}"
```

### Change 5: Validation rules update

**File:** `.claude/lib/validate.py:150-160`

**Current:**
```python
"work_item": {
    "required_fields": ["template", "status", "id", "title", "current_node"],
    "optional_fields": [
        "owner", "created", "closed", "milestone", "priority", "effort",
        "category", "spawned_by", "spawned_by_investigation", "blocked_by",
        ...
    ],
```

**New:**
```python
"work_item": {
    "required_fields": ["template", "status", "id", "title", "current_node", "type"],
    "optional_fields": [
        "owner", "created", "closed", "priority", "effort",
        "requirement_refs", "source_files", "acceptance_criteria",  # NEW
        "artifacts", "extensions",  # NEW
        "blocked_by", "blocks", "enables", "related", "node_history",
        "cycle_docs", "memory_refs", "version",
        # Legacy fields (backward compat)
        "milestone", "category", "spawned_by", "spawned_by_investigation",
        "operator_decisions", "documents",
    ],
    "allowed_status": ["active", "blocked", "complete", "archived"],
    "allowed_types": ["feature", "investigation", "bug", "chore", "spike"],  # NEW
    "expected_sections": ["Context", "Deliverables"],  # Removed "Acceptance Criteria"
},
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Sequential IDs | `WORK-XXX` | Operator decision (Session 210): Simple, no semantics in ID. Type is queryable field. |
| Type field | 5 types | Operator decision: feature, investigation, bug, chore, spike cover common categories. |
| acceptance_criteria location | Frontmatter only | Operator decision: Single source of truth, machine-parseable, no duplication. |
| Backward compat | Keep legacy fields as optional | Existing E2-XXX items must still work; gradual migration. |
| Fallback parsing | `type` falls back to `category` | Smooth transition: old items parsed correctly without migration. |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Existing E2-XXX ID | Parse normally, `type` defaults via `category` fallback | Test 4 |
| Missing type field | Default to "feature" | Test 3 (validation warning) |
| WORK-001 already exists | get_next_work_id scans and returns WORK-002 | Test 2 |
| Gap in IDs (WORK-001, WORK-003) | Next is WORK-004 (no gap filling) | Test 2 |

---

## Open Decisions (MUST resolve before implementation)

All decisions resolved in AMBIGUITY phase:

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| ID format | UUID, semantic, sequential | Sequential (WORK-XXX) | Simple, no semantics in ID. Type as field is queryable. |
| Type taxonomy | 3, 5, or more types | 5 types | feature, investigation, bug, chore, spike covers common work. |
| acceptance_criteria location | Frontmatter, body, both | Frontmatter only | Single source of truth, machine-parseable, no duplication risk. |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add 5 tests to `tests/test_work_engine.py`
- [ ] Test 1: WorkState parses universal fields
- [ ] Test 2: get_next_work_id returns sequential
- [ ] Test 3: validate_work_item checks type field
- [ ] Test 4: Backward compat with E2-XXX
- [ ] Test 5: create_work uses universal fields
- [ ] Verify all tests fail (RED)

### Step 2: Update WorkState dataclass
- [ ] Add new fields to WorkState in `work_engine.py:80-92`
- [ ] Add type, requirement_refs, source_files, acceptance_criteria, artifacts, extensions
- [ ] Test 1 passes (GREEN)

### Step 3: Update _parse_work_file
- [ ] Modify parser in `work_engine.py:570-588`
- [ ] Add fallback: `type` defaults from `category` field
- [ ] Tests 1, 4 pass (GREEN)

### Step 4: Add get_next_work_id to scaffold
- [ ] Add function to `scaffold.py`
- [ ] Scan WORK-* directories, return max+1
- [ ] Test 2 passes (GREEN)

### Step 5: Update work_item template
- [ ] Edit `.claude/templates/work_item.md`
- [ ] Add new frontmatter fields
- [ ] Remove body Acceptance Criteria section
- [ ] Keep Deliverables section
- [ ] Test 5 passes (GREEN)

### Step 6: Update validation rules
- [ ] Modify registry in `validate.py:150-160`
- [ ] Add `type` to required_fields
- [ ] Add `allowed_types` enum
- [ ] Add new optional fields
- [ ] Test 3 passes (GREEN)

### Step 7: Integration Verification
- [ ] All 5 new tests pass
- [ ] Run full test suite: `pytest tests/ -v`
- [ ] No regressions

### Step 8: Consumer Verification
- [ ] Grep for `category:` usage in code (should use `type` now)
- [ ] Verify scaffold commands work with new template
- [ ] Verify existing E2-XXX work items still parse

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment - misinterpreting TRD | Medium | Verified TRD schema matches implementation design |
| Regression - existing E2-XXX items break | High | Added `category` fallback to `type` parsing; backward compat test |
| Scope creep - adding fields not in TRD | Low | Plan strictly follows TRD-WORK-ITEM-UNIVERSAL.md |
| Integration - scaffold doesn't use new template | Medium | Test 5 verifies create_work produces universal structure |
| Knowledge gap - YAML parsing edge cases | Low | Using existing yaml.safe_load patterns from work_engine |

---

## Progress Tracker

<!-- ADR-033: Track session progress against this plan -->
<!-- Update this section when creating checkpoints that reference this plan -->

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| - | - | - | - | No progress recorded yet |

---

## Ground Truth Verification (Before Closing)

### WORK.md Deliverables Check (MUST - Session 192)

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| `.claude/templates/work_item.md` updated | [ ] | Read file, verify type/requirement_refs/etc present |
| WorkEngine handles new fields | [ ] | Run test_workstate_parses_universal_fields |
| ID generation uses WORK-XXX | [ ] | Run test_get_next_work_id_sequential |
| Validation checks new fields | [ ] | Run test_validate_work_item_requires_type |
| First work item tracked (WORK-001) | [x] | Already exists and being used |

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/templates/work_item.md` | Has type, requirement_refs, acceptance_criteria in frontmatter | [ ] | |
| `.claude/haios/modules/work_engine.py` | WorkState has 6 new fields | [ ] | |
| `.claude/lib/scaffold.py` | get_next_work_id() function exists | [ ] | |
| `.claude/lib/validate.py` | work_item registry has type as required | [ ] | |
| `tests/test_work_engine.py` | 5 new tests exist | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_work_engine.py -v -k universal
# Expected: 5 tests passed
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

- @docs/specs/TRD-WORK-ITEM-UNIVERSAL.md (source specification)
- @.claude/haios/epochs/E2_3/arcs/workuniversal/ARC.md (arc context)
- @docs/work/active/WORK-001/WORK.md (work item)

---
