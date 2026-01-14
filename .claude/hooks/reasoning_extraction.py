# generated: 2025-12-05
# System Auto: last updated on: 2025-12-06 22:11:13
#!/usr/bin/env python3
"""
Reasoning Extraction Hook Helper for HAIOS
Standalone script called by Stop.ps1 to extract learnings from completed sessions.

Session 33 Implementation (Closes the ReasoningBank Loop):
- Receives transcript_path from Stop hook
- Parses JSONL transcript to extract:
  - Initial user query (the task)
  - Tools used and their outcomes
  - Overall session outcome (success/failure)
- Stores reasoning trace with strategy extraction via LLM

Usage:
    python reasoning_extraction.py "path/to/transcript.jsonl"

The ReasoningBank Loop:
    RETRIEVE (UserPromptSubmit) -> INJECT -> EXECUTE -> EXTRACT (Stop) -> STORE
                                                              ^
                                                              |
                                                        THIS SCRIPT
"""
import sys
import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

# Configure logging
# Configure logging (info to stderr and file)
log_file = PROJECT_ROOT / '.claude' / 'logs' / 'reasoning_extraction.log'
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

# Minimum conversation length to consider for extraction
MIN_MESSAGES_FOR_EXTRACTION = 3
# Skip extraction for trivial sessions
MIN_TOOL_CALLS = 1


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


def parse_transcript(transcript_path: str) -> Dict:
    """
    Parse JSONL transcript file to extract session information.

    Returns:
        Dict with:
        - initial_query: First user message
        - tools_used: List of tools invoked
        - tool_outcomes: Summary of tool results
        - message_count: Total messages
        - has_errors: Whether errors occurred
        - final_summary: Last assistant message (often contains summary)
    """
    messages = []
    tools_used = []
    tool_outcomes = []
    errors = []

    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)

                    # Skip non-dict entries (e.g., strings, numbers)
                    if not isinstance(entry, dict):
                        continue

                    messages.append(entry)

                    # Track tool usage - Claude Code nests tool calls in message.content
                    entry_type = entry.get('type', '')

                    # Direct tool_use entry (legacy format)
                    if entry_type == 'tool_use':
                        tool_name = entry.get('name', 'unknown')
                        tools_used.append(tool_name)

                    # Assistant message with tool_use in content (Claude Code format)
                    elif entry_type == 'assistant':
                        message = entry.get('message', {})
                        if isinstance(message, dict):
                            content = message.get('content', [])
                            if isinstance(content, list):
                                for item in content:
                                    if isinstance(item, dict) and item.get('type') == 'tool_use':
                                        tool_name = item.get('name', 'unknown')
                                        tools_used.append(tool_name)

                    # Track tool results - also check nested format
                    if entry_type == 'tool_result':
                        is_error = entry.get('is_error', False)
                        if is_error:
                            errors.append(entry.get('content', '')[:200])
                        tool_outcomes.append({
                            'success': not is_error,
                            'preview': str(entry.get('content', ''))[:100]
                        })

                    # User message with tool_result in content (Claude Code format)
                    elif entry_type == 'user':
                        message = entry.get('message', {})
                        if isinstance(message, dict):
                            content = message.get('content', [])
                            if isinstance(content, list):
                                for item in content:
                                    if isinstance(item, dict) and item.get('type') == 'tool_result':
                                        # Check toolUseResult for success/failure
                                        # Note: toolUseResult can be dict or string
                                        tool_result = entry.get('toolUseResult', {})
                                        if isinstance(tool_result, dict):
                                            is_error = not tool_result.get('success', True)
                                        elif isinstance(tool_result, str):
                                            # String result - check if it looks like an error
                                            is_error = 'error' in tool_result.lower() or 'exit code' in tool_result.lower()
                                        else:
                                            is_error = False
                                        result_content = item.get('content', '')
                                        if is_error:
                                            errors.append(str(result_content)[:200])
                                        tool_outcomes.append({
                                            'success': not is_error,
                                            'preview': str(result_content)[:100]
                                        })

                except json.JSONDecodeError:
                    continue

    except Exception as e:
        logger.error(f"Failed to read transcript: {e}")
        return {}

    # Extract initial query (first human/user message that is NOT a continuation summary)
    # Skip messages that start with continuation/summary text from compacted sessions
    SKIP_PREFIXES = [
        "This session is being continued",
        "Analysis:",
        "Summary:",
        "<system-reminder>",
        "Caveat:",
    ]

    initial_query = ""
    for msg in messages:
        if not isinstance(msg, dict):
            continue
        msg_type = msg.get('type', '')
        candidate_query = ""

        # Check for user type with nested message
        if msg_type == 'user':
            message = msg.get('message', {})
            if isinstance(message, dict):
                content = message.get('content', [])
                if isinstance(content, list):
                    for part in content:
                        if isinstance(part, dict) and part.get('type') == 'text':
                            candidate_query = part.get('text', '')[:500]
                            break
                elif isinstance(content, str):
                    candidate_query = content[:500]
        # Legacy format with role
        elif msg.get('role') == 'user':
            content = msg.get('content', '')
            if isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get('type') == 'text':
                        candidate_query = part.get('text', '')[:500]
                        break
            else:
                candidate_query = str(content)[:500]

        # Check if this is a real query (not a continuation/system message)
        if candidate_query:
            is_continuation = any(candidate_query.strip().startswith(prefix) for prefix in SKIP_PREFIXES)
            if not is_continuation:
                initial_query = candidate_query
                break

    # Extract final assistant summary
    final_summary = ""
    for msg in reversed(messages):
        if not isinstance(msg, dict):
            continue
        msg_type = msg.get('type', '')
        # Check for assistant type with nested message
        if msg_type == 'assistant':
            message = msg.get('message', {})
            if isinstance(message, dict):
                content = message.get('content', [])
                if isinstance(content, list):
                    # Look for text content
                    for part in content:
                        if isinstance(part, dict) and part.get('type') == 'text':
                            final_summary = part.get('text', '')[:500]
                            break
                elif isinstance(content, str):
                    final_summary = content[:500]
                if final_summary:
                    break
        # Legacy format
        elif msg.get('role') == 'assistant':
            content = msg.get('content', '')
            if isinstance(content, str):
                final_summary = content[:500]
            if final_summary:
                break

    return {
        'initial_query': initial_query,
        'tools_used': list(set(tools_used)),  # Unique tools
        'tool_count': len(tools_used),
        'tool_outcomes': tool_outcomes,
        'message_count': len(messages),
        'has_errors': len(errors) > 0,
        'error_samples': errors[:3],  # Max 3 error samples
        'final_summary': final_summary
    }


