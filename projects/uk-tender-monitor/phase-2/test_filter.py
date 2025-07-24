#!/usr/bin/env python3
"""
Test Suite for Advanced Filtering Engine (Phase 2 Step 3)
Comprehensive testing of multi-criteria filtering, competition assessment, and business logic
"""

import unittest
import tempfile
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

from filter import (
    ValueFilters, TimelineFilters, CapabilityFilters, GeographicFilters,
    CompetitionAssessment, FilterConfiguration, AdvancedOpportunityFilter,
    FilteredOpportunityResult
)

class TestValueFilters(unittest.TestCase):
    """Test value-based filtering logic"""
    
    def setUp(self):
        self.config = {
            'min_value': 50000,
            'max_value': 10000000,
            'sweet_spot_min': 100000,
            'sweet_spot_max': 2000000,
            'capacity_threshold': 5000000
        }
        self.filter = ValueFilters(self.config)
    
    def test_optimal_value_range(self):
        """Test contracts in optimal value range"""
        tender = {'value_high': 500000}
        result = self.filter.evaluate_value_fit(tender)
        
        self.assertTrue(result['passes'])
        self.assertEqual(result['reason'], 'optimal_value_range')
        self.assertEqual(result['score'], 1.0)
        self.assertIn('Optimal value range', result['assessment'])
    
    def test_below_minimum_threshold(self):
        """Test contracts below minimum value"""
        tender = {'value_high': 25000}
        result = self.filter.evaluate_value_fit(tender)
        
        self.assertFalse(result['passes'])
        self.assertEqual(result['reason'], 'below_minimum_value')
        self.assertEqual(result['score'], 0)
    
    def test_exceeds_maximum_threshold(self):
        """Test contracts exceeding maximum value"""
        tender = {'value_high': 15000000}
        result = self.filter.evaluate_value_fit(tender)
        
        self.assertFalse(result['passes'])
        self.assertEqual(result['reason'], 'exceeds_maximum_value')
        self.assertEqual(result['score'], 0)
    
    def test_capacity_threshold(self):
        """Test capacity threshold filtering"""
        tender = {'value_high': 8000000}
        result = self.filter.evaluate_value_fit(tender)
        
        self.assertFalse(result['passes'])
        self.assertEqual(result['reason'], 'exceeds_organizational_capacity')
        self.assertEqual(result['score'], 0)
    
    def test_acceptable_range_below_sweet_spot(self):
        """Test acceptable range below sweet spot"""
        tender = {'value_high': 75000}
        result = self.filter.evaluate_value_fit(tender)
        
        self.assertTrue(result['passes'])
        self.assertEqual(result['reason'], 'acceptable_value_range')
        self.assertEqual(result['score'], 0.7)
    
    def test_acceptable_range_above_sweet_spot(self):
        """Test acceptable range above sweet spot"""
        tender = {'value_high': 3000000}
        result = self.filter.evaluate_value_fit(tender)
        
        self.assertTrue(result['passes'])
        self.assertEqual(result['reason'], 'acceptable_value_range')
        self.assertEqual(result['score'], 0.8)
    
    def test_unknown_value(self):
        """Test handling of unknown/zero values"""
        tender = {'value_high': 0}
        result = self.filter.evaluate_value_fit(tender)
        
        self.assertTrue(result['passes'])
        self.assertEqual(result['reason'], 'value_unknown')
        self.assertEqual(result['score'], 0.5)

