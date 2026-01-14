# generated: 2025-12-02
# System Auto: last updated on: 2025-12-02 22:45:13
"""
Collaboration Protocol - Agent-to-Agent Handoffs

Implements the collaboration handoff schema for HAIOS agent ecosystem.
Enables structured handoffs between agents (e.g., Interpreter -> Ingester).

Design Decisions:
    DD-018: Synchronous handoff for MVP
    DD-020: Hybrid architecture (Python modules + MCP wrappers)

Reference: docs/specs/collaboration_handoff_schema.md
"""
from dataclasses import dataclass, field, asdict
from typing import Dict, Any, Optional, Callable
from enum import Enum
from datetime import datetime
import uuid
import logging
import time
import hashlib

logger = logging.getLogger(__name__)


class HandoffStatus(Enum):
    """Status of a collaboration handoff."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    FAILED = "failed"
    TIMEOUT = "timeout"


class ResultStatus(Enum):
    """Status of a collaboration result."""
    SUCCESS = "success"
    PARTIAL = "partial"
    ERROR = "error"


@dataclass
class HandoffPayload:
    """Payload for a collaboration handoff."""
    directive: Dict[str, Any]
    context: Optional[Dict[str, Any]] = None
    original_input: Optional[str] = None


@dataclass
class CollaborationHandoff:
    """
    A handoff request from one agent to another.

    Attributes:
        from_agent: Source agent ID
        to_agent: Target agent ID
        payload: The task payload
        handoff_id: Unique identifier (auto-generated)
        created_at: Creation timestamp
        timeout_ms: Timeout in milliseconds (default 30000)
        status: Current handoff status
        expected_output_schema: Optional schema for validation
    """
    from_agent: str
    to_agent: str
    payload: HandoffPayload
    handoff_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=datetime.utcnow)
    timeout_ms: int = 30000
    status: HandoffStatus = HandoffStatus.PENDING
    expected_output_schema: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "handoff_id": self.handoff_id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "payload": {
                "directive": self.payload.directive,
                "context": self.payload.context,
                "original_input": self.payload.original_input,
            },
            "created_at": self.created_at.isoformat(),
            "timeout_ms": self.timeout_ms,
            "status": self.status.value,
            "expected_output_schema": self.expected_output_schema,
        }


@dataclass
class CollaborationResult:
    """
    Result of a collaboration handoff execution.

    Attributes:
        handoff_id: References the original handoff
        executed_by: Agent that executed the task
        status: Result status (success, partial, error)
        result: The result payload
        executed_at: Execution timestamp
        error: Error details if failed
    """
    handoff_id: str
    executed_by: str
    status: ResultStatus
    result: Dict[str, Any]
    executed_at: datetime = field(default_factory=datetime.utcnow)
    error: Optional[Dict[str, Any]] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "handoff_id": self.handoff_id,
            "executed_by": self.executed_by,
            "status": self.status.value,
            "result": self.result,
            "executed_at": self.executed_at.isoformat(),
            "error": self.error,
        }


class CollaborationError(Exception):
    """Exception raised during collaboration."""
    def __init__(self, message: str, handoff_id: str, error_type: str = "unknown"):
        super().__init__(message)
        self.handoff_id = handoff_id
        self.error_type = error_type


# Registry of agent handlers
_AGENT_HANDLERS: Dict[str, Callable[[CollaborationHandoff], CollaborationResult]] = {}


def register_handler(agent_id: str, handler: Callable[[CollaborationHandoff], CollaborationResult]):
    """Register a handler for an agent."""
    _AGENT_HANDLERS[agent_id] = handler
    logger.info(f"Registered collaboration handler for {agent_id}")


def get_handler(agent_id: str) -> Optional[Callable[[CollaborationHandoff], CollaborationResult]]:
    """Get the registered handler for an agent."""
    return _AGENT_HANDLERS.get(agent_id)


class Collaborator:
    """
    Manages collaboration handoffs between agents.

    This is the central coordinator for agent-to-agent communication.
    For MVP (DD-018), handoffs are synchronous.
    """

    def __init__(self, db_manager=None, api_key: Optional[str] = None):
        """
        Initialize the Collaborator.

        Args:
            db_manager: Database manager for persistence
            api_key: API key for LLM operations
        """
        self.db_manager = db_manager
        self.api_key = api_key
        self._register_default_handlers()

    def _register_default_handlers(self):
        """Register default handlers for known agents."""
        # Register ingester handler if not already registered
        if "ingester-v1" not in _AGENT_HANDLERS:
            register_handler("ingester-v1", self._handle_ingester)

    def _handle_ingester(self, handoff: CollaborationHandoff) -> CollaborationResult:
        """
        Default handler for ingester-v1.

        Args:
            handoff: The collaboration handoff

        Returns:
            CollaborationResult with ingestion outcome
        """
        from .ingester import Ingester, IngesterConfig

        try:
            ingester = Ingester(
                db_manager=self.db_manager,
                config=IngesterConfig(),
                api_key=self.api_key
            )

            # Extract parameters from directive
            directive = handoff.payload.directive
            content = directive.get("content", "")
            source_path = directive.get("source_path", f"handoff:{handoff.handoff_id}")
            content_type = directive.get("type", "unknown")

            # If content is empty, check original_input
            if not content and handoff.payload.original_input:
                content = handoff.payload.original_input

            # Execute ingestion
            result = ingester.ingest(content, source_path, content_type)

            # GAP-A5 FIX: Create artifact and link entities/concepts
            # This enables memory_search_with_experience to find ingested content
            artifact_id = None
            if self.db_manager and source_path:
                try:
                    # Create content hash for artifact tracking
                    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()

                    # Insert or update artifact
                    artifact_id = self.db_manager.insert_artifact(
                        file_path=source_path,
                        file_hash=content_hash,
                        size_bytes=len(content.encode('utf-8'))
                    )

                    # Link entities to artifact
                    for entity_id in result.entity_ids:
                        self.db_manager.record_entity_occurrence(
                            entity_id=entity_id,
                            artifact_id=artifact_id,
                            context=content[:200]  # First 200 chars as context
                        )

                    # Link concepts to artifact
                    for concept_id in result.concept_ids:
                        self.db_manager.record_concept_occurrence(
                            concept_id=concept_id,
                            artifact_id=artifact_id,
                            context=content[:200]  # First 200 chars as context
                        )

                    logger.info(f"Created artifact {artifact_id} for {source_path}")

                    # Generate embedding for semantic search
                    try:
                        from haios_etl.extraction import ExtractionManager
                        extractor = ExtractionManager(self.api_key)
                        embedding = extractor.embed_content(content[:8000])  # Limit for API
                        if embedding:
                            self.db_manager.insert_embedding(
                                artifact_id=artifact_id,
                                vector=embedding,
                                model="text-embedding-004",
                                dimensions=len(embedding)
                            )
                            logger.info(f"Generated embedding for artifact {artifact_id}")
                    except Exception as embed_err:
                        logger.warning(f"Failed to generate embedding: {embed_err}")
                        # Continue without embedding - batch job can fix later

                except Exception as e:
                    logger.warning(f"Failed to create artifact for {source_path}: {e}")
                    # Don't fail the whole ingestion if artifact creation fails

            return CollaborationResult(
                handoff_id=handoff.handoff_id,
                executed_by="ingester-v1",
                status=ResultStatus.SUCCESS,
                result={
                    "concept_ids": result.concept_ids,
                    "entity_ids": result.entity_ids,
                    "classification": result.classification,
                    "ingested_by_agent": result.ingested_by_agent,
                    "artifact_id": artifact_id,  # Include artifact ID in result
                }
            )

        except Exception as e:
            logger.error(f"Ingester handler failed: {e}")
            return CollaborationResult(
                handoff_id=handoff.handoff_id,
                executed_by="ingester-v1",
                status=ResultStatus.ERROR,
                result={},
                error={"message": str(e), "error_type": "permanent"}
            )

    def create_handoff(
        self,
        from_agent: str,
        to_agent: str,
        directive: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
        original_input: Optional[str] = None,
        timeout_ms: int = 30000
    ) -> CollaborationHandoff:
        """
        Create a new collaboration handoff.

        Args:
            from_agent: Source agent ID
            to_agent: Target agent ID
            directive: The task directive
            context: Optional context from source agent
            original_input: Original input that triggered this chain
            timeout_ms: Timeout in milliseconds

        Returns:
            CollaborationHandoff instance
        """
        payload = HandoffPayload(
            directive=directive,
            context=context,
            original_input=original_input
        )

        handoff = CollaborationHandoff(
            from_agent=from_agent,
            to_agent=to_agent,
            payload=payload,
            timeout_ms=timeout_ms
        )

        logger.info(f"Created handoff {handoff.handoff_id}: {from_agent} -> {to_agent}")
        return handoff

    def execute_handoff(self, handoff: CollaborationHandoff) -> CollaborationResult:
        """
        Execute a collaboration handoff (synchronous for MVP).

        Args:
            handoff: The handoff to execute

        Returns:
            CollaborationResult with execution outcome

        Raises:
            CollaborationError: If execution fails
        """
        start_time = time.time()
        timeout_seconds = handoff.timeout_ms / 1000.0

        # Mark as accepted
        handoff.status = HandoffStatus.ACCEPTED
        logger.info(f"Executing handoff {handoff.handoff_id} to {handoff.to_agent}")

        # Get handler for target agent
        handler = get_handler(handoff.to_agent)

        if handler is None:
            handoff.status = HandoffStatus.FAILED
            raise CollaborationError(
                f"No handler registered for agent: {handoff.to_agent}",
                handoff.handoff_id,
                "permanent"
            )

        try:
            # Execute with timeout check
            result = handler(handoff)

            elapsed = time.time() - start_time
            if elapsed > timeout_seconds:
                logger.warning(
                    f"Handoff {handoff.handoff_id} exceeded timeout "
                    f"({elapsed:.2f}s > {timeout_seconds}s)"
                )
                handoff.status = HandoffStatus.TIMEOUT
                result.status = ResultStatus.PARTIAL
            else:
                handoff.status = HandoffStatus.COMPLETED

            return result

        except Exception as e:
            handoff.status = HandoffStatus.FAILED
            logger.error(f"Handoff {handoff.handoff_id} failed: {e}")

            return CollaborationResult(
                handoff_id=handoff.handoff_id,
                executed_by=handoff.to_agent,
                status=ResultStatus.ERROR,
                result={},
                error={"message": str(e), "error_type": "unknown"}
            )

    def interpret_and_ingest(
        self,
        intent: str,
        content: str,
        source_path: Optional[str] = None
    ) -> CollaborationResult:
        """
        Convenience method: Interpret intent then ingest content.

        This demonstrates the Interpreter -> Ingester collaboration flow.

        Args:
            intent: Natural language intent
            content: Content to ingest
            source_path: Source path for provenance

        Returns:
            CollaborationResult from the ingestion
        """
        from .interpreter import Interpreter, InterpreterConfig

        # Step 1: Interpret the intent
        interpreter = Interpreter(
            config=InterpreterConfig(use_llm=False, fallback_to_rules=True),
            db_manager=self.db_manager,
            api_key=self.api_key
        )
        interpretation = interpreter.translate(intent)

        # Step 2: Create handoff to ingester
        handoff = self.create_handoff(
            from_agent="interpreter-v1",
            to_agent="ingester-v1",
            directive={
                "action": interpretation.directive.get("action", "ingest"),
                "type": interpretation.directive.get("type", "unknown"),
                "content": content,
                "source_path": source_path or f"intent:{intent[:50]}",
            },
            context={
                "confidence": interpretation.confidence,
                "grounded": interpretation.grounded,
            },
            original_input=intent
        )

        # Step 3: Execute handoff
        return self.execute_handoff(handoff)
