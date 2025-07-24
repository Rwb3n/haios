#!/usr/bin/env python3
"""
UK Tender Monitor - REST API Layer (Phase 2 Step 6)
Comprehensive API endpoints for opportunity discovery, classification, and expert validation

Core Features:
- Opportunity discovery with advanced filtering and scoring
- Real-time tender classification with detailed explanations
- Expert validation workflows with agreement analysis
- Performance monitoring and system health metrics
- Integration with complete Phase 2 classification pipeline
"""

from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any, Union
from datetime import datetime, timedelta
import json
import logging
from pathlib import Path
import sqlite3
from contextlib import contextmanager

# Import Phase 2 components
from database_extensions import EnhancedDataAccess, DatabaseSchemaManager
from system_integration import SystemIntegrationManager, IntegratedTenderPipeline
from classifier import TenderClassifier
from scorer import RelevanceScorer
from filter import AdvancedOpportunityFilter
from trainer import ContinuousLearningSystem

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="UK Tender Monitor API",
    description="Production API for UK government digital transformation opportunity discovery",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global components initialization
data_access = None
integration_manager = None
integrated_pipeline = None

def initialize_system():
    """Initialize API system components"""
    global data_access, integration_manager, integrated_pipeline
    
    try:
        logger.info("Initializing UK Tender Monitor API system...")
        
        # Initialize database access
        data_access = EnhancedDataAccess("../data/tenders.db")
        
        # Initialize system integration
        integration_manager = SystemIntegrationManager(
            data_dir="../data", 
            enable_persistence=True
        )
        
        # Create integrated pipeline
        integrated_pipeline = integration_manager.create_integrated_pipeline()
        
        logger.info("API system initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"API system initialization failed: {e}")
        return False

# Initialize system on startup
@app.on_event("startup")
async def startup_event():
    success = initialize_system()
    if not success:
        logger.error("Critical: API system failed to initialize")

# ==================== REQUEST/RESPONSE MODELS ====================

class TenderBasic(BaseModel):
    """Basic tender information model"""
    notice_identifier: str
    title: str
    organisation_name: str
    value_high: Optional[int] = None
    closing_date: Optional[str] = None
    status: Optional[str] = None

class ClassificationResult(BaseModel):
    """Classification result model"""
    notice_identifier: str
    final_relevance_score: float
    keyword_score: float
    context_score: float
    ml_confidence: float
    composite_score: float
    technical_terms: List[str] = []
    transformation_signals: List[str] = []
    explanation: str
    processing_time_ms: Optional[int] = None
    classification_date: str  # maps to classification_date

class EnhancedResult(BaseModel):
    """Enhanced scoring result model"""
    notice_identifier: str
    final_relevance_score: float
    metadata_score: float
    business_alignment_score: float
    urgency_multiplier: float
    value_multiplier: float
    department_multiplier: float
    priority_level: str
    score_breakdown: Dict[str, Any] = {}
    explanation: str

class FilteredOpportunity(BaseModel):
    """Filtered opportunity result model"""
    notice_identifier: str
    final_relevance_score: float
    filter_passes: bool  # derived from recommendation
    overall_filter_score: float
    bid_probability: float
    competition_level: float
    filter_profile_used: str
    recommendation: str  # maps to recommendation
    risk_factors: List[str] = []
    success_factors: List[str] = []
    resource_requirements: Dict[str, Any] = {}
    recommendation_reasoning: str

class ExpertValidation(BaseModel):
    """Expert validation submission model"""
    notice_identifier: str
    expert_label: str = Field(..., pattern="^(relevant|not_relevant|unsure)$")
    confidence: int = Field(..., ge=1, le=5)
    notes: Optional[str] = None
    reasoning: Optional[str] = None

class ValidationStats(BaseModel):
    """Expert validation statistics model"""
    total_validations: int
    agreement_rate: float
    avg_confidence: float
    label_distribution: Dict[str, int]
    recent_validations: int
    avg_disagreement_magnitude: float

class ModelPerformance(BaseModel):
    """Model performance metrics model"""
    model_version: str
    f1_score: float
    precision_score: float
    recall_score: float
    accuracy_score: float
    training_samples: int
    expert_labels_used: int
    deployment_timestamp: Optional[str] = None
    improvement_over_previous: Optional[float] = None

class SystemHealth(BaseModel):
    """System health status model"""
    database_operational: bool
    classification_pipeline_status: str
    recent_classifications_count: int
    expert_validations_count: int
    model_performance_score: float
    integration_status: Dict[str, bool]
    uptime_hours: float

# ==================== DEPENDENCY INJECTION ====================

def get_data_access():
    """Dependency injection for data access"""
    if data_access is None:
        raise HTTPException(status_code=503, detail="Database not available")
    return data_access

def get_integrated_pipeline():
    """Dependency injection for integrated pipeline"""
    if integrated_pipeline is None:
        raise HTTPException(status_code=503, detail="Classification pipeline not available")
    return integrated_pipeline

# ==================== OPPORTUNITY DISCOVERY ENDPOINTS ====================

@app.get("/api/opportunities/top", response_model=List[Dict[str, Any]])
async def get_top_opportunities(
    min_score: float = Query(50.0, ge=0.0, le=100.0, description="Minimum relevance score"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of results"),
    profile: Optional[str] = Query(None, description="Filter profile (balanced, aggressive, conservative)"),
    filter_passed_only: bool = Query(True, description="Only return opportunities that passed filters"),
    data_access: EnhancedDataAccess = Depends(get_data_access)
):
    """Get top-scoring opportunities with optional filtering"""
    try:
        opportunities = data_access.get_top_opportunities(
            min_score=min_score,
            profile=profile,
            limit=limit,
            filter_passed_only=filter_passed_only
        )
        
        logger.info(f"Retrieved {len(opportunities)} top opportunities (min_score: {min_score})")
        return opportunities
        
    except Exception as e:
        logger.error(f"Failed to retrieve top opportunities: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve opportunities: {str(e)}")

@app.get("/api/opportunities/{notice_identifier}/details")
async def get_opportunity_details(
    notice_identifier: str,
    data_access: EnhancedDataAccess = Depends(get_data_access)
):
    """Get detailed information for a specific opportunity"""
    try:
        with data_access.get_connection() as conn:
            # Get tender details with classification
            cursor = conn.execute("""
                SELECT 
                    t.*,
                    ec.final_relevance_score,
                    CASE WHEN (ec.recommendation LIKE 'IMMEDIATE ACTION%' OR ec.recommendation LIKE 'WORTH REVIEWING%') THEN 1 ELSE 0 END as filter_passes,
                    ec.recommendation as recommendation,
                    0.7 as bid_probability,
                    'MEDIUM' as competition_level,
                    '[]' as risk_factors,
                    '[]' as success_factors,
                    '{}' as resource_requirements,
                    ec.explanation,
                    ec.classification_date as classification_date
                FROM tenders t
                LEFT JOIN v_api_enhanced_classifications ec ON t.notice_identifier = ec.notice_identifier
                WHERE t.notice_identifier = ?
                ORDER BY ec.classification_date DESC
                LIMIT 1
            """, (notice_identifier,))
            
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Opportunity not found")
            
            # Convert to dictionary and parse JSON fields
            opportunity = dict(result)
            
            # Parse JSON fields safely
            for json_field in ['risk_factors', 'success_factors', 'resource_requirements']:
                if opportunity.get(json_field):
                    try:
                        opportunity[json_field] = json.loads(opportunity[json_field])
                    except:
                        opportunity[json_field] = [] if json_field != 'resource_requirements' else {}
            
            logger.info(f"Retrieved detailed information for opportunity {notice_identifier}")
            return opportunity
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve opportunity details: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve details: {str(e)}")

@app.get("/api/opportunities/dashboard-data")
async def get_dashboard_data(
    period_days: int = Query(30, ge=1, le=365, description="Analysis period in days"),
    data_access: EnhancedDataAccess = Depends(get_data_access)
):
    """Get comprehensive dashboard data for opportunity analysis"""
    try:
        dashboard_data = {}
        
        with data_access.get_connection() as conn:
            # Get basic statistics
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_opportunities,
                    AVG(final_relevance_score) as avg_score,
                    COUNT(CASE WHEN (recommendation LIKE 'IMMEDIATE ACTION%' OR recommendation LIKE 'WORTH REVIEWING%') THEN 1 END) as filtered_count,
                    COUNT(CASE WHEN recommendation = 'PURSUE' THEN 1 END) as pursue_count,
                    COUNT(CASE WHEN recommendation = 'CONSIDER' THEN 1 END) as consider_count
                FROM v_api_enhanced_classifications
                WHERE DATE(classification_date) >= DATE('now', '-{} days')
            """.format(period_days))
            
            stats = dict(cursor.fetchone())
            dashboard_data['summary_stats'] = stats
            
            # Get recent high-value opportunities
            cursor = conn.execute("""
                SELECT 
                    ec.notice_identifier,
                    t.title,
                    t.organisation_name,
                    t.value_high,
                    ec.final_relevance_score,
                    ec.recommendation,
                    ec.classification_date
                FROM v_api_enhanced_classifications ec
                JOIN tenders t ON ec.notice_identifier = t.notice_identifier
                WHERE ec.final_relevance_score >= 70
                AND DATE(ec.classification_date) >= DATE('now', '-{} days')
                ORDER BY ec.final_relevance_score DESC, ec.classification_date DESC
                LIMIT 10
            """.format(period_days))
            
            dashboard_data['recent_high_value'] = [dict(row) for row in cursor.fetchall()]
            
            # Get score distribution
            cursor = conn.execute("""
                SELECT 
                    CASE 
                        WHEN final_relevance_score >= 80 THEN 'Excellent (80+)'
                        WHEN final_relevance_score >= 60 THEN 'Good (60-79)'
                        WHEN final_relevance_score >= 40 THEN 'Moderate (40-59)'
                        ELSE 'Low (<40)'
                    END as score_range,
                    COUNT(*) as count
                FROM v_api_enhanced_classifications
                WHERE DATE(classification_date) >= DATE('now', '-{} days')
                GROUP BY score_range
                ORDER BY MIN(final_relevance_score) DESC
            """.format(period_days))
            
            dashboard_data['score_distribution'] = [dict(row) for row in cursor.fetchall()]
            
            # Get recommendation trends
            cursor = conn.execute("""
                SELECT 
                    DATE(classification_date) as date,
                    recommendation,
                    COUNT(*) as count
                FROM v_api_enhanced_classifications
                WHERE DATE(classification_date) >= DATE('now', '-{} days')
                GROUP BY DATE(classification_date), recommendation
                ORDER BY date DESC
            """.format(period_days))
            
            dashboard_data['recommendation_trends'] = [dict(row) for row in cursor.fetchall()]
        
        logger.info(f"Generated dashboard data for {period_days}-day period")
        return dashboard_data
        
    except Exception as e:
        logger.error(f"Failed to generate dashboard data: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard: {str(e)}")

# ==================== CLASSIFICATION ENDPOINTS ====================

@app.post("/api/classify/single", response_model=Dict[str, Any])
async def classify_single_tender(
    tender_data: Dict[str, Any],
    save_to_db: bool = Query(True, description="Save classification result to database"),
    pipeline: IntegratedTenderPipeline = Depends(get_integrated_pipeline)
):
    """Classify a single tender through the complete pipeline"""
    try:
        if 'notice_identifier' not in tender_data:
            raise HTTPException(status_code=400, detail="notice_identifier is required")
        
        # Process through integrated pipeline
        result = pipeline.process_tender_complete(tender_data, save_to_db=save_to_db)
        
        if result['success']:
            logger.info(f"Successfully classified tender {tender_data['notice_identifier']}")
            return {
                'success': True,
                'notice_identifier': result['notice_identifier'],
                'steps_completed': result['steps_completed'],
                'final_result': {
                    'final_relevance_score': getattr(result['final_result'], 'final_relevance_score', 0),
                    'recommendation': getattr(result['final_result'], 'recommendation', 'MONITOR'),
                    'filter_passes': getattr(result['final_result'], 'recommendation', 'LOW PRIORITY').startswith(('IMMEDIATE ACTION', 'WORTH REVIEWING')),
                    'bid_probability': getattr(result['final_result'], 'bid_probability', 0.0),
                    'explanation': getattr(result['final_result'], 'recommendation_reasoning', '')
                },
                'processing_timestamp': result['processing_timestamp'],
                'database_operations': result.get('database_operations', [])
            }
        else:
            logger.error(f"Classification failed for tender {tender_data['notice_identifier']}: {result.get('error')}")
            raise HTTPException(status_code=500, detail=f"Classification failed: {result.get('error')}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Single tender classification error: {e}")
        raise HTTPException(status_code=500, detail=f"Classification error: {str(e)}")

@app.post("/api/classify/batch", response_model=List[Dict[str, Any]])
async def classify_tender_batch(
    tender_data_list: List[Dict[str, Any]],
    save_to_db: bool = Query(True, description="Save classification results to database"),
    pipeline: IntegratedTenderPipeline = Depends(get_integrated_pipeline)
):
    """Classify multiple tenders through the complete pipeline"""
    try:
        if not tender_data_list:
            raise HTTPException(status_code=400, detail="No tender data provided")
        
        if len(tender_data_list) > 50:
            raise HTTPException(status_code=400, detail="Batch size limited to 50 tenders")
        
        # Validate all tenders have notice_identifier
        for tender in tender_data_list:
            if 'notice_identifier' not in tender:
                raise HTTPException(status_code=400, detail="All tenders must have notice_identifier")
        
        # Process batch through integrated pipeline
        results = pipeline.process_tenders_batch(tender_data_list, save_to_db=save_to_db)
        
        # Format results for API response
        formatted_results = []
        for result in results:
            if result['success']:
                formatted_result = {
                    'success': True,
                    'notice_identifier': result['notice_identifier'],
                    'steps_completed': result['steps_completed'],
                    'final_result': {
                        'final_relevance_score': getattr(result.get('final_result'), 'final_relevance_score', 0),
                        'recommendation': getattr(result.get('final_result'), 'recommendation', 'MONITOR'),
                        'filter_passes': getattr(result.get('final_result'), 'recommendation', 'LOW PRIORITY').startswith(('IMMEDIATE ACTION', 'WORTH REVIEWING')),
                        'bid_probability': getattr(result.get('final_result'), 'bid_probability', 0.0)
                    },
                    'processing_timestamp': result['processing_timestamp']
                }
            else:
                formatted_result = {
                    'success': False,
                    'notice_identifier': result['notice_identifier'],
                    'error': result.get('error', 'Unknown error'),
                    'processing_timestamp': result['processing_timestamp']
                }
            
            formatted_results.append(formatted_result)
        
        successful_count = sum(1 for r in results if r['success'])
        logger.info(f"Batch classification completed: {successful_count}/{len(results)} successful")
        
        return formatted_results
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Batch classification error: {e}")
        raise HTTPException(status_code=500, detail=f"Batch classification error: {str(e)}")

@app.get("/api/classify/{notice_identifier}/explain")
async def get_classification_explanation(
    notice_identifier: str,
    data_access: EnhancedDataAccess = Depends(get_data_access)
):
    """Get detailed explanation of classification result"""
    try:
        with data_access.get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    notice_identifier,
                    keyword_score,
                    context_score,
                    ml_confidence,
                    composite_score,
                    metadata_score,
                    business_alignment_score,
                    urgency_multiplier,
                    value_multiplier,
                    department_multiplier,
                    final_relevance_score,
                    score_breakdown,
                    priority_level,
                    CASE WHEN (recommendation LIKE 'IMMEDIATE ACTION%' OR recommendation LIKE 'WORTH REVIEWING%') THEN 1 ELSE 0 END as filter_passes,
                    overall_filter_score,
                    bid_probability,
                    competition_level,
                    recommendation,
                    technical_terms,
                    transformation_signals,
                    risk_factors,
                    success_factors,
                    explanation,
                    model_version,
                    pipeline_version,
                    processing_time_ms,
                    classification_date
                FROM v_api_enhanced_classifications
                WHERE notice_identifier = ?
                ORDER BY classification_date DESC
                LIMIT 1
            """, (notice_identifier,))
            
            result = cursor.fetchone()
            if not result:
                raise HTTPException(status_code=404, detail="Classification not found")
            
            # Convert to dictionary and parse JSON fields
            explanation = dict(result)
            
            # Parse JSON fields
            json_fields = ['score_breakdown', 'technical_terms', 'transformation_signals', 'risk_factors', 'success_factors']
            for field in json_fields:
                if explanation.get(field):
                    try:
                        explanation[field] = json.loads(explanation[field])
                    except:
                        explanation[field] = [] if field != 'score_breakdown' else {}
            
            # Add explanation breakdown
            explanation['detailed_breakdown'] = {
                'step_1_classification': {
                    'keyword_score': explanation['keyword_score'],
                    'context_score': explanation['context_score'],
                    'ml_confidence': explanation['ml_confidence'],
                    'composite_score': explanation['composite_score'],
                    'technical_terms': explanation['technical_terms'],
                    'transformation_signals': explanation['transformation_signals']
                },
                'step_2_enhanced_scoring': {
                    'metadata_score': explanation['metadata_score'],
                    'business_alignment_score': explanation['business_alignment_score'],
                    'urgency_multiplier': explanation['urgency_multiplier'],
                    'value_multiplier': explanation['value_multiplier'],
                    'department_multiplier': explanation['department_multiplier'],
                    'final_relevance_score': explanation['final_relevance_score'],
                    'priority_level': explanation['priority_level']
                },
                'step_3_filtering': {
                    'filter_passes': explanation.get('recommendation', 'LOW PRIORITY').startswith(('IMMEDIATE ACTION', 'WORTH REVIEWING')),
                    'overall_filter_score': explanation['overall_filter_score'],
                    'bid_probability': explanation['bid_probability'],
                    'competition_level': explanation['competition_level'],
                    'recommendation': explanation['recommendation'],
                    'risk_factors': explanation['risk_factors'],
                    'success_factors': explanation['success_factors']
                }
            }
            
            logger.info(f"Generated detailed explanation for classification {notice_identifier}")
            return explanation
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate classification explanation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate explanation: {str(e)}")

# ==================== EXPERT VALIDATION ENDPOINTS ====================

@app.post("/api/validation/submit", response_model=Dict[str, Any])
async def submit_expert_validation(
    validation: ExpertValidation,
    data_access: EnhancedDataAccess = Depends(get_data_access)
):
    """Submit expert validation for a tender classification"""
    try:
        # Get current system prediction for agreement analysis
        with data_access.get_connection() as conn:
            cursor = conn.execute("""
                SELECT final_relevance_score, recommendation, ml_confidence
                FROM v_api_enhanced_classifications
                WHERE notice_identifier = ?
                ORDER BY classification_date DESC
                LIMIT 1
            """, (validation.notice_identifier,))
            
            system_prediction = cursor.fetchone()
        
        # Prepare validation data
        validation_data = {
            'notice_identifier': validation.notice_identifier,
            'expert_label': validation.expert_label,
            'confidence': validation.confidence,
            'notes': validation.notes,
            'reasoning': validation.reasoning,
            'system_prediction_score': system_prediction[0] if system_prediction else None,
            'system_recommendation': system_prediction[1] if system_prediction else None,
            'prediction_confidence': system_prediction[2] if system_prediction else None,
            'timestamp': datetime.now().isoformat()
        }
        
        # Save validation
        validation_id = data_access.save_expert_validation(validation_data)
        
        logger.info(f"Saved expert validation {validation_id} for tender {validation.notice_identifier}")
        
        return {
            'success': True,
            'validation_id': validation_id,
            'notice_identifier': validation.notice_identifier,
            'expert_label': validation.expert_label,
            'confidence': validation.confidence,
            'submission_timestamp': validation_data['timestamp']
        }
        
    except Exception as e:
        logger.error(f"Failed to submit expert validation: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to submit validation: {str(e)}")

@app.get("/api/validation/stats", response_model=ValidationStats)
async def get_validation_stats(
    period_days: int = Query(30, ge=1, le=365, description="Analysis period in days"),
    data_access: EnhancedDataAccess = Depends(get_data_access)
):
    """Get expert validation statistics and agreement analysis"""
    try:
        with data_access.get_connection() as conn:
            # Get basic validation statistics
            cursor = conn.execute("""
                SELECT 
                    COUNT(*) as total_validations,
                    AVG(CASE WHEN expert_system_agreement = 1 THEN 1.0 ELSE 0.0 END) as agreement_rate,
                    AVG(confidence) as avg_confidence,
                    AVG(disagreement_magnitude) as avg_disagreement_magnitude,
                    COUNT(CASE WHEN DATE(validation_timestamp) >= DATE('now', '-7 days') THEN 1 END) as recent_validations
                FROM expert_validation
                WHERE DATE(validation_timestamp) >= DATE('now', '-{} days')
            """.format(period_days))
            
            stats = dict(cursor.fetchone())
            
            # Get label distribution
            cursor = conn.execute("""
                SELECT expert_label, COUNT(*) as count
                FROM expert_validation
                WHERE DATE(validation_timestamp) >= DATE('now', '-{} days')
                GROUP BY expert_label
            """.format(period_days))
            
            label_distribution = {row[0]: row[1] for row in cursor.fetchall()}
            
            validation_stats = ValidationStats(
                total_validations=stats['total_validations'],
                agreement_rate=round(stats['agreement_rate'] or 0.0, 3),
                avg_confidence=round(stats['avg_confidence'] or 0.0, 2),
                label_distribution=label_distribution,
                recent_validations=stats['recent_validations'],
                avg_disagreement_magnitude=round(stats['avg_disagreement_magnitude'] or 0.0, 3)
            )
            
            logger.info(f"Generated validation statistics for {period_days}-day period")
            return validation_stats
            
    except Exception as e:
        logger.error(f"Failed to generate validation statistics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate statistics: {str(e)}")

@app.get("/api/validation/queue", response_model=List[Dict[str, Any]])
async def get_validation_queue(
    limit: int = Query(10, ge=1, le=50, description="Number of tenders to return"),
    min_score: float = Query(40.0, ge=0.0, le=100.0, description="Minimum relevance score"),
    data_access: EnhancedDataAccess = Depends(get_data_access)
):
    """Get tenders that need expert validation"""
    try:
        with data_access.get_connection() as conn:
            # Get tenders that haven't been validated yet, prioritizing high scores
            cursor = conn.execute("""
                SELECT 
                    t.notice_identifier,
                    t.title,
                    t.description,
                    t.organisation_name,
                    t.value_high,
                    t.closing_date,
                    ec.final_relevance_score,
                    ec.recommendation,
                    ec.bid_probability,
                    ec.explanation,
                    ec.classification_date
                FROM v_api_enhanced_classifications ec
                JOIN tenders t ON ec.notice_identifier = t.notice_identifier
                LEFT JOIN expert_validation ev ON ec.notice_identifier = ev.notice_identifier
                WHERE ev.notice_identifier IS NULL
                AND ec.final_relevance_score >= ?
                ORDER BY ec.final_relevance_score DESC, ec.classification_date DESC
                LIMIT ?
            """, (min_score, limit))
            
            validation_queue = [dict(row) for row in cursor.fetchall()]
            
            logger.info(f"Generated validation queue with {len(validation_queue)} tenders")
            return validation_queue
            
    except Exception as e:
        logger.error(f"Failed to generate validation queue: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate queue: {str(e)}")

# ==================== PERFORMANCE MONITORING ENDPOINTS ====================

@app.get("/api/performance/models", response_model=List[ModelPerformance])
async def get_model_performance(
    data_access: EnhancedDataAccess = Depends(get_data_access)
):
    """Get model performance metrics and trends"""
    try:
        with data_access.get_connection() as conn:
            cursor = conn.execute("""
                SELECT 
                    model_version,
                    f1_score,
                    precision_score,
                    recall_score,
                    accuracy_score,
                    training_samples,
                    expert_labels_used,
                    deployment_timestamp,
                    improvement_over_previous,
                    training_timestamp
                FROM model_performance
                ORDER BY training_timestamp DESC
                LIMIT 10
            """)
            
            models = []
            for row in cursor.fetchall():
                model = ModelPerformance(
                    model_version=row[0],
                    f1_score=row[1],
                    precision_score=row[2],
                    recall_score=row[3],
                    accuracy_score=row[4],
                    training_samples=row[5],
                    expert_labels_used=row[6],
                    deployment_timestamp=row[7],
                    improvement_over_previous=row[8]
                )
                models.append(model)
            
            logger.info(f"Retrieved performance data for {len(models)} models")
            return models
            
    except Exception as e:
        logger.error(f"Failed to retrieve model performance: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve performance: {str(e)}")

@app.get("/api/performance/system-health", response_model=SystemHealth)
async def get_system_health(
    data_access: EnhancedDataAccess = Depends(get_data_access),
    integration_manager: SystemIntegrationManager = Depends(lambda: integration_manager)
):
    """Get comprehensive system health metrics"""
    try:
        # Check database operational status
        database_operational = True
        try:
            with data_access.get_connection() as conn:
                conn.execute("SELECT 1").fetchone()
        except:
            database_operational = False
        
        # Get integration status
        integration_status = integration_manager.get_integration_status() if integration_manager else {}
        
        # Get recent activity metrics
        with data_access.get_connection() as conn:
            # Recent classifications
            cursor = conn.execute("""
                SELECT COUNT(*) FROM v_api_enhanced_classifications
                WHERE DATE(classification_date) >= DATE('now', '-7 days')
            """)
            recent_classifications = cursor.fetchone()[0]
            
            # Expert validations
            cursor = conn.execute("""
                SELECT COUNT(*) FROM expert_validation
                WHERE DATE(validation_timestamp) >= DATE('now', '-7 days')
            """)
            expert_validations = cursor.fetchone()[0]
            
            # Latest model performance
            cursor = conn.execute("""
                SELECT f1_score FROM model_performance
                ORDER BY training_timestamp DESC LIMIT 1
            """)
            latest_model = cursor.fetchone()
            model_performance_score = latest_model[0] if latest_model else 0.0
        
        # Determine pipeline status
        pipeline_status = "operational" if database_operational and integration_status.get('database_available', False) else "degraded"
        if not database_operational:
            pipeline_status = "offline"
        
        system_health = SystemHealth(
            database_operational=database_operational,
            classification_pipeline_status=pipeline_status,
            recent_classifications_count=recent_classifications,
            expert_validations_count=expert_validations,
            model_performance_score=round(model_performance_score, 3),
            integration_status=integration_status.get('component_integration_status', {}),
            uptime_hours=24.0  # Placeholder - would need actual uptime tracking
        )
        
        logger.info("Generated system health report")
        return system_health
        
    except Exception as e:
        logger.error(f"Failed to generate system health report: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate health report: {str(e)}")

# ==================== BASIC ENDPOINTS ====================

@app.get("/api/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "2.0.0",
        "service": "UK Tender Monitor API"
    }

@app.get("/api/info")
async def get_api_info():
    """Get API information and statistics"""
    try:
        info = {
            "service": "UK Tender Monitor API",
            "version": "2.0.0",
            "description": "Production API for UK government digital transformation opportunity discovery",
            "endpoints": {
                "opportunities": [
                    "/api/opportunities/top",
                    "/api/opportunities/{notice_id}/details",
                    "/api/opportunities/dashboard-data"
                ],
                "classification": [
                    "/api/classify/single",
                    "/api/classify/batch",
                    "/api/classify/{notice_id}/explain"
                ],
                "validation": [
                    "/api/validation/submit",
                    "/api/validation/stats",
                    "/api/validation/queue"
                ],
                "performance": [
                    "/api/performance/models",
                    "/api/performance/system-health"
                ]
            },
            "documentation": {
                "swagger_ui": "/api/docs",
                "redoc": "/api/redoc"
            }
        }
        
        # Add database statistics if available
        if data_access:
            try:
                with data_access.get_connection() as conn:
                    cursor = conn.execute("SELECT COUNT(*) FROM tenders")
                    total_tenders = cursor.fetchone()[0]
                    
                    cursor = conn.execute("SELECT COUNT(*) FROM v_api_enhanced_classifications")
                    total_classifications = cursor.fetchone()[0]
                    
                    info["statistics"] = {
                        "total_tenders": total_tenders,
                        "total_classifications": total_classifications,
                        "database_operational": True
                    }
            except:
                info["statistics"] = {"database_operational": False}
        
        return info
        
    except Exception as e:
        logger.error(f"Failed to generate API info: {e}")
        return {
            "service": "UK Tender Monitor API",
            "version": "2.0.0",
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    
    print("UK Tender Monitor - API Server Starting")
    print("="*60)
    print("Initializing classification pipeline...")
    
    success = initialize_system()
    if success:
        print("System initialization completed")
        print("Starting API server on http://localhost:8000")
        print("API documentation: http://localhost:8000/api/docs")
        print("Health check: http://localhost:8000/api/health")
        
        uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    else:
        print("System initialization failed - cannot start API server")