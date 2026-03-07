---
id: Migration
name: E2 Artifact Triage
epoch: E2.3 (The Pipeline)
status: Planned
chapters:
- id: CH-001
  title: ArchitectureTriage
  work_items: []
  requirements: []
  dependencies: []
  status: Planned
- id: CH-002
  title: ArcTriage
  work_items: []
  requirements: []
  dependencies: []
  status: Planned
- id: CH-003
  title: WorkItemTriage
  work_items: []
  requirements: []
  dependencies: []
  status: Planned
- id: CH-004
  title: RecipeAudit
  work_items: []
  requirements: []
  dependencies: []
  status: Planned
- id: CH-005
  title: MigrationManifest
  work_items: []
  requirements: []
  dependencies: []
  status: Planned
exit_criteria:
- text: Migration manifest created
  checked: false
- text: E2 arcs triaged
  checked: false
- text: Active work items dispositioned
  checked: false
- text: E2 archived to `epochs/archive/E2/`
  checked: false
---
# generated: 2026-01-18
# System Auto: last updated on: 2026-01-18T16:51:58
# Arc: Migration

## Arc Definition

**Arc ID:** Migration
**Epoch:** E2.3 (The Pipeline)
**Name:** E2 Artifact Triage
**Status:** Planned
**Pressure:** [volumous] - thematic exploration

---

## Theme

Triage E2 artifacts. Decide what transfers to E2.3, what archives.

**Principle:** Context persists through references, not copies.

---

## Chapters

| Chapter | Name | Status | Purpose |
|---------|------|--------|---------|
| CH-001 | ArchitectureTriage | Planned | Which S1-S26 docs transfer vs archive |
| CH-002 | ArcTriage | Planned | Which E2 arcs/chapters are pipeline-relevant |
| CH-003 | WorkItemTriage | Planned | Active work items: reframe or archive |
| CH-004 | RecipeAudit | Planned | 70+ recipes: keep generic, remove HAIOS-specific |
| CH-005 | MigrationManifest | Planned | Document all decisions with rationale |

---

## Triage Categories

| Category | Action | Example |
|----------|--------|---------|
| **Pipeline-relevant** | Transfer to E2.3 | S26, S20, Ground arc |
| **Reusable-infra** | Keep, reference | Memory system, hooks |
| **HAIOS-specific** | Archive with summary | E2-235, INV-054 |
| **Obsolete** | Archive, no action | Completed work |

---

## Exit Criteria

- [ ] Migration manifest created
- [ ] E2 arcs triaged
- [ ] Active work items dispositioned
- [ ] E2 archived to `epochs/archive/E2/`

---

## References

- @.claude/haios/epochs/E2/EPOCH.md (source)
- @.claude/haios/epochs/E2/arcs/ (to triage)
- @docs/work/active/ (to triage)
