#!/usr/bin/env python3
"""
UK Tender Monitor - Advanced Filtering Engine (Phase 2 Step 3)
Sophisticated business logic filtering with competition analysis and decision support

Core Features:
- Multi-criteria filtering (value, timeline, capability, geographic)
- Competition assessment with bid probability calculation
- Configurable filter profiles for different strategies
- Business intelligence enhancement with risk/success factors
- Final recommendation generation (PURSUE/CONSIDER/AVOID)
"""

import json
import sqlite3
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, NamedTuple
import logging
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FilteredOpportunityResult(NamedTuple):
    """Comprehensive filtered opportunity result with business intelligence"""
    # Original enhanced classification data
    notice_identifier: str
    enhanced_result: 'EnhancedClassificationResult'
    tender_data: Dict
    
    # Filter evaluation results
    filter_results: Dict           # Detailed results from each filter category
    overall_filter_score: float    # Combined filter score (0-1)
    filter_passes: bool           # Whether opportunity passes all filters
    filter_recommendation: str    # Detailed filtering recommendation
    
    # Competition analysis
    competition_assessment: Dict   # Detailed competition analysis
    bid_probability: float        # Estimated probability of winning bid
    recommended_bid_strategy: str  # Strategic recommendation for bidding
    
    # Business intelligence enhancements
    risk_factors: List[str]       # Identified risk factors
    success_factors: List[str]    # Identified success factors
    resource_requirements: Dict   # Estimated resource requirements
    strategic_value: str          # HIGH/MEDIUM/LOW strategic value assessment
    
    # Decision support
    final_recommendation: str     # PURSUE/CONSIDER/AVOID
    confidence_level: float       # Confidence in recommendation (0-1)
    next_actions: List[str]       # Recommended next steps

class ValueFilters:
    """Contract value-based filtering with capacity assessment"""
    
    def __init__(self, config: Dict):
        self.min_value = config.get('min_value', 50000)
        self.max_value = config.get('max_value', 10000000)
        self.sweet_spot_min = config.get('sweet_spot_min', 100000)
        self.sweet_spot_max = config.get('sweet_spot_max', 2000000)
        self.capacity_threshold = config.get('capacity_threshold', 5000000)
        
        logger.info(f"Value filters initialized: £{self.min_value:,} - £{self.max_value:,}")
    
    def evaluate_value_fit(self, tender: Dict) -> Dict:
        """Evaluate contract value against business criteria"""
        value = tender.get('value_high', 0)
        
        if value == 0:
            return {
                'passes': True,
                'reason': 'value_unknown',
                'score': 0.5,
                'value': 0,
                'assessment': 'Value TBD - requires clarification'
            }
        
        # Hard exclusions
        if value < self.min_value:
            return {
                'passes': False,
                'reason': 'below_minimum_value',
                'score': 0,
                'value': value,
                'assessment': f'Below £{self.min_value:,} minimum threshold'
            }
        
        if value > self.max_value:
            return {
                'passes': False,
                'reason': 'exceeds_maximum_value',
                'score': 0,
                'value': value,
                'assessment': f'Exceeds £{self.max_value:,} maximum threshold'
            }
        
        # Capacity assessment
        if value > self.capacity_threshold:
            return {
                'passes': False,
                'reason': 'exceeds_organizational_capacity',
                'score': 0,
                'value': value,
                'assessment': f'Exceeds £{self.capacity_threshold:,} capacity limit'
            }
        
        # Sweet spot prioritization
        if self.sweet_spot_min <= value <= self.sweet_spot_max:
            return {
                'passes': True,
                'reason': 'optimal_value_range',
                'score': 1.0,
                'value': value,
                'assessment': 'Optimal value range - high ROI potential'
            }
        
        # Acceptable range with scoring adjustment
        if value < self.sweet_spot_min:
            score = 0.7
            assessment = 'Below optimal range but acceptable'
        else:  # value > sweet_spot_max
            score = 0.8
            assessment = 'Above optimal range but manageable'
        
        return {
            'passes': True,
            'reason': 'acceptable_value_range',
            'score': score,
            'value': value,
            'assessment': assessment
        }

class TimelineFilters:
    """Timeline-based filtering with urgency assessment"""
    
    def __init__(self, config: Dict):
        self.min_lead_time = config.get('min_lead_time', 14)
        self.max_timeline = config.get('max_timeline', 730)
        self.optimal_window_start = config.get('optimal_window_start', 30)
        self.optimal_window_end = config.get('optimal_window_end', 90)
        
        logger.info(f"Timeline filters initialized: {self.min_lead_time}-{self.max_timeline} days range")
    
    def calculate_days_remaining(self, closing_date: str) -> int:
        """Calculate days remaining until tender closing"""
        try:
            if 'T' in closing_date:
                closing_dt = datetime.fromisoformat(closing_date.replace('Z', '+00:00'))
            else:
                closing_dt = datetime.strptime(closing_date, '%Y-%m-%d')
            
            return (closing_dt - datetime.now()).days
        except (ValueError, TypeError):
            return -1  # Invalid date
    
    def evaluate_timeline_fit(self, tender: Dict) -> Dict:
        """Evaluate timeline against bid preparation requirements"""
        closing_date = tender.get('closing_date')
        
        if not closing_date:
            return {
                'passes': True,
                'reason': 'no_deadline_specified',
                'score': 0.6,
                'days_remaining': None,
                'assessment': 'No deadline specified - requires clarification'
            }
        
        days_remaining = self.calculate_days_remaining(closing_date)
        
        if days_remaining < 0:
            return {
                'passes': False,
                'reason': 'opportunity_expired',
                'score': 0,
                'days_remaining': days_remaining,
                'assessment': 'Opportunity has expired'
            }
        
        # Hard exclusions
        if days_remaining < self.min_lead_time:
            return {
                'passes': False,
                'reason': 'insufficient_preparation_time',
                'score': 0,
                'days_remaining': days_remaining,
                'assessment': f'Only {days_remaining} days - insufficient for quality bid preparation'
            }
        
        if days_remaining > self.max_timeline:
            return {
                'passes': False,
                'reason': 'too_distant_future',
                'score': 0,
                'days_remaining': days_remaining,
                'assessment': f'{days_remaining} days away - too distant for current planning'
            }
        
        # Optimal window assessment
        if self.optimal_window_start <= days_remaining <= self.optimal_window_end:
            return {
                'passes': True,
                'reason': 'optimal_timing_window',
                'score': 1.0,
                'days_remaining': days_remaining,
                'assessment': f'{days_remaining} days - optimal preparation window'
            }
        
        # Suboptimal but acceptable timing
        if days_remaining < self.optimal_window_start:
            score = max(0.4, 1.0 - (self.optimal_window_start - days_remaining) / self.optimal_window_start)
            assessment = f'{days_remaining} days - urgent but manageable'
            reason = 'urgent_timeline'
        else:  # days_remaining > optimal_window_end
            score = max(0.6, 1.0 - (days_remaining - self.optimal_window_end) / 365)
            assessment = f'{days_remaining} days - future opportunity'
            reason = 'future_timeline'
        
        return {
            'passes': True,
            'reason': reason,
            'score': score,
            'days_remaining': days_remaining,
            'assessment': assessment
        }

