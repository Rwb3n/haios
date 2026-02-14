---
template: implementation_plan
status: approved
date: 2026-02-14
backlog_id: WORK-075
title: "System Audit as L4 Traceability Verification"
author: Hephaestus
lifecycle_phase: plan
session: 370
version: "1.5"
generated: 2026-02-14
last_updated: 2026-02-14T15:39:01
---
# Implementation Plan: System Audit as L4 Traceability Verification

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

The E2.6 system audit (`system-audit-S365.md`) will have L4 Coverage, Decision Coverage, and Gap Analysis sections that enable bidirectional traceability verification from L4 requirements through to work items, and from epoch decisions through to chapters.

---

## Effort Estimation (Ground Truth)

> **MUST** be based on actual file/code analysis, not guesses.

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/haios/epochs/E2_6/system-audit-S365.md` (662 lines) |
| New files to create | 1 | `scripts/audit_l4_coverage.py` (automation script) |
| Tests to write | 4 | Automation script validation |
| L4 requirements to map | 68 | `grep -oP 'REQ-...' functional_requirements.md \| sort -u` |
| E2.4 decisions to map | 8 | Decisions 1-8 in E2.4/EPOCH.md |
| Work items to cross-reference | 121 | Active WORK.md files with `traces_to:` field |
| Dependencies | 0 | No module imports this — standalone audit document + script |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Standalone document + script, no module coupling |
| Risk of regression | Low | No existing code modified; new script only |
| External dependencies | Low | Reads filesystem only, no MCP/API calls |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Write automation script | 30 min | High |
| Write tests | 15 min | High |
| Run script, produce coverage tables | 10 min | High |
| Add sections to system-audit-S365.md | 15 min | High |
| Write gap analysis narrative | 10 min | High |
| **Total** | ~80 min | High |

---

## Current State vs Desired State

### Current State

The E2.6 system audit (`system-audit-S365.md`, 662 lines) is a comprehensive **inventory** covering 20 sections: skills (34), agents (11), templates (37), recipes (71), hooks (6), commands (19), Python code (45 files), work items (128), and more. It answers "what exists?" but not:

- "Does what exists satisfy L4 requirements?"
- "Which L4 requirements have no implementation?"
- "Which epoch decisions have no chapter assignment?"

The `Implemented By` column in `functional_requirements.md` has informal text like "WORK.md template" or "WorkEngine" — not machine-parseable work item IDs. There is no reverse mapping from work items back to requirements.

Separately, `just audit-decision-coverage` exists (lib/audit_decision_coverage.py, 385 lines) but validates E2.4 decisions-to-chapters only — not L4 requirements-to-work-items.

### Desired State

The system audit gains 3 new sections appended after the existing content:

1. **L4 Coverage** — Table mapping all 68 L4 requirements to implementing work items (via `traces_to:` frontmatter) and their status
2. **Decision Coverage** — Table mapping all 8 E2.4 decisions to chapters/arcs (via epoch and arc definitions)
3. **Gap Analysis** — Lists requirements with no work items and decisions with no chapters

A new script `scripts/audit_l4_coverage.py` generates these tables programmatically, enabling `just audit-l4-coverage` to regenerate on demand.

---

## Tests First (TDD)

Tests for `scripts/audit_l4_coverage.py` in `tests/test_audit_l4_coverage.py`.

### Test 1: Parse traces_to from WORK.md frontmatter
```python
def test_parse_traces_to_extracts_requirement_ids():
    work_content = "---\nid: WORK-075\ntraces_to:\n- REQ-TRACE-005\nstatus: complete\n---\n# Title\n"
    result = parse_traces_to(work_content)
    assert result == {"id": "WORK-075", "traces_to": ["REQ-TRACE-005"], "status": "complete"}
