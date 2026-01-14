# generated: 2025-12-07
# System Auto: last updated on: 2025-12-07 23:06:02
"""
Tests for Background Job Registry (E2-011 Phase 2).

Purpose: Track background jobs for operator visibility.
Plan Reference: PLAN-INVESTIGATION-MEMORY-PROCESS-OBSERVABILITY.md Phase 2

The registry enables:
- Tracking what's currently running
- Displaying job status in /status command
- Automatic cleanup on job completion
"""
import pytest
import json
import tempfile
import os
from pathlib import Path

from haios_etl.job_registry import JobRegistry, JobInfo


class TestJobRegistry:
    """Tests for job registration and tracking."""

    @pytest.fixture
    def temp_registry(self):
        """Create a temporary registry file."""
        fd, path = tempfile.mkstemp(suffix=".json")
        os.close(fd)
        yield path
        if os.path.exists(path):
            os.unlink(path)

    def test_register_job_creates_entry(self, temp_registry):
        """Registering a job creates an entry in the registry."""
        registry = JobRegistry(temp_registry)

        job_id = registry.register(
            command="python -m haios_etl.cli synthesis run",
            shell_id="abc123"
        )

        assert job_id is not None
        jobs = registry.list_jobs()
        assert len(jobs) == 1
        assert jobs[0].shell_id == "abc123"
        assert "synthesis" in jobs[0].command

    def test_deregister_job_removes_entry(self, temp_registry):
        """Deregistering a job removes it from the registry."""
        registry = JobRegistry(temp_registry)

        job_id = registry.register(
            command="python -m haios_etl.cli synthesis run",
            shell_id="abc123"
        )

        registry.deregister(shell_id="abc123")

        jobs = registry.list_jobs()
        assert len(jobs) == 0

    def test_list_jobs_returns_all_active(self, temp_registry):
        """List returns all active jobs."""
        registry = JobRegistry(temp_registry)

        registry.register(command="job1", shell_id="shell1")
        registry.register(command="job2", shell_id="shell2")
        registry.register(command="job3", shell_id="shell3")

        jobs = registry.list_jobs()
        assert len(jobs) == 3

    def test_registry_persists_to_file(self, temp_registry):
        """Registry persists jobs to file."""
        registry = JobRegistry(temp_registry)
        registry.register(command="persistent job", shell_id="persist1")

        # Create new registry instance from same file
        registry2 = JobRegistry(temp_registry)
        jobs = registry2.list_jobs()

        assert len(jobs) == 1
        assert jobs[0].shell_id == "persist1"

    def test_job_info_includes_timestamp(self, temp_registry):
        """Job info includes started_at timestamp."""
        registry = JobRegistry(temp_registry)

        registry.register(command="timestamped job", shell_id="ts1")

        jobs = registry.list_jobs()
        assert jobs[0].started_at is not None

    def test_deregister_nonexistent_job_is_safe(self, temp_registry):
        """Deregistering a job that doesn't exist is safe (no error)."""
        registry = JobRegistry(temp_registry)

        # Should not raise
        registry.deregister(shell_id="nonexistent")

        jobs = registry.list_jobs()
        assert len(jobs) == 0

    def test_registry_handles_empty_file(self, temp_registry):
        """Registry handles empty/nonexistent file gracefully."""
        # Remove the temp file to simulate nonexistent
        os.unlink(temp_registry)

        registry = JobRegistry(temp_registry)
        jobs = registry.list_jobs()

        assert len(jobs) == 0

    def test_get_job_by_shell_id(self, temp_registry):
        """Can retrieve a specific job by shell ID."""
        registry = JobRegistry(temp_registry)

        registry.register(command="find me", shell_id="findme123")
        registry.register(command="other", shell_id="other456")

        job = registry.get_job("findme123")

        assert job is not None
        assert job.command == "find me"

    def test_update_job_status(self, temp_registry):
        """Can update job status (running, completed, failed)."""
        registry = JobRegistry(temp_registry)

        registry.register(command="updatable", shell_id="upd1")
        registry.update_status("upd1", status="completed")

        job = registry.get_job("upd1")
        assert job.status == "completed"


class TestJobInfo:
    """Tests for JobInfo dataclass."""

    def test_job_info_creation(self):
        """JobInfo can be created with required fields."""
        job = JobInfo(
            shell_id="test123",
            command="test command",
            started_at="2025-12-07T12:00:00"
        )

        assert job.shell_id == "test123"
        assert job.command == "test command"
        assert job.status == "running"  # default

    def test_job_info_to_dict(self):
        """JobInfo can be converted to dict for JSON serialization."""
        job = JobInfo(
            shell_id="test123",
            command="test command",
            started_at="2025-12-07T12:00:00"
        )

        d = job.to_dict()

        assert d["shell_id"] == "test123"
        assert d["command"] == "test command"
        assert d["status"] == "running"

    def test_job_info_from_dict(self):
        """JobInfo can be created from dict."""
        d = {
            "shell_id": "from_dict",
            "command": "dict command",
            "started_at": "2025-12-07T12:00:00",
            "status": "completed"
        }

        job = JobInfo.from_dict(d)

        assert job.shell_id == "from_dict"
        assert job.status == "completed"
