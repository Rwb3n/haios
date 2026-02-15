# generated: 2026-02-15
# WORK-093: Lifecycle Asset Types (REQ-ASSET-001)
"""
Assets Module (WORK-093, REQ-ASSET-001)

Typed, immutable asset classes for lifecycle outputs. Each lifecycle
produces a specific Asset subclass with full provenance.

Design Decision (CH-023): Flat structure with all provenance fields
in base class, NOT wrapper pattern.

Lifecycles and their asset types:
    Investigation → FindingsAsset
    Design → SpecificationAsset
    Implementation → ArtifactAsset
    Validation → VerdictAsset
    Triage → PriorityListAsset

Usage:
    from assets import Asset, FindingsAsset, SpecificationAsset
    from assets import ArtifactAsset, VerdictAsset, PriorityListAsset

    findings = FindingsAsset(
        asset_id="investigation-WORK-001-v1",
        type="findings",
        produced_by="investigation",
        source_work="WORK-001",
        version=1,
        timestamp=datetime.now(),
        author="Hephaestus",
        question="What causes X?",
        findings=["Root cause is Y"],
        conclusion="Y is the root cause",
        evidence=["log file Z"],
    )

    d = findings.to_dict()       # Dict with ISO timestamp
    md = findings.to_markdown()  # YAML frontmatter + structured body
"""
from dataclasses import asdict, dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

import yaml


@dataclass
class Asset:
    """Base class for all lifecycle assets - flat provenance structure.

    All provenance fields are in the base class (CH-023 decision: flat, not wrapper).
    Subclasses add lifecycle-specific content fields.

    Attributes:
        asset_id: Unique identifier (e.g., "investigation-WORK-001-v1")
        type: Asset type name (e.g., "findings", "specification")
        produced_by: Lifecycle that produced this asset
        source_work: Work item ID (e.g., "WORK-093")
        version: Asset version number
        timestamp: When the asset was produced
        author: Who produced the asset
        status: Outcome status (success, failure, partial)
        inputs: List of input asset IDs consumed
        piped_from: Asset ID this was piped from (if any)
    """

    asset_id: str
    type: str
    produced_by: str
    source_work: str
    version: int
    timestamp: datetime
    author: str
    status: Literal["success", "failure", "partial"] = "success"
    inputs: List[str] = field(default_factory=list)
    piped_from: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serialize all fields to dict with ISO timestamp string.

        Returns:
            Dict with all fields. datetime converted to ISO format string.
        """
        d = asdict(self)
        d["timestamp"] = self.timestamp.isoformat()
        return d

    def to_markdown(self) -> str:
        """Serialize to markdown with YAML frontmatter and structured body.

        Frontmatter contains provenance fields. Body contains
        lifecycle-specific content fields as sections.

        Returns:
            Markdown string with YAML frontmatter.
        """
        d = self.to_dict()

        # Provenance fields go in frontmatter
        frontmatter_keys = [
            "asset_id",
            "type",
            "produced_by",
            "source_work",
            "version",
            "timestamp",
            "author",
            "status",
            "inputs",
            "piped_from",
        ]
        fm = {k: d[k] for k in frontmatter_keys if k in d}
        body_fields = {
            k: v for k, v in d.items() if k not in frontmatter_keys
        }

        lines = ["---"]
        lines.append(yaml.dump(fm, default_flow_style=False).strip())
        lines.append("---")
        lines.append(
            f"# {self.type.replace('_', ' ').title()} Asset"
        )
        lines.append("")

        for key, value in body_fields.items():
            lines.append(f"## {key.replace('_', ' ').title()}")
            if isinstance(value, list):
                for item in value:
                    lines.append(f"- {item}")
            elif isinstance(value, dict):
                lines.append(
                    yaml.dump(value, default_flow_style=False).strip()
                )
            else:
                lines.append(str(value))
            lines.append("")

        return "\n".join(lines)


# =============================================================================
# Lifecycle-specific Asset subclasses
# =============================================================================


@dataclass
class FindingsAsset(Asset):
    """Investigation lifecycle output: Question -> Findings.

    Attributes:
        question: The investigation question
        findings: List of findings/conclusions
        conclusion: Summary conclusion
        evidence: Supporting evidence references
    """

    question: str = ""
    findings: List[str] = field(default_factory=list)
    conclusion: str = ""
    evidence: List[str] = field(default_factory=list)


@dataclass
class SpecificationAsset(Asset):
    """Design lifecycle output: Requirements -> Specification.

    Attributes:
        requirements: List of requirement IDs addressed
        design_decisions: List of design decisions made
        interface: Interface specification string
    """

    requirements: List[str] = field(default_factory=list)
    design_decisions: List[str] = field(default_factory=list)
    interface: str = ""


@dataclass
class ArtifactAsset(Asset):
    """Implementation lifecycle output: Specification -> Artifact.

    Attributes:
        files_created: List of file paths created
        files_modified: List of file paths modified
        test_results: Test execution results
    """

    files_created: List[str] = field(default_factory=list)
    files_modified: List[str] = field(default_factory=list)
    test_results: Dict[str, Any] = field(default_factory=dict)


@dataclass
class VerdictAsset(Asset):
    """Validation lifecycle output: Artifact x Spec -> Verdict.

    Attributes:
        passed: Whether validation passed
        criteria_results: Results for each validation criterion
        evidence: Supporting evidence references
    """

    passed: bool = False
    criteria_results: List[Dict[str, Any]] = field(default_factory=list)
    evidence: List[str] = field(default_factory=list)


@dataclass
class PriorityListAsset(Asset):
    """Triage lifecycle output: [Items] -> [PrioritizedItems].

    Attributes:
        items: Prioritized items with ranking info
        rationale: Explanation of prioritization rationale
    """

    items: List[Dict[str, Any]] = field(default_factory=list)
    rationale: str = ""
