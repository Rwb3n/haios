# generated: 2025-12-28
# System Auto: last updated on: 2025-12-28T16:54:21
"""Tests for Ground Truth Verification table parser.

E2-219: Ground Truth Verification Parser
Tests the parse_ground_truth_table() and classify_verification_type() functions.
"""

import sys
from pathlib import Path

# Add .claude/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "lib"))

from validate import parse_ground_truth_table, classify_verification_type


class TestParseGroundTruthTable:
    """Tests for parse_ground_truth_table function."""

    def test_parse_ground_truth_table_basic(self):
        """Test parsing a simple Ground Truth Verification table."""
        content = '''
## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/validate.py` | Function exists | [ ] | |
'''
        items = parse_ground_truth_table(content)
        assert len(items) == 1
        assert items[0]['file_path'] == '.claude/lib/validate.py'
        assert items[0]['expected_state'] == 'Function exists'
        assert items[0]['is_checked'] == False
        assert items[0]['notes'] == ''

    def test_parse_ground_truth_table_multiple(self):
        """Test parsing multiple items with checked and unchecked states."""
        content = '''
## Ground Truth Verification (Before Closing)

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `path/a.py` | A exists | [x] | Done |
| `path/b.py` | B exists | [ ] | |
'''
        items = parse_ground_truth_table(content)
        assert len(items) == 2
        assert items[0]['is_checked'] == True
        assert items[0]['notes'] == 'Done'
        assert items[1]['is_checked'] == False

    def test_parse_ground_truth_table_no_section(self):
        """Test parsing content without Ground Truth section returns empty list."""
        content = '''
## Some Other Section

| Column1 | Column2 |
|---------|---------|
| Value1  | Value2  |
'''
        items = parse_ground_truth_table(content)
        assert items == []

    def test_parse_ground_truth_table_real_data(self):
        """Test with real data format from E2-212 plan."""
        content = '''
## Ground Truth Verification (Before Closing)

> **MUST** read each file below and verify state before marking plan complete.

| File | Expected State | Verified | Notes |
|------|---------------|----------|-------|
| `.claude/lib/scaffold.py` | TEMPLATE_CONFIG has directory patterns | [ ] | |
| `Grep: WORK-.*-\\*\\.md` | **MUST:** Zero stale references | [ ] | |
| `tests/test_work_item.py` | 5+ tests passed | [ ] | |
'''
        items = parse_ground_truth_table(content)
        assert len(items) == 3
        assert items[0]['file_path'] == '.claude/lib/scaffold.py'
        assert items[0]['verification_type'] == 'file-check'
        assert items[1]['file_path'] == 'Grep: WORK-.*-\\*\\.md'
        assert items[1]['verification_type'] == 'grep-check'
        assert items[2]['file_path'] == 'tests/test_work_item.py'
        assert items[2]['verification_type'] == 'test-run'


class TestClassifyVerificationType:
    """Tests for classify_verification_type function."""

    def test_classify_verification_type_file_check(self):
        """Test classification of file check type."""
        result = classify_verification_type('.claude/lib/test.py', 'Function X exists')
        assert result == 'file-check'

    def test_classify_verification_type_grep_check(self):
        """Test classification of grep check type."""
        result = classify_verification_type('Grep: old_pattern', 'Zero matches')
        assert result == 'grep-check'

    def test_classify_verification_type_test_run(self):
        """Test classification of test run type."""
        result = classify_verification_type('tests/test_file.py', '5 tests pass')
        assert result == 'test-run'

    def test_classify_verification_type_test_run_by_expected(self):
        """Test classification of test run type by expected state pattern."""
        result = classify_verification_type('some/file.py', 'pytest tests pass')
        assert result == 'test-run'

    def test_classify_verification_type_json_verify(self):
        """Test classification of JSON verify type."""
        result = classify_verification_type('.claude/haios-status.json', 'Field X contains Y')
        assert result == 'json-verify'

    def test_classify_verification_type_human_judgment(self):
        """Test classification of human judgment type (default)."""
        result = classify_verification_type('Some description', 'Code is readable')
        assert result == 'human-judgment'

    def test_classify_verification_type_with_backticks(self):
        """Test that backticks in file path are handled."""
        result = classify_verification_type('`tests/test_file.py`', 'Tests exist')
        assert result == 'test-run'
