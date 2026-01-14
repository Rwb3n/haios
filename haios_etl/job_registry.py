# generated: 2025-12-07
# System Auto: last updated on: 2025-12-07 23:06:39
"""
Background Job Registry for HAIOS Process Observability (E2-011 Phase 2).

This module tracks background jobs to provide operator visibility into
what's currently running. It solves the blind spot where long-running
processes had no status indication.

Usage:
    from haios_etl.job_registry import JobRegistry

    registry = JobRegistry()  # Uses default path
    job_id = registry.register(command="synthesis run", shell_id="abc123")
    jobs = registry.list_jobs()
    registry.deregister(shell_id="abc123")

Default registry path: .claude/background_jobs.json
"""
import json
import os
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Default registry location
DEFAULT_REGISTRY_PATH = ".claude/background_jobs.json"


@dataclass
class JobInfo:
    """
    Information about a background job.

    Attributes:
        shell_id: The bash shell ID from Claude Code
        command: The command being executed
        started_at: ISO timestamp when job started
        status: Job status (running, completed, failed)
        pid: Optional process ID
        description: Optional human-readable description
    """
    shell_id: str
    command: str
    started_at: str
    status: str = "running"
    pid: Optional[int] = None
    description: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "shell_id": self.shell_id,
            "command": self.command,
            "started_at": self.started_at,
            "status": self.status,
            "pid": self.pid,
            "description": self.description
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "JobInfo":
        """Create JobInfo from dictionary."""
        return cls(
            shell_id=data["shell_id"],
            command=data["command"],
            started_at=data["started_at"],
            status=data.get("status", "running"),
            pid=data.get("pid"),
            description=data.get("description")
        )


class JobRegistry:
    """
    Registry for tracking background jobs.

    Provides a simple file-based registry that persists job information
    across sessions. Designed for single-writer scenarios (one Claude
    session at a time).

    Args:
        registry_path: Path to the registry JSON file.
                      Defaults to .claude/background_jobs.json
    """

    def __init__(self, registry_path: Optional[str] = None):
        """Initialize the job registry."""
        if registry_path is None:
            # Find project root (look for .claude directory)
            self.registry_path = Path(DEFAULT_REGISTRY_PATH)
        else:
            self.registry_path = Path(registry_path)

        self._jobs: Dict[str, JobInfo] = {}
        self._load()

    def _load(self) -> None:
        """Load jobs from the registry file."""
        if not self.registry_path.exists():
            self._jobs = {}
            return

        try:
            with open(self.registry_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self._jobs = {
                job_data["shell_id"]: JobInfo.from_dict(job_data)
                for job_data in data.get("jobs", [])
            }
        except (json.JSONDecodeError, KeyError) as e:
            logger.warning(f"Failed to load job registry: {e}")
            self._jobs = {}

    def _save(self) -> None:
        """Save jobs to the registry file."""
        # Ensure directory exists
        self.registry_path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "jobs": [job.to_dict() for job in self._jobs.values()],
            "last_updated": datetime.now().isoformat()
        }

        with open(self.registry_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def register(
        self,
        command: str,
        shell_id: str,
        pid: Optional[int] = None,
        description: Optional[str] = None
    ) -> str:
        """
        Register a new background job.

        Args:
            command: The command being executed
            shell_id: The bash shell ID
            pid: Optional process ID
            description: Optional human-readable description

        Returns:
            The shell_id (used as job identifier)
        """
        job = JobInfo(
            shell_id=shell_id,
            command=command,
            started_at=datetime.now().isoformat(),
            status="running",
            pid=pid,
            description=description
        )

        self._jobs[shell_id] = job
        self._save()

        logger.info(f"Registered background job: {shell_id} - {command}")
        return shell_id

    def deregister(self, shell_id: str) -> None:
        """
        Remove a job from the registry.

        Safe to call with nonexistent shell_id.

        Args:
            shell_id: The shell ID to remove
        """
        if shell_id in self._jobs:
            del self._jobs[shell_id]
            self._save()
            logger.info(f"Deregistered background job: {shell_id}")

    def list_jobs(self, status: Optional[str] = None) -> List[JobInfo]:
        """
        List all registered jobs.

        Args:
            status: Optional filter by status

        Returns:
            List of JobInfo objects
        """
        if status is None:
            return list(self._jobs.values())
        return [job for job in self._jobs.values() if job.status == status]

    def get_job(self, shell_id: str) -> Optional[JobInfo]:
        """
        Get a specific job by shell ID.

        Args:
            shell_id: The shell ID to look up

        Returns:
            JobInfo if found, None otherwise
        """
        return self._jobs.get(shell_id)

    def update_status(self, shell_id: str, status: str) -> None:
        """
        Update the status of a job.

        Args:
            shell_id: The shell ID to update
            status: New status (running, completed, failed)
        """
        if shell_id in self._jobs:
            self._jobs[shell_id].status = status
            self._save()
            logger.info(f"Updated job {shell_id} status to: {status}")

    def clear_completed(self) -> int:
        """
        Remove all completed and failed jobs from the registry.

        Returns:
            Number of jobs removed
        """
        initial_count = len(self._jobs)
        self._jobs = {
            sid: job for sid, job in self._jobs.items()
            if job.status == "running"
        }
        removed = initial_count - len(self._jobs)

        if removed > 0:
            self._save()
            logger.info(f"Cleared {removed} completed/failed jobs")

        return removed
