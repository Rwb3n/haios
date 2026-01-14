# generated: 2025-12-04
# System Auto: last updated on: 2025-12-04 22:53:41
"""
Test cases for extraction type discrimination improvements.

These tests validate that the extraction prompt correctly discriminates between:
- Directive (commands, instructions)
- Critique (evaluative feedback, problem identification)
- Proposal (suggestions, recommendations)
- Decision (formal choices announced)

Session 26 - Path B: Fix extraction quality
Uses REAL SAMPLES from the database to validate type discrimination.
"""

import pytest
import os
import time
from dataclasses import dataclass
from typing import Optional, List

# Import extraction module
from haios_etl.extraction import ExtractionManager, ExtractionConfig


@dataclass
class TypeDiscriminationTestCase:
    """Test case for type discrimination."""
    input_text: str
    expected_type: Optional[str]  # None means "should not be extracted"
    discriminating_feature: str
    category: str  # Group for reporting


# Real samples from haios_memory.db - sufficient length for langextract
TYPE_DISCRIMINATION_CASES = [
    # === DIRECTIVE - Real samples with imperative markers ===
    TypeDiscriminationTestCase(
        input_text="Every test run must now generate a unique `idempotency_key` and propagate a `trace_id` through all logs and result artifacts.",
        expected_type="Directive",
        discriminating_feature="'must' + imperative requirement",
        category="directive"
    ),
    TypeDiscriminationTestCase(
        input_text="The JSON object MUST be placed within a comment block delineated by `/* ANNOTATION_BLOCK_START` and `ANNOTATION_BLOCK_END */`",
        expected_type="Directive",
        discriminating_feature="'MUST' + placement instruction",
        category="directive"
    ),
    TypeDiscriminationTestCase(
        input_text="Create a simulation in the Isaac Sim environment where a virtual 'Hephaestus Prime' must pick up a virtual 'glass beaker' from a cluttered table.",
        expected_type="Directive",
        discriminating_feature="'Create' imperative verb",
        category="directive"
    ),
    TypeDiscriminationTestCase(
        input_text="The Gatekeeper agent must exist before the library it guards can be populated.",
        expected_type="Directive",
        discriminating_feature="'must exist' requirement",
        category="directive"
    ),

    # === PROPOSAL - Real samples with suggestive markers ===
    TypeDiscriminationTestCase(
        input_text="I strongly recommend renaming this ADR to 'ADR-OS-018: Foundational Security Controls' and updating its rationale to match its content",
        expected_type="Proposal",
        discriminating_feature="'recommend' suggestion marker",
        category="proposal"
    ),
    TypeDiscriminationTestCase(
        input_text="Recommendation: Review all annotation blocks across the appendices for similar copy-paste errors.",
        expected_type="Proposal",
        discriminating_feature="'Recommendation:' prefix",
        category="proposal"
    ),
    TypeDiscriminationTestCase(
        input_text="The global_registry_map.txt or issue_summary.txt could be implemented as CRDTs for better conflict resolution in distributed scenarios.",
        expected_type="Proposal",
        discriminating_feature="'could be' suggestive",
        category="proposal"
    ),

    # === DECISION - Real samples with decision markers ===
    TypeDiscriminationTestCase(
        input_text="Architectural Decision: Introduce a new first-class artifact type: the Cookbook Recipe",
        expected_type="Decision",
        discriminating_feature="'Architectural Decision:' prefix",
        category="decision"
    ),
    TypeDiscriminationTestCase(
        input_text="We explicitly decided not to be a 'Band-Aid' (a better CLI agent) but a 'Synergy' tool (the governance layer that commands them)",
        expected_type="Decision",
        discriminating_feature="'decided' explicit choice",
        category="decision"
    ),
    TypeDiscriminationTestCase(
        input_text="Architectural Decision: Implement the Crystallization Protocol, a formal two-space system enforced by a new agent persona.",
        expected_type="Decision",
        discriminating_feature="'Architectural Decision:' formal announcement",
        category="decision"
    ),

    # === CRITIQUE - Real samples with evaluative markers ===
    TypeDiscriminationTestCase(
        input_text="Issue: Wrong exit code (1 instead of 2) for security violations. This breaks the validation pipeline expectations.",
        expected_type="Critique",
        discriminating_feature="'Issue:' + 'Wrong' evaluative",
        category="critique"
    ),
    TypeDiscriminationTestCase(
        input_text="the mismatch between its title ('Persistence & Recovery') and its content ('Security Controls') is a major architectural issue",
        expected_type="Critique",
        discriminating_feature="'mismatch' + 'issue' problem identification",
        category="critique"
    ),
    TypeDiscriminationTestCase(
        input_text="There is no value in having a library of reusable recipes (Cookbook) or an engine to apply them at scale (Orchestrator) if the process for creating those recipes is flawed",
        expected_type="Critique",
        discriminating_feature="'no value' + 'flawed' negative evaluation",
        category="critique"
    ),

    # === DESCRIPTIONS - Should NOT be extracted ===
    TypeDiscriminationTestCase(
        input_text="The caching layer stores frequently accessed data in memory for faster retrieval. When a request comes in, it first checks the cache before querying the database.",
        expected_type=None,
        discriminating_feature="Pure description, no action required",
        category="description_skip"
    ),
    TypeDiscriminationTestCase(
        input_text="Commit: Once a majority of agents have acknowledged the change, the leader commits it to its local log and broadcasts the commit message to all followers.",
        expected_type=None,
        discriminating_feature="Process description, not instruction",
        category="description_skip"
    ),

    # === STATUS UPDATES - Should NOT be extracted ===
    TypeDiscriminationTestCase(
        input_text="I'm now implementing the changes from the code review. The refactoring is progressing well and should be complete by end of day.",
        expected_type=None,
        discriminating_feature="Present progressive status update, not directive",
        category="status_skip"
    ),
    TypeDiscriminationTestCase(
        input_text="We're currently migrating the database to the new schema. This process involves updating all existing records to match the new format.",
        expected_type=None,
        discriminating_feature="'currently' status update, not decision",
        category="status_skip"
    ),
]


