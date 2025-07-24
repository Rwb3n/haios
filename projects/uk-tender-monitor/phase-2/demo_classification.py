#!/usr/bin/env python3
"""
Phase 2 Step 1 Demonstration: NLP Classification Engine
Shows the complete classification pipeline working with real UK government tender data
"""

import sqlite3
from classifier import TenderClassifier
from datetime import datetime

def demonstrate_classification_engine():
    """Comprehensive demonstration of the classification system"""
    
    print("="*80)
    print("UK TENDER MONITOR - Phase 2 Step 1 DEMONSTRATION")
    print("NLP Classification Engine for Digital Transformation Opportunities")
    print("="*80)
    
    # Initialize the classifier
    print("\n1. INITIALIZING CLASSIFICATION ENGINE")
    print("-" * 40)
    classifier = TenderClassifier()
    
    # Check available data
    with sqlite3.connect(classifier.db_path) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM tenders")
        total_tenders = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT COUNT(*) FROM tenders WHERE description IS NOT NULL AND description != ''")
        processable_tenders = cursor.fetchone()[0]
    
    print(f"[OK] Total tenders in database: {total_tenders}")
    print(f"[OK] Tenders with descriptions (processable): {processable_tenders}")
    
    # Train the classifier
    print("\n2. TRAINING MACHINE LEARNING CLASSIFIER")
    print("-" * 40)
    training_results = classifier.train_classifier()
    
    if 'error' not in training_results:
        print(f"[OK] Training completed successfully")
        print(f"   - Cross-validation score: {training_results['cv_mean']:.3f} +/- {training_results['cv_std']:.3f}")
        print(f"   - Test accuracy: {training_results['test_accuracy']:.3f}")
        print(f"   - Training samples: {training_results['training_samples']}")
        print(f"   - Model version: {training_results['model_version']}")
    else:
        print(f"[WARN] Training issue: {training_results['error']}")
        print("   Proceeding with keyword-based classification only")
    
    # Classify all tenders
    print("\n3. CLASSIFYING ALL TENDERS")
    print("-" * 40)
    results = classifier.classify_all_tenders()
    print(f"[OK] Classified {len(results)} tenders successfully")
    
    # Show classification distribution
    scores = [r.composite_score for r in results]
    high_relevance = len([s for s in scores if s >= 40])
    medium_relevance = len([s for s in scores if 20 <= s < 40])
    low_relevance = len([s for s in scores if s < 20])
    
    print(f"   - High relevance (>=40): {high_relevance} tenders")
    print(f"   - Medium relevance (20-39): {medium_relevance} tenders")
    print(f"   - Low relevance (<20): {low_relevance} tenders")
    
    # Get top opportunities
    print("\n4. TOP DIGITAL TRANSFORMATION OPPORTUNITIES")
    print("-" * 40)
    top_opportunities = classifier.get_top_opportunities(min_score=15, limit=15)
    
    if not top_opportunities:
        print("No opportunities found above threshold")
        return
    
    # Get tender details for top opportunities
    tender_details = {}
    with sqlite3.connect(classifier.db_path) as conn:
        for result in top_opportunities:
            cursor = conn.execute("""
                SELECT title, description, organisation_name, value_high, status, closing_date
                FROM tenders 
                WHERE notice_identifier = ?
            """, (result.notice_identifier,))
            
            row = cursor.fetchone()
            if row:
                tender_details[result.notice_identifier] = {
                    'title': row[0],
                    'description': row[1],
                    'organisation': row[2],
                    'value': row[3],
                    'status': row[4],
                    'closing_date': row[5]
                }
    
    # Display top opportunities with rich details
    for i, result in enumerate(top_opportunities, 1):
        details = tender_details.get(result.notice_identifier, {})
        
        print(f"\n[#{i}] OPPORTUNITY - Score: {result.composite_score:.1f}")
        print(f"   Title: {details.get('title', 'N/A')[:70]}")
        print(f"   Organization: {details.get('organisation', 'N/A')}")
        
        # Format value
        value = details.get('value')
        if value:
            if value >= 1000000:
                value_str = f"£{value/1000000:.1f}M"
            elif value >= 1000:
                value_str = f"£{value/1000:.0f}K"
            else:
                value_str = f"£{value:,}"
        else:
            value_str = "Value TBD"
        
        print(f"   Value: {value_str} | Status: {details.get('status', 'N/A')}")
        
        # Show classification breakdown
        print(f"   Classification: Keywords={result.keyword_score:.1f}, "
              f"Context={result.context_score:.1f}, ML={result.ml_confidence:.3f}")
        
        # Show explanation
        print(f"   Reason: {result.explanation}")
        
        # Show technical terms if found
        if result.technical_terms:
            print(f"   Tech Terms: {', '.join(result.technical_terms[:5])}")
        
        # Show description excerpt
        description = details.get('description', '')
        if description:
            excerpt = description[:150].replace('\n', ' ').strip()
            print(f"   Description: {excerpt}...")
        
        print()
    
    # Show keyword analysis breakdown
    print("\n5. KEYWORD ANALYSIS BREAKDOWN")
    print("-" * 40)
    
    keyword_matches = {}
    for result in top_opportunities[:10]:  # Top 10 for analysis
        details = tender_details.get(result.notice_identifier, {})
        text = f"{details.get('title', '')} {details.get('description', '')}".lower()
        
        # Check which keywords were found
        for keyword in classifier.keyword_analyzer.all_keywords:
            if keyword in text:
                if keyword not in keyword_matches:
                    keyword_matches[keyword] = 0
                keyword_matches[keyword] += 1
    
    # Show most common keywords
    sorted_keywords = sorted(keyword_matches.items(), key=lambda x: x[1], reverse=True)
    print("Most frequent keywords in top opportunities:")
    for keyword, count in sorted_keywords[:10]:
        weight = classifier.keyword_analyzer.all_keywords[keyword]
        print(f"   - '{keyword}' (weight: {weight}): {count} occurrences")
    
    # Show technical term analysis
    print("\n6. TECHNICAL TERM ANALYSIS")
    print("-" * 40)
    
    all_tech_terms = []
    for result in top_opportunities[:10]:
        all_tech_terms.extend(result.technical_terms)
    
    # Count technical term frequency
    tech_term_counts = {}
    for term in all_tech_terms:
        tech_term_counts[term] = tech_term_counts.get(term, 0) + 1
    
    sorted_tech_terms = sorted(tech_term_counts.items(), key=lambda x: x[1], reverse=True)
    print("Most frequent technical terms:")
    for term, count in sorted_tech_terms[:10]:
        print(f"   - '{term}': {count} occurrences")
    
    # Show ML model insights (if trained)
    if 'error' not in training_results:
        print("\n7. MACHINE LEARNING INSIGHTS")
        print("-" * 40)
        
        # Show confidence distribution
        ml_confidences = [r.ml_confidence for r in top_opportunities[:10]]
        avg_confidence = sum(ml_confidences) / len(ml_confidences)
        max_confidence = max(ml_confidences)
        min_confidence = min(ml_confidences)
        
        print(f"ML Model performance on top opportunities:")
        print(f"   - Average confidence: {avg_confidence:.3f}")
        print(f"   - Highest confidence: {max_confidence:.3f}")
        print(f"   - Lowest confidence: {min_confidence:.3f}")
        
        # Show feature importance insights
        feature_importance = training_results.get('feature_importance', [])
        if feature_importance:
            print(f"   - Top feature importance scores: {feature_importance[:5]}")
    
    # Performance summary
    print("\n8. PERFORMANCE SUMMARY")
    print("-" * 40)
    
    # Calculate some performance metrics
    above_threshold = len([r for r in results if r.composite_score >= 20])
    digital_keywords = len([r for r in results if any(
        kw in r.explanation.lower() for kw in ['digital', 'transformation', 'modernisation', 'api', 'cloud']
    )])
    
    print(f"[OK] Classification Performance:")
    print(f"   - Total classified: {len(results)} tenders")
    print(f"   - Above relevance threshold (>=20): {above_threshold} tenders ({above_threshold/len(results)*100:.1f}%)")
    print(f"   - Contains digital keywords: {digital_keywords} tenders ({digital_keywords/len(results)*100:.1f}%)")
    print(f"   - Top opportunities identified: {len(top_opportunities)}")
    
    # Show organization distribution
    org_distribution = {}
    for result in top_opportunities:
        details = tender_details.get(result.notice_identifier, {})
        org = details.get('organisation', 'Unknown')
        org_distribution[org] = org_distribution.get(org, 0) + 1
    
    print(f"\n   Organization distribution in top opportunities:")
    for org, count in sorted(org_distribution.items(), key=lambda x: x[1], reverse=True)[:5]:
        print(f"   - {org}: {count} opportunities")
    
    print("\n" + "="*80)
    print("PHASE 2 STEP 1 DEMONSTRATION COMPLETE")
    print("NLP Classification Engine successfully identifies digital transformation opportunities")
    print("="*80)

if __name__ == "__main__":
    demonstrate_classification_engine()