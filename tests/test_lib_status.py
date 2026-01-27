# generated: 2025-12-21
# System Auto: last updated on: 2026-01-27T20:58:34
"""Tests for .claude/haios/lib/status.py - Core status module.

TDD tests for E2-120 Phase 2a (CORE functions only).
Full status tests deferred to E2-125.

Core functions (8):
1. get_agents() - Discover agents from .claude/agents/
2. get_commands() - Discover commands from .claude/commands/
3. get_skills() - Discover skills from .claude/skills/
4. get_memory_stats() - Get concept/entity counts from database
5. get_backlog_stats() - Parse backlog.md for active counts
6. get_session_delta() - Compare last 2 checkpoints for momentum
7. get_milestone_progress() - Calculate milestone completion %
8. get_blocked_items() - Detect blocked_by dependencies
9. generate_slim_status() - Main orchestrator
"""

import sys
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock

import pytest

# Add .claude/haios/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))


class TestGetAgents:
    """Tests for get_agents() function."""

    def test_discovers_agents_from_directory(self):
        """Should find all agent .md files in .claude/agents/."""
        from status import get_agents

        agents = get_agents()

        # Known agents from haios-status-slim.json
        assert "preflight-checker" in agents
        assert "schema-verifier" in agents
        assert "test-runner" in agents
        assert "why-capturer" in agents

    def test_excludes_readme(self):
        """Should not include README.md as an agent."""
        from status import get_agents

        agents = get_agents()

        assert "README" not in agents
        assert "readme" not in agents

    def test_returns_sorted_list(self):
        """Should return agents in sorted order."""
        from status import get_agents

        agents = get_agents()

        assert agents == sorted(agents)


class TestGetCommands:
    """Tests for get_commands() function."""

    def test_discovers_commands_from_directory(self):
        """Should find all command .md files in .claude/commands/."""
        from status import get_commands

        commands = get_commands()

        # Known commands
        assert "/coldstart" in commands
        assert "/close" in commands
        assert "/validate" in commands
        assert "/new-checkpoint" in commands

    def test_commands_prefixed_with_slash(self):
        """All commands should be prefixed with /."""
        from status import get_commands

        commands = get_commands()

        for cmd in commands:
            assert cmd.startswith("/"), f"Command {cmd} should start with /"

    def test_excludes_readme(self):
        """Should not include README.md as a command."""
        from status import get_commands

        commands = get_commands()

        assert "/README" not in commands

    def test_returns_sorted_list(self):
        """Should return commands in sorted order."""
        from status import get_commands

        commands = get_commands()

        assert commands == sorted(commands)


class TestGetSkills:
    """Tests for get_skills() function."""

    def test_discovers_skills_from_directory(self):
        """Should find all skills with SKILL.md in .claude/skills/."""
        from status import get_skills

        skills = get_skills()

        # Known skills
        assert "extract-content" in skills
        assert "implementation-cycle" in skills
        assert "memory-agent" in skills
        assert "schema-ref" in skills

    def test_returns_sorted_list(self):
        """Should return skills in sorted order."""
        from status import get_skills

        skills = get_skills()

        assert skills == sorted(skills)


class TestGetMemoryStats:
    """Tests for get_memory_stats() function."""

    def test_returns_concept_count(self):
        """Should return concept count from database."""
        from status import get_memory_stats

        stats = get_memory_stats()

        assert "concepts" in stats
        assert isinstance(stats["concepts"], int)
        assert stats["concepts"] > 0  # Should have some concepts

    def test_returns_entity_count(self):
        """Should return entity count from database."""
        from status import get_memory_stats

        stats = get_memory_stats()

        assert "entities" in stats
        assert isinstance(stats["entities"], int)

    def test_handles_missing_database(self, tmp_path):
        """Should return None or empty dict if database unavailable."""
        from status import get_memory_stats, PROJECT_ROOT
        import status

        # Temporarily point to non-existent database
        original_root = status.PROJECT_ROOT
        status.PROJECT_ROOT = tmp_path  # No haios_memory.db here

        try:
            stats = get_memory_stats()
            # Should handle gracefully
            assert stats is None or stats == {}
        finally:
            status.PROJECT_ROOT = original_root


