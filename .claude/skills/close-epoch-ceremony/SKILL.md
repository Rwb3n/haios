---
name: close-epoch-ceremony
description: HAIOS Close Epoch Ceremony for verifying epoch DoD. Use when all arcs
  are complete. Guides VALIDATE->ARCHIVE->TRANSITION workflow.
recipes:
- audit-decision-coverage
generated: 2026-02-02
last_updated: '2026-02-02T15:41:21'
---
# Close Epoch Ceremony

This skill defines the VALIDATE-ARCHIVE-TRANSITION cycle for closing epochs and transitioning to a new epoch.

## When to Use

**Manual invocation:** `Skill(skill="close-epoch-ceremony")` when all arcs in an epoch are complete and you want to transition to a new epoch.

**Rare:** Epochs are long-lived containers. This ceremony is invoked infrequently (e.g., E2.3 -> E2.4 transition).

---

## The Cycle

```
VALIDATE --> ARCHIVE --> TRANSITION
```

### 1. VALIDATE Phase

**On Entry:**
```bash
just set-cycle close-epoch-ceremony VALIDATE {epoch_id}
```

**Goal:** Verify epoch meets Definition of Done criteria.

**DoD Criteria:**
- [ ] All arcs have `**Status:** Complete`
- [ ] All epoch decisions have implementations (via audit-decision-coverage)
- [ ] Epoch exit criteria (in EPOCH.md) all checked

**Actions:**
1. Read epoch file: `.claude/haios/epochs/{epoch_id}/EPOCH.md`
2. Glob arc files: `.claude/haios/epochs/{epoch_id}/arcs/*/ARC.md`
3. For each arc file, verify `**Status:** Complete`
4. Run audit-decision-coverage and verify all epoch decisions are implemented:
   ```bash
   just audit-decision-coverage
   ```
   **Expectation:** No orphan decisions, no unimplemented decisions.
5. Check epoch Exit Criteria section - all checkboxes must be `[x]`

**Exit Criteria:**
- [ ] All arcs have `**Status:** Complete`
- [ ] All decisions implemented (no audit errors)
- [ ] All Exit Criteria checkboxes checked

**On Failure:** Report which criteria failed. Do not proceed to ARCHIVE.

**Tools:** Read, Glob, Bash(just audit-decision-coverage)

---

### 2. ARCHIVE Phase

**On Entry:**
```bash
just set-cycle close-epoch-ceremony ARCHIVE {epoch_id}
```

**Goal:** Mark epoch complete and archive work items.

**Actions:**
1. Edit EPOCH.md file
2. Update `**Status:** Active` to `**Status:** Complete`
3. Add completion line after Status:
   ```markdown
   **Completed:** {YYYY-MM-DD} (Session {N})
   ```
4. Move work items from `docs/work/active/` to `docs/work/archive/{epoch_id}/` (per ADR-041: epoch-level cleanup)
   ```bash
   # Create archive directory
   mkdir -p docs/work/archive/{epoch_id}
   # Move completed work items
   mv docs/work/active/* docs/work/archive/{epoch_id}/
   ```
   **Note:** Only move items with `status: complete`. Items with `status: active` remain for the new epoch.

**Exit Criteria:**
- [ ] Epoch file has `**Status:** Complete`
- [ ] Completion timestamp added
- [ ] Completed work items archived

**Tools:** Edit, Bash(mkdir, mv)

---

### 3. TRANSITION Phase

**On Entry:**
```bash
just set-cycle close-epoch-ceremony TRANSITION {epoch_id}
```

**Goal:** Transition to the new epoch.

**Note:** `/new-epoch` command (CH-008) is not yet implemented. This phase is partially manual until CH-008 completes.

**Actions:**
1. (Future) Create new epoch via `/new-epoch` command when CH-008 is implemented
2. Update `haios.yaml` epoch configuration:
   - Set `epoch.current` to new epoch ID
   - Set `epoch.epoch_file` to new epoch path
   - Update `epoch.prior_epoch` to just-closed epoch
   - Reset `epoch.active_arcs` for new epoch
3. Report transition summary to operator

**Manual Steps (until CH-008):**
```yaml
# Edit .claude/haios/config/haios.yaml
epoch:
  current: E2.5  # New epoch
  epoch_file: ".claude/haios/epochs/E2_5/EPOCH.md"
  prior_epoch: ".claude/haios/epochs/E2_4/EPOCH.md"
  active_arcs: []  # Reset for new epoch planning
```

**On Complete:**
```bash
just clear-cycle
```

**Exit Criteria:**
- [ ] haios.yaml updated with new epoch
- [ ] Transition summary reported

**Tools:** Edit (haios.yaml), Read

---

## Composition Map

| Phase | Primary Tool | Output |
|-------|--------------|--------|
| VALIDATE | Read, Glob, Bash | DoD verification result |
| ARCHIVE | Edit, Bash | Updated EPOCH.md, archived work items |
| TRANSITION | Edit | Updated haios.yaml |

---

## Quick Reference

| Phase | Question to Ask | If NO |
|-------|-----------------|-------|
| VALIDATE | Are all arcs Complete? | List incomplete arcs, STOP |
| VALIDATE | Are all decisions implemented? | Show audit errors, STOP |
| VALIDATE | Are Exit Criteria all checked? | List unchecked items, STOP |
| ARCHIVE | Is Status updated to Complete? | Edit EPOCH.md file |
| ARCHIVE | Are work items archived? | Move to docs/work/archive/{epoch} |
| TRANSITION | Is haios.yaml updated? | Edit config file |

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Three phases | VALIDATE -> ARCHIVE -> TRANSITION | Epoch has unique archival and transition needs |
| ARCHIVE includes work migration | Move work items to archive | ADR-041: epoch boundary is when work items move |
| No MEMORY phase | Epochs don't store learnings | WHY capture happens at work item level (ADR-033) |
| No automatic /new-epoch | Manual config update | CH-008 not yet implemented |
| Partial automation | Guide through manual steps | Pragmatic until full tooling exists |

---

## Related

- **close-arc-ceremony skill:** Previous level (arc closure)
- **close-chapter-ceremony skill:** Previous level (chapter closure)
- **audit-decision-coverage recipe:** Validates all decisions implemented
- **ADR-041:** Status over location (archive at epoch boundary)
- **ADR-033:** Work Item Lifecycle (DoD definition)
- **CH-008:** EpochTransition (future: /new-epoch command)