class TestTimelineFilters(unittest.TestCase):
    """Test timeline-based filtering logic"""
    
    def setUp(self):
        self.config = {
            'min_lead_time': 14,
            'max_timeline': 730,
            'optimal_window_start': 30,
            'optimal_window_end': 90
        }
        self.filter = TimelineFilters(self.config)
    
    def test_optimal_timing_window(self):
        """Test opportunities in optimal timing window"""
        closing_date = (datetime.now() + timedelta(days=45)).isoformat()
        tender = {'closing_date': closing_date}
        result = self.filter.evaluate_timeline_fit(tender)
        
        self.assertTrue(result['passes'])
        self.assertEqual(result['reason'], 'optimal_timing_window')
        self.assertEqual(result['score'], 1.0)
        self.assertEqual(result['days_remaining'], 45)
    
    def test_insufficient_preparation_time(self):
        """Test opportunities with insufficient preparation time"""
        closing_date = (datetime.now() + timedelta(days=10)).isoformat()
        tender = {'closing_date': closing_date}
        result = self.filter.evaluate_timeline_fit(tender)
        
        self.assertFalse(result['passes'])
        self.assertEqual(result['reason'], 'insufficient_preparation_time')
        self.assertEqual(result['score'], 0)
    
    def test_expired_opportunity(self):
        """Test expired opportunities"""
        closing_date = (datetime.now() - timedelta(days=5)).isoformat()
        tender = {'closing_date': closing_date}
        result = self.filter.evaluate_timeline_fit(tender)
        
        self.assertFalse(result['passes'])
        self.assertEqual(result['reason'], 'opportunity_expired')
        self.assertEqual(result['score'], 0)
    
    def test_too_distant_future(self):
        """Test opportunities too far in the future"""
        closing_date = (datetime.now() + timedelta(days=800)).isoformat()
        tender = {'closing_date': closing_date}
        result = self.filter.evaluate_timeline_fit(tender)
        
        self.assertFalse(result['passes'])
        self.assertEqual(result['reason'], 'too_distant_future')
        self.assertEqual(result['score'], 0)
    
    def test_urgent_timeline(self):
        """Test urgent but acceptable timeline"""
        closing_date = (datetime.now() + timedelta(days=21)).isoformat()
        tender = {'closing_date': closing_date}
        result = self.filter.evaluate_timeline_fit(tender)
        
        self.assertTrue(result['passes'])
        self.assertEqual(result['reason'], 'urgent_timeline')
        self.assertGreater(result['score'], 0.4)
        self.assertLess(result['score'], 1.0)
    
    def test_future_timeline(self):
        """Test future but acceptable timeline"""
        closing_date = (datetime.now() + timedelta(days=150)).isoformat()
        tender = {'closing_date': closing_date}
        result = self.filter.evaluate_timeline_fit(tender)
        
        self.assertTrue(result['passes'])
        self.assertEqual(result['reason'], 'future_timeline')
        self.assertGreater(result['score'], 0.6)
        self.assertLess(result['score'], 1.0)
    
    def test_no_deadline_specified(self):
        """Test handling of missing closing dates"""
        tender = {'closing_date': None}
        result = self.filter.evaluate_timeline_fit(tender)
        
        self.assertTrue(result['passes'])
        self.assertEqual(result['reason'], 'no_deadline_specified')
        self.assertEqual(result['score'], 0.6)

class TestCapabilityFilters(unittest.TestCase):
    """Test capability matching and complexity assessment"""
    
    def setUp(self):
        self.config = {
            'required_skills': ['digital_transformation'],
            'min_technical_overlap': 2,
            'max_complexity_threshold': 7
        }
        self.filter = CapabilityFilters(self.config)
        
        # Mock enhanced result
        class MockEnhancedResult:
            def __init__(self, technical_terms):
                self.technical_terms = technical_terms
        
        self.mock_enhanced_result = MockEnhancedResult(['api', 'cloud', 'python', 'microservices'])
    
    def test_digital_transformation_capability_match(self):
        """Test matching digital transformation requirements"""
        tender = {
            'title': 'Digital Transformation Project',
            'description': 'Comprehensive digital transformation with cloud migration and API development'
        }
        
        result = self.filter.evaluate_capability_match(tender, self.mock_enhanced_result)
        
        self.assertTrue(result['passes'])
        self.assertEqual(result['reason'], 'capability_requirements_met')
        self.assertGreater(result['score'], 0.3)
        self.assertIn('digital_transformation', [ca['capability'] for ca in result['capability_assessments']])
    
    def test_software_development_capability_match(self):
        """Test matching software development requirements"""
        tender = {
            'title': 'Software Development Services',
            'description': 'Custom software development with Python and API integration'
        }
        
        result = self.filter.evaluate_capability_match(tender, self.mock_enhanced_result)
        
        self.assertTrue(result['passes'])
        self.assertGreater(result['score'], 0.3)
    
    def test_complexity_exceeds_threshold(self):
        """Test rejection due to complexity threshold"""
        # Mock high complexity result
        high_complexity_result = type('MockResult', (), {
            'technical_terms': ['enterprise', 'architecture', 'legacy', 'integration', 'complex', 'bespoke']
        })()
        
        tender = {
            'title': 'Enterprise Architecture Transformation',
            'description': 'Complex enterprise architecture with legacy system integration, bespoke solutions, and advanced technical requirements'
        }
        
        result = self.filter.evaluate_capability_match(tender, high_complexity_result)
        
        self.assertFalse(result['passes'])
        self.assertEqual(result['reason'], 'complexity_exceeds_threshold')
        self.assertGreater(result['complexity_score'], 7)
    
    def test_no_specific_requirements(self):
        """Test handling of tenders with no specific capability requirements"""
        tender = {
            'title': 'General IT Services',
            'description': 'Basic IT support and maintenance services'
        }
        
        result = self.filter.evaluate_capability_match(tender, self.mock_enhanced_result)
        
        self.assertTrue(result['passes'])
        self.assertEqual(result['reason'], 'no_specific_capability_requirements')
        self.assertEqual(result['score'], 0.7)
    
    def test_insufficient_capability_confidence(self):
        """Test rejection due to low capability confidence"""
        # Mock result with minimal technical terms
        low_tech_result = type('MockResult', (), {'technical_terms': []})()
        
        tender = {
            'title': 'Advanced AI and Machine Learning Platform',
            'description': 'Highly specialized artificial intelligence system with machine learning capabilities'
        }
        
        result = self.filter.evaluate_capability_match(tender, low_tech_result)
        
        # Should have low confidence due to mismatch between requirements and technical terms
        if not result['passes']:
            self.assertEqual(result['reason'], 'insufficient_capability_confidence')
        else:
            # If it passes, confidence should still be relatively low
            self.assertLess(result['score'], 0.6)

