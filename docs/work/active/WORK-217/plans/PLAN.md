---
template: implementation_plan
plan_version: "2.0"
status: complete
date: 2026-02-24
backlog_id: WORK-217
title: "Implement Retro-Enrichment Agent"
author: Hephaestus
lifecycle_phase: plan
session: 448
generated: 2026-02-24
last_updated: 2026-02-24T22:33:32

input_contract:
  - field: work_item
    path: "docs/work/active/WORK-217/WORK.md"
    required: true
  - field: source_files_exist
    verify: "all paths in WORK.md source_files exist on disk"
    required: true

output_contract:
  - field: layer_0_complete
    verify: "Layer 0 tables have no placeholder rows"
  - field: layer_1_complete
    verify: "Layer 1 has concrete code blocks, not pseudocode"
  - field: layer_2_complete
    verify: "every step has input/action/output/verify fields"
  - field: layer_3_complete
    verify: "every verification line has a command and expected output"
---
# Implementation Plan: Implement Retro-Enrichment Agent

<!-- TEMPLATE v2.0 (S409)
     4-Layer Structure: Inventory → Specification → Steps → Ground Truth Verification
     Each layer is a sub-agent delegation unit with computable verification.

     SKIP RATIONALE: If ANY section is omitted, provide one-line rationale:
     **SKIPPED:** [reason] -->

---

## Goal

Create a `retro-enrichment-agent.md` agent card (haiku, invoked by `/close` after retro-cycle) that cross-references each extracted retro item against memory via `memory_search_with_experience`, annotates with `related_memory_ids`, `convergence_count`, and `prior_work_ids`, stores enriched output with `retro-enrichment:{work_id}` provenance, and integrate the invocation into `.claude/commands/close.md` after the retro-cycle chain step.

---

## Open Decisions

<!-- All decisions were resolved in WORK-211 investigation. No operator_decisions field in WORK.md. -->

| Decision | Options | Chosen | Rationale |
|----------|---------|--------|-----------|
| Separate agent vs retro-cycle extension | separate, extend | separate | WORK-211 H1 confirmed: retro-cycle is a lifecycle skill with 4 phases; enrichment is post-hoc cross-referencing with a different cognitive pressure. Coupling breaks separation of concerns (mem:88476). |
| Model for enrichment | haiku, sonnet, opus | haiku | Enrichment is mechanical cross-referencing — query memory, collect IDs, count convergences. No judgment required. S436 operator directive (mem:88078). |
| Auto-spawn from enriched items | yes, no | no | REQ-LIFECYCLE-004: chaining is caller choice. Enrichment annotates; triage promotes. (mem:88478). |
| retro-cycle SKILL.md diagram update | in-scope, out-of-scope | out-of-scope | SKILL.md call chain diagram (lines 78-105) will become stale after adding enrichment step. Deferred — no runtime impact, diagram is documentation only. Acknowledged here to prevent silent drift. |

---

## Layer 0: Inventory

<!-- MUST complete before any design work. Map the blast radius.
     Producer: plan-author agent
     Consumer: all downstream agents (DO, CHECK, critique) -->

### Primary Files

| File | Action | Layer |
|------|--------|-------|
| `.claude/agents/retro-enrichment-agent.md` | CREATE | 1 |
| `.claude/commands/close.md` | MODIFY | 1 |

### Consumer Files

<!-- Files that reference primary files and need updating.
     Consumer: test_agent_cards.py hardcodes agent count = 13; adding 1 agent → must update to 14. -->

| File | Reference Type | Line(s) | Action |
|------|---------------|---------|--------|
| `tests/test_agent_cards.py` | `assert len(agents) == 13` | 97, 195 | UPDATE count to 14 |

### Test Files

| File | Action | Disposition |
|------|--------|------------|
| `tests/test_agent_cards.py` | UPDATE | Assert count 13 → 14; assert retro-enrichment-agent present in known agents |

### Scope Metrics

| Metric | Value | Source |
|--------|-------|--------|
| Files to create | 1 | Primary Files table (CREATE rows) |
| Files to modify | 2 | Primary Files (close.md) + Consumer (test_agent_cards.py) |
| Tests to write | 0 new test files | Updates only to existing test file |
| Total blast radius | 3 | 1 create + 2 modify |

---

## Layer 1: Specification

<!-- The contract that the DO agent implements.
     Producer: plan-author agent
     Consumer: DO agent -->

