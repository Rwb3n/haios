---
template: investigation
status: complete
date: 2025-12-22
backlog_id: E2-116
title: "At-Reference Necessity in Checkpoints"
author: Hephaestus
session: 100
lifecycle_phase: conclude
memory_refs: [77186, 77187, 77188, 77189, 77190]
version: "1.2"
generated: 2025-12-22
last_updated: 2025-12-22T20:43:32
---
# Investigation: At-Reference Necessity in Checkpoints

@docs/README.md
@docs/epistemic_state.md

<!-- INVESTIGATION CYCLE (E2-111)
     Phases: HYPOTHESIZE -> EXPLORE -> CONCLUDE

     Update lifecycle_phase as you progress:
     - hypothesize: Defining context, hypotheses, scope
     - explore: Executing investigation, gathering evidence
     - conclude: Synthesizing findings, spawning work

     Optional: Use investigation-agent for complex research
     Task(prompt='HYPOTHESIZE: ...', subagent_type='investigation-agent')
-->

---

## Context

`@` references were introduced in checkpoint templates **before** the memory system existed. They force explicit document linkage at the top of each checkpoint:

```markdown
@docs/README.md
@docs/epistemic_state.md
@docs/checkpoints/2025-12-22-02-SESSION-97...
```

Now checkpoints have a `memory_refs` field pointing to ingested concepts (e.g., `memory_refs: [77147, 77148, ...]`). The question: are `@` references still valuable or redundant ceremony?

**Spawned by:** Session 90 observation during E2-110 implementation

---

## Objective

Determine whether `@` references in checkpoints provide value beyond what `memory_refs` captures, and recommend whether to keep, modify, or remove them.

---

## Scope

### In Scope
- `@` references in checkpoint templates
- How `/coldstart` and agents use `@` references
- Comparison with `memory_refs` field functionality
- Claude Code's handling of `@` syntax

### Out of Scope
- `@` references in other document types (plans, investigations)
- Memory system architecture changes
- Template redesign beyond `@` reference decision

---

## Hypotheses

<!-- HYPOTHESIZE PHASE: Define testable hypotheses before exploring -->

1. **H1:** Claude Code does NOT actually process `@` references - they are purely ceremonial
   - Confidence: Medium
   - Test: Check Claude Code documentation and source behavior

2. **H2:** `@` references serve a different purpose than `memory_refs` - document linkage vs concept linkage
   - Confidence: Medium
   - Test: Compare what each field captures and enables

3. **H3:** `@` references help human readers navigate but don't affect agent behavior
   - Confidence: High
   - Test: Review actual usage patterns in coldstart and checkpoint reading

4. **H4:** Removing `@` references would reduce ceremony without losing functional value
   - Confidence: Low (need evidence first)
   - Test: Depends on H1-H3 findings

---

## Exploration Plan

<!-- EXPLORE PHASE: Execute these steps, document findings as you go -->

1. [x] Check Claude Code documentation for `@` reference handling
2. [x] Search codebase for `@` reference processing logic
3. [x] Examine `/coldstart` command - does it use `@` refs?
4. [x] Compare `@` refs vs `memory_refs` - what does each capture?
5. [x] Count `@` reference usage across checkpoints
6. [x] Synthesize findings and determine recommendation

---

## Findings

### F1: Claude Code @ Syntax is a PROMPT Feature, Not File Parsing

From official Claude Code documentation:
> "Use @ to quickly include files or directories without waiting for Claude to read them."

The `@filepath` syntax is an **interactive prompt feature** - when YOU type `@file.js` in your prompt, Claude reads it. It is **NOT** automatic parsing of `@` symbols in saved markdown documents.

**Key insight:** `@` references in checkpoints are invisible to Claude Code. They are never processed.

### F2: `/coldstart` Does NOT Use @ References

The `/coldstart` command (`.claude/commands/coldstart.md`) explicitly lists files to read:
```
1. Read `CLAUDE.md`
2. Read `docs/epistemic_state.md`
3. Find the 2 most recent files in `docs/checkpoints/`
```

It uses explicit paths, not @ references. The @ references in checkpoints serve no functional purpose during coldstart.

### F3: @ References vs memory_refs Serve Different Purposes

| Field | What it captures | Example | Used by |
|-------|------------------|---------|---------|
| `@ refs` | Related document paths | `@docs/README.md` | Nothing (ceremonial) |
| `memory_refs` | Concept IDs from learnings | `[77147, 77148, ...]` | Memory queries, provenance |

### F4: Usage Statistics

- **151 @ references** across **66 checkpoint files**
- Average: ~2-3 @ refs per checkpoint
- Pattern: Always README, epistemic_state, and prior checkpoint

### Hypothesis Verdicts

| Hypothesis | Evidence | Source | Verdict |
|------------|----------|--------|---------|
| H1: @ refs are ceremonial | Claude Code only processes @ in prompts, not saved files | Claude Code docs | **CONFIRMED** |
| H2: @ refs differ from memory_refs | @ = doc links, memory_refs = concept IDs | Session 99 checkpoint | **CONFIRMED** |
| H3: @ refs help humans, not agents | /coldstart ignores @ refs, uses explicit paths | coldstart.md | **CONFIRMED** |
| H4: Removing reduces ceremony | 151 occurrences of unused markup | Grep count | **CONFIRMED** |

---

## Recommendation

**Remove @ references from checkpoint template.** They are pure ceremony with zero functional value.

### Rationale
1. Claude Code does not process @ symbols in saved files
2. `/coldstart` explicitly reads files by path, ignoring @ refs
3. `memory_refs` already captures semantic linkage to learnings
4. 151 occurrences of unused markup across 66 files = maintenance burden

### Migration Path
- **Templates:** Remove @ refs from checkpoint template (immediate)
- **Existing files:** Leave as-is (harmless, not worth mass-edit)
- **Other doc types:** Investigate separately if needed

---

## Spawned Work Items

<!-- CONCLUDE PHASE: Create spawned items via /new-* commands
     Each spawned item MUST have spawned_by: {this_investigation_id}

     DoD (E2-115): This section MUST have entries, not "None yet" -->

1. **E2-132: Remove @ References from Checkpoint Template**
   - Status: proposed
   - Effort: Small
   - Action: Edit `.claude/templates/checkpoint.md` to remove @ refs
   - spawned_by: E2-116

---

## Closure Checklist

<!-- CONCLUDE PHASE: Complete before /close -->

- [x] Findings synthesized (answer to objective documented)
- [x] Spawned work items created with `spawned_by` field
- [x] Learnings stored to memory (`memory_refs` populated: 77186-77190)
- [x] lifecycle_phase set to `conclude`

---

## References

- Claude Code docs: common-workflows.md, slash-commands.md
- `.claude/commands/coldstart.md`
- `.claude/templates/checkpoint.md`

---
