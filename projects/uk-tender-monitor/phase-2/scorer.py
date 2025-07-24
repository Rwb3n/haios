#!/usr/bin/env python3
"""
UK Tender Monitor - Relevance Scoring System (Phase 2 Step 2)
Enhanced business intelligence scoring with multiplier factors and metadata analysis

Core Features:
- Advanced composite scoring algorithm (0-100 scale)
- Metadata intelligence (CPV codes, organization analysis)
- Business alignment assessment
- Dynamic multiplier factors (urgency, value, department)
- Priority classification and recommendations
"""

import json
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, NamedTuple
import logging

import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EnhancedClassificationResult(NamedTuple):
    """Enhanced result structure with business intelligence"""
    # Original classification fields
    notice_identifier: str
    keyword_score: float
    context_score: float
    ml_confidence: float
    technical_terms: List[str]
    transformation_signals: List[str]
    
    # Enhanced scoring fields
    metadata_score: float           # CPV, org, value analysis (0-15)
    business_alignment_score: float # Strategic fit assessment (0-7.5)
    urgency_multiplier: float       # Timeline-based multiplier (0.8-1.5)
    value_multiplier: float         # Contract value multiplier (0.5-2.0)
    department_multiplier: float    # Organization preference (0.8-1.3)
    competition_multiplier: float   # Competition level assessment (0.7-1.2)
    
    # Final scoring results
    base_composite_score: float     # Pre-multiplier score (0-70)
    final_relevance_score: float    # Ultimate score (0-100)
    score_breakdown: Dict           # Detailed scoring explanation
    recommendation: str             # Action recommendation
    priority_level: str             # HIGH/MEDIUM/LOW priority
    explanation: str                # Human-readable reasoning