```

### Test 2: Build L4 coverage map from work items
```python
def test_build_l4_coverage_maps_requirements_to_work_items():
    work_items = [
        {"id": "WORK-001", "traces_to": ["REQ-TRACE-001", "REQ-TRACE-002"], "status": "complete"},
        {"id": "WORK-002", "traces_to": ["REQ-TRACE-001"], "status": "active"},
    ]
    all_req_ids = ["REQ-TRACE-001", "REQ-TRACE-002", "REQ-TRACE-003"]
    coverage = build_l4_coverage(work_items, all_req_ids)
    assert coverage["REQ-TRACE-001"] == [("WORK-001", "complete"), ("WORK-002", "active")]
    assert coverage["REQ-TRACE-002"] == [("WORK-001", "complete")]
    assert coverage["REQ-TRACE-003"] == []  # Gap
```

### Test 3: Parse epoch decisions
```python
def test_parse_epoch_decisions_extracts_all_decisions():
    epoch_content = "## Core Decisions\n\n### Decision 1: Five-Layer Hierarchy\n\nSome text\n\n### Decision 2: Work Classification\n\nMore text\n"
    decisions = parse_epoch_decisions(epoch_content)
    assert len(decisions) == 2
    assert decisions["D1"]["title"] == "Five-Layer Hierarchy"
    assert decisions["D2"]["title"] == "Work Classification"
```

### Test 4: Gap analysis identifies uncovered requirements
```python
def test_gap_analysis_finds_uncovered_requirements():
    coverage = {
        "REQ-TRACE-001": [("WORK-001", "complete")],
        "REQ-TRACE-002": [],
        "REQ-OBSERVE-001": [],
    }
    gaps = find_gaps(coverage)
    assert "REQ-TRACE-002" in gaps
    assert "REQ-OBSERVE-001" in gaps
    assert "REQ-TRACE-001" not in gaps
```

---

## Detailed Design

This is a **documentation + automation** task. The primary artifact is markdown sections appended to `system-audit-S365.md`. The secondary artifact is a Python script that generates the coverage data programmatically.

### Component 1: `scripts/audit_l4_coverage.py`

New standalone script (follows pattern of existing `scripts/plan_tree.py`).

```python
"""L4 requirement coverage audit for HAIOS.

Scans all work items for traces_to fields, cross-references with L4 requirement
registry, and produces coverage tables + gap analysis.

Usage:
    python scripts/audit_l4_coverage.py
    python scripts/audit_l4_coverage.py --format markdown  # default
    python scripts/audit_l4_coverage.py --format summary   # counts only
"""
import re
import yaml
from pathlib import Path


def parse_traces_to(work_content: str) -> dict:
    """Extract id, traces_to, and status from WORK.md frontmatter.
    Returns traces_to=[] if field is missing (legacy items)."""

def parse_all_work_items(work_dir: Path) -> list[dict]:
    """Scan all WORK.md files in work_dir for traces_to mappings.
    Includes both active/ and archive/ directories."""

def parse_l4_requirement_ids(req_file: Path) -> list[str]:
    """Extract all unique REQ-*-NNN IDs from functional_requirements.md."""

def build_l4_coverage(work_items: list[dict], all_req_ids: list[str]) -> dict:
    """Map each requirement ID to list of (work_id, status) tuples."""

def parse_epoch_decisions(epoch_content: str) -> dict:
    """Extract decision ID, title from EPOCH.md Decision headers."""

def find_gaps(coverage: dict) -> list[str]:
    """Return requirement IDs with no implementing work items."""

def format_l4_coverage_table(coverage: dict) -> str:
    """Render L4 coverage as markdown table."""

def format_decision_coverage_table(decisions: dict, arcs: dict) -> str:
    """Render decision-to-arc/chapter mapping as markdown table."""

def format_gap_analysis(req_gaps: list[str], decision_gaps: list[str]) -> str:
    """Render gap analysis as markdown section."""

def format_data_quality_summary(total_items: int, with_traces: int, without_traces: int) -> str:
    """Render data quality summary showing traces_to field coverage."""

def main():
    """Run full audit and print markdown output including data quality summary."""
```

### Component 2: Sections appended to `system-audit-S365.md`

Three new sections appended after existing section 20:

**Section 21: L4 Requirement Coverage**
```markdown
## 21. L4 Requirement Coverage