def should_extract(session_info: Dict) -> Tuple[bool, str]:
    """
    Determine if this session is worth extracting learnings from.

    Returns:
        (should_extract: bool, reason: str)
    """
    if not session_info:
        return False, "empty_session"

    if session_info.get('message_count', 0) < MIN_MESSAGES_FOR_EXTRACTION:
        return False, "too_short"

    if session_info.get('tool_count', 0) < MIN_TOOL_CALLS:
        return False, "no_tool_usage"

    query = session_info.get('initial_query', '')
    # Skip trivial queries
    trivial_patterns = ['hello', 'hi', 'hey', 'thanks', 'bye', 'ok', 'yes', 'no']
    if query.lower().strip() in trivial_patterns:
        return False, "trivial_query"

    return True, "qualified"


def determine_outcome(session_info: Dict) -> str:
    """Determine overall session outcome."""
    if session_info.get('has_errors'):
        # Check if errors were recovered
        outcomes = session_info.get('tool_outcomes', [])
        if outcomes:
            success_rate = sum(1 for o in outcomes if o.get('success')) / len(outcomes)
            if success_rate >= 0.7:
                return "partial_success"
            return "failure"
    return "success"


def extract_and_store(session_info: Dict) -> bool:
    """
    Extract learnings and store as reasoning trace.

    Uses ReasoningAwareRetrieval.record_reasoning_trace() to store,
    which internally uses LLM to extract transferable strategies.
    """
    from haios_etl.database import DatabaseManager
    from haios_etl.extraction import ExtractionManager
    from haios_etl.retrieval import ReasoningAwareRetrieval

    api_key = os.environ.get('GOOGLE_API_KEY')
    if not api_key:
        logger.error("GOOGLE_API_KEY not set")
        return False

    db_path = PROJECT_ROOT / 'haios_memory.db'
    if not db_path.exists():
        logger.error(f"Database not found: {db_path}")
        return False

    try:
        db = DatabaseManager(str(db_path))
        extractor = ExtractionManager(api_key)
        retrieval = ReasoningAwareRetrieval(db, extractor)

        query = session_info['initial_query']
        outcome = determine_outcome(session_info)

        # Generate embedding for the query (using retrieval's internal method)
        query_embedding = retrieval._generate_embedding(query)

        # Build approach description
        tools_str = ', '.join(session_info.get('tools_used', [])[:5])
        approach = f"Used tools: {tools_str}"

        # Build results summary
        results_summary = session_info.get('final_summary', '')[:300]

        # Build error details
        error_details = ""
        if session_info.get('has_errors'):
            error_details = "; ".join(session_info.get('error_samples', []))[:300]

        # Record the reasoning trace (this calls extract_strategy internally)
        retrieval.record_reasoning_trace(
            query=query,
            query_embedding=query_embedding,
            approach=approach,
            strategy_details={'tools': session_info.get('tools_used', [])},
            outcome=outcome,
            memories_used=[],  # Stop hook doesn't track which memories were used
            execution_time_ms=0,  # Not tracked at hook level
            space_id=None,
            results_summary=results_summary,
            error_details=error_details
        )

        logger.info(f"Extracted reasoning trace: query='{query[:50]}...', outcome={outcome}")
        return True

    except Exception as e:
        logger.error(f"Extraction failed: {e}")
        return False


def main():
    """Main entry point for Stop hook invocation."""
    if len(sys.argv) < 2:
        logger.error("No transcript path provided")
        sys.exit(1)

    transcript_path = sys.argv[1]

    if not os.path.exists(transcript_path):
        logger.error(f"Transcript not found: {transcript_path}")
        sys.exit(1)

    # Load environment
    load_env()

    # Parse transcript
    session_info = parse_transcript(transcript_path)
    logger.info(f"Parsed transcript: {transcript_path} ({session_info.get('message_count')} items)")

    # Check if extraction is warranted
    should, reason = should_extract(session_info)

    if not should:
        logger.info(f"Skipping extraction: {reason}")
        sys.exit(0)

    # Extract and store learnings
    success = extract_and_store(session_info)

    if success:
        print("Learning extracted and stored")
        logger.info("Extraction complete: SUCCESS")
    else:
        logger.warning("Extraction complete: FAILED")

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
