"""Tests for WORK-104: Validation and Triage cycle mappings in activity_matrix.yaml."""

import yaml
from pathlib import Path

MATRIX_PATH = Path(".claude/haios/config/activity_matrix.yaml")


def _load_matrix():
    """Load activity matrix YAML."""
    with open(MATRIX_PATH, "r") as f:
        return yaml.safe_load(f)


class TestValidationCycleMappings:
    """Verify validation-cycle phase_to_state entries exist and map correctly."""

    def test_verify_maps_to_check(self):
        matrix = _load_matrix()
        assert matrix["phase_to_state"]["validation-cycle/VERIFY"] == "CHECK"

    def test_judge_maps_to_check(self):
        matrix = _load_matrix()
        assert matrix["phase_to_state"]["validation-cycle/JUDGE"] == "CHECK"

    def test_report_maps_to_check(self):
        matrix = _load_matrix()
        assert matrix["phase_to_state"]["validation-cycle/REPORT"] == "CHECK"


class TestTriageCycleMappings:
    """Verify triage-cycle phase_to_state entries exist and map correctly."""

    def test_scan_maps_to_explore(self):
        matrix = _load_matrix()
        assert matrix["phase_to_state"]["triage-cycle/SCAN"] == "EXPLORE"

    def test_assess_maps_to_explore(self):
        matrix = _load_matrix()
        assert matrix["phase_to_state"]["triage-cycle/ASSESS"] == "EXPLORE"

    def test_rank_maps_to_design(self):
        matrix = _load_matrix()
        assert matrix["phase_to_state"]["triage-cycle/RANK"] == "DESIGN"

    def test_commit_maps_to_done(self):
        matrix = _load_matrix()
        assert matrix["phase_to_state"]["triage-cycle/COMMIT"] == "DONE"


class TestMappingsMatchTemplates:
    """Verify activity_matrix mappings match template frontmatter maps_to_state values."""

    VALIDATION_EXPECTED = {
        "VERIFY": "CHECK",
        "JUDGE": "CHECK",
        "REPORT": "CHECK",
    }

    TRIAGE_EXPECTED = {
        "SCAN": "EXPLORE",
        "ASSESS": "EXPLORE",
        "RANK": "DESIGN",
        "COMMIT": "DONE",
    }

    def test_validation_template_alignment(self):
        """All validation-cycle mappings match template frontmatter."""
        matrix = _load_matrix()
        mapping = matrix["phase_to_state"]
        for phase, expected_state in self.VALIDATION_EXPECTED.items():
            key = f"validation-cycle/{phase}"
            assert key in mapping, f"Missing mapping: {key}"
            assert mapping[key] == expected_state, (
                f"{key}: expected {expected_state}, got {mapping[key]}"
            )

    def test_triage_template_alignment(self):
        """All triage-cycle mappings match template frontmatter."""
        matrix = _load_matrix()
        mapping = matrix["phase_to_state"]
        for phase, expected_state in self.TRIAGE_EXPECTED.items():
            key = f"triage-cycle/{phase}"
            assert key in mapping, f"Missing mapping: {key}"
            assert mapping[key] == expected_state, (
                f"{key}: expected {expected_state}, got {mapping[key]}"
            )
