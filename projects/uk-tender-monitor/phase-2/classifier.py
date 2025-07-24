#!/usr/bin/env python3
"""
UK Tender Monitor - NLP Classification Engine (Phase 2 Step 1)
Intelligent classification of government tenders for digital transformation relevance

Core Features:
- Multi-tier keyword analysis with weighted scoring
- NLP context processing with technical term extraction
- Machine learning pipeline with TF-IDF features
- Confidence scoring and explanation generation
"""

import re
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, NamedTuple
import logging

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import cross_val_score, train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('punkt')
    nltk.download('stopwords')

# Handle newer NLTK versions
try:
    nltk.data.find('tokenizers/punkt_tab')
except LookupError:
    try:
        nltk.download('punkt_tab')
    except:
        pass  # Fall back to punkt if punkt_tab not available

class ClassificationResult(NamedTuple):
    """Structured result from tender classification"""
    notice_identifier: str
    keyword_score: float
    context_score: float
    ml_confidence: float
    composite_score: float
    explanation: str
    technical_terms: List[str]
    transformation_signals: List[str]

class KeywordAnalyzer:
    """Multi-tier keyword analysis with weighted scoring"""
    
    def __init__(self):
        # Tier 1: Core digital transformation keywords (highest weight)
        self.tier1_keywords = {
            "digital transformation": 10,
            "digital modernisation": 9,
            "digital modernization": 9,
            "digital services": 8,
            "modernisation": 7,
            "modernization": 7,
            "digital strategy": 6,
            "digital reform": 6
        }
        
        # Tier 2: Technical implementation keywords (medium weight)
        self.tier2_keywords = {
            "cloud migration": 8,
            "cloud transformation": 7,
            "api development": 7,
            "system integration": 7,
            "digital platform": 6,
            "automation": 5,
            "workflow": 4,
            "digital infrastructure": 6,
            "software development": 5,
            "data migration": 5,
            "system modernisation": 6,
            "legacy system": 5,
            "digital solution": 4,
            "technology upgrade": 4
        }
        
        # Tier 3: Domain and context keywords (lower weight)
        self.tier3_keywords = {
            "gov.uk": 5,
            "citizen services": 4,
            "public sector technology": 4,
            "government digital service": 6,
            "gds": 5,
            "digital by default": 4,
            "user-centered design": 3,
            "agile development": 3,
            "devops": 3,
            "microservices": 3,
            "digital delivery": 4,
            "service design": 3
        }
        
        # Combine all tiers
        self.all_keywords = {
            **self.tier1_keywords,
            **self.tier2_keywords, 
            **self.tier3_keywords
        }
        
        logger.info(f"Initialized keyword analyzer with {len(self.all_keywords)} keywords")
    
    def analyze(self, title: str, description: str) -> Tuple[float, List[str]]:
        """
        Analyze title and description for keyword matches
        Returns: (weighted_score, matched_keywords)
        """
        text = f"{title} {description}".lower()
        matched_keywords = []
        total_score = 0
        
        for keyword, weight in self.all_keywords.items():
            if keyword in text:
                matched_keywords.append(keyword)
                # Count multiple occurrences with diminishing returns
                occurrences = text.count(keyword)
                keyword_score = weight * (1 + 0.5 * (occurrences - 1))
                total_score += keyword_score
        
        # Normalize score to 0-50 range (50% of total classification score)
        normalized_score = min(total_score, 50)
        
        return normalized_score, matched_keywords

