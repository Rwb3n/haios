# generated: 2026-01-03
# System Auto: last updated on: 2026-01-21T20:31:48
"""
MemoryBridge Module (E2-241)

Stateless wrapper for haios-memory MCP server. Provides:
- Query with mode support (semantic, session_recovery, knowledge_lookup)
- Store with auto-classification
- Auto-link for work item memory refs

L4 Invariants:
- MUST handle MCP timeout gracefully (retry once, then warn)
- MUST parse work_id from source_path for auto-linking
- MUST NOT block on MCP failure (degrade gracefully)

Usage:
    from memory_bridge import MemoryBridge, QueryResult

    bridge = MemoryBridge()
    result = bridge.query("implementation patterns", mode="knowledge_lookup")
    if result.concepts:
        print(f"Found {len(result.concepts)} concepts")
"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import logging
import os
import re

try:
    import google.generativeai as genai
except ImportError:
    genai = None  # Optional dependency for query rewriting

logger = logging.getLogger(__name__)


@dataclass
class QueryResult:
    """Result of a memory query."""

    concepts: List[Dict[str, Any]] = field(default_factory=list)
    reasoning: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StoreResult:
    """Result of a memory store operation."""

    concept_ids: List[int] = field(default_factory=list)
    classification: str = ""
    error: Optional[str] = None


@dataclass
class LearningExtractionResult:
    """Result of learning extraction operation (E2-262)."""

    success: bool
    reason: str  # qualified, too_short, no_tool_usage, trivial_query, error
    outcome: Optional[str] = None  # success, partial_success, failure
    initial_query: Optional[str] = None
    tools_used: Optional[List[str]] = None
    error: Optional[str] = None


class MemoryBridge:
    """
    Stateless memory abstraction module.

    Wraps haios-memory MCP tools with typed interfaces, timeout handling,
    and auto-linking for work item integration.
    """

    VALID_MODES = {"semantic", "session_recovery", "knowledge_lookup"}
    DEFAULT_TIMEOUT_MS = 5000
    MAX_RETRIES = 1
    REWRITE_MIN_LENGTH = 10  # Queries shorter than this skip rewriting

    def __init__(
        self,
        work_engine_callback: Optional[Callable] = None,
        db_path: Optional[Path] = None,
        api_key: Optional[str] = None,
        enable_rewriting: bool = True,
    ):
        """
        Initialize MemoryBridge.

        Args:
            work_engine_callback: Optional callback to update work items.
                                  Signature: callback(work_id: str, memory_refs: List[int])
            db_path: Path to haios_memory.db (default: project_root/haios_memory.db)
            api_key: Google API key for embeddings/rewriting (default: GOOGLE_API_KEY env)
            enable_rewriting: Whether to rewrite queries for better retrieval (default: True)
        """
        self._work_engine_callback = work_engine_callback
        self._handlers: Dict[str, Any] = {}  # For statelessness verification

        # E2-253: Configuration for haios_etl integration
        if db_path is None:
            # Default to project root
            project_root = Path(__file__).parent.parent.parent.parent
            db_path = project_root / "haios_memory.db"
        self._db_path = db_path
        self._api_key = api_key or os.environ.get("GOOGLE_API_KEY")
        self._enable_rewriting = enable_rewriting

    def query(
        self, query: str, mode: str = "semantic", space_id: Optional[str] = None
    ) -> QueryResult:
        """
        Query memory with mode support and graceful degradation.

        Args:
            query: Search query string
            mode: Retrieval mode (semantic, session_recovery, knowledge_lookup)
            space_id: Optional space filter

        Returns:
            QueryResult with concepts and reasoning trace
        """
        if mode not in self.VALID_MODES:
            logger.warning(f"Invalid mode '{mode}', defaulting to 'semantic'")
            mode = "semantic"

        # E2-253: Apply query rewriting if enabled
        if self._enable_rewriting:
            query = self._rewrite_query(query)

        try:
            result = self._call_mcp_with_retry(
                "memory_search_with_experience",
                {"query": query, "mode": mode, "space_id": space_id},
            )
            return QueryResult(
                concepts=result.get("results", []),
                reasoning=result.get("reasoning", {}),
            )
        except Exception as e:
            logger.warning(f"Memory query failed (degraded): {e}")
            return QueryResult(concepts=[], reasoning={"error": str(e), "degraded": True})

    def store(
        self, content: str, source_path: str, content_type_hint: str = "unknown"
    ) -> StoreResult:
        """
        Store content with auto-classification.

        Args:
            content: Content to store
            source_path: Source file path for provenance
            content_type_hint: Classification hint (episteme, techne, doxa, unknown)

        Returns:
            StoreResult with concept IDs and classification
        """
        try:
            result = self._call_mcp_with_retry(
                "ingester_ingest",
                {
                    "content": content,
                    "source_path": source_path,
                    "content_type_hint": content_type_hint,
                },
            )

            store_result = StoreResult(
                concept_ids=result.get("concept_ids", []),
                classification=result.get("classification", "unknown"),
            )

            # Auto-link if work_id can be parsed
            work_id = self._parse_work_id(source_path)
            if work_id and store_result.concept_ids:
                self.auto_link(work_id, store_result.concept_ids)

            return store_result
        except Exception as e:
            logger.warning(f"Memory store failed: {e}")
            return StoreResult(error=str(e))

    def auto_link(self, work_id: str, concept_ids: List[int]) -> None:
        """
        Add memory_refs to work item frontmatter.

        Args:
            work_id: Work item ID (e.g., "E2-241")
            concept_ids: List of concept IDs to link
        """
        if self._work_engine_callback:
            try:
                self._work_engine_callback(work_id, concept_ids)
                logger.info(f"Auto-linked {len(concept_ids)} concepts to {work_id}")
            except Exception as e:
                logger.warning(f"Auto-link failed for {work_id}: {e}")

    def _parse_work_id(self, source_path: str) -> Optional[str]:
        """
        Extract work ID from source path.

        Pattern: docs/work/active/E2-241/... or docs/work/archive/INV-023/...
        """
        # Primary pattern: full work path
        match = re.search(r"docs/work/(?:active|archive)/([A-Z]+-\d+)", source_path)
        if match:
            return match.group(1)

        # Fallback: bare work ID patterns
        for pattern in [r"E2-\d+", r"INV-\d+", r"TD-\d+"]:
            match = re.search(pattern, source_path)
            if match:
                return match.group(0)

        return None

    def _call_mcp_with_retry(
        self, tool_name: str, params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Call MCP tool with retry on timeout.

        L4 Invariant: Retry once, then degrade gracefully.
        """
        last_error = None
        for attempt in range(self.MAX_RETRIES + 1):
            try:
                return self._call_mcp(tool_name, params)
            except TimeoutError as e:
                last_error = e
                if attempt < self.MAX_RETRIES:
                    logger.info(
                        f"Retrying {tool_name} after timeout (attempt {attempt + 1})"
                    )
        raise last_error or TimeoutError("MCP call failed")

    def _call_mcp(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute memory operation by wrapping haios_etl modules.

        E2-253: Dispatches to appropriate handler based on tool name.
        Maps MCP tool names to haios_etl function calls:
        - memory_search_with_experience -> ReasoningAwareRetrieval.search_with_experience()
        - ingester_ingest -> Store via ingester module
        """
        if tool_name == "memory_search_with_experience":
            return self._search_with_experience(params)
        elif tool_name == "ingester_ingest":
            return self._ingest(params)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    def _search_with_experience(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute search via ReasoningAwareRetrieval.

        E2-253: Wraps haios_etl.retrieval with optional query rewriting.
        """
        import sys

        # Add project root for haios_etl imports
        project_root = Path(__file__).parent.parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from haios_etl.database import DatabaseManager
        from haios_etl.extraction import ExtractionManager
        from haios_etl.retrieval import ReasoningAwareRetrieval

        db = DatabaseManager(str(self._db_path))
        extractor = ExtractionManager(self._api_key)
        retrieval = ReasoningAwareRetrieval(db, extractor)

        # Note: Query rewriting is applied in query() before calling this method
        query = params.get("query", "")

        result = retrieval.search_with_experience(
            query=query,
            space_id=params.get("space_id"),
            mode=params.get("mode", "semantic"),
        )
        return result

    def _ingest(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute ingest operation via ingester module.

        E2-253: Wraps haios_etl for content storage.
        """
        import sys

        project_root = Path(__file__).parent.parent.parent.parent
        if str(project_root) not in sys.path:
            sys.path.insert(0, str(project_root))

        from haios_etl.database import DatabaseManager
        from haios_etl.extraction import ExtractionManager
        from haios_etl.ingester import Ingester

        db = DatabaseManager(str(self._db_path))
        extractor = ExtractionManager(self._api_key)
        ingester = Ingester(db, extractor)

        content = params.get("content", "")
        source_path = params.get("source_path", "")
        content_type_hint = params.get("content_type_hint", "unknown")

        # Store content and return result
        result = ingester.ingest_content(content, source_path, content_type_hint)
        return {
            "concept_ids": result.get("concept_ids", []),
            "classification": result.get("classification", "unknown"),
            "entity_ids": result.get("entity_ids", []),
        }

    def _rewrite_query(self, query: str) -> str:
        """
        Rewrite conversational query for better retrieval (E2-063).

        Uses Gemini to transform casual queries into technical, retrieval-optimized
        queries that map better to stored codebase content.
        """
        if len(query) < self.REWRITE_MIN_LENGTH:
            return query

        if genai is None:
            logger.warning("google.generativeai not available, skipping rewrite")
            return query

        try:
            if not self._api_key:
                logger.warning("No API key for query rewriting, using original query")
                return query

            genai.configure(api_key=self._api_key)
            model = genai.GenerativeModel("gemini-2.5-flash-lite")

            prompt = f"""Rewrite this conversational query for semantic search in a technical codebase.
Domain: HAIOS - AI agent orchestration system with concepts like coldstart, checkpoints, memory retrieval, governance hooks, ADRs, backlog items, synthesis.
Remove conversational fluff, expand implicit references, use domain vocabulary.
Return ONLY the rewritten query, no explanation.

Query: {query}"""

            response = model.generate_content(prompt)
            rewritten = response.text.strip()
            logger.info(f"Query rewrite: '{query}' -> '{rewritten}'")
            return rewritten

        except Exception as e:
            logger.warning(f"Query rewrite failed: {e}, using original query")
            return query

    # =========================================================================
    # E2-261: Error Capture
    # =========================================================================

    def is_actual_error(self, tool_name: str, tool_response: dict) -> bool:
        """
        Determine if tool response represents an actual failure.

        Delegates to lib/error_capture.is_actual_error().

        Args:
            tool_name: Name of the tool (Bash, Read, Edit, Write, Grep, Glob)
            tool_response: The tool's response dict from Claude Code

        Returns:
            True only for actual failures, False for successes or false positives.
        """
        # WORK-006: Use lib inside haios/ for portability
        import sys
        lib_path = str(Path(__file__).parent.parent / "lib")  # .claude/haios/lib (sibling to modules/)
        if lib_path not in sys.path:
            sys.path.insert(0, lib_path)

        from error_capture import is_actual_error as _is_actual_error
        return _is_actual_error(tool_name, tool_response)

    def capture_error(self, tool_name: str, error_message: str, tool_input: str = "") -> dict:
        """
        Store error to memory with dedicated type for queryability.

        Delegates to lib/error_capture.store_error().

        Args:
            tool_name: Tool that failed
            error_message: The error message
            tool_input: Summary of what was attempted (optional)

        Returns:
            {"success": True, "concept_id": N} or {"success": False, "error": "..."}
        """
        # WORK-006: Use lib inside haios/ for portability
        import sys
        lib_path = str(Path(__file__).parent.parent / "lib")  # .claude/haios/lib (sibling to modules/)
        if lib_path not in sys.path:
            sys.path.insert(0, lib_path)

        from error_capture import store_error
        return store_error(tool_name, error_message, tool_input)

    # =========================================================================
    # E2-262: Learning Extraction
    # =========================================================================

    def extract_learnings(self, transcript_path: str) -> LearningExtractionResult:
        """
        Extract learnings from session transcript.

        Delegates to hooks/reasoning_extraction.py for transcript parsing
        and learning storage.

        Args:
            transcript_path: Path to session transcript JSONL file

        Returns:
            LearningExtractionResult with extraction status and details
        """
        import os
        import sys

        if not os.path.exists(transcript_path):
            return LearningExtractionResult(
                success=False,
                reason="error",
                error=f"Transcript not found: {transcript_path}"
            )

        # Add hooks directory to path for reasoning_extraction import
        hooks_path = str(Path(__file__).parent.parent.parent / "hooks")
        if hooks_path not in sys.path:
            sys.path.insert(0, hooks_path)

        try:
            from reasoning_extraction import (
                parse_transcript,
                should_extract,
                determine_outcome,
                extract_and_store,
                load_env
            )

            # Load environment for API keys
            load_env()

            # Parse transcript
            session_info = parse_transcript(transcript_path)
            if not session_info:
                return LearningExtractionResult(
                    success=False,
                    reason="error",
                    error="Failed to parse transcript"
                )

            # Check if extraction is warranted
            should, reason = should_extract(session_info)
            if not should:
                return LearningExtractionResult(
                    success=False,
                    reason=reason,
                    initial_query=session_info.get("initial_query"),
                    tools_used=session_info.get("tools_used")
                )

            # Determine outcome and extract
            outcome = determine_outcome(session_info)
            extraction_success = extract_and_store(session_info)

            return LearningExtractionResult(
                success=extraction_success,
                reason="qualified" if extraction_success else "error",
                outcome=outcome,
                initial_query=session_info.get("initial_query"),
                tools_used=session_info.get("tools_used"),
                error=None if extraction_success else "Extraction failed"
            )

        except Exception as e:
            return LearningExtractionResult(
                success=False,
                reason="error",
                error=str(e)
            )
