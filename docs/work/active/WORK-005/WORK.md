---
template: work_item
id: WORK-005
title: Implement Loader Base for Configuration Arc
type: feature
status: active
owner: Hephaestus
created: 2026-01-21
spawned_by: null
chapter: CH-003
arc: configuration
closed: null
priority: medium
effort: medium
requirement_refs: []
source_files:
- .claude/haios/epochs/E2_3/arcs/configuration/CH-003-loader-base.md
- .claude/haios/epochs/E2_3/arcs/configuration/ARC.md
acceptance_criteria:
- Extraction DSL supports all 8 types (blockquote, first_paragraph, all_h3, numbered_list,
  bulleted_list, frontmatter, code_block, full_section)
- Base Loader class with extract(), format(), load() methods
- Output is injection-ready string (not file paths)
- Config-driven extraction (no hardcoded paths)
- Unit tests pass for all extraction types
blocked_by: []
blocks: []
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-21 19:03:13
  exited: null
artifacts: []
cycle_docs: {}
memory_refs: []
extensions: {}
version: '2.0'
generated: 2026-01-21
last_updated: '2026-01-21T19:05:04'
---
# WORK-005: Implement Loader Base for Configuration Arc

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** Agent reads entire files when it only needs specific content.

Current state:
```
Agent reads: L0-telos.md (101 lines)
Agent needs: Prime directive (1 sentence)
Waste: 100 lines of context tokens
```

The Module-First principle (Session 218) established that commands/skills MUST call modules, not instruct agents to read files manually. But even when modules load files, they inject entire file contents rather than extracting the specific pieces needed.

**Root cause:** No extraction DSL exists to select specific content from structured markdown files.

**Solution:** Build a base Loader class with an extraction DSL that can:
1. Parse YAML config defining what to extract
2. Extract specific content types (blockquotes, headings, lists, etc.)
3. Format extracted content for injection
4. Return injection-ready strings (not file paths)

This is the foundation for CH-004 (Identity Loader), CH-005 (Session Loader), and CH-006 (Work Loader).

---

## Deliverables

<!-- VERIFICATION REQUIREMENT (Session 192 - E2-290 Learning)

     These checkboxes are the SOURCE OF TRUTH for work completion.

     During CHECK phase of implementation-cycle:
     - Agent MUST read this section
     - Agent MUST verify EACH checkbox can be marked complete
     - If ANY deliverable is incomplete, work is NOT done

     "Tests pass" ≠ "Deliverables complete"
     Tests verify code works. Deliverables verify scope is complete.

     NOTE (WORK-001): Acceptance criteria are in frontmatter (machine-parseable).
     Deliverables are implementation outputs, not requirements.
-->

- [ ] `.claude/lib/loader.py` - Base Loader class with extract(), format(), load() methods
- [ ] Extraction DSL implementation supporting 8 types:
  - [ ] `blockquote` - First `> ` block in section
  - [ ] `first_paragraph` - Text until blank line
  - [ ] `all_h3` - All `### ` headings with first line
  - [ ] `numbered_list` - All `1. ` items
  - [ ] `bulleted_list` - All `- ` items
  - [ ] `frontmatter` - YAML field extraction
  - [ ] `code_block` - First fenced code block
  - [ ] `full_section` - Everything under heading
- [ ] Output template system for formatting extracted content
- [ ] Unit tests: `tests/test_loader.py`
- [ ] Example config: `.claude/haios/config/loaders/example.yaml`

---

## History

### 2026-01-21 - Created (Session 219)
- Initial creation
- Populated from CH-003 spec via work-creation-cycle

---

## References

- @.claude/haios/epochs/E2_3/arcs/configuration/CH-003-loader-base.md (chapter spec)
- @.claude/haios/epochs/E2_3/arcs/configuration/ARC.md (arc context)
- @.claude/haios/manifesto/L4-implementation.md (Module-First principle)
- Session 218 checkpoint (memory_refs: 82199-82229)