class ContextProcessor:
    """NLP context analysis for technical content understanding"""
    
    def __init__(self):
        self.stemmer = PorterStemmer()
        self.stop_words = set(stopwords.words('english'))
        
        # Technical terms that signal digital transformation projects
        self.tech_terms = {
            'api', 'apis', 'microservice', 'microservices', 'cloud', 'aws', 'azure', 
            'docker', 'kubernetes', 'devops', 'ci/cd', 'automation', 'integration',
            'database', 'sql', 'nosql', 'mongodb', 'postgresql', 'mysql',
            'frontend', 'backend', 'full-stack', 'javascript', 'python', 'java',
            'react', 'angular', 'vue', 'node.js', 'django', 'spring',
            'mobile', 'ios', 'android', 'responsive', 'progressive web app',
            'security', 'authentication', 'authorization', 'encryption', 'oauth',
            'analytics', 'data science', 'machine learning', 'ai', 'artificial intelligence',
            'blockchain', 'iot', 'internet of things', 'big data', 'data warehouse'
        }
        
        # Transformation signal phrases
        self.transformation_patterns = [
            r'replac[ing]+ legacy',
            r'migrat[ing]+ from',
            r'upgrad[ing]+ system',
            r'modern[iz]+ platform',
            r'digital[iz]+ service',
            r'automat[ing]+ process',
            r'streamlin[ing]+ workflow',
            r'improv[ing]+ efficiency',
            r'reduc[ing]+ manual',
            r'enhanc[ing]+ user experience'
        ]
        
        logger.info(f"Initialized context processor with {len(self.tech_terms)} technical terms")
    
    def analyze(self, title: str, description: str) -> Tuple[float, List[str], List[str]]:
        """
        Analyze context for technical content and transformation signals
        Returns: (context_score, technical_terms_found, transformation_signals)
        """
        text = f"{title} {description}".lower()
        
        # Extract technical terms
        tech_terms_found = []
        try:
            words = word_tokenize(text)
        except LookupError:
            # Fallback to simple splitting if NLTK tokenizer fails
            words = text.lower().replace('.', ' ').replace(',', ' ').split()
        
        for word in words:
            if word in self.tech_terms:
                tech_terms_found.append(word)
        
        # Remove duplicates while preserving order
        tech_terms_found = list(dict.fromkeys(tech_terms_found))
        
        # Find transformation signals
        transformation_signals = []
        for pattern in self.transformation_patterns:
            matches = re.findall(pattern, text)
            transformation_signals.extend(matches)
        
        # Calculate context score based on technical density and transformation signals
        tech_density = len(tech_terms_found) / max(len(words), 1) * 100
        transformation_score = len(transformation_signals) * 5
        
        # Context score: weighted combination of technical density and transformation signals
        context_score = min(
            (tech_density * 2) + transformation_score,
            30  # Cap at 30 points (30% of total score)
        )
        
        return context_score, tech_terms_found, transformation_signals

class MLClassifier:
    """Machine learning classifier for tender relevance prediction"""
    
    def __init__(self, model_path: Optional[Path] = None):
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2),  # Include bigrams
            min_df=2,  # Ignore terms that appear in less than 2 documents
            max_df=0.8  # Ignore terms that appear in more than 80% of documents
        )
        
        self.classifier = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=42
        )
        
        self.is_trained = False
        self.model_version = "v1.0"
        self.feature_names = []
        
        if model_path and model_path.exists():
            self.load_model(model_path)
    
    def prepare_features(self, tenders: List[Dict]) -> np.ndarray:
        """Extract features from tender data for ML classification"""
        # Combine text fields for analysis
        texts = []
        for tender in tenders:
            combined_text = f"{tender.get('title', '')} {tender.get('description', '')}"
            texts.append(combined_text)
        
        # TF-IDF vectorization
        if not self.is_trained:
            text_features = self.vectorizer.fit_transform(texts)
        else:
            text_features = self.vectorizer.transform(texts)
        
        # Additional metadata features
        metadata_features = []
        for tender in tenders:
            features = [
                # Value-based features
                float(tender.get('value_high', 0) or 0) / 1000000,  # Value in millions
                1.0 if tender.get('value_high') else 0.0,  # Has value specified
                
                # Organization features
                1.0 if any(org in (tender.get('organisation_name', '').lower()) 
                          for org in ['nhs', 'hmrc', 'cabinet office', 'mod', 'dvla']) else 0.0,
                
                # Status features
                1.0 if tender.get('status', '').lower() == 'open' else 0.0,
                
                # SME suitability
                1.0 if tender.get('suitable_for_sme', '').lower() in ['yes', 'true', '1'] else 0.0,
                
                # Text length features
                len(tender.get('description', '')) / 1000,  # Description length in thousands of chars
                len(tender.get('title', '')) / 100,  # Title length in hundreds of chars
            ]
            metadata_features.append(features)
        
        metadata_features = np.array(metadata_features)
        
        # Combine text and metadata features
        combined_features = np.hstack([
            text_features.toarray(),
            metadata_features
        ])
        
        return combined_features
    
    def train(self, tenders: List[Dict], labels: List[int]) -> Dict:
        """
        Train the ML classifier on labeled tender data
        Returns training performance metrics
        """
        logger.info(f"Training ML classifier on {len(tenders)} samples...")
        
        # Prepare features
        features = self.prepare_features(tenders)
        labels = np.array(labels)
        
        # Train-test split for validation
        X_train, X_test, y_train, y_test = train_test_split(
            features, labels, test_size=0.2, random_state=42, stratify=labels
        )
        
        # Train classifier
        self.classifier.fit(X_train, y_train)
        self.is_trained = True
        
        # Cross-validation scores
        cv_scores = cross_val_score(self.classifier, X_train, y_train, cv=5)
        
        # Test set evaluation
        test_predictions = self.classifier.predict(X_test)
        test_probabilities = self.classifier.predict_proba(X_test)
        
        # Calculate metrics
        performance = {
            'cv_mean': cv_scores.mean(),
            'cv_std': cv_scores.std(),
            'test_accuracy': (test_predictions == y_test).mean(),
            'classification_report': classification_report(y_test, test_predictions, output_dict=True),
            'feature_importance': self.classifier.feature_importances_[:10].tolist(),  # Top 10 features
            'training_samples': len(tenders),
            'model_version': self.model_version
        }
        
        logger.info(f"Training complete. CV Score: {performance['cv_mean']:.3f} ± {performance['cv_std']:.3f}")
        logger.info(f"Test Accuracy: {performance['test_accuracy']:.3f}")
        
        return performance
    
    def predict(self, tenders: List[Dict]) -> List[Tuple[float, float]]:
        """
        Predict relevance for tenders
        Returns list of (probability, confidence) tuples
        """
        if not self.is_trained:
            raise ValueError("Classifier must be trained before making predictions")
        
        features = self.prepare_features(tenders)
        probabilities = self.classifier.predict_proba(features)
        
        results = []
        for prob_array in probabilities:
            # Probability of positive class (relevant)
            positive_prob = prob_array[1] if len(prob_array) > 1 else prob_array[0]
            
            # Confidence is how far the probability is from 0.5 (uncertainty)
            confidence = abs(positive_prob - 0.5) * 2
            
            results.append((positive_prob, confidence))
        
        return results

