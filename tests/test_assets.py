# generated: 2026-02-15
# WORK-093: Lifecycle Asset Types (REQ-ASSET-001)
"""
Tests for Asset type hierarchy.

Tests asset base class provenance, 5 subclasses, serialization (to_dict, to_markdown),
CycleRunner integration, and backward compatibility aliases.
"""
import sys
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

# Ensure modules/ is on sys.path for imports
_modules_path = Path(__file__).parent.parent / ".claude" / "haios" / "modules"
if str(_modules_path) not in sys.path:
    sys.path.insert(0, str(_modules_path))

_lib_path = Path(__file__).parent.parent / ".claude" / "haios" / "lib"
if str(_lib_path) not in sys.path:
    sys.path.insert(0, str(_lib_path))


# =============================================================================
# Test 1: Asset base class has all provenance fields (including status)
# =============================================================================


class TestAssetBase:
    """Tests for Asset base class provenance fields."""

    def test_asset_base_has_provenance_fields(self):
        from assets import Asset

        asset = Asset(
            asset_id="asset-001",
            type="test",
            produced_by="investigation",
            source_work="WORK-093",
            version=1,
            timestamp=datetime(2026, 2, 15),
            author="Hephaestus",
        )
        assert asset.asset_id == "asset-001"
        assert asset.type == "test"
        assert asset.produced_by == "investigation"
        assert asset.source_work == "WORK-093"
        assert asset.version == 1
        assert asset.author == "Hephaestus"
        assert asset.status == "success"  # A2: default value
        assert asset.inputs == []
        assert asset.piped_from is None


# =============================================================================
# Test 2: FindingsAsset has investigation-specific fields
# =============================================================================


class TestFindingsAsset:
    """Tests for FindingsAsset subclass."""

    def test_findings_asset_fields(self):
        from assets import Asset, FindingsAsset

        fa = FindingsAsset(
            asset_id="f-001",
            type="findings",
            produced_by="investigation",
            source_work="WORK-093",
            version=1,
            timestamp=datetime(2026, 2, 15),
            author="Hephaestus",
            question="What causes X?",
            findings=["Root cause is Y"],
            conclusion="Y is the root cause",
            evidence=["log file Z"],
        )
        assert fa.question == "What causes X?"
        assert fa.findings == ["Root cause is Y"]
        assert fa.conclusion == "Y is the root cause"
        assert fa.evidence == ["log file Z"]
        assert fa.type == "findings"
        assert isinstance(fa, Asset)


# =============================================================================
# Test 3: All 5 subclasses instantiate correctly (parametrized)
# =============================================================================


class TestAssetSubclasses:
    """Tests for all 5 Asset subclasses."""

    @pytest.mark.parametrize(
        "cls_name,type_name,extra_fields",
        [
            (
                "FindingsAsset",
                "findings",
                {"question": "Q", "findings": [], "conclusion": "", "evidence": []},
            ),
            (
                "SpecificationAsset",
                "specification",
                {"requirements": [], "design_decisions": [], "interface": ""},
            ),
            (
                "ArtifactAsset",
                "artifact",
                {"files_created": [], "files_modified": [], "test_results": {}},
            ),
            (
                "VerdictAsset",
                "verdict",
                {"passed": True, "criteria_results": [], "evidence": []},
            ),
            (
                "PriorityListAsset",
                "priority_list",
                {"items": [], "rationale": ""},
            ),
        ],
    )
    def test_asset_subclass(self, cls_name, type_name, extra_fields):
        import assets

        cls = getattr(assets, cls_name)
        Asset = assets.Asset

        asset = cls(
            asset_id="test",
            type=type_name,
            produced_by="test",
            source_work="WORK-093",
            version=1,
            timestamp=datetime(2026, 2, 15),
            author="test",
            **extra_fields,
        )
        assert asset.type == type_name
        assert isinstance(asset, Asset)


# =============================================================================
# Test 4: to_dict() returns all fields with ISO timestamp
# =============================================================================