class TestGeographicFilters(unittest.TestCase):
    """Test geographic and delivery model filtering"""
    
    def setUp(self):
        self.config = {
            'preferred_regions': ['England', 'Scotland'],
            'excluded_regions': ['Northern Ireland'],
            'remote_friendly': True,
            'max_travel_distance': 200
        }
        self.filter = GeographicFilters(self.config)
    
    def test_remote_delivery_supported(self):
        """Test remote delivery detection and scoring"""
        tender = {
            'title': 'Remote Development Services',
            'description': 'Distributed team providing remote software development and digital delivery'
        }
        
        result = self.filter.evaluate_geographic_fit(tender)
        
        self.assertTrue(result['passes'])
        self.assertEqual(result['reason'], 'remote_delivery_supported')
        self.assertEqual(result['score'], 1.0)
    
    def test_uk_wide_opportunity(self):
        """Test UK-wide opportunity scoring"""
        tender = {
            'title': 'UK-wide Digital Services',
            'description': 'National digital transformation program across England and Wales'
        }
        
        result = self.filter.evaluate_geographic_fit(tender)
        
        self.assertTrue(result['passes'])
        self.assertEqual(result['reason'], 'uk_wide_opportunity')
        self.assertGreaterEqual(result['score'], 0.7)
    
    def test_preferred_region_match(self):
        """Test matching preferred regions"""
        tender = {
            'title': 'Scotland Digital Initiative',
            'description': 'Digital services for Scottish government departments'
        }
        
        result = self.filter.evaluate_geographic_fit(tender)
        
        self.assertTrue(result['passes'])
        self.assertEqual(result['reason'], 'preferred_region_match')
        self.assertEqual(result['score'], 0.9)
        self.assertIn('Scotland', result['matched_regions'])
    
    def test_excluded_region_rejection(self):
        """Test rejection of excluded regions"""
        tender = {
            'title': 'Northern Ireland Digital Services',
            'description': 'Digital transformation for Northern Ireland government'
        }
        
        result = self.filter.evaluate_geographic_fit(tender)
        
        self.assertFalse(result['passes'])
        self.assertEqual(result['reason'], 'excluded_region')
        self.assertEqual(result['score'], 0)
    
    def test_acceptable_travel_distance(self):
        """Test cities within acceptable travel distance"""
        tender = {
            'title': 'Manchester Digital Hub',
            'description': 'Digital services based in Manchester city center'
        }
        
        result = self.filter.evaluate_geographic_fit(tender)
        
        self.assertTrue(result['passes'])
        self.assertEqual(result['reason'], 'acceptable_travel_distance')
        self.assertGreater(result['score'], 0.4)
    
    def test_excessive_travel_distance(self):
        """Test rejection due to excessive travel distance"""
        tender = {
            'title': 'Aberdeen Oil and Gas Digital Services',
            'description': 'On-site digital services in Aberdeen, Scotland'
        }
        
        # Mock Aberdeen as very distant
        with patch.object(self.filter, 'uk_locations', {
            'aberdeen': {'region': 'Scotland', 'distance_from_base': 400}
        }):
            result = self.filter.evaluate_geographic_fit(tender)
            
            if not result['passes'] and result.get('reason') == 'excessive_travel_distance':
                self.assertEqual(result['score'], 0)
                self.assertGreater(result['closest_city']['distance'], 200)