### Current State

```
# .claude/agents/ currently has 13 agent cards (no retro-enrichment-agent.md)
# .claude/commands/close.md "Chain to Retro Cycle" section ends at line 83:
#   "After retro-cycle completes, invoke close-work-cycle"
# No enrichment step exists between retro-cycle and close-work-cycle.
```

**Behavior:** `/close` invokes retro-cycle (REFLECT→DERIVE→COMMIT→EXTRACT), then chains directly to close-work-cycle. Extracted items have no memory cross-references when they reach observation-triage-cycle. Triage consumes them cold — without knowing if 10 prior sessions flagged the same issue.

**Problem:** 88k+ memory concepts exist but retro output has no mechanism to cross-reference them. Triage receives isolated items rather than items enriched with convergence signals.

### Desired State

```
# .claude/agents/retro-enrichment-agent.md (NEW)
# A haiku agent card with the contract below.

# .claude/commands/close.md — modified "Chain to Retro Cycle" section:
#   After retro-cycle completes:
#     1. Invoke retro-enrichment agent (NEW)
#     2. Then invoke close-work-cycle (unchanged)
```

**Behavior:** After retro-cycle EXTRACT returns `extracted_items` + `extract_concept_ids`, `/close` invokes retro-enrichment-agent. The agent queries memory for each extracted item, annotates with related IDs, convergence count, and prior WORK-* references. Stores enriched output. Then close-work-cycle runs with enriched data available.

**Result:** Observation-triage-cycle receives items annotated with frequency signals — convergence_count tells triage how many prior sessions saw the same issue, prior_work_ids link to prior related work.

### Tests

<!-- No new test file. Updates to existing test_agent_cards.py.
     TDD approach: update assertions RED first (count 13→14), then CREATE the agent card to make GREEN. -->

#### Test 1: Agent count includes retro-enrichment-agent
- **file:** `tests/test_agent_cards.py`
- **function:** `test_agent_count()` (existing — update assertion)
- **setup:** `agents = list_agents()` — reads `.claude/agents/*.md`
- **assertion:** `assert len(agents) == 14` (was 13)

#### Test 2: retro-enrichment-agent present in known agents
- **file:** `tests/test_agent_cards.py`
- **function:** `test_known_agents_present()` (existing — update expected set)
- **setup:** `agents = list_agents(); names = {a.name for a in agents}`
- **assertion:** `"retro-enrichment-agent" in names`

#### Test 3: filter_agents no-filters returns all (count update)
- **file:** `tests/test_agent_cards.py`
- **function:** `test_no_filters_returns_all()` (existing — update assertion)
- **setup:** `all_agents = filter_agents()`
- **assertion:** `assert len(all_agents) == 14` (was 13)

#### Test 4: retro-enrichment-agent has required fields
- **file:** `tests/test_agent_cards.py`
- **function:** `test_retro_enrichment_agent_fields()` (NEW test to add)
- **setup:** `agent = get_agent("retro-enrichment-agent")`
- **assertion:** `agent is not None; agent.model == "haiku"; agent.category == "cycle-delegation"; "memory-cross-referencing" in agent.capabilities`

### Design

#### File 1 (NEW): `.claude/agents/retro-enrichment-agent.md`

