---
template: work_item
id: WORK-093
title: Implement Lifecycle Asset Types (CH-023)
type: feature
status: active
owner: Hephaestus
created: 2026-02-03
spawned_by: E2.5-decomposition
chapter: CH-023-LifecycleAssetTypes
arc: assets
closed: null
priority: high
effort: medium
traces_to:
- REQ-ASSET-001
requirement_refs: []
source_files:
- .claude/haios/modules/
acceptance_criteria:
- Asset base class defined with flat provenance fields
- 5 asset subclasses created (Findings, Specification, Artifact, Verdict, PriorityList)
- CycleRunner.run() returns typed Asset
- Each asset has to_markdown() serialization
- Each asset has to_dict() serialization
blocked_by:
- WORK-084
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-02-03 19:30:00
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions:
  epoch: E2.5
  implementation_type: CREATE_NEW
version: '2.0'
generated: 2026-02-03
last_updated: '2026-02-03T19:44:01'
---
# WORK-093: Implement Lifecycle Asset Types (CH-023)

---

## Context

Lifecycles return ad-hoc output. Need typed Asset classes for consistent piping and storage. This is a prerequisite for WORK-084's typed output requirement.

**Current State:**
- No Asset classes exist
- No `asset*.py` files
- No typed lifecycle outputs
- Lifecycle outputs are markdown files in work directories

**Decision (from CH-023):** Use flat structure with all provenance fields in base class, NOT wrapper pattern.

```python
@dataclass
class Asset:
    """Base class for all lifecycle assets - flat structure."""
    asset_id: str
    type: str
    produced_by: str  # lifecycle name
    source_work: str  # WORK-XXX
    version: int
    timestamp: datetime
    author: str
    inputs: List[str] = field(default_factory=list)
    piped_from: Optional['AssetRef'] = None
```

---

## Deliverables

- [ ] Create .claude/haios/modules/assets.py
- [ ] Define Asset base dataclass with flat provenance
- [ ] Define FindingsAsset(Asset) with question, findings, conclusion, evidence
- [ ] Define SpecificationAsset(Asset) with requirements, design_decisions, interface
- [ ] Define ArtifactAsset(Asset) with files_created, files_modified, test_results
- [ ] Define VerdictAsset(Asset) with passed, criteria_results, evidence
- [ ] Define PriorityListAsset(Asset) with items, rationale
- [ ] Implement to_markdown() on each class
- [ ] Implement to_dict() on each class
- [ ] Unit tests for each asset class
- [ ] Integration test: lifecycle produces correct asset type

---

## History

### 2026-02-03 - Created (Session 297)
- Decomposed from E2.5 CH-023-LifecycleAssetTypes
- Cross-arc dependency: required by lifecycles arc WORK-084

---

## References

- @.claude/haios/epochs/E2_5/arcs/assets/CH-023-LifecycleAssetTypes.md
- @.claude/haios/epochs/E2_5/arcs/lifecycles/CH-001-LifecycleSignature.md (consumer)
- @.claude/haios/manifesto/L4/functional_requirements.md (REQ-ASSET-001)
