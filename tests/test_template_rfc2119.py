# generated: 2025-12-28
# System Auto: last updated on: 2026-02-05T19:16:23
"""
Tests for RFC 2119 governance sections in templates (E2-086).

Each template should have a dedicated RFC 2119 section with MUST/SHOULD/MAY
requirements that guide agents during document creation.
"""
from pathlib import Path

import pytest

TEMPLATES_DIR = Path(".claude/templates")


# test_checkpoint_template_has_rfc2119_section removed (WORK-183): checkpoint template simplified to pure YAML frontmatter


def test_implementation_plan_template_has_rfc2119_section():
    """Implementation plan template should have Pre-Implementation Checklist."""
    template_path = TEMPLATES_DIR / "implementation_plan.md"
    if not template_path.exists():
        template_path = TEMPLATES_DIR / "_legacy" / "implementation_plan.md"
    content = template_path.read_text()
    # Check for the RFC 2119 section
    assert "Pre-Implementation Checklist" in content or "RFC 2119" in content, \
        "implementation_plan.md missing 'Pre-Implementation Checklist' or 'RFC 2119' section"
    # Check for MUST keyword (plans have critical requirements)
    assert "MUST" in content, \
        "implementation_plan.md missing MUST governance keyword"


def test_investigation_template_has_rfc2119_section():
    """Investigation template should have Discovery Protocol section."""
    content = (TEMPLATES_DIR / "investigation.md").read_text()
    # Check for the RFC 2119 section
    assert "Discovery Protocol" in content or "RFC 2119" in content, \
        "investigation.md missing 'Discovery Protocol' or 'RFC 2119' section"
    # Check for governance keywords
    assert "SHOULD" in content or "MUST" in content, \
        "investigation.md missing SHOULD/MUST governance keywords"


def test_report_template_has_rfc2119_section():
    """Report template should have Verification Requirements section."""
    content = (TEMPLATES_DIR / "report.md").read_text()
    # Check for the RFC 2119 section
    assert "Verification Requirements" in content or "RFC 2119" in content, \
        "report.md missing 'Verification Requirements' or 'RFC 2119' section"
    # Check for MUST keyword (reports have critical requirements)
    assert "MUST" in content, \
        "report.md missing MUST governance keyword"


def test_adr_template_has_rfc2119_section():
    """ADR template should have Decision Criteria section."""
    content = (TEMPLATES_DIR / "architecture_decision_record.md").read_text()
    # Check for the RFC 2119 section
    assert "Decision Criteria" in content or "RFC 2119" in content, \
        "architecture_decision_record.md missing 'Decision Criteria' or 'RFC 2119' section"
    # Check for MUST keyword (ADRs have critical requirements)
    assert "MUST" in content, \
        "architecture_decision_record.md missing MUST governance keyword"
