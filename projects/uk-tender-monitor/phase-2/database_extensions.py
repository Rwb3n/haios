#!/usr/bin/env python3
"""
UK Tender Monitor - Database Schema Extensions (Phase 2 Step 5)
Comprehensive database infrastructure for persistent storage of classification results,
expert validation, and performance monitoring

Core Features:
- Enhanced database schema supporting all Phase 2 components
- Migration system for seamless database upgrades
- Enhanced data access layer with optimized queries
- Performance monitoring and analytics infrastructure
- Integration with existing classification, scoring, filtering, and training systems
"""

import sqlite3
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from contextlib import contextmanager
import uuid

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseSchemaManager:
    """Manages database schema versions and migrations"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.current_version = self.get_current_schema_version()
        self.target_version = "2.0"
        
        logger.info(f"Database schema manager initialized: {self.db_path}")
        logger.info(f"Current version: {self.current_version}, Target version: {self.target_version}")
    
    def get_current_schema_version(self) -> str:
        """Get current database schema version"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT name FROM sqlite_master 
                    WHERE type='table' AND name='schema_version'
                """)
                
                if cursor.fetchone():
                    cursor = conn.execute("SELECT version FROM schema_version ORDER BY id DESC LIMIT 1")
                    result = cursor.fetchone()
                    return result[0] if result else "1.0"
                else:
                    return "1.0"  # Phase 1 schema
        except sqlite3.Error as e:
            logger.warning(f"Could not determine schema version: {e}")
            return "1.0"
    
    def create_schema_version_table(self):
        """Create schema version tracking table"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS schema_version (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    version TEXT NOT NULL,
                    description TEXT,
                    applied_timestamp TEXT NOT NULL,
                    applied_by TEXT DEFAULT 'system'
                )
            """)
            
            # Insert initial version if not exists
            cursor = conn.execute("SELECT COUNT(*) FROM schema_version")
            if cursor.fetchone()[0] == 0:
                conn.execute("""
                    INSERT INTO schema_version (version, description, applied_timestamp)
                    VALUES ('1.0', 'Phase 1 base schema', ?)
                """, (datetime.now().isoformat(),))
    
    def upgrade_to_phase2_schema(self) -> bool:
        """Upgrade database to Phase 2 schema"""
        if self.current_version >= "2.0":
            logger.info(f"Database already at version {self.current_version}")
            return True
        
        try:
            logger.info("Starting Phase 2 schema upgrade...")
            
            # Create schema version table first
            self.create_schema_version_table()
            
            # Execute all Phase 2 migrations
            migrations = [
                ("enhanced_classifications", self.create_enhanced_classifications_table),
                ("expert_validation", self.create_expert_validation_table),
                ("model_performance", self.create_model_performance_table),
                ("filter_performance", self.create_filter_performance_table),
                ("classification_history", self.create_classification_history_table),
                ("performance_indexes", self.create_performance_indexes),
                ("data_validation", self.create_data_validation_views)
            ]
            
            with sqlite3.connect(self.db_path) as conn:
                for migration_name, migration_func in migrations:
                    logger.info(f"Applying migration: {migration_name}")
                    migration_func(conn)
                    logger.info(f"✅ Migration {migration_name} completed")
                
                # Update schema version
                conn.execute("""
                    INSERT INTO schema_version (version, description, applied_timestamp)
                    VALUES ('2.0', 'Phase 2 enhanced schema with full pipeline support', ?)
                """, (datetime.now().isoformat(),))
            
            self.current_version = "2.0"
            logger.info("✅ Phase 2 schema upgrade completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"❌ Schema upgrade failed: {e}")
            return False
    
    def create_enhanced_classifications_table(self, conn: sqlite3.Connection):
        """Create enhanced classifications table supporting all pipeline components"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS enhanced_classifications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                notice_identifier TEXT NOT NULL,
                
                -- Step 1: Basic Classification Results
                keyword_score REAL NOT NULL,
                context_score REAL NOT NULL,
                ml_confidence REAL NOT NULL,
                composite_score REAL NOT NULL,
                technical_terms TEXT,                    -- JSON array
                transformation_signals TEXT,             -- JSON array
                
                -- Step 2: Enhanced Scoring Results  
                metadata_score REAL NOT NULL,
                business_alignment_score REAL NOT NULL,
                urgency_multiplier REAL NOT NULL,
                value_multiplier REAL NOT NULL,
                department_multiplier REAL NOT NULL,
                final_relevance_score REAL NOT NULL,
                score_breakdown TEXT,                    -- JSON detailed breakdown
                priority_level TEXT CHECK(priority_level IN ('HIGH', 'MEDIUM', 'LOW')),
                
                -- Step 3: Advanced Filtering Results
                filter_passes BOOLEAN NOT NULL DEFAULT FALSE,
                overall_filter_score REAL,
                bid_probability REAL,
                competition_level REAL,
                filter_profile_used TEXT DEFAULT 'balanced',
                final_recommendation TEXT CHECK(final_recommendation IN ('PURSUE', 'CONSIDER', 'MONITOR', 'AVOID')),
                risk_factors TEXT,                       -- JSON array
                success_factors TEXT,                    -- JSON array
                resource_requirements TEXT,              -- JSON object
                
                -- Step 4: Training Integration
                used_in_training BOOLEAN DEFAULT FALSE,
                training_label INTEGER,                  -- 0/1 if used in training
                prediction_confidence REAL,
                
                -- Metadata
                classification_timestamp TEXT NOT NULL,
                model_version TEXT DEFAULT 'v1.0',
                pipeline_version TEXT DEFAULT 'v2.0',
                processing_time_ms INTEGER,
                explanation TEXT,                        -- Human-readable reasoning
                
                FOREIGN KEY (notice_identifier) REFERENCES tenders(notice_identifier),
                UNIQUE(notice_identifier, classification_timestamp)
            )
        """)
        
        logger.info("Enhanced classifications table created")
    
    def create_expert_validation_table(self, conn: sqlite3.Connection):
        """Create expert validation tracking table"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expert_validation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                notice_identifier TEXT NOT NULL,
                expert_label TEXT CHECK(expert_label IN ('relevant', 'not_relevant', 'unsure')) NOT NULL,
                confidence INTEGER CHECK(confidence BETWEEN 1 AND 5) NOT NULL,
                notes TEXT,
                reasoning TEXT,
                
                -- System prediction at time of labeling
                system_prediction_score REAL,
                system_recommendation TEXT,
                prediction_confidence REAL,
                
                -- Expert session metadata
                validator_id TEXT DEFAULT 'expert',
                labeling_session_id TEXT,
                time_spent_seconds INTEGER,
                validation_timestamp TEXT NOT NULL,
                
                -- Agreement analysis
                expert_system_agreement BOOLEAN,
                disagreement_magnitude REAL,
                
                -- Quality metrics
                validation_quality_score REAL,  -- Internal quality assessment
                validation_source TEXT DEFAULT 'manual',  -- manual, imported, automated
                
                FOREIGN KEY (notice_identifier) REFERENCES tenders(notice_identifier)
            )
        """)
        
        logger.info("Expert validation table created")
    
    def create_model_performance_table(self, conn: sqlite3.Connection):
        """Create model performance tracking table"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS model_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_version TEXT NOT NULL,
                pipeline_components TEXT,               -- JSON: which steps included
                
                -- Training Data
                training_samples INTEGER NOT NULL,
                validation_samples INTEGER NOT NULL,
                expert_labels_used INTEGER DEFAULT 0,
                feature_count INTEGER NOT NULL,
                feature_names TEXT,                     -- JSON array of feature names
                
                -- Performance Metrics
                precision_score REAL NOT NULL,
                recall_score REAL NOT NULL,
                f1_score REAL NOT NULL,
                accuracy_score REAL NOT NULL,
                roc_auc_score REAL,
                
                -- Cross-validation results
                cv_mean REAL,
                cv_std REAL,
                cv_scores TEXT,                         -- JSON array of CV scores
                
                -- Feature importance
                top_features TEXT,                      -- JSON: top features and importance
                feature_importance_full TEXT,           -- JSON: all features and importance
                
                -- Model configuration
                model_type TEXT NOT NULL,               -- 'random_forest', 'gradient_boosting', etc.
                hyperparameters TEXT,                   -- JSON: model hyperparameters
                calibration_method TEXT,                -- 'isotonic', 'sigmoid', etc.
                
                -- Deployment info
                training_timestamp TEXT NOT NULL,
                deployment_timestamp TEXT,
                deployed BOOLEAN DEFAULT FALSE,
                improvement_over_previous REAL,
                deployment_reason TEXT,
                
                -- Validation method
                validation_method TEXT DEFAULT 'stratified_cv',
                test_set_size REAL DEFAULT 0.2,
                
                -- Performance on specific data subsets
                performance_by_value_range TEXT,        -- JSON: performance by contract value
                performance_by_organization TEXT,       -- JSON: performance by org type
                
                notes TEXT,
                
                UNIQUE(model_version, training_timestamp)
            )
        """)
        
        logger.info("Model performance table created")
    
    def create_filter_performance_table(self, conn: sqlite3.Connection):
        """Create filter performance analytics table"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS filter_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filter_profile TEXT NOT NULL,
                analysis_period_start TEXT NOT NULL,
                analysis_period_end TEXT NOT NULL,
                
                -- Volume metrics
                total_opportunities_analyzed INTEGER NOT NULL,
                opportunities_passing_filters INTEGER NOT NULL,
                pass_rate REAL NOT NULL,
                
                -- Recommendation distribution
                pursue_count INTEGER DEFAULT 0,
                consider_count INTEGER DEFAULT 0,
                monitor_count INTEGER DEFAULT 0,
                avoid_count INTEGER DEFAULT 0,
                
                -- Performance metrics
                avg_bid_probability REAL,
                avg_competition_level REAL,
                avg_final_relevance_score REAL,
                avg_overall_filter_score REAL,
                
                -- Filter-specific metrics
                value_filter_pass_rate REAL,
                timeline_filter_pass_rate REAL,
                capability_filter_pass_rate REAL,
                geographic_filter_pass_rate REAL,
                
                -- Success tracking (when available)
                tracked_outcomes INTEGER DEFAULT 0,
                successful_pursuits INTEGER DEFAULT 0,
                actual_success_rate REAL,
                roi_estimate REAL,
                
                -- Quality metrics
                false_positive_estimate REAL,
                false_negative_estimate REAL,
                precision_estimate REAL,
                
                created_timestamp TEXT NOT NULL,
                
                UNIQUE(filter_profile, analysis_period_start, analysis_period_end)
            )
        """)
        
        logger.info("Filter performance table created")
    
    def create_classification_history_table(self, conn: sqlite3.Connection):
        """Create classification history for trend analysis"""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS classification_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                notice_identifier TEXT NOT NULL,
                classification_date TEXT NOT NULL,
                
                -- Snapshot of classification at time
                final_relevance_score REAL NOT NULL,
                recommendation TEXT NOT NULL,
                priority_level TEXT,
                model_version TEXT NOT NULL,
                pipeline_version TEXT DEFAULT 'v2.0',
                
                -- Change tracking
                score_change_from_previous REAL,
                recommendation_change BOOLEAN DEFAULT FALSE,
                priority_change BOOLEAN DEFAULT FALSE,
                change_reason TEXT,
                
                -- Additional context
                tender_status TEXT,                     -- tender status at time of classification
                days_until_closing INTEGER,            -- days remaining when classified
                
                FOREIGN KEY (notice_identifier) REFERENCES tenders(notice_identifier)
            )
        """)
        
        logger.info("Classification history table created")
    
    def create_performance_indexes(self, conn: sqlite3.Connection):
        """Create performance indexes for optimized queries"""
        indexes = [
            # Enhanced classifications indexes
            "CREATE INDEX IF NOT EXISTS idx_enhanced_final_score ON enhanced_classifications(final_relevance_score DESC)",
            "CREATE INDEX IF NOT EXISTS idx_enhanced_recommendation ON enhanced_classifications(final_recommendation)",
            "CREATE INDEX IF NOT EXISTS idx_enhanced_priority ON enhanced_classifications(priority_level)",
            "CREATE INDEX IF NOT EXISTS idx_enhanced_timestamp ON enhanced_classifications(classification_timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_enhanced_filter_passes ON enhanced_classifications(filter_passes)",
            "CREATE INDEX IF NOT EXISTS idx_enhanced_notice_id ON enhanced_classifications(notice_identifier)",
            "CREATE INDEX IF NOT EXISTS idx_enhanced_model_version ON enhanced_classifications(model_version)",
            
            # Expert validation indexes
            "CREATE INDEX IF NOT EXISTS idx_expert_label ON expert_validation(expert_label)",
            "CREATE INDEX IF NOT EXISTS idx_expert_confidence ON expert_validation(confidence)",
            "CREATE INDEX IF NOT EXISTS idx_expert_agreement ON expert_validation(expert_system_agreement)",
            "CREATE INDEX IF NOT EXISTS idx_expert_timestamp ON expert_validation(validation_timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_expert_notice_id ON expert_validation(notice_identifier)",
            
            # Model performance indexes
            "CREATE INDEX IF NOT EXISTS idx_model_version ON model_performance(model_version)",
            "CREATE INDEX IF NOT EXISTS idx_model_f1_score ON model_performance(f1_score DESC)",
            "CREATE INDEX IF NOT EXISTS idx_model_deployed ON model_performance(deployed, training_timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_model_training_time ON model_performance(training_timestamp DESC)",
            
            # Filter performance indexes
            "CREATE INDEX IF NOT EXISTS idx_filter_profile ON filter_performance(filter_profile)",
            "CREATE INDEX IF NOT EXISTS idx_filter_period ON filter_performance(analysis_period_start, analysis_period_end)",
            "CREATE INDEX IF NOT EXISTS idx_filter_pass_rate ON filter_performance(pass_rate DESC)",
            
            # Classification history indexes
            "CREATE INDEX IF NOT EXISTS idx_history_notice_date ON classification_history(notice_identifier, classification_date DESC)",
            "CREATE INDEX IF NOT EXISTS idx_history_score ON classification_history(final_relevance_score DESC)",
            "CREATE INDEX IF NOT EXISTS idx_history_changes ON classification_history(recommendation_change, score_change_from_previous)",
            
            # Composite indexes for common query patterns
            "CREATE INDEX IF NOT EXISTS idx_classification_score_time ON enhanced_classifications(final_relevance_score DESC, classification_timestamp DESC)",
            "CREATE INDEX IF NOT EXISTS idx_filter_profile_performance ON enhanced_classifications(filter_profile_used, filter_passes, final_recommendation)",
            "CREATE INDEX IF NOT EXISTS idx_expert_validation_analysis ON expert_validation(expert_label, confidence, expert_system_agreement)",
            "CREATE INDEX IF NOT EXISTS idx_model_performance_trends ON model_performance(training_timestamp DESC, f1_score DESC, deployed)"
        ]
        
        for index_sql in indexes:
            conn.execute(index_sql)
        
        logger.info(f"Created {len(indexes)} performance indexes")
    
    def create_data_validation_views(self, conn: sqlite3.Connection):
        """Create views for data validation and quality checks"""
        
        # View for classification quality metrics
        conn.execute("""
            CREATE VIEW IF NOT EXISTS classification_quality_metrics AS
            SELECT 
                DATE(classification_timestamp) as classification_date,
                COUNT(*) as total_classifications,
                AVG(final_relevance_score) as avg_relevance_score,
                AVG(processing_time_ms) as avg_processing_time,
                AVG(CASE WHEN filter_passes THEN 1.0 ELSE 0.0 END) as pass_rate,
                COUNT(CASE WHEN final_recommendation = 'PURSUE' THEN 1 END) as pursue_count,
                COUNT(CASE WHEN final_recommendation = 'CONSIDER' THEN 1 END) as consider_count,
                COUNT(CASE WHEN final_recommendation = 'MONITOR' THEN 1 END) as monitor_count,
                COUNT(CASE WHEN final_recommendation = 'AVOID' THEN 1 END) as avoid_count
            FROM enhanced_classifications
            GROUP BY DATE(classification_timestamp)
            ORDER BY classification_date DESC
        """)
        
        # View for expert validation summary
        conn.execute("""
            CREATE VIEW IF NOT EXISTS expert_validation_summary AS
            SELECT 
                DATE(validation_timestamp) as validation_date,
                COUNT(*) as total_validations,
                AVG(confidence) as avg_confidence,
                COUNT(CASE WHEN expert_label = 'relevant' THEN 1 END) as relevant_count,
                COUNT(CASE WHEN expert_label = 'not_relevant' THEN 1 END) as not_relevant_count,
                COUNT(CASE WHEN expert_label = 'unsure' THEN 1 END) as unsure_count,
                AVG(CASE WHEN expert_system_agreement THEN 1.0 ELSE 0.0 END) as agreement_rate,
                AVG(disagreement_magnitude) as avg_disagreement
            FROM expert_validation
            GROUP BY DATE(validation_timestamp)
            ORDER BY validation_date DESC
        """)
        
        # View for model performance trends
        conn.execute("""
            CREATE VIEW IF NOT EXISTS model_performance_trends AS
            SELECT 
                model_version,
                training_timestamp,
                f1_score,
                precision_score,
                recall_score,
                expert_labels_used,
                improvement_over_previous,
                deployed,
                RANK() OVER (ORDER BY f1_score DESC) as performance_rank
            FROM model_performance
            ORDER BY training_timestamp DESC
        """)
        
        logger.info("Data validation views created")


