# generated: 2026-01-24
# System Auto: last updated on: 2026-01-24T19:46:17
"""
Work Loader for Configuration Arc.

CH-006: Implements work context loading for coldstart Phase 3.
Follows SessionLoader pattern (CH-005).

Extracts queue items, pending work, and epoch alignment warnings
for token-efficient work selection context injection.

Usage:
    from work_loader import WorkLoader

    loader = WorkLoader()
    work_options = loader.load()  # Returns ~20 lines of work context

    # Or step by step:
    extracted = loader.extract()  # Dict with queue, pending, epoch info
    formatted = loader.format(extracted)  # Formatted string

Extracted Content:
    - Queue items from `just queue` (top N)
    - Pending items from checkpoint
    - Epoch alignment warning (if legacy items in queue)
"""
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import subprocess
import re
import yaml
import logging

logger = logging.getLogger(__name__)

# Path setup (same pattern as session_loader.py)
CONFIG_DIR = Path(__file__).parent.parent / "config" / "loaders"
DEFAULT_CONFIG = CONFIG_DIR / "work.yaml"
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent


class WorkLoader:
    """
    Extract work context for coldstart Phase 3.

    Uses work.yaml config to extract:
    - Queue items (top N from `just queue`)
    - Pending items from checkpoint
    - Epoch alignment warning

    This follows the SessionLoader pattern (CH-005).
    """

    def __init__(
        self,
        config_path: Optional[Path] = None,
        checkpoint_dir: Optional[Path] = None,
        queue_fn: Optional[Callable[[], List[Dict]]] = None,
    ):
        """
        Initialize work loader.

        Args:
            config_path: Path to work.yaml (default: standard location)
            checkpoint_dir: Override checkpoint directory (for testing)
            queue_fn: Optional function to get queue items (for testing)

        Note:
            Gracefully degrades if config file not found.
        """
        self.config_path = config_path or DEFAULT_CONFIG
        self._checkpoint_dir = checkpoint_dir
        self._queue_fn = queue_fn or self._default_queue_fn
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

    def _default_queue_fn(self) -> List[Dict]:
        """Run `just queue` and parse output."""
        try:
            result = subprocess.run(
                ["just", "queue"],
                capture_output=True,
                text=True,
                cwd=PROJECT_ROOT,
            )
            return self._parse_queue_output(result.stdout)
        except Exception as e:
            logger.warning(f"Queue command failed: {e}")
            return []

    def _parse_queue_output(self, output: str) -> List[Dict]:
        """Parse queue output into list of dicts."""
        items = []
        for line in output.strip().split("\n"):
            # Match pattern: "  1. E2-072: Critique Subagent (priority=medium)"
            match = re.match(r"\s*\d+\.\s+(\S+):\s+(.+?)\s+\(priority=(\w+)\)", line)
            if match:
                items.append({
                    "id": match.group(1),
                    "title": match.group(2),
                    "priority": match.group(3),
                })
        return items

    def _get_pending_from_checkpoint(self) -> List[str]:
        """Get pending items from latest checkpoint."""
        if not self.checkpoint_dir.exists():
            return []
        checkpoints = sorted(self.checkpoint_dir.glob("*.md"), reverse=True)
        # Filter out README.md
        checkpoints = [cp for cp in checkpoints if cp.name != "README.md"]
        if not checkpoints:
            return []
        content = checkpoints[0].read_text(encoding="utf-8")
        # Parse frontmatter
        match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if match:
            try:
                fm = yaml.safe_load(match.group(1)) or {}
                return fm.get("pending", [])
            except yaml.YAMLError:
                return []
        return []

    def _check_epoch_alignment(self, queue: List[Dict]) -> tuple:
        """Check if queue items match current epoch."""
        # Get current epoch from config
        haios_config_path = PROJECT_ROOT / ".claude/haios/config/haios.yaml"
        try:
            with open(haios_config_path, "r", encoding="utf-8") as f:
                haios = yaml.safe_load(f) or {}
            current_epoch = haios.get("epoch", {}).get("current", "E2.3")
        except Exception:
            current_epoch = "E2.3"

        # Count legacy items (E2-xxx when epoch is E2.3)
        legacy_count = sum(1 for item in queue if item["id"].startswith("E2-"))
        return current_epoch, legacy_count

    def extract(self) -> Dict[str, Any]:
        """
        Extract work context from queue and checkpoint.

        Returns:
            Dict with: queue, pending, current_epoch, legacy_count, queue_limit
        """
        queue = self._queue_fn()
        limit = self.config.get("queue", {}).get("limit", 5)
        queue = queue[:limit]

        pending = self._get_pending_from_checkpoint()
        current_epoch, legacy_count = self._check_epoch_alignment(queue)

        return {
            "queue": queue,
            "pending": pending,
            "current_epoch": current_epoch,
            "legacy_count": legacy_count,
            "queue_limit": limit,
        }

    def format(self, extracted: Dict[str, Any]) -> str:
        """
        Format extracted data using output template.

        Args:
            extracted: Dict from extract()

        Returns:
            Formatted string with epoch warning prominent
        """
        output_config = self.config.get("output", {})
        template = output_config.get("template", "")
        sep = output_config.get("list_separator", "\n  ")

        # Build epoch warning
        epoch_warning = ""
        if extracted["legacy_count"] > 0:
            epoch_warning = (
                f"WARNING: Queue contains {extracted['legacy_count']} items from prior epochs.\n"
                f"Current epoch: {extracted['current_epoch']}"
            )

        # Format queue items
        queue_lines = [
            f"{i+1}. {item['id']}: {item['title']}"
            for i, item in enumerate(extracted["queue"])
        ]
        queue_str = sep.join(queue_lines) if queue_lines else "(empty)"

        # Format pending
        pending = extracted["pending"]
        pending_str = sep.join(str(p) for p in pending) if pending else "(none)"

        if not template:
            # Default template
            template = """=== WORK OPTIONS ===

{epoch_warning}

Queue (top {queue_limit}):
{queue}

Pending from checkpoint:
{pending}"""

        return template.format(
            epoch_warning=epoch_warning,
            queue=queue_str,
            pending=pending_str,
            queue_limit=extracted["queue_limit"],
        )

    def load(self) -> str:
        """
        Extract and format in one call.

        Returns:
            Injection-ready string (~20 lines)
        """
        return self.format(self.extract())


# CLI entry point for `just work-options`
if __name__ == "__main__":
    loader = WorkLoader()
    print(loader.load())