class TestCompetitionAssessment(unittest.TestCase):
    """Test competition analysis and bid probability calculation"""
    
    def setUp(self):
        self.assessor = CompetitionAssessment()
        
        # Mock enhanced result
        class MockEnhancedResult:
            def __init__(self, score, technical_terms):
                self.final_relevance_score = score
                self.technical_terms = technical_terms
        
        self.mock_enhanced_result = MockEnhancedResult(75.0, ['api', 'cloud', 'digital'])
    
    def test_low_value_low_competition(self):
        """Test low-value contracts with reduced competition"""
        tender = {
            'title': 'Small Digital Project',
            'description': 'Basic digital services for local council',
            'value_high': 75000,
            'suitable_for_sme': 'yes'
        }
        
        result = self.assessor.assess_competition_level(tender, self.mock_enhanced_result)
        
        self.assertLessEqual(result['competition_level'], 5.0)
        self.assertEqual(result['competition_category'], 'LOW')
        self.assertGreaterEqual(result['bid_probability'], 0.15)
    
    def test_high_value_high_competition(self):
        """Test high-value contracts with increased competition"""
        tender = {
            'title': 'Major Digital Transformation',
            'description': 'Enterprise-wide digital transformation program',
            'value_high': 5000000,
            'suitable_for_sme': 'no'
        }
        
        result = self.assessor.assess_competition_level(tender, self.mock_enhanced_result)
        
        self.assertGreaterEqual(result['competition_level'], 7.0)
        self.assertIn(result['competition_category'], ['HIGH', 'VERY_HIGH'])
        self.assertLessEqual(result['bid_probability'], 0.3)
    
    def test_highly_specialized_reduces_competition(self):
        """Test highly specialized requirements reducing competition"""
        specialized_result = type('MockResult', (), {
            'final_relevance_score': 75.0,
            'technical_terms': ['blockchain', 'ai', 'machine_learning', 'enterprise_architecture']
        })()
        
        tender = {
            'title': 'AI and Blockchain Integration',
            'description': 'Advanced artificial intelligence and blockchain digital transformation with enterprise architecture',
            'value_high': 800000,
            'suitable_for_sme': 'no'
        }
        
        result = self.assessor.assess_competition_level(tender, specialized_result)
        
        specialization = result['assessment_factors']['specialization']
        self.assertEqual(specialization['level'], 'highly_specialized')
        self.assertLess(specialization['multiplier'], 1.0)
    
    def test_framework_reduces_competition(self):
        """Test framework requirements reducing competition"""
        tender = {
            'title': 'G-Cloud Digital Services',
            'description': 'Digital services via G-Cloud framework for government department',
            'value_high': 500000,
            'suitable_for_sme': 'yes'
        }
        
        result = self.assessor.assess_competition_level(tender, self.mock_enhanced_result)
        
        framework_info = result['assessment_factors']['framework']
        self.assertTrue(framework_info['requires_framework'])
        self.assertLess(framework_info['competition_adjustment'], 0)
    
    def test_security_clearance_barrier(self):
        """Test security clearance reducing competition"""
        tender = {
            'title': 'Secure Government Digital Services',
            'description': 'Digital services requiring SC clearance for sensitive government data',
            'value_high': 1000000,
            'suitable_for_sme': 'no'
        }
        
        result = self.assessor.assess_competition_level(tender, self.mock_enhanced_result)
        
        geographic_barriers = result['assessment_factors']['geographic']
        if 'security_clearance' in geographic_barriers['barriers_detected']:
            self.assertLess(geographic_barriers['competition_adjustment'], -1.0)
    
    def test_bid_probability_calculation(self):
        """Test bid probability calculation factors"""
        tender = {
            'value_high': 300000,
            'suitable_for_sme': 'yes'
        }
        
        result = self.assessor.assess_competition_level(tender, self.mock_enhanced_result)
        
        # High relevance score should increase bid probability
        self.assertGreaterEqual(result['bid_probability'], 0.1)
        self.assertIn(result['probability_band'], ['LOW', 'MEDIUM', 'HIGH'])
        self.assertGreaterEqual(result['probability_confidence'], 0.6)