class TestAssetToDict:
    """Tests for Asset.to_dict() serialization."""

    def test_asset_to_dict(self):
        from assets import FindingsAsset

        asset = FindingsAsset(
            asset_id="f-001",
            type="findings",
            produced_by="investigation",
            source_work="WORK-093",
            version=1,
            timestamp=datetime(2026, 2, 15),
            author="Hephaestus",
            question="Q",
            findings=["A"],
            conclusion="C",
            evidence=["E"],
        )
        d = asset.to_dict()
        assert d["asset_id"] == "f-001"
        assert d["type"] == "findings"
        assert d["produced_by"] == "investigation"
        assert d["source_work"] == "WORK-093"
        assert d["version"] == 1
        assert d["author"] == "Hephaestus"
        assert d["question"] == "Q"
        assert d["findings"] == ["A"]
        assert d["timestamp"] == "2026-02-15T00:00:00"

    def test_base_asset_to_dict(self):
        from assets import Asset

        asset = Asset(
            asset_id="a-001",
            type="test",
            produced_by="test",
            source_work="WORK-001",
            version=1,
            timestamp=datetime(2026, 2, 15),
            author="test",
        )
        d = asset.to_dict()
        assert d["asset_id"] == "a-001"
        assert d["status"] == "success"
        assert d["inputs"] == []
        assert d["piped_from"] is None


# =============================================================================
# Test 5: to_markdown() produces valid frontmatter + body
# =============================================================================


class TestAssetToMarkdown:
    """Tests for Asset.to_markdown() serialization."""

    def test_asset_to_markdown(self):
        from assets import FindingsAsset

        asset = FindingsAsset(
            asset_id="f-001",
            type="findings",
            produced_by="investigation",
            source_work="WORK-093",
            version=1,
            timestamp=datetime(2026, 2, 15),
            author="Hephaestus",
            question="What?",
            findings=["Found X"],
            conclusion="Done",
            evidence=["E1"],
        )
        md = asset.to_markdown()
        assert md.startswith("---")
        assert "asset_id: f-001" in md


# =============================================================================
# Test 6: to_markdown() has parseable YAML frontmatter
# =============================================================================


    def test_asset_to_markdown_has_yaml_frontmatter(self):
        from assets import Asset

        asset = Asset(
            asset_id="a-001",
            type="test",
            produced_by="test",
            source_work="WORK-001",
            version=1,
            timestamp=datetime(2026, 2, 15),
            author="test",
        )
        md = asset.to_markdown()
        parts = md.split("---")
        assert len(parts) >= 3  # ---, frontmatter, ---, body
        frontmatter = yaml.safe_load(parts[1])
        assert frontmatter["asset_id"] == "a-001"
        assert frontmatter["type"] == "test"


# =============================================================================
# Test 7: CycleRunner.run() returns Asset (not LifecycleOutput)
# =============================================================================


class TestCycleRunnerAssetIntegration:
    """Tests for CycleRunner integration with Asset types."""

    def test_cycle_runner_run_returns_asset(self):
        from assets import Asset, FindingsAsset
        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer

        runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
        output = runner.run(work_id="WORK-093", lifecycle="investigation")
        assert isinstance(output, Asset)
        assert isinstance(output, FindingsAsset)
        assert output.source_work == "WORK-093"
        assert output.produced_by == "investigation"

    def test_cycle_runner_run_returns_specification_asset(self):
        from assets import Asset, SpecificationAsset
        from cycle_runner import CycleRunner
        from governance_layer import GovernanceLayer

        runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
        output = runner.run(work_id="WORK-093", lifecycle="design")
        assert isinstance(output, Asset)
        assert isinstance(output, SpecificationAsset)


# =============================================================================
# Test 8: Backward compatibility - LifecycleOutput alias still works
# =============================================================================


class TestBackwardCompatibility:
    """Tests for backward compatibility aliases in cycle_runner."""

    def test_lifecycle_output_backward_compat(self):
        from assets import Asset
        from cycle_runner import LifecycleOutput

        assert LifecycleOutput is Asset

    def test_findings_alias_backward_compat(self):
        from assets import FindingsAsset
        from cycle_runner import Findings

        assert Findings is FindingsAsset

    def test_alias_isinstance_works(self):
        from cycle_runner import CycleRunner, LifecycleOutput
        from governance_layer import GovernanceLayer

        runner = CycleRunner(governance=GovernanceLayer(), work_engine=None)
        output = runner.run(work_id="WORK-093", lifecycle="design")
        assert isinstance(output, LifecycleOutput)
