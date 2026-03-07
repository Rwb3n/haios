---
id: assets
epoch: E2.5
theme: Implement typed, versioned asset production
status: Planned
chapters:
- id: CH-023
  title: LifecycleAssetTypes
  work_items: []
  requirements: []
  dependencies: []
  status: REQ-ASSET-001
- id: CH-024
  title: AssetVersioning
  work_items: []
  requirements: []
  dependencies: []
  status: REQ-ASSET-002
- id: CH-025
  title: AssetPiping
  work_items: []
  requirements: []
  dependencies: []
  status: REQ-ASSET-003
- id: CH-026
  title: AssetSchemas
  work_items: []
  requirements: []
  dependencies: []
  status: REQ-ASSET-004
- id: CH-027
  title: AssetProvenance
  work_items: []
  requirements: []
  dependencies: []
  status: REQ-ASSET-005
exit_criteria:
- text: Asset schema defined per lifecycle
  checked: false
- text: Provenance frontmatter on all assets
  checked: false
- text: Version tracking (edit creates v2, not overwrites v1)
  checked: false
- text: 'Piping works: `investigation | design`'
  checked: false
- text: 'Storing works: `investigation > findings.md`'
  checked: false
---
# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T01:00:58
# Arc: Assets

## Definition

**Arc ID:** assets
**Epoch:** E2.5
**Theme:** Implement typed, versioned asset production
**Status:** Planned

---

## Purpose

Implement Unix-pipe-style asset production per REQ-ASSET-001 to 005.

---

## Requirements Implemented

| Requirement | Description |
|-------------|-------------|
| REQ-ASSET-001 | Each lifecycle produces typed, immutable asset |
| REQ-ASSET-002 | Assets versioned, not edited (append-only) |
| REQ-ASSET-003 | Assets can be piped to next lifecycle OR stored |
| REQ-ASSET-004 | Asset schema is lifecycle-specific |
| REQ-ASSET-005 | Assets have provenance |

---

## Asset Types

| Lifecycle | Asset Type | Format |
|-----------|------------|--------|
| Investigation | Findings | markdown |
| Design | Specification | markdown (TRD) |
| Implementation | Artifact | mixed |
| Validation | Verdict | markdown |
| Triage | Priority List | yaml |

---

## Chapters

| CH-ID | Title | Requirements | Dependencies |
|-------|-------|--------------|--------------|
| CH-023 | LifecycleAssetTypes | REQ-ASSET-001 | Lifecycles:CH-001 |
| CH-024 | AssetVersioning | REQ-ASSET-002 | CH-023 |
| CH-025 | AssetPiping | REQ-ASSET-003 | CH-023, Lifecycles:CH-004 |
| CH-026 | AssetSchemas | REQ-ASSET-004 | CH-023 |
| CH-027 | AssetProvenance | REQ-ASSET-005 | CH-023 |

---

## Exit Criteria

- [ ] Asset schema defined per lifecycle
- [ ] Provenance frontmatter on all assets
- [ ] Version tracking (edit creates v2, not overwrites v1)
- [ ] Piping works: `investigation | design`
- [ ] Storing works: `investigation > findings.md`
