---
name: close-chapter-ceremony
description: HAIOS Close Chapter Ceremony for verifying chapter DoD. Use when all
  work items in a chapter are complete. Guides VALIDATE->MARK->REPORT workflow with
  decision verification.
recipes:
- audit-decision-coverage
generated: 2026-02-02
last_updated: '2026-02-02T12:47:38'
---
# Close Chapter Ceremony

This skill defines the VALIDATE-MARK-REPORT cycle for closing chapters with Definition of Done (DoD) enforcement per REQ-DOD-001.

## When to Use

**Manual invocation:** `Skill(skill="close-chapter-ceremony")` when all work items assigned to a chapter are complete and you want to verify the chapter achieved its objectives.

**Not automatic:** This ceremony does not chain to close-arc-ceremony. Operator decides when to close arcs.

---

## The Cycle

```
VALIDATE --> MARK --> REPORT
```

### 1. VALIDATE Phase

**On Entry:**
```bash
just set-cycle close-chapter-ceremony VALIDATE {chapter_id}
```

**Goal:** Verify chapter meets Definition of Done criteria.

**DoD Criteria (REQ-DOD-001):**
- [ ] All work items with `chapter: {arc}/{chapter_id}` have `status: complete`
- [ ] Chapter exit criteria (in chapter file) all checked
- [ ] `implements_decisions` all verified via `just audit-decision-coverage`

**Actions:**
1. Read chapter file: `.claude/haios/epochs/{epoch}/arcs/{arc}/{chapter_id}.md`
2. Extract `implements_decisions` field from chapter file
3. Query work items assigned to chapter:
   ```
   Grep(pattern="chapter: {arc}/{chapter_id}", path="docs/work/active")
   ```
4. For each work item found, verify `status: complete` in frontmatter
5. Run audit-decision-coverage and parse output for chapter-specific errors:
   ```bash
   just audit-decision-coverage
   ```
   **Note:** Audit runs at epoch scope. Filter output for errors mentioning this chapter's `implements_decisions` IDs.
6. Check chapter Exit Criteria section - all checkboxes must be `[x]`

**Exit Criteria:**
- [ ] All assigned work items have `status: complete`
- [ ] `implements_decisions` verified (no errors in audit for these decision IDs)
- [ ] All Exit Criteria checkboxes checked

**On Failure:** Report which criteria failed. Do not proceed to MARK.

**Tools:** Read, Grep, Bash(just audit-decision-coverage)

---

### 2. MARK Phase

**On Entry:**
```bash
just set-cycle close-chapter-ceremony MARK {chapter_id}
```

**Goal:** Update chapter status to Complete.

**Expected Format:** Chapter files use `**Status:** Active` format (bold markdown).

**Actions:**
1. Edit chapter file
2. Update `**Status:** Active` to `**Status:** Complete`
3. Add completion line after Status:
   ```markdown
   **Completed:** {YYYY-MM-DD} (Session {N})
   ```

**Exit Criteria:**
- [ ] Chapter file has `**Status:** Complete`
- [ ] Completion timestamp added

**Tools:** Edit

---

### 3. REPORT Phase

**On Entry:**
```bash
just set-cycle close-chapter-ceremony REPORT {chapter_id}
```

**Goal:** Summarize chapter closure to operator.

**Actions:**
1. Report closure summary to operator (console output):
   - Chapter ID and name
   - Work items completed (count and IDs)
   - Decisions implemented (`implements_decisions` list)
   - Exit criteria satisfied
2. List any observations captured in completed work items

**Output:** Console summary. No file output or memory storage at chapter level (memory capture happens at work item level per ADR-033).

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
| VALIDATE | Read, Grep, Bash | DoD verification result |
| MARK | Edit | Updated chapter file |
| REPORT | Read | Console summary |

---

## Quick Reference

| Phase | Question to Ask | If NO |
|-------|-----------------|-------|
| VALIDATE | Are all work items complete? | List incomplete items, STOP |
| VALIDATE | Are Exit Criteria all checked? | List unchecked items, STOP |
| VALIDATE | Does audit pass for implements_decisions? | Show audit errors, STOP |
| MARK | Is Status updated to Complete? | Edit chapter file |
| REPORT | Is summary reported? | Output to operator |

---

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Three phases | VALIDATE -> MARK -> REPORT | Simpler than close-work-cycle (no MEMORY phase needed) |
| No MEMORY phase | Chapters don't store learnings | WHY capture happens at work item level (ADR-033) |
| No automatic chaining | Manual arc closure | Closing a chapter doesn't mean arc is done |
| Console output only | REPORT to operator | No file artifacts needed at chapter level |
| Audit at epoch scope | Filter for chapter | `just audit-decision-coverage` validates all decisions; ceremony filters results |

---

## Related

- **REQ-DOD-001:** Chapter closure requirement this ceremony implements
- **close-work-cycle skill:** Pattern reference (work item closure)
- **close-arc-ceremony skill:** Next level up (WORK-077)
- **audit-decision-coverage recipe:** Validates decision implementations
- **ADR-033:** Work Item Lifecycle (DoD definition)
