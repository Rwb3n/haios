# generated: 2026-02-16
# System Auto: last updated on: 2026-02-16
"""Tests for manifest auto-sync mechanism (WORK-135)."""

from pathlib import Path

import pytest
import yaml


# Import will fail until scripts/manifest_sync.py exists (RED phase)
from scripts.manifest_sync import compute_manifest_diff, sync_manifest


class TestComputeManifestDiff:
    """Tests for compute_manifest_diff function."""

    def test_detects_missing_skill(self, tmp_path):
        """Skill on disk but not in manifest is reported as missing."""
        # Setup: skill exists on disk
        skill_dir = tmp_path / "skills" / "new-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# New Skill")
        # Setup: empty commands and agents dirs
        (tmp_path / "commands").mkdir()
        (tmp_path / "agents").mkdir()
        # Manifest has no skills
        manifest = {"components": {"skills": [], "commands": [], "agents": []}}

        diff = compute_manifest_diff(
            manifest,
            skills_dir=tmp_path / "skills",
            commands_dir=tmp_path / "commands",
            agents_dir=tmp_path / "agents",
        )

        assert "new-skill" in diff["skills"]["missing_from_manifest"]
        assert diff["skills"]["extra_in_manifest"] == []

    def test_detects_extra_manifest_entry(self, tmp_path):
        """Manifest entry with no disk counterpart is reported as extra."""
        # Setup: empty disk dirs
        (tmp_path / "skills").mkdir()
        (tmp_path / "commands").mkdir()
        (tmp_path / "agents").mkdir()
        # Manifest has a skill that doesn't exist on disk
        manifest = {
            "components": {
                "skills": [
                    {
                        "id": "ghost-skill",
                        "source": "skills/ghost-skill/",
                        "category": "utility",
                    }
                ],
                "commands": [],
                "agents": [],
            }
        }

        diff = compute_manifest_diff(
            manifest,
            skills_dir=tmp_path / "skills",
            commands_dir=tmp_path / "commands",
            agents_dir=tmp_path / "agents",
        )

        assert "ghost-skill" in diff["skills"]["extra_in_manifest"]
        assert diff["skills"]["missing_from_manifest"] == []

    def test_detects_all_component_types(self, tmp_path):
        """Diff works for commands and agents, not just skills."""
        # Setup: command on disk, agent in manifest only
        (tmp_path / "skills").mkdir()
        (tmp_path / "commands").mkdir()
        (tmp_path / "commands" / "new-cmd.md").write_text("# New Command")
        (tmp_path / "commands" / "README.md").write_text("# README")
        (tmp_path / "agents").mkdir()

        manifest = {
            "components": {
                "skills": [],
                "commands": [],
                "agents": [
                    {"id": "ghost-agent", "source": "agents/ghost-agent/", "required": False}
                ],
            }
        }

        diff = compute_manifest_diff(
            manifest,
            skills_dir=tmp_path / "skills",
            commands_dir=tmp_path / "commands",
            agents_dir=tmp_path / "agents",
        )

        assert "new-cmd" in diff["commands"]["missing_from_manifest"]
        assert "ghost-agent" in diff["agents"]["extra_in_manifest"]
        # README.md should be excluded
        assert "README" not in diff["commands"]["missing_from_manifest"]


class TestSyncManifest:
    """Tests for sync_manifest function."""

    def _write_manifest(self, path: Path, manifest: dict) -> None:
        """Helper to write a manifest YAML file."""
        with open(path, "w") as f:
            yaml.dump(manifest, f, default_flow_style=False)

    def test_sync_adds_missing_and_removes_extra(self, tmp_path):
        """sync_manifest writes updated manifest with correct entries."""
        manifest_path = tmp_path / "haios" / "manifest.yaml"
        manifest_path.parent.mkdir(parents=True)

        # Create disk structure at tmp_path level (simulating .claude/)
        skill_dir = tmp_path / "skills" / "real-skill"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# Real Skill")
        (tmp_path / "commands").mkdir()
        (tmp_path / "agents").mkdir()

        # Write manifest with ghost entry and missing real-skill
        initial_manifest = {
            "components": {
                "skills": [
                    {"id": "ghost-skill", "source": "skills/ghost-skill/", "category": "utility"}
                ],
                "commands": [],
                "agents": [],
            }
        }
        self._write_manifest(manifest_path, initial_manifest)

        # Run sync (not dry_run)
        diff = sync_manifest(manifest_path, dry_run=False)

        # Verify diff
        assert "real-skill" in diff["skills"]["missing_from_manifest"]
        assert "ghost-skill" in diff["skills"]["extra_in_manifest"]

        # Re-read manifest and verify
        with open(manifest_path) as f:
            updated = yaml.safe_load(f)
        skill_ids = {s["id"] for s in updated["components"]["skills"]}
        assert "real-skill" in skill_ids
        assert "ghost-skill" not in skill_ids

    def test_roundtrip_no_changes(self, tmp_path):
        """When manifest is in sync, round-trip preserves content."""
        manifest_path = tmp_path / "haios" / "manifest.yaml"
        manifest_path.parent.mkdir(parents=True)

        # Create matching disk and manifest
        (tmp_path / "skills").mkdir()
        (tmp_path / "commands").mkdir()
        (tmp_path / "agents").mkdir()

        initial_manifest = {
            "components": {"skills": [], "commands": [], "agents": []}
        }
        self._write_manifest(manifest_path, initial_manifest)
        original_content = manifest_path.read_text()

        # Sync should be no-op
        diff = sync_manifest(manifest_path, dry_run=False)

        assert diff["skills"]["missing_from_manifest"] == []
        assert diff["skills"]["extra_in_manifest"] == []
        # File should not have changed meaningfully
        updated = yaml.safe_load(manifest_path.read_text())
        assert updated == initial_manifest