```markdown
---
name: retro-enrichment-agent
description: Cross-reference retro-cycle EXTRACT output against memory. Annotates each
  extracted item with related_memory_ids, convergence_count, and prior_work_ids via
  memory_search_with_experience. Stores enriched output with retro-enrichment provenance.
tools: mcp__haios-memory__memory_search_with_experience, mcp__haios-memory__ingester_ingest
model: haiku
requirement_level: recommended
category: cycle-delegation
trigger_conditions:
  - After retro-cycle completes in /close command
  - retro-cycle output has extracted_items (non-empty list)
input_contract: "work_id, memory_concept_ids, extract_concept_ids, extracted_items"
output_contract: "enriched_items list with annotations, enrichment_concept_ids list"
invoked_by:
  - /close command (after retro-cycle, before close-work-cycle)
related_agents:
  - close-work-cycle-agent (runs after enrichment)
id: retro-enrichment-agent
role: cycle-delegate
capabilities:
  - memory-cross-referencing
  - convergence-detection
  - retro-annotation
produces:
  - enriched-retro-items
consumes:
  - retro-extract-output
generated: '2026-02-24'
last_updated: '2026-02-24T00:00:00'
---
# Retro-Enrichment Agent

Cross-references retro-cycle EXTRACT output against memory to annotate items with convergence signals before observation-triage-cycle consumes them.

## Requirement Level

**RECOMMENDED** — Invoked by `/close` after retro-cycle when `extracted_items` is non-empty.

## Context

Retro-cycle EXTRACT produces typed items (bug/feature/refactor/upgrade) stored to memory. These items have no cross-references to prior related observations. The 88k+ concept memory has no mechanism that connects new retro output to existing entries. This agent bridges that gap — running immediately after EXTRACT and before close-work-cycle.

**Agent Contract (WORK-211):**
- Separate agent (not retro-cycle extension) — different cognitive pressure
- Haiku model — mechanical cross-referencing, no judgment
- Annotation only — does NOT auto-spawn (REQ-LIFECYCLE-004)
- Provenance: `retro-enrichment:{work_id}`

## Input

Receives from parent (the main agent executing `/close`):

```
work_id: "WORK-XXX"
memory_concept_ids: [id1, id2, ...]    # from retro-cycle COMMIT phase
extract_concept_ids: [id3, id4, ...]   # from retro-cycle EXTRACT phase
extracted_items:                        # from retro-cycle EXTRACT phase output
  - type: bug|feature|refactor|upgrade
    title: "Brief description"
    evidence: "File path or test reference"
    confidence: high|medium|low
    severity: dod-relevant|high|medium|low  # bug items only; pass through unchanged
    source_dimension: WWW|WCBB|WSY|WDN|WMI
    suggested_priority: now|next|later
    priority_rationale: "..."
    commit_concept_ids: [...]
```

## Process

For each item in `extracted_items`:

1. Build query from item `title` + `evidence` fields
2. Call `memory_search_with_experience(query=query, mode="knowledge_lookup")`
3. From results, extract:
   - `related_memory_ids`: list of all concept IDs returned by `memory_search_with_experience` (function applies its own relevance filter internally)
   - `convergence_count`: `len(related_memory_ids)` — count of results that passed relevance threshold (mechanically derivable, no judgment)
   - `prior_work_ids`: any WORK-XXX or INV-XXX IDs referenced in matching concepts
4. Annotate the item with these fields

After processing all items, store enriched output:

```
ingester_ingest(
  content="<full enriched_items YAML — see output format below>",
  source_path="retro-enrichment:{work_id}",
  content_type_hint="techne"
)
```

Verify: `ingester_ingest` returns non-empty `concept_ids` (S407 silent-drop check).

## Output Format

Return to parent:

```
Enrichment Result: COMPLETE | PARTIAL | EMPTY

## Summary
- work_id: {work_id}
- items_processed: {count}
- items_enriched: {count with at least 1 related memory ID}
- items_cold: {count with 0 related memory IDs}

## Enriched Items
enriched_items:
  - type: {type}
    title: "{title}"
    evidence: "{evidence}"
    confidence: {confidence}
    severity: {severity}  # pass through from EXTRACT; present on bug items
    source_dimension: {dimension}
    suggested_priority: {priority}
    priority_rationale: "{rationale}"
    commit_concept_ids: [...]
    related_memory_ids: [id1, id2, ...]
    convergence_count: {N}
    prior_work_ids: ["WORK-XXX", ...]

## Memory
enrichment_concept_ids: [id from ingester_ingest]
```

Return `EMPTY` if `extracted_items` was empty (valid outcome — no items to enrich).
Return `PARTIAL` if memory search failed for some items but succeeded for others.

## Degradation

| Case | Handling |
|------|----------|
| `extracted_items` is empty | Return EMPTY immediately — no items to cross-reference |
| `memory_search_with_experience` fails for one item | Log failure, continue to next item, return PARTIAL |
| All memory searches fail | Return PARTIAL with `related_memory_ids: []` for all items, still store to memory |
| `ingester_ingest` fails | Log failure, return enriched_items without enrichment_concept_ids |

**Principle:** Enrichment never blocks closure. Degradation is graceful — cold items are valid.

## Edge Cases

- If `memory_search_with_experience` returns results with no relevance signal, set `related_memory_ids: []` and `convergence_count: 0`
- `prior_work_ids` extraction: scan result content for patterns matching `WORK-\d{3}` or `INV-\d{3}`
- If the same concept ID appears in both `memory_concept_ids` and search results, include it in `related_memory_ids` (self-referential links are valid convergence signals)

## Related

- **retro-cycle skill**: Predecessor — produces `extracted_items` this agent enriches
- **/close command**: Invoker — calls this agent after retro-cycle, before close-work-cycle
- **observation-triage-cycle**: Downstream consumer — reads `retro-enrichment:*` provenance tags
- **WORK-211**: Design investigation for this agent
- **WORK-217**: Implementation work item
```