class MetadataAnalyzer:
    """Advanced metadata processing and intelligence"""
    
    def __init__(self):
        # CPV code intelligence database
        self.cpv_intelligence = {
            # IT Services (High Relevance)
            '72000000': {'score': 5, 'description': 'IT services: software development, consultancy'},
            '72200000': {'score': 4, 'description': 'Software programming and consultancy'},
            '72300000': {'score': 4, 'description': 'Data processing services'},
            '72400000': {'score': 3, 'description': 'Internet services'},
            '72500000': {'score': 3, 'description': 'Computer-related services'},
            '48000000': {'score': 3, 'description': 'Software package and information systems'},
            '72600000': {'score': 4, 'description': 'Computer support and consultancy services'},
            '79000000': {'score': 2, 'description': 'Business services (potentially digital)'},
            
            # Medium Relevance
            '51000000': {'score': 1, 'description': 'Installation services (potentially IT)'},
            '73000000': {'score': 2, 'description': 'Research and development services'},
            '80000000': {'score': 1, 'description': 'Education and training services'},
            
            # Low Relevance (explicitly tracked to avoid scoring)
            '45000000': {'score': 0, 'description': 'Construction work'},
            '03000000': {'score': 0, 'description': 'Agricultural products'},
            '15000000': {'score': 0, 'description': 'Food, beverages, tobacco'},
        }
        
        # Organization intelligence categories
        self.org_categories = {
            'high_tech': {
                'keywords': ['digital', 'nhs digital', 'cabinet office digital service', 'hmrc digital', 'dvla digital'],
                'score': 4,
                'description': 'Technology-focused government departments'
            },
            'government_core': {
                'keywords': ['cabinet office', 'hmrc', 'dvla', 'mod', 'home office', 'dfe'],
                'score': 3,
                'description': 'Core government departments'
            },
            'health_sector': {
                'keywords': ['nhs', 'health', 'clinical commissioning', 'foundation trust'],
                'score': 3,
                'description': 'Healthcare organizations (high digitization potential)'
            },
            'education': {
                'keywords': ['university', 'college', 'school', 'education authority'],
                'score': 2,
                'description': 'Educational institutions'
            },
            'local_government': {
                'keywords': ['council', 'borough', 'city council', 'county council'],
                'score': 2,
                'description': 'Local government bodies'
            },
            'generic': {
                'keywords': [],
                'score': 1,
                'description': 'Generic organizations'
            }
        }
        
        logger.info("Metadata analyzer initialized with CPV and organization intelligence")
    
    def analyze_metadata(self, tender_data: Dict) -> Tuple[float, Dict]:
        """
        Comprehensive metadata analysis
        Returns: (total_score, breakdown_dict)
        """
        breakdown = {}
        
        # CPV code analysis (0-5 points)
        cpv_score, cpv_breakdown = self.analyze_cpv_codes(tender_data.get('cpv_codes', ''))
        breakdown['cpv_analysis'] = cpv_breakdown
        
        # Organization intelligence (0-4 points)
        org_score, org_breakdown = self.analyze_organization_type(tender_data.get('organisation_name', ''))
        breakdown['organization_analysis'] = org_breakdown
        
        # Value bracket assessment (0-3 points)
        value_score, value_breakdown = self.analyze_value_bracket(tender_data.get('value_high'))
        breakdown['value_analysis'] = value_breakdown
        
        # Timeline favorability (0-3 points)
        timeline_score, timeline_breakdown = self.analyze_timeline(
            tender_data.get('closing_date'), 
            tender_data.get('start_date')
        )
        breakdown['timeline_analysis'] = timeline_breakdown
        
        total_score = min(cpv_score + org_score + value_score + timeline_score, 15)
        breakdown['total_metadata_score'] = total_score
        
        return total_score, breakdown
    
    def analyze_cpv_codes(self, cpv_codes: str) -> Tuple[float, Dict]:
        """Analyze CPV codes for digital transformation relevance"""
        if not cpv_codes:
            return 0, {'status': 'no_cpv_codes', 'score': 0}
        
        max_score = 0
        matched_cpv = None
        
        for cpv in cpv_codes.split(','):
            cpv_clean = cpv.strip()[:8]  # First 8 digits
            if cpv_clean in self.cpv_intelligence:
                cpv_data = self.cpv_intelligence[cpv_clean]
                if cpv_data['score'] > max_score:
                    max_score = cpv_data['score']
                    matched_cpv = cpv_data
        
        breakdown = {
            'matched_cpv': matched_cpv,
            'score': max_score,
            'status': 'relevant_cpv_found' if max_score > 0 else 'no_relevant_cpv'
        }
        
        return max_score, breakdown
    
    def analyze_organization_type(self, org_name: str) -> Tuple[float, Dict]:
        """Analyze organization for digital transformation potential"""
        if not org_name:
            return 1, {'category': 'unknown', 'score': 1}
        
        org_lower = org_name.lower()
        
        for category, data in self.org_categories.items():
            if category == 'generic':
                continue
                
            for keyword in data['keywords']:
                if keyword in org_lower:
                    return data['score'], {
                        'category': category,
                        'matched_keyword': keyword,
                        'score': data['score'],
                        'description': data['description']
                    }
        
        # Default to generic category
        return 1, {'category': 'generic', 'score': 1, 'description': 'Generic organization'}
    
    def analyze_value_bracket(self, value_high) -> Tuple[float, Dict]:
        """Analyze contract value for strategic importance"""
        if not value_high or value_high == 0:
            return 1, {'bracket': 'unknown', 'score': 1, 'value': 0}
        
        value = float(value_high)
        
        if value < 25000:
            return 0, {'bracket': 'too_small', 'score': 0, 'value': value}
        elif 25000 <= value < 100000:
            return 1, {'bracket': 'small', 'score': 1, 'value': value}
        elif 100000 <= value < 500000:
            return 2, {'bracket': 'medium', 'score': 2, 'value': value}
        elif 500000 <= value < 2000000:
            return 3, {'bracket': 'large', 'score': 3, 'value': value}
        elif value >= 2000000:
            return 3, {'bracket': 'very_large', 'score': 3, 'value': value}
        
        return 1, {'bracket': 'unknown', 'score': 1, 'value': value}
    
    def analyze_timeline(self, closing_date, start_date) -> Tuple[float, Dict]:
        """Analyze timeline for opportunity assessment"""
        if not closing_date:
            return 1, {'status': 'no_closing_date', 'score': 1}
        
        try:
            closing_dt = datetime.fromisoformat(closing_date.replace('Z', '+00:00'))
            days_remaining = (closing_dt - datetime.now()).days
            
            if days_remaining < 0:
                return 0, {'status': 'expired', 'days_remaining': days_remaining, 'score': 0}
            elif days_remaining <= 7:
                return 1, {'status': 'very_urgent', 'days_remaining': days_remaining, 'score': 1}
            elif days_remaining <= 30:
                return 2, {'status': 'urgent', 'days_remaining': days_remaining, 'score': 2}
            elif days_remaining <= 90:
                return 3, {'status': 'good_timing', 'days_remaining': days_remaining, 'score': 3}
            elif days_remaining <= 180:
                return 2, {'status': 'future', 'days_remaining': days_remaining, 'score': 2}
            else:
                return 1, {'status': 'distant', 'days_remaining': days_remaining, 'score': 1}
                
        except (ValueError, TypeError) as e:
            logger.warning(f"Timeline analysis failed: {e}")
            return 1, {'status': 'invalid_date', 'score': 1}

