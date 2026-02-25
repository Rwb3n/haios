# generated: 2026-02-21
# WORK-180: OperationsLoader per ADR-047 Tiered Coldstart
"""
Operations Loader for Coldstart Arc.

WORK-180: Implements OperationsLoader per ADR-047.
Injects operational HOW: tier model, recipe catalogue, module paths,
common patterns. Reads source files live (no caching).

Follows SessionLoader/WorkLoader pattern (standalone class).

Usage:
    from operations_loader import OperationsLoader
    loader = OperationsLoader()
    output = loader.load()  # Returns ~40-60 lines of operational context
"""
from pathlib import Path
from typing import Any, Dict, List, Optional
import re
import logging

logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
# A6 guard: fail fast if path assumption is wrong (Critique A6)
assert (PROJECT_ROOT / ".claude").exists(), f"PROJECT_ROOT miscalculated: {PROJECT_ROOT}"

# Key recipes the agent needs to know about, grouped by category
RECIPE_CATEGORIES = {
    "Governance": [
        "scaffold", "validate", "node", "close-work",
        "set-cycle", "clear-cycle",
    ],
    "Rhythm": [
        "session-start", "session-end", "coldstart-orchestrator",
    ],
    "Plan Tree": [
        "ready", "queue", "queue-prioritize", "queue-commit",
    ],
}

# Common patterns every agent should know
COMMON_PATTERNS = [
    "WorkEngine requires GovernanceLayer: WorkEngine(governance=GovernanceLayer())",
    "Path resolution: ConfigLoader.get().get_path('work_item', id='WORK-XXX')",
    "Scaffold: scaffold_template('work_item', output_path=..., backlog_id=..., title=...)",
    "Agent MUST NOT run `just X` directly — use Skill() or Task() wrappers (ADR-045 Tier model)",
]

# Memory schema hints (WORK-232: prevent wrong column name queries)
# Source of truth: docs/specs/memory_db_schema_v3.sql
MEMORY_SCHEMA_HINTS = {
    "concepts": {
        "columns": ["id", "type", "content", "source_adr",
                     "synthesis_confidence", "synthesized_at",
                     "synthesis_cluster_id", "synthesis_source_count"],
        "note": "Column is 'type' NOT 'concept_type'. Use db_query with sql= parameter.",
    },
}


class OperationsLoader:
    """
    Inject operational context for agent execution.

    Reads source files live at runtime. Stale operational context
    is a silent failure (S393/S394 evidence).
    """

    def __init__(
        self,
        base_path: Optional[Path] = None,
        claude_md_path: Optional[Path] = None,
        justfile_path: Optional[Path] = None,
    ):
        """
        Initialize with paths to source files.

        Args:
            base_path: Project root. Default: auto-detect.
            claude_md_path: Path to CLAUDE.md. Default: {base_path}/CLAUDE.md.
            justfile_path: Path to justfile. Default: {base_path}/justfile.
        """
        self._base_path = base_path or PROJECT_ROOT
        self._claude_md_path = claude_md_path or (self._base_path / "CLAUDE.md")
        self._justfile_path = justfile_path or (self._base_path / "justfile")

    def _extract_agent_table(self) -> List[str]:
        """Extract agent table from CLAUDE.md."""
        if not self._claude_md_path.exists():
            return ["(CLAUDE.md not found)"]
        content = self._claude_md_path.read_text(encoding="utf-8")

        lines = []
        in_agents = False
        for line in content.split("\n"):
            if "| Agent |" in line and "Model" in line:
                in_agents = True
                lines.append(line.strip())
                continue
            if in_agents:
                if line.strip().startswith("|"):
                    lines.append(line.strip())
                else:
                    break
        return lines if lines else ["(No agent table found)"]

    def _extract_governance_triggers(self) -> List[str]:
        """Extract governance trigger rules from CLAUDE.md."""
        if not self._claude_md_path.exists():
            return []
        content = self._claude_md_path.read_text(encoding="utf-8")

        triggers = []
        in_triggers = False
        for line in content.split("\n"):
            if "### Governance Triggers" in line:
                in_triggers = True
                continue
            if in_triggers and line.strip().startswith("#"):
                break
            if in_triggers and line.strip().startswith("- "):
                triggers.append(line.strip())
        return triggers

    def _extract_recipe_availability(self) -> Dict[str, List[str]]:
        """Check which key recipes exist in justfile."""
        if not self._justfile_path.exists():
            return {}
        content = self._justfile_path.read_text(encoding="utf-8")

        available = {}
        for category, recipes in RECIPE_CATEGORIES.items():
            found = []
            for recipe in recipes:
                # Match recipe definition: recipe_name: or recipe_name arg:
                pattern = rf"^{re.escape(recipe)}(?:\s|\:)"
                if re.search(pattern, content, re.MULTILINE):
                    found.append(recipe)
            if found:
                available[category] = found
        return available

    def extract(self) -> Dict[str, Any]:
        """
        Extract operational context from source files.

        Returns:
            Dict with: tier_model, recipes, agent_table,
                       governance_triggers, common_patterns
        """
        return {
            "tier_model": [
                "Tier 1 (Commands): Operator types /command in chat",
                "Tier 2 (Skills+Agents): Agent uses Skill() or Task()",
                "Tier 3 (Recipes): Internal — called by Tier 1/2 only",
                "Rule: Agent MUST NOT run `just X` directly",
            ],
            "recipes": self._extract_recipe_availability(),
            "agent_table": self._extract_agent_table(),
            "governance_triggers": self._extract_governance_triggers(),
            "common_patterns": COMMON_PATTERNS,
            "memory_schema": MEMORY_SCHEMA_HINTS,
        }

    def format(self, extracted: Dict[str, Any]) -> str:
        """
        Format extracted operations data for context injection.

        Args:
            extracted: Dict from extract()

        Returns:
            Formatted string ready for context injection (~40-60 lines).
        """
        lines = ["=== OPERATIONS ==="]

        # Tier model
        lines.append("\nEntry Point Tiers (ADR-045):")
        for t in extracted["tier_model"]:
            lines.append(f"  {t}")

        # Recipe catalogue
        lines.append("\nAvailable Recipes (Tier 3 — call via skills, not directly):")
        for category, recipes in extracted["recipes"].items():
            lines.append(f"  {category}: {', '.join(recipes)}")

        # Agent table
        lines.append("\nAgents:")
        for line in extracted["agent_table"]:
            lines.append(f"  {line}")

        # Governance triggers
        if extracted["governance_triggers"]:
            lines.append("\nGovernance Triggers (MUST):")
            for t in extracted["governance_triggers"]:
                lines.append(f"  {t}")

        # Common patterns
        lines.append("\nCommon Patterns:")
        for p in extracted["common_patterns"]:
            lines.append(f"  {p}")

        # Memory schema hints (WORK-232)
        schema = extracted.get("memory_schema", {})
        if schema:
            lines.append("\nMemory DB Schema (haios_memory.db):")
            for table, info in schema.items():
                cols = ", ".join(info["columns"])
                lines.append(f"  {table}: {cols}")
                if info.get("note"):
                    lines.append(f"  NOTE: {info['note']}")

        return "\n".join(lines)

    def load(self) -> str:
        """
        Extract and format operational context in one call.

        Returns:
            Injection-ready string (~40-60 lines).
        """
        return self.format(self.extract())


# CLI entry point for `just operations-context`
if __name__ == "__main__":
    loader = OperationsLoader()
    print(loader.load())
