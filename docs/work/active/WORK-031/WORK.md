---
template: work_item
id: WORK-031
title: CorpusLoader Module Implementation
type: feature
status: complete
owner: Hephaestus
created: 2026-01-29
spawned_by: null
chapter: CH-001
arc: pipeline
closed: '2026-01-29'
priority: medium
effort: medium
traces_to:
- REQ-TRACE-004
- REQ-TRACE-005
requirement_refs: []
source_files:
- .claude/haios/modules/corpus_loader.py
acceptance_criteria:
- Corpus schema defined (YAML)
- CorpusLoader class implements discover() and filter_by_type()
- Multi-source corpus definition works
- Exclusion patterns work
- RequirementExtractor accepts CorpusLoader
- CLI commands work
- Tests verify discovery with sample corpus
blocked_by: []
blocks:
- WORK-032
enables: []
current_node: backlog
node_history:
- node: backlog
  entered: 2026-01-29 18:31:50
  exited: null
artifacts: []
cycle_docs: {}
memory_refs:
- 82554
- 82555
- 81334
- 82581
- 82582
- 82583
- 82584
- 82589
- 82590
- 82591
- 82592
- 82593
- 82594
- 82595
- 82596
- 82597
- 82598
extensions: {}
version: '2.0'
generated: 2026-01-29
last_updated: '2026-01-29T19:43:15'
---
# WORK-031: CorpusLoader Module Implementation

@docs/README.md
@docs/epistemic_state.md

---

## Context

**Problem:** RequirementExtractor currently uses `rglob("*.md")` for file discovery, which is too broad and not configurable. The Pipeline needs a CorpusLoader that can define corpus from YAML config, support multiple source directories, filter and exclude patterns.

**Root cause:** No corpus definition mechanism exists. File discovery is hardcoded in RequirementExtractor._discover_files().

**Solution:** Build CorpusLoader module that:
1. Reads corpus definition from YAML config
2. Supports multiple source directories with patterns
3. Filters by document type
4. Supports exclusion patterns
5. Integrates with RequirementExtractor as file discovery mechanism

This enables the INGEST stage to work on arbitrary corpora, not just hardcoded HAIOS paths.

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

- [x] `.claude/haios/modules/corpus_loader.py` - CorpusLoader class
- [x] Corpus schema definition (YAML format specification)
- [x] `discover()` method returns filtered file list
- [x] `filter_by_type()` method for document type filtering
- [x] Multi-source corpus definition support
- [x] Exclusion pattern support
- [x] CLI command: `corpus-list <corpus_config>`
- [x] CLI integration: `extract-requirements --corpus <corpus_config>`
- [x] Unit tests: `tests/test_corpus_loader.py`
- [x] Example corpus config: `.claude/haios/config/corpus/haios-requirements.yaml`

---

## History

### 2026-01-29 - Created (Session 257)
- Initial creation from L4/E2.3 gap analysis
- Chapter CH-001 created with requirements
- Part of INGEST stage completion for Pipeline arc

---

## References

- @.claude/haios/epochs/E2_3/arcs/pipeline/CH-001-corpus-loader.md (chapter definition)
- @.claude/haios/modules/requirement_extractor.py (consumer)
- @.claude/haios/epochs/E2/architecture/S26-pipeline-architecture.md (stage interface)
