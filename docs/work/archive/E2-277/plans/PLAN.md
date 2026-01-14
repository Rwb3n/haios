---
template: implementation_plan
status: complete
date: 2026-01-06
backlog_id: E2-277
title: Implement Portal System in Work Items
author: Hephaestus
lifecycle_phase: done
session: 179
version: '1.6'
generated: 2025-12-21
last_updated: '2026-01-06T23:26:12'
memory_refs:
- 80999
- 81000
- 81001
- 81002
- 81003
- 81004
- 81005
- 81006
- 81007
- 81008
- 81009
- 81010
- 81011
- 81012
- 81013
---
# Implementation Plan: Implement Portal System in Work Items

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

Work items will have a `references/REFS.md` portal file that lists spawned_from, blocks, related, ADR, and memory links, enabling ground-cycle to traverse provenance chains.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 2 | `work_engine.py` (1069 lines), `work_item.md` template (70 lines) |
| Lines of code affected | ~50 | New methods in WorkEngine + template addition |
| New files to create | 1 | `.claude/templates/portal_refs.md` (portal template) |
| Tests to write | 4 | Portal creation, update, read, template validation |
| Dependencies | 1 | ground-cycle will consume portals (future E2-280) |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Med | WorkEngine creates/updates portals on work lifecycle events |
| Risk of regression | Low | Additive change, existing work_engine tests cover base |
| External dependencies | Low | File system only |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Template creation | 15 min | High |
| WorkEngine portal methods | 45 min | High |
| Tests | 30 min | High |
| **Total** | ~1.5 hr | High |

---

## Current State vs Desired State

### Current State

```
docs/work/active/E2-277/
├── WORK.md           # Has spawned_by, blocked_by in frontmatter
├── plans/            # Exists
└── (no references/)  # MISSING - no portal file
```

**Behavior:** Work items store relationships in WORK.md frontmatter (`spawned_by_investigation`, `blocked_by`, `related`, `memory_refs`). Data is embedded, not linked. No portal file exists.

**Result:** ground-cycle cannot traverse provenance because there's no standard traversal target. E2-271 was planned against wrong architecture because spawned_by_investigation chain wasn't traversed.

### Desired State

```
docs/work/active/E2-277/
├── WORK.md           # State machine (unchanged)
├── plans/
└── references/       # NEW
    └── REFS.md       # Portal file with traversable links
```

```yaml
# references/REFS.md content (per S2C)
---
type: portal-index
work_id: E2-277
---

# Provenance
- **Spawned from:** [[E2-276]]

# Dependencies
- **Blocks:** [[E2-280]]
- **Related:** [[E2-271]], [[INV-052]]

# ADRs
(none)

# Memory Concepts
- [[concept:80910]] - Portal system design
- [[concept:80911]]
- [[concept:80912]]
```

**Behavior:** WorkEngine creates `references/` directory and `REFS.md` on work item creation. Updates portal on relationship changes.

**Result:** ground-cycle can traverse `references/REFS.md` to find source investigations, load their architecture, and ensure plans are authored against correct specs.

---

## Tests First (TDD)

### Test 1: Portal directory created on work item creation
```python
def test_create_work_creates_references_directory(tmp_path):
    """WorkEngine.create_work creates references/ directory."""
    governance = GovernanceLayer()
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    engine.create_work("E2-TEST", "Test Work Item")

    refs_dir = tmp_path / "docs/work/active/E2-TEST/references"
    assert refs_dir.exists()
    assert refs_dir.is_dir()
```

### Test 2: REFS.md created with frontmatter
```python
def test_create_work_creates_refs_md(tmp_path):
    """WorkEngine.create_work creates REFS.md with frontmatter."""
    governance = GovernanceLayer()
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    engine.create_work("E2-TEST", "Test Work Item")

    refs_file = tmp_path / "docs/work/active/E2-TEST/references/REFS.md"
    assert refs_file.exists()
    content = refs_file.read_text()
    assert "type: portal-index" in content
    assert "work_id: E2-TEST" in content
```

