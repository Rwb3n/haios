#!/usr/bin/env python3
"""
UK Tender Monitor - System Integration Layer (Phase 2 Step 5)
Integration layer connecting database persistence with existing pipeline components

Core Features:
- Automatic result persistence for all pipeline components
- Configuration management for database operations
- Integration with classifier, scorer, filter, and trainer components
- Performance monitoring and error handling
- Graceful fallback when database operations fail
"""

import logging
from typing import Dict, List, Optional, Any, Union
from pathlib import Path
import json
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemIntegrationManager:
    """Manages integration between pipeline components and database persistence"""
    
    def __init__(self, data_dir: str = "data", enable_persistence: bool = True):
        self.data_dir = Path(data_dir)
        self.enable_persistence = enable_persistence
        self.data_access = None
        
        # Initialize database access if persistence enabled
        if enable_persistence:
            self._initialize_database_access()
        
        # Component integration status
        self.integration_status = {
            'database_available': self.data_access is not None,
            'classifier_integrated': False,
            'scorer_integrated': False,
            'filter_integrated': False,
            'trainer_integrated': False
        }
        
        logger.info(f"System integration manager initialized (persistence: {enable_persistence})")
    
    def _initialize_database_access(self):
        """Initialize database access layer"""
        try:
            from database_extensions import EnhancedDataAccess
            db_path = self.data_dir / "tenders.db"
            self.data_access = EnhancedDataAccess(str(db_path))
            logger.info("Database access layer initialized successfully")
        except Exception as e:
            logger.warning(f"Failed to initialize database access: {e}")
            self.data_access = None
    
    def integrate_classifier(self, classifier_instance):
        """Integrate database persistence with classifier component"""
        if not self.data_access:
            logger.warning("Database not available - classifier integration skipped")
            return False
        
        try:
            # Add persistence method to classifier
            original_classify_enhanced = getattr(classifier_instance, 'classify_tender_enhanced', None)
            if original_classify_enhanced:
                def classify_with_persistence(tender_data: Dict, save_to_db: bool = True):
                    """Enhanced classification with automatic database persistence"""
                    # Get classification result
                    result = original_classify_enhanced(tender_data)
                    
                    # Save to database if enabled
                    if save_to_db and self.enable_persistence:
                        try:
                            classification_id = self.data_access.save_classification_result(result, tender_data)
                            result.classification_id = classification_id
                            logger.debug(f"Saved classification {classification_id} to database")
                        except Exception as e:
                            logger.warning(f"Failed to save classification result: {e}")
                    
                    return result
                
                # Replace method with persistence-enabled version
                classifier_instance.classify_tender_enhanced = classify_with_persistence
                self.integration_status['classifier_integrated'] = True
                logger.info("Classifier component integrated with database persistence")
                return True
                
        except Exception as e:
            logger.error(f"Failed to integrate classifier: {e}")
            return False
    
    def integrate_scorer(self, scorer_instance):
        """Integrate database persistence with scorer component"""
        if not self.data_access:
            logger.warning("Database not available - scorer integration skipped")
            return False
        
        try:
            # Add persistence method to scorer
            original_score_classified = getattr(scorer_instance, 'score_classified_tender', None)
            if original_score_classified:
                def score_with_persistence(tender_data: Dict, classification_result, save_to_db: bool = True):
                    """Enhanced scoring with automatic database persistence"""
                    # Get scoring result
                    result = original_score_classified(tender_data, classification_result)
                    
                    # Save to database if enabled
                    if save_to_db and self.enable_persistence:
                        try:
                            classification_id = self.data_access.save_classification_result(result, tender_data)
                            result.classification_id = classification_id
                            logger.debug(f"Saved enhanced scoring {classification_id} to database")
                        except Exception as e:
                            logger.warning(f"Failed to save scoring result: {e}")
                    
                    return result
                
                # Replace method with persistence-enabled version
                scorer_instance.score_classified_tender = score_with_persistence
                self.integration_status['scorer_integrated'] = True
                logger.info("Scorer component integrated with database persistence")
                return True
                
        except Exception as e:
            logger.error(f"Failed to integrate scorer: {e}")
            return False
    
    def integrate_filter(self, filter_instance):
        """Integrate database persistence with filter component"""
        if not self.data_access:
            logger.warning("Database not available - filter integration skipped")
            return False
        
        try:
            # Add persistence method to filter
            original_filter_opportunities = getattr(filter_instance, 'filter_opportunities', None)
            if original_filter_opportunities:
                def filter_with_persistence(enhanced_results: List, profile: str = 'balanced', save_to_db: bool = True):
                    """Advanced filtering with automatic database persistence"""
                    # Get filtering results
                    results = original_filter_opportunities(enhanced_results, profile)
                    
                    # Save to database if enabled
                    if save_to_db and self.enable_persistence:
                        for result in results:
                            try:
                                # Load tender data for the result
                                tender_data = self._load_tender_data(result.notice_identifier)
                                classification_id = self.data_access.save_classification_result(result, tender_data)
                                result.classification_id = classification_id
                                logger.debug(f"Saved filter result {classification_id} to database")
                            except Exception as e:
                                logger.warning(f"Failed to save filter result for {result.notice_identifier}: {e}")
                    
                    return results
                
                # Replace method with persistence-enabled version
                filter_instance.filter_opportunities = filter_with_persistence
                self.integration_status['filter_integrated'] = True
                logger.info("Filter component integrated with database persistence")
                return True
                
        except Exception as e:
            logger.error(f"Failed to integrate filter: {e}")
            return False
    
    def integrate_trainer(self, trainer_instance):
        """Integrate database persistence with trainer component"""
        if not self.data_access:
            logger.warning("Database not available - trainer integration skipped")
            return False
        
        try:
            # Add persistence methods to trainer
            original_save_expert_label = getattr(trainer_instance.labeling_interface, 'present_for_labeling', None)
            if original_save_expert_label:
                def save_expert_label_with_persistence(tender_data: Dict, current_prediction: Dict = None):
                    """Expert labeling with automatic database persistence"""
                    # Get expert label
                    expert_record = original_save_expert_label(tender_data, current_prediction)
                    
                    # Save to database if enabled and record exists
                    if expert_record and self.enable_persistence:
                        try:
                            validation_id = self.data_access.save_expert_validation(expert_record)
                            expert_record['validation_id'] = validation_id
                            logger.debug(f"Saved expert validation {validation_id} to database")
                        except Exception as e:
                            logger.warning(f"Failed to save expert validation: {e}")
                    
                    return expert_record
                
                # Replace method with persistence-enabled version
                trainer_instance.labeling_interface.present_for_labeling = save_expert_label_with_persistence
            
            # Add model performance persistence
            original_update_model = getattr(trainer_instance, 'update_model_with_expert_feedback', None)
            if original_update_model:
                def update_model_with_persistence():
                    """Model update with automatic performance persistence"""
                    # Update model
                    performance_record = original_update_model()
                    
                    # Save performance to database if enabled
                    if 'error' not in performance_record and self.enable_persistence:
                        try:
                            performance_id = self.data_access.save_model_performance(performance_record)
                            performance_record['performance_id'] = performance_id
                            logger.debug(f"Saved model performance {performance_id} to database")
                        except Exception as e:
                            logger.warning(f"Failed to save model performance: {e}")
                    
                    return performance_record
                
                # Replace method with persistence-enabled version
                trainer_instance.update_model_with_expert_feedback = update_model_with_persistence
            
            self.integration_status['trainer_integrated'] = True
            logger.info("Trainer component integrated with database persistence")
            return True
            
        except Exception as e:
            logger.error(f"Failed to integrate trainer: {e}")
            return False
    
    def _load_tender_data(self, notice_identifier: str) -> Optional[Dict]:
        """Load tender data from database for a given notice identifier"""
        try:
            with self.data_access.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT notice_identifier, title, description, organisation_name,
                           value_high, status, suitable_for_sme, cpv_codes, closing_date,
                           published_date, links, contact_details
                    FROM tenders
                    WHERE notice_identifier = ?
                """, (notice_identifier,))
                
                row = cursor.fetchone()
                if row:
                    return dict(row)
                else:
                    return None
                    
        except Exception as e:
            logger.warning(f"Failed to load tender data for {notice_identifier}: {e}")
            return None
    
    def get_integration_status(self) -> Dict:
        """Get current integration status"""
        return {
            'database_persistence_enabled': self.enable_persistence,
            'database_available': self.data_access is not None,
            'component_integration_status': self.integration_status,
            'integration_summary': {
                'total_components': 4,
                'integrated_components': sum(1 for status in self.integration_status.values() if status and status != self.integration_status['database_available']),
                'integration_complete': all(self.integration_status.values())
            }
        }
    
    def create_integrated_pipeline(self):
        """Create a fully integrated pipeline with all components"""
        try:
            # Import all components
            from classifier import TenderClassifier
            from scorer import RelevanceScorer
            from filter import AdvancedOpportunityFilter
            from trainer import ContinuousLearningSystem
            
            # Initialize components
            classifier = TenderClassifier(enable_enhanced_scoring=True)
            scorer = RelevanceScorer()
            opportunity_filter = AdvancedOpportunityFilter()
            continuous_learner = ContinuousLearningSystem(str(self.data_dir))
            
            # Integrate all components with database persistence
            classifier_integrated = self.integrate_classifier(classifier)
            scorer_integrated = self.integrate_scorer(scorer)
            filter_integrated = self.integrate_filter(opportunity_filter)
            trainer_integrated = self.integrate_trainer(continuous_learner)
            
            # Create integrated pipeline object
            integrated_pipeline = IntegratedTenderPipeline(
                classifier=classifier,
                scorer=scorer,
                opportunity_filter=opportunity_filter,
                continuous_learner=continuous_learner,
                data_access=self.data_access,
                integration_manager=self
            )
            
            logger.info(f"Integrated pipeline created - Components integrated: {sum([classifier_integrated, scorer_integrated, filter_integrated, trainer_integrated])}/4")
            return integrated_pipeline
            
        except Exception as e:
            logger.error(f"Failed to create integrated pipeline: {e}")
            return None


class IntegratedTenderPipeline:
    """Fully integrated tender monitoring pipeline with database persistence"""
    
    def __init__(self, classifier, scorer, opportunity_filter, continuous_learner, data_access, integration_manager):
        self.classifier = classifier
        self.scorer = scorer
        self.opportunity_filter = opportunity_filter
        self.continuous_learner = continuous_learner
        self.data_access = data_access
        self.integration_manager = integration_manager
        
        logger.info("Integrated tender pipeline initialized")
    
    def process_tender_complete(self, tender_data: Dict, save_to_db: bool = True) -> Dict:
        """Process tender through complete pipeline with optional database persistence"""
        pipeline_result = {
            'notice_identifier': tender_data['notice_identifier'],
            'processing_timestamp': datetime.now().isoformat(),
            'steps_completed': [],
            'final_result': None,
            'database_operations': []
        }
        
        try:
            # Step 1: Basic Classification
            classification_result = self.classifier.classify_tender(tender_data)
            pipeline_result['steps_completed'].append('classification')
            pipeline_result['classification_result'] = classification_result
            
            # Step 2: Enhanced Scoring
            if hasattr(self.classifier, 'classify_tender_enhanced'):
                enhanced_result = self.classifier.classify_tender_enhanced(tender_data, save_to_db=save_to_db)
                pipeline_result['steps_completed'].append('enhanced_scoring')
                pipeline_result['enhanced_result'] = enhanced_result
                
                if save_to_db and hasattr(enhanced_result, 'classification_id'):
                    pipeline_result['database_operations'].append(f"Enhanced result saved: ID {enhanced_result.classification_id}")
            else:
                # Fallback to scorer if enhanced method not available
                enhanced_result = self.scorer.score_classified_tender(tender_data, classification_result, save_to_db=save_to_db)
                pipeline_result['steps_completed'].append('scoring')
                pipeline_result['enhanced_result'] = enhanced_result
            
            # Step 3: Advanced Filtering
            filtered_results = self.opportunity_filter.filter_opportunities([enhanced_result], save_to_db=save_to_db)
            if filtered_results:
                filtered_result = filtered_results[0]
                pipeline_result['steps_completed'].append('filtering')
                pipeline_result['filtered_result'] = filtered_result
                pipeline_result['final_result'] = filtered_result
                
                if save_to_db and hasattr(filtered_result, 'classification_id'):
                    pipeline_result['database_operations'].append(f"Filter result saved: ID {filtered_result.classification_id}")
            else:
                pipeline_result['final_result'] = enhanced_result
            
            pipeline_result['success'] = True
            
        except Exception as e:
            pipeline_result['success'] = False
            pipeline_result['error'] = str(e)
            logger.error(f"Pipeline processing failed for {tender_data['notice_identifier']}: {e}")
        
        return pipeline_result
    
    def process_tenders_batch(self, tender_data_list: List[Dict], save_to_db: bool = True) -> List[Dict]:
        """Process multiple tenders through complete pipeline"""
        results = []
        
        for i, tender_data in enumerate(tender_data_list):
            logger.info(f"Processing tender {i+1}/{len(tender_data_list)}: {tender_data['notice_identifier']}")
            
            try:
                result = self.process_tender_complete(tender_data, save_to_db=save_to_db)
                results.append(result)
            except Exception as e:
                error_result = {
                    'notice_identifier': tender_data.get('notice_identifier', 'unknown'),
                    'success': False,
                    'error': str(e),
                    'processing_timestamp': datetime.now().isoformat()
                }
                results.append(error_result)
                logger.error(f"Failed to process tender {tender_data.get('notice_identifier', 'unknown')}: {e}")
        
        return results
    
    def get_pipeline_performance_summary(self, period_days: int = 30) -> Dict:
        """Get pipeline performance summary"""
        if not self.data_access:
            return {'error': 'Database not available for performance analysis'}
        
        try:
            # Get classification statistics
            classification_stats = self.data_access.get_classification_statistics(period_days)
            
            # Get expert validation stats
            validation_stats = self.data_access.get_expert_validation_stats(period_days)
            
            # Get model performance
            model_performance = self.data_access.get_best_performing_model()
            
            # Get integration status
            integration_status = self.integration_manager.get_integration_status()
            
            return {
                'period_days': period_days,
                'generated_timestamp': datetime.now().isoformat(),
                'classification_performance': classification_stats,
                'expert_validation_performance': validation_stats,
                'model_performance': model_performance,
                'integration_status': integration_status,
                'pipeline_health': {
                    'all_components_integrated': integration_status['integration_summary']['integration_complete'],
                    'database_operational': integration_status['database_available'],
                    'persistence_enabled': integration_status['database_persistence_enabled']
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to generate performance summary: {e}")
            return {'error': f'Failed to generate performance summary: {e}'}
    
    def demonstrate_integrated_pipeline(self, limit: int = 5) -> Dict:
        """Demonstrate integrated pipeline with sample data"""
        try:
            # Load sample tenders from database
            with self.data_access.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT notice_identifier, title, description, organisation_name,
                           value_high, status, suitable_for_sme, cpv_codes, closing_date
                    FROM tenders
                    ORDER BY RANDOM()
                    LIMIT ?
                """, (limit,))
                
                sample_tenders = [dict(row) for row in cursor.fetchall()]
            
            if not sample_tenders:
                return {'error': 'No sample tenders available in database'}
            
            # Process sample tenders through integrated pipeline
            logger.info(f"Demonstrating integrated pipeline with {len(sample_tenders)} sample tenders")
            
            demo_results = []
            for tender in sample_tenders:
                result = self.process_tender_complete(tender, save_to_db=False)  # Demo mode - don't save
                
                # Create summary for demo
                demo_summary = {
                    'notice_identifier': result['notice_identifier'],
                    'title': tender['title'][:50] + '...' if len(tender['title']) > 50 else tender['title'],
                    'organisation': tender['organisation_name'],
                    'steps_completed': result['steps_completed'],
                    'success': result['success']
                }
                
                if result['success'] and result.get('final_result'):
                    final = result['final_result']
                    demo_summary.update({
                        'final_relevance_score': getattr(final, 'final_relevance_score', 0),
                        'recommendation': getattr(final, 'final_recommendation', 'MONITOR'),
                        'filter_passes': getattr(final, 'filter_passes', False),
                        'bid_probability': getattr(final, 'bid_probability', 0.0)
                    })
                
                demo_results.append(demo_summary)
            
            return {
                'demonstration_timestamp': datetime.now().isoformat(),
                'sample_size': len(sample_tenders),
                'successful_processing': sum(1 for r in demo_results if r['success']),
                'integration_status': self.integration_manager.get_integration_status(),
                'sample_results': demo_results
            }
            
        except Exception as e:
            logger.error(f"Pipeline demonstration failed: {e}")
            return {'error': f'Pipeline demonstration failed: {e}'}


