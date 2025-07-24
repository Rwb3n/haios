#!/usr/bin/env python3
"""
Test Suite for Database Schema Extensions (Phase 2 Step 5)
Comprehensive testing of database schema, migration, data access, and integration components
"""

import unittest
import tempfile
import sqlite3
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import MagicMock, patch

from database_extensions import DatabaseSchemaManager, EnhancedDataAccess
from system_integration import SystemIntegrationManager, IntegratedTenderPipeline

class TestDatabaseSchemaManager(unittest.TestCase):
    """Test database schema management and migration functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_tenders.db"
        
        # Create Phase 1 database structure
        self._create_phase1_database()
        
        self.schema_manager = DatabaseSchemaManager(str(self.db_path))
    
    def tearDown(self):
        # Cleanup
        if self.db_path.exists():
            self.db_path.unlink()
        os.rmdir(self.temp_dir)
    
    def _create_phase1_database(self):
        """Create Phase 1 database structure for testing migration"""
        with sqlite3.connect(self.db_path) as conn:
            # Create basic tenders table (Phase 1)
            conn.execute("""
                CREATE TABLE tenders (
                    notice_identifier TEXT PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    organisation_name TEXT,
                    value_high INTEGER,
                    status TEXT,
                    suitable_for_sme TEXT,
                    cpv_codes TEXT,
                    closing_date TEXT,
                    published_date TEXT,
                    links TEXT,
                    contact_details TEXT
                )
            """)
            
            # Insert test data
            test_tenders = [
                ('TEST_001', 'Digital Transformation Project', 
                 'Comprehensive digital transformation with cloud migration',
                 'NHS Digital', 2500000, 'open', 'yes', '72000000', 
                 '2024-02-15', '2024-01-01', '', ''),
                ('TEST_002', 'Software Development Services',
                 'Custom software development using Python and JavaScript',
                 'Cabinet Office', 750000, 'open', 'yes', '72200000',
                 '2024-03-01', '2024-01-15', '', ''),
                ('TEST_003', 'IT Support Services',
                 'Basic IT support and maintenance services',
                 'Local Council', 150000, 'open', 'yes', '72400000',
                 '2024-02-20', '2024-01-10', '', ''),
            ]
            
            conn.executemany("""
                INSERT INTO tenders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, test_tenders)
    
    def test_schema_version_detection(self):
        """Test schema version detection for Phase 1 database"""
        version = self.schema_manager.get_current_schema_version()
        self.assertEqual(version, "1.0")
    
    def test_schema_version_table_creation(self):
        """Test schema version table creation"""
        self.schema_manager.create_schema_version_table()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='schema_version'
            """)
            self.assertIsNotNone(cursor.fetchone())
            
            # Check initial version record
            cursor = conn.execute("SELECT version FROM schema_version")
            version_record = cursor.fetchone()
            self.assertEqual(version_record[0], "1.0")
    
    def test_phase2_schema_upgrade(self):
        """Test complete Phase 2 schema upgrade"""
        success = self.schema_manager.upgrade_to_phase2_schema()
        self.assertTrue(success)
        
        # Verify all new tables exist
        expected_tables = [
            'enhanced_classifications', 'expert_validation', 'model_performance',
            'filter_performance', 'classification_history', 'schema_version'
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name IN ({})
            """.format(','.join('?' * len(expected_tables))), expected_tables)
            
            found_tables = [row[0] for row in cursor.fetchall()]
            
            for table in expected_tables:
                self.assertIn(table, found_tables, f"Table {table} not found after upgrade")
        
        # Verify schema version updated
        updated_version = self.schema_manager.get_current_schema_version()
        self.assertEqual(updated_version, "2.0")
    
    def test_enhanced_classifications_table_structure(self):
        """Test enhanced classifications table structure"""
        self.schema_manager.upgrade_to_phase2_schema()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("PRAGMA table_info(enhanced_classifications)")
            columns = {row[1]: row[2] for row in cursor.fetchall()}  # column_name: type
            
            # Check key columns exist
            required_columns = [
                'notice_identifier', 'keyword_score', 'context_score', 'ml_confidence',
                'final_relevance_score', 'filter_passes', 'bid_probability', 
                'final_recommendation', 'classification_timestamp'
            ]
            
            for column in required_columns:
                self.assertIn(column, columns, f"Column {column} missing from enhanced_classifications")
    
    def test_performance_indexes_creation(self):
        """Test performance indexes creation"""
        self.schema_manager.upgrade_to_phase2_schema()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='index' AND name LIKE 'idx_%'
            """)
            
            indexes = [row[0] for row in cursor.fetchall()]
            
            # Check some key indexes exist
            expected_indexes = [
                'idx_enhanced_final_score', 'idx_enhanced_recommendation',
                'idx_expert_label', 'idx_model_f1_score'
            ]
            
            for index in expected_indexes:
                self.assertIn(index, indexes, f"Index {index} not found")
    
    def test_data_validation_views_creation(self):
        """Test data validation views creation"""
        self.schema_manager.upgrade_to_phase2_schema()
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='view'
            """)
            
            views = [row[0] for row in cursor.fetchall()]
            
            expected_views = [
                'classification_quality_metrics', 'expert_validation_summary',
                'model_performance_trends'
            ]
            
            for view in expected_views:
                self.assertIn(view, views, f"View {view} not found")


