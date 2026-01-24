# generated: 2026-01-24
# System Auto: last updated on: 2026-01-24T18:40:20
"""
Session Loader for Configuration Arc.

CH-005: Implements session context loading for coldstart Phase 2.
Follows IdentityLoader pattern (WORK-007).

Extracts checkpoint frontmatter and queries memory refs for
token-efficient session context injection.

Usage:
    from session_loader import SessionLoader

    loader = SessionLoader()
    session_context = loader.load()  # Returns ~30 lines of session context

    # Or step by step:
    extracted = loader.extract()  # Dict with session, pending, drift, etc.
    formatted = loader.format(extracted)  # Formatted string

Extracted Content:
    - Prior session number from checkpoint
    - Completed work from last session
    - Pending items for next session
    - Drift warnings (PROMINENT)
    - Memory refs content
"""
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import re
import yaml
import logging

logger = logging.getLogger(__name__)

# Path setup (same pattern as identity_loader.py)
CONFIG_DIR = Path(__file__).parent.parent / "config" / "loaders"
DEFAULT_CONFIG = CONFIG_DIR / "session.yaml"
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


class SessionLoader:
    """
    Extract session context from latest checkpoint + memory.

    Uses session.yaml config to extract:
    - Prior session number
    - Completed work
    - Pending items
    - Drift warnings (PROMINENT)
    - Memory refs content

    This follows the IdentityLoader pattern (WORK-007).
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
        checkpoint_dir: Optional[Path] = None,
        memory_query_fn: Optional[Callable[[List[int]], str]] = None,
    ):
        """
        Initialize session loader.

        Args:
            config_path: Path to session.yaml (default: standard location)
            checkpoint_dir: Override checkpoint directory (for testing)
            memory_query_fn: Optional function to query memory IDs

        Note:
            Gracefully degrades if config file not found.
        """
        self.config_path = config_path or DEFAULT_CONFIG
        self._checkpoint_dir = checkpoint_dir
        self._memory_query_fn = memory_query_fn
        self._load_config()

    def _load_config(self) -> None:
        """Load config from YAML file."""
        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}
        else:
            logger.warning(f"Config not found: {self.config_path}")
            self.config = {}

    @property
    def checkpoint_dir(self) -> Path:
        """Get checkpoint directory from config or override."""
        if self._checkpoint_dir:
            return self._checkpoint_dir
        return PROJECT_ROOT / self.config.get("checkpoint_dir", "docs/checkpoints/")

    def _find_latest_checkpoint(self) -> Optional[Path]:
        """Find most recent checkpoint by filename sort."""
        if not self.checkpoint_dir.exists():
            logger.warning(f"Checkpoint dir not found: {self.checkpoint_dir}")
            return None
        checkpoints = sorted(self.checkpoint_dir.glob("*.md"), reverse=True)
        # Filter out README.md
        checkpoints = [cp for cp in checkpoints if cp.name != "README.md"]
        return checkpoints[0] if checkpoints else None

    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from markdown."""
        if not content.strip().startswith("---"):
            return {}
        match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1)) or {}
            except yaml.YAMLError as e:
                logger.warning(f"Failed to parse frontmatter: {e}")
                return {}
        return {}

    def _query_memory_ids(self, ids: List[int]) -> str:
        """Query memory for concept IDs."""
        if not ids:
            return "(no memory refs)"
        if self._memory_query_fn:
            return self._memory_query_fn(ids)
        # Default: format IDs for manual query (fallback)
        return f"Memory IDs to query: {ids}"

    def extract(self) -> Dict[str, Any]:
        """
        Extract session context from latest checkpoint + memory.

        Returns:
            Dict with: prior_session, completed, pending, drift_observed,
                       memory_refs, memory_content
        """
        result = {
            "prior_session": None,
            "completed": [],
            "pending": [],
            "drift_observed": [],
            "memory_refs": [],
            "memory_content": "",
        }

        checkpoint = self._find_latest_checkpoint()
        if not checkpoint:
            logger.warning("No checkpoint found")
            return result

        content = checkpoint.read_text(encoding="utf-8")
        fm = self._parse_frontmatter(content)

        result["prior_session"] = fm.get("session")
        result["completed"] = fm.get("completed", [])
        result["pending"] = fm.get("pending", [])
        result["drift_observed"] = fm.get("drift_observed", [])
        result["memory_refs"] = fm.get("load_memory_refs", [])
        result["memory_content"] = self._query_memory_ids(result["memory_refs"])

        return result

    def format(self, extracted: Dict[str, Any]) -> str:
        """
        Format extracted data using output template.

        Args:
            extracted: Dict from extract()

        Returns:
            Formatted string with drift warnings prominent
        """
        output_config = self.config.get("output", {})
        template = output_config.get("template", "")
        sep = output_config.get("list_separator", "\n- ")

        if not template:
            # Default template with drift prominence
            template = """=== SESSION CONTEXT ===
Prior Session: {prior_session}

Completed last session:
{completed}

=== DRIFT WARNINGS ===
{drift_observed}

Memory from prior session:
{memory_content}

Pending:
{pending}"""

        # Format lists
        format_vals = {}
        for k, v in extracted.items():
            if isinstance(v, list):
                format_vals[k] = sep.join(str(i) for i in v) if v else "(none)"
            else:
                format_vals[k] = v if v is not None else "(unknown)"

        return template.format(**format_vals)

    def load(self) -> str:
        """
        Extract and format in one call.

        Returns:
            Injection-ready string (~30 lines)
        """
        return self.format(self.extract())


# CLI entry point for `just session-context`
if __name__ == "__main__":
    loader = SessionLoader()
    print(loader.load())
