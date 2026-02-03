# generated: 2026-02-03
# System Auto: last updated on: 2026-02-03T23:02:35
# WORK-087: Tests for close-work-cycle CHAIN phase caller chaining
"""Tests for close-work-cycle SKILL.md CHAIN phase behavior.

These tests verify the skill markdown content, not runtime behavior.
Skills are instruction documents interpreted by Claude Code.

REQ-LIFECYCLE-004: Chaining is caller choice, not callee side-effect.
"""
import re
from pathlib import Path

import pytest


def extract_section(content: str, section_header: str) -> str:
    """Extract a markdown section by header."""
    # Find the section start
    pattern = rf"(^|\n)(#{1,4}\s*\d*\.?\s*{re.escape(section_header.lstrip('#').strip())})"
    match = re.search(pattern, content, re.IGNORECASE)
    if not match:
        return ""

    start = match.start()

    # Find the next section of same or higher level
    header_level = len(section_header.split()[0])  # Count #s
    remaining = content[start + len(match.group()):]

    # Look for next header of same or higher level
    next_section = re.search(rf"\n#{{{1},{header_level}}}\s+[^#]", remaining)
    if next_section:
        end = start + len(match.group()) + next_section.start()
        return content[start:end]

    return content[start:]


class TestChainPhaseCallerChoice:
    """Tests for WORK-087: Caller Chaining (REQ-LIFECYCLE-004)."""

    @pytest.fixture
    def skill_content(self) -> str:
        """Load close-work-cycle SKILL.md content."""
        skill_path = Path(".claude/skills/close-work-cycle/SKILL.md")
        if not skill_path.exists():
            pytest.skip("close-work-cycle SKILL.md not found")
        return skill_path.read_text(encoding="utf-8")

    @pytest.fixture
    def chain_section(self, skill_content: str) -> str:
        """Extract CHAIN phase section from skill."""
        # Try different header patterns (including Post-MEMORY suffix)
        for header in [
            "### 4. CHAIN Phase (Post-MEMORY)",
            "### 4. CHAIN Phase",
            "4. CHAIN Phase",
            "CHAIN Phase"
        ]:
            section = extract_section(skill_content, header)
            if section:
                return section

        # Fallback: search for CHAIN Phase anywhere
        if "CHAIN Phase" in skill_content:
            # Find the section manually
            idx = skill_content.find("### 4. CHAIN")
            if idx >= 0:
                # Find next ### header
                next_header = skill_content.find("\n### ", idx + 1)
                if next_header > idx:
                    return skill_content[idx:next_header]
                return skill_content[idx:]

        pytest.fail("CHAIN phase section not found in SKILL.md")

    def test_chain_phase_presents_options_without_auto_executing(self, chain_section: str):
        """CHAIN phase presents options but does not auto-execute Skill() calls.

        REQ-LIFECYCLE-004: Chaining is caller choice, not callee side-effect.
        The skill should present options and await caller choice.
        """
        # Should have "Present options" or "Await" pattern
        has_present = "present options" in chain_section.lower() or "present" in chain_section.lower()
        has_await = "await" in chain_section.lower()
        has_choice = "choice" in chain_section.lower() or "choose" in chain_section.lower()

        assert has_present or has_await or has_choice, (
            "CHAIN phase should present options to caller, not auto-execute. "
            "Expected 'Present options', 'Await', or 'choice' language."
        )

        # Should have "Complete without spawn" as an option
        assert "complete without spawn" in chain_section.lower(), (
            "CHAIN phase should list 'Complete without spawn' as a valid option."
        )

    def test_complete_without_spawn_is_valid_option_without_warning(self, chain_section: str):
        """'Complete without spawn' is listed as valid option without warnings.

        REQ-LIFECYCLE-004: "Complete without spawn" is a first-class valid outcome.
        The option should not be accompanied by warning language.
        """
        # Find "Complete without spawn" in the section
        assert "complete without spawn" in chain_section.lower(), (
            "'Complete without spawn' should be present in CHAIN phase."
        )

        # Check for note about it being valid (not a warning)
        has_valid_note = (
            "valid" in chain_section.lower() or
            "first-class" in chain_section.lower() or
            "no warning" in chain_section.lower()
        )

        # Check it's NOT framed as a warning or error case
        # Split at "Complete without spawn" and check surrounding context
        lower_section = chain_section.lower()
        spawn_idx = lower_section.find("complete without spawn")

        if spawn_idx > 0:
            # Check 200 chars before and after for warning language
            context_start = max(0, spawn_idx - 200)
            context_end = min(len(lower_section), spawn_idx + 250)
            context = lower_section[context_start:context_end]

            # Should not have warning/error framing near this option
            warning_indicators = ["warn", "error", "fail", "invalid", "problem"]
            has_warning = any(ind in context for ind in warning_indicators)

            # If there IS warning language, it should be saying "no warning"
            if has_warning:
                assert "no warning" in context or "valid" in context, (
                    "'Complete without spawn' should not have warning language nearby. "
                    "Found warning indicators without 'no warning' or 'valid' qualifier."
                )

    def test_routing_table_preserved_but_not_auto_executed(self, chain_section: str):
        """Routing decision table still exists for guidance, but execution is caller choice.

        WORK-030: Type field is authoritative for routing suggestions.
        REQ-LIFECYCLE-004: Execution is caller choice, not automatic.
        """
        # Routing logic should still exist (for determining suggestions)
        has_type_routing = "type" in chain_section.lower()
        has_investigation = "investigation" in chain_section.lower()

        assert has_type_routing, (
            "Routing logic based on 'type' field should exist for suggestions."
        )
        assert has_investigation, (
            "Investigation routing should be mentioned (type-based routing)."
        )

        # Should have explicit caller choice language
        choice_indicators = ["choice", "choose", "select", "option", "caller"]
        has_choice_language = any(ind in chain_section.lower() for ind in choice_indicators)

        assert has_choice_language, (
            "CHAIN phase should have explicit caller choice language. "
            "Expected: 'choice', 'choose', 'select', 'option', or 'caller'."
        )

        # Should NOT have "execute immediately" or "do not pause" directives
        immediate_indicators = ["execute immediately", "do not pause", "without acknowledgment"]
        has_immediate = any(ind in chain_section.lower() for ind in immediate_indicators)

        assert not has_immediate, (
            "CHAIN phase should NOT have 'execute immediately' or 'do not pause' directives. "
            "These contradict REQ-LIFECYCLE-004 (caller choice)."
        )
