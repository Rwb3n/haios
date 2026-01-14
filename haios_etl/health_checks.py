# generated: 2025-12-07
# System Auto: last updated on: 2025-12-07 23:09:02
"""
System Health Checks for HAIOS Process Observability (E2-011 Phase 3).

This module provides health monitoring for:
- Database (SQLite) - WAL size, accessibility, table stats
- Memory usage - percent used, available MB
- MCP server - availability, response time

Usage:
    from haios_etl.health_checks import HealthChecker

    checker = HealthChecker(db_path="haios_memory.db")
    status = checker.full_health_check()
    print(status.to_dict())

Thresholds:
- DB WAL > 100MB: warning
- Memory > 80%: warning
- Memory > 95%: critical
- MCP unavailable: warning
"""
import os
import sqlite3
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, Dict, Any
import psutil

logger = logging.getLogger(__name__)

# Default paths
DEFAULT_DB_PATH = "haios_memory.db"

# Thresholds
WAL_WARNING_MB = 100
MEMORY_WARNING_PERCENT = 80
MEMORY_CRITICAL_PERCENT = 95


@dataclass
class DBHealth:
    """Database health status."""
    accessible: bool
    status: str  # healthy, warning, critical
    wal_size_mb: float = 0.0
    db_size_mb: float = 0.0
    table_count: int = 0
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "accessible": self.accessible,
            "status": self.status,
            "wal_size_mb": round(self.wal_size_mb, 2),
            "db_size_mb": round(self.db_size_mb, 2),
            "table_count": self.table_count,
            "error": self.error_message
        }


@dataclass
class MemoryHealth:
    """Memory health status."""
    status: str  # healthy, warning, critical
    usage_percent: float
    available_mb: float
    total_mb: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "status": self.status,
            "usage_percent": round(self.usage_percent, 1),
            "available_mb": round(self.available_mb, 1),
            "total_mb": round(self.total_mb, 1)
        }


@dataclass
class MCPHealth:
    """MCP server health status."""
    available: bool
    status: str  # healthy, warning, critical
    response_time_ms: Optional[float] = None
    server_name: str = "haios-memory"
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "available": self.available,
            "status": self.status,
            "response_time_ms": self.response_time_ms,
            "server_name": self.server_name,
            "error": self.error_message
        }


@dataclass
class HealthStatus:
    """Overall health status combining all checks."""
    db: DBHealth
    memory: MemoryHealth
    mcp: MCPHealth
    overall: str  # healthy, warning, critical

    def to_dict(self) -> Dict[str, Any]:
        return {
            "overall": self.overall,
            "db": self.db.to_dict(),
            "memory": self.memory.to_dict(),
            "mcp": self.mcp.to_dict()
        }


class HealthChecker:
    """
    Health checker for HAIOS system components.

    Checks database, memory, and MCP server health.
    """

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize health checker.

        Args:
            db_path: Path to SQLite database. Defaults to haios_memory.db
        """
        self.db_path = Path(db_path) if db_path else Path(DEFAULT_DB_PATH)

    def check_db_health(self) -> DBHealth:
        """
        Check database health.

        Returns:
            DBHealth object with accessibility, WAL size, stats
        """
        # Check if DB file exists
        if not self.db_path.exists():
            return DBHealth(
                accessible=False,
                status="critical",
                error_message=f"Database not found: {self.db_path}"
            )

        try:
            # Get file sizes
            db_size_mb = self.db_path.stat().st_size / (1024 * 1024)

            # Check for WAL file
            wal_path = Path(str(self.db_path) + "-wal")
            wal_size_mb = 0.0
            if wal_path.exists():
                wal_size_mb = wal_path.stat().st_size / (1024 * 1024)

            # Try to connect and get stats
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()

            # Count tables
            cursor.execute(
                "SELECT COUNT(*) FROM sqlite_master WHERE type='table'"
            )
            table_count = cursor.fetchone()[0]

            conn.close()

            # Determine status
            status = "healthy"
            if wal_size_mb > WAL_WARNING_MB:
                status = "warning"
                logger.warning(
                    f"Database WAL file is large: {wal_size_mb:.1f}MB"
                )

            return DBHealth(
                accessible=True,
                status=status,
                wal_size_mb=wal_size_mb,
                db_size_mb=db_size_mb,
                table_count=table_count
            )

        except sqlite3.Error as e:
            logger.error(f"Database health check failed: {e}")
            return DBHealth(
                accessible=False,
                status="critical",
                error_message=str(e)
            )

    def check_memory_health(self) -> MemoryHealth:
        """
        Check system memory health.

        Returns:
            MemoryHealth object with usage stats
        """
        try:
            mem = psutil.virtual_memory()

            usage_percent = mem.percent
            available_mb = mem.available / (1024 * 1024)
            total_mb = mem.total / (1024 * 1024)

            # Determine status
            if usage_percent >= MEMORY_CRITICAL_PERCENT:
                status = "critical"
                logger.warning(f"Memory usage critical: {usage_percent:.1f}%")
            elif usage_percent >= MEMORY_WARNING_PERCENT:
                status = "warning"
                logger.warning(f"Memory usage high: {usage_percent:.1f}%")
            else:
                status = "healthy"

            return MemoryHealth(
                status=status,
                usage_percent=usage_percent,
                available_mb=available_mb,
                total_mb=total_mb
            )

        except Exception as e:
            logger.error(f"Memory health check failed: {e}")
            return MemoryHealth(
                status="critical",
                usage_percent=0,
                available_mb=0,
                total_mb=0
            )

    def check_mcp_health(self) -> MCPHealth:
        """
        Check MCP server health.

        Returns:
            MCPHealth object with availability status
        """
        import time

        start = time.time()
        available = self._ping_mcp()
        response_time_ms = (time.time() - start) * 1000

        if available:
            return MCPHealth(
                available=True,
                status="healthy",
                response_time_ms=response_time_ms
            )
        else:
            return MCPHealth(
                available=False,
                status="warning",
                error_message="MCP server not responding"
            )

    def _ping_mcp(self) -> bool:
        """
        Ping the MCP server to check availability.

        This is a placeholder - actual implementation would depend
        on how MCP is configured and running.

        Returns:
            True if MCP is available, False otherwise
        """
        # TODO: Implement actual MCP ping
        # For now, check if haios-memory MCP config exists
        mcp_config = Path(".claude/mcp.json")
        return mcp_config.exists()

    def full_health_check(self) -> HealthStatus:
        """
        Run all health checks and return combined status.

        Returns:
            HealthStatus object with all component health
        """
        db_health = self.check_db_health()
        memory_health = self.check_memory_health()
        mcp_health = self.check_mcp_health()

        # Determine overall status (worst of all)
        statuses = [db_health.status, memory_health.status, mcp_health.status]

        if "critical" in statuses:
            overall = "critical"
        elif "warning" in statuses:
            overall = "warning"
        else:
            overall = "healthy"

        return HealthStatus(
            db=db_health,
            memory=memory_health,
            mcp=mcp_health,
            overall=overall
        )
