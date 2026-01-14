# generated: 2025-11-29
# System Auto: last updated on: 2025-12-20 10:47:22
"""
Memory Synthesis Pipeline - Phase 9 Enhancement

This module implements memory consolidation and synthesis per PLAN-SYNTHESIS-001.
The pipeline has 5 stages:
1. CLUSTER - Group similar memories by vector similarity
2. SYNTHESIZE - Extract meta-patterns using LLM
3. STORE - Save synthesized concepts with provenance
4. CROSS-POLLINATE - Bridge concepts and reasoning traces
5. PRUNE - Archive redundant entries (optional)
"""

import logging
import json
import struct
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime

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
    cluster_id: Optional[int] = None


@dataclass
class ClusterInfo:
    """Information about a memory cluster."""
    id: int
    cluster_type: str
    member_ids: List[int]
    member_count: int
    centroid: Optional[List[float]] = None


@dataclass
class SynthesisStats:
    """Statistics about synthesis pipeline state."""
    total_concepts: int
    total_traces: int
    synthesized_concepts: int
    pending_clusters: int
    completed_clusters: int
    cross_pollination_links: int


class SynthesisManager:
    """
    Manages memory consolidation and synthesis.

    Implements a 5-stage pipeline:
    1. Clustering - Group similar memories
    2. Synthesis - Extract meta-patterns
    3. Storage - Save with provenance
    4. Cross-pollination - Bridge types
    5. Pruning - Archive redundant
    """

    # Configuration
    SIMILARITY_THRESHOLD = 0.85  # DD-006: Slightly stricter than 0.8
    CROSS_POLLINATION_THRESHOLD = 0.65  # Lower threshold for cross-modal comparison (Empirically verified)
    MIN_CLUSTER_SIZE = 2
    MAX_CLUSTER_SIZE = 20  # DD-007: Balance granularity vs LLM context

    def __init__(self, db_path: str, extractor: Optional[ExtractionManager] = None):
        """
        Initialize the SynthesisManager.

        Args:
            db_path: Path to the SQLite database
            extractor: ExtractionManager for embeddings and LLM calls
        """
        self.db = DatabaseManager(db_path)
        self.extractor = extractor
        self.logger = logging.getLogger(__name__)

    # =========================================================================
    # Stage 1: CLUSTERING
    # =========================================================================

    def find_similar_concepts(self, limit: int = 1000) -> List[ClusterInfo]:
        """
        Group concepts by vector similarity.

        Uses embeddings from the embeddings table to find concepts
        that are semantically similar (>85% cosine similarity).

        Args:
            limit: Maximum number of concepts to consider

        Returns:
            List of ClusterInfo objects, each containing member IDs
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Get concepts with embeddings that haven't been clustered
        # E2-FIX-004: Added synthesis_cluster_id IS NULL to exclude already-clustered concepts
        # Bug: Query checked synthesized_at, but store_synthesis sets synthesis_cluster_id
        # Fix: Align query filter with what store actually sets
        sql = """
            SELECT c.id, c.content, e.vector
            FROM concepts c
            JOIN embeddings e ON c.id = e.concept_id
            WHERE c.synthesized_at IS NULL
              AND c.synthesis_cluster_id IS NULL
            ORDER BY c.id
            LIMIT ?
        """
        cursor.execute(sql, (limit,))
        rows = cursor.fetchall()

        if not rows:
            self.logger.info("No unsynthesized concepts with embeddings found")
            return []

        # Build clusters using simple greedy approach
        # TODO: Consider more sophisticated clustering (DBSCAN, etc.)
        clusters = self._build_clusters(rows, 'concept')

        self.logger.info(f"Found {len(clusters)} concept clusters from {len(rows)} concepts")
        return clusters

    def find_similar_traces(self, limit: int = 100) -> List[ClusterInfo]:
        """
        Group reasoning traces by query embedding similarity.

        Args:
            limit: Maximum number of traces to consider

        Returns:
            List of ClusterInfo objects
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Get traces with embeddings that have strategies
        sql = """
            SELECT id, query, query_embedding
            FROM reasoning_traces
            WHERE query_embedding IS NOT NULL
            AND strategy_title IS NOT NULL
            ORDER BY id
            LIMIT ?
        """
        cursor.execute(sql, (limit,))
        rows = cursor.fetchall()

        if not rows:
            self.logger.info("No reasoning traces with embeddings found")
            return []

        # Build clusters
        clusters = self._build_clusters(rows, 'trace')

        self.logger.info(f"Found {len(clusters)} trace clusters from {len(rows)} traces")
        return clusters

    def _build_clusters(
        self,
        items: List[Tuple],
        item_type: str
    ) -> List[ClusterInfo]:
        """
        Build clusters from items using greedy similarity grouping.

        Args:
            items: List of (id, content, embedding) tuples
            item_type: 'concept' or 'trace'

        Returns:
            List of ClusterInfo objects
        """
        if not items:
            return []

        # Track which items are already clustered
        clustered = set()
        clusters = []

        # E2-011 Phase 1b: Progress logging for clustering
        import time
        total_items = len(items)
        start_time = time.time()
        last_progress_time = start_time
        progress_interval = 10  # Log every N items processed
        time_interval = 5       # Or every N seconds

        for i, (item_id, content, embedding) in enumerate(items):
            # Progress logging (E2-011 Phase 1b)
            current_time = time.time()
            if i > 0 and (i % progress_interval == 0 or (current_time - last_progress_time) >= time_interval):
                elapsed = current_time - start_time
                pct = (i / total_items) * 100 if total_items > 0 else 0
                self.logger.info(f"Clustering progress: {i}/{total_items} items ({pct:.1f}%) - {elapsed:.1f}s elapsed")
                last_progress_time = current_time
            if item_id in clustered:
                continue

            # Start new cluster with this item
            cluster_members = [item_id]
            clustered.add(item_id)

            # Find similar items
            item_embedding = self._parse_embedding(embedding)
            if item_embedding is None:
                continue

            for j, (other_id, other_content, other_embedding) in enumerate(items):
                if other_id in clustered:
                    continue
                if len(cluster_members) >= self.MAX_CLUSTER_SIZE:
                    break

                other_vec = self._parse_embedding(other_embedding)
                if other_vec is None:
                    continue

                similarity = self._cosine_similarity(item_embedding, other_vec)
                if similarity >= self.SIMILARITY_THRESHOLD:
                    cluster_members.append(other_id)
                    clustered.add(other_id)

            # Only keep clusters with minimum size
            if len(cluster_members) >= self.MIN_CLUSTER_SIZE:
                clusters.append(ClusterInfo(
                    id=len(clusters),  # Temporary ID
                    cluster_type=item_type,
                    member_ids=cluster_members,
                    member_count=len(cluster_members),
                    centroid=item_embedding  # Use first item as centroid
                ))

        return clusters

    def _parse_embedding(self, blob: bytes) -> Optional[List[float]]:
        """Parse embedding from SQLite BLOB format."""
        if blob is None:
            return None
        try:
            # Embeddings are stored as packed floats
            num_floats = len(blob) // 4
            return list(struct.unpack(f'{num_floats}f', blob))
        except Exception as e:
            self.logger.warning(f"Failed to parse embedding: {e}")
            return None

    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        """Compute cosine similarity between two vectors."""
        if len(a) != len(b):
            return 0.0

        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5

        if norm_a == 0 or norm_b == 0:
            return 0.0

        return dot_product / (norm_a * norm_b)

    # =========================================================================
    # Stage 2: SYNTHESIS
    # =========================================================================

    def synthesize_cluster(
        self,
        cluster: ClusterInfo
    ) -> Optional[SynthesisResult]:
        """
        Use LLM to extract meta-pattern from cluster.

        Args:
            cluster: ClusterInfo with member IDs

        Returns:
            SynthesisResult or None if synthesis failed
        """
        if self.extractor is None:
            self.logger.warning("No extractor configured, cannot synthesize")
            return None

        # Fetch cluster content
        if cluster.cluster_type == 'concept':
            contents = self._get_concept_contents(cluster.member_ids)
            prompt = self._build_concept_synthesis_prompt(contents)
        else:
            contents = self._get_trace_contents(cluster.member_ids)
            prompt = self._build_trace_synthesis_prompt(contents)

        if not contents:
            return None

        # Call LLM
        try:
            result = self._call_synthesis_llm(prompt)
            if result:
                return SynthesisResult(
                    title=result.get('title', 'Untitled Insight'),
                    content=result.get('content', ''),
                    confidence=result.get('confidence', 0.5),
                    source_ids=cluster.member_ids,
                    source_type=cluster.cluster_type,
                    cluster_id=cluster.id
                )
        except Exception as e:
            self.logger.error(f"Synthesis failed for cluster {cluster.id}: {e}")

        return None

    def _get_concept_contents(self, concept_ids: List[int]) -> List[Dict]:
        """Fetch concept content by IDs."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        placeholders = ','.join('?' * len(concept_ids))
        sql = f"SELECT id, type, content FROM concepts WHERE id IN ({placeholders})"
        cursor.execute(sql, concept_ids)

        return [{'id': r[0], 'type': r[1], 'content': r[2]} for r in cursor.fetchall()]

    def _get_trace_contents(self, trace_ids: List[int]) -> List[Dict]:
        """Fetch trace content by IDs."""
        conn = self.db.get_connection()
        cursor = conn.cursor()

        placeholders = ','.join('?' * len(trace_ids))
        sql = f"""
            SELECT id, query, strategy_title, strategy_content
            FROM reasoning_traces
            WHERE id IN ({placeholders})
        """
        cursor.execute(sql, trace_ids)

        return [{
            'id': r[0],
            'query': r[1],
            'strategy_title': r[2],
            'strategy_content': r[3]
        } for r in cursor.fetchall()]

    def _build_concept_synthesis_prompt(self, concepts: List[Dict]) -> str:
        """Build LLM prompt for concept cluster synthesis."""
        formatted = "\n".join([
            f"- [{c['type']}] {c['content'][:200]}..."
            if len(c['content']) > 200 else f"- [{c['type']}] {c['content']}"
            for c in concepts
        ])

        return f"""Analyze these related concepts extracted from the HAIOS codebase.
