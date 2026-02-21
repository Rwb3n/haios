# generated: 2026-02-21
# WORK-180: EpochLoader per ADR-047 Tiered Coldstart
"""
Epoch Loader for Coldstart Arc.

WORK-180: Implements EpochLoader per ADR-047.
Reads EPOCH.md + active ARC.md files live at runtime,
extracts/compresses status, chapters, exit criteria.

Follows SessionLoader/WorkLoader pattern (standalone class).

Usage:
    from epoch_loader import EpochLoader
    loader = EpochLoader()
    output = loader.load()  # Returns ~60-80 lines of epoch context
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import re
import yaml
import logging

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
# A6 guard: fail fast if path assumption is wrong (Critique A6)
assert (PROJECT_ROOT / ".claude").exists(), f"PROJECT_ROOT miscalculated: {PROJECT_ROOT}"


class EpochLoader:
    """
    Extract epoch context from EPOCH.md and active ARC.md files.

    Reads source files live every invocation (no caching).
    Epoch content changes frequently — stale context is a silent failure.
    """

    def __init__(
        self,
        haios_config_path: Optional[Path] = None,
        base_path: Optional[Path] = None,
    ):
        """
        Initialize with haios.yaml config path.

        Args:
            haios_config_path: Path to haios.yaml. Default: standard location.
            base_path: Project root for resolving relative paths. Default: auto-detect.
        """
        self._base_path = base_path or PROJECT_ROOT
        self._haios_config_path = haios_config_path or (
            self._base_path / ".claude" / "haios" / "config" / "haios.yaml"
        )
        self._haios_config = self._load_haios_config()

    def _load_haios_config(self) -> Dict:
        """Load haios.yaml from disk."""
        try:
            with open(self._haios_config_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            logger.warning(f"Failed to load haios.yaml: {e}")
            return {}

    def _parse_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from markdown."""
        if not content.strip().startswith("---"):
            return {}
        match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
        if match:
            try:
                return yaml.safe_load(match.group(1)) or {}
            except yaml.YAMLError:
                return {}
        return {}

    def _extract_exit_criteria(self, content: str) -> List[str]:
        """Extract exit criteria checkboxes from markdown."""
        criteria = []
        in_exit = False
        for line in content.split("\n"):
            if line.strip().startswith("## Exit Criteria"):
                in_exit = True
                continue
            if in_exit and line.strip().startswith("## "):
                break
            if in_exit and line.strip().startswith("- ["):
                criteria.append(line.strip())
        return criteria

    def _extract_chapter_table(self, content: str) -> List[Dict]:
        """Extract chapter status rows from arc markdown tables."""
        chapters = []
        for line in content.split("\n"):
            line_s = line.strip()
            if not line_s.startswith("|"):
                continue
            if "CH-ID" in line_s or "---" in line_s:
                continue
            cells = [c.strip() for c in line_s.split("|") if c.strip()]
            if len(cells) >= 4 and cells[0].startswith("CH-"):
                chapters.append({
                    "id": cells[0],
                    "title": cells[1],
                    "status": cells[-1],
                })
        return chapters

    def extract(self) -> Dict[str, Any]:
        """
        Extract epoch context from EPOCH.md and active ARC.md files.

        Returns:
            Dict with: epoch_id, epoch_name, epoch_status, arcs, exit_criteria, error
        """
        epoch_cfg = self._haios_config.get("epoch", {})
        result = {
            "epoch_id": epoch_cfg.get("current", "unknown"),
            "epoch_name": "",
            "epoch_status": "",
            "arcs": [],
            "exit_criteria": [],
            "error": None,
        }

        # Read EPOCH.md
        epoch_file = epoch_cfg.get("epoch_file", "")
        if not epoch_file:
            result["error"] = "No epoch_file in haios.yaml"
            return result

        epoch_path = self._base_path / epoch_file
        if not epoch_path.exists():
            result["error"] = f"EPOCH.md not found: {epoch_path}"
            return result

        epoch_content = epoch_path.read_text(encoding="utf-8")
        fm = self._parse_frontmatter(epoch_content)

        # Extract from EPOCH.md content — try bold-prefix pattern first,
        # fall back to frontmatter fields (Critique A5: validation for empty values)
        for line in epoch_content.split("\n"):
            if line.startswith("**Name:**"):
                result["epoch_name"] = line.split("**Name:**")[1].strip()
            if line.startswith("**Status:**"):
                result["epoch_status"] = line.split("**Status:**")[1].strip()

        # A5 fix: fallback to frontmatter if bold-prefix extraction failed
        if not result["epoch_name"]:
            result["epoch_name"] = fm.get("name", "")
        if not result["epoch_status"]:
            result["epoch_status"] = fm.get("status", "")

        # A5 fix: warn if still empty after fallback
        if not result["epoch_name"]:
            logger.warning("Could not extract epoch name from EPOCH.md")
            result["epoch_name"] = "(unknown — check EPOCH.md format)"
        if not result["epoch_status"]:
            logger.warning("Could not extract epoch status from EPOCH.md")
            result["epoch_status"] = "(unknown)"

        result["exit_criteria"] = self._extract_exit_criteria(epoch_content)

        # Read active ARC.md files
        arcs_dir = epoch_cfg.get("arcs_dir", "")
        active_arcs = epoch_cfg.get("active_arcs", [])

        for arc_name in active_arcs:
            arc_path = self._base_path / arcs_dir / arc_name / "ARC.md"
            arc_data = {"name": arc_name, "chapters": [], "error": None}

            if not arc_path.exists():
                arc_data["error"] = f"ARC.md not found: {arc_path}"
                result["arcs"].append(arc_data)
                continue

            arc_content = arc_path.read_text(encoding="utf-8")
            arc_data["chapters"] = self._extract_chapter_table(arc_content)
            result["arcs"].append(arc_data)

        return result

    def format(self, extracted: Dict[str, Any]) -> str:
        """
        Format extracted epoch data for context injection.

        Args:
            extracted: Dict from extract()

        Returns:
            Formatted string ready for context injection (~60-80 lines).
        """
        lines = ["=== EPOCH CONTEXT ==="]

        if extracted.get("error"):
            lines.append(f"(Epoch loading error: {extracted['error']})")
            return "\n".join(lines)

        lines.append(
            f"Epoch: {extracted['epoch_id']} — {extracted['epoch_name']} "
            f"({extracted['epoch_status']})"
        )

        # Arcs + chapters
        for arc in extracted["arcs"]:
            lines.append(f"\nArc: {arc['name']}")
            if arc.get("error"):
                lines.append(f"  (Warning: {arc['error']})")
                continue
            for ch in arc["chapters"]:
                lines.append(f"  {ch['id']} {ch['title']}: {ch['status']}")

        # Exit criteria
        if extracted["exit_criteria"]:
            lines.append("\nEpoch Exit Criteria:")
            for c in extracted["exit_criteria"]:
                lines.append(f"  {c}")

        return "\n".join(lines)

    def load(self) -> str:
        """
        Extract and format epoch context in one call.

        Returns:
            Injection-ready string (~60-80 lines).
        """
        return self.format(self.extract())


# CLI entry point for `just epoch-context`
if __name__ == "__main__":
    loader = EpochLoader()
    print(loader.load())