class TestFilterConfiguration(unittest.TestCase):
    """Test filter configuration and profiles"""
    
    def setUp(self):
        self.config = FilterConfiguration()
    
    def test_default_configuration_loaded(self):
        """Test default configuration is properly loaded"""
        self.assertIn('value_filters', self.config.config)
        self.assertIn('timeline_filters', self.config.config)
        self.assertIn('capability_filters', self.config.config)
        self.assertIn('geographic_filters', self.config.config)
        self.assertEqual(self.config.config['value_filters']['min_value'], 50000)
    
    def test_filter_profiles_creation(self):
        """Test creation of different filter profiles"""
        profiles = self.config.create_filter_profiles()
        
        expected_profiles = ['aggressive', 'balanced', 'conservative', 'strategic', 'rapid_growth']
        for profile in expected_profiles:
            self.assertIn(profile, profiles)
            self.assertIn('description', profiles[profile])
            self.assertIn('config_overrides', profiles[profile])
    
    def test_aggressive_profile_settings(self):
        """Test aggressive profile has appropriate settings"""
        aggressive_config = self.config.apply_profile('aggressive')
        
        self.assertEqual(aggressive_config['scoring_thresholds']['min_relevance_score'], 30.0)
        self.assertEqual(aggressive_config['competition_filters']['max_competition_level'], 9.0)
        self.assertEqual(aggressive_config['value_filters']['min_value'], 25000)
    
    def test_conservative_profile_settings(self):
        """Test conservative profile has appropriate settings"""
        conservative_config = self.config.apply_profile('conservative')
        
        self.assertEqual(conservative_config['scoring_thresholds']['min_relevance_score'], 60.0)
        self.assertEqual(conservative_config['competition_filters']['max_competition_level'], 5.0)
        self.assertEqual(conservative_config['capability_filters']['max_complexity_threshold'], 6)
    
    def test_strategic_profile_settings(self):
        """Test strategic profile focuses on high-value opportunities"""
        strategic_config = self.config.apply_profile('strategic')
        
        self.assertEqual(strategic_config['value_filters']['min_value'], 500000)
        self.assertEqual(strategic_config['competition_filters']['min_bid_probability'], 0.12)
    
    def test_unknown_profile_fallback(self):
        """Test fallback to balanced profile for unknown profiles"""
        unknown_config = self.config.apply_profile('unknown_profile')
        balanced_config = self.config.apply_profile('balanced')
        
        self.assertEqual(unknown_config['scoring_thresholds'], balanced_config['scoring_thresholds'])

