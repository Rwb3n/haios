# generated: 2025-11-27
# System Auto: last updated on: 2025-12-20 20:55:50
import json
import logging
from typing import List, Dict, Optional, Any
from .database import DatabaseManager
from .extraction import ExtractionManager

logger = logging.getLogger(__name__)

class RetrievalService:
    """
    Core retrieval service implementing Hybrid Search (Vector + Metadata).
    """
    
    def __init__(self, db_manager: DatabaseManager, extraction_manager: ExtractionManager):
        self.db = db_manager
        self.extractor = extraction_manager

    def search(
        self,
        query: str,
        space_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        top_k: int = 10,
        mode: str = 'semantic'
    ) -> List[Dict[str, Any]]:
        """
        Execute a hybrid search.

        Args:
            query: The search query string.
            space_id: Optional space ID to restrict search.
            filters: Optional metadata filters (key-value pairs).
            top_k: Number of results to return.
            mode: Retrieval mode (Session 72 - ADR-037):
                - 'semantic': Pure semantic similarity (default)
                - 'session_recovery': Excludes synthesis, for coldstart
                - 'knowledge_lookup': Filters to episteme/techne types

        Returns:
            List of memory dictionaries with scores.
        """
        logger.info(f"Searching for: '{query}' (Space: {space_id}, Filters: {filters}, Mode: {mode})")

        # 1. Generate Query Embedding
        try:
            # We use the extraction manager's underlying model or a dedicated embedding method
            # For now, assuming ExtractionManager has a method or we use the same model
            # TODO: Add explicit embed method to ExtractionManager or use a separate EmbeddingService
            # For MVP, we'll use the genai library directly if needed, or add a helper
            query_embedding = self._generate_embedding(query)
        except Exception as e:
            logger.error(f"Failed to generate embedding for query: {e}")
            return []

        # 2. Execute Vector Search via DatabaseManager
        # The DatabaseManager needs a method for vector search
        results = self.db.search_memories(
            query_vector=query_embedding,
            space_id=space_id,
            filters=filters,
            limit=top_k,
            mode=mode
        )

        return results

    def _generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for the given text using the configured model.
        """
        # This should ideally be in ExtractionManager or a dedicated EmbeddingService
        # For now, we'll delegate to ExtractionManager if it exposes it, or implement here
        return self.extractor.embed_content(text)

class ReasoningAwareRetrieval(RetrievalService):
    """
    Retrieval service with ReasoningBank-style experience learning.
    """
    
    def search_with_experience(
        self,
        query: str,
        space_id: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None,
        mode: str = 'semantic'
    ) -> Dict[str, Any]:
        """
        Search with automatic learning from past attempts.

        Args:
            query: The search query
            space_id: Optional space filter
            filters: Optional additional filters
            mode: Retrieval mode (Session 72 - ADR-037):
                - 'semantic': Pure semantic similarity (default)
                - 'session_recovery': Excludes synthesis, for coldstart
                - 'knowledge_lookup': Filters to episteme/techne types
        """
        # 1. Generate Query Embedding
        try:
            query_embedding = self._generate_embedding(query)
        except Exception as e:
            logger.error(f"Failed to generate embedding: {e}")
            return {'results': [], 'reasoning': {'outcome': 'failure', 'error': str(e)}}

        # 2. Find similar past reasoning traces
        past_attempts = self.find_similar_reasoning_traces(query_embedding, space_id)

        # 3. Learn from past experience (Strategy Selection)
        strategy = self._determine_strategy(past_attempts)

        # 4. Execute search with learned strategy
        import time
        start_time = time.time()

        # Apply strategy adjustments (e.g., modifying filters or query)
        # For MVP, we just use the base search, but strategy could imply different parameters
        # TODO: Apply strategy.parameters to filters/query

        results = self.search(query, space_id, filters, mode=mode)
        
        execution_time = int((time.time() - start_time) * 1000)
        
        # 5. Evaluate outcome
        outcome = 'success' if results and len(results) > 0 else 'failure'

        # 6. Prepare context for strategy extraction
        results_summary = ""
        error_details = ""
        if outcome == 'success':
            results_summary = f"Found {len(results)} results. Top result IDs: {[r.get('id') for r in results[:3]]}"
        else:
            error_details = "No matching memories found for query"

        # 7. Record this reasoning attempt (with strategy extraction)
        self.record_reasoning_trace(
            query=query,
            query_embedding=query_embedding,
            approach=strategy['description'],
            strategy_details=strategy['parameters'],
            outcome=outcome,
            memories_used=[m['id'] for m in results],
            execution_time_ms=execution_time,
            space_id=space_id,
            results_summary=results_summary,
            error_details=error_details
        )

        # 8. Build relevant_strategies from past attempts (for prompt injection)
        relevant_strategies = []
        for t in past_attempts[:3]:
            if t.get('strategy_content'):
                relevant_strategies.append({
                    'title': t.get('strategy_title', t.get('approach_taken')),
                    'content': t.get('strategy_content')
                })

        return {
            'results': results,
            'reasoning': {
                'strategy_used': strategy['description'],
                'learned_from': len(past_attempts),
                'outcome': outcome,
                'execution_time_ms': execution_time,
                # NEW: For system prompt injection (ReasoningBank alignment)
                'relevant_strategies': relevant_strategies
            }
        }

    def find_similar_reasoning_traces(
        self,
        query_embedding: List[float],
        space_id: Optional[str] = None,
        threshold: float = 0.6
    ) -> List[Dict[str, Any]]:
        """
        Find past reasoning attempts for similar queries using vector similarity.

        Design Decision DD-002: Uses direct vec_distance_cosine() on column for MVP.
        Switch to vec0 indexed search when traces exceed 10k rows.

        Design Decision DD-003: Threshold lowered to 0.6 (from 0.8) per Session 30
        gap analysis. Original 0.8 was too strict for experiential learning.
        Converted to cosine distance internally (max_distance = 1 - threshold).

        Note: Embedding APIs may produce slightly different vectors for identical
        queries across calls. Threshold of 0.6 allows broader strategy retrieval
        while still maintaining relevance.
        """
        import struct

        conn = self.db.get_connection()
        cursor = conn.cursor()

        # Check if reasoning_traces table has any rows with embeddings
        cursor.execute("SELECT COUNT(*) FROM reasoning_traces WHERE query_embedding IS NOT NULL")
        count = cursor.fetchone()[0]
        if count == 0:
            return []

        # Pack embedding for sqlite-vec
        vector_bytes = struct.pack(f'{len(query_embedding)}f', *query_embedding)

        # Build query - DD-002: direct column search for MVP
        # Updated to include strategy columns per ReasoningBank alignment
        sql = """
            SELECT
                rt.id,
                rt.query,
                rt.approach_taken,
                rt.strategy_details,
                rt.outcome,
                rt.failure_reason,
                rt.memories_used,
                rt.execution_time_ms,
                vec_distance_cosine(rt.query_embedding, ?) as distance,
                rt.strategy_title,
                rt.strategy_description,
                rt.strategy_content
            FROM reasoning_traces rt
            WHERE rt.query_embedding IS NOT NULL
        """

        params = [vector_bytes]

        if space_id:
            sql += " AND rt.space_id = ?"
            params.append(space_id)

        sql += " ORDER BY distance ASC LIMIT 10"

        try:
            cursor.execute(sql, params)
            rows = cursor.fetchall()
        except Exception as e:
            logger.warning(f"Vector search on reasoning_traces failed: {e}")
            return []

        # DD-003: Convert similarity threshold to distance
        # Cosine distance: 0 = identical, 2 = opposite
        # Similarity 0.8 -> max distance 0.2
        max_distance = 1 - threshold

        results = []
        for row in rows:
            distance = row[8]
            if distance is not None and distance <= max_distance:
                results.append({
                    'id': row[0],
                    'query': row[1],
                    'approach_taken': row[2],
                    'strategy_details': row[3],
                    'outcome': row[4],
                    'failure_reason': row[5],
                    'memories_used': row[6],
                    'execution_time_ms': row[7],
                    'distance': distance,
                    # Strategy columns (ReasoningBank alignment)
                    'strategy_title': row[9],
                    'strategy_description': row[10],
                    'strategy_content': row[11]
                })

        return results

    def _determine_strategy(self, past_attempts: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Determine the best strategy based on past attempts."""
        if not past_attempts:
            return {'description': 'default_hybrid', 'parameters': {}}
            
        # Simple logic: if any success, reuse it.
        successful = [t for t in past_attempts if t.get('outcome') == 'success']
        if successful:
            return {
                'description': successful[0]['approach_taken'], 
                'parameters': json.loads(successful[0].get('strategy_details', '{}'))
            }
            
        return {'description': 'default_hybrid', 'parameters': {}}

    def record_reasoning_trace(
        self,
        query: str,
        query_embedding: List[float],
        approach: str,
        strategy_details: Dict,
        outcome: str,
        memories_used: List[int],
        execution_time_ms: int,
        space_id: Optional[str],
        results_summary: str = "",
        error_details: str = ""
    ):
        """
        Record reasoning attempt WITH strategy extraction.

        Per ReasoningBank paper: extracts WHAT WAS LEARNED, not just what happened.
        Uses LLM to distill transferable strategies from success/failure.
        """
        # Extract strategy using LLM (ReasoningBank paper alignment)
        strategy = self.extractor.extract_strategy(
            query=query,
            approach=approach,
            outcome=outcome,
            results_summary=results_summary,
            error_details=error_details
        )

        conn = self.db.get_connection()
        cursor = conn.cursor()

        import struct
        vector_bytes = struct.pack(f'{len(query_embedding)}f', *query_embedding)

        # E2-103: Compute failure_reason for failure/partial_success outcomes
        failure_reason = None
        if outcome in ('failure', 'partial_success') and error_details:
            failure_reason = error_details

        cursor.execute("""
            INSERT INTO reasoning_traces
            (query, query_embedding, approach_taken, strategy_details, outcome,
             memories_used, execution_time_ms, space_id,
             strategy_title, strategy_description, strategy_content, extraction_model,
             failure_reason)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            query,
            vector_bytes,
            approach,
            json.dumps(strategy_details),
            outcome,
            json.dumps(memories_used),
            execution_time_ms,
            space_id,
            strategy.get('title'),
            strategy.get('description'),
            strategy.get('content'),
            self.extractor.model_id,
            failure_reason
        ))
        conn.commit()

        logger.info(f"Recorded trace with strategy: {strategy.get('title')}")