class TestGetBacklogStats:
    """Tests for get_backlog_stats() function."""

    def test_returns_active_count(self):
        """Should return count of active (non-closed) items."""
        from status import get_backlog_stats

        stats = get_backlog_stats()

        assert "active_count" in stats
        assert isinstance(stats["active_count"], int)

    def test_returns_priority_breakdown(self):
        """Should return counts by priority level."""
        from status import get_backlog_stats

        stats = get_backlog_stats()

        assert "by_priority" in stats
        priorities = stats["by_priority"]
        assert "urgent" in priorities
        assert "high" in priorities
        assert "medium" in priorities
        assert "low" in priorities

    def test_returns_last_session(self):
        """Should return highest session number mentioned."""
        from status import get_backlog_stats

        stats = get_backlog_stats()

        assert "last_session" in stats
        assert isinstance(stats["last_session"], int)
        # backlog.md was archived - now work files are source of truth
        # This function returns 0 when backlog doesn't exist
        assert stats["last_session"] >= 0


class TestGetSessionDelta:
    """Tests for get_session_delta() function."""

    def test_returns_prior_and_current_session(self):
        """Should identify prior and current session numbers."""
        from status import get_session_delta

        delta = get_session_delta()

        assert "prior_session" in delta
        assert "current_session" in delta
        # Current should be >= prior
        if delta["prior_session"] and delta["current_session"]:
            assert delta["current_session"] >= delta["prior_session"]

    def test_returns_completed_items(self):
        """Should list items completed since prior session."""
        from status import get_session_delta

        delta = get_session_delta()

        assert "completed" in delta
        assert isinstance(delta["completed"], list)
        assert "completed_count" in delta

    def test_returns_added_items(self):
        """Should list items added since prior session."""
        from status import get_session_delta

        delta = get_session_delta()

        assert "added" in delta
        assert isinstance(delta["added"], list)
        assert "added_count" in delta


class TestGetMilestoneProgress:
    """Tests for get_milestone_progress() function."""

    def test_returns_milestone_with_progress(self):
        """Should return milestone info with progress percentage."""
        from status import get_milestone_progress

        # Need to provide existing milestones
        existing = {
            "M4-Research": {
                "name": "Investigation Infrastructure",
                "items": ["E2-100", "E2-101", "E2-102"],
                "complete": ["E2-102"],
                "progress": 33
            }
        }

        result = get_milestone_progress(existing)

        assert "M4-Research" in result
        milestone = result["M4-Research"]
        assert "name" in milestone
        assert "progress" in milestone
        assert isinstance(milestone["progress"], int)
        assert 0 <= milestone["progress"] <= 100


class TestGetBlockedItems:
    """Tests for get_blocked_items() function."""

    def test_returns_list_of_blocked_items(self):
        """Should return list of items with unresolved blockers."""
        from status import get_blocked_items

        blocked = get_blocked_items()

        assert isinstance(blocked, list)
        # Each blocked item should have id and blocked_by
        for item in blocked:
            assert "id" in item
            assert "blocked_by" in item

    def test_excludes_resolved_blockers(self):
        """Should not include items whose blockers are complete."""
        from status import get_blocked_items

        blocked = get_blocked_items()

        # Blocked items should only have unresolved blockers
        for item in blocked:
            assert len(item["blocked_by"]) > 0


