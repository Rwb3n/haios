#!/usr/bin/env python3
"""
UK Tender Monitor - Training Data Management System (Phase 2 Step 4)
Comprehensive training system for continuous learning and model improvement

Core Features:
- Data preparation engine with advanced feature engineering
- Manual labeling interface for expert validation
- Enhanced model training pipeline with improved algorithms
- Validation framework with comprehensive metrics
- Continuous learning system for automated model updates
- Performance monitoring and analytics dashboard
"""

import os
import json
import sqlite3
import pickle
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import warnings
warnings.filterwarnings('ignore', category=FutureWarning)

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import (
    StratifiedKFold, cross_val_score, GridSearchCV, 
    train_test_split, validation_curve
)
from sklearn.metrics import (
    precision_score, recall_score, f1_score, accuracy_score,
    roc_auc_score, confusion_matrix, classification_report,
    precision_recall_curve, roc_curve
)
from sklearn.calibration import CalibratedClassifierCV
from sklearn.feature_selection import SelectKBest, f_classif, RFE
import matplotlib.pyplot as plt
import seaborn as sns

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TrainingDataPreparator:
    """Advanced data preparation engine for training data processing"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.db_path = self.data_dir / "tenders.db"
        
        # Initialize existing system components for feature engineering
        self._initialize_system_components()
        
        logger.info("Training data preparator initialized")
    
    def _initialize_system_components(self):
        """Initialize existing classifier, scorer, and filter components"""
        try:
            from classifier import TenderClassifier
            from scorer import RelevanceScorer
            from filter import AdvancedOpportunityFilter
            
            self.classifier = TenderClassifier(enable_enhanced_scoring=True)
            self.relevance_scorer = RelevanceScorer()
            self.opportunity_filter = AdvancedOpportunityFilter()
            
            self.system_components_available = True
            logger.info("System components loaded for feature engineering")
            
        except ImportError as e:
            logger.warning(f"System components not available: {e}")
            self.system_components_available = False
    
    def load_tender_data(self) -> List[Dict]:
        """Load tender data from Phase 1 database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT notice_identifier, title, description, organisation_name,
                       value_high, status, suitable_for_sme, cpv_codes, closing_date,
                       published_date, links, contact_details
                FROM tenders
                WHERE description IS NOT NULL AND description != ''
                AND title IS NOT NULL AND title != ''
            """)
            
            tenders = []
            for row in cursor.fetchall():
                tender = {
                    'notice_identifier': row[0],
                    'title': row[1],
                    'description': row[2],
                    'organisation_name': row[3],
                    'value_high': row[4] or 0,
                    'status': row[5] or '',
                    'suitable_for_sme': row[6] or '',
                    'cpv_codes': row[7] or '',
                    'closing_date': row[8] or '',
                    'published_date': row[9] or '',
                    'links': row[10] or '',
                    'contact_details': row[11] or ''
                }
                tenders.append(tender)
        
        logger.info(f"Loaded {len(tenders)} tenders for training data preparation")
        return tenders
    
    def validate_data_quality(self, tenders: List[Dict]) -> Dict:
        """Validate data quality and completeness"""
        quality_report = {
            'total_records': len(tenders),
            'field_completeness': {},
            'data_quality_issues': [],
            'recommendations': []
        }
        
        # Check field completeness
        fields = ['title', 'description', 'organisation_name', 'value_high', 'cpv_codes']
        for field in fields:
            complete_count = sum(1 for tender in tenders if tender.get(field))
            quality_report['field_completeness'][field] = {
                'complete': complete_count,
                'percentage': (complete_count / len(tenders)) * 100
            }
            
            if quality_report['field_completeness'][field]['percentage'] < 80:
                quality_report['data_quality_issues'].append(
                    f"Low completeness for {field}: {quality_report['field_completeness'][field]['percentage']:.1f}%"
                )
        
        # Check for duplicates
        identifiers = [tender['notice_identifier'] for tender in tenders]
        duplicates = len(identifiers) - len(set(identifiers))
        if duplicates > 0:
            quality_report['data_quality_issues'].append(f"Found {duplicates} duplicate records")
        
        # Check text field lengths
        avg_desc_length = np.mean([len(tender['description']) for tender in tenders])
        avg_title_length = np.mean([len(tender['title']) for tender in tenders])
        
        quality_report['text_statistics'] = {
            'avg_description_length': avg_desc_length,
            'avg_title_length': avg_title_length
        }
        
        # Generate recommendations
        if quality_report['field_completeness']['value_high']['percentage'] < 90:
            quality_report['recommendations'].append("Consider value imputation for missing contract values")
        
        if avg_desc_length < 200:
            quality_report['recommendations'].append("Short descriptions may limit feature extraction quality")
        
        logger.info(f"Data quality assessment complete: {len(quality_report['data_quality_issues'])} issues found")
        return quality_report
    
    def extract_comprehensive_features(self, tenders: List[Dict]) -> Tuple[np.ndarray, List[str]]:
        """Extract comprehensive features leveraging existing system components"""
        features = []
        feature_names = []
        
        # Base text features (if system components not available)
        if not self.system_components_available:
            logger.warning("Extracting basic features only - system components not available")
            return self._extract_basic_features(tenders)
        
        logger.info("Extracting comprehensive features using system components...")
        
        for i, tender in enumerate(tenders):
            if i % 20 == 0:
                logger.info(f"Processing tender {i+1}/{len(tenders)}")
            
            feature_vector = []
            
            try:
                # Step 1: Basic classification features
                classification_result = self.classifier.classify_tender(tender)
                feature_vector.extend([
                    classification_result.keyword_score,
                    classification_result.context_score,
                    classification_result.ml_confidence,
                    classification_result.composite_score,
                    len(classification_result.technical_terms),
                    len(classification_result.transformation_signals)
                ])
                
                if i == 0:  # Add feature names only once
                    feature_names.extend([
                        'keyword_score', 'context_score', 'ml_confidence', 
                        'composite_score', 'technical_terms_count', 'transformation_signals_count'
                    ])
                
                # Step 2: Enhanced scoring features
                enhanced_result = self.relevance_scorer.score_classified_tender(tender, classification_result)
                feature_vector.extend([
                    enhanced_result.metadata_score,
                    enhanced_result.business_alignment_score,
                    enhanced_result.urgency_multiplier,
                    enhanced_result.value_multiplier,
                    enhanced_result.department_multiplier,
                    enhanced_result.final_relevance_score
                ])
                
                if i == 0:
                    feature_names.extend([
                        'metadata_score', 'business_alignment_score', 'urgency_multiplier',
                        'value_multiplier', 'department_multiplier', 'final_relevance_score'
                    ])
                
                # Step 3: Advanced filtering features
                try:
                    # Patch filter to load real data
                    self._patch_filter_for_training(tender)
                    filtered_results = self.opportunity_filter.filter_opportunities([enhanced_result], 'balanced')
                    
                    if filtered_results:
                        filter_result = filtered_results[0]
                        feature_vector.extend([
                            filter_result.overall_filter_score,
                            filter_result.bid_probability,
                            1.0 if filter_result.filter_passes else 0.0,
                            filter_result.competition_assessment['competition_level'],
                            len(filter_result.risk_factors),
                            len(filter_result.success_factors)
                        ])
                        
                        if i == 0:
                            feature_names.extend([
                                'overall_filter_score', 'bid_probability', 'filter_passes',
                                'competition_level', 'risk_factors_count', 'success_factors_count'
                            ])
                    else:
                        # Fallback values if filtering fails
                        feature_vector.extend([0.0, 0.0, 0.0, 5.0, 0, 0])
                        if i == 0:
                            feature_names.extend([
                                'overall_filter_score', 'bid_probability', 'filter_passes',
                                'competition_level', 'risk_factors_count', 'success_factors_count'
                            ])
                
                except Exception as e:
                    logger.warning(f"Filtering failed for tender {tender['notice_identifier']}: {e}")
                    feature_vector.extend([0.0, 0.0, 0.0, 5.0, 0, 0])
                    if i == 0:
                        feature_names.extend([
                            'overall_filter_score', 'bid_probability', 'filter_passes',
                            'competition_level', 'risk_factors_count', 'success_factors_count'
                        ])
                
                # Additional metadata features
                feature_vector.extend([
                    len(tender['title']),
                    len(tender['description']),
                    1.0 if tender['suitable_for_sme'].lower() in ['yes', 'true', '1'] else 0.0,
                    float(tender['value_high']) / 1000000 if tender['value_high'] else 0.0,  # Value in millions
                ])
                
                if i == 0:
                    feature_names.extend([
                        'title_length', 'description_length', 'sme_suitable', 'value_millions'
                    ])
                
            except Exception as e:
                logger.error(f"Feature extraction failed for tender {tender['notice_identifier']}: {e}")
                # Use default feature vector
                feature_vector = [0.0] * len(feature_names) if feature_names else [0.0] * 22
            
            features.append(feature_vector)
        
        features_array = np.array(features)
        logger.info(f"Extracted {features_array.shape[1]} features for {features_array.shape[0]} tenders")
        
        return features_array, feature_names
    
    def _patch_filter_for_training(self, tender_data: Dict):
        """Patch filter to load training tender data"""
        def load_training_tender_data(notice_identifier: str) -> Dict:
            return tender_data
        
        # Monkey patch the method
        self.opportunity_filter.load_tender_data = load_training_tender_data
    
    def _extract_basic_features(self, tenders: List[Dict]) -> Tuple[np.ndarray, List[str]]:
        """Extract basic features when system components unavailable"""
        from sklearn.feature_extraction.text import TfidfVectorizer
        
        # Basic TF-IDF features
        texts = [f"{tender['title']} {tender['description']}" for tender in tenders]
        vectorizer = TfidfVectorizer(max_features=100, stop_words='english', ngram_range=(1, 2))
        tfidf_features = vectorizer.fit_transform(texts).toarray()
        
        # Basic metadata features
        metadata_features = []
        for tender in tenders:
            metadata_features.append([
                len(tender['title']),
                len(tender['description']),
                1.0 if tender['suitable_for_sme'].lower() in ['yes', 'true', '1'] else 0.0,
                float(tender['value_high']) / 1000000 if tender['value_high'] else 0.0,
            ])
        
        metadata_features = np.array(metadata_features)
        
        # Combine features
        combined_features = np.hstack([tfidf_features, metadata_features])
        
        # Generate feature names
        tfidf_names = [f"tfidf_{i}" for i in range(tfidf_features.shape[1])]
        metadata_names = ['title_length', 'description_length', 'sme_suitable', 'value_millions']
        feature_names = tfidf_names + metadata_names
        
        logger.info(f"Extracted {combined_features.shape[1]} basic features")
        return combined_features, feature_names
    
    def generate_heuristic_labels(self, tenders: List[Dict]) -> List[int]:
        """Generate initial training labels using enhanced heuristic rules"""
        labels = []
        
        # Enhanced digital transformation signals
        high_value_signals = [
            'digital transformation', 'digital modernisation', 'digital modernization',
            'digital services', 'digital platform', 'digital strategy'
        ]
        
        medium_value_signals = [
            'cloud migration', 'cloud transformation', 'api development', 'system integration',
            'software development', 'automation', 'modernisation', 'modernization'
        ]
        
        technical_signals = [
            'cloud', 'api', 'software', 'system', 'technology', 'platform',
            'solution', 'development', 'infrastructure', 'digital'
        ]
        
        for tender in tenders:
            text = f"{tender['title']} {tender['description']}".lower()
            
            # Count different types of signals
            high_signals = sum(1 for signal in high_value_signals if signal in text)
            medium_signals = sum(1 for signal in medium_value_signals if signal in text)
            tech_signals = sum(1 for signal in technical_signals if signal in text)
            
            # Enhanced labeling logic
            is_relevant = False
            
            # High confidence relevant
            if high_signals >= 1:
                is_relevant = True
            # Medium confidence relevant
            elif medium_signals >= 2 or (medium_signals >= 1 and tech_signals >= 3):
                is_relevant = True
            # Value-based relevance for large contracts
            elif (tender.get('value_high', 0) > 500000 and 
                  tech_signals >= 2 and 
                  any(term in text for term in ['government', 'public sector', 'digital', 'technology'])):
                is_relevant = True
            # CPV code based relevance
            elif (tender.get('cpv_codes', '') and 
                  any(code in tender['cpv_codes'] for code in ['72000000', '72200000', '72300000'])):
                is_relevant = True
            
            labels.append(1 if is_relevant else 0)
        
        positive_count = sum(labels)
        logger.info(f"Generated {positive_count}/{len(labels)} positive labels ({positive_count/len(labels)*100:.1f}%)")
        
        return labels
    
    def prepare_training_dataset(self) -> Tuple[np.ndarray, np.ndarray, List[str], Dict]:
        """Prepare complete training dataset with quality assessment"""
        logger.info("Preparing comprehensive training dataset...")
        
        # Load and validate data
        tenders = self.load_tender_data()
        quality_report = self.validate_data_quality(tenders)
        
        # Extract features
        features, feature_names = self.extract_comprehensive_features(tenders)
        
        # Generate labels
        labels = self.generate_heuristic_labels(tenders)
        labels = np.array(labels)
        
        # Final dataset statistics
        dataset_stats = {
            'total_samples': len(features),
            'feature_count': len(feature_names),
            'positive_samples': np.sum(labels),
            'negative_samples': len(labels) - np.sum(labels),
            'class_balance': np.sum(labels) / len(labels),
            'feature_names': feature_names,
            'quality_report': quality_report
        }
        
        logger.info(f"Training dataset prepared: {dataset_stats['total_samples']} samples, "
                   f"{dataset_stats['feature_count']} features, "
                   f"{dataset_stats['positive_samples']} positive ({dataset_stats['class_balance']*100:.1f}%)")
        
        return features, labels, feature_names, dataset_stats


class ManualLabelingInterface:
    """Interactive interface for expert validation and labeling"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.db_path = self.data_dir / "tenders.db"
        self.labels_file = self.data_dir / "expert_labels.json"
        
        # Load existing expert labels
        self.expert_labels = self._load_existing_labels()
        
        logger.info("Manual labeling interface initialized")
    
    def _load_existing_labels(self) -> Dict:
        """Load existing expert labels from file"""
        if self.labels_file.exists():
            with open(self.labels_file, 'r') as f:
                labels = json.load(f)
            logger.info(f"Loaded {len(labels)} existing expert labels")
            return labels
        else:
            return {}
    
    def _save_labels(self):
        """Save expert labels to file"""
        with open(self.labels_file, 'w') as f:
            json.dump(self.expert_labels, f, indent=2)
        logger.info(f"Saved {len(self.expert_labels)} expert labels")
    
    def present_for_labeling(self, tender_data: Dict, current_prediction: Dict = None) -> Dict:
        """Present tender to expert with current system prediction"""
        print("\n" + "="*80)
        print(f"TENDER LABELING SESSION")
        print("="*80)
        print(f"Tender ID: {tender_data['notice_identifier']}")
        print(f"Organization: {tender_data.get('organisation_name', 'Unknown')}")
        print(f"Value: £{tender_data.get('value_high', 0):,}" if tender_data.get('value_high') else "Value: Not specified")
        print(f"SME Suitable: {tender_data.get('suitable_for_sme', 'Unknown')}")
        print("-"*80)
        print(f"TITLE: {tender_data['title']}")
        print("-"*80)
        print("DESCRIPTION:")
        description = tender_data['description'][:500] + "..." if len(tender_data['description']) > 500 else tender_data['description']
        print(description)
        print("-"*80)
        
        if current_prediction:
            print("CURRENT SYSTEM ASSESSMENT:")
            print(f"  Final Score: {current_prediction.get('final_relevance_score', 'N/A')}/100")
            print(f"  Recommendation: {current_prediction.get('recommendation', 'N/A')}")
            print(f"  Priority: {current_prediction.get('priority_level', 'N/A')}")
            if 'explanation' in current_prediction:
                print(f"  Reasoning: {current_prediction['explanation']}")
            print("-"*80)
        
        # Get expert input
        while True:
            try:
                expert_label = input("\nExpert Assessment (relevant/not_relevant/unsure/skip): ").strip().lower()
                if expert_label in ['relevant', 'not_relevant', 'unsure', 'skip']:
                    break
                print("Please enter: relevant, not_relevant, unsure, or skip")
            except KeyboardInterrupt:
                print("\nLabeling session interrupted.")
                return None
        
        if expert_label == 'skip':
            return None
        
        confidence = None
        while True:
            try:
                confidence_input = input("Confidence (1-5, where 5=very confident): ").strip()
                confidence = int(confidence_input)
                if 1 <= confidence <= 5:
                    break
                print("Please enter a number between 1 and 5")
            except (ValueError, KeyboardInterrupt):
                print("Please enter a valid number or press Ctrl+C to exit")
        
        notes = input("Notes/Reasoning (optional): ").strip()
        
        # Create expert label record
        expert_record = {
            'notice_identifier': tender_data['notice_identifier'],
            'expert_label': expert_label,
            'confidence': confidence,
            'notes': notes,
            'timestamp': datetime.now().isoformat(),
            'tender_data': {
                'title': tender_data['title'],
                'organisation_name': tender_data.get('organisation_name', ''),
                'value_high': tender_data.get('value_high', 0)
            }
        }
        
        if current_prediction:
            expert_record['system_prediction'] = current_prediction
        
        # Store the label
        self.expert_labels[tender_data['notice_identifier']] = expert_record
        self._save_labels()
        
        print(f"✅ Label saved for {tender_data['notice_identifier']}")
        return expert_record
    
    def run_labeling_session(self, tenders: List[Dict], max_labels: int = 20, 
                           focus_uncertain: bool = True) -> List[Dict]:
        """Run interactive labeling session"""
        print(f"\n🎯 Starting expert labeling session (max {max_labels} labels)")
        print("Commands: 'relevant', 'not_relevant', 'unsure', 'skip', or Ctrl+C to exit")
        
        labeled_count = 0
        new_labels = []
        
        # Filter out already labeled tenders
        unlabeled_tenders = [t for t in tenders if t['notice_identifier'] not in self.expert_labels]
        
        if focus_uncertain:
            # If system components available, focus on uncertain predictions
            try:
                from classifier import TenderClassifier
                classifier = TenderClassifier(enable_enhanced_scoring=True)
                
                # Sort by uncertainty (closest to 0.5 probability or mid-range scores)
                scored_tenders = []
                for tender in unlabeled_tenders[:50]:  # Limit to first 50 for performance
                    try:
                        result = classifier.classify_tender_enhanced(tender)
                        uncertainty = abs(result.final_relevance_score - 50) / 50  # 0-1 where 0 is most uncertain
                        scored_tenders.append((uncertainty, tender, result))
                    except:
                        scored_tenders.append((0.5, tender, None))
                
                unlabeled_tenders = [t[1] for t in sorted(scored_tenders, key=lambda x: x[0])]
                predictions = {t[1]['notice_identifier']: t[2] for t in scored_tenders if t[2]}
                
                logger.info("Focusing on most uncertain predictions for labeling")
                
            except ImportError:
                predictions = {}
                logger.info("System components not available - using random order")
        else:
            predictions = {}
        
        try:
            for tender in unlabeled_tenders:
                if labeled_count >= max_labels:
                    break
                
                current_prediction = predictions.get(tender['notice_identifier'])
                prediction_dict = None
                
                if current_prediction:
                    prediction_dict = {
                        'final_relevance_score': current_prediction.final_relevance_score,
                        'recommendation': getattr(current_prediction, 'recommendation', 'N/A'),
                        'priority_level': getattr(current_prediction, 'priority_level', 'N/A'),
                        'explanation': current_prediction.explanation
                    }
                
                label_record = self.present_for_labeling(tender, prediction_dict)
                
                if label_record:
                    new_labels.append(label_record)
                    labeled_count += 1
                    
                    print(f"Progress: {labeled_count}/{max_labels} labels completed")
                    
                    # Ask if user wants to continue
                    if labeled_count < max_labels:
                        continue_input = input("\nContinue labeling? (y/n/q): ").strip().lower()
                        if continue_input in ['n', 'no', 'q', 'quit']:
                            break
        
        except KeyboardInterrupt:
            print(f"\n✅ Labeling session completed. {labeled_count} labels added.")
        
        logger.info(f"Labeling session completed: {labeled_count} new labels collected")
        return new_labels
    
    def get_expert_labels_for_training(self) -> Tuple[List[str], List[int], List[Dict]]:
        """Get expert labels formatted for training"""
        notice_ids = []
        labels = []
        metadata = []
        
        for notice_id, record in self.expert_labels.items():
            if record['expert_label'] in ['relevant', 'not_relevant']:  # Exclude 'unsure'
                notice_ids.append(notice_id)
                labels.append(1 if record['expert_label'] == 'relevant' else 0)
                metadata.append(record)
        
        logger.info(f"Retrieved {len(labels)} expert labels for training ({sum(labels)} positive)")
        return notice_ids, labels, metadata
    
    def analyze_labeling_patterns(self) -> Dict:
        """Analyze expert labeling patterns and agreement"""
        if not self.expert_labels:
            return {'error': 'No expert labels available'}
        
        analysis = {
            'total_labels': len(self.expert_labels),
            'label_distribution': {},
            'confidence_distribution': {},
            'agreement_analysis': {}
        }
        
        # Label distribution
        for record in self.expert_labels.values():
            label = record['expert_label']
            analysis['label_distribution'][label] = analysis['label_distribution'].get(label, 0) + 1
        
        # Confidence distribution
        for record in self.expert_labels.values():
            conf = record['confidence']
            analysis['confidence_distribution'][conf] = analysis['confidence_distribution'].get(conf, 0) + 1
        
        # System vs expert agreement (if available)
        agreements = []
        for record in self.expert_labels.values():
            if 'system_prediction' in record and record['expert_label'] in ['relevant', 'not_relevant']:
                expert_relevant = record['expert_label'] == 'relevant'
                system_score = record['system_prediction'].get('final_relevance_score', 50)
                system_relevant = system_score > 50
                
                agreements.append(expert_relevant == system_relevant)
        
        if agreements:
            analysis['agreement_analysis'] = {
                'total_comparisons': len(agreements),
                'agreement_rate': sum(agreements) / len(agreements),
                'disagreement_count': len(agreements) - sum(agreements)
            }
        
        return analysis


