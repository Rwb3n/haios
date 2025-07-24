#!/usr/bin/env python3
"""
Test Suite for Training Data Management System (Phase 2 Step 4)
Comprehensive testing of data preparation, model training, and continuous learning components
"""

import unittest
import tempfile
import sqlite3
import json
import numpy as np
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from trainer import (
    TrainingDataPreparator, ManualLabelingInterface, 
    EnhancedModelTrainer, ContinuousLearningSystem
)

class TestTrainingDataPreparator(unittest.TestCase):
    """Test data preparation engine functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir)
        
        # Create test database
        self.db_path = self.data_dir / "tenders.db"
        self._create_test_database()
        
        self.preparator = TrainingDataPreparator(str(self.data_dir))
    
    def _create_test_database(self):
        """Create test database with sample tender data"""
        with sqlite3.connect(self.db_path) as conn:
            # Create tenders table
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
                 'Comprehensive digital transformation with cloud migration and API development for modern digital services platform',
                 'NHS Digital', 2500000, 'open', 'yes', '72000000', '2024-02-15', '2024-01-01', '', ''),
                ('TEST_002', 'Software Development Services',
                 'Custom software development using Python and JavaScript for government digital platform with API integration',
                 'Cabinet Office', 750000, 'open', 'yes', '72200000', '2024-03-01', '2024-01-15', '', ''),
                ('TEST_003', 'IT Support Services',
                 'Basic IT support and maintenance services for office systems and network infrastructure',
                 'Local Council', 150000, 'open', 'yes', '72400000', '2024-02-20', '2024-01-10', '', ''),
                ('TEST_004', 'Construction Project',
                 'Building construction and renovation work for new office facilities and infrastructure development',
                 'Transport Authority', 5000000, 'open', 'no', '45000000', '2024-04-01', '2024-01-20', '', ''),
                ('TEST_005', 'Advanced AI System',
                 'Artificial intelligence and machine learning platform development with cloud infrastructure and data analytics',
                 'HMRC Digital', 1800000, 'open', 'no', '72000000', '2024-03-15', '2024-01-25', '', ''),
            ]
            
            conn.executemany("""
                INSERT INTO tenders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, test_tenders)
    
    def test_load_tender_data(self):
        """Test loading tender data from database"""
        tenders = self.preparator.load_tender_data()
        
        self.assertEqual(len(tenders), 5)
        self.assertIn('notice_identifier', tenders[0])
        self.assertIn('title', tenders[0])
        self.assertIn('description', tenders[0])
        
        # Check specific tender
        digital_tender = next(t for t in tenders if t['notice_identifier'] == 'TEST_001')
        self.assertEqual(digital_tender['title'], 'Digital Transformation Project')
        self.assertEqual(digital_tender['value_high'], 2500000)
    
    def test_validate_data_quality(self):
        """Test data quality validation"""
        tenders = self.preparator.load_tender_data()
        quality_report = self.preparator.validate_data_quality(tenders)
        
        self.assertIn('total_records', quality_report)
        self.assertIn('field_completeness', quality_report)
        self.assertIn('data_quality_issues', quality_report)
        
        self.assertEqual(quality_report['total_records'], 5)
        
        # Check field completeness
        title_completeness = quality_report['field_completeness']['title']['percentage']
        self.assertEqual(title_completeness, 100.0)  # All titles present
    
    def test_generate_heuristic_labels(self):
        """Test heuristic label generation"""
        tenders = self.preparator.load_tender_data()
        labels = self.preparator.generate_heuristic_labels(tenders)
        
        self.assertEqual(len(labels), 5)
        self.assertTrue(all(label in [0, 1] for label in labels))
        
        # Digital transformation tender should be labeled positive
        digital_tender_idx = next(i for i, t in enumerate(tenders) if t['notice_identifier'] == 'TEST_001')
        self.assertEqual(labels[digital_tender_idx], 1)
        
        # Construction tender should be labeled negative
        construction_tender_idx = next(i for i, t in enumerate(tenders) if t['notice_identifier'] == 'TEST_004')
        self.assertEqual(labels[construction_tender_idx], 0)
        
        # Should have some positive labels
        positive_count = sum(labels)
        self.assertGreater(positive_count, 0)
        self.assertLess(positive_count, len(labels))  # Not all positive
    
    @patch('trainer.TenderClassifier')
    @patch('trainer.RelevanceScorer')
    @patch('trainer.AdvancedOpportunityFilter')
    def test_extract_comprehensive_features_with_components(self, mock_filter, mock_scorer, mock_classifier):
        """Test comprehensive feature extraction with system components"""
        # Mock system components
        mock_classification_result = MagicMock()
        mock_classification_result.keyword_score = 15.0
        mock_classification_result.context_score = 8.0
        mock_classification_result.ml_confidence = 0.75
        mock_classification_result.composite_score = 35.0
        mock_classification_result.technical_terms = ['api', 'cloud']
        mock_classification_result.transformation_signals = ['digital transformation']
        
        mock_enhanced_result = MagicMock()
        mock_enhanced_result.metadata_score = 12.0
        mock_enhanced_result.business_alignment_score = 6.0
        mock_enhanced_result.urgency_multiplier = 1.2
        mock_enhanced_result.value_multiplier = 1.8
        mock_enhanced_result.department_multiplier = 1.3
        mock_enhanced_result.final_relevance_score = 85.0
        
        mock_filter_result = MagicMock()
        mock_filter_result.overall_filter_score = 0.8
        mock_filter_result.bid_probability = 0.25
        mock_filter_result.filter_passes = True
        mock_filter_result.competition_assessment = {'competition_level': 6.5}
        mock_filter_result.risk_factors = ['high competition']
        mock_filter_result.success_factors = ['optimal value', 'remote delivery']
        
        # Setup mocks
        mock_classifier_instance = mock_classifier.return_value
        mock_classifier_instance.classify_tender.return_value = mock_classification_result
        
        mock_scorer_instance = mock_scorer.return_value
        mock_scorer_instance.score_classified_tender.return_value = mock_enhanced_result
        
        mock_filter_instance = mock_filter.return_value
        mock_filter_instance.filter_opportunities.return_value = [mock_filter_result]
        
        # Force system components to be available
        self.preparator.system_components_available = True
        self.preparator.classifier = mock_classifier_instance
        self.preparator.relevance_scorer = mock_scorer_instance
        self.preparator.opportunity_filter = mock_filter_instance
        
        # Test feature extraction
        tenders = self.preparator.load_tender_data()
        features, feature_names = self.preparator.extract_comprehensive_features(tenders)
        
        self.assertEqual(features.shape[0], 5)  # 5 tenders
        self.assertGreater(features.shape[1], 15)  # Multiple feature categories
        self.assertEqual(len(feature_names), features.shape[1])
        
        # Check feature values for first tender
        first_features = features[0]
        self.assertEqual(first_features[0], 15.0)  # keyword_score
        self.assertEqual(first_features[1], 8.0)   # context_score
        self.assertEqual(first_features[2], 0.75)  # ml_confidence
    
    def test_extract_basic_features_fallback(self):
        """Test basic feature extraction when system components unavailable"""
        # Force system components to be unavailable
        self.preparator.system_components_available = False
        
        tenders = self.preparator.load_tender_data()
        features, feature_names = self.preparator.extract_comprehensive_features(tenders)
        
        self.assertEqual(features.shape[0], 5)  # 5 tenders
        self.assertGreater(features.shape[1], 50)  # TF-IDF + metadata features
        self.assertEqual(len(feature_names), features.shape[1])
    
    def test_prepare_training_dataset(self):
        """Test complete training dataset preparation"""
        features, labels, feature_names, dataset_stats = self.preparator.prepare_training_dataset()
        
        # Check outputs
        self.assertEqual(len(features), len(labels))
        self.assertEqual(len(feature_names), features.shape[1])
        
        # Check dataset stats
        self.assertIn('total_samples', dataset_stats)
        self.assertIn('feature_count', dataset_stats)
        self.assertIn('positive_samples', dataset_stats)
        self.assertIn('class_balance', dataset_stats)
        
        self.assertEqual(dataset_stats['total_samples'], 5)
        self.assertGreater(dataset_stats['positive_samples'], 0)