class TestGenerateSlimStatus:
    """Tests for generate_slim_status() function."""

    def test_generates_valid_json_structure(self):
        """Should generate valid JSON with expected top-level keys."""
        from status import generate_slim_status

        slim = generate_slim_status()

        # Required top-level keys
        assert "generated" in slim
        assert "milestone" in slim
        assert "session_delta" in slim
        assert "active_work" in slim
        assert "counts" in slim
        assert "infrastructure" in slim

    def test_session_state_in_slim_status(self):
        """E2-286: Verify generate_slim_status() includes session_state section."""
        from status import generate_slim_status

        slim = generate_slim_status()

        assert "session_state" in slim
        assert isinstance(slim["session_state"], dict)
        # Verify all required fields present
        assert "active_cycle" in slim["session_state"]
        assert "current_phase" in slim["session_state"]
        assert "work_id" in slim["session_state"]
        assert "entered_at" in slim["session_state"]

    def test_session_state_default_values(self):
        """E2-286: Verify session_state fields default to None when no cycle active."""
        from status import generate_slim_status

        slim = generate_slim_status()

        # Default state: no active cycle
        assert slim["session_state"]["active_cycle"] is None
        assert slim["session_state"]["current_phase"] is None
        assert slim["session_state"]["work_id"] is None
        assert slim["session_state"]["entered_at"] is None

    def test_existing_fields_unchanged(self):
        """E2-286: Verify existing slim status fields are not affected."""
        from status import generate_slim_status

        slim = generate_slim_status()

        # All existing top-level keys must be present
        assert "generated" in slim
        assert "milestone" in slim
        assert "session_delta" in slim
        assert "work_cycle" in slim
        assert "active_work" in slim
        assert "blocked_items" in slim
        assert "counts" in slim
        assert "infrastructure" in slim

    def test_infrastructure_has_all_sections(self):
        """Infrastructure should include commands, skills, agents, mcps."""
        from status import generate_slim_status

        slim = generate_slim_status()
        infra = slim["infrastructure"]

        assert "commands" in infra
        assert "skills" in infra
        assert "agents" in infra
        assert "mcps" in infra

    def test_counts_section_structure(self):
        """Counts should include concepts, entities, backlog_pending."""
        from status import generate_slim_status

        slim = generate_slim_status()
        counts = slim["counts"]

        assert "concepts" in counts
        assert "entities" in counts
        assert "backlog_pending" in counts

    def test_output_matches_existing_slim_format(self):
        """Output should match format of existing haios-status-slim.json."""
        from status import generate_slim_status

        slim = generate_slim_status()

        # Compare with actual file
        slim_path = Path(".claude/haios-status-slim.json")
        if slim_path.exists():
            # Read with utf-8-sig to handle BOM
            with open(slim_path, encoding="utf-8-sig") as f:
                existing = json.load(f)

            # Same top-level keys
            assert set(slim.keys()) == set(existing.keys())


class TestWriteSlimStatus:
    """Tests for write_slim_status() function."""

    def test_writes_valid_json_file(self, tmp_path):
        """Should write valid JSON to specified path."""
        from status import generate_slim_status, write_slim_status

        output_path = tmp_path / "test-slim.json"

        slim = generate_slim_status()
        write_slim_status(slim, str(output_path))

        assert output_path.exists()

        # Should be valid JSON
        with open(output_path) as f:
            loaded = json.load(f)

        assert loaded == slim


class TestIntegration:
    """Integration tests for status module."""

    def test_full_status_generation_flow(self):
        """Full flow: gather data -> generate slim -> verify structure."""
        from status import generate_slim_status

        slim = generate_slim_status()

        # Verify complete structure
        assert slim["generated"]
        assert slim["infrastructure"]["commands"]
        assert slim["infrastructure"]["skills"]
        assert slim["infrastructure"]["agents"]
        assert len(slim["infrastructure"]["mcps"]) >= 1

    def test_status_generation_performance(self):
        """Status generation should complete within reasonable time."""
        import time
        from status import generate_slim_status

        start = time.time()
        slim = generate_slim_status()
        elapsed = time.time() - start

        # Should complete in under 5 seconds
        assert elapsed < 5.0, f"Status generation took {elapsed:.2f}s"