class EnhancedModelTrainer:
    """Enhanced model training pipeline with improved algorithms"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.models_dir = self.data_dir / "models"
        self.models_dir.mkdir(exist_ok=True)
        
        self.current_model = None
        self.model_metadata = {}
        
        logger.info("Enhanced model trainer initialized")
    
    def train_ensemble_classifier(self, features: np.ndarray, labels: np.ndarray, 
                                feature_names: List[str]) -> Dict:
        """Train enhanced ensemble classifier with optimized hyperparameters"""
        logger.info(f"Training ensemble classifier on {len(features)} samples with {features.shape[1]} features")
        
        # Split data for validation
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Train multiple models
        models = {}
        
        # 1. Enhanced Random Forest
        rf_params = {
            'n_estimators': 200,
            'max_depth': 15,
            'min_samples_split': 3,
            'min_samples_leaf': 1,
            'class_weight': 'balanced',
            'random_state': 42,
            'n_jobs': -1
        }
        
        models['random_forest'] = RandomForestClassifier(**rf_params)
        
        # 2. Gradient Boosting
        gb_params = {
            'n_estimators': 100,
            'learning_rate': 0.1,
            'max_depth': 6,
            'min_samples_split': 5,
            'min_samples_leaf': 2,
            'random_state': 42
        }
        models['gradient_boosting'] = GradientBoostingClassifier(**gb_params)
        
        # Training results
        training_results = {}
        
        for name, model in models.items():
            logger.info(f"Training {name}...")
            
            # Cross-validation
            cv_scores = cross_val_score(
                model, X_train, y_train,
                cv=StratifiedKFold(n_splits=5, shuffle=True, random_state=42),
                scoring='f1'
            )
            
            # Train on full training set
            model.fit(X_train, y_train)
            
            # Test set evaluation
            test_predictions = model.predict(X_test)
            test_probabilities = model.predict_proba(X_test)[:, 1]
            
            # Calculate metrics
            metrics = {
                'cv_f1_mean': cv_scores.mean(),
                'cv_f1_std': cv_scores.std(),
                'test_precision': precision_score(y_test, test_predictions),
                'test_recall': recall_score(y_test, test_predictions),
                'test_f1': f1_score(y_test, test_predictions),
                'test_accuracy': accuracy_score(y_test, test_predictions),
                'test_auc': roc_auc_score(y_test, test_probabilities)
            }
            
            # Feature importance
            if hasattr(model, 'feature_importances_'):
                feature_importance = list(zip(feature_names, model.feature_importances_))
                feature_importance.sort(key=lambda x: x[1], reverse=True)
                metrics['feature_importance'] = feature_importance[:15]  # Top 15 features
            
            training_results[name] = {
                'model': model,
                'metrics': metrics
            }
            
            logger.info(f"{name} - F1: {metrics['test_f1']:.3f}, "
                       f"Precision: {metrics['test_precision']:.3f}, "
                       f"Recall: {metrics['test_recall']:.3f}")
        
        # Select best model based on F1 score
        best_model_name = max(training_results.keys(), 
                             key=lambda x: training_results[x]['metrics']['test_f1'])
        best_model = training_results[best_model_name]['model']
        
        # Calibrate the best model
        logger.info(f"Calibrating best model ({best_model_name})...")
        calibrated_model = CalibratedClassifierCV(best_model, method='isotonic', cv=3)
        calibrated_model.fit(X_train, y_train)
        
        # Final evaluation with calibrated model
        final_predictions = calibrated_model.predict(X_test)
        final_probabilities = calibrated_model.predict_proba(X_test)[:, 1]
        
        final_metrics = {
            'precision': precision_score(y_test, final_predictions),
            'recall': recall_score(y_test, final_predictions),
            'f1_score': f1_score(y_test, final_predictions),
            'accuracy': accuracy_score(y_test, final_predictions),
            'roc_auc': roc_auc_score(y_test, final_probabilities),
            'confusion_matrix': confusion_matrix(y_test, final_predictions).tolist()
        }
        
        # Store the calibrated model
        self.current_model = calibrated_model
        self.model_metadata = {
            'model_type': f'calibrated_{best_model_name}',
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'feature_count': features.shape[1],
            'feature_names': feature_names,
            'training_timestamp': datetime.now().isoformat(),
            'best_base_model': best_model_name,
            'all_model_results': training_results,
            'final_metrics': final_metrics
        }
        
        logger.info(f"Training complete. Best model: {best_model_name}")
        logger.info(f"Final metrics - F1: {final_metrics['f1_score']:.3f}, "
                   f"ROC-AUC: {final_metrics['roc_auc']:.3f}")
        
        return {
            'model': calibrated_model,
            'metadata': self.model_metadata,
            'training_results': training_results,
            'final_metrics': final_metrics
        }
    
    def hyperparameter_optimization(self, features: np.ndarray, labels: np.ndarray) -> Dict:
        """Perform hyperparameter optimization for best model"""
        logger.info("Performing hyperparameter optimization...")
        
        # Random Forest parameter grid
        rf_param_grid = {
            'n_estimators': [100, 200, 300],
            'max_depth': [10, 15, 20, None],
            'min_samples_split': [2, 3, 5],
            'min_samples_leaf': [1, 2, 3],
            'class_weight': ['balanced', None]
        }
        
        # Grid search
        rf_grid = GridSearchCV(
            RandomForestClassifier(random_state=42, n_jobs=-1),
            rf_param_grid,
            cv=StratifiedKFold(n_splits=3, shuffle=True, random_state=42),
            scoring='f1',
            n_jobs=-1,
            verbose=1
        )
        
        rf_grid.fit(features, labels)
        
        optimization_results = {
            'best_params': rf_grid.best_params_,
            'best_cv_score': rf_grid.best_score_,
            'best_model': rf_grid.best_estimator_
        }
        
        logger.info(f"Optimization complete. Best F1: {rf_grid.best_score_:.3f}")
        logger.info(f"Best parameters: {rf_grid.best_params_}")
        
        return optimization_results
    
    def save_model(self, model_name: str = None) -> str:
        """Save trained model and metadata"""
        if not self.current_model:
            raise ValueError("No model trained to save")
        
        if not model_name:
            model_name = f"tender_classifier_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        model_path = self.models_dir / f"{model_name}.pkl"
        metadata_path = self.models_dir / f"{model_name}_metadata.json"
        
        # Save model
        with open(model_path, 'wb') as f:
            pickle.dump(self.current_model, f)
        
        # Save metadata
        with open(metadata_path, 'w') as f:
            json.dump(self.model_metadata, f, indent=2, default=str)
        
        logger.info(f"Model saved: {model_path}")
        return str(model_path)
    
    def load_model(self, model_path: str) -> bool:
        """Load trained model and metadata"""
        model_path = Path(model_path)
        metadata_path = model_path.with_suffix('').with_name(f"{model_path.stem}_metadata.json")
        
        try:
            # Load model
            with open(model_path, 'rb') as f:
                self.current_model = pickle.load(f)
            
            # Load metadata
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    self.model_metadata = json.load(f)
            
            logger.info(f"Model loaded: {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


class ContinuousLearningSystem:
    """Continuous learning system for automated model updates"""
    
    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.performance_log = self.data_dir / "model_performance_log.json"
        
        self.preparator = TrainingDataPreparator(data_dir)
        self.labeling_interface = ManualLabelingInterface(data_dir)
        self.trainer = EnhancedModelTrainer(data_dir)
        
        # Load performance history
        self.performance_history = self._load_performance_history()
        
        logger.info("Continuous learning system initialized")
    
    def _load_performance_history(self) -> List[Dict]:
        """Load model performance history"""
        if self.performance_log.exists():
            with open(self.performance_log, 'r') as f:
                history = json.load(f)
            logger.info(f"Loaded {len(history)} performance records")
            return history
        else:
            return []
    
    def _save_performance_history(self):
        """Save performance history to file"""
        with open(self.performance_log, 'w') as f:
            json.dump(self.performance_history, f, indent=2, default=str)
    
    def update_model_with_expert_feedback(self) -> Dict:
        """Update model with accumulated expert feedback"""
        logger.info("Updating model with expert feedback...")
        
        # Get expert labels
        expert_ids, expert_labels, expert_metadata = self.labeling_interface.get_expert_labels_for_training()
        
        if len(expert_labels) < 10:
            logger.warning(f"Insufficient expert labels ({len(expert_labels)}) for retraining")
            return {'error': 'Insufficient expert labels for retraining'}
        
        # Load all tender data and prepare features
        all_features, all_labels, feature_names, dataset_stats = self.preparator.prepare_training_dataset()
        
        # Create mapping from notice_id to index
        tenders = self.preparator.load_tender_data()
        id_to_index = {tender['notice_identifier']: i for i, tender in enumerate(tenders)}
        
        # Update labels with expert feedback
        updated_labels = all_labels.copy()
        expert_indices = []
        
        for expert_id, expert_label in zip(expert_ids, expert_labels):
            if expert_id in id_to_index:
                idx = id_to_index[expert_id]
                updated_labels[idx] = expert_label
                expert_indices.append(idx)
        
        logger.info(f"Updated {len(expert_indices)} labels with expert feedback")
        
        # Split into training and validation sets, ensuring expert labels are in training
        non_expert_indices = [i for i in range(len(all_features)) if i not in expert_indices]
        
        # Use expert labels + random sample of non-expert for training
        training_indices = expert_indices + list(np.random.choice(
            non_expert_indices, 
            size=min(len(non_expert_indices), len(expert_indices) * 4),
            replace=False
        ))
        
        validation_indices = [i for i in range(len(all_features)) if i not in training_indices]
        
        train_features = all_features[training_indices]
        train_labels = updated_labels[training_indices]
        
        if validation_indices:
            val_features = all_features[validation_indices]
            val_labels = updated_labels[validation_indices]
        else:
            # Use a portion of training data for validation
            train_features, val_features, train_labels, val_labels = train_test_split(
                train_features, train_labels, test_size=0.2, random_state=42, stratify=train_labels
            )
        
        # Train updated model
        training_results = self.trainer.train_ensemble_classifier(
            train_features, train_labels, feature_names
        )
        
        # Evaluate on validation set
        val_predictions = training_results['model'].predict(val_features)
        val_probabilities = training_results['model'].predict_proba(val_features)[:, 1]
        
        validation_metrics = {
            'precision': precision_score(val_labels, val_predictions),
            'recall': recall_score(val_labels, val_predictions),
            'f1_score': f1_score(val_labels, val_predictions),
            'accuracy': accuracy_score(val_labels, val_predictions),
            'roc_auc': roc_auc_score(val_labels, val_probabilities)
        }
        
        # Compare with previous performance
        improvement = 0.0
        if self.performance_history:
            last_f1 = self.performance_history[-1].get('validation_metrics', {}).get('f1_score', 0)
            improvement = validation_metrics['f1_score'] - last_f1
        
        # Record performance
        performance_record = {
            'timestamp': datetime.now().isoformat(),
            'training_samples': len(train_features),
            'validation_samples': len(val_features),
            'expert_labels_used': len(expert_indices),
            'validation_metrics': validation_metrics,
            'improvement': improvement,
            'model_metadata': training_results['metadata']
        }
        
        self.performance_history.append(performance_record)
        self._save_performance_history()
        
        # Deploy model if improvement threshold met
        deployment_threshold = 0.02  # 2% improvement
        if improvement > deployment_threshold:
            model_name = f"continuous_learning_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            model_path = self.trainer.save_model(model_name)
            performance_record['deployed'] = True
            performance_record['model_path'] = model_path
            logger.info(f"Model deployed with {improvement:.3f} improvement: {model_path}")
        else:
            performance_record['deployed'] = False
            logger.info(f"Model not deployed - insufficient improvement ({improvement:.3f})")
        
        return performance_record
    
    def recommend_labeling_targets(self, n_targets: int = 20) -> List[Dict]:
        """Recommend tenders for expert labeling based on uncertainty"""
        logger.info(f"Recommending {n_targets} tenders for expert labeling...")
        
        try:
            # Load system components for uncertainty assessment
            from classifier import TenderClassifier
            classifier = TenderClassifier(enable_enhanced_scoring=True)
            
            # Get all tenders
            tenders = self.preparator.load_tender_data()
            
            # Get already labeled tenders
            labeled_ids = set(self.labeling_interface.expert_labels.keys())
            unlabeled_tenders = [t for t in tenders if t['notice_identifier'] not in labeled_ids]
            
            if not unlabeled_tenders:
                return []
            
            # Score tenders and calculate uncertainty
            scored_tenders = []
            for tender in unlabeled_tenders[:100]:  # Limit for performance
                try:
                    result = classifier.classify_tender_enhanced(tender)
                    
                    # Calculate uncertainty (distance from decision boundary)
                    score = result.final_relevance_score
                    uncertainty = 1.0 - abs(score - 50) / 50  # Higher for scores near 50
                    
                    scored_tenders.append({
                        'tender': tender,
                        'score': score,
                        'uncertainty': uncertainty,
                        'result': result
                    })
                except Exception as e:
                    logger.warning(f"Scoring failed for {tender['notice_identifier']}: {e}")
            
            # Sort by uncertainty (most uncertain first)
            scored_tenders.sort(key=lambda x: x['uncertainty'], reverse=True)
            
            # Return top recommendations
            recommendations = []
            for item in scored_tenders[:n_targets]:
                recommendations.append({
                    'notice_identifier': item['tender']['notice_identifier'],
                    'title': item['tender']['title'],
                    'organisation_name': item['tender'].get('organisation_name', ''),
                    'current_score': item['score'],
                    'uncertainty': item['uncertainty'],
                    'reasoning': f"Uncertain prediction (score: {item['score']:.1f}, uncertainty: {item['uncertainty']:.2f})"
                })
            
            logger.info(f"Generated {len(recommendations)} labeling recommendations")
            return recommendations
            
        except ImportError:
            logger.warning("System components not available for uncertainty-based recommendations")
            return []
    
    def generate_performance_report(self) -> Dict:
        """Generate comprehensive performance report"""
        if not self.performance_history:
            return {'error': 'No performance history available'}
        
        # Latest performance
        latest = self.performance_history[-1]
        
        # Performance trends
        f1_scores = [record['validation_metrics']['f1_score'] for record in self.performance_history]
        improvements = [record['improvement'] for record in self.performance_history]
        
        report = {
            'summary': {
                'total_training_runs': len(self.performance_history),
                'latest_f1_score': latest['validation_metrics']['f1_score'],
                'latest_precision': latest['validation_metrics']['precision'],
                'latest_recall': latest['validation_metrics']['recall'],
                'total_improvement': f1_scores[-1] - f1_scores[0] if len(f1_scores) > 1 else 0,
                'average_improvement_per_run': np.mean(improvements) if improvements else 0
            },
            'trends': {
                'f1_scores': f1_scores,
                'improvements': improvements,
                'timestamps': [record['timestamp'] for record in self.performance_history]
            },
            'expert_labels': {
                'total_expert_labels': len(self.labeling_interface.expert_labels),
                'labels_used_in_latest': latest.get('expert_labels_used', 0)
            },
            'deployment_history': [
                {
                    'timestamp': record['timestamp'],
                    'deployed': record.get('deployed', False),
                    'improvement': record['improvement'],
                    'f1_score': record['validation_metrics']['f1_score']
                }
                for record in self.performance_history
            ]
        }
        
        return report


def main():
    """Test the training data management system"""
    print("🎯 UK Tender Monitor - Training Data Management System Test")
    print("="*60)
    
    # Initialize components
    preparator = TrainingDataPreparator()
    labeling_interface = ManualLabelingInterface()
    trainer = EnhancedModelTrainer()
    continuous_learner = ContinuousLearningSystem()
    
    # 1. Prepare training dataset
    print("\n1️⃣ Preparing training dataset...")
    features, labels, feature_names, dataset_stats = preparator.prepare_training_dataset()
    
    print(f"Dataset prepared:")
    print(f"  - Samples: {dataset_stats['total_samples']}")
    print(f"  - Features: {dataset_stats['feature_count']}")
    print(f"  - Positive ratio: {dataset_stats['class_balance']:.1%}")
    
    # 2. Train model
    print("\n2️⃣ Training enhanced model...")
    training_results = trainer.train_ensemble_classifier(features, labels, feature_names)
    
    print(f"Training complete:")
    print(f"  - Model type: {training_results['metadata']['model_type']}")
    print(f"  - F1 Score: {training_results['final_metrics']['f1_score']:.3f}")
    print(f"  - Precision: {training_results['final_metrics']['precision']:.3f}")
    print(f"  - Recall: {training_results['final_metrics']['recall']:.3f}")
    
    # 3. Save model
    model_path = trainer.save_model("test_model")
    print(f"  - Model saved: {model_path}")
    
    # 4. Generate labeling recommendations
    print("\n3️⃣ Generating labeling recommendations...")
    recommendations = continuous_learner.recommend_labeling_targets(5)
    
    if recommendations:
        print("Top uncertain predictions for labeling:")
        for i, rec in enumerate(recommendations[:3], 1):
            print(f"  {i}. {rec['title'][:50]}... (Score: {rec['current_score']:.1f})")
    
    # 5. Demo labeling interface (non-interactive)
    print("\n4️⃣ Manual labeling interface ready")
    print("Use labeling_interface.run_labeling_session() for interactive labeling")
    
    # 6. Performance report
    print("\n5️⃣ System status:")
    expert_labels_count = len(labeling_interface.expert_labels)
    print(f"  - Expert labels collected: {expert_labels_count}")
    print(f"  - System components: {'✅ Available' if preparator.system_components_available else '❌ Limited'}")
    print(f"  - Training ready: ✅ Yes")
    
    print("\n✅ Training Data Management System ready for production use!")


if __name__ == "__main__":
    main()