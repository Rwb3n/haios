# generated: 2026-01-05
# System Auto: last updated on: 2026-01-05T20:03:07
"""Tests for HAIOS plugin manifest.yaml (E2-269)."""

from pathlib import Path

import pytest
import yaml


class TestManifest:
    """Test suite for .claude/haios/manifest.yaml."""

    @pytest.fixture
    def manifest_path(self) -> Path:
        """Return path to manifest.yaml."""
        return Path(".claude/haios/manifest.yaml")

    @pytest.fixture
    def manifest(self, manifest_path: Path) -> dict:
        """Load and return manifest as dict."""
        with open(manifest_path) as f:
            return yaml.safe_load(f)

    def test_manifest_exists_and_parses(self, manifest_path: Path, manifest: dict):
        """Verify manifest.yaml exists and is valid YAML."""
        assert manifest_path.exists(), "manifest.yaml must exist"
        assert isinstance(manifest, dict), "manifest must be a dict"
        assert "plugin" in manifest, "manifest must have 'plugin' section"
        assert "components" in manifest, "manifest must have 'components' section"

    def test_component_counts_match_file_system(self, manifest: dict):
        """Verify manifest declares correct number of components."""
        # Count actual files (excluding READMEs)
        commands = [
            f for f in Path(".claude/commands").glob("*.md") if f.name != "README.md"
        ]
        skills = list(Path(".claude/skills").glob("*/SKILL.md"))
        agents = [
            f for f in Path(".claude/agents").glob("*.md") if f.name != "README.md"
        ]

        assert len(manifest["components"]["commands"]) == len(
            commands
        ), f"Expected {len(commands)} commands, got {len(manifest['components']['commands'])}"
        assert len(manifest["components"]["skills"]) == len(
            skills
        ), f"Expected {len(skills)} skills, got {len(manifest['components']['skills'])}"
        assert len(manifest["components"]["agents"]) == len(
            agents
        ), f"Expected {len(agents)} agents, got {len(manifest['components']['agents'])}"
        assert (
            len(manifest["components"]["hooks"]) == 4
        ), f"Expected 4 hook handlers, got {len(manifest['components']['hooks'])}"

    def test_required_fields_present(self, manifest: dict):
        """Verify manifest has all required fields per SECTION-18."""
        # Plugin metadata
        assert "name" in manifest["plugin"], "plugin.name required"
        assert "version" in manifest["plugin"], "plugin.version required"
        assert "description" in manifest["plugin"], "plugin.description required"

        # Targets
        assert "targets" in manifest, "targets section required"
        assert any(
            t["id"] == "claude" for t in manifest["targets"]
        ), "must have claude target"

        # Dependencies
        assert "dependencies" in manifest, "dependencies section required"
        assert (
            "mcp_servers" in manifest["dependencies"]
        ), "dependencies.mcp_servers required"
