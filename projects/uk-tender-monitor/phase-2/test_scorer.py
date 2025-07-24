#!/usr/bin/env python3
"""
Test Suite for Enhanced Relevance Scoring System (Phase 2 Step 2)
Comprehensive testing of metadata analysis, business alignment, and multiplier systems
"""

import unittest
import tempfile
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

from scorer import (
    RelevanceScorer, MetadataAnalyzer, BusinessAlignmentAnalyzer, 
    MultiplierCalculator, EnhancedClassificationResult
)
from classifier import ClassificationResult, TenderClassifier

class TestMetadataAnalyzer(unittest.TestCase):
    """Test metadata analysis components"""
    
    def setUp(self):
        self.analyzer = MetadataAnalyzer()
    
    def test_cpv_code_analysis_high_relevance(self):
        """Test CPV code analysis for IT services"""
        cpv_codes = "72000000,45000000"  # IT services + construction
        score, breakdown = self.analyzer.analyze_cpv_codes(cpv_codes)
        
        self.assertEqual(score, 5)  # Should match highest score (IT services)
        self.assertEqual(breakdown['matched_cpv']['score'], 5)
        self.assertIn('IT services', breakdown['matched_cpv']['description'])
    
    def test_cpv_code_analysis_medium_relevance(self):
        """Test CPV code analysis for medium relevance"""
        cpv_codes = "72400000"  # Internet services
        score, breakdown = self.analyzer.analyze_cpv_codes(cpv_codes)
        
        self.assertEqual(score, 3)
        self.assertEqual(breakdown['status'], 'relevant_cpv_found')
    
    def test_cpv_code_analysis_no_relevance(self):
        """Test CPV code analysis with no relevant codes"""
        cpv_codes = "45000000,03000000"  # Construction + agriculture
        score, breakdown = self.analyzer.analyze_cpv_codes(cpv_codes)
        
        self.assertEqual(score, 0)
        self.assertEqual(breakdown['status'], 'no_relevant_cpv')
    
    def test_cpv_code_analysis_empty(self):
        """Test CPV code analysis with no codes"""
        score, breakdown = self.analyzer.analyze_cpv_codes("")
        
        self.assertEqual(score, 0)
        self.assertEqual(breakdown['status'], 'no_cpv_codes')
    
    def test_organization_analysis_high_tech(self):
        """Test organization analysis for high-tech orgs"""
        org_name = "NHS Digital Technology Services"
        score, breakdown = self.analyzer.analyze_organization_type(org_name)
        
        self.assertEqual(score, 4)
        self.assertEqual(breakdown['category'], 'high_tech')
        # The matched keyword might be 'digital' or 'nhs digital' depending on order
        self.assertIn(breakdown['matched_keyword'], ['digital', 'nhs digital'])
    
    def test_organization_analysis_government_core(self):
        """Test organization analysis for core government"""
        org_name = "Cabinet Office Digital Service"
        score, breakdown = self.analyzer.analyze_organization_type(org_name)
        
        self.assertGreaterEqual(score, 3)  # Should match high_tech or government_core
        self.assertIn(breakdown['category'], ['high_tech', 'government_core'])
    
    def test_organization_analysis_health_sector(self):
        """Test organization analysis for health sector"""
        org_name = "University Hospitals NHS Foundation Trust"
        score, breakdown = self.analyzer.analyze_organization_type(org_name)
        
        self.assertEqual(score, 3)
        self.assertEqual(breakdown['category'], 'health_sector')
    
    def test_value_bracket_analysis(self):
        """Test value bracket analysis"""
        test_cases = [
            (750000, 3, 'large'),      # Large contract
            (150000, 2, 'medium'),     # Medium contract
            (75000, 1, 'small'),       # Small contract
            (10000, 0, 'too_small'),   # Too small
            (5000000, 3, 'very_large') # Very large
        ]
        
        for value, expected_score, expected_bracket in test_cases:
            with self.subTest(value=value):
                score, breakdown = self.analyzer.analyze_value_bracket(value)
                self.assertEqual(score, expected_score)
                self.assertEqual(breakdown['bracket'], expected_bracket)
    
    def test_timeline_analysis(self):
        """Test timeline analysis"""
        # Future dates for testing
        future_7_days = (datetime.now() + timedelta(days=7)).isoformat()
        future_30_days = (datetime.now() + timedelta(days=30)).isoformat()
        future_90_days = (datetime.now() + timedelta(days=90)).isoformat()
        past_date = (datetime.now() - timedelta(days=5)).isoformat()
        
        test_cases = [
            (future_7_days, 1, 'very_urgent'),
            (future_30_days, 2, 'urgent'),
            (future_90_days, 3, 'good_timing'),
            (past_date, 0, 'expired')
        ]
        
        for date_str, expected_score, expected_status in test_cases:
            with self.subTest(date=date_str):
                score, breakdown = self.analyzer.analyze_timeline(date_str, None)
                self.assertEqual(score, expected_score)
                self.assertEqual(breakdown['status'], expected_status)
    
    def test_comprehensive_metadata_analysis(self):
        """Test full metadata analysis integration"""
        tender_data = {
            'cpv_codes': '72000000',
            'organisation_name': 'NHS Digital',
            'value_high': 500000,
            'closing_date': (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        total_score, breakdown = self.analyzer.analyze_metadata(tender_data)
        
        self.assertGreaterEqual(total_score, 10)  # Should be high scoring
        self.assertIn('cpv_analysis', breakdown)
        self.assertIn('organization_analysis', breakdown)
        self.assertIn('value_analysis', breakdown)
        self.assertIn('timeline_analysis', breakdown)

class TestBusinessAlignmentAnalyzer(unittest.TestCase):
    """Test business alignment assessment"""
    
    def setUp(self):
        self.analyzer = BusinessAlignmentAnalyzer()
    
    def test_capability_assessment_high_complexity(self):
        """Test high complexity capability assessment"""
        text = "comprehensive digital transformation and enterprise architecture project"
        score, breakdown = self.analyzer.assess_capability_requirements(text)
        
        self.assertEqual(score, 3)
        self.assertEqual(breakdown['complexity_level'], 'high_complexity')
        self.assertIn('digital transformation', breakdown['matched_term'])
    
    def test_capability_assessment_medium_complexity(self):
        """Test medium complexity capability assessment"""
        text = "software development and api development for cloud migration"
        score, breakdown = self.analyzer.assess_capability_requirements(text)
        
        self.assertGreaterEqual(score, 2)
        self.assertIn(breakdown['complexity_level'], ['medium_complexity', 'high_complexity'])
    
    def test_tech_stack_alignment_preferred(self):
        """Test technology stack alignment with preferred tech"""
        text = "python django api with react frontend and aws cloud infrastructure"
        score, breakdown = self.analyzer.assess_tech_stack_alignment(text)
        
        self.assertGreaterEqual(score, 1.5)  # Should be high alignment
        self.assertGreaterEqual(breakdown['preferred_count'], 2)
        self.assertEqual(breakdown['alignment_level'], 'high_alignment')
    
    def test_tech_stack_alignment_supported(self):
        """Test technology stack alignment with supported tech"""
        text = "java spring application with mysql database"
        score, breakdown = self.analyzer.assess_tech_stack_alignment(text)
        
        self.assertGreaterEqual(score, 1)
        self.assertGreaterEqual(breakdown['supported_count'], 1)
    
    def test_tech_stack_alignment_legacy(self):
        """Test technology stack with legacy concerns"""
        text = "cobol mainframe system with oracle database"
        score, breakdown = self.analyzer.assess_tech_stack_alignment(text)
        
        self.assertEqual(score, 0.5)
        self.assertEqual(breakdown['alignment_level'], 'legacy_concerns')
        self.assertGreaterEqual(breakdown['legacy_count'], 1)
    
    def test_delivery_model_remote_friendly(self):
        """Test delivery model assessment for remote work"""
        text = "remote development team with distributed architecture"
        score, breakdown = self.analyzer.assess_delivery_model(text)
        
        self.assertEqual(score, 1.5)
        self.assertEqual(breakdown['model'], 'remote_friendly')
    
    def test_delivery_model_onsite_required(self):
        """Test delivery model for on-site requirements"""
        text = "on-site development team required at client premises"
        score, breakdown = self.analyzer.assess_delivery_model(text)
        
        self.assertEqual(score, 0.5)
        self.assertEqual(breakdown['model'], 'onsite_required')
    
    def test_strategic_priority_high(self):
        """Test strategic priority assessment"""
        tender_data = {
            'title': 'Digital Transformation Initiative',
            'description': 'Comprehensive modernization and innovation project to improve citizen services'
        }
        
        score, breakdown = self.analyzer.assess_strategic_priority(tender_data)
        
        self.assertEqual(score, 1.0)
        self.assertEqual(breakdown['priority_level'], 'high')
        self.assertGreaterEqual(len(breakdown['matched_terms']), 2)
    
    def test_comprehensive_business_alignment(self):
        """Test full business alignment analysis"""
        tender_data = {
            'title': 'Digital Health Platform',
            'description': 'Modern python-based healthcare system with react frontend, cloud deployment, and digital transformation focus'
        }
        
        total_score, breakdown = self.analyzer.assess_business_alignment(tender_data)
        
        self.assertGreaterEqual(total_score, 5)  # Should be well aligned
        self.assertIn('capability_assessment', breakdown)
        self.assertIn('technology_alignment', breakdown)
        self.assertIn('delivery_model', breakdown)
        self.assertIn('strategic_priority', breakdown)

class TestMultiplierCalculator(unittest.TestCase):
    """Test multiplier factor calculations"""
    
    def setUp(self):
        self.calculator = MultiplierCalculator()
    
    def test_urgency_multiplier_urgent(self):
        """Test urgency multiplier for urgent opportunities"""
        tender_data = {
            'closing_date': (datetime.now() + timedelta(days=10)).isoformat()
        }
        
        multiplier, breakdown = self.calculator.calculate_urgency_multiplier(tender_data)
        
        self.assertEqual(multiplier, 1.5)
        self.assertEqual(breakdown['status'], 'urgent')
        self.assertLessEqual(breakdown['days_remaining'], 14)
    
    def test_urgency_multiplier_soon(self):
        """Test urgency multiplier for soon opportunities"""
        tender_data = {
            'closing_date': (datetime.now() + timedelta(days=25)).isoformat()
        }
        
        multiplier, breakdown = self.calculator.calculate_urgency_multiplier(tender_data)
        
        self.assertEqual(multiplier, 1.3)
        self.assertEqual(breakdown['status'], 'soon')
    
    def test_urgency_multiplier_expired(self):
        """Test urgency multiplier for expired opportunities"""
        tender_data = {
            'closing_date': (datetime.now() - timedelta(days=5)).isoformat()
        }
        
        multiplier, breakdown = self.calculator.calculate_urgency_multiplier(tender_data)
        
        self.assertEqual(multiplier, 0.5)
        self.assertEqual(breakdown['status'], 'expired')
    
    def test_value_multiplier_sweet_spot(self):
        """Test value multiplier for sweet spot range"""
        tender_data = {'value_high': 300000}
        
        multiplier, breakdown = self.calculator.calculate_value_multiplier(tender_data)
        
        self.assertEqual(multiplier, 1.4)
        self.assertEqual(breakdown['bracket'], 'sweet_spot')
    
    def test_value_multiplier_high_value(self):
        """Test value multiplier for high value contracts"""
        tender_data = {'value_high': 1000000}
        
        multiplier, breakdown = self.calculator.calculate_value_multiplier(tender_data)
        
        self.assertEqual(multiplier, 1.8)
        self.assertEqual(breakdown['bracket'], 'high_value')
    
    def test_value_multiplier_too_small(self):
        """Test value multiplier for small contracts"""
        tender_data = {'value_high': 25000}
        
        multiplier, breakdown = self.calculator.calculate_value_multiplier(tender_data)
        
        self.assertEqual(multiplier, 0.5)
        self.assertEqual(breakdown['bracket'], 'too_small')
    
    def test_department_multiplier_high_preference(self):
        """Test department multiplier for preferred organizations"""
        tender_data = {'organisation_name': 'NHS Digital Technology Services'}
        
        multiplier, breakdown = self.calculator.calculate_department_multiplier(tender_data)
        
        self.assertEqual(multiplier, 1.3)
        self.assertEqual(breakdown['preference'], 'high')
    
    def test_department_multiplier_medium_preference(self):
        """Test department multiplier for medium preference orgs"""
        tender_data = {'organisation_name': 'University of Edinburgh'}
        
        multiplier, breakdown = self.calculator.calculate_department_multiplier(tender_data)
        
        self.assertEqual(multiplier, 1.1)
        self.assertEqual(breakdown['preference'], 'medium')
    
    def test_competition_multiplier_sme_friendly(self):
        """Test competition multiplier for SME-friendly contracts"""
        tender_data = {
            'value_high': 200000,
            'suitable_for_sme': 'yes'
        }
        
        multiplier, breakdown = self.calculator.calculate_competition_multiplier(tender_data)
        
        self.assertEqual(multiplier, 1.2)
        self.assertEqual(breakdown['level'], 'low')
        self.assertEqual(breakdown['reason'], 'sme_friendly')
    
    def test_competition_multiplier_very_high_value(self):
        """Test competition multiplier for very high value contracts"""
        tender_data = {
            'value_high': 8000000,
            'suitable_for_sme': 'no'
        }
        
        multiplier, breakdown = self.calculator.calculate_competition_multiplier(tender_data)
        
        self.assertEqual(multiplier, 0.7)
        self.assertEqual(breakdown['level'], 'very_high')

class TestRelevanceScorer(unittest.TestCase):
    """Test the main relevance scoring engine"""
    
    def setUp(self):
        self.scorer = RelevanceScorer()
        
        # Mock classification result
        self.mock_classification = ClassificationResult(
            notice_identifier='test_001',
            keyword_score=15.0,
            context_score=8.5,
            ml_confidence=0.85,
            composite_score=25.0,
            explanation='Test classification',
            technical_terms=['api', 'cloud', 'python'],
            transformation_signals=['digital transformation']
        )
    
    def test_enhanced_scoring_high_quality_opportunity(self):
        """Test enhanced scoring for high-quality opportunity"""
        tender_data = {
            'notice_identifier': 'test_001',
            'title': 'Digital Health Platform',
            'description': 'Modern python healthcare system with cloud architecture and digital transformation focus',
            'organisation_name': 'NHS Digital',
            'value_high': 750000,
            'cpv_codes': '72000000',
            'suitable_for_sme': 'yes',
            'closing_date': (datetime.now() + timedelta(days=21)).isoformat()
        }
        
        result = self.scorer.score_classified_tender(tender_data, self.mock_classification)
        
        # Should be high scoring
        self.assertGreaterEqual(result.final_relevance_score, 50)
        self.assertEqual(result.priority_level, 'HIGH')
        self.assertGreater(result.urgency_multiplier, 1.0)
        self.assertGreater(result.value_multiplier, 1.0)
        self.assertGreater(result.department_multiplier, 1.0)
    
    def test_enhanced_scoring_medium_opportunity(self):
        """Test enhanced scoring for medium opportunity"""
        tender_data = {
            'notice_identifier': 'test_002',
            'title': 'Software Development Services',
            'description': 'Java application development with database integration',
            'organisation_name': 'Local Council',
            'value_high': 150000,
            'cpv_codes': '72200000',
            'suitable_for_sme': 'yes',
            'closing_date': (datetime.now() + timedelta(days=45)).isoformat()
        }
        
        result = self.scorer.score_classified_tender(tender_data, self.mock_classification)
        
        # Should be medium scoring
        self.assertGreaterEqual(result.final_relevance_score, 25)
        self.assertLess(result.final_relevance_score, 70)
        self.assertIn(result.priority_level, ['MEDIUM', 'LOW'])
    
    def test_enhanced_scoring_low_opportunity(self):
        """Test enhanced scoring for low-quality opportunity"""
        tender_data = {
            'notice_identifier': 'test_003',
            'title': 'Office Cleaning Services',
            'description': 'Regular cleaning and maintenance of office buildings',
            'organisation_name': 'Generic Company',
            'value_high': 30000,
            'cpv_codes': '90000000',  # Non-IT CPV
            'suitable_for_sme': 'yes',
            'closing_date': (datetime.now() + timedelta(days=200)).isoformat()
        }
        
        # Mock low classification result
        low_classification = ClassificationResult(
            notice_identifier='test_003',
            keyword_score=0.0,
            context_score=0.0,
            ml_confidence=0.15,
            composite_score=4.5,
            explanation='No digital signals',
            technical_terms=[],
            transformation_signals=[]
        )
        
        result = self.scorer.score_classified_tender(tender_data, low_classification)
        
        # Should be low scoring
        self.assertLess(result.final_relevance_score, 25)
        self.assertEqual(result.priority_level, 'LOW')
    
    def test_priority_level_determination(self):
        """Test priority level determination logic"""
        # High priority case
        high_priority = self.scorer.determine_priority_level(85, 1.0)
        self.assertEqual(high_priority, 'HIGH')
        
        # Medium priority elevated by urgency
        medium_elevated = self.scorer.determine_priority_level(45, 1.4)
        self.assertEqual(medium_elevated, 'HIGH')
        
        # Low priority
        low_priority = self.scorer.determine_priority_level(15, 1.0)
        self.assertEqual(low_priority, 'LOW')
    
    def test_score_breakdown_completeness(self):
        """Test that score breakdown includes all components"""
        tender_data = {
            'notice_identifier': 'test_breakdown',
            'title': 'Test Tender',
            'description': 'API development with cloud infrastructure',
            'organisation_name': 'Test Org',
            'value_high': 200000,
            'cpv_codes': '72000000',
            'closing_date': (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        result = self.scorer.score_classified_tender(tender_data, self.mock_classification)
        
        # Check breakdown completeness
        breakdown = result.score_breakdown
        self.assertIn('base_components', breakdown)
        self.assertIn('multipliers', breakdown)
        self.assertIn('analysis_details', breakdown)
        self.assertIn('scoring_summary', breakdown)
        
        # Check base components
        base_components = breakdown['base_components']
        self.assertIn('keyword_score', base_components)
        self.assertIn('context_score', base_components)
        self.assertIn('ml_confidence', base_components)
        self.assertIn('metadata_score', base_components)
        self.assertIn('business_alignment_score', base_components)
        
        # Check multipliers
        multipliers = breakdown['multipliers']
        self.assertIn('urgency', multipliers)
        self.assertIn('value', multipliers)
        self.assertIn('department', multipliers)
        self.assertIn('competition', multipliers)

class TestIntegrationWithClassifier(unittest.TestCase):
    """Test integration with existing classifier"""
    
    def setUp(self):
        # Create temporary database for testing
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        
        # Initialize classifier with enhanced scoring
        self.classifier = TenderClassifier()
        self.classifier.db_path = Path(self.temp_db.name)
        
        # Create test database
        self.create_test_database()
    
    def tearDown(self):
        Path(self.temp_db.name).unlink(missing_ok=True)
    
    def create_test_database(self):
        """Create test database with sample data"""
        conn = sqlite3.connect(self.temp_db.name)
        conn.execute("""
            CREATE TABLE tenders (
                notice_identifier TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                organisation_name TEXT,
                value_high INTEGER,
                status TEXT,
                suitable_for_sme TEXT,
                cpv_codes TEXT,
                closing_date TEXT
            )
        """)
        
        test_tenders = [
            ('test1', 'Digital Health Platform', 'Modern healthcare system with API integration and cloud infrastructure', 'NHS Digital', 750000, 'open', 'yes', '72000000', (datetime.now() + timedelta(days=21)).isoformat()),
            ('test2', 'Office Supplies Purchase', 'Buying paper, pens and basic office equipment', 'Local Council', 5000, 'open', 'yes', '30000000', (datetime.now() + timedelta(days=30)).isoformat()),
            ('test3', 'Legacy System Modernisation', 'Replacing old mainframe with modern microservices architecture', 'HMRC', 2000000, 'open', 'no', '72000000', (datetime.now() + timedelta(days=45)).isoformat())
        ]
        
        conn.executemany("""
            INSERT INTO tenders 
            (notice_identifier, title, description, organisation_name, value_high, status, suitable_for_sme, cpv_codes, closing_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, test_tenders)
        
        conn.commit()
        conn.close()
    
    def test_enhanced_opportunities_retrieval(self):
        """Test retrieving opportunities with enhanced scoring"""
        if not self.classifier.enable_enhanced_scoring:
            self.skipTest("Enhanced scoring not available")
        
        # Train classifier first
        self.classifier.train_classifier()
        
        # Get enhanced opportunities
        opportunities = self.classifier.get_enhanced_opportunities(min_score=30, limit=5)
        
        self.assertIsInstance(opportunities, list)
        
        if opportunities:
            # Check that results are EnhancedClassificationResult instances
            first_result = opportunities[0]
            self.assertIsInstance(first_result, EnhancedClassificationResult)
            
            # Check enhanced fields are present
            self.assertIsNotNone(first_result.final_relevance_score)
            self.assertIsNotNone(first_result.priority_level)
            self.assertIsNotNone(first_result.recommendation)
            self.assertIsNotNone(first_result.score_breakdown)
            
            # Check scores are properly ordered
            scores = [r.final_relevance_score for r in opportunities]
            self.assertEqual(scores, sorted(scores, reverse=True))
    
    def test_classify_tender_enhanced(self):
        """Test enhanced classification of individual tender"""
        if not self.classifier.enable_enhanced_scoring:
            self.skipTest("Enhanced scoring not available")
        
        # Train classifier first
        self.classifier.train_classifier()
        
        test_tender = {
            'notice_identifier': 'test_individual',
            'title': 'Cloud Migration Project',
            'description': 'Moving legacy systems to modern cloud infrastructure with API integration',
            'organisation_name': 'NHS Digital',
            'value_high': 800000,
            'cpv_codes': '72000000',
            'closing_date': (datetime.now() + timedelta(days=30)).isoformat()
        }
        
        result = self.classifier.classify_tender_enhanced(test_tender)
        
        if isinstance(result, EnhancedClassificationResult):
            # Enhanced result
            self.assertGreater(result.final_relevance_score, 0)
            self.assertIn(result.priority_level, ['HIGH', 'MEDIUM', 'LOW'])
            self.assertIsNotNone(result.recommendation)
        else:
            # Basic result (fallback)
            self.assertIsNotNone(result.composite_score)

def run_comprehensive_tests():
    """Run all test suites for Phase 2 Step 2"""
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestMetadataAnalyzer,
        TestBusinessAlignmentAnalyzer,
        TestMultiplierCalculator,
        TestRelevanceScorer,
        TestIntegrationWithClassifier
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Report summary
    print(f"\n{'='*60}")
    print(f"PHASE 2 STEP 2 TEST SUMMARY")
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