class CapabilityFilters:
    """Capability matching and complexity assessment"""
    
    def __init__(self, config: Dict):
        self.required_skills = config.get('required_skills', [])
        self.min_technical_overlap = config.get('min_technical_overlap', 2)
        self.max_complexity_threshold = config.get('max_complexity_threshold', 7)
        
        # Capability matrix with organizational strengths
        self.capability_matrix = {
            'digital_transformation': {
                'required_terms': ['digital transformation', 'modernisation', 'digital strategy', 'digital reform'],
                'technical_terms': ['api', 'cloud', 'microservices', 'integration', 'automation'],
                'complexity_indicators': ['enterprise architecture', 'legacy migration', 'system integration'],
                'complexity_weight': 0.8,
                'organizational_strength': 9  # 1-10 scale
            },
            'software_development': {
                'required_terms': ['software development', 'application development', 'system development', 'web development'],
                'technical_terms': ['python', 'javascript', 'database', 'web application', 'mobile app'],
                'complexity_indicators': ['custom development', 'bespoke solution', 'full stack'],
                'complexity_weight': 0.6,
                'organizational_strength': 8
            },
            'cloud_infrastructure': {
                'required_terms': ['cloud', 'aws', 'azure', 'infrastructure', 'cloud migration'],
                'technical_terms': ['docker', 'kubernetes', 'devops', 'automation', 'ci/cd'],
                'complexity_indicators': ['infrastructure as code', 'container orchestration', 'multi-cloud'],
                'complexity_weight': 0.7,
                'organizational_strength': 7
            },
            'data_analytics': {
                'required_terms': ['data analytics', 'business intelligence', 'data science', 'machine learning'],
                'technical_terms': ['python', 'sql', 'analytics', 'dashboard', 'reporting'],
                'complexity_indicators': ['big data', 'real-time analytics', 'predictive modeling'],
                'complexity_weight': 0.9,
                'organizational_strength': 6
            }
        }
        
        logger.info(f"Capability filters initialized with {len(self.capability_matrix)} capability areas")
    
    def assess_complexity(self, text: str, technical_terms: List[str]) -> float:
        """Assess technical complexity of tender requirements (1-10 scale)"""
        complexity_score = 3.0  # Base complexity
        
        # High complexity indicators
        high_complexity_terms = [
            'enterprise', 'architecture', 'integration', 'legacy', 'migration',
            'transformation', 'bespoke', 'custom', 'complex', 'advanced'
        ]
        
        complexity_matches = sum(1 for term in high_complexity_terms if term in text.lower())
        complexity_score += complexity_matches * 0.5
        
        # Technical term density indicates complexity
        if len(technical_terms) >= 5:
            complexity_score += 1.0
        elif len(technical_terms) >= 3:
            complexity_score += 0.5
        
        # Multiple technology stacks indicate higher complexity
        tech_stacks = ['frontend', 'backend', 'database', 'cloud', 'mobile', 'api']
        stack_count = sum(1 for stack in tech_stacks if any(stack in term for term in technical_terms))
        if stack_count >= 3:
            complexity_score += 1.0
        
        return min(complexity_score, 10.0)
    
    def evaluate_capability_match(self, tender: Dict, enhanced_result) -> Dict:
        """Evaluate capability match against organizational strengths"""
        text = f"{tender.get('title', '')} {tender.get('description', '')}".lower()
        
        # Identify required capabilities from tender
        required_capabilities = []
        capability_evidence = {}
        
        for capability, criteria in self.capability_matrix.items():
            # Check for required terms
            matched_terms = [term for term in criteria['required_terms'] if term in text]
            if matched_terms:
                required_capabilities.append(capability)
                capability_evidence[capability] = {
                    'matched_terms': matched_terms,
                    'strength': criteria['organizational_strength']
                }
        
        if not required_capabilities:
            return {
                'passes': True,
                'reason': 'no_specific_capability_requirements',
                'score': 0.7,
                'required_capabilities': [],
                'assessment': 'No specific capability requirements identified'
            }
        
        # Assess complexity level
        complexity_score = self.assess_complexity(text, enhanced_result.technical_terms)
        
        if complexity_score > self.max_complexity_threshold:
            return {
                'passes': False,
                'reason': 'complexity_exceeds_threshold',
                'score': 0,
                'complexity_score': complexity_score,
                'assessment': f'Complexity score {complexity_score:.1f} exceeds threshold {self.max_complexity_threshold}'
            }
        
        # Evaluate each required capability
        capability_assessments = []
        for capability in required_capabilities:
            criteria = self.capability_matrix[capability]
            evidence = capability_evidence[capability]
            
            # Technical term alignment
            tech_overlap = len(set(enhanced_result.technical_terms) & set(criteria['technical_terms']))
            
            # Organizational strength vs complexity
            strength_vs_complexity = criteria['organizational_strength'] / max(complexity_score, 1.0)
            
            # Capability confidence calculation
            base_confidence = min(evidence['strength'] / 10.0, 1.0)
            tech_confidence = min(tech_overlap / len(criteria['technical_terms']), 1.0) if criteria['technical_terms'] else 0.5
            complexity_confidence = min(strength_vs_complexity / 1.5, 1.0)
            
            overall_confidence = (base_confidence * 0.4 + tech_confidence * 0.3 + complexity_confidence * 0.3)
            
            capability_assessments.append({
                'capability': capability,
                'confidence': overall_confidence,
                'technical_overlap': tech_overlap,
                'strength_vs_complexity': strength_vs_complexity,
                'matched_terms': evidence['matched_terms']
            })
        
        # Overall capability match assessment
        if not capability_assessments:
            return {'passes': False, 'reason': 'no_capability_matches', 'score': 0}
        
        avg_confidence = sum(ca['confidence'] for ca in capability_assessments) / len(capability_assessments)
        
        # Minimum confidence threshold
        if avg_confidence < 0.3:
            return {
                'passes': False,
                'reason': 'insufficient_capability_confidence',
                'score': avg_confidence,
                'capability_assessments': capability_assessments,
                'assessment': f'Low capability match confidence: {avg_confidence:.2f}'
            }
        
        return {
            'passes': True,
            'reason': 'capability_requirements_met',
            'score': avg_confidence,
            'complexity_score': complexity_score,
            'capability_assessments': capability_assessments,
            'assessment': f'Strong capability match: {avg_confidence:.2f} confidence'
        }

