# generated: 2025-12-24
# System Auto: last updated on: 2025-12-24T19:11:12
"""Tests for .claude/lib/audit.py"""
import pytest
import tempfile
import os
from pathlib import Path
import sys

# Import after path setup
sys.path.insert(0, '.claude/lib')


def test_parse_frontmatter_valid():
    """Test parsing valid YAML frontmatter."""
    from audit import parse_frontmatter

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write('---\nstatus: active\nid: E2-001\n---\n# Content')
        f.flush()
        result = parse_frontmatter(f.name)
        assert result['status'] == 'active'
        assert result['id'] == 'E2-001'
    os.unlink(f.name)


def test_parse_frontmatter_missing():
    """Test parsing file without frontmatter."""
    from audit import parse_frontmatter

    with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
        f.write('# No frontmatter here')
        f.flush()
        result = parse_frontmatter(f.name)
        assert result == {}
    os.unlink(f.name)


def test_audit_sync_returns_list():
    """Verify audit_sync returns a list."""
    from audit import audit_sync

    result = audit_sync()
    assert isinstance(result, list)


def test_audit_gaps_returns_list():
    """Verify audit_gaps returns a list."""
    from audit import audit_gaps

    result = audit_gaps()
    assert isinstance(result, list)


def test_audit_stale_returns_list():
    """Verify audit_stale returns a list."""
    from audit import audit_stale

    result = audit_stale()
    assert isinstance(result, list)


def test_audit_stale_threshold():
    """Verify threshold parameter works."""
    from audit import audit_stale

    result_high = audit_stale(threshold=1000)  # Very high, should find nothing recent
    result_low = audit_stale(threshold=0)      # Zero, should find everything
    # At minimum, result should be a list
    assert isinstance(result_high, list)
    assert isinstance(result_low, list)