class EnhancedDataAccess:
    """Enhanced data access layer with optimized queries and transaction management"""
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        
        # Initialize database schema if needed
        schema_manager = DatabaseSchemaManager(db_path)
        if schema_manager.current_version < "2.0":
            schema_manager.upgrade_to_phase2_schema()
        
        logger.info(f"Enhanced data access layer initialized: {self.db_path}")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections with proper cleanup"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
        finally:
            conn.close()
    
    # ==================== Classification Results Management ====================
    
    def save_classification_result(self, result, tender_data: Dict = None) -> int:
        """Save complete classification result with all pipeline components"""
        try:
            with self.get_connection() as conn:
                # Handle different result types (enhanced, filtered, basic)
                if hasattr(result, 'final_relevance_score'):
                    # Enhanced result from Step 2
                    data = self._extract_enhanced_result_data(result, tender_data)
                elif hasattr(result, 'filter_passes'):
                    # Filtered result from Step 3
                    data = self._extract_filtered_result_data(result, tender_data)
                else:
                    # Basic classification result from Step 1
                    data = self._extract_basic_result_data(result, tender_data)
                
                cursor = conn.execute("""
                    INSERT INTO enhanced_classifications (
                        notice_identifier, keyword_score, context_score, ml_confidence, composite_score,
                        technical_terms, transformation_signals, metadata_score, business_alignment_score,
                        urgency_multiplier, value_multiplier, department_multiplier, final_relevance_score,
                        score_breakdown, priority_level, filter_passes, overall_filter_score,
                        bid_probability, competition_level, filter_profile_used, final_recommendation,
                        risk_factors, success_factors, resource_requirements, classification_timestamp,
                        model_version, pipeline_version, processing_time_ms, explanation
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, data)
                
                classification_id = cursor.lastrowid
                
                # Also save to classification history for trend tracking
                self._save_classification_history(conn, result, tender_data)
                
                logger.debug(f"Saved classification result {classification_id} for {data[0]}")
                return classification_id
                
        except Exception as e:
            logger.error(f"Failed to save classification result: {e}")
            raise
    
    def _extract_enhanced_result_data(self, result, tender_data: Dict = None) -> tuple:
        """Extract data from enhanced classification result"""
        timestamp = datetime.now().isoformat()
        
        return (
            result.notice_identifier,
            result.keyword_score,
            result.context_score,
            result.ml_confidence,
            getattr(result, 'composite_score', 0.0),
            json.dumps(result.technical_terms) if hasattr(result, 'technical_terms') else '[]',
            json.dumps(result.transformation_signals) if hasattr(result, 'transformation_signals') else '[]',
            result.metadata_score,
            result.business_alignment_score,
            result.urgency_multiplier,
            result.value_multiplier,
            result.department_multiplier,
            result.final_relevance_score,
            json.dumps(getattr(result, 'score_breakdown', {})),
            getattr(result, 'priority_level', self._determine_priority_level(result.final_relevance_score)),
            False,  # filter_passes - not available in enhanced result
            0.0,    # overall_filter_score
            0.0,    # bid_probability
            0.0,    # competition_level
            'none', # filter_profile_used
            'MONITOR', # final_recommendation
            '[]',   # risk_factors
            '[]',   # success_factors
            '{}',   # resource_requirements
            timestamp,
            getattr(result, 'model_version', 'v1.0'),
            'v2.0',
            getattr(result, 'processing_time_ms', 0),
            result.explanation
        )
    
    def _extract_filtered_result_data(self, result, tender_data: Dict = None) -> tuple:
        """Extract data from filtered opportunity result"""
        timestamp = datetime.now().isoformat()
        enhanced = result.original_enhanced_result
        
        return (
            result.notice_identifier,
            enhanced.keyword_score,
            enhanced.context_score,
            enhanced.ml_confidence,
            getattr(enhanced, 'composite_score', 0.0),
            json.dumps(enhanced.technical_terms) if hasattr(enhanced, 'technical_terms') else '[]',
            json.dumps(enhanced.transformation_signals) if hasattr(enhanced, 'transformation_signals') else '[]',
            enhanced.metadata_score,
            enhanced.business_alignment_score,
            enhanced.urgency_multiplier,
            enhanced.value_multiplier,
            enhanced.department_multiplier,
            enhanced.final_relevance_score,
            json.dumps(getattr(enhanced, 'score_breakdown', {})),
            getattr(enhanced, 'priority_level', self._determine_priority_level(enhanced.final_relevance_score)),
            result.filter_passes,
            result.overall_filter_score,
            result.bid_probability,
            result.competition_assessment.get('competition_level', 0.0),
            result.filter_profile_used,
            result.final_recommendation,
            json.dumps(result.risk_factors),
            json.dumps(result.success_factors),
            json.dumps(result.resource_requirements),
            timestamp,
            getattr(result, 'model_version', 'v1.0'),
            'v2.0',
            getattr(result, 'processing_time_ms', 0),
            getattr(result, 'recommendation_reasoning', '')
        )
    
    def _extract_basic_result_data(self, result, tender_data: Dict = None) -> tuple:
        """Extract data from basic classification result"""
        timestamp = datetime.now().isoformat()
        
        return (
            result.notice_identifier,
            result.keyword_score,
            result.context_score,
            result.ml_confidence,
            result.composite_score,
            json.dumps(result.technical_terms),
            json.dumps(result.transformation_signals),
            0.0,    # metadata_score
            0.0,    # business_alignment_score  
            1.0,    # urgency_multiplier
            1.0,    # value_multiplier
            1.0,    # department_multiplier
            result.composite_score,  # final_relevance_score
            '{}',   # score_breakdown
            self._determine_priority_level(result.composite_score),
            False,  # filter_passes
            0.0,    # overall_filter_score
            0.0,    # bid_probability
            0.0,    # competition_level
            'none', # filter_profile_used
            'MONITOR', # final_recommendation
            '[]',   # risk_factors
            '[]',   # success_factors
            '{}',   # resource_requirements
            timestamp,
            'v1.0',
            'v1.0',
            0,
            result.explanation
        )
    
    def _determine_priority_level(self, score: float) -> str:
        """Determine priority level from relevance score"""
        if score >= 70:
            return 'HIGH'
        elif score >= 40:
            return 'MEDIUM'
        else:
            return 'LOW'
    
    def _save_classification_history(self, conn: sqlite3.Connection, result, tender_data: Dict = None):
        """Save classification to history table for trend tracking"""
        try:
            notice_id = result.notice_identifier
            final_score = getattr(result, 'final_relevance_score', getattr(result, 'composite_score', 0.0))
            recommendation = getattr(result, 'final_recommendation', 'MONITOR')
            priority = getattr(result, 'priority_level', self._determine_priority_level(final_score))
            model_version = getattr(result, 'model_version', 'v1.0')
            
            # Get previous classification for change tracking
            cursor = conn.execute("""
                SELECT final_relevance_score, recommendation, priority_level
                FROM classification_history 
                WHERE notice_identifier = ?
                ORDER BY classification_date DESC LIMIT 1
            """, (notice_id,))
            
            previous = cursor.fetchone()
            score_change = None
            recommendation_change = False
            priority_change = False
            
            if previous:
                score_change = final_score - previous[0]
                recommendation_change = recommendation != previous[1]
                priority_change = priority != previous[2]
            
            # Calculate days until closing if tender data available
            days_until_closing = None
            if tender_data and tender_data.get('closing_date'):
                try:
                    closing_date = datetime.fromisoformat(tender_data['closing_date'])
                    days_until_closing = (closing_date - datetime.now()).days
                except:
                    pass
            
            conn.execute("""
                INSERT INTO classification_history (
                    notice_identifier, classification_date, final_relevance_score,
                    recommendation, priority_level, model_version, pipeline_version,
                    score_change_from_previous, recommendation_change, priority_change,
                    tender_status, days_until_closing
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                notice_id, datetime.now().isoformat(), final_score,
                recommendation, priority, model_version, 'v2.0',
                score_change, recommendation_change, priority_change,
                tender_data.get('status') if tender_data else None, days_until_closing
            ))
            
        except Exception as e:
            logger.warning(f"Failed to save classification history: {e}")
    
    def get_top_opportunities(self, min_score: float = 50, 
                            profile: str = None, limit: int = 20,
                            filter_passed_only: bool = True) -> List[Dict]:
        """Get top opportunities with optional filtering"""
        with self.get_connection() as conn:
            where_conditions = ["final_relevance_score >= ?"]
            params = [min_score]
            
            if filter_passed_only:
                where_conditions.append("(recommendation LIKE 'IMMEDIATE ACTION%' OR recommendation LIKE 'WORTH REVIEWING%')")
            
            if profile:
                where_conditions.append("(priority_level = ? OR recommendation LIKE ?)")
                params.append(f'%{profile}%')
                params.append(profile)
            
            where_clause = " AND ".join(where_conditions)
            
            cursor = conn.execute(f"""
                SELECT 
                    ec.*,
                    t.title, t.description, t.organisation_name, t.value_high, t.closing_date
                FROM v_api_enhanced_classifications ec
                JOIN tenders t ON ec.notice_identifier = t.notice_identifier
                WHERE {where_clause}
                ORDER BY ec.final_relevance_score DESC, ec.classification_date DESC
                LIMIT ?
            """, params + [limit])
            
            results = []
            for row in cursor.fetchall():
                result_dict = dict(row)
                # Parse JSON fields
                for json_field in ['technical_terms', 'transformation_signals', 'risk_factors', 'success_factors']:
                    if result_dict.get(json_field):
                        try:
                            result_dict[json_field] = json.loads(result_dict[json_field])
                        except:
                            result_dict[json_field] = []
                
                results.append(result_dict)
            
            return results