class TestEnhancedDataAccess(unittest.TestCase):
    """Test enhanced data access layer functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_tenders.db"
        
        # Create and upgrade database
        self._create_test_database()
        
        self.data_access = EnhancedDataAccess(str(self.db_path))
    
    def tearDown(self):
        # Cleanup
        if self.db_path.exists():
            self.db_path.unlink()
        os.rmdir(self.temp_dir)
    
    def _create_test_database(self):
        """Create test database with Phase 2 schema"""
        # Create Phase 1 structure first
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE tenders (
                    notice_identifier TEXT PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    organisation_name TEXT,
                    value_high INTEGER,
                    status TEXT,
                    suitable_for_sme TEXT,
                    cpv_codes TEXT,
                    closing_date TEXT,
                    published_date TEXT,
                    links TEXT,
                    contact_details TEXT
                )
            """)
            
            # Insert test data
            test_tenders = [
                ('TEST_001', 'Digital Transformation Project', 
                 'Comprehensive digital transformation with cloud migration',
                 'NHS Digital', 2500000, 'open', 'yes', '72000000', 
                 '2024-02-15', '2024-01-01', '', ''),
                ('TEST_002', 'Software Development Services',
                 'Custom software development using Python and JavaScript',
                 'Cabinet Office', 750000, 'open', 'yes', '72200000',
                 '2024-03-01', '2024-01-15', '', ''),
            ]
            
            conn.executemany("""
                INSERT INTO tenders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, test_tenders)
        
        # Upgrade to Phase 2
        schema_manager = DatabaseSchemaManager(str(self.db_path))
        schema_manager.upgrade_to_phase2_schema()
    
    def test_save_basic_classification_result(self):
        """Test saving basic classification result"""
        # Create mock basic classification result
        mock_result = MagicMock()
        mock_result.notice_identifier = 'TEST_001'
        mock_result.keyword_score = 15.0
        mock_result.context_score = 8.5
        mock_result.ml_confidence = 0.78
        mock_result.composite_score = 42.3
        mock_result.technical_terms = ['api', 'cloud', 'digital']
        mock_result.transformation_signals = ['digital transformation']
        mock_result.explanation = 'Strong digital transformation indicators'
        
        # Test saving
        classification_id = self.data_access.save_classification_result(mock_result)
        self.assertIsInstance(classification_id, int)
        self.assertGreater(classification_id, 0)
        
        # Verify saved data
        with self.data_access.get_connection() as conn:
            cursor = conn.execute("""
                SELECT notice_identifier, keyword_score, final_relevance_score
                FROM enhanced_classifications WHERE id = ?
            """, (classification_id,))
            
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], 'TEST_001')
            self.assertEqual(row[1], 15.0)
            self.assertEqual(row[2], 42.3)  # Should use composite_score as final_relevance_score
    
    def test_save_enhanced_classification_result(self):
        """Test saving enhanced classification result with full scoring"""
        # Create mock enhanced classification result
        mock_result = MagicMock()
        mock_result.notice_identifier = 'TEST_002'
        mock_result.keyword_score = 12.0
        mock_result.context_score = 7.0
        mock_result.ml_confidence = 0.85
        mock_result.technical_terms = ['software', 'development', 'python']
        mock_result.transformation_signals = ['digital services']
        mock_result.metadata_score = 10.5
        mock_result.business_alignment_score = 6.0
        mock_result.urgency_multiplier = 1.3
        mock_result.value_multiplier = 1.8
        mock_result.department_multiplier = 1.2
        mock_result.final_relevance_score = 78.5
        mock_result.explanation = 'High-quality software development opportunity'
        
        # Test saving
        classification_id = self.data_access.save_classification_result(mock_result)
        
        # Verify saved data includes enhanced scoring fields
        with self.data_access.get_connection() as conn:
            cursor = conn.execute("""
                SELECT final_relevance_score, metadata_score, business_alignment_score,
                       urgency_multiplier, value_multiplier
                FROM enhanced_classifications WHERE id = ?
            """, (classification_id,))
            
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], 78.5)  # final_relevance_score
            self.assertEqual(row[1], 10.5)  # metadata_score
            self.assertEqual(row[2], 6.0)   # business_alignment_score
            self.assertEqual(row[3], 1.3)   # urgency_multiplier
            self.assertEqual(row[4], 1.8)   # value_multiplier
    
    def test_save_filtered_classification_result(self):
        """Test saving filtered opportunity result with full pipeline data"""
        # Create mock filtered opportunity result
        mock_enhanced = MagicMock()
        mock_enhanced.keyword_score = 14.0
        mock_enhanced.context_score = 9.0
        mock_enhanced.ml_confidence = 0.82
        mock_enhanced.technical_terms = ['cloud', 'transformation']
        mock_enhanced.transformation_signals = ['digital transformation']
        mock_enhanced.metadata_score = 11.0
        mock_enhanced.business_alignment_score = 7.5
        mock_enhanced.urgency_multiplier = 1.4
        mock_enhanced.value_multiplier = 2.0
        mock_enhanced.department_multiplier = 1.3
        mock_enhanced.final_relevance_score = 89.2
        
        mock_result = MagicMock()
        mock_result.notice_identifier = 'TEST_001'
        mock_result.original_enhanced_result = mock_enhanced
        mock_result.filter_passes = True
        mock_result.overall_filter_score = 0.88
        mock_result.bid_probability = 0.28
        mock_result.competition_assessment = {'competition_level': 6.5}
        mock_result.filter_profile_used = 'balanced'
        mock_result.final_recommendation = 'PURSUE'
        mock_result.risk_factors = ['high competition', 'urgent timeline']
        mock_result.success_factors = ['optimal value', 'remote delivery', 'NHS partnership']
        mock_result.resource_requirements = {'team_size': 8, 'duration_months': 18}
        
        # Test saving
        classification_id = self.data_access.save_classification_result(mock_result)
        
        # Verify all pipeline data saved correctly
        with self.data_access.get_connection() as conn:
            cursor = conn.execute("""
                SELECT filter_passes, overall_filter_score, bid_probability,
                       competition_level, final_recommendation, risk_factors, success_factors
                FROM enhanced_classifications WHERE id = ?
            """, (classification_id,))
            
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertTrue(row[0])  # filter_passes
            self.assertEqual(row[1], 0.88)  # overall_filter_score
            self.assertEqual(row[2], 0.28)  # bid_probability
            self.assertEqual(row[3], 6.5)   # competition_level
            self.assertEqual(row[4], 'PURSUE')  # final_recommendation
            
            # Check JSON fields
            risk_factors = json.loads(row[5])
            success_factors = json.loads(row[6])
            self.assertEqual(len(risk_factors), 2)
            self.assertEqual(len(success_factors), 3)
    
    def test_get_top_opportunities(self):
        """Test retrieving top opportunities with filtering"""
        # Insert test classification data
        test_classifications = [
            ('TEST_001', 89.2, True, 'PURSUE', 0.28, 'balanced'),
            ('TEST_002', 65.5, True, 'CONSIDER', 0.18, 'balanced'),
            ('TEST_003', 45.0, False, 'MONITOR', 0.08, 'conservative'),
        ]
        
        with self.data_access.get_connection() as conn:
            for notice_id, score, passes, recommendation, bid_prob, profile in test_classifications:
                conn.execute("""
                    INSERT INTO enhanced_classifications (
                        notice_identifier, keyword_score, context_score,
                        ml_confidence, composite_score, technical_terms, transformation_signals,
                        metadata_score, business_alignment_score, urgency_multiplier,
                        value_multiplier, department_multiplier, final_relevance_score,
                        score_breakdown, priority_level, filter_passes, overall_filter_score,
                        bid_probability, competition_level, filter_profile_used,
                        final_recommendation, risk_factors, success_factors,
                        resource_requirements, classification_timestamp, model_version,
                        pipeline_version, processing_time_ms, explanation
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    notice_id, 10.0, 5.0, 0.7, score, '[]', '[]',
                    8.0, 4.0, 1.2, 1.5, 1.1, score, '{}',
                    'HIGH' if score > 70 else 'MEDIUM' if score > 40 else 'LOW',
                    passes, 0.8, bid_prob, 5.0, profile, recommendation,
                    '[]', '[]', '{}', datetime.now().isoformat(),
                    'v1.0', 'v2.0', 150, 'Test classification'
                ))
        
        # Test getting top opportunities with filter
        top_opportunities = self.data_access.get_top_opportunities(
            min_score=60, filter_passed_only=True, limit=10
        )
        
        self.assertEqual(len(top_opportunities), 2)  # Only TEST_001 and TEST_002 pass filters and score >= 60
        self.assertEqual(top_opportunities[0]['notice_identifier'], 'TEST_001')  # Highest score first
        self.assertEqual(top_opportunities[1]['notice_identifier'], 'TEST_002')
        
        # Test without filter requirement
        all_opportunities = self.data_access.get_top_opportunities(
            min_score=40, filter_passed_only=False, limit=10
        )
        
        self.assertEqual(len(all_opportunities), 3)  # All three should be included
    
    def test_save_expert_validation(self):
        """Test saving expert validation data"""
        validation_data = {
            'notice_identifier': 'TEST_001',
            'expert_label': 'relevant',
            'confidence': 4,
            'notes': 'Clear digital transformation project',
            'reasoning': 'Strong technical indicators and strategic value',
            'system_prediction_score': 89.2,
            'system_recommendation': 'PURSUE',
            'prediction_confidence': 0.85,
            'timestamp': datetime.now().isoformat()
        }
        
        validation_id = self.data_access.save_expert_validation(validation_data)
        self.assertIsInstance(validation_id, int)
        self.assertGreater(validation_id, 0)
        
        # Verify saved data
        with self.data_access.get_connection() as conn:
            cursor = conn.execute("""
                SELECT expert_label, confidence, expert_system_agreement, disagreement_magnitude
                FROM expert_validation WHERE id = ?
            """, (validation_id,))
            
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], 'relevant')
            self.assertEqual(row[1], 4)
            self.assertTrue(row[2])  # Should agree (both relevant and score > 50)
            self.assertLess(row[3], 0.2)  # Low disagreement magnitude
    
    def test_save_model_performance(self):
        """Test saving model performance data"""
        performance_data = {
            'model_version': 'v2.1',
            'pipeline_components': ['classification', 'scoring', 'filtering'],
            'training_samples': 120,
            'validation_samples': 30,
            'expert_labels_used': 25,
            'feature_count': 22,
            'feature_names': ['keyword_score', 'context_score', 'metadata_score'],
            'validation_metrics': {
                'precision': 0.87,
                'recall': 0.84,
                'f1_score': 0.855,
                'accuracy': 0.89,
                'roc_auc': 0.91
            },
            'model_type': 'random_forest',
            'hyperparameters': {'n_estimators': 200, 'max_depth': 15},
            'calibration_method': 'isotonic',
            'timestamp': datetime.now().isoformat(),
            'deployed': True,
            'improvement': 0.03
        }
        
        performance_id = self.data_access.save_model_performance(performance_data)
        self.assertIsInstance(performance_id, int)
        self.assertGreater(performance_id, 0)
        
        # Verify saved data
        with self.data_access.get_connection() as conn:
            cursor = conn.execute("""
                SELECT model_version, f1_score, deployed, improvement_over_previous
                FROM model_performance WHERE id = ?
            """, (performance_id,))
            
            row = cursor.fetchone()
            self.assertIsNotNone(row)
            self.assertEqual(row[0], 'v2.1')
            self.assertEqual(row[1], 0.855)
            self.assertTrue(row[2])  # deployed
            self.assertEqual(row[3], 0.03)  # improvement


