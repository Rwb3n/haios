# generated: 2025-12-01
# System Auto: last updated on: 2025-12-13 15:55:52
"""
Ingester Agent - The "Mouth" of HAIOS

Classifies and stores content in memory using the Greek Triad taxonomy.
Implements DD-015 (single-item), DD-016 (retry), DD-017 (provenance), DD-019 (timeout).

Reference: docs/plans/PLAN-AGENT-ECOSYSTEM-001.md
           docs/handoff/2025-12-01-VALIDATION-interpreter-ingester-implementation.md
"""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import logging
import time
import re
import os

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Classification of ingestion errors (DD-016)."""
    RETRYABLE = "retryable"     # rate limit, timeout, connection
    PERMANENT = "permanent"     # malformed, invalid, not found
    UNKNOWN = "unknown"


class IngestionError(Exception):
    """Custom exception for ingestion failures."""
    def __init__(self, message: str, error_type: ErrorType = ErrorType.UNKNOWN):
        super().__init__(message)
        self.error_type = error_type


@dataclass
class IngesterConfig:
    """Configuration for Ingester agent (DD-016, DD-019)."""
    timeout_seconds: int = 30           # DD-019: 30 second timeout
    max_retries: int = 3                # DD-016: 3 retries
    backoff_base: float = 2.0           # DD-016: exponential backoff (2s, 4s, 8s)
    model_id: str = "gemini-2.5-flash-lite"


@dataclass
class IngestionResult:
    """Result of ingesting content into memory (DD-017)."""
    concept_ids: List[int]          # IDs of stored concepts
    entity_ids: List[int]           # IDs of stored entities
    classification: str             # episteme, techne, doxa
    ingested_by_agent: str          # DD-017: Agent ID for provenance


# Valid content types (Greek Triad)
VALID_CONTENT_TYPES = {"episteme", "techne", "doxa"}


class Ingester:
    """
    Ingester Agent - Classifies and stores content in memory.

    Design Decisions:
        DD-015: Single-item ingestion (no batching in MVP)
        DD-016: 3 retries with exponential backoff (2s, 4s, 8s)
        DD-017: Include agent ID in provenance
        DD-019: 30 second timeout
    """

    AGENT_ID = "ingester-v1"

    # Patterns for auto-classification
    CLASSIFICATION_PATTERNS = {
        'episteme': [
            r'\b(is|are|was|were|will be)\b.*\b(fact|true|truth|definition)\b',
            r'\b(according to|defined as|known as|means that)\b',
            r'\b(architecture|system|protocol|specification)\b',
        ],
        'techne': [
            r'\b(step \d|how to|to do|guide|procedure|install|setup|configure)\b',
            r'\b(run|execute|implement|build|deploy)\b.*\b(command|script|code)\b',
            r'\b(first|then|next|finally|after)\b.*\b(do|run|execute)\b',
        ],
        'doxa': [
            r'\b(i think|i believe|in my opinion|seems like|probably)\b',
            r'\b(should|could|might|may)\b.*\b(better|best|prefer)\b',
            r'\b(recommend|suggest|propose)\b',
        ],
    }

    def __init__(
        self,
        db_manager=None,
        config: Optional[IngesterConfig] = None,
        api_key: Optional[str] = None,
        extractor=None  # E2-FIX-002: ExtractionManager for embeddings
    ):
        self.db_manager = db_manager
        self.config = config or IngesterConfig()
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.extractor = extractor  # E2-FIX-002: Optional extractor for embedding generation

    def ingest(
        self,
        content: str,
        source_path: str,
        content_type_hint: str = "unknown"
    ) -> IngestionResult:
        """
        Ingest content into memory with classification.

        Args:
            content: The text content to ingest
            source_path: Source file path for provenance
            content_type_hint: Classification hint (episteme, techne, doxa, unknown)

        Returns:
            IngestionResult with stored IDs and classification

        Raises:
            IngestionError: If ingestion fails after retries
        """
        # Validate input
        if not content or not content.strip():
            raise IngestionError(
                "Content cannot be empty",
                ErrorType.PERMANENT
            )

        # Validate content type
        if content_type_hint != "unknown" and content_type_hint not in VALID_CONTENT_TYPES:
            raise IngestionError(
                f"Invalid content_type_hint '{content_type_hint}'. Must be one of: {', '.join(VALID_CONTENT_TYPES)} or 'unknown'",
                ErrorType.PERMANENT
            )

        # Step 1: Classify if hint is "unknown"
        if content_type_hint == "unknown":
            classification = self._classify_content(content)
        else:
            classification = content_type_hint

        # Step 2: Extract entities/concepts (with retry logic)
        extraction_result = self._extract_with_retry(content, source_path)

        # Step 3: Store in memory
        entity_ids = []
        concept_ids = []

        if self.db_manager:
            # Store entities
            for entity in extraction_result.get("entities", []):
                try:
                    entity_id = self.db_manager.insert_entity(
                        type=entity.get("type", "Unknown"),
                        value=entity.get("value", "")
                    )
                    entity_ids.append(entity_id)
                except Exception as e:
                    logger.warning(f"Failed to store entity: {e}")

            # Store concepts
            for concept in extraction_result.get("concepts", []):
                try:
                    concept_id = self.db_manager.insert_concept(
                        type=concept.get("type", classification),
                        name=concept.get("content", "")[:100],
                        description=concept.get("content", "")
                    )
                    concept_ids.append(concept_id)

                    # E2-FIX-002: Generate embedding for semantic search
                    # Without embedding, ingested concepts are invisible to retrieval
                    if self.extractor:
                        try:
                            content = concept.get("content", "")[:8000]
                            embedding = self.extractor.embed_content(content)
                            if embedding:
                                self.db_manager.insert_concept_embedding(
                                    concept_id=concept_id,
                                    vector=embedding,
                                    model="text-embedding-004",
                                    dimensions=len(embedding)
                                )
                        except Exception as embed_err:
                            logger.warning(f"Failed to generate embedding for concept {concept_id}: {embed_err}")
                            # Continue without embedding - can be backfilled later

                except Exception as e:
                    logger.warning(f"Failed to store concept: {e}")

        # Step 4: Return result with provenance (DD-017)
        return IngestionResult(
            concept_ids=concept_ids,
            entity_ids=entity_ids,
            classification=classification,
            ingested_by_agent=self.AGENT_ID
        )

    def _classify_content(self, content: str) -> str:
        """
        Auto-classify content using Greek Triad taxonomy.

        Args:
            content: The content to classify

        Returns:
            Classification: episteme, techne, or doxa
        """
        content_lower = content.lower()
        scores = {k: 0 for k in VALID_CONTENT_TYPES}

        # Score based on pattern matches
        for classification, patterns in self.CLASSIFICATION_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, content_lower, re.IGNORECASE):
                    scores[classification] += 1

        # Return highest scoring, default to episteme
        best = max(scores, key=scores.get)
        if scores[best] == 0:
            return "episteme"  # Default to knowledge/facts
        return best

    def _extract_with_retry(
        self,
        content: str,
        source_path: str
    ) -> Dict[str, Any]:
        """
        Extract content with retry logic (DD-016).

        Args:
            content: Content to extract from
            source_path: Source file path

        Returns:
            Extraction result dict

        Raises:
            IngestionError: After max retries exhausted
        """
        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                return self._extract_content(content, source_path)
            except Exception as e:
                last_error = e
                error_type = self._classify_error(e)

                if error_type == ErrorType.PERMANENT:
                    raise IngestionError(str(e), error_type)

                if attempt < self.config.max_retries - 1:
                    # Exponential backoff (DD-016: 2s, 4s, 8s)
                    sleep_time = self.config.backoff_base ** (attempt + 1)
                    logger.warning(
                        f"Extraction failed (attempt {attempt + 1}/{self.config.max_retries}), "
                        f"retrying in {sleep_time}s: {e}"
                    )
                    time.sleep(sleep_time)

        raise IngestionError(
            f"Extraction failed after {self.config.max_retries} retries: {last_error}",
            ErrorType.RETRYABLE
        )

    def _classify_error(self, error: Exception) -> ErrorType:
        """
        Classify an error for retry logic (DD-016).

        Args:
            error: The exception to classify

        Returns:
            ErrorType classification
        """
        error_str = str(error).lower()

        # Permanent errors (no retry)
        permanent_patterns = [
            "invalid", "malformed", "not found", "401", "403", "400",
            "empty", "format"
        ]
        for pattern in permanent_patterns:
            if pattern in error_str:
                return ErrorType.PERMANENT

        # Retryable errors
        retryable_patterns = [
            "rate limit", "429", "timeout", "connection", "503", "502",
            "500", "unavailable", "temporarily"
        ]
        for pattern in retryable_patterns:
            if pattern in error_str:
                return ErrorType.RETRYABLE

        return ErrorType.UNKNOWN

    def _extract_content(
        self,
        content: str,
        source_path: str
    ) -> Dict[str, Any]:
        """
        Extract entities and concepts from content.

        Args:
            content: The content to extract from
            source_path: Source file path for context

        Returns:
            Dict with "entities" and "concepts" lists
        """
        try:
            from ..extraction import ExtractionManager

            extraction_manager = ExtractionManager(api_key=self.api_key or "dummy")
            result = extraction_manager.extract_from_file(source_path, content)

            return {
                "entities": [
                    {"type": e.type, "value": e.value}
                    for e in result.entities
                ],
                "concepts": [
                    {"type": c.type, "content": c.content, "source_adr": c.source_adr}
                    for c in result.concepts
                ]
            }
        except Exception as e:
            logger.error(f"Extraction failed: {e}")
            raise