class GeographicFilters:
    """Geographic and delivery model filtering"""
    
    def __init__(self, config: Dict):
        self.preferred_regions = config.get('preferred_regions', ['UK-wide', 'England', 'Scotland'])
        self.excluded_regions = config.get('excluded_regions', [])
        self.remote_friendly = config.get('remote_friendly', True)
        self.max_travel_distance = config.get('max_travel_distance', 200)
        
        # UK cities and regions for location matching
        self.uk_locations = {
            'london': {'region': 'England', 'distance_from_base': 50},
            'manchester': {'region': 'England', 'distance_from_base': 120},
            'birmingham': {'region': 'England', 'distance_from_base': 80},
            'glasgow': {'region': 'Scotland', 'distance_from_base': 300},
            'edinburgh': {'region': 'Scotland', 'distance_from_base': 280},
            'cardiff': {'region': 'Wales', 'distance_from_base': 150},
            'bristol': {'region': 'England', 'distance_from_base': 100},
            'leeds': {'region': 'England', 'distance_from_base': 150},
            'liverpool': {'region': 'England', 'distance_from_base': 140},
            'newcastle': {'region': 'England', 'distance_from_base': 200}
        }
        
        logger.info(f"Geographic filters initialized: {len(self.preferred_regions)} preferred regions")
    
    def extract_location_info(self, tender: Dict) -> Dict:
        """Extract location information from tender data"""
        # Check multiple fields for location information
        text_fields = [
            tender.get('title', ''),
            tender.get('description', ''),
            tender.get('organisation_name', ''),
            tender.get('location', ''),
            tender.get('region', '')
        ]
        
        combined_text = ' '.join(text_fields).lower()
        
        location_info = {
            'regions_mentioned': [],
            'cities_mentioned': [],
            'specific_location': None,
            'uk_wide': False,
            'remote_indicators': []
        }
        
        # Check for UK-wide indicators
        uk_wide_terms = ['uk-wide', 'uk wide', 'nationwide', 'national', 'england and wales', 'great britain']
        if any(term in combined_text for term in uk_wide_terms):
            location_info['uk_wide'] = True
        
        # Check for specific cities
        for city, details in self.uk_locations.items():
            if city in combined_text:
                location_info['cities_mentioned'].append({
                    'city': city,
                    'region': details['region'],
                    'distance': details['distance_from_base']
                })
        
        # Check for regions
        regions = ['england', 'scotland', 'wales', 'northern ireland']
        for region in regions:
            if region in combined_text:
                location_info['regions_mentioned'].append(region.title())
        
        return location_info
    
    def detect_remote_delivery(self, tender: Dict) -> Dict:
        """Detect remote/distributed delivery indicators"""
        text = f"{tender.get('title', '')} {tender.get('description', '')}".lower()
        
        remote_indicators = {
            'positive': ['remote', 'distributed', 'virtual', 'online', 'cloud-based', 'digital delivery'],
            'negative': ['on-site', 'on site', 'premises', 'physical presence', 'face-to-face', 'in-person']
        }
        
        positive_matches = [term for term in remote_indicators['positive'] if term in text]
        negative_matches = [term for term in remote_indicators['negative'] if term in text]
        
        # Determine remote friendliness
        if positive_matches and not negative_matches:
            remote_score = 1.0
            assessment = 'Remote delivery explicitly supported'
        elif positive_matches and negative_matches:
            remote_score = 0.6
            assessment = 'Hybrid delivery model possible'
        elif negative_matches:
            remote_score = 0.2
            assessment = 'On-site presence required'
        else:
            remote_score = 0.5  # Neutral
            assessment = 'Delivery model not specified'
        
        return {
            'is_remote_friendly': remote_score >= 0.5,
            'remote_score': remote_score,
            'positive_indicators': positive_matches,
            'negative_indicators': negative_matches,
            'assessment': assessment
        }
    
    def evaluate_geographic_fit(self, tender: Dict) -> Dict:
        """Evaluate geographic and delivery model fit"""
        location_info = self.extract_location_info(tender)
        remote_info = self.detect_remote_delivery(tender)
        
        # Remote delivery gets highest preference if enabled
        if self.remote_friendly and remote_info['is_remote_friendly']:
            return {
                'passes': True,
                'reason': 'remote_delivery_supported',
                'score': 1.0,
                'location_info': location_info,
                'remote_info': remote_info,
                'assessment': 'Remote delivery supported - optimal geographic fit'
            }
        
        # UK-wide opportunities are generally acceptable
        if location_info['uk_wide']:
            score = 0.9 if self.remote_friendly else 0.7
            return {
                'passes': True,
                'reason': 'uk_wide_opportunity',
                'score': score,
                'location_info': location_info,
                'assessment': 'UK-wide opportunity - good geographic fit'
            }
        
        # Regional preference matching
        if location_info['regions_mentioned']:
            preferred_matches = [r for r in location_info['regions_mentioned'] if r in self.preferred_regions]
            excluded_matches = [r for r in location_info['regions_mentioned'] if r in self.excluded_regions]
            
            if excluded_matches:
                return {
                    'passes': False,
                    'reason': 'excluded_region',
                    'score': 0,
                    'excluded_regions': excluded_matches,
                    'assessment': f'Located in excluded region(s): {", ".join(excluded_matches)}'
                }
            
            if preferred_matches:
                return {
                    'passes': True,
                    'reason': 'preferred_region_match',
                    'score': 0.9,
                    'matched_regions': preferred_matches,
                    'assessment': f'Located in preferred region(s): {", ".join(preferred_matches)}'
                }
        
        # City-specific assessment
        if location_info['cities_mentioned']:
            closest_city = min(location_info['cities_mentioned'], key=lambda x: x['distance'])
            
            if closest_city['distance'] <= self.max_travel_distance:
                score = max(0.4, 1.0 - (closest_city['distance'] / self.max_travel_distance))
                return {
                    'passes': True,
                    'reason': 'acceptable_travel_distance',
                    'score': score,
                    'closest_city': closest_city,
                    'assessment': f"Located in {closest_city['city']} - {closest_city['distance']} miles from base"
                }
            else:
                return {
                    'passes': False,
                    'reason': 'excessive_travel_distance',
                    'score': 0,
                    'closest_city': closest_city,
                    'assessment': f"Located in {closest_city['city']} - {closest_city['distance']} miles exceeds {self.max_travel_distance} mile limit"
                }
        
        # Default neutral assessment for unclear locations
        return {
            'passes': True,
            'reason': 'location_neutral',
            'score': 0.6,
            'location_info': location_info,
            'assessment': 'Location details unclear - neutral geographic fit'
        }

