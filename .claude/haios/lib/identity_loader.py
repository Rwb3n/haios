# generated: 2026-01-21
# System Auto: last updated on: 2026-01-21T23:02:26
"""
Identity Loader for Configuration Arc.

WORK-007: Implements CH-004 Identity Loader
First runtime consumer of loader.py base (E2-250 requirement).

Extracts ~50 lines of identity context from manifesto files (L0-L3)
for token-efficient coldstart loading. Reduces 1137 lines to ~50 lines.

Usage:
    from identity_loader import IdentityLoader

    loader = IdentityLoader()
    identity = loader.load()  # Returns ~50 lines of identity context

    # Or step by step:
    extracted = loader.extract()  # Dict with mission, principles, etc.
    formatted = loader.format(extracted)  # Formatted string

Extracted Content:
    - Mission: Prime directive from L0-telos.md
    - Companion: Relationship principles from L0-telos.md
    - Constraints: Known constraints from L1-principal.md
    - Principles: Core behavioral principles from L3-requirements.md
    - Epoch: Current epoch name from EPOCH.md frontmatter
"""
from pathlib import Path
from typing import Dict, Any, Optional

# Path setup (same pattern as config.py)
CONFIG_DIR = Path(__file__).parent.parent / "config" / "loaders"
DEFAULT_CONFIG = CONFIG_DIR / "identity.yaml"

# Import base Loader (same pattern as sibling modules)
from loader import Loader


class IdentityLoader:
    """
    Extract identity context from manifesto files.

    Uses base Loader with identity.yaml config to extract:
    - Mission (prime directive from L0)
    - Companion relationship (from L0)
    - Constraints (from L1)
    - Principles (from L3)
    - Epoch context

    This is the first runtime consumer of loader.py (E2-250 requirement).
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize with config file.

        Args:
            config_path: Path to identity.yaml. Default: standard location.

        Raises:
            FileNotFoundError: If config file not found.
        """
        self.config_path = config_path or DEFAULT_CONFIG
        self._loader = Loader(self.config_path)

    @property
    def config(self) -> Dict[str, Any]:
        """Access underlying config for inspection."""
        return self._loader.config

    def extract(self) -> Dict[str, Any]:
        """
        Extract identity components from manifesto files.

        Returns:
            Dict with keys: mission, companion, constraints, principles, epoch_name
        """
        return self._loader.extract()

    def format(self, extracted: Dict[str, Any]) -> str:
        """
        Format extracted identity for injection.

        Args:
            extracted: Dict from extract()

        Returns:
            Formatted string ready for context injection.
        """
        return self._loader.format(extracted)

    def load(self) -> str:
        """
        Extract and format identity context in one call.

        Returns:
            Formatted string ~50 lines ready for context injection.
        """
        return self._loader.load()


# CLI entry point for `just identity`
if __name__ == "__main__":
    loader = IdentityLoader()
    print(loader.load())