class BusinessAlignmentAnalyzer:
    """Strategic business alignment assessment"""
    
    def __init__(self):
        # Capability requirement categories
        self.capability_requirements = {
            'high_complexity': {
                'terms': ['digital transformation', 'enterprise architecture', 'system integration', 'legacy modernization'],
                'score': 3,
                'description': 'High-complexity digital transformation projects'
            },
            'medium_complexity': {
                'terms': ['software development', 'api development', 'cloud migration', 'database design'],
                'score': 2,
                'description': 'Medium-complexity technical implementations'
            },
            'basic_complexity': {
                'terms': ['technical support', 'maintenance', 'configuration', 'installation'],
                'score': 1,
                'description': 'Basic technical services'
            }
        }
        
        # Technology stack alignment
        self.tech_stack_alignment = {
            'preferred_technologies': ['python', 'javascript', 'react', 'node.js', 'aws', 'azure', 'docker', 'kubernetes'],
            'supported_technologies': ['java', 'php', 'angular', 'vue', 'mysql', 'postgresql', 'mongodb'],
            'legacy_technologies': ['cobol', 'fortran', 'vb6', 'asp.net', 'oracle', 'mainframe']
        }
        
        logger.info("Business alignment analyzer initialized")
    
    def assess_business_alignment(self, tender_data: Dict) -> Tuple[float, Dict]:
        """
        Comprehensive business alignment assessment
        Returns: (total_score, breakdown_dict)
        """
        text = f"{tender_data.get('title', '')} {tender_data.get('description', '')}".lower()
        breakdown = {}
        
        # Capability requirements assessment (0-3 points)
        capability_score, capability_breakdown = self.assess_capability_requirements(text)
        breakdown['capability_assessment'] = capability_breakdown
        
        # Technology stack alignment (0-2 points)
        tech_score, tech_breakdown = self.assess_tech_stack_alignment(text)
        breakdown['technology_alignment'] = tech_breakdown
        
        # Delivery model compatibility (0-1.5 points)
        delivery_score, delivery_breakdown = self.assess_delivery_model(text)
        breakdown['delivery_model'] = delivery_breakdown
        
        # Strategic priority alignment (0-1 point)
        strategic_score, strategic_breakdown = self.assess_strategic_priority(tender_data)
        breakdown['strategic_priority'] = strategic_breakdown
        
        total_score = min(capability_score + tech_score + delivery_score + strategic_score, 7.5)
        breakdown['total_alignment_score'] = total_score
        
        return total_score, breakdown
    
    def assess_capability_requirements(self, text: str) -> Tuple[float, Dict]:
        """Assess capability requirements match"""
        for complexity, data in self.capability_requirements.items():
            for term in data['terms']:
                if term in text:
                    return data['score'], {
                        'complexity_level': complexity,
                        'matched_term': term,
                        'score': data['score'],
                        'description': data['description']
                    }
        
        return 0, {'complexity_level': 'none_detected', 'score': 0}
    
    def assess_tech_stack_alignment(self, text: str) -> Tuple[float, Dict]:
        """Assess technology stack alignment"""
        preferred_count = sum(1 for tech in self.tech_stack_alignment['preferred_technologies'] if tech in text)
        supported_count = sum(1 for tech in self.tech_stack_alignment['supported_technologies'] if tech in text)
        legacy_count = sum(1 for tech in self.tech_stack_alignment['legacy_technologies'] if tech in text)
        
        if preferred_count >= 2:
            score = 2
            level = 'high_alignment'
        elif preferred_count >= 1 or supported_count >= 2:
            score = 1.5
            level = 'medium_alignment'
        elif supported_count >= 1:
            score = 1
            level = 'basic_alignment'
        elif legacy_count >= 1:
            score = 0.5
            level = 'legacy_concerns'
        else:
            score = 0
            level = 'no_tech_detected'
        
        return score, {
            'alignment_level': level,
            'preferred_count': preferred_count,
            'supported_count': supported_count,
            'legacy_count': legacy_count,
            'score': score
        }
    
    def assess_delivery_model(self, text: str) -> Tuple[float, Dict]:
        """Assess delivery model compatibility"""
        remote_terms = ['remote', 'distributed', 'virtual', 'online delivery']
        onsite_terms = ['on-site', 'on site', 'premises', 'location specific']
        hybrid_terms = ['hybrid', 'flexible', 'blended']
        
        remote_match = any(term in text for term in remote_terms)
        onsite_match = any(term in text for term in onsite_terms)
        hybrid_match = any(term in text for term in hybrid_terms)
        
        if remote_match or hybrid_match:
            return 1.5, {'model': 'remote_friendly', 'score': 1.5}
        elif not onsite_match:
            return 1.0, {'model': 'flexible', 'score': 1.0}
        else:
            return 0.5, {'model': 'onsite_required', 'score': 0.5}
    
    def assess_strategic_priority(self, tender_data: Dict) -> Tuple[float, Dict]:
        """Assess strategic priority alignment"""
        # High-priority strategic terms
        strategic_terms = [
            'digital transformation', 'modernization', 'innovation', 'efficiency',
            'citizen services', 'public service improvement', 'cost reduction'
        ]
        
        text = f"{tender_data.get('title', '')} {tender_data.get('description', '')}".lower()
        matched_terms = [term for term in strategic_terms if term in text]
        
        if len(matched_terms) >= 2:
            return 1.0, {'priority_level': 'high', 'matched_terms': matched_terms, 'score': 1.0}
        elif len(matched_terms) >= 1:
            return 0.7, {'priority_level': 'medium', 'matched_terms': matched_terms, 'score': 0.7}
        else:
            return 0.3, {'priority_level': 'low', 'matched_terms': [], 'score': 0.3}