| Requirement | Domain | Work Items | Status |
|-------------|--------|------------|--------|
| REQ-TRACE-001 | Traceability | WORK-015, WORK-025, ... | Implemented |
| REQ-OBSERVE-005 | Observability | WORK-146 | Planning |
| REQ-ASSET-004 | Asset | - | Gap |
```

Status logic:
- "Implemented" = at least one work item with `status: complete`
- "In Progress" = work items exist but none complete
- "Gap" = no work items trace to this requirement

Data quality note: Many legacy work items (E2-xxx, INV-xxx, CH-xxx) lack `traces_to` field entirely. The script reports a data quality summary showing what percentage of items have the field. "Gap" means no items *with traces_to* reference this requirement — not necessarily that no implementation exists.

**Section 22: E2.4 Decision Coverage**
```markdown
## 22. E2.4 Decision Coverage

| Decision | Title | Arcs/Chapters | Status |
|----------|-------|---------------|--------|
| D1 | Five-Layer Hierarchy | discoverability/CH-032 | Partial |
| D7 | Four-Dimensional State | - | Gap |
```

**Section 23: Gap Analysis**
```markdown
## 23. Gap Analysis

### L4 Requirements Without Implementation
- REQ-ASSET-004: Asset schema is lifecycle-specific — No work item traces to this

### Epoch Decisions Without Chapters
- D7: Four-Dimensional State — No chapter assigned
```

### Component 3: justfile recipe

```just
# Audit: L4 requirement coverage against work items
audit-l4-coverage:
    @python scripts/audit_l4_coverage.py
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Standalone script in `scripts/` | Not in `lib/` or `modules/` | This is a one-off audit tool, not a runtime module. Follows `plan_tree.py` pattern. |
| Parse `traces_to:` from YAML frontmatter | Not query memory or database | Frontmatter is the authoritative source (REQ-TRACE-001). No MCP dependency. |
| Target E2.6 audit, not E2.4 | Append to `system-audit-S365.md` | E2.4 SYSTEM-AUDIT.md is closed epoch. E2.6 is current and has the comprehensive inventory. |
| Status derived from work item `status` field | Not `current_node` | `status` is ADR-041 authoritative (REQ-WORK-002). `current_node` has known drift (97% stuck at backlog). |
| Decision coverage uses arc/chapter definitions | Not `assigned_to` field in EPOCH.md | E2.4 decisions predate the `assigned_to` schema (WORK-069). Arc/chapter definitions in E2.6 are the actual mappings. |

### Edge Cases

| Case | Handling | Test Coverage |
|------|----------|---------------|
| Work item has empty `traces_to: []` | Skip, don't count as implementing anything | Test 1 |
| Work item in archive directory | Include — archived items are still valid implementations | parse_all_work_items scans archive/ too |
| Requirement ID in `traces_to` doesn't match registry | Flag as warning in output, don't count as coverage | Gap analysis |
| Decision has no matching arc structure | Report as gap | Test 3 |

### Open Questions

**Q: Should the script also update system-audit-S365.md in-place?**

No. The script outputs markdown to stdout. The agent appends the output manually. This keeps the script side-effect-free and avoids accidental overwrites.

---

## Open Decisions (MUST resolve before implementation)

No `operator_decisions` in WORK-075 frontmatter. No blocking decisions.

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Target audit file | E2.4 SYSTEM-AUDIT.md, E2.6 system-audit-S365.md | E2.6 system-audit-S365.md | E2.4 is closed epoch. E2.6 is current, comprehensive (20 sections). |

---

## Implementation Steps

### Step 1: Write Failing Tests (RED)
- [ ] Create `tests/test_audit_l4_coverage.py`
- [ ] Write tests 1-4 from Tests First section
- [ ] Verify all 4 tests fail

### Step 2: Implement `scripts/audit_l4_coverage.py` (GREEN)
- [ ] Implement `parse_traces_to()` — Tests 1 passes
- [ ] Implement `build_l4_coverage()` + `find_gaps()` — Tests 2, 4 pass
- [ ] Implement `parse_epoch_decisions()` — Test 3 passes
- [ ] Implement formatting functions and `main()`

