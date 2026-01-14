---
name: work-creation-cycle
description: HAIOS Work Creation Cycle for structured work item population. Use when
  creating new work items. Guides VERIFY->POPULATE->READY workflow.
recipes:
- work
generated: 2025-12-25
last_updated: '2026-01-12T01:32:18'
---
# Work Creation Cycle

This skill defines the VERIFY-POPULATE-READY cycle for populating work items after scaffolding. It ensures work items have complete Context and Deliverables before being actioned.

## When to Use

**Invoked automatically** by `/new-work` command after scaffolding.
**Manual invocation:** `Skill(skill="work-creation-cycle")` when populating an existing work file.

---

## The Cycle

```
VERIFY --> POPULATE --> READY --> CHAIN
                                    |
                          [confidence check]
                           /              \
                     HIGH                  LOW
                      |                     |
              auto-chain to           /reason +
           /new-plan or              user decision
           /new-investigation
```

### 1. VERIFY Phase

**Goal:** Confirm work file was created and is valid.

**Actions:**
1. Read the work file: `docs/work/active/{id}/WORK.md` (E2-212 directory structure)
2. Verify file has valid YAML frontmatter
3. Confirm `status: active` and `current_node: backlog`
4. Check for `spawned_by` field if this is spawned work

**Exit Criteria:**
- [ ] Work file exists at expected path
- [ ] Frontmatter valid (template: work_item)
- [ ] Status is `active`

**Tools:** Read, Glob

---

### 2. POPULATE Phase

**Goal:** Fill in essential work item fields.

**Guardrails (MUST follow):**
1. **Context section MUST be populated** - Replace `[Problem and root cause]` with actual problem description
2. **Deliverables MUST be actionable** - Replace placeholders with specific checkboxes

**Actions:**
1. Prompt for Context: "What problem does this work item solve?"
2. Fill in Context section with problem statement
3. Prompt for Deliverables: "What are the specific outputs?"
4. Fill in Deliverables as checklist items
5. Optionally set: milestone, priority, spawned_by, blocked_by

**Exit Criteria:**
- [ ] Context section has real content (not placeholder)
- [ ] Deliverables have specific items (not placeholders)
- [ ] Optional: milestone assigned

**Tools:** Edit, AskUserQuestion

---

### 3. READY Phase

**Goal:** Validate work item is actionable.

**Guardrails (MUST follow - E2-191):**
1. **Context MUST NOT contain placeholders** - Detect `[Problem and root cause]`
2. **Deliverables MUST NOT contain placeholders** - Detect `[Deliverable 1]`, `[Deliverable 2]`

**Actions:**
1. Read work file to verify all fields populated
2. Check Context section contains >20 characters AND no placeholder text
3. Check Deliverables has at least one checkbox item AND no placeholder text
4. **If placeholders found:** Report to user, recommend completing POPULATE phase
5. Update History section with population timestamp

**Exit Criteria:**
- [ ] Context populated with meaningful content (no placeholders)
- [ ] Deliverables has actionable checklist (no placeholders)
- [ ] Work item ready for further lifecycle progression

**Tools:** Read, Edit

---

### 4. CHAIN Phase (Post-READY)

**Goal:** Route to appropriate next cycle based on confidence.

**Confidence-Based Routing:**

| Signal | Confidence | Action |
|--------|------------|--------|
| ID starts with `INV-` | HIGH | Auto-chain: `/new-investigation {id} {title}` |
| `spawned_by_investigation` is populated | HIGH | Auto-chain: `/new-plan {id} {title}` (discovery done) |
| Clear technical deliverables, small scope | HIGH | Auto-chain: `/new-plan {id} {title}` |
| Complex/architectural work | LOW | Chain to `/reason` for structured decision |
| Unclear if needs investigation first | LOW | Chain to `/reason` for structured decision |
| No clear signals | LOW | Chain to `/reason` for structured decision |

**Actions:**
1. Read work file frontmatter for signals (id prefix, spawned_by_investigation)
2. Assess deliverables complexity
3. **If HIGH confidence:** Auto-invoke appropriate command
4. **If LOW confidence:** Invoke `/reason` and ask user

**Exit Criteria:**
- [ ] Next lifecycle step initiated (plan, investigation, or user decision)

**Tools:** Read, Skill

---

## Composition Map

| Phase | Primary Tool | Memory Integration |
|-------|--------------|-------------------|
| VERIFY | Read, Glob | - |
| POPULATE | Edit, AskUserQuestion | Query for prior similar work |
| READY | Read, Edit | - |
| CHAIN | Read, Skill | - |

---

## Quick Reference

| Phase | Question to Ask | If NO |
|-------|-----------------|-------|
| VERIFY | Does work file exist? | Re-run /new-work |
| POPULATE | Is Context filled? | Prompt user for problem statement |
| POPULATE | Are Deliverables defined? | Prompt user for outputs |
| READY | Is work item actionable? | Return to POPULATE |

---

## Related

- **Investigation-cycle skill:** Parallel workflow for research
- **Implementation-cycle skill:** Parallel workflow for implementation
- **Work item template:** `.claude/templates/work_item.md`
- **ADR-039:** Work Item as File Architecture
- **/new-work command:** Creates work item files