class MultiplierCalculator:
    """Dynamic multiplier factor calculations"""
    
    def __init__(self):
        logger.info("Multiplier calculator initialized")
    
    def calculate_urgency_multiplier(self, tender_data: Dict) -> Tuple[float, Dict]:
        """Calculate urgency-based multiplier (0.8x - 1.5x)"""
        closing_date = tender_data.get('closing_date')
        
        if not closing_date:
            return 1.0, {'status': 'no_date', 'multiplier': 1.0}
        
        try:
            closing_dt = datetime.fromisoformat(closing_date.replace('Z', '+00:00'))
            days_remaining = (closing_dt - datetime.now()).days
            
            if days_remaining < 0:
                return 0.5, {'status': 'expired', 'days_remaining': days_remaining, 'multiplier': 0.5}
            elif days_remaining <= 14:
                return 1.5, {'status': 'urgent', 'days_remaining': days_remaining, 'multiplier': 1.5}
            elif days_remaining <= 30:
                return 1.3, {'status': 'soon', 'days_remaining': days_remaining, 'multiplier': 1.3}
            elif days_remaining <= 60:
                return 1.1, {'status': 'good_timing', 'days_remaining': days_remaining, 'multiplier': 1.1}
            elif days_remaining <= 180:
                return 1.0, {'status': 'future', 'days_remaining': days_remaining, 'multiplier': 1.0}
            else:
                return 0.8, {'status': 'distant', 'days_remaining': days_remaining, 'multiplier': 0.8}
                
        except (ValueError, TypeError) as e:
            logger.warning(f"Urgency calculation failed: {e}")
            return 1.0, {'status': 'invalid_date', 'multiplier': 1.0}
    
    def calculate_value_multiplier(self, tender_data: Dict) -> Tuple[float, Dict]:
        """Calculate value-based multiplier (0.5x - 2.0x)"""
        value = tender_data.get('value_high')
        
        if not value or value == 0:
            return 0.8, {'status': 'no_value', 'multiplier': 0.8}
        
        value = float(value)
        
        if value < 50000:
            return 0.5, {'bracket': 'too_small', 'value': value, 'multiplier': 0.5}
        elif 50000 <= value < 150000:
            return 1.0, {'bracket': 'small', 'value': value, 'multiplier': 1.0}
        elif 150000 <= value < 500000:
            return 1.4, {'bracket': 'sweet_spot', 'value': value, 'multiplier': 1.4}
        elif 500000 <= value < 2000000:
            return 1.8, {'bracket': 'high_value', 'value': value, 'multiplier': 1.8}
        elif 2000000 <= value < 10000000:
            return 2.0, {'bracket': 'very_high_value', 'value': value, 'multiplier': 2.0}
        else:
            return 1.2, {'bracket': 'extremely_high', 'value': value, 'multiplier': 1.2}
    
    def calculate_department_multiplier(self, tender_data: Dict) -> Tuple[float, Dict]:
        """Calculate department preference multiplier (0.8x - 1.3x)"""
        org_name = tender_data.get('organisation_name', '').lower()
        
        # High-preference organizations (1.3x)
        high_pref = ['nhs digital', 'cabinet office', 'hmrc', 'dvla', 'mod', 'home office']
        for org in high_pref:
            if org in org_name:
                return 1.3, {'preference': 'high', 'matched_org': org, 'multiplier': 1.3}
        
        # Medium-preference organizations (1.1x)
        med_pref = ['nhs', 'university', 'council', 'government', 'public health']
        for org in med_pref:
            if org in org_name:
                return 1.1, {'preference': 'medium', 'matched_org': org, 'multiplier': 1.1}
        
        # Standard organizations (1.0x)
        return 1.0, {'preference': 'standard', 'multiplier': 1.0}
    
    def calculate_competition_multiplier(self, tender_data: Dict) -> Tuple[float, Dict]:
        """Calculate competition level multiplier (0.7x - 1.2x)"""
        # Basic competition assessment based on tender characteristics
        value = tender_data.get('value_high', 0)
        sme_suitable = tender_data.get('suitable_for_sme', '').lower()
        
        # High competition indicators
        if value > 5000000:  # Very high value attracts many bidders
            return 0.7, {'level': 'very_high', 'reason': 'high_value_contract', 'multiplier': 0.7}
        
        # Medium-high competition
        if value > 1000000 and sme_suitable in ['no', 'false']:
            return 0.8, {'level': 'high', 'reason': 'large_corp_only', 'multiplier': 0.8}
        
        # Medium competition
        if 500000 <= value <= 1000000:
            return 0.9, {'level': 'medium', 'reason': 'medium_value', 'multiplier': 0.9}
        
        # Lower competition (SME-friendly)
        if sme_suitable in ['yes', 'true'] and value < 500000:
            return 1.2, {'level': 'low', 'reason': 'sme_friendly', 'multiplier': 1.2}
        
        # Standard competition
        return 1.0, {'level': 'standard', 'multiplier': 1.0}