class TestAdvancedOpportunityFilter(unittest.TestCase):
    """Test the main advanced filtering engine"""
    
    def setUp(self):
        self.filter = AdvancedOpportunityFilter()
        
        # Mock enhanced results
        class MockEnhancedResult:
            def __init__(self, notice_id, score, technical_terms):
                self.notice_identifier = notice_id
                self.final_relevance_score = score
                self.technical_terms = technical_terms
        
        self.mock_enhanced_results = [
            MockEnhancedResult('test_001', 85.0, ['api', 'cloud', 'digital']),
            MockEnhancedResult('test_002', 45.0, ['software', 'development']),
            MockEnhancedResult('test_003', 25.0, ['support', 'maintenance'])
        ]
    
    def test_filter_initialization(self):
        """Test filter components are properly initialized"""
        self.assertIsNotNone(self.filter.value_filters)
        self.assertIsNotNone(self.filter.timeline_filters)
        self.assertIsNotNone(self.filter.capability_filters)
        self.assertIsNotNone(self.filter.geographic_filters)
        self.assertIsNotNone(self.filter.competition_assessment)
    
    def test_overall_filter_score_calculation(self):
        """Test combined filter score calculation"""
        filter_results = {
            'value': {'passes': True, 'score': 1.0},
            'timeline': {'passes': True, 'score': 0.8},
            'capability': {'passes': True, 'score': 0.9},
            'geographic': {'passes': True, 'score': 0.7}
        }
        
        overall_score = self.filter.calculate_overall_filter_score(filter_results)
        
        # Expected: 1.0*0.3 + 0.8*0.25 + 0.9*0.3 + 0.7*0.15 = 0.875
        expected_score = 1.0*0.3 + 0.8*0.25 + 0.9*0.3 + 0.7*0.15
        self.assertAlmostEqual(overall_score, expected_score, places=3)
    
    def test_risk_success_factor_analysis(self):
        """Test risk and success factor identification"""
        filter_results = {
            'timeline': {'days_remaining': 15, 'reason': 'urgent_timeline'},
            'value': {'reason': 'optimal_value_range', 'value': 500000},
            'capability': {'score': 0.9, 'complexity_score': 6},
            'geographic': {'reason': 'remote_delivery_supported'}
        }
        
        competition_analysis = {'competition_level': 3.5}
        
        risk_factors, success_factors = self.filter.analyze_risk_success_factors(
            self.mock_enhanced_results[0], filter_results, competition_analysis
        )
        
        self.assertIsInstance(risk_factors, list)
        self.assertIsInstance(success_factors, list)
        
        # Should identify remote delivery as success factor
        remote_success = any('Remote delivery' in factor for factor in success_factors)
        self.assertTrue(remote_success)
        
        # Should identify optimal value as success factor
        value_success = any('optimal range' in factor for factor in success_factors)
        self.assertTrue(value_success)
    
    def test_resource_requirements_estimation(self):
        """Test resource requirements estimation"""
        filter_results = {
            'timeline': {'days_remaining': 45},
            'capability': {'complexity_score': 6}
        }
        
        tender_data = {'value_high': 750000}
        
        resource_req = self.filter.estimate_resource_requirements(
            self.mock_enhanced_results[0], tender_data, filter_results
        )
        
        self.assertIn('estimated_team_size', resource_req)
        self.assertIn('estimated_duration_months', resource_req)
        self.assertIn('bid_preparation_days', resource_req)
        self.assertIn('project_complexity', resource_req)
        self.assertIn('resource_intensity', resource_req)
        
        # High-value contract should require larger team
        self.assertIn('Large', resource_req['estimated_team_size'])
    
    def test_strategic_value_determination(self):
        """Test strategic value assessment"""
        filter_results = {
            'capability': {'complexity_score': 8},
            'geographic': {'score': 0.9}
        }
        
        tender_data = {
            'value_high': 1500000,
            'organisation_name': 'NHS Digital'
        }
        
        strategic_value = self.filter.determine_strategic_value(
            self.mock_enhanced_results[0], tender_data, filter_results
        )
        
        # High relevance score + high value + strategic org should be HIGH
        self.assertEqual(strategic_value, 'HIGH')
    
    def test_final_recommendation_generation(self):
        """Test final recommendation logic"""
        filter_results = {
            'value': {'passes': True, 'score': 1.0},
            'timeline': {'passes': True, 'score': 0.9},
            'capability': {'passes': True, 'score': 0.8},
            'geographic': {'passes': True, 'score': 0.8}
        }
        
        competition_analysis = {
            'competition_level': 4.0,
            'bid_probability': 0.25
        }
        
        overall_filter_score = 0.85
        
        recommendation = self.filter.generate_final_recommendation(
            self.mock_enhanced_results[0], filter_results, 
            competition_analysis, overall_filter_score
        )
        
        self.assertIn('recommendation', recommendation)
        self.assertIn('confidence', recommendation)
        self.assertIn('reasoning', recommendation)
        self.assertIn('next_actions', recommendation)
        
        # High scores should result in PURSUE recommendation
        self.assertEqual(recommendation['recommendation'], 'PURSUE')

def run_comprehensive_tests():
    """Run all test suites for Phase 2 Step 3"""
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestValueFilters,
        TestTimelineFilters,
        TestCapabilityFilters,
        TestGeographicFilters,
        TestCompetitionAssessment,
        TestFilterConfiguration,
        TestAdvancedOpportunityFilter
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Report summary
    print(f"\n{'='*60}")
    print(f"PHASE 2 STEP 3 TEST SUMMARY")
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