#### File 2 (MODIFY): `.claude/commands/close.md`

**Location:** Lines 69-89, "Chain to Retro Cycle" and "Chain to Close Work Cycle" sections.

**Current Code:**
```markdown
## Chain to Retro Cycle

After work item is found, first invoke retro-cycle for structured reflection:

```
Skill(skill="retro-cycle")
```

This forces the agent into dedicated cognitive space (REFLECT -> DERIVE -> COMMIT -> EXTRACT) before entering "closing mode." Evidence-anchored observations are stored with typed provenance tags.

---

## Chain to Close Work Cycle

After retro-cycle completes, invoke close-work-cycle:
```

**Target Code:**
```markdown
## Chain to Retro Cycle

After work item is found, first invoke retro-cycle for structured reflection:

```
Skill(skill="retro-cycle")
```

This forces the agent into dedicated cognitive space (REFLECT -> DERIVE -> COMMIT -> EXTRACT) before entering "closing mode." Evidence-anchored observations are stored with typed provenance tags.

---

## Chain to Retro-Enrichment Agent

After retro-cycle completes and returns `extracted_items`, invoke retro-enrichment-agent if `extracted_items` is non-empty.

**IMPORTANT:** Before invoking Task(), the executing agent MUST substitute `{work_id}`, `{memory_concept_ids_json}`, `{extract_concept_ids_json}`, and `{extracted_items_yaml}` with actual values from the retro-cycle return object. Do NOT copy the template verbatim — literal placeholder strings will cause silent malformed input.

```
Task(
  subagent_type='retro-enrichment-agent',
  model='haiku',
  prompt='Enrich retro-cycle EXTRACT output for {work_id}.
    work_id: {work_id}
    memory_concept_ids: {memory_concept_ids_json}
    extract_concept_ids: {extract_concept_ids_json}
    extracted_items: {extracted_items_yaml}
    Cross-reference each item against memory via memory_search_with_experience.
    Annotate with related_memory_ids, convergence_count, prior_work_ids.
    Store enriched output with retro-enrichment:{work_id} provenance.
    Return enriched_items list + enrichment_concept_ids.'
)
```

If `extracted_items` is empty (trivial scale or no actionable items), skip enrichment.
Enrichment never blocks closure — proceed to close-work-cycle regardless of enrichment result.

---

## Chain to Close Work Cycle

After retro-enrichment completes (or was skipped), invoke close-work-cycle:
```

**Diff:**
```diff
 ## Chain to Close Work Cycle

-After retro-cycle completes, invoke close-work-cycle:
+After retro-enrichment completes (or was skipped), invoke close-work-cycle:
```

Plus the new section inserted between "Chain to Retro Cycle" and "Chain to Close Work Cycle".

### Call Chain

```
/close {work_id}
    |
    +-> Step 1: Lookup Work Item
    |
    +-> Step 1.1: Detect Effort Tier
    |
    +-> retro-cycle (REFLECT->DERIVE->COMMIT->EXTRACT)
    |       Returns: extracted_items, memory_concept_ids, extract_concept_ids
    |
    +-> retro-enrichment-agent [NEW]    # <-- what we're adding
    |       Input: work_id, memory_concept_ids, extract_concept_ids, extracted_items
    |       Returns: enriched_items, enrichment_concept_ids
    |       Model: haiku
    |       Condition: only if extracted_items non-empty
    |
    +-> close-work-cycle
            VALIDATE -> ARCHIVE -> CHAIN
```

### Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Separate agent card vs inline instructions in close.md | Separate agent card | Follows established pattern (close-work-cycle-agent, why-capturer). Agent card enables programmatic discovery via `list_agents()` / `filter_agents()`. |
| Invocation condition: non-empty extracted_items | Skip if empty | No items to enrich — trivial closures (2 max items) may still benefit from enrichment, but empty list is an unambiguous skip signal with zero risk. |
| Degradation: never block closure | Log failure, continue | Enrichment is additive — cold items are still valid retro output. Blocking closure on enrichment failure violates "RETRO never blocks closure" principle. |
| `memory_search_with_experience` mode | `knowledge_lookup` | Matches prior usage pattern in WORK-211 investigation (mem:88478). Returns semantically related concepts without requiring exact text match. |
| convergence_count definition | `len(related_memory_ids)` — count of results passing relevance threshold | Mechanically derivable, no judgment required — fits haiku model constraints. Eliminates ambiguous "same pattern" matching. |
| prior_work_ids extraction | Regex scan of result content for WORK-\d{3} pattern | Most reliable approach — concept content directly references work IDs. No reliance on metadata that may be absent. |
| Store enrichment to memory | Yes, always (even if cold) | Provenance tag `retro-enrichment:{work_id}` lets observation-triage-cycle query enrichment results. Storing cold results confirms enrichment ran — absence of IDs is itself signal (no convergence found). |

### Edge Cases

| Case | Handling | Test |
|------|----------|------|
| `extracted_items` is empty (trivial scale) | Skip enrichment invocation entirely | Test 4 (EMPTY result path) |
| Memory search returns no results | Annotate with `related_memory_ids: []`, `convergence_count: 0` | Covered in degradation spec |
| `ingester_ingest` silent drop (S407) | Verify non-empty concept_ids; re-invoke if empty | Covered in agent card process section |
| Item title too short for meaningful query | Use title + evidence combined | Covered in agent card process section |

### Risks

| Risk | Impact | Mitigation |
|------|--------|------------|
| Agent card frontmatter schema mismatch breaks `list_agents()` | M | Read critique-agent.md for exact schema; test_agent_cards test catches this immediately (TDD RED catches it before agent card write) |
| test_agent_cards.py count assertion (13→14) missed | M | Layer 0 Consumer Files table explicitly flags this. Step 1 updates test first (TDD RED). |
| close.md modification breaks lightweight_close path | L | Enrichment skip condition (if empty) covers trivial scale. Lightweight path (trivial retro) produces empty or 0-2 items — enrichment invoked at most with 2 items, adds minimal overhead. |
| `memory_search_with_experience` unavailable in haiku context | M | Agent card `tools` field lists it explicitly. If unavailable, degradation path returns PARTIAL without enrichment. Closure not blocked. |
| Retro-enrichment stored concept ID lost (S407 silent drop) | L | Agent card process section mandates verification after ingester_ingest. |

---

## Layer 2: Implementation Steps

<!-- Ordered steps. Each step is a sub-agent delegation unit.
     Producer: plan-author agent
     Consumer: DO agent + orchestrator -->

### Step 1: Update Test Assertions (RED)
- **spec_ref:** Layer 1 > Tests
- **input:** Layer 0 inventory complete, Layer 1 test specs defined
- **action:** Edit `tests/test_agent_cards.py`: change count assertions 13→14 on lines 97 and 195; add `"retro-enrichment-agent"` to expected set in `test_known_agents_present()`; add new `test_retro_enrichment_agent_fields()` test
- **output:** Test file updated, 3 tests now FAIL (count 14 != 13, name not found, agent None)
- **verify:** `pytest tests/test_agent_cards.py -v 2>&1 | grep -c "FAILED"` equals 3 or more

### Step 2: Create Agent Card (GREEN)
- **spec_ref:** Layer 1 > Design > File 1 (NEW)
- **input:** Step 1 complete (tests fail)
- **action:** Create `.claude/agents/retro-enrichment-agent.md` with exact content from Layer 1 Design File 1
- **output:** Agent card exists with valid frontmatter; `list_agents()` discovers it
- **verify:** `pytest tests/test_agent_cards.py -v` exits 0, all agent card tests pass

### Step 3: Integrate into /close Command
- **spec_ref:** Layer 1 > Design > File 2 (MODIFY)
- **input:** Step 2 complete (agent card GREEN)
- **action:** Edit `.claude/commands/close.md`: insert "Chain to Retro-Enrichment Agent" section between "Chain to Retro Cycle" and "Chain to Close Work Cycle" sections; update "Chain to Close Work Cycle" opening sentence per Layer 1 Design diff; also update the Example Usage section (lines 287-310) to include enrichment as a step after retro-cycle and renumber subsequent steps
- **output:** close.md contains enrichment invocation step
- **verify:** `grep "retro-enrichment-agent" .claude/commands/close.md` returns 1+ matches