class RelevanceScorer:
    """Main relevance scoring engine with business intelligence"""
    
    def __init__(self, config_path: Optional[str] = None):
        self.config = self.load_scoring_config(config_path)
        self.metadata_analyzer = MetadataAnalyzer()
        self.business_analyzer = BusinessAlignmentAnalyzer()
        self.multiplier_calculator = MultiplierCalculator()
        
        # Scoring weights (should total to 1.0 for base score)
        self.base_weights = {
            'keyword_score': 0.30,      # 30% - Direct keyword matches
            'context_score': 0.25,      # 25% - Technical context analysis
            'ml_confidence': 0.25,      # 25% - Machine learning prediction
            'metadata_score': 0.15,     # 15% - CPV, org, value analysis
            'business_alignment': 0.05  # 5% - Strategic fit assessment
        }
        
        logger.info("Relevance scorer initialized with enhanced business intelligence")
    
    def load_scoring_config(self, config_path: Optional[str]) -> Dict:
        """Load scoring configuration"""
        default_config = {
            'priority_thresholds': {
                'high': 70,
                'medium': 40,
                'low': 20
            },
            'recommendation_templates': {
                'immediate_action': "IMMEDIATE ACTION: High-priority opportunity closing soon",
                'high_interest': "HIGH INTEREST: Strong digital transformation opportunity",
                'worth_reviewing': "WORTH REVIEWING: Relevant opportunity for consideration",
                'low_priority': "LOW PRIORITY: Limited relevance or poor timing"
            }
        }
        
        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def score_classified_tender(self, tender_data: Dict, classification_result) -> EnhancedClassificationResult:
        """
        Generate enhanced relevance score with business intelligence
        """
        # Extract basic classification components
        keyword_score = classification_result.keyword_score
        context_score = classification_result.context_score
        ml_confidence = classification_result.ml_confidence
        
        # Enhanced metadata analysis
        metadata_score, metadata_breakdown = self.metadata_analyzer.analyze_metadata(tender_data)
        
        # Business alignment assessment
        business_score, business_breakdown = self.business_analyzer.assess_business_alignment(tender_data)
        
        # Calculate base composite score (0-70 points before multipliers)
        base_score = (
            keyword_score * self.base_weights['keyword_score'] +
            context_score * self.base_weights['context_score'] +
            (ml_confidence * 100) * self.base_weights['ml_confidence'] +
            metadata_score * self.base_weights['metadata_score'] +
            business_score * self.base_weights['business_alignment']
        )
        
        # Calculate multiplier factors
        urgency_mult, urgency_breakdown = self.multiplier_calculator.calculate_urgency_multiplier(tender_data)
        value_mult, value_breakdown = self.multiplier_calculator.calculate_value_multiplier(tender_data)
        dept_mult, dept_breakdown = self.multiplier_calculator.calculate_department_multiplier(tender_data)
        comp_mult, comp_breakdown = self.multiplier_calculator.calculate_competition_multiplier(tender_data)
        
        # Apply multipliers to get final score (cap at 100)
        final_score = min(base_score * urgency_mult * value_mult * dept_mult * comp_mult, 100)
        
        # Generate priority level and recommendation
        priority_level = self.determine_priority_level(final_score, urgency_mult)
        recommendation = self.generate_recommendation(final_score, urgency_mult, value_mult, tender_data)
        
        # Create comprehensive score breakdown
        score_breakdown = {
            'base_components': {
                'keyword_score': keyword_score,
                'context_score': context_score,
                'ml_confidence': ml_confidence,
                'metadata_score': metadata_score,
                'business_alignment_score': business_score
            },
            'multipliers': {
                'urgency': urgency_breakdown,
                'value': value_breakdown,
                'department': dept_breakdown,
                'competition': comp_breakdown
            },
            'analysis_details': {
                'metadata_analysis': metadata_breakdown,
                'business_analysis': business_breakdown
            },
            'scoring_summary': {
                'base_score': base_score,
                'final_score': final_score,
                'total_multiplier': urgency_mult * value_mult * dept_mult * comp_mult
            }
        }
        
        # Generate enhanced explanation
        explanation = self.generate_enhanced_explanation(
            classification_result, metadata_breakdown, business_breakdown,
            urgency_mult, value_mult, dept_mult, comp_mult
        )
        
        return EnhancedClassificationResult(
            notice_identifier=classification_result.notice_identifier,
            keyword_score=keyword_score,
            context_score=context_score,
            ml_confidence=ml_confidence,
            technical_terms=classification_result.technical_terms,
            transformation_signals=classification_result.transformation_signals,
            metadata_score=metadata_score,
            business_alignment_score=business_score,
            urgency_multiplier=urgency_mult,
            value_multiplier=value_mult,
            department_multiplier=dept_mult,
            competition_multiplier=comp_mult,
            base_composite_score=base_score,
            final_relevance_score=final_score,
            score_breakdown=score_breakdown,
            recommendation=recommendation,
            priority_level=priority_level,
            explanation=explanation
        )
    
    def determine_priority_level(self, score: float, urgency_mult: float) -> str:
        """Determine priority level based on score and urgency"""
        if score >= self.config['priority_thresholds']['high']:
            return 'HIGH'
        elif score >= self.config['priority_thresholds']['medium']:
            return 'MEDIUM' if urgency_mult <= 1.2 else 'HIGH'  # Urgency can elevate priority
        elif score >= self.config['priority_thresholds']['low']:
            return 'LOW' if urgency_mult <= 1.0 else 'MEDIUM'   # Urgency can elevate priority
        else:
            return 'LOW'
    
    def generate_recommendation(self, score: float, urgency_mult: float, value_mult: float, tender_data: Dict) -> str:
        """Generate action recommendation"""
        if score >= 80 and urgency_mult >= 1.3:
            return self.config['recommendation_templates']['immediate_action']
        elif score >= 60:
            return self.config['recommendation_templates']['high_interest']
        elif score >= 30:
            return self.config['recommendation_templates']['worth_reviewing']
        else:
            return self.config['recommendation_templates']['low_priority']
    
    def generate_enhanced_explanation(self, classification_result, metadata_breakdown, 
                                    business_breakdown, urgency_mult, value_mult, 
                                    dept_mult, comp_mult) -> str:
        """Generate comprehensive human-readable explanation"""
        explanation_parts = []
        
        # Classification components
        if classification_result.technical_terms:
            explanation_parts.append(f"Tech terms: {', '.join(classification_result.technical_terms[:3])}")
        
        # Metadata insights
        if metadata_breakdown.get('cpv_analysis', {}).get('matched_cpv'):
            cpv_desc = metadata_breakdown['cpv_analysis']['matched_cpv']['description']
            explanation_parts.append(f"CPV: {cpv_desc}")
        
        # Significant multipliers
        multiplier_explanations = []
        if urgency_mult >= 1.2:
            multiplier_explanations.append(f"Urgent timing ({urgency_mult:.1f}x)")
        if value_mult >= 1.5:
            multiplier_explanations.append(f"High value ({value_mult:.1f}x)")
        if dept_mult >= 1.2:
            multiplier_explanations.append(f"Preferred dept ({dept_mult:.1f}x)")
        
        if multiplier_explanations:
            explanation_parts.append(" | ".join(multiplier_explanations))
        
        return " | ".join(explanation_parts) if explanation_parts else "Limited transformation signals detected"