### Test 3: Portal updated when spawned_by set
```python
def test_link_spawned_items_updates_portal(tmp_path):
    """link_spawned_items updates REFS.md with spawned_from."""
    governance = GovernanceLayer()
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Create work item
    engine.create_work("E2-TEST", "Test Work Item")

    # Link to parent
    engine.link_spawned_items("INV-050", ["E2-TEST"])

    refs_file = tmp_path / "docs/work/active/E2-TEST/references/REFS.md"
    content = refs_file.read_text()
    assert "INV-050" in content
    assert "Spawned from" in content
```

### Test 4: Portal includes memory_refs
```python
def test_add_memory_refs_updates_portal(tmp_path):
    """add_memory_refs updates REFS.md with memory concepts."""
    governance = GovernanceLayer()
    engine = WorkEngine(governance=governance, base_path=tmp_path)

    # Create work item
    engine.create_work("E2-TEST", "Test Work Item")

    # Add memory refs
    engine.add_memory_refs("E2-TEST", [80910, 80911])

    refs_file = tmp_path / "docs/work/active/E2-TEST/references/REFS.md"
    content = refs_file.read_text()
    assert "80910" in content
    assert "Memory" in content
```

---

## Detailed Design

### Component 1: Portal Template

**File:** `.claude/templates/portal_refs.md` (NEW)

```markdown
---
type: portal-index
work_id: {{WORK_ID}}
generated: {{DATE}}
last_updated: {{TIMESTAMP}}
---
# References: {{WORK_ID}}

## Provenance
{{#if spawned_from}}
- **Spawned from:** [[{{spawned_from}}]]
{{else}}
(no parent)
{{/if}}

## Dependencies
{{#if blocks}}
### Blocks
{{#each blocks}}
- [[{{this}}]]
{{/each}}
{{/if}}

{{#if related}}
### Related
{{#each related}}
- [[{{this}}]]
{{/each}}
{{/if}}

## ADRs
(none)

## Memory Concepts
{{#each memory_refs}}
- [[concept:{{this}}]]
{{/each}}
```

### Component 2: WorkEngine Changes

**File:** `.claude/haios/modules/work_engine.py`

#### Change 1: Create references directory in create_work()

**Location:** Lines 171-202 in `create_work()`

**Current Code (lines 171-176):**
```python
        work_dir = self.active_dir / id
        work_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (work_dir / "plans").mkdir(exist_ok=True)
```

**Changed Code:**
```python
        work_dir = self.active_dir / id
        work_dir.mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        (work_dir / "plans").mkdir(exist_ok=True)
        (work_dir / "references").mkdir(exist_ok=True)  # NEW: Portal directory

        # Create initial REFS.md
        self._create_portal(id, work_dir / "references" / "REFS.md")
```

#### Change 2: Add _create_portal() method

**New method after line 354:**

