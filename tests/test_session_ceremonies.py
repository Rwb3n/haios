"""Tests for session ceremony implementations (WORK-120, CH-014).

Validates that session-start-ceremony, session-end-ceremony, and checkpoint-cycle
have working implementations with ceremony logic, contracts, and event logging
per REQ-CEREMONY-001/002.
"""

from pathlib import Path

import yaml

# Project root (tests/ is one level below)
PROJECT_ROOT = Path(__file__).parent.parent
SKILLS_DIR = PROJECT_ROOT / ".claude" / "skills"


def _extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}
    end = content.index("---", 3)
    fm_text = content[3:end].strip()
    return yaml.safe_load(fm_text) or {}


# --- Session Start Ceremony Tests ---


class TestSessionStartCeremony:
    """Tests 1-3: session-start-ceremony de-stubbed with ceremony logic."""

    def test_session_start_ceremony_not_stub(self):
        """Test 1: session-start-ceremony must not have stub: true."""
        skill_path = SKILLS_DIR / "session-start-ceremony" / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        fm = _extract_frontmatter(content)
        assert fm.get("stub") is not True, "session-start-ceremony is still a stub"

    def test_session_start_has_detailed_steps(self):
        """Test 2: session-start-ceremony must have detailed ceremony steps."""
        skill_path = SKILLS_DIR / "session-start-ceremony" / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        assert "## Ceremony Steps" in content
        steps_idx = content.index("## Ceremony Steps")
        steps_section = content[steps_idx:]
        assert len(steps_section) > 300, (
            f"Ceremony steps too brief ({len(steps_section)} chars, need >300)"
        )

    def test_session_start_references_ceremony_context(self):
        """Test 3: session-start-ceremony must reference ceremony boundary."""
        skill_path = SKILLS_DIR / "session-start-ceremony" / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        has_ref = (
            "ceremony_context" in content
            or "ceremony boundary" in content.lower()
        )
        assert has_ref, "session-start-ceremony missing ceremony_context reference"


# --- Session End Ceremony Tests ---


class TestSessionEndCeremony:
    """Tests 4-7: session-end-ceremony de-stubbed with orphan detection."""

    def test_session_end_ceremony_not_stub(self):
        """Test 4: session-end-ceremony must not have stub: true."""
        skill_path = SKILLS_DIR / "session-end-ceremony" / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        fm = _extract_frontmatter(content)
        assert fm.get("stub") is not True, "session-end-ceremony is still a stub"

    def test_session_end_has_orphan_detection(self):
        """Test 5: session-end-ceremony must include orphan work detection."""
        skill_path = SKILLS_DIR / "session-end-ceremony" / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        has_orphan = "orphan" in content.lower()
        has_scan = (
            "scan_incomplete_work" in content
            or "incomplete work" in content.lower()
        )
        assert has_orphan, "session-end-ceremony missing orphan detection"
        assert has_scan, "session-end-ceremony missing scan_incomplete_work reference"

    def test_session_end_has_uncommitted_check(self):
        """Test 6: session-end-ceremony must check for uncommitted changes."""
        skill_path = SKILLS_DIR / "session-end-ceremony" / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        has_check = (
            "uncommitted" in content.lower()
            or "git status" in content.lower()
        )
        assert has_check, "session-end-ceremony missing uncommitted changes check"

    def test_session_end_references_ceremony_context(self):
        """Test 7: session-end-ceremony must reference ceremony boundary."""
        skill_path = SKILLS_DIR / "session-end-ceremony" / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        has_ref = (
            "ceremony_context" in content
            or "ceremony boundary" in content.lower()
        )
        assert has_ref, "session-end-ceremony missing ceremony_context reference"


# --- Checkpoint Ceremony Tests ---


class TestCheckpointCeremony:
    """Test 8: checkpoint-cycle has contract validation reference."""

    def test_checkpoint_has_contract_reference(self):
        """Test 8: checkpoint-cycle must reference ceremony contracts."""
        skill_path = SKILLS_DIR / "checkpoint-cycle" / "SKILL.md"
        content = skill_path.read_text(encoding="utf-8")
        assert "contract" in content.lower(), (
            "checkpoint-cycle missing contract reference"
        )


# --- Shared Session Ceremony Tests ---


class TestSharedSessionCeremonyProperties:
    """Tests 9-10: All session ceremonies have required frontmatter."""

    SESSION_CEREMONIES = [
        "session-start-ceremony",
        "session-end-ceremony",
        "checkpoint-cycle",
    ]

    def test_all_session_ceremonies_have_type(self):
        """Test 9: All session ceremony skills must have type: ceremony."""
        for name in self.SESSION_CEREMONIES:
            skill_path = SKILLS_DIR / name / "SKILL.md"
            content = skill_path.read_text(encoding="utf-8")
            fm = _extract_frontmatter(content)
            assert fm.get("type") == "ceremony", (
                f"{name} missing type: ceremony"
            )

    def test_session_ceremonies_have_side_effects(self):
        """Test 10: All session ceremony skills must declare side_effects."""
        for name in self.SESSION_CEREMONIES:
            skill_path = SKILLS_DIR / name / "SKILL.md"
            content = skill_path.read_text(encoding="utf-8")
            fm = _extract_frontmatter(content)
            assert "side_effects" in fm, (
                f"{name} missing side_effects declaration"
            )