They are semantically similar (>85% cosine similarity).

CONCEPTS:
{formatted}

Extract ONE higher-order insight that captures their common theme.
This should be a transferable principle, not a summary.

Output ONLY valid JSON (no markdown):
{{"title": "Short title (max 10 words)", "content": "The synthesized insight (2-3 sentences)", "confidence": 0.0-1.0}}"""

    def _build_trace_synthesis_prompt(self, traces: List[Dict]) -> str:
        """Build LLM prompt for trace cluster synthesis."""
        formatted = "\n".join([
            f"- Query: {t['query'][:100]}... | Strategy: {t['strategy_title']}"
            for t in traces
        ])

        return f"""Analyze these similar reasoning traces from past search operations.

TRACES:
{formatted}

Extract ONE meta-strategy that could guide future similar queries.
Focus on WHAT WAS LEARNED, not what happened.

Output ONLY valid JSON (no markdown):
{{"title": "Strategy name (max 8 words)", "content": "The meta-strategy (2-3 sentences)", "confidence": 0.0-1.0}}"""

    def _call_synthesis_llm(self, prompt: str) -> Optional[Dict]:
        """Call LLM for synthesis."""
        import google.generativeai as genai

        genai.configure(api_key=self.extractor.api_key)
        model = genai.GenerativeModel(self.extractor.model_id)

        try:
            response = model.generate_content(prompt)
            text = response.text.strip()

            # Clean up markdown code blocks
            if text.startswith("```"):
                text = text.split("\n", 1)[1]
                if text.endswith("```"):
                    text = text[:-3]
                text = text.strip()

            return json.loads(text)
        except json.JSONDecodeError as e:
            self.logger.warning(f"Synthesis JSON parse failed: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Synthesis LLM call failed: {e}")
            return None

    # =========================================================================
    # Stage 3: STORAGE
    # =========================================================================

    def store_synthesis(self, result: SynthesisResult) -> Optional[int]:
        """
        Store synthesized concept with provenance.

        Creates a new concept and links it to source memories
        via the synthesis_provenance table.

        Args:
            result: SynthesisResult from synthesis stage

        Returns:
            ID of the new synthesized concept, or None if failed
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        try:
            # 1. Create new concept
            cursor.execute("""
                INSERT INTO concepts (type, content, source_adr,
                    synthesis_source_count, synthesis_confidence, synthesized_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                'SynthesizedInsight',
                f"[{result.title}] {result.content}",
                'virtual:synthesis',
                len(result.source_ids),
                result.confidence,
                datetime.now().isoformat()
            ))
            new_concept_id = cursor.lastrowid

            # 2. Save cluster reference
            cluster_id = self._save_cluster(
                cursor,
                result.source_type,
                result.source_ids,
                new_concept_id
            )

            # Update concept with cluster ID
            cursor.execute("""
                UPDATE concepts SET synthesis_cluster_id = ?
                WHERE id = ?
            """, (cluster_id, new_concept_id))

            # 3. Create provenance links
            for source_id in result.source_ids:
                cursor.execute("""
                    INSERT INTO synthesis_provenance
                    (synthesized_concept_id, source_type, source_id)
                    VALUES (?, ?, ?)
                """, (new_concept_id, result.source_type, source_id))

            # 4. Mark source concepts as synthesized (if concepts)
            if result.source_type == 'concept':
                placeholders = ','.join('?' * len(result.source_ids))
                cursor.execute(f"""
                    UPDATE concepts
                    SET synthesis_cluster_id = ?
                    WHERE id IN ({placeholders})
                """, [cluster_id] + result.source_ids)

            conn.commit()

            # 5. Generate embedding for the synthesized concept (E2-FIX-001)
            # Without embedding, synthesized concepts are invisible to retrieval
            if self.extractor:
                try:
                    content = f"[{result.title}] {result.content}"
                    embedding = self.extractor.embed_content(content[:8000])
                    if embedding:
                        cursor.execute("""
                            INSERT INTO embeddings (concept_id, vector, model, dimensions)
                            VALUES (?, ?, ?, ?)
                        """, (
                            new_concept_id,
                            struct.pack(f'{len(embedding)}f', *embedding),
                            "text-embedding-004",
                            len(embedding)
                        ))
                        conn.commit()
                        self.logger.info(f"Generated embedding for synthesis {new_concept_id}")
                except Exception as embed_err:
                    self.logger.warning(f"Failed to generate embedding for synthesis: {embed_err}")
                    # Continue without embedding - can be backfilled later

            self.logger.info(
                f"Stored synthesis: {result.title} "
                f"(id={new_concept_id}, sources={len(result.source_ids)})"
            )
            return new_concept_id

        except Exception as e:
            conn.rollback()
            self.logger.error(f"Failed to store synthesis: {e}")
            return None

    def _save_cluster(
        self,
        cursor,
        cluster_type: str,
        member_ids: List[int],
        synthesized_concept_id: int
    ) -> int:
        """Save cluster record and members."""
        # Insert cluster
        cursor.execute("""
            INSERT INTO synthesis_clusters
            (cluster_type, member_count, synthesized_concept_id, status, synthesized_at)
            VALUES (?, ?, ?, 'synthesized', ?)
        """, (cluster_type, len(member_ids), synthesized_concept_id, datetime.now().isoformat()))
        cluster_id = cursor.lastrowid

        # Insert members
        for member_id in member_ids:
            cursor.execute("""
                INSERT INTO synthesis_cluster_members
                (cluster_id, member_type, member_id)
                VALUES (?, ?, ?)
            """, (cluster_id, cluster_type, member_id))

        return cluster_id

    # =========================================================================
    # Stage 4: CROSS-POLLINATION
    # =========================================================================

    def _bridge_exists(self, concept_id: int, trace_id: int) -> bool:
        """
        Check if a bridge insight already exists for this concept-trace pair.

        Idempotency guard to prevent duplicate bridge creation on repeated runs.

        Args:
            concept_id: The concept ID
            trace_id: The trace ID

        Returns:
            True if bridge already exists, False otherwise
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Check if there's a synthesized concept with both this concept and trace as sources
        cursor.execute("""
            SELECT 1 FROM synthesis_provenance p1
            JOIN synthesis_provenance p2
              ON p1.synthesized_concept_id = p2.synthesized_concept_id
            WHERE p1.source_type = 'cross' AND p1.source_id = ?
              AND p2.source_type = 'cross' AND p2.source_id = ?
            LIMIT 1
        """, (concept_id, trace_id))

        return cursor.fetchone() is not None

    def find_cross_type_overlaps(
        self,
        limit: int = 100,
        concept_sample: int = 0,
        trace_sample: int = 0
    ) -> List[Tuple[int, int, float]]:
        """
        Find concept<->trace similarities for bridging.

        Identifies concepts that are semantically related to
        reasoning traces, enabling knowledge transfer between types.

        Args:
            limit: Maximum number of pairs to return
            concept_sample: Max concepts to sample (0 = ALL)
            trace_sample: Max traces to sample (0 = ALL)

        Returns:
            List of (concept_id, trace_id, similarity) tuples
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Get concepts with embeddings
        concept_sql = """
            SELECT c.id, e.vector
            FROM concepts c
            JOIN embeddings e ON c.id = e.concept_id
            WHERE c.type != 'SynthesizedInsight'
        """
        if concept_sample > 0:
            concept_sql += f" LIMIT {concept_sample}"
        cursor.execute(concept_sql)
        concepts = cursor.fetchall()

        # Get traces with embeddings
        trace_sql = """
            SELECT id, query_embedding
            FROM reasoning_traces
            WHERE query_embedding IS NOT NULL
        """
        if trace_sample > 0:
            trace_sql += f" LIMIT {trace_sample}"
        cursor.execute(trace_sql)
        traces = cursor.fetchall()

        if not concepts or not traces:
            self.logger.info("No concepts or traces available for cross-pollination")
            return []

        # Find overlaps
        overlaps = []
        max_similarity = 0.0
        comparisons = 0
        near_misses = []  # Track pairs that almost matched

        # Progress tracking (E2-011 Phase 1a)
        import time
        total_comparisons = len(concepts) * len(traces)
        start_time = time.time()
        last_progress_time = start_time
        progress_interval = 10000  # Log every N comparisons
        time_interval = 10  # Or every N seconds

        self.logger.info(f"Comparing {len(concepts)} concepts against {len(traces)} traces (Threshold: {self.CROSS_POLLINATION_THRESHOLD})")

        for concept_id, concept_vec_blob in concepts:
            concept_vec = self._parse_embedding(concept_vec_blob)
            if concept_vec is None:
                continue

            for trace_id, trace_vec_blob in traces:
                trace_vec = self._parse_embedding(trace_vec_blob)
                if trace_vec is None:
                    continue

                comparisons += 1
                similarity = self._cosine_similarity(concept_vec, trace_vec)
                max_similarity = max(max_similarity, similarity)

                if similarity >= self.CROSS_POLLINATION_THRESHOLD:
                    overlaps.append((concept_id, trace_id, similarity))
                elif similarity >= 0.65: # Log near misses
                    near_misses.append((concept_id, trace_id, similarity))

                # Progress logging (E2-011)
                current_time = time.time()
                if comparisons % progress_interval == 0 or (current_time - last_progress_time) >= time_interval:
                    elapsed = current_time - start_time
                    rate = comparisons / elapsed if elapsed > 0 else 0
                    pct = (comparisons / total_comparisons) * 100 if total_comparisons > 0 else 0
                    eta_sec = (total_comparisons - comparisons) / rate if rate > 0 else 0
                    self.logger.info(f"Progress: {comparisons}/{total_comparisons} ({pct:.1f}%) - {elapsed:.0f}s elapsed - {rate/1000:.1f}k/sec - ETA {eta_sec:.0f}s")
                    last_progress_time = current_time

        # Log diagnostics
        self.logger.info(f"Cross-pollination stats: {comparisons} comparisons, Max Sim: {max_similarity:.4f}")
        if not overlaps and near_misses:
            near_misses.sort(key=lambda x: x[2], reverse=True)
            top_misses = near_misses[:3]
            self.logger.info(f"Top 3 near misses: {[f'{s:.4f}' for _, _, s in top_misses]}")

        # Sort by similarity and limit
        overlaps.sort(key=lambda x: x[2], reverse=True)
        return overlaps[:limit]

    def create_bridge_insight(
        self,
        concept_id: int,
        trace_id: int
    ) -> Optional[SynthesisResult]:
        """
        Generate bridge insight connecting concept and trace.

        Args:
            concept_id: ID of the concept
            trace_id: ID of the reasoning trace

        Returns:
            SynthesisResult for the bridge insight
        """
        if self.extractor is None:
            return None

        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Get concept
        cursor.execute("SELECT content FROM concepts WHERE id = ?", (concept_id,))
        concept_row = cursor.fetchone()
        if not concept_row:
            return None

        # Get trace
        cursor.execute("""
            SELECT query, strategy_title, strategy_content
            FROM reasoning_traces WHERE id = ?
        """, (trace_id,))
        trace_row = cursor.fetchone()
        if not trace_row:
            return None

        prompt = f"""A concept and a reasoning trace have high semantic overlap.

CONCEPT:
{concept_row[0][:500]}

REASONING TRACE:
Query: {trace_row[0]}
Strategy: {trace_row[1]}
Details: {trace_row[2] or 'N/A'}

Generate a BRIDGE INSIGHT that connects theory (concept) with practice (trace).

Output ONLY valid JSON (no markdown):
{{"title": "Bridge title", "content": "How the concept manifests in practice", "confidence": 0.0-1.0}}"""

        result = self._call_synthesis_llm(prompt)
        if result:
            return SynthesisResult(
                title=result.get('title', 'Bridge Insight'),
                content=result.get('content', ''),
                confidence=result.get('confidence', 0.5),
                source_ids=[concept_id, trace_id],
                source_type='cross'
            )

        return None

    # =========================================================================
    # Stage 5: PRUNING (Optional)
    # =========================================================================

    def mark_as_synthesized(
        self,
        source_ids: List[int],
        synthesized_id: int,
        source_type: str = 'concept'
    ) -> None:
        """
        Mark source memories as contributing to synthesis.

        This doesn't delete them but tags them for potential
        future archival/pruning.

        Args:
            source_ids: IDs of source memories
            synthesized_id: ID of the synthesized concept
            source_type: 'concept' or 'trace'
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        for source_id in source_ids:
            # Add metadata tag
            cursor.execute("""
                INSERT OR REPLACE INTO memory_metadata
                (memory_id, key, value)
                VALUES (?, 'synthesis_parent_id', ?)
            """, (source_id, str(synthesized_id)))

        conn.commit()

    # =========================================================================
    # ORCHESTRATION
    # =========================================================================

    def run_synthesis_pipeline(
        self,
        dry_run: bool = False,
        limit: int = 1000,
        concepts_only: bool = False,
        traces_only: bool = False,
        skip_cross_pollinate: bool = False,
        cross_only: bool = False,
        max_bridges: int = 100,
        concept_sample: int = 0,
        trace_sample: int = 0
    ) -> Dict[str, Any]:
        """
        Run full synthesis pipeline.

        Args:
            dry_run: If True, preview without database changes
            limit: Maximum items to process
            concepts_only: Only synthesize concepts
            traces_only: Only synthesize traces
            skip_cross_pollinate: Skip cross-pollination stage
            cross_only: Skip stages 1-3, run only cross-pollination
            max_bridges: Maximum bridge insights to create (default 100)
            concept_sample: Max concepts to sample for cross-pollination (0 = ALL)
            trace_sample: Max traces to sample for cross-pollination (0 = ALL)

        Returns:
            Dict with pipeline results and statistics
        """
        results = {
            'dry_run': dry_run,
            'concept_clusters': 0,
            'trace_clusters': 0,
            'synthesized': 0,
            'cross_pollination_pairs': 0,
            'bridge_insights': 0,
            'skipped_existing': 0,
            'errors': []
        }

        # Skip stages 1-3 if cross_only
        if not cross_only:
            # Stage 1: Clustering
            self.logger.info("Stage 1: Clustering...")

            concept_clusters = []
            trace_clusters = []

            if not traces_only:
                concept_clusters = self.find_similar_concepts(limit)
                results['concept_clusters'] = len(concept_clusters)

            if not concepts_only:
                trace_clusters = self.find_similar_traces(min(limit, 100))
                results['trace_clusters'] = len(trace_clusters)

            if dry_run:
                self.logger.info(f"[DRY RUN] Would process {len(concept_clusters)} concept clusters")
                self.logger.info(f"[DRY RUN] Would process {len(trace_clusters)} trace clusters")
                return results

            # Stage 2 & 3: Synthesize and Store
            self.logger.info("Stage 2-3: Synthesizing and storing...")

            all_clusters = concept_clusters + trace_clusters
            for cluster in all_clusters:
                try:
                    synthesis_result = self.synthesize_cluster(cluster)
                    if synthesis_result:
                        concept_id = self.store_synthesis(synthesis_result)
                        if concept_id:
                            results['synthesized'] += 1
                except Exception as e:
                    results['errors'].append(str(e))
                    self.logger.error(f"Cluster synthesis failed: {e}")

        # Stage 4: Cross-pollination
        if not skip_cross_pollinate:
            self.logger.info("Stage 4: Cross-pollinating...")
            try:
                overlaps = self.find_cross_type_overlaps(
                    limit=max_bridges * 10,  # Get more overlaps than needed to filter
                    concept_sample=concept_sample,
                    trace_sample=trace_sample
                )
                results['cross_pollination_pairs'] = len(overlaps)

                bridges_created = 0
                for i, (concept_id, trace_id, similarity) in enumerate(overlaps):
                    if bridges_created >= max_bridges:
                        break

                    # Idempotency check - skip if bridge already exists
                    if self._bridge_exists(concept_id, trace_id):
                        results['skipped_existing'] += 1
                        continue

                    bridge = self.create_bridge_insight(concept_id, trace_id)
                    if bridge:
                        bridge_id = self.store_synthesis(bridge)
                        if bridge_id:
                            bridges_created += 1
                            results['bridge_insights'] += 1

                            # Progress logging every 100 bridges
                            if bridges_created % 100 == 0:
                                self.logger.info(f"Progress: {bridges_created}/{max_bridges} bridges created")

            except Exception as e:
                results['errors'].append(f"Cross-pollination: {e}")

        self.logger.info(f"Synthesis complete: {results['synthesized']} synthesized, {results['bridge_insights']} bridges")
        if results['skipped_existing'] > 0:
            self.logger.info(f"Skipped {results['skipped_existing']} existing bridges (idempotency)")
        return results

    def get_synthesis_stats(self) -> SynthesisStats:
        """
        Get statistics about synthesis state.

        Returns:
            SynthesisStats with counts for all relevant tables
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Total concepts
        cursor.execute("SELECT COUNT(*) FROM concepts")
        total_concepts = cursor.fetchone()[0]

        # Total traces
        cursor.execute("SELECT COUNT(*) FROM reasoning_traces")
        total_traces = cursor.fetchone()[0]

        # Synthesized concepts
        cursor.execute("""
            SELECT COUNT(*) FROM concepts
            WHERE type = 'SynthesizedInsight'
        """)
        synthesized_concepts = cursor.fetchone()[0]

        # Pending clusters
        cursor.execute("""
            SELECT COUNT(*) FROM synthesis_clusters
            WHERE status = 'pending'
        """)
        pending_clusters = cursor.fetchone()[0]

        # Completed clusters
        cursor.execute("""
            SELECT COUNT(*) FROM synthesis_clusters
            WHERE status = 'synthesized'
        """)
        completed_clusters = cursor.fetchone()[0]

        # Cross-pollination links (bridge insights)
        cursor.execute("""
            SELECT COUNT(*) FROM synthesis_provenance
            WHERE source_type = 'cross'
        """)
        cross_links = cursor.fetchone()[0]

        return SynthesisStats(
            total_concepts=total_concepts,
            total_traces=total_traces,
            synthesized_concepts=synthesized_concepts,
            pending_clusters=pending_clusters,
            completed_clusters=completed_clusters,
            cross_pollination_links=cross_links
        )
