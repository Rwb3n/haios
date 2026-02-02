---
name: close-arc-ceremony
description: HAIOS Close Arc Ceremony for verifying arc DoD. Use when all chapters
  in an arc are complete. Guides VALIDATE->MARK->REPORT workflow with orphan decision
  check.
recipes:
- audit-decision-coverage
generated: 2026-02-02
last_updated: '2026-02-02T13:22:19'
---
# Close Arc Ceremony

This skill defines the VALIDATE-MARK-REPORT cycle for closing arcs with Definition of Done (DoD) enforcement per REQ-DOD-002.

## When to Use

**Manual invocation:** `Skill(skill="close-arc-ceremony")` when all chapters in an arc are complete and you want to verify the arc achieved its theme.

**Not automatic:** This ceremony does not chain to close-epoch-ceremony. Operator decides when to close epochs.

---

## The Cycle

```
VALIDATE --> MARK --> REPORT
```

### 1. VALIDATE Phase

**On Entry:**
```bash
just set-cycle close-arc-ceremony VALIDATE {arc_id}
```

**Goal:** Verify arc meets Definition of Done criteria.

**DoD Criteria (REQ-DOD-002):**
- [ ] All chapters in arc have `**Status:** Complete`
- [ ] No epoch decisions assigned to this arc are unimplemented (orphan check)
- [ ] Arc exit criteria (in ARC.md) all checked

**Actions:**
1. Read arc file: `.claude/haios/epochs/{epoch}/arcs/{arc}/ARC.md`
2. Glob chapter files: `.claude/haios/epochs/{epoch}/arcs/{arc}/CH-*.md`
3. For each chapter file, verify `**Status:** Complete`
4. Run audit-decision-coverage and check for unassigned/orphan decisions for this arc:
   ```bash
   just audit-decision-coverage
   ```
   **Note:** Audit runs at epoch scope. Filter output for errors mentioning this arc's decisions.
5. Check arc Exit Criteria section - all checkboxes must be `[x]`

**Exit Criteria:**
- [ ] All chapters have `**Status:** Complete`
- [ ] No orphan decisions (unassigned epoch decisions for this arc)
- [ ] All Exit Criteria checkboxes checked

**On Failure:** Report which criteria failed. Do not proceed to MARK.

**Tools:** Read, Glob, Bash(just audit-decision-coverage)

---

### 2. MARK Phase

**On Entry:**
```bash
just set-cycle close-arc-ceremony MARK {arc_id}
```

**Goal:** Update arc status to Complete.

**Expected Format:** Arc files use `**Status:** Active` or `**Status:** Planned` format (bold markdown).

**Actions:**
1. Edit ARC.md file
2. Update `**Status:** Active` (or `Planned`) to `**Status:** Complete`
3. Add completion line after Status:
   ```markdown
   **Completed:** {YYYY-MM-DD} (Session {N})
   ```

**Exit Criteria:**
- [ ] Arc file has `**Status:** Complete`
- [ ] Completion timestamp added

**Tools:** Edit

---

### 3. REPORT Phase

**On Entry:**
```bash
just set-cycle close-arc-ceremony REPORT {arc_id}
```

**Goal:** Summarize arc closure to operator.

**Actions:**
1. Report closure summary to operator (console output):
   - Arc ID and theme name
   - Chapters completed (count and IDs)
   - Exit criteria satisfied
2. List any chapters that had observations

**Output:** Console summary. No file output or memory storage at arc level (memory capture happens at work item level per ADR-033).

**On Complete:**
```bash
just clear-cycle
```

**Exit Criteria:**
- [ ] Closure summary reported to operator

**Tools:** Read (to gather summary data)

---

## Composition Map

| Phase | Primary Tool | Output |
|-------|--------------|--------|
| VALIDATE | Read, Glob, Bash | DoD verification result |
| MARK | Edit | Updated ARC.md file |
| REPORT | Read | Console summary |

---

## Quick Reference

| Phase | Question to Ask | If NO |
|-------|-----------------|-------|
| VALIDATE | Are all chapters Complete? | List incomplete chapters, STOP |
| VALIDATE | Are Exit Criteria all checked? | List unchecked items, STOP |
| VALIDATE | Does audit pass (no orphan decisions)? | Show audit errors, STOP |
| MARK | Is Status updated to Complete? | Edit ARC.md file |
| REPORT | Is summary reported? | Output to operator |

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Three phases | VALIDATE -> MARK -> REPORT | Consistent with close-chapter-ceremony |
| No MEMORY phase | Arcs don't store learnings | WHY capture happens at work item level (ADR-033) |
| No automatic chaining | Manual epoch closure | Closing an arc doesn't mean epoch is done |
| Console output only | REPORT to operator | No file artifacts needed at arc level |
| Orphan decision check | Via audit-decision-coverage | Ensures all epoch decisions assigned to arc are implemented |

---

## Related

- **REQ-DOD-002:** Arc closure requirement this ceremony implements
- **close-chapter-ceremony skill:** Pattern reference (chapter closure)
- **close-epoch-ceremony skill:** Next level up (WORK-078)
- **audit-decision-coverage recipe:** Validates decision implementations
- **ADR-033:** Work Item Lifecycle (DoD definition)