```python
    def _create_portal(self, id: str, refs_path: Path) -> None:
        """
        Create initial REFS.md portal file.

        Args:
            id: Work item ID
            refs_path: Path to REFS.md
        """
        now = datetime.now()
        content = f"""---
type: portal-index
work_id: {id}
generated: {now.strftime("%Y-%m-%d")}
last_updated: {now.isoformat()}
---
# References: {id}

## Provenance
(no parent)

## Dependencies
(none)

## ADRs
(none)

## Memory Concepts
(none)
"""
        refs_path.write_text(content, encoding="utf-8")

    def _update_portal(self, id: str, updates: Dict[str, Any]) -> None:
        """
        Update REFS.md portal file with new data.

        Args:
            id: Work item ID
            updates: Dict with keys: spawned_from, blocks, related, adrs, memory_refs
        """
        refs_path = self.active_dir / id / "references" / "REFS.md"
        if not refs_path.exists():
            return

        # Read current content
        content = refs_path.read_text(encoding="utf-8")
        parts = content.split("---", 2)
        if len(parts) < 3:
            return

        fm = yaml.safe_load(parts[1]) or {}
        fm["last_updated"] = datetime.now().isoformat()

        # Build sections
        sections = []
        sections.append(f"# References: {id}")
        sections.append("")

        # Provenance
        sections.append("## Provenance")
        spawned_from = updates.get("spawned_from") or fm.get("spawned_from")
        if spawned_from:
            sections.append(f"- **Spawned from:** [[{spawned_from}]]")
            fm["spawned_from"] = spawned_from
        else:
            sections.append("(no parent)")
        sections.append("")

        # Dependencies
        sections.append("## Dependencies")
        blocks = updates.get("blocks", [])
        related = updates.get("related", [])
        if blocks:
            sections.append("### Blocks")
            for b in blocks:
                sections.append(f"- [[{b}]]")
        if related:
            sections.append("### Related")
            for r in related:
                sections.append(f"- [[{r}]]")
        if not blocks and not related:
            sections.append("(none)")
        sections.append("")

        # ADRs
        sections.append("## ADRs")
        adrs = updates.get("adrs", [])
        if adrs:
            for a in adrs:
                sections.append(f"- [[{a}]]")
        else:
            sections.append("(none)")
        sections.append("")

        # Memory Concepts
        sections.append("## Memory Concepts")
        memory_refs = updates.get("memory_refs", [])
        if memory_refs:
            for m in memory_refs:
                sections.append(f"- [[concept:{m}]]")
        else:
            sections.append("(none)")

        # Write back
        new_fm = yaml.dump(fm, default_flow_style=False, sort_keys=False)
        new_content = f"---\n{new_fm}---\n" + "\n".join(sections) + "\n"
        refs_path.write_text(new_content, encoding="utf-8")
```

#### Change 3: Update link_spawned_items() to call _update_portal()

**Location:** Lines 395-438 in `link_spawned_items()`

**Add after line 433:**
```python
                # Update portal with spawned_from
                self._update_portal(work_id, {"spawned_from": spawned_by})
```

#### Change 4: Update add_memory_refs() to call _update_portal()

**Location:** Lines 330-354 in `add_memory_refs()`

**Add after line 350:**
```python
        # Update portal with memory refs
        self._update_portal(id, {"memory_refs": work.memory_refs})
```

### Call Chain Context

