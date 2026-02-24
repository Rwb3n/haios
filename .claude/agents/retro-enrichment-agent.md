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
- Enrichment agent is stateless with respect to `lightweight_close` — it processes whatever items it receives regardless of scale tier

## Related

- **retro-cycle skill**: Predecessor — produces `extracted_items` this agent enriches
- **/close command**: Invoker — calls this agent after retro-cycle, before close-work-cycle
- **observation-triage-cycle**: Downstream consumer — reads `retro-enrichment:*` provenance tags
- **WORK-211**: Design investigation for this agent
- **WORK-217**: Implementation work item
