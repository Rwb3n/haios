# generated: 2025-11-23
# System Auto: last updated on: 2025-11-23 22:09:43
# Handoff Type Reference

## Overview

Handoffs are structured communication documents from Executor/Planner agents to Implementer agents. Different types of work require different handoff formats.

## Handoff Types

### 1. BUG HANDOFF
**When to use:** Defects, broken functionality, data corruption
**Priority:** Usually High/Critical
**Template:** `BUG_<description>.md`

**Structure:**
- Summary (what's broken)
- Impact (how bad is it)
- Root Cause (why it's broken)
- Expected Behavior (what should happen)
- Solution Options (how to fix)
- Testing Requirements
- Acceptance Criteria

**Example:** `BUG_duplicate_occurrences_on_reprocess.md`

---

### 2. FEATURE HANDOFF
**When to use:** New functionality, capabilities that don't exist yet
**Priority:** Medium (unless critical business need)
**Template:** `FEATURE_<name>.md`

**Structure:**
- User Story / Business Need
- Acceptance Criteria (what defines "done")
- Technical Approach (recommended implementation)
- Dependencies (what's needed)
- Testing Strategy
- Out of Scope (what NOT to include)

**Example:** `FEATURE_mcp_server_for_memory.md` (future)

---

### 3. ENHANCEMENT HANDOFF
**When to use:** Improvements to existing functionality
**Priority:** Low to Medium
**Template:** `ENHANCEMENT_<feature>_<improvement>.md`

**Structure:**
- Current Behavior
- Proposed Improvement
- Benefit / Rationale
- Implementation Approach
- Backward Compatibility
- Testing

**Example:** `improve_status_display.md` (already created)

---

### 4. REFACTOR HANDOFF
**When to use:** Code quality, architecture improvements, tech debt
**Priority:** Low (unless blocking other work)
**Template:** `REFACTOR_<component>_<reason>.md`

**Structure:**
- Current State (what's messy)
- Problems (why it needs refactoring)
- Target State (what good looks like)
- Migration Strategy (how to transition)
- Risk Assessment
- Testing Requirements

**Example:** `REFACTOR_preprocessor_architecture.md` (if needed)

---

### 5. INVESTIGATION HANDOFF
**When to use:** Unknown root cause, research needed before decision
**Priority:** Varies
**Template:** `INVESTIGATION_<topic>.md`

**Structure:**
- Question / Mystery
- Context (what we know)
- What to Investigate
- Expected Outputs (findings, recommendations)
- Constraints (time, resources)
- Next Steps (what happens with findings)

**Example:** `INVESTIGATION_slow_extraction_performance.md` (if needed)

---

### 6. DOCUMENTATION HANDOFF
**When to use:** Docs missing, outdated, or unclear
**Priority:** Low (unless blocking adoption)
**Template:** `DOCS_<topic>.md`

**Structure:**
- Documentation Gap (what's missing)
- Target Audience (who needs it)
- Required Content (what to document)
- Format (README, guide, reference)
- Examples Needed
- Review Criteria

**Example:** `DOCS_preprocessor_development_guide.md` (future)

---

## Handoff Metadata Template

All handoffs should include:

```yaml
Type: [Bug|Feature|Enhancement|Refactor|Investigation|Documentation]
Severity: [Critical|High|Medium|Low]
Priority: [Critical|High|Medium|Low]
Date: YYYY-MM-DD
Discovered By: [Agent Name]
Assigned To: [Agent Name or Role]
Estimated Effort: [X minutes/hours]
Dependencies: [List or "None"]
Blocking: [List or "None"]
```

## File Naming Convention

```
YYYY-MM-DD-NN-TYPE-descriptive-name.md

Where:
- YYYY-MM-DD: Date handoff created
- NN: Sequential number (00, 01, 02...)
- TYPE: Handoff type in UPPERCASE
- descriptive-name: Kebab-case description

Examples:
- 2025-11-23-01-BUG-duplicate-occurrences-on-reprocess.md
- 2025-11-24-01-FEATURE-add-vector-search.md
- 2025-11-23-02-ENHANCEMENT-improve-status-display.md
- 2025-11-25-01-REFACTOR-database-layer-separation.md
- 2025-11-26-01-INVESTIGATION-memory-leak-in-extraction.md
- 2025-11-27-01-DOCS-operator-quickstart-guide.md
``````
[TYPE]_[descriptive_name].md

Examples:
- BUG_duplicate_occurrences_on_reprocess.md
- FEATURE_add_vector_search.md
- ENHANCEMENT_improve_status_display.md
- REFACTOR_database_layer_separation.md
- INVESTIGATION_memory_leak_in_extraction.md
- DOCS_operator_quickstart_guide.md
```

## Handoff Storage

**Location:** `docs/handoff/`

**Organization:**
```
docs/handoff/
├── active/              # Current handoffs (in progress)
├── completed/           # Completed handoffs (archive)
├── blocked/             # Blocked handoffs (waiting on dependencies)
├── HANDOFF_TYPES.md     # This file
└── *.md                 # Active handoffs (root level)
```

**Lifecycle:**
1. Created → `docs/handoff/[TYPE]_name.md`
2. Picked up → Implementer adds notes, updates status
3. Completed → Move to `docs/handoff/completed/`
4. Blocked → Move to `docs/handoff/blocked/`, document blocker

## Current Active Handoffs

As of 2025-11-23:

1. **2025-11-23-01-BUG-duplicate-occurrences-on-reprocess.md** (High Priority)
   - Type: Bug
   - Status: Active
   - Blocks: Clean database state

2. **2025-11-23-02-ENHANCEMENT-improve-status-display.md** (Low Priority)
   - Type: Enhancement
   - Status: Active
   - Blocks: None

## Guidelines

### Writing Good Handoffs

**DO:**
- ✅ Be specific (exact file paths, line numbers)
- ✅ Include code examples
- ✅ Provide multiple solution options
- ✅ Define clear acceptance criteria
- ✅ Link to related specs/ADRs
- ✅ Estimate effort realistically

**DON'T:**
- ❌ Make assumptions about implementation details
- ❌ Skip testing requirements
- ❌ Leave acceptance criteria vague
- ❌ Forget to specify priority
- ❌ Mix multiple unrelated issues in one handoff

### Implementer Response

When picking up a handoff, Implementer should:
1. Add comment block at top with status
2. Ask clarifying questions if needed
3. Update estimated effort if incorrect
4. Document implementation decisions
5. Mark completed when done
6. Create test evidence

**Example:**
```markdown
<!-- IMPLEMENTER NOTES
Status: In Progress
Started: 2025-11-23 22:30
Assigned: Claude (Implementer)
Estimated Effort: 30 minutes (was 45)
Notes: Using Option A - Delete Before Insert approach
-->
```

## Templates

Templates for each handoff type available in:
- `HAIOS-RAW/templates/handoff_bug_template.md`
- `HAIOS-RAW/templates/handoff_feature_template.md`
- `HAIOS-RAW/templates/handoff_enhancement_template.md`
- etc.

(Future: Create these templates)