class CompetitionAssessment:
    """Advanced competition analysis and bid probability calculation"""
    
    def __init__(self):
        self.competition_factors = {
            'contract_value_bands': {
                (0, 100000): {'competition_level': 3.0, 'typical_bidders': '3-5'},
                (100000, 500000): {'competition_level': 5.0, 'typical_bidders': '5-8'},
                (500000, 2000000): {'competition_level': 7.0, 'typical_bidders': '8-12'},
                (2000000, 10000000): {'competition_level': 9.0, 'typical_bidders': '10-20'},
            },
            'specialization_multipliers': {
                'highly_specialized': 0.6,  # Digital transformation, AI, blockchain
                'specialized': 0.8,         # Software development, cloud
                'general': 1.2              # IT support, maintenance
            },
            'framework_adjustments': {
                'g_cloud': -1.0,           # G-Cloud framework reduces competition
                'digital_outcomes': -0.5,  # DOS framework slight reduction
                'open_tender': 0.0,        # No adjustment
                'restricted': -1.5         # Restricted procedures significant reduction
            }
        }
        
        logger.info("Competition assessment engine initialized")
    
    def assess_specialization_level(self, tender: Dict, enhanced_result) -> Dict:
        """Assess the specialization level of tender requirements"""
        text = f"{tender.get('title', '')} {tender.get('description', '')}".lower()
        
        # Highly specialized indicators
        highly_specialized_terms = [
            'digital transformation', 'artificial intelligence', 'machine learning',
            'blockchain', 'enterprise architecture', 'legacy modernization',
            'system integration', 'data science', 'cybersecurity'
        ]
        
        # Specialized indicators
        specialized_terms = [
            'software development', 'web development', 'mobile app',
            'cloud migration', 'api development', 'database design',
            'devops', 'automation', 'analytics'
        ]
        
        # General IT indicators
        general_terms = [
            'it support', 'technical support', 'maintenance',
            'helpdesk', 'hardware', 'installation'
        ]
        
        highly_specialized_count = sum(1 for term in highly_specialized_terms if term in text)
        specialized_count = sum(1 for term in specialized_terms if term in text)
        general_count = sum(1 for term in general_terms if term in text)
        
        # Determine specialization level
        if highly_specialized_count >= 2 or (highly_specialized_count >= 1 and len(enhanced_result.technical_terms) >= 4):
            level = 'highly_specialized'
            multiplier = self.competition_factors['specialization_multipliers']['highly_specialized']
            description = 'Highly specialized requirements - fewer qualified bidders'
        elif specialized_count >= 2 or (specialized_count >= 1 and len(enhanced_result.technical_terms) >= 2):
            level = 'specialized'
            multiplier = self.competition_factors['specialization_multipliers']['specialized']
            description = 'Specialized technical requirements - moderate competition'
        else:
            level = 'general'
            multiplier = self.competition_factors['specialization_multipliers']['general']
            description = 'General IT requirements - high competition'
        
        return {
            'level': level,
            'multiplier': multiplier,
            'description': description,
            'highly_specialized_matches': highly_specialized_count,
            'specialized_matches': specialized_count,
            'general_matches': general_count
        }
    
    def detect_framework_requirements(self, tender: Dict) -> Dict:
        """Detect procurement framework requirements"""
        text = f"{tender.get('title', '')} {tender.get('description', '')}".lower()
        
        framework_indicators = {
            'g_cloud': ['g-cloud', 'gcloud', 'g cloud'],
            'digital_outcomes': ['digital outcomes', 'dos', 'digital marketplace'],
            'restricted': ['restricted procedure', 'pre-qualification', 'pqq', 'shortlist'],
            'framework_agreement': ['framework agreement', 'call-off', 'call off']
        }
        
        detected_frameworks = []
        for framework, indicators in framework_indicators.items():
            if any(indicator in text for indicator in indicators):
                detected_frameworks.append(framework)
        
        if detected_frameworks:
            # Use the framework with the most significant competition adjustment
            primary_framework = min(detected_frameworks, 
                                  key=lambda f: self.competition_factors['framework_adjustments'].get(f, 0))
            
            adjustment = self.competition_factors['framework_adjustments'].get(primary_framework, 0)
            
            return {
                'requires_framework': True,
                'primary_framework': primary_framework,
                'all_frameworks': detected_frameworks,
                'competition_adjustment': adjustment,
                'description': f'Requires {primary_framework.replace("_", " ").title()} framework access'
            }
        
        return {
            'requires_framework': False,
            'primary_framework': None,
            'competition_adjustment': 0,
            'description': 'Open tender - no specific framework requirements'
        }
    
    def assess_geographic_barriers(self, tender: Dict) -> Dict:
        """Assess geographic barriers to competition"""
        text = f"{tender.get('title', '')} {tender.get('description', '')}".lower()
        
        # Geographic barriers that might reduce competition
        barriers = {
            'on_site_required': ['on-site', 'on site', 'premises', 'physical presence'],
            'specific_location': ['london', 'manchester', 'birmingham', 'glasgow', 'edinburgh'],
            'security_clearance': ['security clearance', 'dv clearance', 'sc clearance', 'baseline clearance'],
            'local_presence': ['local presence', 'local office', 'regional office']
        }
        
        detected_barriers = []
        competition_adjustment = 0
        
        for barrier_type, indicators in barriers.items():
            if any(indicator in text for indicator in indicators):
                detected_barriers.append(barrier_type)
                
                # Adjust competition based on barrier type
                if barrier_type == 'security_clearance':
                    competition_adjustment -= 2.0  # Significant barrier
                elif barrier_type == 'on_site_required':
                    competition_adjustment -= 0.5
                elif barrier_type == 'local_presence':
                    competition_adjustment -= 1.0
                elif barrier_type == 'specific_location':
                    competition_adjustment -= 0.3
        
        return {
            'barriers_detected': detected_barriers,
            'competition_adjustment': competition_adjustment,
            'description': f'Geographic barriers: {", ".join(detected_barriers)}' if detected_barriers else 'No significant geographic barriers'
        }
    
    def calculate_bid_probability(self, competition_level: float, relevance_score: float, 
                                organizational_factors: Dict = None) -> Dict:
        """Calculate estimated bid probability based on multiple factors"""
        
        # Base probability from competition level (inverse relationship)
        base_probability = max(0.05, 1.0 - (competition_level / 10.0))
        
        # Relevance score adjustment (higher relevance = better fit = higher probability)
        relevance_multiplier = min(2.0, relevance_score / 50.0)  # 50 score = 1.0 multiplier
        
        # Organizational factors (if provided)
        org_multiplier = 1.0
        if organizational_factors:
            # Past performance factor
            past_performance = organizational_factors.get('past_performance_score', 0.7)  # 0-1 scale
            org_multiplier *= (0.7 + (past_performance * 0.6))  # 0.7-1.3 range
            
            # Relationship factor
            existing_relationship = organizational_factors.get('existing_relationship', False)
            if existing_relationship:
                org_multiplier *= 1.2
        
        # Calculate final probability
        final_probability = min(0.8, base_probability * relevance_multiplier * org_multiplier)
        
        # Confidence calculation
        confidence = 0.7  # Base confidence in probability estimation
        if relevance_score >= 70:
            confidence += 0.1
        if competition_level <= 5:
            confidence += 0.1
        
        confidence = min(0.9, confidence)
        
        return {
            'bid_probability': final_probability,
            'confidence': confidence,
            'factors': {
                'base_probability': base_probability,
                'relevance_multiplier': relevance_multiplier,
                'organizational_multiplier': org_multiplier,
                'competition_level': competition_level
            },
            'probability_band': self.categorize_probability(final_probability)
        }
    
    def categorize_probability(self, probability: float) -> str:
        """Categorize bid probability into bands"""
        if probability >= 0.4:
            return 'HIGH'
        elif probability >= 0.2:
            return 'MEDIUM'
        elif probability >= 0.1:
            return 'LOW'
        else:
            return 'VERY_LOW'
    
    def assess_competition_level(self, tender: Dict, enhanced_result) -> Dict:
        """Comprehensive competition level assessment"""
        competition_score = 5.0  # Base competition level (1-10 scale)
        assessment_factors = {}
        
        # Value-based competition assessment
        value = tender.get('value_high', 0)
        for (min_val, max_val), factors in self.competition_factors['contract_value_bands'].items():
            if min_val <= value < max_val:
                competition_score = factors['competition_level']
                assessment_factors['value_band'] = {
                    'range': f'£{min_val:,}-£{max_val:,}',
                    'typical_bidders': factors['typical_bidders'],
                    'competition_level': factors['competition_level']
                }
                break
        
        # SME suitability impact
        sme_suitable = tender.get('suitable_for_sme', '').lower()
        if sme_suitable in ['yes', 'true']:
            competition_score -= 1.0
            assessment_factors['sme_impact'] = {'adjustment': -1.0, 'reason': 'SME-friendly reduces competition'}
        elif sme_suitable in ['no', 'false'] and value > 1000000:
            competition_score += 1.5
            assessment_factors['sme_impact'] = {'adjustment': +1.5, 'reason': 'Large-corp-only increases competition'}
        
        # Specialization level assessment
        specialization = self.assess_specialization_level(tender, enhanced_result)
        competition_score *= specialization['multiplier']
        assessment_factors['specialization'] = specialization
        
        # Framework requirements impact
        framework_info = self.detect_framework_requirements(tender)
        competition_score += framework_info['competition_adjustment']
        assessment_factors['framework'] = framework_info
        
        # Geographic barriers impact
        geographic_barriers = self.assess_geographic_barriers(tender)
        competition_score += geographic_barriers['competition_adjustment']
        assessment_factors['geographic'] = geographic_barriers
        
        # Ensure competition score stays within reasonable bounds
        final_competition_score = max(1.0, min(10.0, competition_score))
        
        # Calculate bid probability
        bid_probability_info = self.calculate_bid_probability(
            final_competition_score, 
            enhanced_result.final_relevance_score
        )
        
        return {
            'competition_level': final_competition_score,
            'competition_category': self.categorize_competition(final_competition_score),
            'assessment_factors': assessment_factors,
            'bid_probability': bid_probability_info['bid_probability'],
            'probability_confidence': bid_probability_info['confidence'],
            'probability_band': bid_probability_info['probability_band'],
            'recommendation': self.generate_competition_recommendation(final_competition_score, bid_probability_info['bid_probability'])
        }
    
    def categorize_competition(self, competition_level: float) -> str:
        """Categorize competition level"""
        if competition_level <= 3:
            return 'LOW'
        elif competition_level <= 6:
            return 'MEDIUM'
        elif competition_level <= 8:
            return 'HIGH'
        else:
            return 'VERY_HIGH'
    
    def generate_competition_recommendation(self, competition_level: float, bid_probability: float) -> str:
        """Generate strategic recommendation based on competition analysis"""
        if competition_level <= 4 and bid_probability >= 0.3:
            return 'PURSUE - Low competition with good win probability'
        elif competition_level <= 6 and bid_probability >= 0.2:
            return 'CONSIDER - Moderate competition, reasonable win chance'
        elif competition_level <= 8 and bid_probability >= 0.15:
            return 'EVALUATE - High competition, requires strong bid strategy'
        else:
            return 'AVOID - Very high competition with low win probability'

