# generated: 2025-12-29
# System Auto: last updated on: 2026-01-27T20:57:52
"""
Tests for anti-pattern-checker agent.

TDD tests for E2-232 - Anti-Pattern Checker Agent implementation.
Tests written FIRST per implementation-cycle methodology.
"""
from pathlib import Path
import sys

# Add .claude/haios/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))


class TestAntiPatternCheckerAgent:
    """Tests for anti-pattern-checker agent file structure."""

    def test_agent_file_exists(self):
        """Agent file must exist at expected location."""
        agent_file = Path('.claude/agents/anti-pattern-checker.md')
        assert agent_file.exists(), "Missing .claude/agents/anti-pattern-checker.md"

    def test_agent_has_required_frontmatter(self):
        """Agent must have name, description, tools in frontmatter."""
        agent_file = Path('.claude/agents/anti-pattern-checker.md')
        content = agent_file.read_text()
        assert 'name: anti-pattern-checker' in content, "Missing 'name: anti-pattern-checker' in frontmatter"
        assert 'description:' in content, "Missing 'description:' in frontmatter"
        assert 'tools:' in content, "Missing 'tools:' in frontmatter"


class TestVerificationLenses:
    """Tests for the 6 L1 anti-pattern verification lenses."""

    def test_agent_defines_six_lenses(self):
        """Agent must define all 6 L1 anti-pattern lenses."""
        agent_file = Path('.claude/agents/anti-pattern-checker.md')
        content = agent_file.read_text().lower()

        # Check for each lens (allow underscore or space variants)
        lenses = [
            ('assume_over_verify', 'assume over verify'),
            ('generate_over_retrieve', 'generate over retrieve'),
            ('move_fast', 'move fast'),
            ('optimistic_confidence', 'optimistic confidence'),
            ('pattern_match', 'pattern-match'),
            ('ceremonial_completion', 'ceremonial completion'),
        ]

        for lens_id, lens_text in lenses:
            assert lens_id in content or lens_text in content, f"Missing lens: {lens_id}"


class TestOutputFormat:
    """Tests for agent output format documentation."""

    def test_agent_has_output_format_section(self):
        """Agent must document output format."""
        agent_file = Path('.claude/agents/anti-pattern-checker.md')
        content = agent_file.read_text()
        assert 'Output Format' in content or '## Output' in content, "Missing output format section"

    def test_agent_documents_verified_field(self):
        """Agent must document 'verified' field in output."""
        agent_file = Path('.claude/agents/anti-pattern-checker.md')
        content = agent_file.read_text()
        assert '"verified"' in content or 'verified' in content, "Missing 'verified' field documentation"

    def test_agent_documents_lenses_field(self):
        """Agent must document 'lenses' field in output."""
        agent_file = Path('.claude/agents/anti-pattern-checker.md')
        content = agent_file.read_text()
        assert '"lenses"' in content or 'lenses' in content, "Missing 'lenses' field documentation"


class TestRuntimeDiscovery:
    """Tests for agent runtime discovery."""

    def test_agent_discovered_by_status(self):
        """Agent must appear in get_agents() after creation."""
        from status import get_agents

        agents = get_agents()
        assert 'anti-pattern-checker' in agents, "Agent not discovered by get_agents()"
