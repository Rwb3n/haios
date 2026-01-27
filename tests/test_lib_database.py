# generated: 2025-12-21
# System Auto: last updated on: 2026-01-27T20:57:13
"""
Phase 1a Tests: Database Layer from .claude/haios/lib/

Tests verify database module works from new location.
Written FIRST per TDD methodology.
"""
import sys
from pathlib import Path

# Add .claude/haios/lib to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / ".claude" / "haios" / "lib"))


class TestDatabaseImport:
    """Tests for database module importability."""

    def test_can_import_database_module(self):
        """Database module must be importable from .claude/haios/lib/."""
        from database import DatabaseManager
        assert DatabaseManager is not None

    def test_database_manager_has_required_methods(self):
        """DatabaseManager must have core methods."""
        from database import DatabaseManager

        required_methods = [
            'get_connection',
            'setup',
            'insert_artifact',
            'insert_entity',
            'insert_concept',
            'search_memories',
            'get_stats',
            'get_schema_info',
            'query_read_only',
        ]

        for method in required_methods:
            assert hasattr(DatabaseManager, method), f"Missing method: {method}"


class TestDatabaseFunctionality:
    """Tests for database functionality from new location."""

    def test_database_manager_instantiation(self):
        """DatabaseManager can be instantiated."""
        from database import DatabaseManager
        db = DatabaseManager(':memory:')
        assert db is not None
        assert db.db_path == ':memory:'

    def test_database_connection(self):
        """DatabaseManager can create a connection."""
        from database import DatabaseManager
        db = DatabaseManager(':memory:')
        conn = db.get_connection()
        assert conn is not None

    def test_get_stats_works(self):
        """get_stats returns expected structure."""
        from database import DatabaseManager
        db = DatabaseManager(':memory:')
        db.setup()
        stats = db.get_stats()

        assert 'artifacts' in stats
        assert 'entities' in stats
        assert 'concepts' in stats
        assert isinstance(stats['artifacts'], int)

    def test_get_schema_info_returns_tables(self):
        """get_schema_info returns table list."""
        from database import DatabaseManager
        db = DatabaseManager(':memory:')
        db.setup()

        info = db.get_schema_info()
        assert 'tables' in info
        assert 'artifacts' in info['tables']
        assert 'concepts' in info['tables']

    def test_get_schema_info_returns_columns(self):
        """get_schema_info returns column info for specific table."""
        from database import DatabaseManager
        db = DatabaseManager(':memory:')
        db.setup()

        info = db.get_schema_info('concepts')
        assert 'columns' in info
        assert info['table'] == 'concepts'

        column_names = [c['name'] for c in info['columns']]
        assert 'id' in column_names
        assert 'type' in column_names
        assert 'content' in column_names