### Step 4: Run Full Test Suite
- **spec_ref:** Layer 0 > Scope Metrics
- **input:** Step 3 complete
- **action:** Run full pytest suite to verify no regressions
- **output:** All tests pass, 0 new failures
- **verify:** `pytest tests/ -v 2>&1 | tail -5` shows "N passed, 0 failed" where N >= 1571

### Step 5: Update Documentation
- **spec_ref:** Layer 0 > Primary Files
- **input:** Step 4 complete
- **action:** Verify `.claude/agents/README.md` accurately describes the new agent schema (no content change needed — README describes schema format, not individual agents). AGENTS.md is auto-generated — run `just update-agents-md` if such recipe exists, otherwise note that AGENTS.md will be regenerated at next session start.
- **output:** No stale references to agent count in static docs
- **verify:** `grep "retro-enrichment" .claude/agents/README.md` (expect 0 — README is schema doc, not instance doc); `grep "retro-enrichment-agent" AGENTS.md` returns match if AGENTS.md was regenerated

---

## Ground Truth Verification

<!-- Computable verification protocol.
     Producer: plan-author agent
     Consumer: CHECK agent + orchestrator

     Every line has a command and expected output.
     The CHECK agent runs these mechanically — no judgment needed. -->

### Tests

| Command | Expected |
|---------|----------|
| `pytest tests/test_agent_cards.py -v` | All tests pass, 0 failed |
| `pytest tests/ -v 2>&1 \| tail -5` | 0 new failures vs 1571 pre-existing passing |

### Deliverables

| Deliverable | Verify Command | Expected |
|-------------|---------------|----------|
| `retro-enrichment-agent.md` agent card exists | `test -f .claude/agents/retro-enrichment-agent.md && echo EXISTS` | EXISTS |
| Agent card has input/output contract | `grep "input_contract\|output_contract" .claude/agents/retro-enrichment-agent.md` | 2 matches |
| Agent card model is haiku | `grep "^model: haiku" .claude/agents/retro-enrichment-agent.md` | 1 match |
| /close integration exists | `grep "retro-enrichment-agent" .claude/commands/close.md` | 1+ matches |
| Memory provenance tag present in agent card | `grep "retro-enrichment:{work_id}" .claude/agents/retro-enrichment-agent.md` | 1+ matches |
| Enrichment stores with correct provenance | `grep "retro-enrichment" .claude/agents/retro-enrichment-agent.md` | 2+ matches |

### Consumer Integrity

| Check | Command | Expected |
|-------|---------|----------|
| list_agents() finds new agent | `pytest tests/test_agent_cards.py::TestListAgents -v` | All pass |
| Agent count updated | `pytest tests/test_agent_cards.py::TestListAgents::test_agent_count -v` | PASS (14 agents) |
| filter_agents() count updated | `pytest tests/test_agent_cards.py::TestFilterAgents::test_no_filters_returns_all -v` | PASS (14 agents) |
| close.md chain order correct | `grep -n "Chain to" .claude/commands/close.md` | Retro → Enrichment → Close sequence |

### Completion Criteria (DoD)

- [ ] All tests pass (Layer 2 Step 4 verify)
- [ ] All WORK.md deliverables verified (table above)
- [ ] Runtime consumer exists: `/close` command references retro-enrichment-agent (Consumer Integrity table above)
- [ ] No stale references: agent count 13 not present in test assertions
- [ ] WHY captured (memory_refs populated via ingester_ingest)

> "Tests pass" proves code works. "Runtime consumer exists" proves code is used. (E2-250)
> "Tests pass" =/= "Deliverables complete". Both required. (E2-290)

---

## References

- `docs/work/active/WORK-211/WORK.md` — source investigation, agent contract design
- `.claude/skills/retro-cycle/SKILL.md` — integration point (output_contract: extracted_items, memory_concept_ids, extract_concept_ids)
- `.claude/commands/close.md` — invocation point (Chain to Retro Cycle section)
- `.claude/agents/close-work-cycle-agent.md` — similar agent pattern (frontmatter schema template)
- `.claude/skills/observation-triage-cycle/SKILL.md` — downstream consumer
- `tests/test_agent_cards.py` — consumer test requiring count update
- Memory: 88476 (separate agent decision), 88478 (memory cross-referencing feasibility), 88078 (S436 operator directive — haiku model, EXTRACT/COMMIT mechanical)

---