def get_api_key() -> str:
    """Get API key from environment or .env file."""
    for var in ['GOOGLE_API_KEY', 'GEMINI_API_KEY']:
        key = os.environ.get(var)
        if key:
            return key

    # Try .env file
    env_file = os.path.join(os.path.dirname(__file__), '..', '.env')
    if os.path.exists(env_file):
        with open(env_file) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    k, v = line.strip().split('=', 1)
                    if k.strip() in ['GOOGLE_API_KEY', 'GEMINI_API_KEY']:
                        return v.strip().strip('"\'')

    raise ValueError("No API key found")


def run_extraction(text: str, manager: ExtractionManager) -> List[dict]:
    """Run extraction and return concept types found."""
    result = manager.extract_from_file("test.md", text)
    return [{"type": c.type, "content": c.content} for c in result.concepts]


def run_all_tests():
    """Run all type discrimination tests with actual LLM extraction."""
    print("=" * 70)
    print("TYPE DISCRIMINATION TESTS - USING REAL DATABASE SAMPLES")
    print("=" * 70)
    print()

    # Initialize extraction manager
    api_key = get_api_key()
    config = ExtractionConfig(max_retries=2, max_workers=1)
    manager = ExtractionManager(api_key=api_key, config=config)

    results = {
        'passed': [],
        'failed': [],
        'by_category': {}
    }

    for i, case in enumerate(TYPE_DISCRIMINATION_CASES):
        print(f"\nTest {i+1}/{len(TYPE_DISCRIMINATION_CASES)}: {case.input_text[:60]}...")
        print(f"  Expected: {case.expected_type or 'NO EXTRACTION'}")
        print(f"  Feature: {case.discriminating_feature}")

        try:
            # Run extraction
            concepts = run_extraction(case.input_text, manager)

            # Determine actual result
            if not concepts:
                actual_type = None
            else:
                # Get primary concept type (first one)
                actual_type = concepts[0]['type']

            # Compare
            passed = (actual_type == case.expected_type)

            print(f"  Actual: {actual_type or 'NO EXTRACTION'}")
            print(f"  Result: {'PASS' if passed else 'FAIL'}")

            if concepts:
                for c in concepts:
                    print(f"    - [{c['type']}] {c['content'][:60]}...")

            # Record result
            result_record = {
                'case': case,
                'actual': actual_type,
                'concepts': concepts
            }

            if passed:
                results['passed'].append(result_record)
            else:
                results['failed'].append(result_record)

            # Track by category
            if case.category not in results['by_category']:
                results['by_category'][case.category] = {'passed': 0, 'failed': 0}

            if passed:
                results['by_category'][case.category]['passed'] += 1
            else:
                results['by_category'][case.category]['failed'] += 1

            # Rate limiting delay
            time.sleep(0.5)

        except Exception as e:
            print(f"  ERROR: {e}")
            results['failed'].append({
                'case': case,
                'actual': 'ERROR',
                'error': str(e)
            })

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    total = len(TYPE_DISCRIMINATION_CASES)
    passed = len(results['passed'])
    failed = len(results['failed'])

    print(f"\nTotal: {total} | Passed: {passed} | Failed: {failed}")
    print(f"Pass Rate: {passed/total*100:.1f}%")

    print("\nBy Category:")
    for category, counts in results['by_category'].items():
        cat_total = counts['passed'] + counts['failed']
        print(f"  {category}: {counts['passed']}/{cat_total}")

    if results['failed']:
        print("\nFailed Cases:")
        for r in results['failed']:
            case = r['case']
            print(f"  - {case.input_text[:50]}...")
            print(f"    Expected: {case.expected_type or 'NO EXTRACTION'}, Got: {r.get('actual', 'ERROR')}")

    return results


if __name__ == "__main__":
    run_all_tests()
