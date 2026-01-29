# generated: 2026-01-04
# System Auto: last updated on: 2026-01-22T22:27:35
"""
Tests for ContextLoader Module (E2-254)

TDD approach: Tests written before implementation.
"""
import json
import sys
from pathlib import Path
from unittest.mock import Mock, patch
import pytest

# Add modules path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "modules"))


class TestComputeSessionNumber:
    """Tests for compute_session_number method."""

    def test_compute_session_number_returns_tuple(self, tmp_path):
        """compute_session_number returns (current, prior) from status."""
        from context_loader import ContextLoader

        # Create mock status file
        status_path = tmp_path / ".claude" / "haios-status.json"
        status_path.parent.mkdir(parents=True)
        status_path.write_text(json.dumps({"last_session": 165}))

        loader = ContextLoader(project_root=tmp_path)
        loader.STATUS_PATH = Path(".claude/haios-status.json")

        current, prior = loader.compute_session_number()

        assert isinstance(current, int)
        assert current == 166  # last_session + 1
        assert prior == 165

    def test_compute_session_number_missing_file(self, tmp_path):
        """compute_session_number returns (1, None) when status missing."""
        from context_loader import ContextLoader

        loader = ContextLoader(project_root=tmp_path)
        current, prior = loader.compute_session_number()

        assert current == 1
        assert prior is None

    def test_compute_session_number_zero_session(self, tmp_path):
        """compute_session_number handles zero session (first run)."""
        from context_loader import ContextLoader

        status_path = tmp_path / ".claude" / "haios-status.json"
        status_path.parent.mkdir(parents=True)
        status_path.write_text(json.dumps({"last_session": 0}))

        loader = ContextLoader(project_root=tmp_path)
        loader.STATUS_PATH = Path(".claude/haios-status.json")

        current, prior = loader.compute_session_number()

        assert current == 1
        assert prior is None  # 0 means no prior session


class TestGroundedContext:
    """Tests for GroundedContext dataclass."""

    def test_grounded_context_has_required_fields(self):
        """GroundedContext dataclass has all L0-L4 fields."""
        from context_loader import GroundedContext
        import dataclasses

        fields = {f.name for f in dataclasses.fields(GroundedContext)}
        required = {
            "session_number",
            "prior_session",
            "l0_telos",
            "l1_principal",
            "l2_intent",
            "l3_requirements",
            "l4_implementation",
            "checkpoint_summary",
            "strategies",
            "ready_work",
        }
        assert required <= fields

    def test_grounded_context_defaults(self):
        """GroundedContext has sensible defaults."""
        from context_loader import GroundedContext

        ctx = GroundedContext(session_number=1)

        assert ctx.session_number == 1
        assert ctx.prior_session is None
        assert ctx.l0_telos == ""
        assert ctx.l1_principal == ""
        assert ctx.strategies == []
        assert ctx.ready_work == []


