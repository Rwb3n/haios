# generated: 2025-12-05
# System Auto: last updated on: 2025-12-14 20:22:38
#!/usr/bin/env python3
"""
Memory Retrieval Hook Helper for HAIOS
Standalone script called by UserPromptSubmit.ps1 to inject memory context.

Session 32 Implementation:
- Receives user prompt as argument
- Generates embedding via Google's text-embedding-004
- Searches HAIOS memory database (concepts + artifacts)
- Returns TOON-formatted results for token efficiency

Usage:
    python memory_retrieval.py "user query text"
"""
import sys
import os
import json
import logging
from pathlib import Path

import google.generativeai as genai

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging (errors to stderr, info to file)
log_file = PROJECT_ROOT / '.claude' / 'logs' / 'memory_retrieval.log'
log_file.parent.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stderr),
        logging.FileHandler(str(log_file))
    ]
)
logger = logging.getLogger(__name__)

# Similarity threshold (Session 32: raised to 0.7 for less noise)
SIMILARITY_THRESHOLD = 0.7
MAX_RESULTS = 3  # Reduced from 5 - quality over quantity

# Query rewriting constants (E2-063)
REWRITE_MIN_LENGTH = 10  # Queries shorter than this pass through unchanged
REWRITE_MODEL = "gemini-2.5-flash-lite"  # Fast, unlimited quota - matches extraction.py pattern

# Query rewriting prompt (E2-063 - domain-grounded with few-shot examples)
REWRITE_PROMPT = """Rewrite this conversational query for semantic search in a technical codebase.

Domain: HAIOS - AI agent orchestration system with concepts like coldstart,
checkpoints, memory retrieval, governance hooks, ADRs, backlog items, synthesis.

Remove conversational fluff, expand implicit references, use domain vocabulary.
Return ONLY the rewritten query, no explanation.

Examples:
- "that schema thing" -> "database schema ADR architecture decision"
- "lets check coldstart" -> "HAIOS coldstart session initialization"

Query: {query}"""


def rewrite_query_for_retrieval(query: str) -> str:
    """
    Transform conversational user prompts into technical, retrieval-optimized queries.

    Uses Gemini API to rewrite casual/conversational text into keyword-rich
    technical queries that map better to stored codebase content.

    Args:
        query: Raw user prompt, potentially conversational
               (e.g., "okay sure, lets revisit coldstart")

    Returns:
        Rewritten technical query optimized for semantic search
        (e.g., "HAIOS coldstart command session initialization")
        Falls back to original query on API failure.

    Raises:
        No exceptions raised - graceful fallback on all errors.
    """
    # Short query passthrough - save API calls
    if len(query) < REWRITE_MIN_LENGTH:
        return query

    try:
        # Configure Gemini with API key from environment
        api_key = os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            logger.warning("No GOOGLE_API_KEY for query rewriting, using original query")
            return query

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(REWRITE_MODEL)

        # Generate rewritten query
        prompt = REWRITE_PROMPT.format(query=query)
        response = model.generate_content(prompt)

        rewritten = response.text.strip()

        # Log both for observability
        logger.info(f"Query rewrite: '{query}' -> '{rewritten}'")

        return rewritten

    except Exception as e:
        # Graceful fallback - return original on any error
        logger.warning(f"Query rewrite failed: {e}, using original query")
        return query


def load_env():
    """Load environment variables from .env file."""
    env_path = PROJECT_ROOT / '.env'
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ.setdefault(key.strip(), value.strip())


