---
template: implementation_plan
status: complete
date: 2025-12-22
backlog_id: E2-115
title: "Investigation Closure"
author: Hephaestus
lifecycle_phase: plan
session: 98
spawned_by: M4-Research
related: [E2-111, E2-023, ADR-033]
milestone: M4-Research
version: "1.5"
generated: 2025-12-22
last_updated: 2025-12-22T17:53:46
---
# Implementation Plan: Investigation Closure

@docs/README.md
@docs/epistemic_state.md
@.claude/commands/close.md
@.claude/skills/investigation-cycle/SKILL.md

---

## Goal

Extend `/close` command to enforce investigation-specific DoD when closing INV-* work items, ensuring findings are documented and spawned work items are created and linked.

---

## Effort Estimation (Ground Truth)

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to modify | 1 | `.claude/commands/close.md` |
| Lines of code affected | ~30 | Adding investigation-specific section |
| New files to create | 0 | Extending existing command |
| Tests to write | 0 | Command is prompt-based (manual verification) |
| Dependencies | 1 | Investigation template structure |

### Complexity Factors

| Factor | Level | Notes |
|--------|-------|-------|
| Integration points | Low | Extends existing /close flow |
| Risk of regression | Low | Additive change, existing flow unchanged |
| External dependencies | Low | Uses existing grep/read patterns |

### Effort Estimate

| Phase | Estimate | Confidence |
|-------|----------|------------|
| Design DoD criteria | 15 min | High |
| Update close.md | 20 min | High |
| Test with real investigation | 10 min | High |
| **Total** | ~45 min | High |

---

## Current State vs Desired State

### Current State

**SKIPPED:** Current /close command exists but doesn't have investigation-specific DoD.

**File:** `.claude/commands/close.md:61-90`

**Behavior:**
- Generic DoD: tests pass, WHY captured, docs current, traced files complete
- No check for investigation-specific requirements (Findings, Spawned Work Items)

**Result:** Investigations can be closed without documenting findings or creating spawned work items.

### Desired State

**Behavior:**
- When `backlog_id` starts with `INV-`, apply investigation-specific DoD
- Check Findings section has real content (not placeholder)
- Check Spawned Work Items section has entries (not "None yet")
- Verify investigation file has `memory_refs` populated

**Result:** Investigations cannot close until findings are documented and spawns are created - enforcing CONCLUDE phase exit criteria from investigation-cycle skill.

---

## Tests First (TDD)

**SKIPPED:** Command is prompt-based documentation. Verification is manual: test by running `/close INV-xxx` on a real investigation.

**Manual Verification:**
1. Attempt `/close INV-022` (has findings but no memory_refs yet)
2. Verify investigation-specific DoD prompts appear
3. Verify closure blocked until DoD satisfied

---

## Detailed Design

### Investigation DoD Criteria

From investigation-cycle CONCLUDE phase exit criteria:

| Criterion | Verification | Template Location |
|-----------|--------------|-------------------|
| Findings documented | Findings section != placeholder | `## Findings` section |
| Spawned items exist | Spawned Work Items != "None yet" | `## Spawned Work Items` section |
| Memory refs populated | `memory_refs:` in frontmatter | YAML frontmatter |

### Detection Logic

```
IF backlog_id matches /^INV-/ THEN
    Apply investigation-specific DoD
ELSE
    Apply standard DoD (current behavior)
```

### Investigation DoD Flow

```
/close INV-xxx
    │
    ├── [1] Find investigation file
    │   └── Grep: docs/investigations/INVESTIGATION-{backlog_id}-*.md
    │
    ├── [2] Read investigation file
    │
    ├── [3] Check investigation-specific DoD
    │   ├── Findings section has content? (not placeholder text)
    │   ├── Spawned Work Items has entries? (not "None yet")
    │   └── memory_refs in frontmatter? (concepts stored)
    │
    ├── [4] Report DoD status
    │   ├── All pass → Continue to standard closure
    │   └── Any fail → Report what's missing, STOP
    │
    └── [5] Standard closure flow (existing)
```

### Placeholder Detection