class TestLoadContext:
    """Tests for load_context method."""

    def test_load_context_returns_grounded_context(self, tmp_path):
        """load_context returns GroundedContext with all L0-L4 fields."""
        from context_loader import ContextLoader, GroundedContext

        # Set up directory structure
        manifesto_dir = tmp_path / ".claude" / "haios" / "manifesto"
        manifesto_dir.mkdir(parents=True)
        (manifesto_dir / "L0-telos.md").write_text("# L0 Telos Content")
        (manifesto_dir / "L1-principal.md").write_text("# L1 Principal")
        (manifesto_dir / "L2-intent.md").write_text("# L2 Intent")
        (manifesto_dir / "L3-requirements.md").write_text("# L3 Requirements")
        (manifesto_dir / "L4-implementation.md").write_text("# L4 Implementation")

        status_path = tmp_path / ".claude" / "haios-status.json"
        status_path.write_text(json.dumps({"last_session": 10}))

        checkpoint_dir = tmp_path / "docs" / "checkpoints"
        checkpoint_dir.mkdir(parents=True)
        (checkpoint_dir / "2026-01-04-checkpoint.md").write_text("# Checkpoint")

        loader = ContextLoader(project_root=tmp_path)

        ctx = loader.load_context()

        assert isinstance(ctx, GroundedContext)
        assert ctx.session_number == 11
        assert ctx.l0_telos == "# L0 Telos Content"
        assert ctx.l1_principal == "# L1 Principal"

    def test_load_context_calls_work_engine(self):
        """load_context gets ready work from WorkEngine."""
        from context_loader import ContextLoader

        # Create mock WorkEngine
        mock_work = Mock()
        mock_work.id = "E2-254"
        mock_engine = Mock()
        mock_engine.get_ready.return_value = [mock_work]

        loader = ContextLoader(work_engine=mock_engine)

        # Mock file reads to prevent errors
        with patch.object(loader, "_read_manifesto_file", return_value=""):
            with patch.object(loader, "_get_latest_checkpoint", return_value=""):
                with patch.object(loader, "compute_session_number", return_value=(1, None)):
                    ctx = loader.load_context()

        mock_engine.get_ready.assert_called_once()
        assert "E2-254" in ctx.ready_work

    def test_load_context_calls_memory_bridge(self):
        """load_context gets strategies from MemoryBridge."""
        from context_loader import ContextLoader

        # Create mock MemoryBridge
        mock_result = Mock()
        mock_result.concepts = [{"id": 1, "content": "strategy"}]
        mock_bridge = Mock()
        mock_bridge.query.return_value = mock_result

        loader = ContextLoader(memory_bridge=mock_bridge)

        # Mock file reads to prevent errors
        with patch.object(loader, "_read_manifesto_file", return_value=""):
            with patch.object(loader, "_get_latest_checkpoint", return_value=""):
                with patch.object(loader, "compute_session_number", return_value=(1, None)):
                    ctx = loader.load_context()

        mock_bridge.query.assert_called()
        assert len(ctx.strategies) == 1

    def test_load_context_graceful_without_dependencies(self, tmp_path):
        """load_context works without WorkEngine or MemoryBridge."""
        from context_loader import ContextLoader

        # Set up minimal structure
        manifesto_dir = tmp_path / ".claude" / "haios" / "manifesto"
        manifesto_dir.mkdir(parents=True)
        for level in ["L0-telos", "L1-principal", "L2-intent", "L3-requirements", "L4-implementation"]:
            (manifesto_dir / f"{level}.md").write_text(f"# {level}")

        status_path = tmp_path / ".claude" / "haios-status.json"
        status_path.write_text(json.dumps({"last_session": 5}))

        loader = ContextLoader(project_root=tmp_path)  # No work_engine or memory_bridge

        ctx = loader.load_context()

        assert ctx.session_number == 6
        assert ctx.strategies == []
        assert ctx.ready_work == []


class TestCLIIntegration:
    """Tests for CLI command integration."""

    def test_cli_coldstart_command_exists(self):
        """CLI module has cmd_coldstart function."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "modules"))

        from cli import cmd_context_load

        assert callable(cmd_context_load)

    def test_cli_coldstart_runs(self, tmp_path, capsys):
        """CLI coldstart command runs and produces output."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "modules"))

        from cli import cmd_context_load

        # Set up minimal structure
        manifesto_dir = tmp_path / ".claude" / "haios" / "manifesto"
        manifesto_dir.mkdir(parents=True)
        for level in ["L0-telos", "L1-principal", "L2-intent", "L3-requirements", "L4-implementation"]:
            (manifesto_dir / f"{level}.md").write_text(f"# {level}")

        status_path = tmp_path / ".claude" / "haios-status.json"
        status_path.write_text(json.dumps({"last_session": 5}))

        # Run with project_root override
        result = cmd_context_load(project_root=tmp_path)

        assert result == 0


