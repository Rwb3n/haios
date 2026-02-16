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
        """Verify manifest declares correct components with specific diff."""
        # Commands: .md files excluding README.md
        disk_commands = {
            f.stem for f in Path(".claude/commands").glob("*.md") if f.name != "README.md"
        }
        manifest_commands = {c["id"] for c in manifest["components"]["commands"]}
        missing_cmds = disk_commands - manifest_commands
        extra_cmds = manifest_commands - disk_commands
        assert not missing_cmds, f"Commands on disk but not in manifest: {missing_cmds}"
        assert not extra_cmds, f"Commands in manifest but not on disk: {extra_cmds}"

        # Skills: dirs containing SKILL.md
        disk_skills = {
            d.parent.name for d in Path(".claude/skills").glob("*/SKILL.md")
        }
        manifest_skills = {s["id"] for s in manifest["components"]["skills"]}
        missing_skills = disk_skills - manifest_skills
        extra_skills = manifest_skills - disk_skills
        assert not missing_skills, f"Skills on disk but not in manifest: {missing_skills}"
        assert not extra_skills, f"Skills in manifest but not on disk: {extra_skills}"

        # Agents: .md files excluding README.md
        disk_agents = {
            f.stem for f in Path(".claude/agents").glob("*.md") if f.name != "README.md"
        }
        manifest_agents = {a["id"] for a in manifest["components"]["agents"]}
        missing_agents = disk_agents - manifest_agents
        extra_agents = manifest_agents - disk_agents
        assert not missing_agents, f"Agents on disk but not in manifest: {missing_agents}"
        assert not extra_agents, f"Agents in manifest but not on disk: {extra_agents}"

        # Hooks: fixed count
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
