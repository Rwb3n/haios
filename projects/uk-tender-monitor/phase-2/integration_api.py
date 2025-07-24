#!/usr/bin/env python3
"""
UK Tender Monitor - Phase 1 Integration API (Phase 2 Step 6)
Integration layer connecting Phase 2 classification pipeline with Phase 1 data collection system

Core Features:
- Automatic classification of new tenders from data collector
- Enhanced monitoring with classification-based priority scoring
- Backward compatibility with existing Phase 1 database operations
- Configuration management for classification automation
- Real-time integration with existing collection and monitoring workflows
"""

import logging
import sqlite3
import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from contextlib import contextmanager
import threading
import time

# Import Phase 1 components
try:
    from data_collector import TenderDataCollector
    from monitor import TenderMonitor
except ImportError:
    logging.warning("Phase 1 components not available for import")

# Import Phase 2 components
from database_extensions import EnhancedDataAccess, DatabaseSchemaManager
from system_integration import SystemIntegrationManager, IntegratedTenderPipeline
from api import initialize_system

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Phase1IntegrationManager:
    """Manages integration between Phase 2 classification and Phase 1 collection/monitoring"""
    
    def __init__(self, data_dir: str = "data", enable_auto_classification: bool = True):
        self.data_dir = Path(data_dir)
        self.enable_auto_classification = enable_auto_classification
        self.db_path = self.data_dir / "tenders.db"
        
        # Initialize Phase 2 components
        self.data_access = None
        self.integration_manager = None
        self.integrated_pipeline = None
        self.phase1_collector = None
        self.phase1_monitor = None
        
        # Integration status
        self.integration_active = False
        self.classification_stats = {
            'total_processed': 0,
            'successful_classifications': 0,
            'failed_classifications': 0,
            'last_classification_time': None
        }
        
        logger.info(f"Phase 1 Integration Manager initialized (auto_classification: {enable_auto_classification})")
    
    def initialize_components(self) -> bool:
        """Initialize all integration components"""
        try:
            logger.info("Initializing Phase 1 integration components...")
            
            # Initialize Phase 2 components
            self.data_access = EnhancedDataAccess(str(self.db_path))
            self.integration_manager = SystemIntegrationManager(
                data_dir=str(self.data_dir),
                enable_persistence=True
            )
            self.integrated_pipeline = self.integration_manager.create_integrated_pipeline()
            
            # Initialize Phase 1 components if available
            try:
                self.phase1_collector = TenderDataCollector()
                self.phase1_monitor = TenderMonitor(str(self.db_path))
                logger.info("✅ Phase 1 components initialized successfully")
            except Exception as e:
                logger.warning(f"Phase 1 components not available: {e}")
            
            self.integration_active = True
            logger.info("✅ Phase 1 integration components initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize integration components: {e}")
            return False
    
    def integrate_with_data_collector(self) -> bool:
        """Integrate automatic classification with data collector"""
        if not self.phase1_collector or not self.integrated_pipeline:
            logger.warning("Data collector or classification pipeline not available")
            return False
        
        try:
            # Add post-collection hook for automatic classification
            original_process_records = getattr(self.phase1_collector, 'process_export_records', None)
            
            if original_process_records:
                def process_with_classification(records_data):
                    """Process records with automatic classification"""
                    # Process records normally
                    result = original_process_records(records_data)
                    
                    # Automatically classify new/updated records if enabled
                    if self.enable_auto_classification and result.get('new_records', 0) > 0:
                        self._classify_recent_records(hours_back=1)
                    
                    return result
                
                # Replace method with classification-enhanced version
                self.phase1_collector.process_export_records = process_with_classification
                logger.info("✅ Data collector integrated with automatic classification")
                return True
            
        except Exception as e:
            logger.error(f"Failed to integrate with data collector: {e}")
            return False
    
    def integrate_with_monitor(self) -> bool:
        """Integrate classification-enhanced monitoring with Phase 1 monitor"""
        if not self.phase1_monitor or not self.data_access:
            logger.warning("Monitor or data access not available")
            return False
        
        try:
            # Add classification-based priority enhancement
            original_analyze_changes = getattr(self.phase1_monitor, 'analyze_changes', None)
            
            if original_analyze_changes:
                def analyze_with_classification_priority(changes):
                    """Analyze changes with classification-based priority enhancement"""
                    # Analyze changes normally
                    analysis = original_analyze_changes(changes)
                    
                    # Enhance priority scores with classification data
                    enhanced_analysis = self._enhance_change_analysis_with_classification(analysis)
                    
                    return enhanced_analysis
                
                # Replace method with classification-enhanced version
                self.phase1_monitor.analyze_changes = analyze_with_classification_priority
                logger.info("✅ Monitor integrated with classification-based priority scoring")
                return True
            
        except Exception as e:
            logger.error(f"Failed to integrate with monitor: {e}")
            return False
    
    def _classify_recent_records(self, hours_back: int = 1) -> Dict[str, Any]:
        """Classify recently added/updated tender records"""
        try:
            # Get recent tender records
            cutoff_time = datetime.now() - timedelta(hours=hours_back)
            
            with self.data_access.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT notice_identifier, title, description, organisation_name,
                           value_high, status, suitable_for_sme, cpv_codes, closing_date,
                           published_date, links, contact_details
                    FROM tenders
                    WHERE published_date >= ?
                    OR notice_identifier NOT IN (
                        SELECT DISTINCT notice_identifier 
                        FROM enhanced_classifications
                    )
                    ORDER BY published_date DESC
                    LIMIT 50
                """, (cutoff_time.isoformat(),))
                
                recent_tenders = [dict(row) for row in cursor.fetchall()]
            
            if not recent_tenders:
                logger.info("No recent tenders found for classification")
                return {'processed': 0, 'successful': 0, 'failed': 0}
            
            # Classify recent tenders through integrated pipeline
            logger.info(f"Classifying {len(recent_tenders)} recent tenders...")
            
            results = self.integrated_pipeline.process_tenders_batch(
                recent_tenders, 
                save_to_db=True
            )
            
            # Update statistics
            successful = sum(1 for r in results if r['success'])
            failed = len(results) - successful
            
            self.classification_stats['total_processed'] += len(results)
            self.classification_stats['successful_classifications'] += successful
            self.classification_stats['failed_classifications'] += failed
            self.classification_stats['last_classification_time'] = datetime.now().isoformat()
            
            logger.info(f"✅ Recent classification completed: {successful}/{len(results)} successful")
            
            return {
                'processed': len(results),
                'successful': successful,
                'failed': failed,
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Failed to classify recent records: {e}")
            return {'processed': 0, 'successful': 0, 'failed': 0, 'error': str(e)}
    
    def _enhance_change_analysis_with_classification(self, analysis: Dict) -> Dict:
        """Enhance change analysis with classification-based priority scoring"""
        try:
            enhanced_analysis = analysis.copy()
            
            # Get classification data for changed tenders
            changed_tenders = analysis.get('changes', [])
            if not changed_tenders:
                return enhanced_analysis
            
            # Extract notice identifiers from changes
            notice_ids = []
            for change in changed_tenders:
                if 'notice_identifier' in change:
                    notice_ids.append(change['notice_identifier'])
            
            if not notice_ids:
                return enhanced_analysis
            
            # Get classification scores for changed tenders
            with self.data_access.get_connection() as conn:
                placeholders = ','.join('?' * len(notice_ids))
                cursor = conn.execute(f"""
                    SELECT notice_identifier, final_relevance_score, final_recommendation,
                           filter_passes, bid_probability, priority_level
                    FROM enhanced_classifications
                    WHERE notice_identifier IN ({placeholders})
                    ORDER BY classification_timestamp DESC
                """, notice_ids)
                
                classifications = {row[0]: dict(row) for row in cursor.fetchall()}
            
            # Enhance priority scores based on classification
            enhanced_changes = []
            for change in changed_tenders:
                enhanced_change = change.copy()
                notice_id = change.get('notice_identifier')
                
                if notice_id in classifications:
                    classification = classifications[notice_id]
                    
                    # Calculate enhanced priority score
                    base_priority = change.get('priority_score', 5)
                    relevance_score = classification.get('final_relevance_score', 0)
                    
                    # Boost priority for high-relevance opportunities
                    if relevance_score >= 80:
                        priority_multiplier = 1.5
                    elif relevance_score >= 60:
                        priority_multiplier = 1.2
                    elif relevance_score >= 40:
                        priority_multiplier = 1.0
                    else:
                        priority_multiplier = 0.8
                    
                    # Additional boost for PURSUE recommendations
                    if classification.get('final_recommendation') == 'PURSUE':
                        priority_multiplier *= 1.3
                    
                    enhanced_priority = min(base_priority * priority_multiplier, 10)
                    
                    # Add classification context to change
                    enhanced_change.update({
                        'enhanced_priority_score': round(enhanced_priority, 1),
                        'classification_score': relevance_score,
                        'recommendation': classification.get('final_recommendation'),
                        'filter_passes': classification.get('filter_passes'),
                        'bid_probability': classification.get('bid_probability'),
                        'priority_reason': f"Enhanced by classification (score: {relevance_score}, recommendation: {classification.get('final_recommendation')})"
                    })
                
                enhanced_changes.append(enhanced_change)
            
            # Update analysis with enhanced changes
            enhanced_analysis['changes'] = enhanced_changes
            enhanced_analysis['classification_enhanced'] = True
            enhanced_analysis['enhancement_timestamp'] = datetime.now().isoformat()
            
            logger.info(f"Enhanced change analysis with classification data for {len(enhanced_changes)} changes")
            return enhanced_analysis
            
        except Exception as e:
            logger.error(f"Failed to enhance change analysis: {e}")
            return analysis
    
    def classify_all_unclassified_tenders(self) -> Dict[str, Any]:
        """Classify all tenders that haven't been classified yet"""
        try:
            logger.info("Starting classification of all unclassified tenders...")
            
            # Get all unclassified tenders
            with self.data_access.get_connection() as conn:
                cursor = conn.execute("""
                    SELECT notice_identifier, title, description, organisation_name,
                           value_high, status, suitable_for_sme, cpv_codes, closing_date,
                           published_date, links, contact_details
                    FROM tenders
                    WHERE notice_identifier NOT IN (
                        SELECT DISTINCT notice_identifier 
                        FROM enhanced_classifications
                    )
                    ORDER BY published_date DESC
                """)
                
                unclassified_tenders = [dict(row) for row in cursor.fetchall()]
            
            if not unclassified_tenders:
                logger.info("No unclassified tenders found")
                return {'processed': 0, 'successful': 0, 'failed': 0}
            
            logger.info(f"Found {len(unclassified_tenders)} unclassified tenders")
            
            # Process in batches to avoid memory issues
            batch_size = 25
            all_results = []
            total_successful = 0
            total_failed = 0
            
            for i in range(0, len(unclassified_tenders), batch_size):
                batch = unclassified_tenders[i:i+batch_size]
                logger.info(f"Processing batch {i//batch_size + 1}: {len(batch)} tenders")
                
                batch_results = self.integrated_pipeline.process_tenders_batch(
                    batch, 
                    save_to_db=True
                )
                
                successful = sum(1 for r in batch_results if r['success'])
                failed = len(batch_results) - successful
                
                total_successful += successful
                total_failed += failed
                all_results.extend(batch_results)
                
                logger.info(f"Batch completed: {successful}/{len(batch_results)} successful")
                
                # Small delay between batches
                time.sleep(0.5)
            
            # Update statistics
            self.classification_stats['total_processed'] += len(all_results)
            self.classification_stats['successful_classifications'] += total_successful
            self.classification_stats['failed_classifications'] += total_failed
            self.classification_stats['last_classification_time'] = datetime.now().isoformat()
            
            logger.info(f"✅ Bulk classification completed: {total_successful}/{len(all_results)} successful")
            
            return {
                'processed': len(all_results),
                'successful': total_successful,
                'failed': total_failed,
                'results': all_results,
                'batch_count': (len(unclassified_tenders) + batch_size - 1) // batch_size
            }
            
        except Exception as e:
            logger.error(f"Failed to classify unclassified tenders: {e}")
            return {'processed': 0, 'successful': 0, 'failed': 0, 'error': str(e)}
    
    def get_integration_status(self) -> Dict[str, Any]:
        """Get comprehensive integration status"""
        try:
            # Database status
            database_status = "operational"
            try:
                with self.data_access.get_connection() as conn:
                    conn.execute("SELECT 1").fetchone()
            except:
                database_status = "error"
            
            # Phase 1 component status
            phase1_status = {
                'collector_available': self.phase1_collector is not None,
                'monitor_available': self.phase1_monitor is not None,
                'collector_integrated': hasattr(self.phase1_collector, 'process_export_records') if self.phase1_collector else False,
                'monitor_integrated': hasattr(self.phase1_monitor, 'analyze_changes') if self.phase1_monitor else False
            }
            
            # Phase 2 component status
            phase2_status = {
                'data_access_available': self.data_access is not None,
                'integration_manager_available': self.integration_manager is not None,
                'pipeline_available': self.integrated_pipeline is not None
            }
            
            # Classification statistics
            with self.data_access.get_connection() as conn:
                # Total tenders
                cursor = conn.execute("SELECT COUNT(*) FROM tenders")
                total_tenders = cursor.fetchone()[0]
                
                # Classified tenders
                cursor = conn.execute("SELECT COUNT(DISTINCT notice_identifier) FROM enhanced_classifications")
                classified_tenders = cursor.fetchone()[0]
                
                # Recent activity
                cursor = conn.execute("""
                    SELECT COUNT(*) FROM enhanced_classifications
                    WHERE DATE(classification_timestamp) >= DATE('now', '-7 days')
                """)
                recent_classifications = cursor.fetchone()[0]
            
            classification_coverage = (classified_tenders / total_tenders * 100) if total_tenders > 0 else 0
            
            return {
                'integration_active': self.integration_active,
                'auto_classification_enabled': self.enable_auto_classification,
                'database_status': database_status,
                'phase1_components': phase1_status,
                'phase2_components': phase2_status,
                'classification_stats': self.classification_stats,
                'coverage_stats': {
                    'total_tenders': total_tenders,
                    'classified_tenders': classified_tenders,
                    'classification_coverage_percent': round(classification_coverage, 1),
                    'recent_classifications_7days': recent_classifications
                },
                'status_timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get integration status: {e}")
            return {
                'integration_active': False,
                'error': str(e),
                'status_timestamp': datetime.now().isoformat()
            }
    
    def setup_automatic_classification_schedule(self, interval_minutes: int = 60) -> bool:
        """Set up automatic classification of new tenders on a schedule"""
        if not self.enable_auto_classification:
            logger.info("Automatic classification disabled - skipping schedule setup")
            return False
        
        try:
            def classification_worker():
                """Background worker for automatic classification"""
                while self.integration_active:
                    try:
                        logger.info("Running scheduled classification of recent tenders...")
                        result = self._classify_recent_records(hours_back=interval_minutes // 60 + 1)
                        
                        if result['processed'] > 0:
                            logger.info(f"Scheduled classification: {result['successful']}/{result['processed']} successful")
                        
                    except Exception as e:
                        logger.error(f"Scheduled classification error: {e}")
                    
                    # Wait for next interval
                    time.sleep(interval_minutes * 60)
            
            # Start background worker thread
            worker_thread = threading.Thread(target=classification_worker, daemon=True)
            worker_thread.start()
            
            logger.info(f"✅ Automatic classification schedule started (interval: {interval_minutes} minutes)")
            return True
            
        except Exception as e:
            logger.error(f"Failed to setup classification schedule: {e}")
            return False
    
    def create_enhanced_data_collector(self):
        """Create an enhanced data collector with automatic classification"""
        if not self.phase1_collector:
            logger.warning("Base data collector not available")
            return None
        
        class EnhancedTenderDataCollector(TenderDataCollector):
            def __init__(self, integration_manager):
                super().__init__()
                self.integration_manager = integration_manager
            
            def process_export_records(self, records_data):
                """Enhanced processing with automatic classification"""
                # Process records normally
                result = super().process_export_records(records_data)
                
                # Auto-classify new records
                if (self.integration_manager.enable_auto_classification and 
                    result.get('new_records', 0) > 0):
                    
                    classification_result = self.integration_manager._classify_recent_records(hours_back=1)
                    result['classification_result'] = classification_result
                
                return result
        
        try:
            enhanced_collector = EnhancedTenderDataCollector(self)
            logger.info("✅ Enhanced data collector created with automatic classification")
            return enhanced_collector
        except Exception as e:
            logger.error(f"Failed to create enhanced data collector: {e}")
            return None

def main():
    """Test Phase 1 integration system"""
    print("🎯 UK Tender Monitor - Phase 1 Integration Test")
    print("="*60)
    
    # Initialize integration manager
    print("\n1️⃣ Initializing Phase 1 integration manager...")
    integration = Phase1IntegrationManager(enable_auto_classification=True)
    
    success = integration.initialize_components()
    if not success:
        print("❌ Integration initialization failed")
        return
    
    print("✅ Integration components initialized successfully")
    
    # Get integration status
    print("\n2️⃣ Checking integration status...")
    status = integration.get_integration_status()
    
    print(f"Database status: {status['database_status']}")
    print(f"Classification coverage: {status['coverage_stats']['classification_coverage_percent']}%")
    print(f"Total tenders: {status['coverage_stats']['total_tenders']}")
    print(f"Classified tenders: {status['coverage_stats']['classified_tenders']}")
    
    # Test component integration
    print("\n3️⃣ Testing component integration...")
    collector_integrated = integration.integrate_with_data_collector()
    monitor_integrated = integration.integrate_with_monitor()
    
    print(f"Data collector integration: {'✅ Success' if collector_integrated else '⚠️ Skipped'}")
    print(f"Monitor integration: {'✅ Success' if monitor_integrated else '⚠️ Skipped'}")
    
    # Test classification of unclassified tenders
    print("\n4️⃣ Testing classification of unclassified tenders...")
    classification_result = integration.classify_all_unclassified_tenders()
    
    print(f"Tenders processed: {classification_result['processed']}")
    print(f"Successful classifications: {classification_result['successful']}")
    print(f"Failed classifications: {classification_result['failed']}")
    
    if classification_result.get('batch_count'):
        print(f"Processed in {classification_result['batch_count']} batches")
    
    # Final status
    print("\n5️⃣ Final integration status...")
    final_status = integration.get_integration_status()
    print(f"Updated classification coverage: {final_status['coverage_stats']['classification_coverage_percent']}%")
    
    print("\n✅ Phase 1 Integration test completed!")

if __name__ == "__main__":
    main()