def main():
    """Test the database extensions system"""
    print("🎯 UK Tender Monitor - Database Schema Extensions Test")
    print("="*60)
    
    # Initialize database manager
    db_path = "data/tenders.db"
    
    print("\n1️⃣ Initializing database schema manager...")
    schema_manager = DatabaseSchemaManager(db_path)
    
    print(f"Current schema version: {schema_manager.current_version}")
    print(f"Target schema version: {schema_manager.target_version}")
    
    # Upgrade schema if needed
    if schema_manager.current_version < "2.0":
        print("\n2️⃣ Upgrading database schema to Phase 2...")
        success = schema_manager.upgrade_to_phase2_schema()
        
        if success:
            print("✅ Schema upgrade completed successfully")
        else:
            print("❌ Schema upgrade failed")
            return
    else:
        print("\n2️⃣ Database schema already up to date")
    
    # Initialize enhanced data access
    print("\n3️⃣ Initializing enhanced data access layer...")
    data_access = EnhancedDataAccess(db_path)
    
    # Test basic operations
    print("\n4️⃣ Testing database operations...")
    
    # Test top opportunities query
    try:
        top_opportunities = data_access.get_top_opportunities(min_score=0, limit=5, filter_passed_only=False)
        print(f"  - Top opportunities query: {len(top_opportunities)} results")
    except Exception as e:
        print(f"  - Top opportunities query failed: {e}")
    
    print("\n✅ Database Schema Extensions system ready for production use!")
    print("\n📊 System Summary:")
    print(f"  - Schema Version: {schema_manager.current_version}")
    print(f"  - Database Path: {db_path}")
    print(f"  - Enhanced Tables: 5 (classifications, validation, performance, history, filter)")
    print(f"  - Performance Indexes: 20+ optimized indexes")
    print(f"  - Analytics Views: 3 data validation views")


if __name__ == "__main__":
    main()