| Section | Placeholder Text | How to Detect |
|---------|------------------|---------------|
| Findings | `[Document findings here after investigation]` | Exact match or section < 50 chars |
| Spawned Work Items | `- [ ] None yet` | Contains "None yet" |
| memory_refs | Missing or empty | `memory_refs:` not in frontmatter or empty array |

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Extend /close vs new command | Extend | Unified closure, less fragmentation |
| Detect by backlog_id prefix | INV-* pattern | Simple, reliable, matches existing pattern (E2-*, TD-*) |
| Findings check method | Length + placeholder | Avoids false positives from minimal edits |
| Spawns check strictness | Must have entries | "None yet" is explicit no-action marker |

### Changes to close.md

**Add new Step 1.5: Investigation-Specific DoD (after Step 1, before Step 2)**

```markdown
### Step 1.5: Investigation-Specific DoD (INV-* only)

If backlog_id starts with `INV-`:

1. **Find investigation file:**
   ```
   Glob(pattern="docs/investigations/INVESTIGATION-{backlog_id}-*.md")
   ```

2. **Read and verify investigation DoD:**

   | Criterion | Check | Fail Condition |
   |-----------|-------|----------------|
   | Findings documented | Read `## Findings` section | Contains placeholder or < 50 chars |
   | Spawned items exist | Read `## Spawned Work Items` | Contains "None yet" |
   | Memory refs populated | Check frontmatter `memory_refs:` | Missing or empty |

3. **Report investigation DoD status:**
   - "Investigation DoD for {backlog_id}:"
   - "- [x/!] Findings documented"
   - "- [x/!] Spawned work items created"
   - "- [x/!] Memory refs populated"

4. **If any criterion fails:**
   - Report: "Investigation DoD not met. Complete CONCLUDE phase first."
   - STOP (do not proceed to standard DoD)
```

---

## Implementation Steps

### Step 1: Update close.md with Investigation DoD
- [ ] Add Step 1.5 after existing Step 1
- [ ] Add detection logic for INV-* prefix
- [ ] Add investigation-specific DoD checks
- [ ] Add failure reporting

### Step 2: Test with Real Investigation
- [ ] Run `/close INV-022` (active investigation)
- [ ] Verify investigation DoD prompts appear
- [ ] Verify standard DoD still works for E2-* items

### Step 3: README Sync (MUST)
- [ ] **MUST:** Update `.claude/commands/README.md` if it exists

### Step 4: Consumer Verification (MUST for migrations/refactors)

**SKIPPED:** Not a migration - additive change to existing command.

---

## Verification

- [ ] `/close INV-xxx` shows investigation-specific DoD checks
- [ ] `/close E2-xxx` still uses standard DoD (no regression)
- [ ] Investigation DoD blocks closure when criteria not met

---

## Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| False positive on Findings check | Low | Use placeholder text match + length check |
| Breaks existing /close | Low | Additive change, standard flow unchanged |

---

## Progress Tracker

| Session | Date | Checkpoint | Status | Notes |
|---------|------|------------|--------|-------|
| 98 | 2025-12-22 | - | Plan drafted | Design complete |

---

## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/commands/close.md` | Has Step 1.5 for INV-* | [ ] | |
| Test: `/close INV-022` | Shows investigation DoD | [ ] | |
| Test: `/close E2-xxx` | Standard DoD (no change) | [ ] | |

**Verification Commands:**
```bash
# Check close.md has investigation section
Grep(pattern="INV-", path=".claude/commands/close.md")
# Expected: Multiple matches showing INV-* handling
```

**Binary Verification (Yes/No):**

| Question | Answer | Notes |
|----------|--------|-------|
| All listed files verified by reading? | [Yes/No] | |
| Test output pasted above? | [Yes/No] | |
| Any deviations from plan? | [Yes/No] | Explain: |

---

**Completion Criteria (DoD per ADR-033):**
- [ ] N/A - no pytest tests (command is documentation)
- [ ] WHY captured (reasoning stored to memory)
- [ ] **MUST:** READMEs updated in modified directories
- [ ] All traced files complete
- [ ] Ground Truth Verification completed above

---

## References

- **E2-111:** Investigation Cycle Skill (CONCLUDE phase exit criteria)
- **E2-023:** Work Loop Closure Automation (original /close design)
- **ADR-033:** Work Item Lifecycle (DoD definition)
- **Investigation template:** `.claude/templates/investigation.md`
- **Backlog:** E2-115

---
