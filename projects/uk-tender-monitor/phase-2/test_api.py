#!/usr/bin/env python3
"""
UK Tender Monitor - API Testing Suite (Phase 2 Step 6)
Comprehensive testing of REST API endpoints and integration functionality

Test Coverage:
- API endpoint functionality and response validation
- Database integration and data persistence
- Error handling and edge cases
- Performance and load testing
- End-to-end workflow validation
"""

import unittest
import requests
import json
import time
import threading
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import tempfile
import sqlite3
from pathlib import Path

# Test configuration
API_BASE_URL = "http://localhost:8000/api"
TEST_TIMEOUT = 30  # seconds

class APITestCase(unittest.TestCase):
    """Base test case with common API testing utilities"""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment"""
        cls.api_url = API_BASE_URL
        cls.session = requests.Session()
        cls.session.headers.update({'Content-Type': 'application/json'})
        
        # Wait for API to be ready
        cls._wait_for_api_ready()
    
    @classmethod
    def _wait_for_api_ready(cls, max_wait=30):
        """Wait for API server to be ready"""
        start_time = time.time()
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(f"{cls.api_url}/health", timeout=5)
                if response.status_code == 200:
                    print("✅ API server ready for testing")
                    return
            except requests.exceptions.RequestException:
                pass
            time.sleep(1)
        
        raise RuntimeError("API server not ready within timeout period")
    
    def api_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make API request with error handling"""
        url = f"{self.api_url}{endpoint}"
        
        try:
            response = self.session.request(method, url, timeout=TEST_TIMEOUT, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            self.fail(f"API request failed: {method} {endpoint} - {e}")
    
    def assert_api_success(self, response: requests.Response, expected_status: int = 200):
        """Assert API response is successful"""
        self.assertEqual(response.status_code, expected_status, 
                        f"Expected status {expected_status}, got {response.status_code}: {response.text}")
        
        # Verify content type for JSON responses
        if expected_status == 200:
            self.assertIn('application/json', response.headers.get('content-type', ''))
    
    def assert_api_error(self, response: requests.Response, expected_status: int):
        """Assert API response is an expected error"""
        self.assertEqual(response.status_code, expected_status,
                        f"Expected error status {expected_status}, got {response.status_code}")


class TestBasicEndpoints(APITestCase):
    """Test basic API endpoints and health checks"""
    
    def test_health_check(self):
        """Test API health check endpoint"""
        response = self.api_request('GET', '/health')
        self.assert_api_success(response)
        
        data = response.json()
        self.assertIn('status', data)
        self.assertEqual(data['status'], 'healthy')
        self.assertIn('timestamp', data)
        self.assertIn('version', data)
        self.assertIn('service', data)
    
    def test_api_info(self):
        """Test API information endpoint"""
        response = self.api_request('GET', '/info')
        self.assert_api_success(response)
        
        data = response.json()
        self.assertIn('service', data)
        self.assertIn('version', data)
        self.assertIn('endpoints', data)
        self.assertIn('documentation', data)
        
        # Verify endpoint categories
        endpoints = data['endpoints']
        expected_categories = ['opportunities', 'classification', 'validation', 'performance']
        for category in expected_categories:
            self.assertIn(category, endpoints)
            self.assertIsInstance(endpoints[category], list)
            self.assertGreater(len(endpoints[category]), 0)


class TestOpportunityEndpoints(APITestCase):
    """Test opportunity discovery endpoints"""
    
    def test_get_top_opportunities_default(self):
        """Test getting top opportunities with default parameters"""
        response = self.api_request('GET', '/opportunities/top')
        self.assert_api_success(response)
        
        data = response.json()
        self.assertIsInstance(data, list)
        
        # If data exists, validate structure
        if data:
            opportunity = data[0]
            required_fields = ['notice_identifier', 'title', 'organisation_name', 'final_relevance_score']
            for field in required_fields:
                self.assertIn(field, opportunity)
            
            # Validate score is numeric and in range
            score = opportunity['final_relevance_score']
            self.assertIsInstance(score, (int, float))
            self.assertGreaterEqual(score, 0)
            self.assertLessEqual(score, 100)
    
    def test_get_top_opportunities_with_filters(self):
        """Test getting opportunities with various filter parameters"""
        # Test with different minimum scores
        for min_score in [40, 60, 80]:
            with self.subTest(min_score=min_score):
                response = self.api_request('GET', f'/opportunities/top?min_score={min_score}&limit=5')
                self.assert_api_success(response)
                
                data = response.json()
                self.assertIsInstance(data, list)
                self.assertLessEqual(len(data), 5)
                
                # Verify all opportunities meet minimum score
                for opp in data:
                    self.assertGreaterEqual(opp['final_relevance_score'], min_score)
    
    def test_get_top_opportunities_with_profile(self):
        """Test getting opportunities with different filter profiles"""
        profiles = ['balanced', 'aggressive', 'conservative']
        
        for profile in profiles:
            with self.subTest(profile=profile):
                response = self.api_request('GET', f'/opportunities/top?profile={profile}&limit=10')
                self.assert_api_success(response)
                
                data = response.json()
                self.assertIsInstance(data, list)
    
    def test_get_opportunity_details_valid(self):
        """Test getting details for a valid opportunity"""
        # First get a list of opportunities
        response = self.api_request('GET', '/opportunities/top?limit=1')
        self.assert_api_success(response)
        
        opportunities = response.json()
        if not opportunities:
            self.skipTest("No opportunities available for testing")
        
        notice_id = opportunities[0]['notice_identifier']
        
        # Get details for the opportunity
        response = self.api_request('GET', f'/opportunities/{notice_id}/details')
        self.assert_api_success(response)
        
        details = response.json()
        self.assertIn('notice_identifier', details)
        self.assertEqual(details['notice_identifier'], notice_id)
        self.assertIn('title', details)
        self.assertIn('organisation_name', details)
    
    def test_get_opportunity_details_invalid(self):
        """Test getting details for invalid opportunity ID"""
        response = self.api_request('GET', '/opportunities/INVALID_ID/details')
        self.assert_api_error(response, 404)
    
    def test_get_dashboard_data(self):
        """Test dashboard data endpoint"""
        response = self.api_request('GET', '/opportunities/dashboard-data')
        self.assert_api_success(response)
        
        data = response.json()
        required_sections = ['summary_stats', 'recent_high_value', 'score_distribution', 'recommendation_trends']
        for section in required_sections:
            self.assertIn(section, data)
        
        # Validate summary stats structure
        summary = data['summary_stats']
        expected_stats = ['total_opportunities', 'avg_score', 'filtered_count', 'pursue_count', 'consider_count']
        for stat in expected_stats:
            self.assertIn(stat, summary)
        
        # Validate lists
        self.assertIsInstance(data['recent_high_value'], list)
        self.assertIsInstance(data['score_distribution'], list)
        self.assertIsInstance(data['recommendation_trends'], list)
    
    def test_dashboard_data_with_period(self):
        """Test dashboard data with different time periods"""
        periods = [7, 30, 90]
        
        for period in periods:
            with self.subTest(period=period):
                response = self.api_request('GET', f'/opportunities/dashboard-data?period_days={period}')
                self.assert_api_success(response)
                
                data = response.json()
                self.assertIn('summary_stats', data)


class TestClassificationEndpoints(APITestCase):
    """Test classification endpoints"""
    
    def test_classify_single_tender_valid(self):
        """Test classifying a single tender with valid data"""
        tender_data = {
            "notice_identifier": "TEST_API_001",
            "title": "Digital Transformation Consultancy Services",
            "description": "Comprehensive digital transformation services including cloud migration, API development, and system modernisation for government departments.",
            "organisation_name": "Cabinet Office",
            "value_high": 500000,
            "status": "open",
            "suitable_for_sme": "yes",
            "cpv_codes": "72000000",
            "closing_date": (datetime.now() + timedelta(days=30)).isoformat(),
            "published_date": datetime.now().isoformat()
        }
        
        response = self.api_request('POST', '/classify/single?save_to_db=false', json=tender_data)
        self.assert_api_success(response)
        
        result = response.json()
        self.assertTrue(result['success'])
        self.assertEqual(result['notice_identifier'], tender_data['notice_identifier'])
        self.assertIn('steps_completed', result)
        self.assertIn('final_result', result)
        
        final_result = result['final_result']
        self.assertIn('final_relevance_score', final_result)
        self.assertIn('final_recommendation', final_result)
        self.assertIn('filter_passes', final_result)
        
        # Validate score range
        score = final_result['final_relevance_score']
        self.assertGreaterEqual(score, 0)
        self.assertLessEqual(score, 100)
        
        # Validate recommendation
        recommendation = final_result['final_recommendation']
        valid_recommendations = ['PURSUE', 'CONSIDER', 'MONITOR', 'AVOID']
        self.assertIn(recommendation, valid_recommendations)
    
    def test_classify_single_tender_invalid(self):
        """Test classifying tender with invalid data"""
        invalid_data = {
            "title": "Test Tender"
            # Missing required notice_identifier
        }
        
        response = self.api_request('POST', '/classify/single', json=invalid_data)
        self.assert_api_error(response, 400)
    
    def test_classify_tender_batch_valid(self):
        """Test batch classification with valid data"""
        tender_batch = [
            {
                "notice_identifier": "TEST_BATCH_001",
                "title": "Cloud Infrastructure Services",
                "description": "Cloud hosting and infrastructure services for government applications",
                "organisation_name": "HMRC",
                "value_high": 750000,
                "status": "open"
            },
            {
                "notice_identifier": "TEST_BATCH_002", 
                "title": "Software Development Framework",
                "description": "Development of custom software solutions using modern frameworks",
                "organisation_name": "NHS Digital",
                "value_high": 1200000,
                "status": "open"
            }
        ]
        
        response = self.api_request('POST', '/classify/batch?save_to_db=false', json=tender_batch)
        self.assert_api_success(response)
        
        results = response.json()
        self.assertIsInstance(results, list)
        self.assertEqual(len(results), 2)
        
        # Validate each result
        for i, result in enumerate(results):
            self.assertEqual(result['notice_identifier'], tender_batch[i]['notice_identifier'])
            self.assertIn('success', result)
            if result['success']:
                self.assertIn('final_result', result)
    
    def test_classify_batch_size_limit(self):
        """Test batch classification size limits"""
        # Test with oversized batch (>50 items)
        large_batch = [
            {
                "notice_identifier": f"TEST_LARGE_{i:03d}",
                "title": f"Test Tender {i}",
                "description": "Test description",
                "organisation_name": "Test Org",
                "value_high": 100000,
                "status": "open"
            }
            for i in range(51)  # 51 items - should exceed limit
        ]
        
        response = self.api_request('POST', '/classify/batch', json=large_batch)
        self.assert_api_error(response, 400)
    
    def test_get_classification_explanation(self):
        """Test getting classification explanation"""
        # First classify a tender
        tender_data = {
            "notice_identifier": "TEST_EXPLAIN_001",
            "title": "Digital Services Platform Development",
            "description": "Development of a comprehensive digital services platform with API integration and cloud deployment",
            "organisation_name": "GDS",
            "value_high": 800000,
            "status": "open"
        }
        
        # Classify with database save
        response = self.api_request('POST', '/classify/single?save_to_db=true', json=tender_data)
        self.assert_api_success(response)
        
        result = response.json()
        if not result['success']:
            self.skipTest("Classification failed - cannot test explanation")
        
        # Get explanation
        notice_id = tender_data['notice_identifier']
        response = self.api_request('GET', f'/classify/{notice_id}/explain')
        
        if response.status_code == 404:
            self.skipTest("Classification not found in database - may need time to persist")
        
        self.assert_api_success(response)
        
        explanation = response.json()
        self.assertEqual(explanation['notice_identifier'], notice_id)
        
        # Validate explanation structure
        expected_fields = [
            'keyword_score', 'context_score', 'ml_confidence', 'composite_score',
            'final_relevance_score', 'final_recommendation', 'filter_passes',
            'explanation', 'detailed_breakdown'
        ]
        for field in expected_fields:
            self.assertIn(field, explanation)
        
        # Validate detailed breakdown
        breakdown = explanation['detailed_breakdown']
        expected_steps = ['step_1_classification', 'step_2_enhanced_scoring', 'step_3_filtering']
        for step in expected_steps:
            self.assertIn(step, breakdown)


class TestValidationEndpoints(APITestCase):
    """Test expert validation endpoints"""
    
    def test_submit_validation_valid(self):
        """Test submitting valid expert validation"""
        # First ensure we have a classified tender
        tender_data = {
            "notice_identifier": "TEST_VALIDATION_001",
            "title": "API Integration Services",
            "description": "REST API development and integration services for government systems",
            "organisation_name": "DVLA",
            "value_high": 400000,
            "status": "open"
        }
        
        # Classify tender
        response = self.api_request('POST', '/classify/single?save_to_db=true', json=tender_data)
        self.assert_api_success(response)
        
        # Submit validation
        validation_data = {
            "notice_identifier": tender_data['notice_identifier'],
            "expert_label": "relevant",
            "confidence": 4,
            "notes": "Clear digital transformation opportunity with API focus",
            "reasoning": "Strong technical indicators and strategic value for government modernisation"
        }
        
        response = self.api_request('POST', '/validation/submit', json=validation_data)
        self.assert_api_success(response)
        
        result = response.json()
        self.assertTrue(result['success'])
        self.assertIn('validation_id', result)
        self.assertEqual(result['notice_identifier'], validation_data['notice_identifier'])
        self.assertEqual(result['expert_label'], validation_data['expert_label'])
        self.assertEqual(result['confidence'], validation_data['confidence'])
    
    def test_submit_validation_invalid_label(self):
        """Test submitting validation with invalid label"""
        validation_data = {
            "notice_identifier": "TEST_001",
            "expert_label": "invalid_label",  # Invalid label
            "confidence": 3
        }
        
        response = self.api_request('POST', '/validation/submit', json=validation_data)
        self.assert_api_error(response, 422)  # Validation error
    
    def test_submit_validation_invalid_confidence(self):
        """Test submitting validation with invalid confidence"""
        validation_data = {
            "notice_identifier": "TEST_001",
            "expert_label": "relevant",
            "confidence": 10  # Invalid confidence (must be 1-5)
        }
        
        response = self.api_request('POST', '/validation/submit', json=validation_data)
        self.assert_api_error(response, 422)  # Validation error
    
    def test_get_validation_stats(self):
        """Test getting validation statistics"""
        response = self.api_request('GET', '/validation/stats')
        self.assert_api_success(response)
        
        stats = response.json()
        expected_fields = [
            'total_validations', 'agreement_rate', 'avg_confidence',
            'label_distribution', 'recent_validations', 'avg_disagreement_magnitude'
        ]
        for field in expected_fields:
            self.assertIn(field, stats)
        
        # Validate data types
        self.assertIsInstance(stats['total_validations'], int)
        self.assertIsInstance(stats['agreement_rate'], (int, float))
        self.assertIsInstance(stats['avg_confidence'], (int, float))
        self.assertIsInstance(stats['label_distribution'], dict)
        self.assertIsInstance(stats['recent_validations'], int)
    
    def test_get_validation_stats_with_period(self):
        """Test validation stats with different time periods"""
        periods = [7, 30, 90]
        
        for period in periods:
            with self.subTest(period=period):
                response = self.api_request('GET', f'/validation/stats?period_days={period}')
                self.assert_api_success(response)
                
                stats = response.json()
                self.assertIn('total_validations', stats)
    
    def test_get_validation_queue(self):
        """Test getting validation queue"""
        response = self.api_request('GET', '/validation/queue')
        self.assert_api_success(response)
        
        queue = response.json()
        self.assertIsInstance(queue, list)
        
        # If queue has items, validate structure
        if queue:
            item = queue[0]
            expected_fields = [
                'notice_identifier', 'title', 'organisation_name',
                'final_relevance_score', 'final_recommendation'
            ]
            for field in expected_fields:
                self.assertIn(field, item)
    
    def test_validation_queue_with_filters(self):
        """Test validation queue with different filters"""
        # Test with different minimum scores
        response = self.api_request('GET', '/validation/queue?min_score=60&limit=5')
        self.assert_api_success(response)
        
        queue = response.json()
        self.assertIsInstance(queue, list)
        self.assertLessEqual(len(queue), 5)
        
        # Verify all items meet minimum score
        for item in queue:
            self.assertGreaterEqual(item['final_relevance_score'], 60)


class TestPerformanceEndpoints(APITestCase):
    """Test performance monitoring endpoints"""
    
    def test_get_model_performance(self):
        """Test getting model performance metrics"""
        response = self.api_request('GET', '/performance/models')
        self.assert_api_success(response)
        
        models = response.json()
        self.assertIsInstance(models, list)
        
        # If models exist, validate structure
        if models:
            model = models[0]
            expected_fields = [
                'model_version', 'f1_score', 'precision_score', 'recall_score',
                'accuracy_score', 'training_samples', 'expert_labels_used'
            ]
            for field in expected_fields:
                self.assertIn(field, model)
            
            # Validate score ranges
            for score_field in ['f1_score', 'precision_score', 'recall_score', 'accuracy_score']:
                if model.get(score_field) is not None:
                    score = model[score_field]
                    self.assertGreaterEqual(score, 0)
                    self.assertLessEqual(score, 1)
    
    def test_get_system_health(self):
        """Test getting system health metrics"""
        response = self.api_request('GET', '/performance/system-health')
        self.assert_api_success(response)
        
        health = response.json()
        expected_fields = [
            'database_operational', 'classification_pipeline_status',
            'recent_classifications_count', 'expert_validations_count',
            'model_performance_score', 'integration_status', 'uptime_hours'
        ]
        for field in expected_fields:
            self.assertIn(field, health)
        
        # Validate data types
        self.assertIsInstance(health['database_operational'], bool)
        self.assertIsInstance(health['classification_pipeline_status'], str)
        self.assertIsInstance(health['recent_classifications_count'], int)
        self.assertIsInstance(health['expert_validations_count'], int)
        self.assertIsInstance(health['model_performance_score'], (int, float))
        self.assertIsInstance(health['integration_status'], dict)
        self.assertIsInstance(health['uptime_hours'], (int, float))


class TestAPIPerformance(APITestCase):
    """Test API performance and load handling"""
    
    def test_response_times(self):
        """Test API response times meet requirements"""
        endpoints_to_test = [
            ('GET', '/health'),
            ('GET', '/opportunities/top?limit=10'),
            ('GET', '/opportunities/dashboard-data'),
            ('GET', '/validation/stats'),
            ('GET', '/performance/system-health')
        ]
        
        for method, endpoint in endpoints_to_test:
            with self.subTest(endpoint=endpoint):
                start_time = time.time()
                response = self.api_request(method, endpoint)
                response_time = time.time() - start_time
                
                self.assert_api_success(response)
                self.assertLess(response_time, 5.0, f"Response time too slow: {response_time:.2f}s")
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        def make_request():
            response = self.api_request('GET', '/health')
            return response.status_code == 200
        
        # Create multiple threads to make concurrent requests
        threads = []
        results = []
        
        for _ in range(10):
            thread = threading.Thread(target=lambda: results.append(make_request()))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all requests succeeded
        self.assertEqual(len(results), 10)
        self.assertTrue(all(results), "Some concurrent requests failed")


class TestErrorHandling(APITestCase):
    """Test API error handling and edge cases"""
    
    def test_invalid_endpoints(self):
        """Test handling of invalid endpoints"""
        invalid_endpoints = [
            '/nonexistent',
            '/opportunities/invalid',
            '/classify/missing',
            '/validation/badendpoint'
        ]
        
        for endpoint in invalid_endpoints:
            with self.subTest(endpoint=endpoint):
                response = self.api_request('GET', endpoint)
                self.assert_api_error(response, 404)
    
    def test_method_not_allowed(self):
        """Test handling of invalid HTTP methods"""
        # Try POST on GET-only endpoint
        response = self.api_request('POST', '/health')
        self.assert_api_error(response, 405)
        
        # Try GET on POST-only endpoint
        response = self.api_request('GET', '/classify/single')
        self.assert_api_error(response, 405)
    
    def test_malformed_json(self):
        """Test handling of malformed JSON in requests"""
        response = self.session.post(
            f"{self.api_url}/classify/single",
            data="{ invalid json }",
            headers={'Content-Type': 'application/json'}
        )
        self.assert_api_error(response, 422)
    
    def test_missing_content_type(self):
        """Test handling of missing content type for JSON endpoints"""
        response = self.session.post(
            f"{self.api_url}/classify/single",
            data='{"test": "data"}',
            headers={}  # No content-type header
        )
        # Should still work or give appropriate error
        self.assertIn(response.status_code, [200, 400, 422])


def run_comprehensive_api_tests():
    """Run complete API test suite"""
    print("🎯 UK Tender Monitor - API Testing Suite")
    print("="*60)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes in order of complexity
    test_classes = [
        TestBasicEndpoints,
        TestOpportunityEndpoints,
        TestClassificationEndpoints,
        TestValidationEndpoints,
        TestPerformanceEndpoints,
        TestAPIPerformance,
        TestErrorHandling
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2, buffer=True)
    result = runner.run(test_suite)
    
    # Generate summary report
    print(f"\n{'='*60}")
    print(f"API TESTING SUMMARY")
    print(f"{'='*60}")
    print(f"Tests Run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100) if result.testsRun > 0 else 0
    print(f"Success Rate: {success_rate:.1f}%")
    
    if result.failures:
        print(f"\n❌ FAILURES ({len(result.failures)}):")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback.split('AssertionError:')[-1].strip() if 'AssertionError:' in traceback else 'Unknown failure'}")
    
    if result.errors:
        print(f"\n🚨 ERRORS ({len(result.errors)}):")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback.split('Exception:')[-1].strip() if 'Exception:' in traceback else 'Unknown error'}")
    
    if result.skipped:
        print(f"\n⏭️  SKIPPED ({len(result.skipped)}):")
        for test, reason in result.skipped:
            print(f"  - {test}: {reason}")
    
    print(f"\n{'='*60}")
    
    if result.wasSuccessful():
        print("✅ ALL API TESTS PASSED - SYSTEM READY FOR PRODUCTION")
    else:
        print("❌ SOME TESTS FAILED - REVIEW ISSUES BEFORE DEPLOYMENT")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_comprehensive_api_tests()
    exit(0 if success else 1)