class TestFullStatusModule:
    """Tests for E2-125: Full status module (8 deferred functions)."""

    def test_get_valid_templates_returns_list(self):
        """Should return list of template definitions from validate.py registry."""
        from status import get_valid_templates

        templates = get_valid_templates()

        assert isinstance(templates, list)
        assert len(templates) >= 7  # checkpoint, plan, adr, investigation, report, readme, backlog_item
        # Each template should have name and required_fields
        for t in templates:
            assert "name" in t
            assert "required_fields" in t

    def test_get_live_files_finds_checkpoints(self):
        """Should scan governed paths and find checkpoint files."""
        from status import get_live_files

        files = get_live_files()

        assert isinstance(files, list)
        assert len(files) > 0
        # Should find at least one checkpoint
        checkpoint_files = [f for f in files if "checkpoints" in f.get("path", "")]
        assert len(checkpoint_files) > 0
        # Each file should have path, template, status
        for f in files[:5]:  # Check first 5
            assert "path" in f
            assert "template" in f or f.get("template") is None

    def test_get_outstanding_items_finds_pending(self):
        """Should find items with status != complete/closed."""
        from status import get_outstanding_items

        items = get_outstanding_items()

        assert isinstance(items, list)
        # Each item should have id and status
        for item in items[:5]:  # Check first 5
            assert "id" in item or "path" in item
            assert "status" in item

    def test_get_stale_items_has_threshold(self):
        """Should detect files not updated within threshold days."""
        from status import get_stale_items

        items = get_stale_items(days=30)

        assert isinstance(items, list)
        # Each stale item should have path and last_updated
        for item in items[:5]:  # Check first 5
            assert "path" in item
            assert "last_updated" in item or "days_stale" in item

    def test_get_workspace_summary_structure(self):
        """Should aggregate counts by template type and status."""
        from status import get_workspace_summary

        summary = get_workspace_summary()

        assert isinstance(summary, dict)
        assert "total_files" in summary
        assert "by_template" in summary
        assert isinstance(summary["by_template"], dict)

    def test_check_alignment_returns_mapping(self):
        """Should match files to backlog items and detect orphans."""
        from status import check_alignment

        alignment = check_alignment()

        assert isinstance(alignment, dict)
        # Should have aligned, orphan_files, missing_files
        assert "aligned" in alignment or "orphan_files" in alignment

    def test_get_spawn_map_structure(self):
        """Should track spawned_by relationships from frontmatter."""
        from status import get_spawn_map

        spawn_map = get_spawn_map()

        assert isinstance(spawn_map, dict)
        # E2-120 spawned E2-125, E2-126
        if "E2-120" in spawn_map:
            assert "E2-125" in spawn_map["E2-120"] or "E2-126" in spawn_map["E2-120"]

    def test_generate_full_status_includes_all_sections(self):
        """Should orchestrate all functions into complete status dict."""
        from status import generate_full_status

        full = generate_full_status()

        assert isinstance(full, dict)
        # Should have all sections from full status
        assert "templates" in full or "valid_templates" in full
        assert "live_files" in full
        assert "workspace" in full or "workspace_summary" in full


class TestMilestoneAutoDiscovery:
    """Tests for E2-117: Milestone auto-discovery."""

    def test_format_milestone_name(self):
        """Converts M6-WorkCycle to 'WorkCycle' for display."""
        from status import _format_milestone_name

        assert _format_milestone_name("M6-WorkCycle") == "WorkCycle"
        assert _format_milestone_name("M7-NewFeature") == "NewFeature"
        assert _format_milestone_name("M2-Governance") == "Governance"

    def test_format_milestone_name_no_dash(self):
        """Handles keys without dash."""
        from status import _format_milestone_name

        assert _format_milestone_name("M6") == "M6"

    def test_discover_milestones_finds_real_milestones(self):
        """Auto-discovers milestones from merged sources (backlog + work files)."""
        from status import _load_existing_milestones

        milestones = _load_existing_milestones()

        # Should find M7d-Plumbing from work files
        assert "M7d-Plumbing" in milestones
        assert milestones["M7d-Plumbing"]["name"] == "Plumbing"

    def test_discover_milestones_returns_empty_for_missing_backlog(self, tmp_path, monkeypatch):
        """Returns empty dict if backlog doesn't exist and no work files."""
        import status
        monkeypatch.setattr(status, "PROJECT_ROOT", tmp_path)

        milestones = status._discover_milestones_from_backlog()

        assert milestones == {}

    def test_discover_milestones_deduplicates(self):
        """Same milestone referenced multiple times is only in dict once."""
        from status import _load_existing_milestones

        milestones = _load_existing_milestones()

        # Each key should appear exactly once (tests merged result)
        key_count = sum(1 for k in milestones.keys() if k == "M7d-Plumbing")
        assert key_count == 1


