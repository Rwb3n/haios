---
template: implementation_plan
status: complete
date: 2025-11-29
title: "Memory Synthesis Pipeline Implementation"
backlog_id: PLAN-SYNTHESIS-001
author: Hephaestus
project_phase: Phase 9 Enhancement
version: "1.0"
---
# generated: 2025-11-29
# System Auto: last updated on: 2025-12-09 18:49:05
# Memory Synthesis Pipeline Implementation Plan

> **Navigation:** [Quick Reference](#quick-reference) | [Strategic Overview](#strategic-overview) | [Implementation Details](#implementation-details) | [Validation](#validation)

> **Cold Start:** Read this document to understand the Memory Synthesis Pipeline. For vision context, see @docs/VISION_ANCHOR.md first. For exploration analysis, see @docs/specs/TRD-SYNTHESIS-EXPLORATION.md.

---

## Quick Reference

### Status: IMPLEMENTED (Session 15c)

| Item | Status |
|------|--------|
| Exploration Analysis | COMPLETE |
| User Requirements | CAPTURED |
| Implementation Plan | APPROVED |
| CLI Command | IMPLEMENTED |
| Tests | 16 PASSING |
| Migration 007 | APPLIED |
| Live Validation | CONFIRMED |

### Key Commands (Post-Implementation)

```bash
# Run synthesis pipeline
python -m haios_etl.cli synthesis run --limit 1000 --dry-run

# Check synthesis stats
python -m haios_etl.cli synthesis stats

# Run tests
python -m pytest tests/test_synthesis.py -v
```

### Key Files (Planned)

| File | Purpose |
|------|---------|
| `haios_etl/synthesis.py` | SynthesisManager class |
| `haios_etl/migrations/007_add_synthesis_tables.sql` | Schema changes |
| `tests/test_synthesis.py` | Unit and integration tests |
| `haios_etl/cli.py` | New `synthesis` command group |

---

## Strategic Overview

### The Problem

The memory system has accumulated significant data:
- **34,000+ concepts** extracted from 595 files
- **200+ reasoning traces** with strategy extraction
- **High redundancy** - many concepts express the same idea differently
- **No meta-patterns** - individual insights not synthesized into higher-order knowledge
- **No cross-pollination** - concepts and traces exist in silos

### The Solution

A 5-stage synthesis pipeline that:
1. **Clusters** similar memories using vector similarity
2. **Synthesizes** clusters into meta-patterns using LLM
3. **Stores** synthesized knowledge with provenance links
4. **Cross-pollinates** concepts with reasoning traces
5. **Prunes** redundant entries (optional)

### User Requirements (Session 15b)

| Requirement | Value |
|-------------|-------|
| Input Sources | Concepts (34k) + Reasoning Traces (200+) |
| Cross-pollinate | Yes - find overlaps between types |
| Goals | Dedupe + Meta-patterns + Knowledge Graph |
| Trigger | On-demand CLI command |

### Architecture Overview

```
                 Existing Memories
                 (34k concepts, 200+ traces)
                          |
                          v
        +----------------------------------+
        |     1. CLUSTER                   |
        |  - Generate/verify embeddings    |
        |  - Group by similarity (>0.85)   |
        |  - Separate: concepts vs traces  |
        +----------------------------------+
                          |
                          v
        +----------------------------------+
        |     2. SYNTHESIZE                |
        |  - LLM: "Common insight?"        |
        |  - Output: meta-pattern          |
        |  - Type: SynthesizedInsight      |
        +----------------------------------+
                          |
                          v
        +----------------------------------+
        |     3. STORE                     |
        |  - New concept row               |
        |  - memory_relationships links    |
        |  - memory_metadata tags          |
        +----------------------------------+
                          |
                          v
        +----------------------------------+
        |     4. CROSS-POLLINATE           |
        |  - Find concept<->trace overlaps |
        |  - Generate bridge insights      |
        +----------------------------------+
                          |
                          v
        +----------------------------------+
        |     5. PRUNE (Optional)          |
        |  - Archive low-value duplicates  |
        |  - Mark as synthesis_source      |
        +----------------------------------+
```

---

## Implementation Details

### Phase 1: Schema Migration (007)

**File:** `haios_etl/migrations/007_add_synthesis_tables.sql`

```sql
-- Add synthesis-specific columns to concepts table
ALTER TABLE concepts ADD COLUMN synthesis_source_count INTEGER DEFAULT 0;
ALTER TABLE concepts ADD COLUMN synthesis_confidence REAL;
ALTER TABLE concepts ADD COLUMN synthesized_at TIMESTAMP;

-- Add synthesis tracking to memory_metadata keys
-- Keys: 'synthesis_status', 'synthesis_cluster_id', 'synthesis_parent_id'

-- Add synthesis relationship type
-- relationship_type values: 'synthesized_from', 'cross_pollinates'

-- Create synthesis_clusters table for batch tracking
CREATE TABLE IF NOT EXISTS synthesis_clusters (
    id INTEGER PRIMARY KEY,
    cluster_type TEXT NOT NULL,  -- 'concept' or 'trace'
    centroid_embedding BLOB,
    member_count INTEGER DEFAULT 0,
    synthesized_concept_id INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (synthesized_concept_id) REFERENCES concepts(id)
);

-- Index for efficient cluster lookups
CREATE INDEX IF NOT EXISTS idx_synthesis_clusters_type ON synthesis_clusters(cluster_type);
```

### Phase 2: SynthesisManager Class

**File:** `haios_etl/synthesis.py`

```python
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import sqlite3
from .database import DatabaseManager
from .extraction import ExtractionManager

@dataclass
class SynthesisResult:
    """Result of synthesizing a cluster of memories."""
    title: str
    content: str
    confidence: float
    source_ids: List[int]
    source_type: str  # 'concept' or 'trace'

class SynthesisManager:
    """Manages memory consolidation and synthesis."""

    SIMILARITY_THRESHOLD = 0.85
    MIN_CLUSTER_SIZE = 2
    MAX_CLUSTER_SIZE = 20

    def __init__(self, db_path: str, extractor: ExtractionManager):
        self.db = DatabaseManager(db_path)
        self.extractor = extractor

    # Stage 1: Clustering
    def find_similar_concepts(self, limit: int = 1000) -> List[List[int]]:
        """Group concepts by vector similarity."""
        pass

    def find_similar_traces(self, limit: int = 100) -> List[List[int]]:
        """Group reasoning traces by query embedding similarity."""
        pass

    # Stage 2: Synthesis
    def synthesize_cluster(self,
                          cluster: List[Dict],
                          source_type: str) -> SynthesisResult:
        """Use LLM to extract meta-pattern from cluster."""
        pass

    # Stage 3: Storage
    def store_synthesis(self, result: SynthesisResult) -> int:
        """Store synthesized concept with provenance."""
        pass

    # Stage 4: Cross-pollination
    def find_cross_type_overlaps(self) -> List[Tuple[int, int, float]]:
        """Find concept<->trace similarities for bridging."""
        pass

    def create_bridge_insight(self,
                             concept_id: int,
                             trace_id: int) -> Optional[SynthesisResult]:
        """Generate bridge insight connecting concept and trace."""
        pass

    # Stage 5: Pruning
    def mark_as_synthesized(self, source_ids: List[int],
                           synthesized_id: int) -> None:
        """Mark source memories as contributing to synthesis."""
        pass

    # Orchestration
    def run_synthesis_pipeline(self,
                              dry_run: bool = False,
                              limit: int = 1000) -> Dict:
        """Run full synthesis pipeline."""
        pass

    def get_synthesis_stats(self) -> Dict:
        """Get statistics about synthesis state."""
        pass
```

### Phase 3: LLM Prompts

**Concept Cluster Synthesis:**

```
Analyze these related concepts extracted from the HAIOS codebase.
They are semantically similar (>85% cosine similarity).

CONCEPTS:
{formatted_concepts}

Extract ONE higher-order insight that captures their common theme.
This should be a transferable principle, not a summary.

Output JSON:
{
  "title": "Short title (max 10 words)",
  "content": "The synthesized insight (2-3 sentences)",
  "confidence": 0.0-1.0
}
```

**Trace Cluster Synthesis:**

```
Analyze these similar reasoning traces from past search operations.

TRACES:
{formatted_traces}

Extract ONE meta-strategy that could guide future similar queries.
Focus on WHAT WAS LEARNED, not what happened.

Output JSON:
{
  "title": "Strategy name (max 8 words)",
  "content": "The meta-strategy (2-3 sentences)",
  "confidence": 0.0-1.0
}
```

**Cross-Pollination Bridge:**

```
A concept and a reasoning trace have high semantic overlap.

CONCEPT:
{concept_content}

REASONING TRACE:
Query: {trace_query}
Strategy: {trace_strategy}

Generate a BRIDGE INSIGHT that connects theory (concept) with practice (trace).

Output JSON:
{
  "title": "Bridge title",
  "content": "How the concept manifests in practice",
  "confidence": 0.0-1.0
}
```

### Phase 4: CLI Commands

**File:** `haios_etl/cli.py` (additions)

```python
@cli.group()
def synthesis():
    """Memory synthesis pipeline commands."""
    pass

@synthesis.command()
@click.option('--limit', default=1000, help='Max items to process')
@click.option('--dry-run', is_flag=True, help='Preview without changes')
@click.option('--concepts-only', is_flag=True, help='Only synthesize concepts')
@click.option('--traces-only', is_flag=True, help='Only synthesize traces')
@click.option('--skip-cross-pollinate', is_flag=True, help='Skip cross-pollination')
def run(limit, dry_run, concepts_only, traces_only, skip_cross_pollinate):
    """Run synthesis pipeline."""
    pass

@synthesis.command()
def stats():
    """Show synthesis statistics."""
    pass

@synthesis.command()
@click.argument('cluster_id', type=int)
def inspect(cluster_id):
    """Inspect a synthesis cluster."""
    pass
```

### Phase 5: Tests

**File:** `tests/test_synthesis.py`

```python
class TestSynthesisClustering:
    def test_find_similar_concepts_returns_clusters(self):
        """Verify clustering groups similar concepts."""
        pass

    def test_cluster_respects_min_size(self):
        """Clusters smaller than MIN_CLUSTER_SIZE excluded."""
        pass

    def test_cluster_respects_max_size(self):
        """Large groups split into manageable clusters."""
        pass

class TestSynthesisLLM:
    def test_synthesize_cluster_returns_result(self):
        """LLM synthesis produces valid result."""
        pass

    def test_synthesize_handles_llm_failure(self):
        """Graceful fallback on LLM error."""
        pass

class TestSynthesisStorage:
    def test_store_synthesis_creates_concept(self):
        """Synthesized insight stored as new concept."""
        pass

    def test_store_synthesis_creates_relationships(self):
        """Provenance links created in memory_relationships."""
        pass

    def test_store_synthesis_creates_metadata(self):
        """Metadata tags applied correctly."""
        pass

class TestCrossPollination:
    def test_find_overlaps_returns_pairs(self):
        """Cross-type similarity detection works."""
        pass

    def test_bridge_insight_created(self):
        """Bridge insights link concepts to traces."""
        pass

class TestSynthesisPipeline:
    def test_dry_run_no_changes(self):
        """Dry run doesn't modify database."""
        pass

    def test_full_pipeline_integration(self):
        """End-to-end pipeline test."""
        pass
```

---

## Validation

### Success Criteria

| Criterion | Target |
|-----------|--------|
| Migration 007 applied | Schema changes in place |
| SynthesisManager implemented | All 5 stages functional |
| CLI commands working | `synthesis run/stats/inspect` |
| Tests passing | 12+ tests covering all stages |
| Dry run verified | No changes in dry-run mode |
| Live validation | At least 10 clusters synthesized |

### Performance Targets

| Metric | Target | Rationale |
|--------|--------|-----------|
| Clustering speed | < 30s for 1000 items | Batch vector comparison |
| Synthesis per cluster | < 5s | Single LLM call |
| Full pipeline (1000 items) | < 10 minutes | Acceptable for batch |

### Estimated Effort

| Phase | Hours | Priority |
|-------|-------|----------|
| Schema Migration (007) | 0.5 | P1 |
| SynthesisManager skeleton | 1 | P1 |
| Clustering implementation | 2 | P1 |
| LLM synthesis | 1.5 | P1 |
| Storage with provenance | 1 | P1 |
| Cross-pollination | 1.5 | P2 |
| Pruning (optional) | 1 | P3 |
| CLI commands | 1 | P1 |
| Tests | 2 | P1 |
| Documentation | 0.5 | P1 |

**Total: ~12 hours**

---

## Design Decisions

| ID | Decision | Rationale |
|----|----------|-----------|
| DD-005 | SynthesizedInsight as concept type | Reuses existing schema |
| DD-006 | 0.85 similarity threshold | Slightly stricter than 0.8 for quality |
| DD-007 | Cluster size 2-20 | Balance granularity vs LLM context |
| DD-008 | Separate concept/trace pipelines | Different synthesis prompts needed |
| DD-009 | Bridge insights as new concepts | Creates knowledge graph links |

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| LLM cost for 34k concepts | MEDIUM | HIGH | Batch by cluster, limit first run |
| Low-quality synthesis | MEDIUM | MEDIUM | Confidence threshold, human review |
| Slow clustering | LOW | MEDIUM | Limit batch size, add indexes |
| Data loss during pruning | LOW | HIGH | Soft delete with archive flag |

---

## Related Documents

### This Document Links To:
- @docs/VISION_ANCHOR.md - Core architectural vision
- @docs/epistemic_state.md - Current system state
- @docs/specs/TRD-SYNTHESIS-EXPLORATION.md - Exploration analysis
- @docs/specs/TRD-ETL-v2.md - ETL specification
- @haios_etl/refinement.py - Existing refinement patterns

### Documents That Link Here:
- @docs/epistemic_state.md - Active Planning section
- @docs/plans/README.md - Active Plans table

---

## Approval Request

**Decision Required:**
1. Approve this implementation plan
2. Request modifications
3. Defer to future session

**Recommended Starting Point:** Phase 1 (Migration) + Phase 2 (SynthesisManager skeleton)


<!-- VALIDATION ERRORS (2025-11-29 20:15:00):
  - ERROR: Invalid status 'complete' for implementation_plan template. Allowed: draft, approved, rejected
-->
