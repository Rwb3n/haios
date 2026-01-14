# generated: 2025-12-07
# System Auto: last updated on: 2025-12-07 23:08:17
"""
Tests for System Health Checks (E2-011 Phase 3).

Purpose: Monitor database, memory, and MCP health for operator visibility.
Plan Reference: PLAN-INVESTIGATION-MEMORY-PROCESS-OBSERVABILITY.md Phase 3

Health checks enable:
- DB health monitoring (WAL size, locks)
- Memory usage tracking
- MCP server availability
"""
import pytest
import sqlite3
import tempfile
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from haios_etl.health_checks import (
    HealthChecker,
    HealthStatus,
    DBHealth,
    MemoryHealth,
    MCPHealth
)


class TestDBHealth:
    """Tests for database health monitoring."""

    @pytest.fixture
    def temp_db(self):
        """Create a temporary database."""
        fd, path = tempfile.mkstemp(suffix=".db")
        os.close(fd)

        # Create a simple table to make it a valid SQLite DB
        conn = sqlite3.connect(path)
        conn.execute("CREATE TABLE test (id INTEGER)")
        conn.commit()
        conn.close()

        yield path

        if os.path.exists(path):
            os.unlink(path)
        # Clean up WAL files if they exist
        wal_path = path + "-wal"
        shm_path = path + "-shm"
        if os.path.exists(wal_path):
            os.unlink(wal_path)
        if os.path.exists(shm_path):
            os.unlink(shm_path)

    def test_db_health_returns_status(self, temp_db):
        """DB health check returns a valid status object."""
        checker = HealthChecker(db_path=temp_db)
        health = checker.check_db_health()

        assert isinstance(health, DBHealth)
        assert health.status in ["healthy", "warning", "critical"]

    def test_db_health_includes_wal_size(self, temp_db):
        """DB health includes WAL file size."""
        checker = HealthChecker(db_path=temp_db)
        health = checker.check_db_health()

        assert hasattr(health, 'wal_size_mb')
        assert health.wal_size_mb >= 0

    def test_db_health_detects_accessible_db(self, temp_db):
        """DB health reports healthy for accessible database."""
        checker = HealthChecker(db_path=temp_db)
        health = checker.check_db_health()

        assert health.accessible is True
        assert health.status == "healthy"

    def test_db_health_detects_missing_db(self):
        """DB health reports critical for missing database."""
        checker = HealthChecker(db_path="/nonexistent/path.db")
        health = checker.check_db_health()

        assert health.accessible is False
        assert health.status == "critical"

    def test_db_health_includes_stats(self, temp_db):
        """DB health includes table/row statistics."""
        checker = HealthChecker(db_path=temp_db)
        health = checker.check_db_health()

        assert hasattr(health, 'table_count')


class TestMemoryHealth:
    """Tests for memory usage monitoring."""

    def test_memory_health_returns_status(self):
        """Memory health check returns a valid status object."""
        checker = HealthChecker()
        health = checker.check_memory_health()

        assert isinstance(health, MemoryHealth)
        assert health.status in ["healthy", "warning", "critical"]

    def test_memory_health_includes_usage_percent(self):
        """Memory health includes usage percentage."""
        checker = HealthChecker()
        health = checker.check_memory_health()

        assert hasattr(health, 'usage_percent')
        assert 0 <= health.usage_percent <= 100

    def test_memory_health_includes_available_mb(self):
        """Memory health includes available memory in MB."""
        checker = HealthChecker()
        health = checker.check_memory_health()

        assert hasattr(health, 'available_mb')
        assert health.available_mb > 0


class TestMCPHealth:
    """Tests for MCP server health monitoring."""

    def test_mcp_health_returns_status(self):
        """MCP health check returns a valid status object."""
        checker = HealthChecker()

        # Mock the MCP check since server may not be running
        with patch.object(checker, '_ping_mcp', return_value=True):
            health = checker.check_mcp_health()

        assert isinstance(health, MCPHealth)
        assert health.status in ["healthy", "warning", "critical"]

    def test_mcp_health_reports_unavailable_when_no_response(self):
        """MCP health reports unavailable when server doesn't respond."""
        checker = HealthChecker()

        with patch.object(checker, '_ping_mcp', return_value=False):
            health = checker.check_mcp_health()

        assert health.available is False
        assert health.status in ["warning", "critical"]


class TestHealthChecker:
    """Tests for the main HealthChecker class."""

    def test_full_health_check_returns_all_components(self):
        """Full health check returns DB, memory, and MCP status."""
        checker = HealthChecker()

        with patch.object(checker, '_ping_mcp', return_value=True):
            status = checker.full_health_check()

        assert isinstance(status, HealthStatus)
        assert hasattr(status, 'db')
        assert hasattr(status, 'memory')
        assert hasattr(status, 'mcp')

    def test_health_status_has_overall_status(self):
        """Health status includes overall status summary."""
        checker = HealthChecker()

        with patch.object(checker, '_ping_mcp', return_value=True):
            status = checker.full_health_check()

        assert hasattr(status, 'overall')
        assert status.overall in ["healthy", "warning", "critical"]

    def test_health_status_to_dict(self):
        """Health status can be converted to dict for JSON."""
        checker = HealthChecker()

        with patch.object(checker, '_ping_mcp', return_value=True):
            status = checker.full_health_check()

        d = status.to_dict()
        assert "db" in d
        assert "memory" in d
        assert "mcp" in d
        assert "overall" in d