class FilterConfiguration:
    """Advanced filter configuration with profiles for different strategies"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.default_config = {
            'value_filters': {
                'min_value': 50000,
                'max_value': 10000000,
                'sweet_spot_min': 100000,
                'sweet_spot_max': 2000000,
                'capacity_threshold': 5000000
            },
            'timeline_filters': {
                'min_lead_time': 14,
                'max_timeline': 730,
                'optimal_window_start': 30,
                'optimal_window_end': 90
            },
            'capability_filters': {
                'required_skills': ['digital_transformation', 'software_development'],
                'min_technical_overlap': 2,
                'max_complexity_threshold': 7
            },
            'geographic_filters': {
                'preferred_regions': ['UK-wide', 'England', 'Scotland'],
                'excluded_regions': [],
                'remote_friendly': True,
                'max_travel_distance': 200
            },
            'competition_filters': {
                'max_competition_level': 8.0,
                'min_bid_probability': 0.15,
                'avoid_framework_only': False
            },
            'scoring_thresholds': {
                'min_relevance_score': 40.0,
                'min_combined_filter_score': 0.6,
                'priority_boost_threshold': 70.0
            }
        }
        
        self.config = self.load_config(config_path) if config_path else self.default_config
        logger.info("Filter configuration initialized")
    
    def load_config(self, config_path: str) -> Dict:
        """Load configuration from JSON file"""
        try:
            with open(config_path, 'r') as f:
                custom_config = json.load(f)
            
            # Merge with defaults
            merged_config = self.default_config.copy()
            for section, settings in custom_config.items():
                if section in merged_config:
                    merged_config[section].update(settings)
                else:
                    merged_config[section] = settings
            
            return merged_config
        except Exception as e:
            logger.warning(f"Failed to load config from {config_path}: {e}")
            return self.default_config
    
    def create_filter_profiles(self) -> Dict:
        """Create different filtering profiles for different bidding strategies"""
        profiles = {
            'aggressive': {
                'description': 'Cast wide net - pursue more opportunities with higher risk tolerance',
                'config_overrides': {
                    'scoring_thresholds': {
                        'min_relevance_score': 30.0,
                        'min_combined_filter_score': 0.4
                    },
                    'competition_filters': {
                        'max_competition_level': 9.0,
                        'min_bid_probability': 0.10
                    },
                    'value_filters': {
                        'min_value': 25000,  # Lower minimum
                        'sweet_spot_min': 50000
                    }
                }
            },
            'balanced': {
                'description': 'Balanced approach - good opportunities with reasonable competition',
                'config_overrides': {
                    'scoring_thresholds': {
                        'min_relevance_score': 40.0,
                        'min_combined_filter_score': 0.6
                    },
                    'competition_filters': {
                        'max_competition_level': 7.0,
                        'min_bid_probability': 0.15
                    }
                }
            },
            'conservative': {
                'description': 'High-probability wins - focus on best opportunities only',
                'config_overrides': {
                    'scoring_thresholds': {
                        'min_relevance_score': 60.0,
                        'min_combined_filter_score': 0.8
                    },
                    'competition_filters': {
                        'max_competition_level': 5.0,
                        'min_bid_probability': 0.25
                    },
                    'capability_filters': {
                        'max_complexity_threshold': 6  # Lower complexity threshold
                    }
                }
            },
            'strategic': {
                'description': 'Strategic partnerships - high-value, relationship-building opportunities',
                'config_overrides': {
                    'scoring_thresholds': {
                        'min_relevance_score': 50.0,
                        'min_combined_filter_score': 0.7
                    },
                    'competition_filters': {
                        'max_competition_level': 8.0,
                        'min_bid_probability': 0.12
                    },
                    'value_filters': {
                        'min_value': 500000,  # High-value focus
                        'sweet_spot_min': 750000
                    },
                    'geographic_filters': {
                        'preferred_regions': ['UK-wide', 'England']  # Broader reach
                    }
                }
            },
            'rapid_growth': {
                'description': 'Growth-focused - prioritize volume and learning opportunities',
                'config_overrides': {
                    'scoring_thresholds': {
                        'min_relevance_score': 35.0,
                        'min_combined_filter_score': 0.5
                    },
                    'competition_filters': {
                        'max_competition_level': 8.5,
                        'min_bid_probability': 0.08
                    },
                    'capability_filters': {
                        'max_complexity_threshold': 8  # Accept higher complexity for learning
                    },
                    'timeline_filters': {
                        'min_lead_time': 10,  # Accept shorter timelines
                        'optimal_window_start': 21
                    }
                }
            }
        }
        
        return profiles
    
    def apply_profile(self, profile_name: str) -> Dict:
        """Apply a specific profile to the base configuration"""
        profiles = self.create_filter_profiles()
        
        if profile_name not in profiles:
            logger.warning(f"Unknown profile '{profile_name}', using balanced profile")
            profile_name = 'balanced'
        
        profile = profiles[profile_name]
        config_copy = json.loads(json.dumps(self.config))  # Deep copy
        
        # Apply overrides
        for section, overrides in profile['config_overrides'].items():
            if section in config_copy:
                config_copy[section].update(overrides)
            else:
                config_copy[section] = overrides
        
        return config_copy

class AdvancedOpportunityFilter:
    """Main advanced filtering engine combining all filter categories"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.filter_config = FilterConfiguration(config_path)
        self.initialize_filters()
        
        logger.info("Advanced opportunity filter initialized")
    
    def initialize_filters(self, profile_config: Dict = None):
        """Initialize filter components with configuration"""
        config = profile_config or self.filter_config.config
        
        self.value_filters = ValueFilters(config['value_filters'])
        self.timeline_filters = TimelineFilters(config['timeline_filters'])
        self.capability_filters = CapabilityFilters(config['capability_filters'])
        self.geographic_filters = GeographicFilters(config['geographic_filters'])
        self.competition_assessment = CompetitionAssessment()
        self.current_config = config
    
    def apply_all_filters(self, enhanced_result, tender_data: Dict) -> Dict:
        """Apply all filter categories and return comprehensive results"""
        filter_results = {}
        
        # Apply each filter category
        filter_results['value'] = self.value_filters.evaluate_value_fit(tender_data)
        filter_results['timeline'] = self.timeline_filters.evaluate_timeline_fit(tender_data)
        filter_results['capability'] = self.capability_filters.evaluate_capability_match(tender_data, enhanced_result)
        filter_results['geographic'] = self.geographic_filters.evaluate_geographic_fit(tender_data)
        
        return filter_results
    
    def calculate_overall_filter_score(self, filter_results: Dict) -> float:
        """Calculate combined filter score weighted by importance"""
        weights = {
            'value': 0.3,      # 30% - Contract value fit
            'timeline': 0.25,  # 25% - Timeline feasibility
            'capability': 0.3, # 30% - Capability match
            'geographic': 0.15 # 15% - Geographic fit
        }
        
        weighted_score = 0
        for category, weight in weights.items():
            if category in filter_results and filter_results[category]['passes']:
                weighted_score += filter_results[category]['score'] * weight
        
        return weighted_score
    
    def evaluate_against_profile(self, enhanced_result, filter_results: Dict, 
                                competition_analysis: Dict, profile_config: Dict) -> bool:
        """Evaluate opportunity against profile-specific criteria"""
        thresholds = profile_config['scoring_thresholds']
        competition_limits = profile_config['competition_filters']
        
        # Check relevance score threshold
        if enhanced_result.final_relevance_score < thresholds['min_relevance_score']:
            return False
        
        # Check combined filter score
        overall_filter_score = self.calculate_overall_filter_score(filter_results)
        if overall_filter_score < thresholds['min_combined_filter_score']:
            return False
        
        # Check competition limits
        if competition_analysis['competition_level'] > competition_limits['max_competition_level']:
            return False
        
        if competition_analysis['bid_probability'] < competition_limits['min_bid_probability']:
            return False
        
        # All filters passed
        return True
    
    def analyze_risk_success_factors(self, enhanced_result, filter_results: Dict, 
                                   competition_analysis: Dict) -> Tuple[List[str], List[str]]:
        """Analyze risk factors and success factors for the opportunity"""
        risk_factors = []
        success_factors = []
        
        # Timeline risks/successes
        timeline_result = filter_results.get('timeline', {})
        if timeline_result.get('days_remaining', 0) < 21:
            risk_factors.append('Short preparation time - limited bid development opportunity')
        elif timeline_result.get('days_remaining', 0) > 60:
            success_factors.append('Adequate preparation time for comprehensive bid development')
        
        # Value risks/successes
        value_result = filter_results.get('value', {})
        if value_result.get('reason') == 'optimal_value_range':
            success_factors.append('Contract value in optimal range for strong ROI')
        elif value_result.get('value', 0) > 2000000:
            risk_factors.append('High-value contract requires significant resource commitment')
        
        # Capability risks/successes
        capability_result = filter_results.get('capability', {})
        if capability_result.get('score', 0) >= 0.8:
            success_factors.append('Strong capability alignment with tender requirements')
        elif capability_result.get('complexity_score', 0) > 7:
            risk_factors.append('High complexity project may strain organizational capacity')
        
        # Competition risks/successes
        if competition_analysis['competition_level'] <= 4:
            success_factors.append('Low competition level increases win probability')
        elif competition_analysis['competition_level'] >= 8:
            risk_factors.append('High competition level reduces win probability significantly')
        
        # Geographic risks/successes
        geographic_result = filter_results.get('geographic', {})
        if geographic_result.get('reason') == 'remote_delivery_supported':
            success_factors.append('Remote delivery supported - optimal delivery model')
        elif 'travel' in geographic_result.get('reason', ''):
            risk_factors.append('Travel requirements may impact project margins')
        
        return risk_factors, success_factors
    
    def estimate_resource_requirements(self, enhanced_result, tender_data: Dict, 
                                     filter_results: Dict) -> Dict:
        """Estimate resource requirements for pursuing the opportunity"""
        value = tender_data.get('value_high', 0)
        timeline_result = filter_results.get('timeline', {})
        capability_result = filter_results.get('capability', {})
        
        # Base resource estimation
        if value < 100000:
            team_size = 'Small (2-3 people)'
            duration_months = 3
            bid_effort_days = 5
        elif value < 500000:
            team_size = 'Medium (4-6 people)'
            duration_months = 6
            bid_effort_days = 10
        elif value < 2000000:
            team_size = 'Large (6-10 people)'
            duration_months = 12
            bid_effort_days = 15
        else:
            team_size = 'Very Large (10+ people)'
            duration_months = 18
            bid_effort_days = 25
        
        # Complexity adjustments
        complexity_score = capability_result.get('complexity_score', 5)
        if complexity_score >= 8:
            bid_effort_days *= 1.5
            duration_months *= 1.2
        
        # Timeline pressure adjustments
        days_remaining = timeline_result.get('days_remaining', 60)
        if days_remaining < 21:
            bid_effort_days *= 1.3  # More intensive effort required
        
        return {
            'estimated_team_size': team_size,
            'estimated_duration_months': duration_months,
            'bid_preparation_days': int(bid_effort_days),
            'project_complexity': 'High' if complexity_score >= 7 else 'Medium' if complexity_score >= 5 else 'Low',
            'resource_intensity': 'High' if value > 1000000 else 'Medium' if value > 200000 else 'Low'
        }
    
    def determine_strategic_value(self, enhanced_result, tender_data: Dict, 
                                filter_results: Dict) -> str:
        """Determine strategic value of the opportunity"""
        relevance_score = enhanced_result.final_relevance_score
        value = tender_data.get('value_high', 0)
        org_name = tender_data.get('organisation_name', '').lower()
        
        strategic_points = 0
        
        # High relevance score
        if relevance_score >= 70:
            strategic_points += 3
        elif relevance_score >= 50:
            strategic_points += 2
        elif relevance_score >= 35:
            strategic_points += 1
        
        # High-value contracts
        if value >= 1000000:
            strategic_points += 2
        elif value >= 500000:
            strategic_points += 1
        
        # Strategic organizations
        strategic_orgs = ['nhs digital', 'cabinet office', 'hmrc', 'mod', 'home office']
        if any(org in org_name for org in strategic_orgs):
            strategic_points += 2
        
        # Capability development opportunities
        capability_result = filter_results.get('capability', {})
        if capability_result.get('complexity_score', 0) >= 7:
            strategic_points += 1  # Learning opportunity
        
        # Geographic preference
        geographic_result = filter_results.get('geographic', {})
        if geographic_result.get('score', 0) >= 0.8:
            strategic_points += 1
        
        # Determine strategic value
        if strategic_points >= 6:
            return 'HIGH'
        elif strategic_points >= 3:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def generate_final_recommendation(self, enhanced_result, filter_results: Dict, 
                                    competition_analysis: Dict, overall_filter_score: float) -> Dict:
        """Generate final PURSUE/CONSIDER/AVOID recommendation with reasoning"""
        relevance_score = enhanced_result.final_relevance_score
        competition_level = competition_analysis['competition_level']
        bid_probability = competition_analysis['bid_probability']
        
        # Decision matrix
        if (relevance_score >= 70 and overall_filter_score >= 0.8 and 
            competition_level <= 6.0 and bid_probability >= 0.20):
            return {
                'recommendation': 'PURSUE',
                'confidence': 0.9,
                'reasoning': 'High-quality opportunity with strong win probability and excellent fit',
                'next_actions': [
                    'Begin immediate bid preparation',
                    'Assign senior team members',
                    'Conduct detailed requirements analysis',
                    'Develop competitive positioning strategy'
                ]
            }
        
        elif (relevance_score >= 50 and overall_filter_score >= 0.6 and 
              competition_level <= 8.0 and bid_probability >= 0.12):
            return {
                'recommendation': 'CONSIDER',
                'confidence': 0.7,
                'reasoning': 'Reasonable opportunity requiring careful evaluation and strong bid strategy',
                'next_actions': [
                    'Conduct detailed go/no-go analysis',
                    'Assess team availability and capacity',
                    'Review similar past bids for insights',
                    'Evaluate partnership opportunities'
                ]
            }
        
        elif (relevance_score >= 35 and overall_filter_score >= 0.4 and 
              competition_level <= 9.0 and bid_probability >= 0.08):
            return {
                'recommendation': 'MONITOR',
                'confidence': 0.6,
                'reasoning': 'Marginal opportunity - monitor for changes or similar future opportunities',
                'next_actions': [
                    'Monitor for clarifications or amendments',
                    'Track similar opportunities from this organization',
                    'Consider capability development needs',
                    'Evaluate as learning opportunity'
                ]
            }
        
        else:
            return {
                'recommendation': 'AVOID',
                'confidence': 0.8,
                'reasoning': 'Low probability of success, poor strategic fit, or excessive competition',
                'next_actions': [
                    'Monitor for similar future opportunities',
                    'Analyze why opportunity was unsuitable',
                    'Consider capability development needs',
                    'Focus resources on better opportunities'
                ]
            }
        
    def generate_bid_strategy_recommendation(self, enhanced_result, tender_data: Dict, 
                                           competition_analysis: Dict) -> str:
        """Generate strategic bidding approach recommendation"""
        competition_level = competition_analysis['competition_level']
        specialization = competition_analysis['assessment_factors'].get('specialization', {})
        value = tender_data.get('value_high', 0)
        
        if competition_level <= 4:
            if specialization.get('level') == 'highly_specialized':
                return 'TECHNICAL_EXCELLENCE - Focus on deep technical expertise and innovation'
            else:
                return 'COMPETITIVE_PRICING - Balance quality with competitive pricing'
        
        elif competition_level <= 7:
            if value >= 1000000:
                return 'PARTNERSHIP_STRATEGY - Consider teaming with complementary organizations'
            else:
                return 'DIFFERENTIATION - Emphasize unique value proposition and past performance'
        
        else:  # High competition
            return 'NICHE_POSITIONING - Focus on specific strengths and avoid direct price competition'
    
    def create_filtered_result(self, enhanced_result, tender_data: Dict, 
                             filter_results: Dict, competition_analysis: Dict,
                             overall_filter_score: float, passes_filters: bool) -> FilteredOpportunityResult:
        """Create comprehensive filtered opportunity result"""
        
        # Analyze risk and success factors
        risk_factors, success_factors = self.analyze_risk_success_factors(
            enhanced_result, filter_results, competition_analysis
        )
        
        # Estimate resource requirements
        resource_requirements = self.estimate_resource_requirements(
            enhanced_result, tender_data, filter_results
        )
        
        # Determine strategic value
        strategic_value = self.determine_strategic_value(
            enhanced_result, tender_data, filter_results
        )
        
        # Generate final recommendation
        final_recommendation = self.generate_final_recommendation(
            enhanced_result, filter_results, competition_analysis, overall_filter_score
        )
        
        # Generate bid strategy recommendation
        bid_strategy = self.generate_bid_strategy_recommendation(
            enhanced_result, tender_data, competition_analysis
        )
        
        # Create filter recommendation
        if passes_filters:
            filter_recommendation = f"PASSES ALL FILTERS - Overall score: {overall_filter_score:.2f}"
        else:
            failed_filters = [cat for cat, result in filter_results.items() if not result.get('passes', True)]
            filter_recommendation = f"FAILS FILTERS: {', '.join(failed_filters)}"
        
        return FilteredOpportunityResult(
            notice_identifier=enhanced_result.notice_identifier,
            enhanced_result=enhanced_result,
            tender_data=tender_data,
            filter_results=filter_results,
            overall_filter_score=overall_filter_score,
            filter_passes=passes_filters,
            filter_recommendation=filter_recommendation,
            competition_assessment=competition_analysis,
            bid_probability=competition_analysis['bid_probability'],
            recommended_bid_strategy=bid_strategy,
            risk_factors=risk_factors,
            success_factors=success_factors,
            resource_requirements=resource_requirements,
            strategic_value=strategic_value,
            final_recommendation=final_recommendation['recommendation'],
            confidence_level=final_recommendation['confidence'],
            next_actions=final_recommendation['next_actions']
        )
    
    def filter_opportunities(self, enhanced_results: List, profile: str = 'balanced') -> List[FilteredOpportunityResult]:
        """Apply comprehensive filtering to enhanced scoring results"""
        # Apply profile configuration
        profile_config = self.filter_config.apply_profile(profile)
        self.initialize_filters(profile_config)
        
        filtered_results = []
        
        logger.info(f"Filtering {len(enhanced_results)} opportunities with '{profile}' profile")
        
        for enhanced_result in enhanced_results:
            try:
                # Load tender data (in real implementation, this would query the database)
                tender_data = self.load_tender_data(enhanced_result.notice_identifier)
                
                # Apply all filters
                filter_results = self.apply_all_filters(enhanced_result, tender_data)
                
                # Competition assessment
                competition_analysis = self.competition_assessment.assess_competition_level(
                    tender_data, enhanced_result
                )
                
                # Calculate overall filter score
                overall_score = self.calculate_overall_filter_score(filter_results)
                
                # Check if passes profile criteria
                passes_filters = self.evaluate_against_profile(
                    enhanced_result, filter_results, competition_analysis, profile_config
                )
                
                # Create comprehensive filtered result
                filtered_result = self.create_filtered_result(
                    enhanced_result, tender_data, filter_results,
                    competition_analysis, overall_score, passes_filters
                )
                
                filtered_results.append(filtered_result)
                
            except Exception as e:
                logger.error(f"Filtering failed for {enhanced_result.notice_identifier}: {e}")
                continue
        
        # Sort by combined relevance and filter score
        return self.rank_filtered_opportunities(filtered_results)
    
    def load_tender_data(self, notice_identifier: str) -> Dict:
        """Load tender data from database (placeholder for real implementation)"""
        # In real implementation, this would query the database
        # For now, return mock data
        return {
            'notice_identifier': notice_identifier,
            'title': 'Mock Tender Title',
            'description': 'Mock tender description for testing',
            'organisation_name': 'Mock Organization',
            'value_high': 500000,
            'suitable_for_sme': 'yes',
            'closing_date': (datetime.now() + timedelta(days=45)).isoformat()
        }
    
    def rank_filtered_opportunities(self, filtered_results: List[FilteredOpportunityResult]) -> List[FilteredOpportunityResult]:
        """Rank filtered opportunities by combined scoring"""
        def ranking_score(result):
            # Combined ranking: relevance score (70%) + filter score (20%) + bid probability (10%)
            relevance_component = result.enhanced_result.final_relevance_score * 0.7
            filter_component = result.overall_filter_score * 100 * 0.2
            probability_component = result.bid_probability * 100 * 0.1
            
            return relevance_component + filter_component + probability_component
        
        return sorted(filtered_results, key=ranking_score, reverse=True)

