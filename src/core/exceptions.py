from __future__ import annotations

# ANNOTATION_BLOCK_START
{
  "artifact_annotation_header": {
    "artifact_id_of_host": "core_exceptions_py_g137",
    "g_annotation_created": 137,
    "version_tag_of_host_at_annotation": "1.0.0"
  },
  "payload": {
    "description": "Defines the custom exception hierarchy for the HAiOS core engine, enabling granular error handling.",
    "artifact_type": "CORE_MODULE_PYTHON",
    "purpose_statement": "To provide a clear taxonomy of operational errors, distinguishing between configuration, I/O, state, security, and planning failures.",
    "linked_issue_ids": ["issue_00121"]
  }
}
# ANNOTATION_BLOCK_END
"""core.exceptions
~~~~~~~~~~~~~~~~~
Unified error hierarchy for the HAiOS core engine.
"""
class OSCoreError(Exception):
    """Base class for all custom errors in the HAiOS engine."""

# --- Configuration Errors ---
class ConfigError(OSCoreError):
    """Base class for configuration-related errors."""

class ConfigNotFoundError(ConfigError):
    """Raised when the configuration file cannot be found."""

class ConfigParseError(ConfigError):
    """Raised when the configuration file is malformed."""

# --- Data & State Safety Errors ---
class DataSafetyError(OSCoreError):
    """Base class for errors related to data integrity and I/O safety."""

class AtomicWriteError(DataSafetyError):
    """Raised when an atomic write operation fails."""

class WriteConflictError(DataSafetyError):
    """Raised by a locking mechanism when a write conflict is detected."""

# --- Security Errors ---
class SecurityError(OSCoreError):
    """Base class for security-related errors."""

class PathEscapeError(SecurityError):
    """Raised when a path resolution attempts to escape its sandbox."""

class VaultError(SecurityError):
    """Raised for errors related to the secrets vault."""

class SignatureError(SecurityError):
    """Raised when a digital signature is invalid."""

# --- Planner & Execution Errors ---
class PlannerError(OSCoreError):
    """Base class for errors during plan execution."""

class DependencyCycleError(PlannerError):
    """Raised when a dependency cycle is detected in an execution plan."""

class TaskExecutionError(PlannerError):
    """Raised when a specific task fails during execution."""

class BudgetExceededError(PlannerError):
    """Raised when a resource budget is exceeded."""