class TestSystemIntegration(unittest.TestCase):
    """Test system integration functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir)
        
        # Create test database
        self.db_path = self.data_dir / "tenders.db"
        self._create_test_database()
        
        self.integration_manager = SystemIntegrationManager(
            data_dir=str(self.data_dir), 
            enable_persistence=True
        )
    
    def tearDown(self):
        # Cleanup
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _create_test_database(self):
        """Create test database for integration testing"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE tenders (
                    notice_identifier TEXT PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    organisation_name TEXT,
                    value_high INTEGER,
                    status TEXT,
                    suitable_for_sme TEXT,
                    cpv_codes TEXT,
                    closing_date TEXT,
                    published_date TEXT,
                    links TEXT,
                    contact_details TEXT
                )
            """)
            
            conn.execute("""
                INSERT INTO tenders VALUES 
                ('TEST_001', 'Digital Transformation Project', 
                 'Comprehensive digital transformation', 'NHS Digital', 
                 2500000, 'open', 'yes', '72000000', '2024-02-15', 
                 '2024-01-01', '', '')
            """)
        
        # Upgrade to Phase 2 schema
        schema_manager = DatabaseSchemaManager(str(self.db_path))
        schema_manager.upgrade_to_phase2_schema()
    
    def test_integration_status_check(self):
        """Test integration status checking"""
        status = self.integration_manager.get_integration_status()
        
        self.assertIn('database_persistence_enabled', status)
        self.assertIn('database_available', status)
        self.assertIn('component_integration_status', status)
        self.assertIn('integration_summary', status)
        
        self.assertTrue(status['database_persistence_enabled'])
        self.assertTrue(status['database_available'])
    
    @patch('system_integration.TenderClassifier')
    def test_classifier_integration(self, mock_classifier_class):
        """Test classifier component integration"""
        # Create mock classifier instance
        mock_classifier = MagicMock()
        mock_classifier_class.return_value = mock_classifier
        
        # Mock classify_tender_enhanced method
        mock_result = MagicMock()
        mock_result.notice_identifier = 'TEST_001'
        mock_result.final_relevance_score = 85.0
        mock_classifier.classify_tender_enhanced = MagicMock(return_value=mock_result)
        
        # Test integration
        success = self.integration_manager.integrate_classifier(mock_classifier)
        self.assertTrue(success)
        
        # Verify integration status updated
        status = self.integration_manager.get_integration_status()
        self.assertTrue(status['component_integration_status']['classifier_integrated'])
        
        # Test that integrated method includes persistence
        tender_data = {'notice_identifier': 'TEST_001', 'title': 'Test Tender'}
        result = mock_classifier.classify_tender_enhanced(tender_data, save_to_db=False)
        
        # Verify method was called
        self.assertIsNotNone(result)
    
    def test_database_not_available_fallback(self):
        """Test integration fallback when database not available"""
        # Create integration manager with disabled persistence
        fallback_manager = SystemIntegrationManager(enable_persistence=False)
        
        status = fallback_manager.get_integration_status()
        self.assertFalse(status['database_persistence_enabled'])
        self.assertFalse(status['database_available'])
        
        # Mock classifier for integration test
        mock_classifier = MagicMock()
        success = fallback_manager.integrate_classifier(mock_classifier)
        self.assertFalse(success)  # Should fail gracefully


class TestIntegratedPipeline(unittest.TestCase):
    """Test integrated pipeline functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir)
        
        # Create test database
        self.db_path = self.data_dir / "tenders.db"
        self._create_test_database()
        
        # Create mock components
        self.mock_classifier = MagicMock()
        self.mock_scorer = MagicMock()
        self.mock_filter = MagicMock()
        self.mock_trainer = MagicMock()
        self.mock_data_access = MagicMock()
        self.mock_integration_manager = MagicMock()
        
        self.pipeline = IntegratedTenderPipeline(
            classifier=self.mock_classifier,
            scorer=self.mock_scorer,
            opportunity_filter=self.mock_filter,
            continuous_learner=self.mock_trainer,
            data_access=self.mock_data_access,
            integration_manager=self.mock_integration_manager
        )
    
    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def _create_test_database(self):
        """Create test database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE tenders (
                    notice_identifier TEXT PRIMARY KEY,
                    title TEXT,
                    description TEXT,
                    organisation_name TEXT,
                    value_high INTEGER,
                    status TEXT,
                    suitable_for_sme TEXT,
                    cpv_codes TEXT,
                    closing_date TEXT,
                    published_date TEXT,
                    links TEXT,
                    contact_details TEXT
                )
            """)
    
    def test_process_tender_complete_success(self):
        """Test successful complete tender processing"""
        # Setup mock responses
        classification_result = MagicMock()
        classification_result.notice_identifier = 'TEST_001'
        
        enhanced_result = MagicMock()
        enhanced_result.notice_identifier = 'TEST_001'
        enhanced_result.final_relevance_score = 85.0
        enhanced_result.classification_id = 123
        
        filtered_result = MagicMock()
        filtered_result.notice_identifier = 'TEST_001'
        filtered_result.final_recommendation = 'PURSUE'
        filtered_result.classification_id = 124
        
        self.mock_classifier.classify_tender.return_value = classification_result
        self.mock_classifier.classify_tender_enhanced = MagicMock(return_value=enhanced_result)
        self.mock_filter.filter_opportunities.return_value = [filtered_result]
        
        # Test processing
        tender_data = {
            'notice_identifier': 'TEST_001',
            'title': 'Test Digital Transformation Project',
            'description': 'Test description',
            'organisation_name': 'Test Org'
        }
        
        result = self.pipeline.process_tender_complete(tender_data, save_to_db=True)
        
        # Verify results
        self.assertTrue(result['success'])
        self.assertEqual(result['notice_identifier'], 'TEST_001')
        self.assertIn('classification', result['steps_completed'])
        self.assertIn('enhanced_scoring', result['steps_completed'])
        self.assertIn('filtering', result['steps_completed'])
        self.assertEqual(result['final_result'], filtered_result)
        
        # Verify components were called
        self.mock_classifier.classify_tender.assert_called_once_with(tender_data)
        self.mock_classifier.classify_tender_enhanced.assert_called_once()
        self.mock_filter.filter_opportunities.assert_called_once()
    
    def test_process_tender_complete_with_error(self):
        """Test tender processing with error handling"""
        # Setup mock to raise exception
        self.mock_classifier.classify_tender.side_effect = Exception("Classification failed")
        
        tender_data = {'notice_identifier': 'TEST_001', 'title': 'Test Tender'}
        
        result = self.pipeline.process_tender_complete(tender_data)
        
        # Verify error handling
        self.assertFalse(result['success'])
        self.assertIn('error', result)
        self.assertEqual(result['notice_identifier'], 'TEST_001')
    
    def test_process_tenders_batch(self):
        """Test batch processing of multiple tenders"""
        # Setup mock responses for successful processing
        def mock_process_complete(tender_data, save_to_db=True):
            return {
                'notice_identifier': tender_data['notice_identifier'],
                'success': True,
                'steps_completed': ['classification', 'enhanced_scoring', 'filtering'],
                'processing_timestamp': datetime.now().isoformat()
            }
        
        # Replace process_tender_complete with mock
        self.pipeline.process_tender_complete = mock_process_complete
        
        tender_data_list = [
            {'notice_identifier': 'TEST_001', 'title': 'Tender 1'},
            {'notice_identifier': 'TEST_002', 'title': 'Tender 2'},
            {'notice_identifier': 'TEST_003', 'title': 'Tender 3'}
        ]
        
        results = self.pipeline.process_tenders_batch(tender_data_list, save_to_db=False)
        
        # Verify batch processing
        self.assertEqual(len(results), 3)
        for i, result in enumerate(results):
            self.assertTrue(result['success'])
            self.assertEqual(result['notice_identifier'], f'TEST_00{i+1}')


def run_comprehensive_tests():
    """Run all test suites for Database Schema Extensions"""
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestDatabaseSchemaManager,
        TestEnhancedDataAccess,
        TestSystemIntegration,
        TestIntegratedPipeline
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Report summary
    print(f"\n{'='*60}")
    print(f"PHASE 2 STEP 5 DATABASE EXTENSIONS TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success Rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\nFAILURES:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback.split('AssertionError:')[-1].strip()}")
    
    if result.errors:
        print(f"\nERRORS:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback.split('Exception:')[-1].strip()}")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_tests()
    exit(0 if success else 1)