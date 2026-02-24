# generated: 2026-02-24
# Session 439: WORK-164 Agent Cards
"""Tests for agent_cards.py — programmatic agent discovery (REQ-DISCOVER-003)."""

from pathlib import Path

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))
from agent_cards import AgentCard, list_agents, get_agent, filter_agents, AGENTS_DIR


# --- AgentCard dataclass ---

class TestAgentCard:
    """Test AgentCard dataclass construction and defaults."""

    def test_minimal_construction(self):
        """AgentCard can be constructed with only required fields."""
        card = AgentCard(name="test-agent", description="A test", tools=["Read"], model="haiku")
        assert card.name == "test-agent"
        assert card.description == "A test"
        assert card.tools == ["Read"]
        assert card.model == "haiku"

    def test_optional_fields_have_defaults(self):
        """New fields (id, role, capabilities, produces, consumes) default gracefully."""
        card = AgentCard(name="test-agent", description="A test", tools=["Read"], model="haiku")
        assert card.id == ""
        assert card.role == ""
        assert card.capabilities == []
        assert card.produces == []
        assert card.consumes == []

    def test_existing_optional_fields_have_defaults(self):
        """Existing optional fields default gracefully."""
        card = AgentCard(name="test-agent", description="A test", tools=["Read"], model="haiku")
        assert card.requirement_level == "optional"
        assert card.category == "utility"
        assert card.trigger_conditions == []
        assert card.input_contract == ""
        assert card.output_contract == ""
        assert card.invoked_by == []
        assert card.related_agents == []

    def test_full_construction(self):
        """AgentCard can be constructed with all fields."""
        card = AgentCard(
            name="critique-agent",
            description="Assumption surfacing",
            tools=["Read", "Glob"],
            model="opus",
            requirement_level="recommended",
            category="verification",
            trigger_conditions=["Before DO phase"],
            input_contract="plan_path, work_id",
            output_contract="critique-report.md",
            invoked_by=["implementation-cycle"],
            related_agents=["anti-pattern-checker"],
            id="critique-agent",
            role="verifier",
            capabilities=["assumption-surfacing", "plan-critique"],
            produces=["critique-report", "assumptions-yaml"],
            consumes=["plan-document", "work-item"],
        )
        assert card.id == "critique-agent"
        assert card.role == "verifier"
        assert len(card.capabilities) == 2
        assert len(card.produces) == 2
        assert len(card.consumes) == 2

    def test_id_defaults_to_empty_not_name(self):
        """id defaults to empty string — caller resolves to name if needed."""
        card = AgentCard(name="test", description="", tools=[], model="haiku")
        assert card.id == ""


# --- list_agents ---

class TestListAgents:
    """Test list_agents() against real agent files."""

    def test_returns_list(self):
        """list_agents() returns a list."""
        agents = list_agents()
        assert isinstance(agents, list)

    def test_returns_agent_cards(self):
        """Each item is an AgentCard."""
        agents = list_agents()
        for agent in agents:
            assert isinstance(agent, AgentCard)

    def test_agent_count(self):
        """Should find exactly 13 agents (excludes README.md)."""
        agents = list_agents()
        assert len(agents) == 13, \
            f"Expected 13 agents, got {len(agents)}: {[a.name for a in agents]}"

    def test_excludes_readme(self):
        """README.md should not appear in results."""
        agents = list_agents()
        names = [a.name for a in agents]
        assert "README" not in names
        assert "README.md" not in names

    def test_all_have_name(self):
        """Every agent has a non-empty name."""
        agents = list_agents()
        for agent in agents:
            assert agent.name, f"Agent with empty name found"

    def test_all_have_description(self):
        """Every agent has a non-empty description."""
        agents = list_agents()
        for agent in agents:
            assert agent.description, f"Agent {agent.name} has empty description"

    def test_all_have_model(self):
        """Every agent has a valid model."""
        valid_models = {"haiku", "sonnet", "opus"}
        agents = list_agents()
        for agent in agents:
            assert agent.model in valid_models, \
                f"Agent {agent.name} has invalid model '{agent.model}'"

    def test_known_agents_present(self):
        """Key agents must be in the list."""
        agents = list_agents()
        names = {a.name for a in agents}
        expected = {
            "critique-agent", "test-runner", "schema-verifier",
            "preflight-checker", "validation-agent", "why-capturer",
        }
        assert expected.issubset(names), f"Missing agents: {expected - names}"


# --- get_agent ---

class TestGetAgent:
    """Test get_agent() lookup by name."""

    def test_known_agent(self):
        """Can retrieve critique-agent by name."""
        agent = get_agent("critique-agent")
        assert agent is not None
        assert agent.name == "critique-agent"

    def test_unknown_agent_returns_none(self):
        """Unknown agent name returns None."""
        agent = get_agent("nonexistent-agent")
        assert agent is None

    def test_returns_agent_card(self):
        """Result is an AgentCard instance."""
        agent = get_agent("test-runner")
        assert isinstance(agent, AgentCard)


# --- filter_agents ---

class TestFilterAgents:
    """Test filter_agents() with various criteria."""

    def test_filter_by_category_gate(self):
        """Filtering by category='gate' returns gate agents."""
        gates = filter_agents(category="gate")
        names = {a.name for a in gates}
        assert "preflight-checker" in names
        assert "schema-verifier" in names

    def test_filter_by_category_verification(self):
        """Filtering by category='verification' returns verification agents."""
        verifiers = filter_agents(category="verification")
        names = {a.name for a in verifiers}
        assert "critique-agent" in names
        assert "validation-agent" in names

    def test_filter_by_requirement_level_required(self):
        """Filtering by requirement_level='required' returns required agents."""
        required = filter_agents(requirement_level="required")
        names = {a.name for a in required}
        assert "preflight-checker" in names
        assert "schema-verifier" in names
        assert "investigation-agent" in names

    def test_filter_by_model(self):
        """Filtering by model returns agents with that model."""
        haiku_agents = filter_agents(model="haiku")
        for agent in haiku_agents:
            assert agent.model == "haiku"

    def test_no_filters_returns_all(self):
        """No filters returns all agents."""
        all_agents = filter_agents()
        assert len(all_agents) == 13

    def test_combined_filters(self):
        """Multiple filters are ANDed together."""
        result = filter_agents(category="gate", model="haiku")
        for agent in result:
            assert agent.category == "gate"
            assert agent.model == "haiku"

    def test_no_matches_returns_empty(self):
        """Filter with no matches returns empty list."""
        result = filter_agents(category="nonexistent")
        assert result == []


# --- AGENTS_DIR constant ---

class TestAgentsDir:
    """Test AGENTS_DIR is correctly resolved."""

    def test_agents_dir_exists(self):
        """AGENTS_DIR points to a real directory."""
        assert AGENTS_DIR.exists(), f"AGENTS_DIR does not exist: {AGENTS_DIR}"

    def test_agents_dir_has_md_files(self):
        """AGENTS_DIR contains .md files."""
        md_files = list(AGENTS_DIR.glob("*.md"))
        assert len(md_files) > 0