```
/new-work E2-XXX
    |
    +-> cli.py scaffold work_item
            |
            +-> WorkEngine.create_work()
                    |
                    +-> mkdir plans/
                    +-> mkdir references/       # NEW
                    +-> _create_portal()        # NEW
                    +-> write WORK.md

link_spawned_items(spawned_by, [id])
    |
    +-> update WORK.md frontmatter
    +-> _update_portal()                        # NEW

add_memory_refs(id, concept_ids)
    |
    +-> update WORK.md memory_refs
    +-> _update_portal()                        # NEW
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Portal as separate file vs frontmatter | Separate `REFS.md` file | S2C spec defines portal as separate file; enables future extensions like memory-refs.md |
| Wikilink syntax `[[ID]]` | Match S2C spec | Obsidian-compatible, human readable |
| Update portal on link operations | Call _update_portal in link_spawned_items, add_memory_refs | Keep portal synchronized with WORK.md relationships |
| Sections match S2C | Provenance, Dependencies, ADRs, Memory | Direct implementation of S2C portal types |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| references/ directory already exists | mkdir exist_ok=True | Test 1 (implicit) |
| REFS.md doesn't exist on update | Return early, no error | Test 3 (creates first) |
| Empty memory_refs list | Show "(none)" | Test 4 |
| Work item archived | Portal moves with directory | Existing archive() behavior |

### Open Questions

**Q: Should portal be updated on transition() (node changes)?**

Answer: No. Node changes are state machine transitions. Portal tracks relationships (provenance, dependencies), not state. This matches S2C's "portals link to other universes" design.

---

## Open Decisions (MUST resolve before implementation)

<!-- No operator_decisions in work item - section is clean -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| *No open decisions* | - | - | Work item operator_decisions is empty |

---

## Implementation Steps

### Step 1: Write Failing Tests
- [ ] Add 4 tests to `tests/test_work_engine.py`
- [ ] Run `pytest tests/test_work_engine.py -v -k portal` - all 4 fail

### Step 2: Add _create_portal() Method
- [ ] Add `_create_portal()` method to WorkEngine
- [ ] Tests 1, 2 still fail (create_work not updated)

### Step 3: Update create_work() to Create Portals
- [ ] Add `(work_dir / "references").mkdir()` line
- [ ] Add `self._create_portal()` call
- [ ] Tests 1, 2 should pass

### Step 4: Add _update_portal() Method
- [ ] Add `_update_portal()` method to WorkEngine
- [ ] Tests 3, 4 still fail (not called yet)

### Step 5: Update link_spawned_items() to Update Portal
- [ ] Add `self._update_portal(work_id, {"spawned_from": spawned_by})` after frontmatter update
- [ ] Test 3 should pass

### Step 6: Update add_memory_refs() to Update Portal
- [ ] Add `self._update_portal(id, {"memory_refs": work.memory_refs})` after memory_refs update
- [ ] Test 4 should pass

### Step 7: Run Full Test Suite
- [ ] Run `pytest tests/test_work_engine.py -v` - all tests pass
- [ ] Run `pytest tests/` - no regressions

### Step 8: README Sync (MUST)
- [ ] **MUST:** Update `.claude/haios/modules/README.md` to document portal methods
- [ ] **MUST:** Verify README content matches actual file state

### Step 9: Update S2C Architecture Doc
- [ ] Update `.claude/haios/epochs/E2/architecture/S2C-work-item-directory.md` to note implementation status
- [ ] Mark portal system as "Implemented in WorkEngine"

---

## Verification

- [ ] Tests pass
- [ ] **MUST:** All READMEs current (upstream and downstream of changes)
- [ ] Code review complete

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Spec misalignment: Portal format doesn't match S2C | High | Detailed Design mirrors S2C exactly |
| Integration: ground-cycle can't parse portal | Medium | Tests verify portal format; E2-280 will implement traversal |
| Regression: Existing create_work callers break | Low | Additive change only (new directory, new file) |
| Scope creep: Adding portal features not in S2C | Low | Design constrained to S2C portal types only |
| Knowledge gap: Unsure about wikilink parsing | Low | Format is text-based; ground-cycle reads as markdown |

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

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/haios/modules/work_engine.py` | Has `_create_portal()`, `_update_portal()` methods | [ ] | |
| `tests/test_work_engine.py` | Has 4 portal tests, all pass | [ ] | |
| `.claude/haios/modules/README.md` | **MUST:** Documents portal methods | [ ] | |
| `.claude/haios/epochs/E2/architecture/S2C-work-item-directory.md` | Notes portal as implemented | [ ] | |

**Verification Commands:**
```bash
# Paste actual output when verifying
pytest tests/test_work_engine.py -v -k portal
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
- [ ] **Runtime consumer exists** (code is called by system, not just tests)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in all modified directories (upstream and downstream)
- [ ] **MUST:** Consumer verification complete (for migrations: zero stale references)
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

> **E2-250 Learning:** "Tests pass" proves code works. "Runtime consumer exists" proves code is used. Code without consumers is a prototype, not done.

---

## References

- `.claude/haios/epochs/E2/architecture/S2C-work-item-directory.md` - Portal system design (PRIMARY)
- `.claude/haios/epochs/E2/EPOCH.md` - Epoch architecture
- `.claude/haios/epochs/E2/architecture/S17-modular-architecture.md` - WorkEngine interface
- `.claude/haios/modules/work_engine.py` - Implementation target
- `docs/work/active/E2-276/plans/PLAN.md` - ground-cycle design (portal consumer)
- `docs/checkpoints/2026-01-06-01-SESSION-177-epoch-chapter-arc-hierarchy-and-ground-cycle-discovery.md` - Discovery session

---