def main():
    """Test the enhanced scoring system"""
    # Test data
    test_tender = {
        'notice_identifier': 'test_enhanced_001',
        'title': 'Digital Health Platform Development',
        'description': 'Comprehensive digital transformation of healthcare systems with cloud migration, API development, and modern user interfaces using React and Node.js',
        'organisation_name': 'NHS Digital',
        'value_high': 750000,
        'status': 'open',
        'suitable_for_sme': 'yes',
        'cpv_codes': '72000000',
        'closing_date': (datetime.now() + timedelta(days=21)).isoformat()
    }
    
    # Mock classification result
    from classifier import ClassificationResult
    classification_result = ClassificationResult(
        notice_identifier='test_enhanced_001',
        keyword_score=15.0,
        context_score=8.5,
        ml_confidence=0.85,
        composite_score=25.0,  # Will be recalculated
        explanation='Mock explanation',
        technical_terms=['api', 'react', 'cloud'],
        transformation_signals=['digital transformation']
    )
    
    # Test enhanced scoring
    scorer = RelevanceScorer()
    enhanced_result = scorer.score_classified_tender(test_tender, classification_result)
    
    print("=== Enhanced Relevance Scoring Test ===")
    print(f"Notice ID: {enhanced_result.notice_identifier}")
    print(f"Final Score: {enhanced_result.final_relevance_score:.1f}")
    print(f"Priority: {enhanced_result.priority_level}")
    print(f"Recommendation: {enhanced_result.recommendation}")
    print(f"Explanation: {enhanced_result.explanation}")
    print(f"Multipliers: Urgency={enhanced_result.urgency_multiplier:.2f}, Value={enhanced_result.value_multiplier:.2f}")

if __name__ == "__main__":
    main()