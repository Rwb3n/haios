# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T19:44:32
# Chapter: Lifecycle Asset Types

## Definition

**Chapter ID:** CH-023
**Arc:** assets
**Status:** Planned
**Implementation Type:** CREATE NEW
**Depends:** Lifecycles:CH-001
**Work Items:** WORK-093

---

## Current State (Verified)

**Source:** Codebase search

No Asset classes exist:
- No `asset*.py` files
- No `class Asset` definitions
- No typed lifecycle outputs

**What exists:**
- Lifecycle outputs are markdown files in work directories
- Investigation outputs in `docs/work/active/*/` as markdown
- No structured Asset type

**What doesn't exist:**
- Asset base class
- FindingsAsset, SpecificationAsset, etc.
- AssetStore
- to_markdown(), to_dict() methods

---

## Asset Structure Decision (Resolves CH-023/CH-027 Conflict)

**DECISION:** Use flat structure with all provenance fields in base class.

```python
@dataclass
class Asset:
    """Base class for all lifecycle assets - flat structure."""
    # Identity
    asset_id: str           # UUID or deterministic ID
    type: str               # findings, specification, etc.

    # Provenance (from CH-027)
    produced_by: str        # lifecycle name
    source_work: str        # WORK-XXX
    version: int
    timestamp: datetime
    author: str
    inputs: List[str] = field(default_factory=list)
    piped_from: Optional['AssetRef'] = None

    # Methods
    def to_markdown(self) -> str: ...
    def to_dict(self) -> Dict: ...
```

**NOT** the wrapper pattern from CH-027:
```python
# REJECTED - too much indirection
class Asset:
    provenance: Provenance  # Wrapper
    content: Any
```

This decision propagates to CH-027 which must be updated to match.

---

## Problem

Lifecycles return ad-hoc output. Need typed Asset classes for consistent piping and storage.

---

## Agent Need

> "I need each lifecycle to produce a typed asset so I know exactly what format the output will be and can reliably pipe or store it."

---

## Requirements

### R1: Typed Asset Per Lifecycle (REQ-ASSET-001)

Each lifecycle produces specific asset type:

| Lifecycle | Asset Type | Python Class |
|-----------|------------|--------------|
| Investigation | Findings | `FindingsAsset` |
| Design | Specification | `SpecificationAsset` |
| Implementation | Artifact | `ArtifactAsset` |
| Validation | Verdict | `VerdictAsset` |
| Triage | PriorityList | `PriorityListAsset` |

### R2: Asset Base Class

```python
@dataclass
class Asset:
    """Base class for all lifecycle assets."""
    type: str
    produced_by: str  # lifecycle name
    source_work: str  # WORK-XXX
    version: int
    timestamp: datetime
    author: str

    def to_markdown(self) -> str:
        """Serialize to markdown with frontmatter."""

    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
```

### R3: Lifecycle Return Type

CycleRunner.run() returns typed asset:

```python
def run(work_id: str, lifecycle: str) -> Asset:
    """
    Run lifecycle and return typed asset.

    Returns:
        Asset subclass appropriate to lifecycle
    """
```

---

## Interface

### Asset Classes

```python
@dataclass
class FindingsAsset(Asset):
    type: str = "findings"
    question: str
    findings: List[Finding]
    conclusion: str
    evidence: List[str]

@dataclass
class SpecificationAsset(Asset):
    type: str = "specification"
    requirements: List[str]
    design_decisions: List[Decision]
    interface: str
    success_criteria: List[str]

@dataclass
class ArtifactAsset(Asset):
    type: str = "artifact"
    files_created: List[Path]
    files_modified: List[Path]
    entry_point: Path
    test_results: TestResults

@dataclass
class VerdictAsset(Asset):
    type: str = "verdict"
    passed: bool
    criteria_results: List[CriterionResult]
    evidence: List[str]

@dataclass
class PriorityListAsset(Asset):
    type: str = "priority_list"
    items: List[PrioritizedItem]
    rationale: str
```

### CycleRunner Integration

```python
# Before (untyped)
result = cycle_runner.run(work_id, "investigation")
# result is Dict with unknown structure

# After (typed)
findings: FindingsAsset = cycle_runner.run(work_id, "investigation")
# findings has known attributes: .question, .findings, .conclusion
```

---

## Success Criteria

- [ ] Asset base class defined
- [ ] 5 asset subclasses (one per lifecycle)
- [ ] CycleRunner.run() returns typed Asset
- [ ] Each asset has to_markdown() serialization
- [ ] Each asset has to_dict() serialization
- [ ] Type hints on all public methods
- [ ] Unit tests for each asset class
- [ ] Integration test: lifecycle produces correct asset type

---

## Non-Goals

- Asset storage (see CH-025)
- Asset versioning (see CH-024)
- Asset schemas (see CH-026)

---

## References

- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-ASSET-001)
- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-001-LifecycleSignature.md (lifecycle signatures)