def main():
    """Test system integration"""
    print("🎯 UK Tender Monitor - System Integration Test")
    print("="*60)
    
    # Initialize integration manager
    print("\n1️⃣ Initializing system integration manager...")
    integration_manager = SystemIntegrationManager(enable_persistence=True)
    
    # Check integration status
    status = integration_manager.get_integration_status()
    print(f"Database available: {status['database_available']}")
    print(f"Persistence enabled: {status['database_persistence_enabled']}")
    
    # Create integrated pipeline
    print("\n2️⃣ Creating integrated pipeline...")
    pipeline = integration_manager.create_integrated_pipeline()
    
    if pipeline:
        print("✅ Integrated pipeline created successfully")
        
        # Get integration status
        integration_status = integration_manager.get_integration_status()
        integrated_count = integration_status['integration_summary']['integrated_components']
        total_count = integration_status['integration_summary']['total_components']
        print(f"Components integrated: {integrated_count}/{total_count}")
        
        # Demonstrate pipeline
        print("\n3️⃣ Demonstrating integrated pipeline...")
        demo_results = pipeline.demonstrate_integrated_pipeline(limit=3)
        
        if 'error' not in demo_results:
            print(f"✅ Pipeline demonstration completed")
            print(f"Sample size: {demo_results['sample_size']}")
            print(f"Successful processing: {demo_results['successful_processing']}/{demo_results['sample_size']}")
            
            # Show sample results
            for i, result in enumerate(demo_results['sample_results'][:2], 1):
                print(f"\n  Sample {i}: {result['title']}")
                print(f"    Steps: {' → '.join(result['steps_completed'])}")
                if result['success']:
                    print(f"    Final Score: {result.get('final_relevance_score', 'N/A')}")
                    print(f"    Recommendation: {result.get('recommendation', 'N/A')}")
        else:
            print(f"❌ Pipeline demonstration failed: {demo_results['error']}")
        
        # Get performance summary
        print("\n4️⃣ Performance summary...")
        try:
            performance = pipeline.get_pipeline_performance_summary(period_days=7)
            if 'error' not in performance:
                print("✅ Performance summary generated")
                print(f"Pipeline health: {'✅ Healthy' if performance['pipeline_health']['all_components_integrated'] else '⚠️ Partial'}")
            else:
                print(f"⚠️ Performance summary error: {performance['error']}")
        except Exception as e:
            print(f"⚠️ Performance summary failed: {e}")
    else:
        print("❌ Failed to create integrated pipeline")
    
    print("\n✅ System Integration test completed!")


if __name__ == "__main__":
    main()