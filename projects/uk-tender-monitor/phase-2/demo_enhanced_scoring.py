#!/usr/bin/env python3
"""
Phase 2 Step 2 Demonstration: Enhanced Relevance Scoring System
Shows the complete enhanced scoring pipeline with business intelligence
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import json

from classifier import TenderClassifier
from scorer import RelevanceScorer
from database_extensions import DatabaseExtensions

def demonstrate_enhanced_scoring_system():
    """Comprehensive demonstration of enhanced relevance scoring"""
    
    print("=" * 80)
    print("UK TENDER MONITOR - Phase 2 Step 2 DEMONSTRATION")
    print("Enhanced Relevance Scoring System with Business Intelligence")
    print("=" * 80)
    
    # Initialize components
    print("\n1. INITIALIZING ENHANCED SCORING SYSTEM")
    print("-" * 50)
    
    # Initialize classifier with enhanced scoring enabled
    classifier = TenderClassifier(enable_enhanced_scoring=True)
    
    if not classifier.enable_enhanced_scoring:
        print("[WARN] Enhanced scoring not available - falling back to basic classification")
        return
    
    # Initialize database extensions
    db_extensions = DatabaseExtensions(classifier.db_path)
    db_extensions.create_enhanced_tables()
    db_extensions.create_indexes()
    
    print("[OK] Enhanced scoring system initialized")
    print("[OK] Database schema extended with enhanced tables")
    
    # Check available data
    with sqlite3.connect(classifier.db_path) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM tenders")
        total_tenders = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT COUNT(*) FROM tenders WHERE description IS NOT NULL AND description != ''")
        processable_tenders = cursor.fetchone()[0]
    
    print(f"[OK] Total tenders in database: {total_tenders}")
    print(f"[OK] Tenders processable for enhanced scoring: {processable_tenders}")
    
    # Train the classifier
    print("\n2. TRAINING CLASSIFICATION ENGINE")
    print("-" * 50)
    training_results = classifier.train_classifier()
    
    if 'error' not in training_results:
        print(f"[OK] Training completed successfully")
        print(f"   - Cross-validation score: {training_results['cv_mean']:.3f} +/- {training_results['cv_std']:.3f}")
        print(f"   - Test accuracy: {training_results['test_accuracy']:.3f}")
        print(f"   - Training samples: {training_results['training_samples']}")
    else:
        print(f"[WARN] Training issue: {training_results['error']}")
    
    # Demonstrate enhanced scoring with examples
    print("\n3. ENHANCED SCORING EXAMPLES")
    print("-" * 50)
    
    # Test different tender scenarios
    test_scenarios = [
        {
            'name': 'HIGH-VALUE NHS DIGITAL TRANSFORMATION',
            'tender': {
                'notice_identifier': 'demo_001',
                'title': 'NHS Digital Health Platform Modernisation',
                'description': 'Comprehensive digital transformation of healthcare systems including cloud migration, API development, microservices architecture, and patient data integration using modern technologies like Python, React, and AWS cloud infrastructure.',
                'organisation_name': 'NHS Digital',
                'value_high': 2500000,
                'cpv_codes': '72000000',
                'suitable_for_sme': 'no',
                'status': 'open',
                'closing_date': (datetime.now() + timedelta(days=21)).isoformat()
            }
        },
        {
            'name': 'MEDIUM-VALUE UNIVERSITY IT PROJECT',
            'tender': {
                'notice_identifier': 'demo_002',
                'title': 'Student Information System Upgrade',
                'description': 'Modernizing legacy student management system with new web-based interface, database migration, and integration with existing university systems.',
                'organisation_name': 'University of Cambridge',
                'value_high': 350000,
                'cpv_codes': '72200000',
                'suitable_for_sme': 'yes',
                'status': 'open',
                'closing_date': (datetime.now() + timedelta(days=45)).isoformat()
            }
        },
        {
            'name': 'URGENT LOW-VALUE TECHNICAL SUPPORT',
            'tender': {
                'notice_identifier': 'demo_003',
                'title': 'IT Support Services',
                'description': 'Technical support and maintenance for existing computer systems and software applications.',
                'organisation_name': 'Local District Council',
                'value_high': 85000,
                'cpv_codes': '72500000',
                'suitable_for_sme': 'yes',
                'status': 'open',
                'closing_date': (datetime.now() + timedelta(days=12)).isoformat()
            }
        },
        {
            'name': 'NON-DIGITAL PROCUREMENT',
            'tender': {
                'notice_identifier': 'demo_004',
                'title': 'Office Furniture and Equipment',
                'description': 'Purchase of desks, chairs, filing cabinets and general office furniture for new government building.',
                'organisation_name': 'Cabinet Office',
                'value_high': 150000,
                'cpv_codes': '39000000',
                'suitable_for_sme': 'yes',
                'status': 'open',
                'closing_date': (datetime.now() + timedelta(days=60)).isoformat()
            }
        }
    ]
    
    enhanced_results = []
    
    for scenario in test_scenarios:
        print(f"\n--- {scenario['name']} ---")
        tender = scenario['tender']
        
        # Get enhanced classification
        result = classifier.classify_tender_enhanced(tender)
        enhanced_results.append(result)
        
        # Display comprehensive results
        print(f"Tender: {tender['title'][:50]}...")
        print(f"Organization: {tender['organisation_name']}")
        print(f"Value: £{tender['value_high']:,}")
        print(f"Closing: {tender['closing_date'][:10]}")
        
        print(f"\nSCORING BREAKDOWN:")
        print(f"  Basic Scores - Keywords: {result.keyword_score:.1f}, Context: {result.context_score:.1f}, ML: {result.ml_confidence:.3f}")
        print(f"  Enhanced - Metadata: {result.metadata_score:.1f}, Business: {result.business_alignment_score:.1f}")
        print(f"  Multipliers - Urgency: {result.urgency_multiplier:.2f}x, Value: {result.value_multiplier:.2f}x, Dept: {result.department_multiplier:.2f}x")
        print(f"  FINAL SCORE: {result.final_relevance_score:.1f}/100")
        print(f"  PRIORITY: {result.priority_level}")
        print(f"  RECOMMENDATION: {result.recommendation}")
        print(f"  EXPLANATION: {result.explanation}")
        
        # Save to database
        db_extensions.save_enhanced_classification(result, tender)
    
    # Show comparative analysis
    print("\n4. COMPARATIVE SCORING ANALYSIS")
    print("-" * 50)
    
    # Sort by final relevance score
    sorted_results = sorted(enhanced_results, key=lambda x: x.final_relevance_score, reverse=True)
    
    print("OPPORTUNITIES RANKED BY ENHANCED RELEVANCE SCORE:")
    for i, result in enumerate(sorted_results, 1):
        multiplier_impact = (result.urgency_multiplier * result.value_multiplier * 
                           result.department_multiplier * result.competition_multiplier)
        
        print(f"{i}. {result.notice_identifier} - Score: {result.final_relevance_score:.1f}")
        print(f"   Priority: {result.priority_level} | Base Score: {result.base_composite_score:.1f} | Multiplier Impact: {multiplier_impact:.2f}x")
    
    # Demonstrate real tender classification
    print("\n5. REAL TENDER DATA ENHANCED CLASSIFICATION")
    print("-" * 50)
    
    # Get top enhanced opportunities from real data
    try:
        top_enhanced = classifier.get_enhanced_opportunities(min_score=30, limit=10)
        
        if top_enhanced:
            print(f"Found {len(top_enhanced)} enhanced opportunities above score threshold:")
            
            for i, result in enumerate(top_enhanced[:5], 1):  # Show top 5
                print(f"\n[#{i}] ENHANCED OPPORTUNITY - Score: {result.final_relevance_score:.1f}")
                
                # Get tender details (from database query)
                with sqlite3.connect(classifier.db_path) as conn:
                    cursor = conn.execute("""
                        SELECT title, organisation_name, value_high, closing_date, status
                        FROM tenders WHERE notice_identifier = ?
                    """, (result.notice_identifier,))
                    
                    row = cursor.fetchone()
                    if row:
                        title, org, value, closing, status = row
                        
                        print(f"   Title: {title[:60]}...")
                        print(f"   Organization: {org}")
                        print(f"   Value: £{value:,}" if value else "Value TBD")
                        print(f"   Status: {status} | Closing: {closing[:10] if closing else 'TBD'}")
                
                print(f"   Priority: {result.priority_level}")
                print(f"   Recommendation: {result.recommendation}")
                print(f"   Score Breakdown: Base={result.base_composite_score:.1f}, Multipliers={result.urgency_multiplier:.2f}x{result.value_multiplier:.2f}x{result.department_multiplier:.2f}x")
                print(f"   Business Intelligence: {result.explanation}")
                
                # Show technical terms if available
                if result.technical_terms:
                    print(f"   Technical Terms: {', '.join(result.technical_terms[:5])}")
        
        else:
            print("No opportunities found above threshold - adjusting criteria...")
            # Try lower threshold
            lower_threshold = classifier.get_enhanced_opportunities(min_score=15, limit=5)
            if lower_threshold:
                print(f"Found {len(lower_threshold)} opportunities with lower threshold:")
                for result in lower_threshold:
                    print(f"  - {result.notice_identifier}: {result.final_relevance_score:.1f} ({result.priority_level})")
    
    except Exception as e:
        print(f"[ERROR] Real tender classification failed: {e}")
        print("Continuing with demonstration examples...")
    
    # Show enhanced vs basic comparison
    print("\n6. ENHANCED VS BASIC SCORING COMPARISON")
    print("-" * 50)
    
    print("Comparison of Basic vs Enhanced Scoring:")
    print("| Tender | Basic Score | Enhanced Score | Priority | Improvement |")
    print("|--------|-------------|----------------|----------|-------------|")
    
    for result in enhanced_results:
        # Calculate basic score equivalent (for comparison)
        basic_equivalent = (result.keyword_score * 0.4 + result.context_score * 0.3 + 
                          result.ml_confidence * 100 * 0.3)
        improvement = ((result.final_relevance_score - basic_equivalent) / max(basic_equivalent, 1)) * 100
        
        print(f"| {result.notice_identifier} | {basic_equivalent:.1f} | {result.final_relevance_score:.1f} | {result.priority_level} | {improvement:+.0f}% |")
    
    # Show business intelligence insights
    print("\n7. BUSINESS INTELLIGENCE INSIGHTS")
    print("-" * 50)
    
    # Analyze multiplier impacts
    urgency_impacts = [r.urgency_multiplier for r in enhanced_results]
    value_impacts = [r.value_multiplier for r in enhanced_results]
    dept_impacts = [r.department_multiplier for r in enhanced_results]
    
    print("MULTIPLIER ANALYSIS:")
    print(f"  Average Urgency Impact: {sum(urgency_impacts)/len(urgency_impacts):.2f}x")
    print(f"  Average Value Impact: {sum(value_impacts)/len(value_impacts):.2f}x")
    print(f"  Average Department Preference: {sum(dept_impacts)/len(dept_impacts):.2f}x")
    
    # Identify high-impact factors
    high_urgency = [r for r in enhanced_results if r.urgency_multiplier >= 1.3]
    high_value = [r for r in enhanced_results if r.value_multiplier >= 1.5]
    preferred_orgs = [r for r in enhanced_results if r.department_multiplier >= 1.2]
    
    print(f"\nHIGH-IMPACT OPPORTUNITIES:")
    print(f"  Urgent timing (≥1.3x): {len(high_urgency)} opportunities")
    print(f"  High value bracket (≥1.5x): {len(high_value)} opportunities")
    print(f"  Preferred organizations (≥1.2x): {len(preferred_orgs)} opportunities")
    
    # Database statistics
    print("\n8. DATABASE STATISTICS")
    print("-" * 50)
    
    stats = db_extensions.get_scoring_statistics()
    if stats:
        print(f"Total Enhanced Classifications: {stats.get('total_classifications', 0)}")
        
        if 'score_distribution' in stats:
            dist = stats['score_distribution']
            print(f"Score Distribution:")
            print(f"  High Score (≥70): {dist.get('high_score_count', 0)}")
            print(f"  Medium Score (40-69): {dist.get('medium_score_count', 0)}")
            print(f"  Low Score (<40): {dist.get('low_score_count', 0)}")
            print(f"  Average Score: {dist.get('average_score', 0):.1f}")
        
        if 'priority_distribution' in stats:
            priority_dist = stats['priority_distribution']
            print(f"Priority Distribution:")
            for priority, count in priority_dist.items():
                print(f"  {priority}: {count}")
    
    print("\n" + "=" * 80)
    print("PHASE 2 STEP 2 DEMONSTRATION COMPLETE")
    print("Enhanced Relevance Scoring System with Business Intelligence")
    print("✅ Advanced composite scoring (0-100 scale)")
    print("✅ Metadata analysis (CPV codes, organization intelligence)")
    print("✅ Business alignment assessment")
    print("✅ Dynamic multiplier factors (urgency, value, department)")
    print("✅ Priority classification and actionable recommendations")
    print("=" * 80)

def demonstrate_specific_features():
    """Demonstrate specific enhanced scoring features"""
    
    print("\n" + "=" * 60)
    print("SPECIFIC FEATURE DEMONSTRATIONS")
    print("=" * 60)
    
    # Initialize scorer
    scorer = RelevanceScorer()
    
    # Demonstrate metadata analysis
    print("\n1. METADATA ANALYSIS EXAMPLES")
    print("-" * 40)
    
    test_metadata = [
        {
            'name': 'High-Tech NHS Digital',
            'data': {
                'cpv_codes': '72000000',
                'organisation_name': 'NHS Digital',
                'value_high': 1500000,
                'closing_date': (datetime.now() + timedelta(days=30)).isoformat()
            }
        },
        {
            'name': 'Medium Council Project',
            'data': {
                'cpv_codes': '72200000',
                'organisation_name': 'Manchester City Council',
                'value_high': 250000,
                'closing_date': (datetime.now() + timedelta(days=60)).isoformat()
            }
        }
    ]
    
    for test in test_metadata:
        score, breakdown = scorer.metadata_analyzer.analyze_metadata(test['data'])
        print(f"\n{test['name']}:")
        print(f"  Total Metadata Score: {score:.1f}/15")
        print(f"  CPV Analysis: {breakdown.get('cpv_analysis', {}).get('score', 0)}")
        print(f"  Organization Score: {breakdown.get('organization_analysis', {}).get('score', 0)}")
        print(f"  Value Score: {breakdown.get('value_analysis', {}).get('score', 0)}")
    
    # Demonstrate multiplier calculations
    print("\n2. MULTIPLIER FACTOR EXAMPLES")
    print("-" * 40)
    
    test_multipliers = [
        {
            'name': 'Urgent High-Value NHS',
            'data': {
                'closing_date': (datetime.now() + timedelta(days=10)).isoformat(),
                'value_high': 2000000,
                'organisation_name': 'NHS Digital',
                'suitable_for_sme': 'no'
            }
        },
        {
            'name': 'Standard University Project',
            'data': {
                'closing_date': (datetime.now() + timedelta(days=45)).isoformat(),
                'value_high': 300000,
                'organisation_name': 'University of Oxford',
                'suitable_for_sme': 'yes'
            }
        }
    ]
    
    for test in test_multipliers:
        print(f"\n{test['name']}:")
        
        urgency_mult, urgency_breakdown = scorer.multiplier_calculator.calculate_urgency_multiplier(test['data'])
        value_mult, value_breakdown = scorer.multiplier_calculator.calculate_value_multiplier(test['data'])
        dept_mult, dept_breakdown = scorer.multiplier_calculator.calculate_department_multiplier(test['data'])
        comp_mult, comp_breakdown = scorer.multiplier_calculator.calculate_competition_multiplier(test['data'])
        
        total_multiplier = urgency_mult * value_mult * dept_mult * comp_mult
        
        print(f"  Urgency: {urgency_mult:.2f}x ({urgency_breakdown.get('status', 'unknown')})")
        print(f"  Value: {value_mult:.2f}x ({value_breakdown.get('bracket', 'unknown')})")
        print(f"  Department: {dept_mult:.2f}x ({dept_breakdown.get('preference', 'standard')})")
        print(f"  Competition: {comp_mult:.2f}x ({comp_breakdown.get('level', 'standard')})")
        print(f"  TOTAL MULTIPLIER: {total_multiplier:.2f}x")

if __name__ == "__main__":
    try:
        demonstrate_enhanced_scoring_system()
        demonstrate_specific_features()
    except Exception as e:
        print(f"\nDemonstration failed with error: {e}")
        import traceback
        traceback.print_exc()
        print("\nThis may be due to missing dependencies or database issues.")
        print("Please ensure all Phase 2 Step 2 components are properly installed.")