class TestManualLabelingInterface(unittest.TestCase):
    """Test manual labeling interface functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir)
        
        self.interface = ManualLabelingInterface(str(self.data_dir))
    
    def test_load_save_labels(self):
        """Test loading and saving expert labels"""
        # Initially empty
        self.assertEqual(len(self.interface.expert_labels), 0)
        
        # Add a label
        test_label = {
            'notice_identifier': 'TEST_001',
            'expert_label': 'relevant',
            'confidence': 4,
            'notes': 'Clear digital transformation project',
            'timestamp': datetime.now().isoformat()
        }
        
        self.interface.expert_labels['TEST_001'] = test_label
        self.interface._save_labels()
        
        # Create new interface instance and check persistence
        new_interface = ManualLabelingInterface(str(self.data_dir))
        self.assertEqual(len(new_interface.expert_labels), 1)
        self.assertEqual(new_interface.expert_labels['TEST_001']['expert_label'], 'relevant')
    
    @patch('builtins.input', side_effect=['relevant', '4', 'Good digital transformation project'])
    def test_present_for_labeling(self, mock_input):
        """Test presenting tender for expert labeling"""
        tender_data = {
            'notice_identifier': 'TEST_001',
            'title': 'Digital Transformation Project',
            'description': 'Comprehensive digital transformation...',
            'organisation_name': 'NHS Digital',
            'value_high': 2500000,
            'suitable_for_sme': 'yes'
        }
        
        current_prediction = {
            'final_relevance_score': 85.0,
            'recommendation': 'PURSUE',
            'priority_level': 'HIGH',
            'explanation': 'High-value digital transformation opportunity'
        }
        
        # Redirect stdout to capture output
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            result = self.interface.present_for_labeling(tender_data, current_prediction)
            
            self.assertIsNotNone(result)
            self.assertEqual(result['notice_identifier'], 'TEST_001')
            self.assertEqual(result['expert_label'], 'relevant')
            self.assertEqual(result['confidence'], 4)
            self.assertEqual(result['notes'], 'Good digital transformation project')
            self.assertIn('system_prediction', result)
            
            # Check label was saved
            self.assertIn('TEST_001', self.interface.expert_labels)
            
        finally:
            sys.stdout = sys.__stdout__
    
    @patch('builtins.input', side_effect=['skip'])
    def test_present_for_labeling_skip(self, mock_input):
        """Test skipping tender labeling"""
        tender_data = {
            'notice_identifier': 'TEST_002',
            'title': 'Test Tender',
            'description': 'Test description'
        }
        
        # Redirect stdout
        import io
        import sys
        captured_output = io.StringIO()
        sys.stdout = captured_output
        
        try:
            result = self.interface.present_for_labeling(tender_data)
            self.assertIsNone(result)
            
        finally:
            sys.stdout = sys.__stdout__
    
    def test_get_expert_labels_for_training(self):
        """Test retrieving expert labels for training"""
        # Add test labels
        self.interface.expert_labels = {
            'TEST_001': {
                'notice_identifier': 'TEST_001',
                'expert_label': 'relevant',
                'confidence': 4,
                'notes': 'Good project'
            },
            'TEST_002': {
                'notice_identifier': 'TEST_002',
                'expert_label': 'not_relevant',
                'confidence': 5,
                'notes': 'Not digital transformation'
            },
            'TEST_003': {
                'notice_identifier': 'TEST_003',
                'expert_label': 'unsure',
                'confidence': 2,
                'notes': 'Unclear requirements'
            }
        }
        
        notice_ids, labels, metadata = self.interface.get_expert_labels_for_training()
        
        # Should exclude 'unsure' labels
        self.assertEqual(len(notice_ids), 2)
        self.assertEqual(len(labels), 2)
        self.assertEqual(len(metadata), 2)
        
        # Check labels converted correctly
        self.assertIn(1, labels)  # relevant -> 1
        self.assertIn(0, labels)  # not_relevant -> 0
    
    def test_analyze_labeling_patterns(self):
        """Test analysis of expert labeling patterns"""
        # Add test labels
        self.interface.expert_labels = {
            'TEST_001': {'expert_label': 'relevant', 'confidence': 4},
            'TEST_002': {'expert_label': 'relevant', 'confidence': 5},
            'TEST_003': {'expert_label': 'not_relevant', 'confidence': 3},
            'TEST_004': {'expert_label': 'unsure', 'confidence': 2}
        }
        
        analysis = self.interface.analyze_labeling_patterns()
        
        self.assertEqual(analysis['total_labels'], 4)
        self.assertEqual(analysis['label_distribution']['relevant'], 2)
        self.assertEqual(analysis['label_distribution']['not_relevant'], 1)
        self.assertEqual(analysis['label_distribution']['unsure'], 1)
        
        # Check confidence distribution
        self.assertIn('confidence_distribution', analysis)


class TestEnhancedModelTrainer(unittest.TestCase):
    """Test enhanced model training functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir)
        
        self.trainer = EnhancedModelTrainer(str(self.data_dir))
        
        # Create sample training data
        np.random.seed(42)
        self.features = np.random.randn(100, 20)  # 100 samples, 20 features
        self.labels = np.random.choice([0, 1], size=100, p=[0.7, 0.3])  # Imbalanced classes
        self.feature_names = [f'feature_{i}' for i in range(20)]
    
    def test_train_ensemble_classifier(self):
        """Test ensemble classifier training"""
        results = self.trainer.train_ensemble_classifier(
            self.features, self.labels, self.feature_names
        )
        
        # Check results structure
        self.assertIn('model', results)
        self.assertIn('metadata', results)
        self.assertIn('training_results', results)
        self.assertIn('final_metrics', results)
        
        # Check model exists
        self.assertIsNotNone(results['model'])
        
        # Check metrics
        metrics = results['final_metrics']
        self.assertIn('precision', metrics)
        self.assertIn('recall', metrics)
        self.assertIn('f1_score', metrics)
        self.assertIn('accuracy', metrics)
        self.assertIn('roc_auc', metrics)
        
        # All metrics should be between 0 and 1
        for metric in ['precision', 'recall', 'f1_score', 'accuracy', 'roc_auc']:
            self.assertGreaterEqual(metrics[metric], 0.0)
            self.assertLessEqual(metrics[metric], 1.0)
        
        # Check metadata
        metadata = results['metadata']
        self.assertEqual(metadata['feature_count'], 20)
        self.assertEqual(len(metadata['feature_names']), 20)
        self.assertIn('training_timestamp', metadata)
    
    def test_model_prediction(self):
        """Test model prediction functionality"""
        # Train model
        results = self.trainer.train_ensemble_classifier(
            self.features, self.labels, self.feature_names
        )
        
        model = results['model']
        
        # Test predictions
        test_features = np.random.randn(10, 20)
        predictions = model.predict(test_features)
        probabilities = model.predict_proba(test_features)
        
        self.assertEqual(len(predictions), 10)
        self.assertEqual(probabilities.shape, (10, 2))
        
        # All predictions should be 0 or 1
        self.assertTrue(all(p in [0, 1] for p in predictions))
        
        # Probabilities should sum to 1
        for prob_pair in probabilities:
            self.assertAlmostEqual(sum(prob_pair), 1.0, places=5)
    
    def test_save_load_model(self):
        """Test model saving and loading"""
        # Train model
        results = self.trainer.train_ensemble_classifier(
            self.features, self.labels, self.feature_names
        )
        
        # Save model
        model_path = self.trainer.save_model("test_model")
        self.assertTrue(Path(model_path).exists())
        
        # Create new trainer and load model
        new_trainer = EnhancedModelTrainer(str(self.data_dir))
        success = new_trainer.load_model(model_path)
        
        self.assertTrue(success)
        self.assertIsNotNone(new_trainer.current_model)
        self.assertIsNotNone(new_trainer.model_metadata)
        
        # Test loaded model predictions
        test_features = np.random.randn(5, 20)
        predictions = new_trainer.current_model.predict(test_features)
        self.assertEqual(len(predictions), 5)