def main():
    """Test the filtering components"""
    # Test data
    test_tender = {
        'notice_identifier': 'test_filter_001',
        'title': 'NHS Digital Health Platform Development',
        'description': 'Comprehensive digital transformation of healthcare systems with cloud migration, API development, and modern user interfaces. Remote delivery supported.',
        'organisation_name': 'NHS Digital',
        'value_high': 750000,
        'status': 'open',
        'suitable_for_sme': 'yes',
        'cpv_codes': '72000000',
        'closing_date': (datetime.now() + timedelta(days=35)).isoformat()
    }
    
    # Mock enhanced result
    class MockEnhancedResult:
        def __init__(self):
            self.final_relevance_score = 78.5
            self.technical_terms = ['api', 'cloud', 'digital', 'healthcare']
    
    enhanced_result = MockEnhancedResult()
    
    # Test filter components
    print("=== Advanced Filtering Engine Test ===")
    
    # Value filters
    config = {'min_value': 50000, 'max_value': 5000000, 'sweet_spot_min': 100000, 'sweet_spot_max': 2000000}
    value_filter = ValueFilters(config)
    value_result = value_filter.evaluate_value_fit(test_tender)
    print(f"Value Filter: {value_result['passes']} - {value_result['assessment']}")
    
    # Timeline filters
    timeline_config = {'min_lead_time': 14, 'optimal_window_start': 30, 'optimal_window_end': 90}
    timeline_filter = TimelineFilters(timeline_config)
    timeline_result = timeline_filter.evaluate_timeline_fit(test_tender)
    print(f"Timeline Filter: {timeline_result['passes']} - {timeline_result['assessment']}")
    
    # Capability filters
    capability_config = {'required_skills': ['digital_transformation'], 'max_complexity_threshold': 8}
    capability_filter = CapabilityFilters(capability_config)
    capability_result = capability_filter.evaluate_capability_match(test_tender, enhanced_result)
    print(f"Capability Filter: {capability_result['passes']} - {capability_result['assessment']}")
    
    # Geographic filters
    geographic_config = {'preferred_regions': ['England'], 'remote_friendly': True}
    geographic_filter = GeographicFilters(geographic_config)
    geographic_result = geographic_filter.evaluate_geographic_fit(test_tender)
    print(f"Geographic Filter: {geographic_result['passes']} - {geographic_result['assessment']}")
    
    # Competition assessment
    competition_assessor = CompetitionAssessment()
    competition_result = competition_assessor.assess_competition_level(test_tender, enhanced_result)
    print(f"Competition Assessment: Level {competition_result['competition_level']:.1f} - {competition_result['recommendation']}")
    print(f"Bid Probability: {competition_result['bid_probability']:.1%} ({competition_result['probability_band']})")

if __name__ == "__main__":
    main()