class TestWorkFileMilestoneDiscovery:
    """Tests for E2-173: Work file milestone discovery."""

    def test_discover_milestones_from_work_files_basic(self, tmp_path, monkeypatch):
        """Should discover milestones from work file YAML frontmatter."""
        import status
        monkeypatch.setattr(status, "PROJECT_ROOT", tmp_path)

        # Setup: create mock work file with milestone field
        active_dir = tmp_path / "docs" / "work" / "active"
        active_dir.mkdir(parents=True)
        (active_dir / "WORK-E2-001-test.md").write_text(
            "---\nmilestone: M7a-Recipes\nid: E2-001\nstatus: active\n---\n# Test"
        )

        result = status._discover_milestones_from_work_files()

        assert "M7a-Recipes" in result
        assert "E2-001" in result["M7a-Recipes"]["items"]
        assert result["M7a-Recipes"]["name"] == "Recipes"

    def test_discover_milestones_from_work_files_complete_status(self, tmp_path, monkeypatch):
        """Should track complete items based on status field."""
        import status
        monkeypatch.setattr(status, "PROJECT_ROOT", tmp_path)

        # Setup: create complete work file in archive
        archive_dir = tmp_path / "docs" / "work" / "archive"
        archive_dir.mkdir(parents=True)
        (archive_dir / "WORK-E2-002-done.md").write_text(
            "---\nmilestone: M7a-Recipes\nid: E2-002\nstatus: complete\n---\n# Done"
        )

        result = status._discover_milestones_from_work_files()

        assert "M7a-Recipes" in result
        assert "E2-002" in result["M7a-Recipes"]["items"]
        assert "E2-002" in result["M7a-Recipes"]["complete"]
        assert result["M7a-Recipes"]["progress"] == 100

    def test_discover_milestones_from_work_files_skips_null_milestone(self, tmp_path, monkeypatch):
        """Should skip work files with null or missing milestone."""
        import status
        monkeypatch.setattr(status, "PROJECT_ROOT", tmp_path)

        active_dir = tmp_path / "docs" / "work" / "active"
        active_dir.mkdir(parents=True)
        (active_dir / "WORK-E2-003-no-ms.md").write_text(
            "---\nmilestone: null\nid: E2-003\nstatus: active\n---\n# No milestone"
        )

        result = status._discover_milestones_from_work_files()

        assert len(result) == 0

    def test_load_existing_milestones_merges_sources(self, tmp_path, monkeypatch):
        """Should merge work file milestones with backlog milestones."""
        import status
        monkeypatch.setattr(status, "PROJECT_ROOT", tmp_path)

        # Setup: create work file with M7a milestone
        active_dir = tmp_path / "docs" / "work" / "active"
        active_dir.mkdir(parents=True)
        (active_dir / "WORK-E2-001-test.md").write_text(
            "---\nmilestone: M7a-Recipes\nid: E2-001\nstatus: active\n---\n# Test"
        )

        # Setup: create backlog.md with M4 milestone (legacy)
        backlog_dir = tmp_path / "docs" / "pm"
        backlog_dir.mkdir(parents=True)
        (backlog_dir / "backlog.md").write_text(
            "### [MEDIUM] E2-099: Legacy Item\n- **Milestone:** M4-Research\n"
        )

        # Setup: plans dir (needed by _discover_milestones_from_backlog)
        (tmp_path / "docs" / "plans").mkdir(parents=True)

        result = status._load_existing_milestones()

        # Both sources should be merged
        assert "M7a-Recipes" in result  # from work files
        assert "M4-Research" in result   # from backlog

    def test_real_work_files_discover_m7_milestones(self):
        """Integration: Should discover M7 sub-milestones from real work files."""
        from status import _discover_milestones_from_work_files

        milestones = _discover_milestones_from_work_files()

        # Real work files should have M7a, M7b, M7c, M7d, M7e assignments
        m7_keys = [k for k in milestones.keys() if k.startswith("M7")]
        assert len(m7_keys) > 0, "Should discover at least one M7 sub-milestone from work files"