def format_toon(search_result: dict, query: str) -> str:
    """
    Format results in TOON (Token-Oriented Object Notation) for efficiency.
    Now handles ReasoningAwareRetrieval output with strategies.
    """
    results = search_result.get('results', [])
    reasoning = search_result.get('reasoning', {})
    strategies = reasoning.get('relevant_strategies', [])

    if not results and not strategies:
        return ""

    lines = []
    
    logger.info(f"Formatting results: {len(results)} memories, {len(strategies)} strategies")

    # Filter results by threshold
    filtered = [r for r in results if r.get('score', 0) >= SIMILARITY_THRESHOLD]

    # Add strategies first (high-value reasoning traces)
    if strategies:
        lines.append(f"strategies[{len(strategies)}]{{title,content}}:")
        for s in strategies[:2]:  # Max 2 strategies
            title = s.get('title', 'unknown')[:50]
            content = s.get('content', '')[:150]
            content = content.replace('\n', ' ').replace(',', ';')
            lines.append(f"  {title},{content}")

    # Then add memory results
    if filtered:
        lines.append(f"memory[{len(filtered[:MAX_RESULTS])}]{{type,score,content}}:")
        for r in filtered[:MAX_RESULTS]:
            content = r.get('content', '')[:150]
            content = content.replace('\n', ' ').replace(',', ';')
            score = f"{r.get('score', 0):.2f}"
            rtype = r.get('type', 'unknown')
            lines.append(f"  {rtype},{score},{content}")

    return '\n'.join(lines) if lines else ""


def search_memory(query: str) -> dict:
    """
    Search HAIOS memory database with ReasoningBank-aware retrieval.
    Uses ReasoningAwareRetrieval for strategy-informed search.

    Session 32 upgrade: Now uses full ReasoningBank pattern:
    - Finds similar past reasoning traces
    - Applies learned strategies
    - Records attempt for future learning
    """
    from haios_etl.database import DatabaseManager
    from haios_etl.extraction import ExtractionManager
    from haios_etl.retrieval import ReasoningAwareRetrieval

    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        logger.error("GOOGLE_API_KEY not set")
        return {'results': [], 'reasoning': {'outcome': 'failure', 'error': 'No API key'}}

    db_path = PROJECT_ROOT / 'haios_memory.db'
    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        return {'results': [], 'reasoning': {'outcome': 'failure', 'error': 'No database'}}

    try:
        db = DatabaseManager(str(db_path))
        extractor = ExtractionManager(api_key)
        retrieval = ReasoningAwareRetrieval(db, extractor)

        # E2-063: Rewrite conversational queries for better retrieval
        rewritten_query = rewrite_query_for_retrieval(query)

        logger.info(f"Searching DB: {db_path} for query: {query} (rewritten: {rewritten_query})")

        # Use full ReasoningBank search with experience learning
        # ADR-037: session_recovery mode excludes SynthesizedInsight concepts
        # E2-063: Use rewritten query for better semantic matching
        result = retrieval.search_with_experience(
            query=rewritten_query,
            space_id=None,
            filters=None,
            mode='session_recovery'
        )

        return result

    except Exception as e:
        logger.error(f"Search failed: {e}")
        return {'results': [], 'reasoning': {'outcome': 'failure', 'error': str(e)}}


def main():
    """Main entry point for hook invocation."""
    if len(sys.argv) < 2:
        # No query provided - silent exit
        sys.exit(0)

    query = ' '.join(sys.argv[1:])

    if len(query.strip()) < 5:
        # Query too short - skip memory retrieval
        sys.exit(0)

    # Load environment
    load_env()

    logger.info(f"Memory Retrieval Started. Query: {query}")

    # Search memory with ReasoningBank pattern
    search_result = search_memory(query)

    # Format and output (includes strategies + memories)
    toon_output = format_toon(search_result, query)

    if toon_output:
        # Show learning metadata
        reasoning = search_result.get('reasoning', {})
        learned_from = reasoning.get('learned_from', 0)
        strategy = reasoning.get('strategy_used', 'default')

        print(f"\n--- Memory Context (learned_from: {learned_from}, strategy: {strategy}) ---")
        print(toon_output)
        print("--- End Memory Context ---\n")

    sys.exit(0)


if __name__ == '__main__':
    main()
