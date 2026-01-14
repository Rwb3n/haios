# generated: 2025-12-02
# System Auto: last updated on: 2025-12-02 21:58:41
"""
Tests for Collaboration Protocol (GAP-A4)

Tests the agent-to-agent handoff functionality.
Reference: docs/specs/collaboration_handoff_schema.md
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime


class TestCollaborationHandoff:
    """Tests for CollaborationHandoff dataclass."""

    def test_handoff_creation_basic(self):
        """Test basic handoff creation."""
        from haios_etl.agents.collaboration import (
            CollaborationHandoff, HandoffPayload, HandoffStatus
        )

        payload = HandoffPayload(
            directive={"action": "ingest", "type": "episteme"},
            context={"confidence": 0.85},
            original_input="Store this as knowledge"
        )

        handoff = CollaborationHandoff(
            from_agent="interpreter-v1",
            to_agent="ingester-v1",
            payload=payload
        )

        assert handoff.from_agent == "interpreter-v1"
        assert handoff.to_agent == "ingester-v1"
        assert handoff.payload.directive["action"] == "ingest"
        assert handoff.status == HandoffStatus.PENDING
        assert handoff.timeout_ms == 30000

    def test_handoff_has_uuid(self):
        """Test that handoff gets a UUID."""
        from haios_etl.agents.collaboration import (
            CollaborationHandoff, HandoffPayload
        )

        payload = HandoffPayload(directive={"action": "test"})
        handoff = CollaborationHandoff(
            from_agent="a1",
            to_agent="a2",
            payload=payload
        )

        assert handoff.handoff_id is not None
        assert len(handoff.handoff_id) == 36  # UUID length

    def test_handoff_has_timestamp(self):
        """Test that handoff gets a creation timestamp."""
        from haios_etl.agents.collaboration import (
            CollaborationHandoff, HandoffPayload
        )

        payload = HandoffPayload(directive={"action": "test"})
        handoff = CollaborationHandoff(
            from_agent="a1",
            to_agent="a2",
            payload=payload
        )

        assert handoff.created_at is not None
        assert isinstance(handoff.created_at, datetime)

    def test_handoff_to_dict(self):
        """Test handoff serialization."""
        from haios_etl.agents.collaboration import (
            CollaborationHandoff, HandoffPayload
        )

        payload = HandoffPayload(
            directive={"action": "ingest"},
            context={"key": "value"}
        )
        handoff = CollaborationHandoff(
            from_agent="interpreter-v1",
            to_agent="ingester-v1",
            payload=payload
        )

        result = handoff.to_dict()

        assert result["from_agent"] == "interpreter-v1"
        assert result["to_agent"] == "ingester-v1"
        assert result["payload"]["directive"]["action"] == "ingest"
        assert result["status"] == "pending"
        assert "handoff_id" in result
        assert "created_at" in result


class TestCollaborationResult:
    """Tests for CollaborationResult dataclass."""

    def test_result_creation_success(self):
        """Test successful result creation."""
        from haios_etl.agents.collaboration import (
            CollaborationResult, ResultStatus
        )

        result = CollaborationResult(
            handoff_id="test-123",
            executed_by="ingester-v1",
            status=ResultStatus.SUCCESS,
            result={"concept_ids": [1, 2, 3]}
        )

        assert result.handoff_id == "test-123"
        assert result.executed_by == "ingester-v1"
        assert result.status == ResultStatus.SUCCESS
        assert result.result["concept_ids"] == [1, 2, 3]
        assert result.error is None

    def test_result_creation_error(self):
        """Test error result creation."""
        from haios_etl.agents.collaboration import (
            CollaborationResult, ResultStatus
        )

        result = CollaborationResult(
            handoff_id="test-123",
            executed_by="ingester-v1",
            status=ResultStatus.ERROR,
            result={},
            error={"message": "Failed", "error_type": "permanent"}
        )

        assert result.status == ResultStatus.ERROR
        assert result.error["message"] == "Failed"

    def test_result_to_dict(self):
        """Test result serialization."""
        from haios_etl.agents.collaboration import (
            CollaborationResult, ResultStatus
        )

        result = CollaborationResult(
            handoff_id="test-123",
            executed_by="ingester-v1",
            status=ResultStatus.SUCCESS,
            result={"data": "value"}
        )

        data = result.to_dict()

        assert data["handoff_id"] == "test-123"
        assert data["status"] == "success"
        assert "executed_at" in data


class TestHandoffPayload:
    """Tests for HandoffPayload dataclass."""

    def test_payload_with_all_fields(self):
        """Test payload with all fields."""
        from haios_etl.agents.collaboration import HandoffPayload

        payload = HandoffPayload(
            directive={"action": "ingest", "type": "episteme"},
            context={"confidence": 0.9},
            original_input="Store this document"
        )

        assert payload.directive["action"] == "ingest"
        assert payload.context["confidence"] == 0.9
        assert payload.original_input == "Store this document"

    def test_payload_minimal(self):
        """Test payload with only required field."""
        from haios_etl.agents.collaboration import HandoffPayload

        payload = HandoffPayload(directive={"action": "test"})

        assert payload.directive["action"] == "test"
        assert payload.context is None
        assert payload.original_input is None


class TestCollaborator:
    """Tests for Collaborator class."""

    @pytest.fixture
    def db_manager(self):
        """Create a mock database manager."""
        mock = Mock()
        mock.insert_entity = Mock(return_value=1)
        mock.insert_concept = Mock(return_value=1)
        return mock

    @pytest.fixture
    def collaborator(self, db_manager):
        """Create a Collaborator instance."""
        from haios_etl.agents.collaboration import Collaborator
        return Collaborator(db_manager=db_manager, api_key="test-key")

    def test_create_handoff(self, collaborator):
        """Test creating a handoff."""
        handoff = collaborator.create_handoff(
            from_agent="interpreter-v1",
            to_agent="ingester-v1",
            directive={"action": "ingest", "content": "test"},
            context={"confidence": 0.85}
        )

        assert handoff.from_agent == "interpreter-v1"
        assert handoff.to_agent == "ingester-v1"
        assert handoff.payload.directive["action"] == "ingest"
        assert handoff.payload.context["confidence"] == 0.85

    def test_create_handoff_with_original_input(self, collaborator):
        """Test creating handoff with original input."""
        handoff = collaborator.create_handoff(
            from_agent="interpreter-v1",
            to_agent="ingester-v1",
            directive={"action": "ingest"},
            original_input="Store this as knowledge"
        )

        assert handoff.payload.original_input == "Store this as knowledge"

    def test_create_handoff_custom_timeout(self, collaborator):
        """Test creating handoff with custom timeout."""
        handoff = collaborator.create_handoff(
            from_agent="a1",
            to_agent="a2",
            directive={"action": "test"},
            timeout_ms=60000
        )

        assert handoff.timeout_ms == 60000

    @patch('haios_etl.agents.collaboration.get_handler')
    def test_execute_handoff_success(self, mock_get_handler, collaborator):
        """Test successful handoff execution."""
        from haios_etl.agents.collaboration import (
            CollaborationResult, ResultStatus, HandoffStatus
        )

        # Mock the handler
        mock_handler = Mock(return_value=CollaborationResult(
            handoff_id="test-123",
            executed_by="ingester-v1",
            status=ResultStatus.SUCCESS,
            result={"concept_ids": [1, 2]}
        ))
        mock_get_handler.return_value = mock_handler

        handoff = collaborator.create_handoff(
            from_agent="interpreter-v1",
            to_agent="ingester-v1",
            directive={"action": "ingest", "content": "test"}
        )

        result = collaborator.execute_handoff(handoff)

        assert result.status == ResultStatus.SUCCESS
        assert handoff.status == HandoffStatus.COMPLETED
        mock_handler.assert_called_once()

    @patch('haios_etl.agents.collaboration.get_handler')
    def test_execute_handoff_no_handler(self, mock_get_handler, collaborator):
        """Test handoff execution with no handler registered."""
        from haios_etl.agents.collaboration import (
            CollaborationError, HandoffStatus
        )

        mock_get_handler.return_value = None

        handoff = collaborator.create_handoff(
            from_agent="interpreter-v1",
            to_agent="unknown-agent",
            directive={"action": "test"}
        )

        with pytest.raises(CollaborationError) as exc_info:
            collaborator.execute_handoff(handoff)

        assert "No handler registered" in str(exc_info.value)
        assert handoff.status == HandoffStatus.FAILED

    @patch('haios_etl.agents.collaboration.get_handler')
    def test_execute_handoff_handler_exception(self, mock_get_handler, collaborator):
        """Test handoff execution when handler throws exception."""
        from haios_etl.agents.collaboration import ResultStatus

        mock_handler = Mock(side_effect=Exception("Handler error"))
        mock_get_handler.return_value = mock_handler

        handoff = collaborator.create_handoff(
            from_agent="interpreter-v1",
            to_agent="ingester-v1",
            directive={"action": "test"}
        )

        result = collaborator.execute_handoff(handoff)

        assert result.status == ResultStatus.ERROR
        assert "Handler error" in result.error["message"]


class TestHandlerRegistry:
    """Tests for handler registration."""

    def test_register_handler(self):
        """Test registering a handler."""
        from haios_etl.agents.collaboration import register_handler, get_handler

        def custom_handler(handoff):
            return None

        register_handler("custom-agent", custom_handler)
        handler = get_handler("custom-agent")

        assert handler == custom_handler

    def test_get_unregistered_handler(self):
        """Test getting an unregistered handler."""
        from haios_etl.agents.collaboration import get_handler

        handler = get_handler("nonexistent-agent-xyz")
        assert handler is None


class TestCollaboratorIntegration:
    """Integration tests for Collaborator with real agents."""

    @pytest.fixture
    def db_manager(self):
        """Create a mock database manager."""
        mock = Mock()
        mock.insert_entity = Mock(return_value=1)
        mock.insert_concept = Mock(return_value=1)
        return mock

    @patch('haios_etl.extraction.ExtractionManager')
    def test_ingester_handler_success(self, mock_extraction_manager, db_manager):
        """Test the default ingester handler."""
        from haios_etl.agents.collaboration import (
            Collaborator, HandoffPayload, CollaborationHandoff, ResultStatus
        )

        # Mock extraction result
        mock_result = Mock()
        mock_result.entities = [Mock(type="Person", value="Alice")]
        mock_result.concepts = [Mock(type="episteme", content="Test concept", source_adr="ADR-001")]
        mock_extraction_manager.return_value.extract_from_file.return_value = mock_result

        collaborator = Collaborator(db_manager=db_manager, api_key="test")

        handoff = CollaborationHandoff(
            from_agent="interpreter-v1",
            to_agent="ingester-v1",
            payload=HandoffPayload(
                directive={
                    "action": "ingest",
                    "content": "Alice is a person who knows about testing.",
                    "type": "episteme"
                }
            )
        )

        result = collaborator.execute_handoff(handoff)

        assert result.status == ResultStatus.SUCCESS
        assert result.executed_by == "ingester-v1"
        assert "concept_ids" in result.result

    @patch('haios_etl.extraction.ExtractionManager')
    def test_interpret_and_ingest_flow(self, mock_extraction_manager, db_manager):
        """Test the full interpret -> ingest flow."""
        from haios_etl.agents.collaboration import Collaborator, ResultStatus

        # Mock extraction result
        mock_result = Mock()
        mock_result.entities = []
        mock_result.concepts = [Mock(type="episteme", content="ADR content", source_adr="ADR-001")]
        mock_extraction_manager.return_value.extract_from_file.return_value = mock_result

        collaborator = Collaborator(db_manager=db_manager, api_key="test")

        result = collaborator.interpret_and_ingest(
            intent="Store this ADR as knowledge",
            content="ADR-001: We decided to use Python.",
            source_path="docs/ADR/ADR-001.md"
        )

        assert result.status == ResultStatus.SUCCESS
        assert result.executed_by == "ingester-v1"


class TestHandoffStatus:
    """Tests for HandoffStatus enum."""

    def test_status_values(self):
        """Test all status values exist."""
        from haios_etl.agents.collaboration import HandoffStatus

        assert HandoffStatus.PENDING.value == "pending"
        assert HandoffStatus.ACCEPTED.value == "accepted"
        assert HandoffStatus.COMPLETED.value == "completed"
        assert HandoffStatus.FAILED.value == "failed"
        assert HandoffStatus.TIMEOUT.value == "timeout"


class TestResultStatus:
    """Tests for ResultStatus enum."""

    def test_result_status_values(self):
        """Test all result status values exist."""
        from haios_etl.agents.collaboration import ResultStatus

        assert ResultStatus.SUCCESS.value == "success"
        assert ResultStatus.PARTIAL.value == "partial"
        assert ResultStatus.ERROR.value == "error"


class TestCollaborationError:
    """Tests for CollaborationError exception."""

    def test_error_creation(self):
        """Test creating a collaboration error."""
        from haios_etl.agents.collaboration import CollaborationError

        error = CollaborationError(
            message="Test error",
            handoff_id="test-123",
            error_type="permanent"
        )

        assert str(error) == "Test error"
        assert error.handoff_id == "test-123"
        assert error.error_type == "permanent"

    def test_error_default_type(self):
        """Test error with default type."""
        from haios_etl.agents.collaboration import CollaborationError

        error = CollaborationError(
            message="Test error",
            handoff_id="test-123"
        )

        assert error.error_type == "unknown"
