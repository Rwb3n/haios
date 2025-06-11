from __future__ import annotations

# ANNOTATION_BLOCK_START
{
  "artifact_annotation_header": {
    "artifact_id_of_host": "core_config_py_g146",
    "g_annotation_created": 146,
    "version_tag_of_host_at_annotation": "1.0.0"
  },
  "payload": {
    "description": "Defines the immutable Config dataclass, providing a type-safe and explicit contract for all OS configuration data.",
    "artifact_type": "CORE_MODULE_PYTHON",
    "purpose_statement": "To eliminate brittle, 'magic key' access to configuration and provide a single source of truth for configuration shape.",
    "authors_and_contributors": [{"g_contribution": 146, "identifier": "Cody"}],
    "internal_dependencies": ["core_exceptions_py_g137"],
    "linked_issue_ids": ["issue_00121"]
  }
}
# ANNOTATION_BLOCK_END
"""core.config
~~~~~~~~~~~~~~~
Provides a type-safe, immutable dataclass for HAiOS configuration.
"""
import dataclasses
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, NamedTuple

from .exceptions import ConfigError

class PathConfig(NamedTuple):
    """Container for all configured paths."""
    os_root: Path
    project_workspace: Path
    project_templates: Path
    scaffold_definitions: Path
    guidelines: Path
    state_file: Path
    schema_dir: Path
    human_attention_queue: Path
    secrets_vault: Path
    control: Path
    exec_plans: Path
    global_registry_map: Path

@dataclass(frozen=True)
class RuntimeConfig:
    """Container for runtime mode settings."""
    mode: str
    cli_override_allowed: bool

    def replace(self, **changes: Any) -> RuntimeConfig:
        """Create a new RuntimeConfig instance with updated values."""
        return dataclasses.replace(self, **changes)

@dataclass(frozen=True)
class ExecutionConfig:
    """Container for execution settings."""
    isolation_mode: str

    def replace(self, **changes: Any) -> ExecutionConfig:
        """Create a new ExecutionConfig instance with updated values."""
        return dataclasses.replace(self, **changes)

@dataclass(frozen=True)
class BudgetsConfig:
    """Container for resource and cost budgets."""
    max_cpu_seconds_per_plan: int
    max_mem_bytes_per_plan: int
    max_tokens_per_plan: int
    max_usd_per_plan: float

    def replace(self, **changes: Any) -> BudgetsConfig:
        """Create a new BudgetsConfig instance with updated values."""
        return dataclasses.replace(self, **changes)

@dataclass(frozen=True)
class SecurityConfig:
    """Container for security settings."""
    redact_regexes: List[str]

    def replace(self, **changes: Any) -> SecurityConfig:
        """Create a new SecurityConfig instance with updated values."""
        return dataclasses.replace(self, **changes)

@dataclass(frozen=True)
class Config:
    """
    An immutable, type-safe representation of the haios.config.json file.
    """
    project_name: str
    project_root: Path
    paths: PathConfig
    runtime: RuntimeConfig
    execution: ExecutionConfig
    budgets: BudgetsConfig
    security: SecurityConfig
    os_settings: Dict[str, Any] = field(default_factory=dict)
    project_constraints: List[Dict[str, Any]] = field(default_factory=list)

    def replace(self, **changes: Any) -> Config:
        """Create a new Config instance with updated values."""
        return dataclasses.replace(self, **changes)

    def __getitem__(self, key: str):
        """Dictionary-style access shim for legacy tests.

        Only top-level keys are supported.  The mapping is *name* →
        ``project_name``.  For any other key, attribute lookup of the same
        name is attempted (e.g. ``runtime``).
        """
        if key == "name" and hasattr(self, "project_name"):
            return self.project_name
        if hasattr(self, key):
            return getattr(self, key)
        raise KeyError(key)

    # ------------------------------------------------------------------
    # Convenience helpers
    # ------------------------------------------------------------------
    @classmethod
    def from_file(cls, path: Path | str) -> "Config":
        """Loads JSON from *path* and returns a Config object.

        This is syntactic sugar for ``Config.from_dict(json.load(path),
        project_root_path=path.parent)`` and is used by several legacy
        integration tests.
        """
        import json
        p = Path(path)
        with p.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data, project_root_path=p.parent.resolve())

    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any], project_root_path: Path) -> Config:
        """
        Factory method to create a Config instance from a raw dictionary.

        Args:
            config_dict: The dictionary loaded from haios.config.json.
            project_root_path: The absolute path to the project's root directory.

        Returns:
            An immutable Config object.

        Raises:
            ConfigError: If required keys are missing or paths are invalid.
        """
        try:
            path_data = config_dict.get("paths", {})
            def _p(key, default):
                return project_root_path / path_data.get(key, default)
            paths = PathConfig(
                os_root=_p("os_root", "os_root"),
                project_workspace=_p("project_workspace", "project_workspace"),
                project_templates=_p("project_templates", "project_templates"),
                scaffold_definitions=_p("scaffold_definitions", "os_root/scaffold_definitions"),
                guidelines=_p("guidelines", "docs/guidelines"),
                state_file=_p("state_file", "os_root/state.txt"),
                schema_dir=_p("schema_dir", "schemas"),
                human_attention_queue=_p("human_attention_queue", "os_root/human_attention_queue.txt"),
                secrets_vault=_p("secrets_vault", "os_root/vault.enc"),
                control=_p("control", "os_root/control"),
                exec_plans=_p("exec_plans", "os_root/initiatives"),
                global_registry_map=_p("global_registry_map", "os_root/global_registry_map.txt"),
            )

            runtime_data = config_dict.get("runtime", {})
            runtime = RuntimeConfig(
                mode=runtime_data.get("mode", "DEV_FAST"),
                cli_override_allowed=runtime_data.get("cli_override_allowed", True),
            )

            execution_data = config_dict.get("execution", {})
            execution = ExecutionConfig(
                isolation_mode=execution_data.get("isolation_mode", "NONE"),
            )

            budgets_data = config_dict.get("budgets", {})
            budgets = BudgetsConfig(
                max_cpu_seconds_per_plan=budgets_data.get("max_cpu_seconds_per_plan", 10_000),
                max_mem_bytes_per_plan=budgets_data.get("max_mem_bytes_per_plan", 1_000_000_000),
                max_tokens_per_plan=budgets_data.get("max_tokens_per_plan", 500_000),
                max_usd_per_plan=budgets_data.get("max_usd_per_plan", 10.0),
            )

            security_data = config_dict.get("security", {})
            security = SecurityConfig(
                redact_regexes=security_data.get("redact_regexes", []),
            )

            return cls(
                project_name=config_dict.get("project_name", "Unnamed Project"),
                project_root=project_root_path,
                paths=paths,
                runtime=runtime,
                execution=execution,
                budgets=budgets,
                security=security,
                os_settings=config_dict.get("os_settings", {}),
                project_constraints=config_dict.get("project_constraints", []),
            )
        except Exception as e:
            raise ConfigError(f"Configuration structure is invalid: {e}") from e