class TenderClassifier:
    """Main classification engine combining all analysis methods"""
    
    def __init__(self, data_dir: str = "data", enable_enhanced_scoring: bool = True):
        self.data_dir = Path(data_dir)
        self.db_path = self.data_dir / "tenders.db"
        self.enable_enhanced_scoring = enable_enhanced_scoring
        
        # Initialize analysis components
        self.keyword_analyzer = KeywordAnalyzer()
        self.context_processor = ContextProcessor()
        self.ml_classifier = MLClassifier()
        
        # Initialize enhanced scoring components if enabled
        if self.enable_enhanced_scoring:
            try:
                from scorer import RelevanceScorer
                self.relevance_scorer = RelevanceScorer()
                logger.info("Enhanced relevance scoring enabled")
                
                # Initialize advanced filtering if available
                try:
                    from filter import AdvancedOpportunityFilter
                    self.opportunity_filter = AdvancedOpportunityFilter()
                    self.enable_advanced_filtering = True
                    logger.info("Advanced opportunity filtering enabled")
                except ImportError as e:
                    logger.warning(f"Advanced filtering not available: {e}")
                    self.enable_advanced_filtering = False
                    self.opportunity_filter = None
                    
            except ImportError as e:
                logger.warning(f"Enhanced scoring not available: {e}")
                self.enable_enhanced_scoring = False
                self.enable_advanced_filtering = False
                self.relevance_scorer = None
                self.opportunity_filter = None
        
        # Classification weights for composite scoring (Phase 1 compatibility)
        self.weights = {
            'keyword_score': 0.40,    # 40% - Direct keyword matches
            'context_score': 0.30,    # 30% - Technical context analysis
            'ml_confidence': 0.30     # 30% - Machine learning prediction
        }
        
        logger.info("Tender classifier initialized")
    
    def load_training_data(self) -> Tuple[List[Dict], List[int]]:
        """
        Load tender data and generate initial training labels
        For Phase 2 Step 1, we'll use heuristic labeling based on strong signals
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.execute("""
                SELECT notice_identifier, title, description, organisation_name,
                       value_high, status, suitable_for_sme, cpv_codes
                FROM tenders
                WHERE description IS NOT NULL AND description != ''
            """)
            
            tenders = []
            for row in cursor.fetchall():
                tender = {
                    'notice_identifier': row[0],
                    'title': row[1],
                    'description': row[2],
                    'organisation_name': row[3],
                    'value_high': row[4],
                    'status': row[5],
                    'suitable_for_sme': row[6],
                    'cpv_codes': row[7]
                }
                tenders.append(tender)
        
        # Generate heuristic labels for initial training
        labels = []
        for tender in tenders:
            # Expanded heuristic: label as relevant if contains any digital/tech transformation signals
            text = f"{tender['title']} {tender['description']}".lower()
            
            # More inclusive labeling to ensure we have positive examples
            digital_signals = [
                'digital', 'modernisation', 'modernization', 'transformation', 
                'upgrade', 'migration', 'integration', 'automation', 'cloud',
                'api', 'software', 'system', 'technology', 'platform',
                'solution', 'development', 'infrastructure', 'service'
            ]
            
            # Count digital/tech signals - label as relevant if >= 2 signals or high-value contract
            signal_count = sum(1 for signal in digital_signals if signal in text)
            is_high_value = tender.get('value_high') and tender['value_high'] > 100000
            
            # Label as relevant if multiple signals or high-value tech contract
            is_relevant = signal_count >= 2 or (signal_count >= 1 and is_high_value)
            labels.append(1 if is_relevant else 0)
        
        logger.info(f"Loaded {len(tenders)} tenders with {sum(labels)} positive labels")
        return tenders, labels
    
    def train_classifier(self) -> Dict:
        """Train the ML classifier using available data"""
        tenders, labels = self.load_training_data()
        
        if len(tenders) < 10:
            logger.warning("Insufficient training data. Need at least 10 samples.")
            return {"error": "Insufficient training data"}
        
        if sum(labels) == 0:
            logger.warning("No positive examples in training data")
            return {"error": "No positive examples found"}
        
        return self.ml_classifier.train(tenders, labels)
    
    def classify_tender(self, tender_data: Dict) -> ClassificationResult:
        """
        Classify a single tender for digital transformation relevance
        """
        title = tender_data.get('title', '')
        description = tender_data.get('description', '')
        notice_id = tender_data.get('notice_identifier', '')
        
        # Keyword analysis
        keyword_score, matched_keywords = self.keyword_analyzer.analyze(title, description)
        
        # Context analysis
        context_score, tech_terms, transformation_signals = self.context_processor.analyze(title, description)
        
        # ML prediction (if trained)
        ml_confidence = 0.5  # Default neutral confidence
        if self.ml_classifier.is_trained:
            try:
                predictions = self.ml_classifier.predict([tender_data])
                if predictions:
                    ml_confidence = predictions[0][0]  # Probability of relevance
            except Exception as e:
                logger.warning(f"ML prediction failed: {e}")
        
        # Calculate composite score
        composite_score = (
            keyword_score * self.weights['keyword_score'] +
            context_score * self.weights['context_score'] +
            (ml_confidence * 100) * self.weights['ml_confidence']
        )
        
        # Generate explanation
        explanation_parts = []
        if matched_keywords:
            explanation_parts.append(f"Matched keywords: {', '.join(matched_keywords[:5])}")
        if tech_terms:
            explanation_parts.append(f"Technical terms: {', '.join(tech_terms[:5])}")
        if transformation_signals:
            explanation_parts.append(f"Transformation signals: {len(transformation_signals)} found")
        
        explanation = " | ".join(explanation_parts) if explanation_parts else "Limited digital transformation signals detected"
        
        return ClassificationResult(
            notice_identifier=notice_id,
            keyword_score=keyword_score,
            context_score=context_score,
            ml_confidence=ml_confidence,
            composite_score=composite_score,
            explanation=explanation,
            technical_terms=tech_terms,
            transformation_signals=transformation_signals
        )
    
    def classify_all_tenders(self) -> List[ClassificationResult]:
        """Classify all tenders in the database"""
        tenders, _ = self.load_training_data()
        
        results = []
        for tender in tenders:
            try:
                result = self.classify_tender(tender)
                results.append(result)
            except Exception as e:
                logger.error(f"Classification failed for {tender.get('notice_identifier', 'unknown')}: {e}")
                continue
        
        logger.info(f"Classified {len(results)} tenders")
        return results
    
    def get_top_opportunities(self, min_score: float = 30, limit: int = 20, use_enhanced_scoring: bool = None) -> List:
        """Get top-scored opportunities above threshold"""
        if use_enhanced_scoring is None:
            use_enhanced_scoring = self.enable_enhanced_scoring
            
        if use_enhanced_scoring and self.relevance_scorer:
            return self.get_enhanced_opportunities(min_score, limit)
        else:
            # Fallback to original classification
            all_results = self.classify_all_tenders()
            filtered_results = [r for r in all_results if r.composite_score >= min_score]
            sorted_results = sorted(filtered_results, key=lambda x: x.composite_score, reverse=True)
            return sorted_results[:limit]
    
    def get_enhanced_opportunities(self, min_score: float = 50, limit: int = 20):
        """Get opportunities using enhanced relevance scoring"""
        if not self.enable_enhanced_scoring or not self.relevance_scorer:
            raise ValueError("Enhanced scoring not available")
        
        # Load tender data with full metadata
        tenders, _ = self.load_training_data()
        enhanced_results = []
        
        for tender in tenders:
            try:
                # Get basic classification first
                basic_result = self.classify_tender(tender)
                
                # Apply enhanced scoring
                enhanced_result = self.relevance_scorer.score_classified_tender(tender, basic_result)
                enhanced_results.append(enhanced_result)
                
            except Exception as e:
                logger.error(f"Enhanced scoring failed for {tender.get('notice_identifier', 'unknown')}: {e}")
                continue
        
        # Filter and sort by final relevance score
        filtered_results = [r for r in enhanced_results if r.final_relevance_score >= min_score]
        sorted_results = sorted(filtered_results, key=lambda x: x.final_relevance_score, reverse=True)
        
        logger.info(f"Enhanced scoring: {len(sorted_results)} opportunities above {min_score} threshold")
        return sorted_results[:limit]
    
    def classify_tender_enhanced(self, tender_data: Dict):
        """Classify tender with enhanced scoring if available"""
        # Get basic classification
        basic_result = self.classify_tender(tender_data)
        
        # Apply enhanced scoring if enabled
        if self.enable_enhanced_scoring and self.relevance_scorer:
            return self.relevance_scorer.score_classified_tender(tender_data, basic_result)
        else:
            return basic_result
    
    def get_filtered_opportunities(self, profile: str = 'balanced', min_score: float = None, limit: int = 20):
        """Get opportunities filtered through advanced filtering system"""
        if not self.enable_advanced_filtering or not self.opportunity_filter:
            logger.warning("Advanced filtering not available - falling back to enhanced opportunities")
            return self.get_enhanced_opportunities(min_score or 50, limit)
        
        # Get enhanced opportunities first
        enhanced_results = self.get_enhanced_opportunities(min_score or 30, limit * 3)  # Get more for filtering
        
        if not enhanced_results:
            logger.info("No enhanced opportunities found for filtering")
            return []
        
        # Apply advanced filtering
        try:
            filtered_results = self.opportunity_filter.filter_opportunities(enhanced_results, profile)
            logger.info(f"Advanced filtering: {len(filtered_results)} opportunities processed with '{profile}' profile")
            
            # Return only opportunities that pass filters
            passing_results = [r for r in filtered_results if r.filter_passes]
            
            return passing_results[:limit]
            
        except Exception as e:
            logger.error(f"Advanced filtering failed: {e}")
            return enhanced_results[:limit]  # Fallback to enhanced results
    
    def get_filtered_opportunities_all(self, profile: str = 'balanced') -> List:
        """Get all filtered opportunities regardless of pass/fail status for analysis"""
        if not self.enable_advanced_filtering or not self.opportunity_filter:
            logger.warning("Advanced filtering not available")
            return []
        
        # Get all enhanced opportunities
        enhanced_results = self.get_enhanced_opportunities(min_score=20, limit=100)
        
        if not enhanced_results:
            return []
        
        # Apply advanced filtering to all
        try:
            # Temporarily modify the filter to load real tender data
            self._patch_filter_for_real_data()
            
            filtered_results = self.opportunity_filter.filter_opportunities(enhanced_results, profile)
            logger.info(f"Complete filtering analysis: {len(filtered_results)} opportunities analyzed")
            
            return filtered_results
            
        except Exception as e:
            logger.error(f"Complete filtering analysis failed: {e}")
            return []
    
    def _patch_filter_for_real_data(self):
        """Patch the filter to load real tender data from database"""
        original_load_method = self.opportunity_filter.load_tender_data
        
        def load_real_tender_data(notice_identifier: str) -> Dict:
            """Load actual tender data from database"""
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute("""
                    SELECT notice_identifier, title, description, organisation_name,
                           value_high, status, suitable_for_sme, cpv_codes, closing_date
                    FROM tenders
                    WHERE notice_identifier = ?
                """, (notice_identifier,))
                
                row = cursor.fetchone()
                if row:
                    return {
                        'notice_identifier': row[0],
                        'title': row[1] or '',
                        'description': row[2] or '',
                        'organisation_name': row[3] or '',
                        'value_high': row[4] or 0,
                        'status': row[5] or '',
                        'suitable_for_sme': row[6] or '',
                        'cpv_codes': row[7] or '',
                        'closing_date': row[8] or ''
                    }
                else:
                    logger.warning(f"No tender data found for {notice_identifier}")
                    return original_load_method(notice_identifier)
        
        # Monkey patch the method
        self.opportunity_filter.load_tender_data = load_real_tender_data
    
    def analyze_filtering_performance(self, profile: str = 'balanced') -> Dict:
        """Analyze the performance of different filtering profiles"""
        if not self.enable_advanced_filtering:
            return {'error': 'Advanced filtering not available'}
        
        profiles = ['aggressive', 'balanced', 'conservative', 'strategic']
        analysis = {}
        
        # Get base enhanced results
        enhanced_results = self.get_enhanced_opportunities(min_score=20, limit=50)
        if not enhanced_results:
            return {'error': 'No enhanced opportunities available for analysis'}
        
        # Test each profile
        for test_profile in profiles:
            try:
                self._patch_filter_for_real_data()
                filtered_results = self.opportunity_filter.filter_opportunities(enhanced_results, test_profile)
                
                passing_count = len([r for r in filtered_results if r.filter_passes])
                avg_bid_probability = sum(r.bid_probability for r in filtered_results) / len(filtered_results)
                avg_competition_level = sum(r.competition_assessment['competition_level'] for r in filtered_results) / len(filtered_results)
                
                pursue_count = len([r for r in filtered_results if r.final_recommendation == 'PURSUE'])
                consider_count = len([r for r in filtered_results if r.final_recommendation == 'CONSIDER'])
                
                analysis[test_profile] = {
                    'total_analyzed': len(filtered_results),
                    'passing_filters': passing_count,
                    'pass_rate': passing_count / len(filtered_results) if filtered_results else 0,
                    'avg_bid_probability': avg_bid_probability,
                    'avg_competition_level': avg_competition_level,
                    'pursue_recommendations': pursue_count,
                    'consider_recommendations': consider_count,
                    'recommendation_distribution': {
                        'PURSUE': pursue_count,
                        'CONSIDER': consider_count,
                        'MONITOR': len([r for r in filtered_results if r.final_recommendation == 'MONITOR']),
                        'AVOID': len([r for r in filtered_results if r.final_recommendation == 'AVOID'])
                    }
                }
                
            except Exception as e:
                analysis[test_profile] = {'error': str(e)}
        
        return analysis


def main():
    """Test the classification system"""
    classifier = TenderClassifier()
    
    # Train the ML classifier
    print("Training ML classifier...")
    training_results = classifier.train_classifier()
    print(f"Training results: {training_results}")
    
    # Get top opportunities
    print("\nFinding top digital transformation opportunities...")
    top_opportunities = classifier.get_top_opportunities(min_score=20, limit=10)
    
    print(f"\n=== Top {len(top_opportunities)} Digital Transformation Opportunities ===")
    for i, result in enumerate(top_opportunities, 1):
        print(f"\n{i}. Score: {result.composite_score:.1f}")
        print(f"   Tender: {result.notice_identifier}")
        print(f"   Breakdown: Keywords={result.keyword_score:.1f}, Context={result.context_score:.1f}, ML={result.ml_confidence:.3f}")
        print(f"   Explanation: {result.explanation}")
        
        if result.technical_terms:
            print(f"   Technical Terms: {', '.join(result.technical_terms[:5])}")


if __name__ == "__main__":
    main()