class TestRoleBasedLoading:
    """Tests for role-based config-driven loading (WORK-008)."""

    def test_load_context_accepts_role(self, tmp_path):
        """load_context() accepts role parameter."""
        from context_loader import ContextLoader

        # Set up minimal config with context.roles
        config_dir = tmp_path / ".claude" / "haios" / "config"
        config_dir.mkdir(parents=True)
        (config_dir / "haios.yaml").write_text("""
context:
  roles:
    main:
      loaders: []
      description: "Test role"
""")

        # Set up manifesto for fallback
        manifesto_dir = tmp_path / ".claude" / "haios" / "manifesto"
        manifesto_dir.mkdir(parents=True)
        for level in ["L0-telos", "L1-principal", "L2-intent", "L3-requirements", "L4-implementation"]:
            (manifesto_dir / f"{level}.md").write_text(f"# {level}")

        status_path = tmp_path / ".claude" / "haios-status.json"
        status_path.write_text(json.dumps({"last_session": 1}))

        loader = ContextLoader(project_root=tmp_path)
        ctx = loader.load_context(role="main")

        assert ctx is not None
        assert ctx.role == "main"

    def test_config_has_role_loader_mapping(self):
        """haios.yaml has context.roles section."""
        import yaml

        config_path = Path(__file__).parent.parent / ".claude" / "haios" / "config" / "haios.yaml"
        with open(config_path) as f:
            config = yaml.safe_load(f)

        assert "context" in config
        assert "roles" in config["context"]
        assert "main" in config["context"]["roles"]

    def test_main_role_loads_identity(self):
        """Role 'main' loads identity context from real project."""
        from context_loader import ContextLoader

        # Use real project root where IdentityLoader exists
        project_root = Path(__file__).parent.parent
        loader = ContextLoader(project_root=project_root)
        ctx = loader.load_context(role="main")

        assert "identity" in ctx.loaded_context
        # Content should be from identity loader (contains IDENTITY header or Mission)
        assert "IDENTITY" in ctx.loaded_context["identity"] or "Mission" in ctx.loaded_context["identity"]

    def test_unknown_role_raises(self):
        """Unknown role raises ValueError."""
        from context_loader import ContextLoader

        # Use real project root where config exists
        project_root = Path(__file__).parent.parent
        loader = ContextLoader(project_root=project_root)

        with pytest.raises(ValueError):
            loader.load_context(role="nonexistent_role")

    def test_loader_registry_extensible(self):
        """New loaders can be added to registry."""
        from context_loader import ContextLoader

        # Use real project root where IdentityLoader exists
        project_root = Path(__file__).parent.parent
        loader = ContextLoader(project_root=project_root)

        # Should have identity loader registered
        assert hasattr(loader, "_loader_registry")
        assert "identity" in loader._loader_registry


class TestCLIContextLoadIdentityOutput:
    """Tests for CLI context-load outputting identity content (WORK-009)."""

    def test_context_load_returns_zero_with_valid_config(self, tmp_path):
        """context-load command returns 0 when config is valid."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "modules"))

        from cli import cmd_context_load

        # Set up config with identity loader
        config_dir = tmp_path / ".claude" / "haios" / "config"
        config_dir.mkdir(parents=True)
        (config_dir / "haios.yaml").write_text("""
context:
  roles:
    main:
      loaders: []
      description: "Main agent role"
""")

        # Set up manifesto
        manifesto_dir = tmp_path / ".claude" / "haios" / "manifesto"
        manifesto_dir.mkdir(parents=True)
        for level in ["L0-telos", "L1-principal", "L2-intent", "L3-requirements", "L4-implementation"]:
            (manifesto_dir / f"{level}.md").write_text(f"# {level}")

        status_path = tmp_path / ".claude" / "haios-status.json"
        status_path.write_text('{"last_session": 227}')

        # Run CLI command - just verify it returns 0
        result = cmd_context_load(project_root=tmp_path, role="main")

        assert result == 0

    def test_context_load_accepts_role_parameter(self, tmp_path):
        """context-load accepts role parameter without error."""
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "modules"))

        from cli import cmd_context_load

        # Minimal setup
        config_dir = tmp_path / ".claude" / "haios" / "config"
        config_dir.mkdir(parents=True)
        (config_dir / "haios.yaml").write_text("""
context:
  roles:
    main:
      loaders: []
    builder:
      loaders: []
""")

        manifesto_dir = tmp_path / ".claude" / "haios" / "manifesto"
        manifesto_dir.mkdir(parents=True)
        for level in ["L0-telos", "L1-principal", "L2-intent", "L3-requirements", "L4-implementation"]:
            (manifesto_dir / f"{level}.md").write_text(f"# {level}")

        status_path = tmp_path / ".claude" / "haios-status.json"
        status_path.write_text('{"last_session": 227}')

        # Test both roles work
        result_main = cmd_context_load(project_root=tmp_path, role="main")
        result_builder = cmd_context_load(project_root=tmp_path, role="builder")

        assert result_main == 0
        assert result_builder == 0


class TestGenerateStatus:
    """Tests for generate_status method (E2-259)."""

    def test_generate_status_returns_dict(self):
        """generate_status returns a dict with expected keys."""
        from context_loader import ContextLoader

        loader = ContextLoader()
        result = loader.generate_status()

        assert isinstance(result, dict)
        assert "generated" in result
        assert "milestone" in result

    def test_generate_status_slim_default(self):
        """generate_status defaults to slim status."""
        from context_loader import ContextLoader

        loader = ContextLoader()
        result = loader.generate_status()  # No slim arg

        # Slim status has infrastructure but NOT live_files
        assert "infrastructure" in result
        assert "live_files" not in result

    def test_generate_status_full_mode(self):
        """generate_status(slim=False) returns full status."""
        from context_loader import ContextLoader

        loader = ContextLoader()
        result = loader.generate_status(slim=False)

        # Full status has live_files
        assert "live_files" in result