### Step 3: Run script, capture output
- [ ] Run `python scripts/audit_l4_coverage.py` to generate markdown
- [ ] Review output for accuracy (spot-check 5+ requirements)

### Step 4: Append sections to system-audit-S365.md
- [ ] Append Section 21: L4 Requirement Coverage table
- [ ] Append Section 22: E2.4 Decision Coverage table
- [ ] Append Section 23: Gap Analysis narrative

### Step 5: Add justfile recipe
- [ ] Add `audit-l4-coverage` recipe to justfile

### Step 6: Integration Verification
- [ ] All 4 new tests pass
- [ ] Run full test suite (no regressions)
- [ ] Run `just audit-l4-coverage` to verify recipe works

### Step 7: Consumer Verification
- [ ] **SKIPPED:** No migration/rename — new files only, no consumers to update

---

## Verification

- [ ] 4 new tests pass (`tests/test_audit_l4_coverage.py`)
- [ ] Full test suite passes (no regressions)
- [ ] `just audit-l4-coverage` produces valid markdown output
- [ ] system-audit-S365.md has sections 21, 22, 23 with real data

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| `traces_to:` field inconsistently populated across work items | Medium | Script handles empty/missing gracefully; gap analysis surfaces the problem rather than hiding it |
| E2.4 decision format doesn't match parser expectations | Low | Test 3 validates against real EPOCH.md content; regex pattern matches actual headers |
| Coverage data becomes stale as work progresses | Low | `just audit-l4-coverage` regenerates on demand; sections can be refreshed |
| Scope creep into fixing gaps (not just identifying them) | Medium | Plan explicitly scopes to reporting only; fixes are separate work items |

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

**MUST** read `docs/work/active/WORK-075/WORK.md` and verify ALL deliverables:

| Deliverable | Complete | Evidence |
|-------------|----------|----------|
| L4 Coverage section — Maps each L4 requirement to work items and artifacts | [ ] | Section 21 in system-audit-S365.md |
| Decision Coverage section — Maps each E2.4 decision to chapters | [ ] | Section 22 in system-audit-S365.md |
| Gap Analysis section — Lists requirements and decisions without implementation | [ ] | Section 23 in system-audit-S365.md |
| Automation consideration — Document how `just audit-l4-coverage` could generate these sections | [ ] | Script exists at `scripts/audit_l4_coverage.py`, recipe in justfile |

> **Anti-pattern prevented:** "Tests pass = Done" (E2-290). Tests verify code works. Deliverables verify scope is complete. Both required.

### File Verification

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `scripts/audit_l4_coverage.py` | Script with 7+ functions, produces markdown | [ ] | |
| `tests/test_audit_l4_coverage.py` | 4 tests, all pass | [ ] | |
| `.claude/haios/epochs/E2_6/system-audit-S365.md` | Sections 21-23 appended | [ ] | |
| `justfile` | `audit-l4-coverage` recipe added | [ ] | |

**Verification Commands:**
```bash
pytest tests/test_audit_l4_coverage.py -v
# Expected: 4 tests passed
python scripts/audit_l4_coverage.py
# Expected: markdown tables with 68 requirements, 8 decisions
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

- @docs/work/active/WORK-075/WORK.md (work item)
- @.claude/haios/manifesto/L4/functional_requirements.md (68 L4 requirements — source of truth)
- @.claude/haios/epochs/E2_4/EPOCH.md (8 decisions — Decision 1-8)
- @.claude/haios/epochs/E2_6/system-audit-S365.md (target file, 662 lines, 20 sections)
- @.claude/haios/lib/audit_decision_coverage.py (existing decision audit — pattern reference)
- @scripts/plan_tree.py (existing scripts/ pattern reference)
- Memory 84990: "Verification-heavy work needs a lightweight plan option"
- Memory 85297: "Include enum-consistency lint in audit system once schemas centralized"

---