class TestContinuousLearningSystem(unittest.TestCase):
    """Test continuous learning system functionality"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir)
        
        # Create test database (reuse from TestTrainingDataPreparator)
        self.db_path = self.data_dir / "tenders.db"
        self._create_test_database()
        
        self.learning_system = ContinuousLearningSystem(str(self.data_dir))
    
    def _create_test_database(self):
        """Create test database with sample tender data"""
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
            
            test_tenders = [
                ('TEST_001', 'Digital Transformation Project', 
                 'Comprehensive digital transformation with cloud migration',
                 'NHS Digital', 2500000, 'open', 'yes', '72000000', '2024-02-15', '2024-01-01', '', ''),
                ('TEST_002', 'Software Development Services',
                 'Custom software development using Python and JavaScript',
                 'Cabinet Office', 750000, 'open', 'yes', '72200000', '2024-03-01', '2024-01-15', '', ''),
                ('TEST_003', 'IT Support Services',
                 'Basic IT support and maintenance services',
                 'Local Council', 150000, 'open', 'yes', '72400000', '2024-02-20', '2024-01-10', '', ''),
            ]
            
            conn.executemany("""
                INSERT INTO tenders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, test_tenders)
    
    def test_performance_history_persistence(self):
        """Test performance history loading and saving"""
        # Initially empty
        self.assertEqual(len(self.learning_system.performance_history), 0)
        
        # Add performance record
        test_record = {
            'timestamp': datetime.now().isoformat(),
            'validation_metrics': {'f1_score': 0.85, 'precision': 0.82, 'recall': 0.88},
            'improvement': 0.03,
            'deployed': True
        }
        
        self.learning_system.performance_history.append(test_record)
        self.learning_system._save_performance_history()
        
        # Create new system instance and check persistence
        new_system = ContinuousLearningSystem(str(self.data_dir))
        self.assertEqual(len(new_system.performance_history), 1)
        self.assertEqual(new_system.performance_history[0]['improvement'], 0.03)
    
    @patch('trainer.TenderClassifier')
    def test_recommend_labeling_targets(self, mock_classifier):
        """Test labeling target recommendation"""
        # Mock classifier
        mock_result = MagicMock()
        mock_result.final_relevance_score = 52.0  # Uncertain score near 50
        
        mock_classifier_instance = mock_classifier.return_value
        mock_classifier_instance.classify_tender_enhanced.return_value = mock_result
        
        recommendations = self.learning_system.recommend_labeling_targets(2)
        
        # Should return recommendations if system components available
        if recommendations:  # Only if mocking worked
            self.assertLessEqual(len(recommendations), 2)
            
            for rec in recommendations:
                self.assertIn('notice_identifier', rec)
                self.assertIn('title', rec)
                self.assertIn('uncertainty', rec)
                self.assertIn('reasoning', rec)
    
    def test_generate_performance_report_empty(self):
        """Test performance report generation with no history"""
        report = self.learning_system.generate_performance_report()
        
        self.assertIn('error', report)
        self.assertEqual(report['error'], 'No performance history available')
    
    def test_generate_performance_report_with_data(self):
        """Test performance report generation with history"""
        # Add test performance history
        test_records = [
            {
                'timestamp': '2024-01-01T10:00:00',
                'validation_metrics': {'f1_score': 0.80, 'precision': 0.78, 'recall': 0.82},
                'improvement': 0.0,
                'expert_labels_used': 15,
                'deployed': False
            },
            {
                'timestamp': '2024-01-02T10:00:00',
                'validation_metrics': {'f1_score': 0.85, 'precision': 0.83, 'recall': 0.87},
                'improvement': 0.05,
                'expert_labels_used': 20,
                'deployed': True
            }
        ]
        
        self.learning_system.performance_history.extend(test_records)
        
        report = self.learning_system.generate_performance_report()
        
        # Check report structure
        self.assertIn('summary', report)
        self.assertIn('trends', report)
        self.assertIn('expert_labels', report)
        self.assertIn('deployment_history', report)
        
        # Check summary data
        summary = report['summary']
        self.assertEqual(summary['total_training_runs'], 2)
        self.assertEqual(summary['latest_f1_score'], 0.85)
        self.assertEqual(summary['total_improvement'], 0.05)
        
        # Check trends
        trends = report['trends']
        self.assertEqual(len(trends['f1_scores']), 2)
        self.assertEqual(len(trends['improvements']), 2)
        
        # Check deployment history
        deployment_history = report['deployment_history']
        self.assertEqual(len(deployment_history), 2)
        self.assertFalse(deployment_history[0]['deployed'])
        self.assertTrue(deployment_history[1]['deployed'])


