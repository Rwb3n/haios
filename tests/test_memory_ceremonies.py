# generated: 2026-02-12
"""
Tests for memory ceremonies (CH-016, WORK-133).

Validates:
1. All 3 memory ceremony skills have valid contracts in frontmatter
2. memory-commit-ceremony is not a stub
3. memory-commit-ceremony has event logging and error handling
4. close-work-cycle composes observation-capture as entry gate
5. ceremony_registry.yaml lists all 3 memory ceremonies
"""

import sys
from pathlib import Path

import pytest

# Add .claude/haios/lib to path for ceremony_contracts imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))

from ceremony_contracts import CeremonyContract, load_ceremony_registry
from helpers import load_frontmatter


def _has_category(entry, cat):
    """Check if registry entry has category (handles str or list)."""
    if isinstance(entry.category, list):
        return cat in entry.category
    return entry.category == cat


# --- Test 1: All three memory ceremony skills have valid contracts ---


class TestMemoryCeremonyContracts:
    """Verify all 3 memory ceremonies have valid ceremony contracts."""

    def test_observation_capture_has_ceremony_contract(self):
        """observation-capture-cycle has type: ceremony and valid contracts."""
        skill = load_frontmatter(".claude/skills/observation-capture-cycle/SKILL.md")
        assert skill["type"] == "ceremony"
        assert skill["category"] == "memory"
        contract = CeremonyContract.from_frontmatter(skill)
        assert len(contract.input_contract) >= 1
        assert len(contract.output_contract) >= 1
        assert len(contract.side_effects) >= 1

    def test_observation_triage_has_ceremony_contract(self):
        """observation-triage-cycle has type: ceremony and valid contracts."""
        skill = load_frontmatter(".claude/skills/observation-triage-cycle/SKILL.md")
        assert skill["type"] == "ceremony"
        assert skill["category"] == "memory"
        contract = CeremonyContract.from_frontmatter(skill)
        assert len(contract.output_contract) >= 1

    def test_memory_commit_has_ceremony_contract(self):
        """memory-commit-ceremony has type: ceremony and valid contracts."""
        skill = load_frontmatter(".claude/skills/memory-commit-ceremony/SKILL.md")
        assert skill["type"] == "ceremony"
        assert skill["category"] == "memory"
        contract = CeremonyContract.from_frontmatter(skill)
        assert len(contract.input_contract) >= 1
        assert len(contract.output_contract) >= 1


# --- Test 2: memory-commit-ceremony is not a stub ---


class TestMemoryCommitNotStub:
    """Verify memory-commit-ceremony is a full implementation, not a stub."""

    def test_memory_commit_not_stub(self):
        """memory-commit-ceremony must not have stub: true."""
        skill = load_frontmatter(".claude/skills/memory-commit-ceremony/SKILL.md")
        assert skill.get("stub") is not True, "memory-commit-ceremony must not be a stub"


# --- Test 3: memory-commit-ceremony has event logging ---


class TestMemoryCommitEventLogging:
    """Verify memory-commit-ceremony documents governance event logging."""

    def test_memory_commit_has_event_logging(self):
        """memory-commit-ceremony documents MemoryCommitted event logging."""
        content = Path(".claude/skills/memory-commit-ceremony/SKILL.md").read_text(
            encoding="utf-8"
        )
        assert (
            "MemoryCommitted" in content
            or "log_ceremony_event" in content
            or "governance-events" in content
        ), "memory-commit-ceremony must document event logging"


# --- Test 4: memory-commit-ceremony has error handling ---


class TestMemoryCommitErrorHandling:
    """Verify memory-commit-ceremony documents failure handling."""

    def test_memory_commit_has_error_handling(self):
        """memory-commit-ceremony documents failure handling."""
        content = Path(".claude/skills/memory-commit-ceremony/SKILL.md").read_text(
            encoding="utf-8"
        )
        content_lower = content.lower()
        assert (
            "error" in content_lower or "fail" in content_lower
        ), "memory-commit-ceremony must document error handling"


# --- Test 5: close-work-cycle composes observation-capture ---


class TestCloseWorkCycleComposition:
    """Verify close-work-cycle references observation-capture-cycle as entry gate."""

    def test_close_work_cycle_composes_observation_capture(self):
        """close-work-cycle references observation-capture-cycle as entry gate."""
        content = Path(".claude/skills/close-work-cycle/SKILL.md").read_text(
            encoding="utf-8"
        )
        assert "observation-capture-cycle" in content
        # observation-capture must come before VALIDATE phase
        obs_pos = content.find("observation-capture-cycle")
        validate_pos = content.find("### 1. VALIDATE Phase")
        assert obs_pos < validate_pos, (
            "observation-capture-cycle must be referenced before VALIDATE phase"
        )


# --- Test 6: ceremony registry lists all 3 memory ceremonies ---


class TestCeremonyRegistryMemory:
    """Verify ceremony_registry.yaml has all 3 memory ceremonies."""

    def test_registry_has_three_memory_ceremonies(self):
        """ceremony_registry.yaml has all 3 memory ceremonies with contracts."""
        registry = load_ceremony_registry()
        memory_ceremonies = [
            c for c in registry.ceremonies if _has_category(c, "memory")
        ]
        assert len(memory_ceremonies) == 3, (
            f"Expected 3 memory ceremonies, got {len(memory_ceremonies)}"
        )
        names = {c.name for c in memory_ceremonies}
        assert names == {"observation-capture", "observation-triage", "memory-commit"}
        for c in memory_ceremonies:
            assert c.has_contract is True, f"{c.name} must have contract"
            assert c.has_skill is True, f"{c.name} must have skill"