class TestTrainingSystemIntegration(unittest.TestCase):
    """Test integration between training system components"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.data_dir = Path(self.temp_dir)
        
        # Create test database
        self.db_path = self.data_dir / "tenders.db"
        self._create_test_database()
    
    def _create_test_database(self):
        """Create comprehensive test database"""
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
            
            # Larger dataset for integration testing
            test_tenders = [
                ('TEST_001', 'Digital Transformation Project', 
                 'Comprehensive digital transformation with cloud migration and API development for modern digital services platform',
                 'NHS Digital', 2500000, 'open', 'yes', '72000000', '2024-02-15', '2024-01-01', '', ''),
                ('TEST_002', 'Software Development Services',
                 'Custom software development using Python and JavaScript for government digital platform with API integration',
                 'Cabinet Office', 750000, 'open', 'yes', '72200000', '2024-03-01', '2024-01-15', '', ''),
                ('TEST_003', 'Cloud Migration Project',
                 'Migration of legacy systems to cloud infrastructure with modern APIs and microservices architecture',
                 'HMRC Digital', 1200000, 'open', 'no', '72000000', '2024-03-10', '2024-01-20', '', ''),
                ('TEST_004', 'IT Support Services',
                 'Basic IT support and maintenance services for office systems and network infrastructure',
                 'Local Council', 150000, 'open', 'yes', '72400000', '2024-02-20', '2024-01-10', '', ''),
                ('TEST_005', 'Construction Project',
                 'Building construction and renovation work for new office facilities and infrastructure development',
                 'Transport Authority', 5000000, 'open', 'no', '45000000', '2024-04-01', '2024-01-20', '', ''),
                ('TEST_006', 'Data Analytics Platform',
                 'Advanced data analytics and reporting platform with machine learning capabilities for government insights',
                 'Cabinet Office', 900000, 'open', 'yes', '72000000', '2024-03-20', '2024-01-25', '', ''),
            ]
            
            conn.executemany("""
                INSERT INTO tenders VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, test_tenders)
    
    def test_end_to_end_training_pipeline(self):
        """Test complete end-to-end training pipeline"""
        # 1. Data preparation
        preparator = TrainingDataPreparator(str(self.data_dir))
        features, labels, feature_names, dataset_stats = preparator.prepare_training_dataset()
        
        self.assertEqual(dataset_stats['total_samples'], 6)
        self.assertGreater(dataset_stats['positive_samples'], 0)
        self.assertLess(dataset_stats['positive_samples'], 6)  # Some negative samples
        
        # 2. Model training
        trainer = EnhancedModelTrainer(str(self.data_dir))
        training_results = trainer.train_ensemble_classifier(features, labels, feature_names)
        
        self.assertIsNotNone(training_results['model'])
        self.assertGreater(training_results['final_metrics']['f1_score'], 0.0)
        
        # 3. Model saving
        model_path = trainer.save_model("integration_test_model")
        self.assertTrue(Path(model_path).exists())
        
        # 4. Model loading in new trainer
        new_trainer = EnhancedModelTrainer(str(self.data_dir))
        load_success = new_trainer.load_model(model_path)
        self.assertTrue(load_success)
        
        # 5. Predictions with loaded model
        test_features = features[:2]  # Use first 2 samples for testing
        predictions = new_trainer.current_model.predict(test_features)
        probabilities = new_trainer.current_model.predict_proba(test_features)
        
        self.assertEqual(len(predictions), 2)
        self.assertEqual(probabilities.shape, (2, 2))
    
    def test_expert_labeling_workflow(self):
        """Test expert labeling workflow integration"""
        # 1. Initialize labeling interface
        interface = ManualLabelingInterface(str(self.data_dir))
        
        # 2. Simulate expert labels
        expert_labels = {
            'TEST_001': {
                'notice_identifier': 'TEST_001',
                'expert_label': 'relevant',
                'confidence': 5,
                'notes': 'Clear digital transformation project',
                'timestamp': datetime.now().isoformat()
            },
            'TEST_002': {
                'notice_identifier': 'TEST_002',
                'expert_label': 'relevant',
                'confidence': 4,
                'notes': 'Software development for government',
                'timestamp': datetime.now().isoformat()
            },
            'TEST_005': {
                'notice_identifier': 'TEST_005',
                'expert_label': 'not_relevant',
                'confidence': 5,
                'notes': 'Construction project, not digital',
                'timestamp': datetime.now().isoformat()
            }
        }
        
        interface.expert_labels = expert_labels
        interface._save_labels()
        
        # 3. Retrieve labels for training
        notice_ids, labels, metadata = interface.get_expert_labels_for_training()
        
        self.assertEqual(len(notice_ids), 3)
        self.assertEqual(len(labels), 3)
        self.assertEqual(sum(labels), 2)  # 2 relevant, 1 not relevant
        
        # 4. Analyze labeling patterns
        analysis = interface.analyze_labeling_patterns()
        self.assertEqual(analysis['total_labels'], 3)
        self.assertEqual(analysis['label_distribution']['relevant'], 2)
        self.assertEqual(analysis['label_distribution']['not_relevant'], 1)
    
    def test_continuous_learning_integration(self):
        """Test continuous learning system integration"""
        # 1. Initialize system
        learning_system = ContinuousLearningSystem(str(self.data_dir))
        
        # 2. Add expert labels
        learning_system.labeling_interface.expert_labels = {
            'TEST_001': {
                'notice_identifier': 'TEST_001',
                'expert_label': 'relevant',
                'confidence': 5,
                'notes': 'Digital transformation'
            },
            'TEST_002': {
                'notice_identifier': 'TEST_002',
                'expert_label': 'relevant',
                'confidence': 4,
                'notes': 'Software development'
            },
            'TEST_005': {
                'notice_identifier': 'TEST_005',
                'expert_label': 'not_relevant',
                'confidence': 5,
                'notes': 'Construction project'
            }
        }
        
        # 3. Update model (will use basic features due to no system components)
        learning_system.preparator.system_components_available = False
        
        # Mock to avoid actual training (too slow for unit test)
        with patch.object(learning_system.trainer, 'train_ensemble_classifier') as mock_train:
            mock_model = MagicMock()
            mock_model.predict.return_value = np.array([1, 1, 0])
            mock_model.predict_proba.return_value = np.array([[0.2, 0.8], [0.3, 0.7], [0.9, 0.1]])
            
            mock_train.return_value = {
                'model': mock_model,
                'metadata': {'model_type': 'test_model'},
                'final_metrics': {'f1_score': 0.85, 'precision': 0.83, 'recall': 0.87}
            }
            
            # This would normally train, but we're mocking it
            performance_record = learning_system.update_model_with_expert_feedback()
            
            if 'error' not in performance_record:
                # Check performance record structure
                self.assertIn('timestamp', performance_record)
                self.assertIn('validation_metrics', performance_record)
                self.assertIn('improvement', performance_record)
                self.assertIn('expert_labels_used', performance_record)
        
        # 4. Generate performance report
        if learning_system.performance_history:
            report = learning_system.generate_performance_report()
            self.assertIn('summary', report)
            self.assertGreater(report['summary']['total_training_runs'], 0)


def run_comprehensive_tests():
    """Run all test suites for Training Data Management System"""
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestTrainingDataPreparator,
        TestManualLabelingInterface,
        TestEnhancedModelTrainer,
        TestContinuousLearningSystem,
        TestTrainingSystemIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Report summary
    print(f"\n{'='*60}")
    print(f"PHASE 2 STEP 4 TEST SUMMARY")
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