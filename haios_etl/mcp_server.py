# generated: 2025-11-30
# System Auto: last updated on: 2025-12-14 13:17:48
import os
import logging
import json
from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv

# TOON for token-efficient serialization (Session 31)
try:
    from toon import encode as toon_encode
    TOON_AVAILABLE = True
except ImportError:
    TOON_AVAILABLE = False

from .database import DatabaseManager
from .extraction import ExtractionManager
from .retrieval import ReasoningAwareRetrieval

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize services
DB_PATH = os.getenv("DB_PATH", "haios_memory.db")
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    logger.warning("GOOGLE_API_KEY not found in environment variables. Embeddings will fail.")

# Initialize managers
db_manager = DatabaseManager(DB_PATH)
extraction_manager = ExtractionManager(api_key=API_KEY or "dummy")
retrieval_service = ReasoningAwareRetrieval(db_manager, extraction_manager)

# Create MCP Server
mcp = FastMCP("haios-memory")

@mcp.tool()
def memory_search_with_experience(query: str, space_id: str = None, mode: str = 'semantic') -> str:
    """
    Search memory with automatic learning from past attempts (ReasoningBank).

    Args:
        query: The search query.
        space_id: Optional space ID (e.g., 'dev_copilot', 'salesforce').
        mode: Retrieval mode (Session 72 - ADR-037):
            - 'semantic': Pure semantic similarity (default)
            - 'session_recovery': Excludes synthesis, for coldstart
            - 'knowledge_lookup': Filters to episteme/techne/actionable types

    Returns:
        TOON-encoded string (57% smaller than JSON) containing results and reasoning trace.
    """
    try:
        result = retrieval_service.search_with_experience(query, space_id=space_id, mode=mode)

        # Use TOON for token-efficient output (Session 31)
        if TOON_AVAILABLE:
            return toon_encode(result)
        else:
            return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return json.dumps({"error": str(e)})

@mcp.tool()
def memory_stats() -> str:
    """Get statistics about the memory database."""
    try:
        stats = db_manager.get_stats()
        stats['status'] = "online"
        stats['db_path'] = DB_PATH
        return json.dumps(stats, indent=2)
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return json.dumps({"error": str(e), "status": "error"})


@mcp.tool()
def marketplace_list_agents(capability: str = None) -> str:
    """
    List available agents in the marketplace, optionally filtering by capability.
    
    Args:
        capability: Optional capability to filter by (e.g., 'vision-alignment', 'knowledge-classification')
    """
    try:
        agents = db_manager.list_agents(capability)
        if not agents:
            return "No agents found matching criteria."
        
        # Format as a readable list
        output = ["## Available Agents"]
        for agent in agents:
            output.append(f"- **{agent['name']}** (v{agent['version']}) - {agent['type']}")
            output.append(f"  ID: `{agent['id']}`")
            output.append(f"  Description: {agent['description']}")
            if agent['capabilities']:
                output.append(f"  Capabilities: {', '.join(agent['capabilities'])}")
            output.append("")
            
        return "\n".join(output)
    except Exception as e:
        return f"Error listing agents: {str(e)}"

@mcp.tool()
def marketplace_get_agent(agent_id: str) -> str:
    """
    Retrieve full details for a specific agent, including its input/output schema.
    
    Args:
        agent_id: The ID of the agent to retrieve
    """
    try:
        agent = db_manager.get_agent(agent_id)
        if not agent:
            return f"Agent not found: {agent_id}"
            
        return json.dumps(agent, indent=2)
    except Exception as e:
        return f"Error retrieving agent: {str(e)}"


# Valid content types (Greek Triad)
VALID_CONTENT_TYPES = {"episteme", "techne", "doxa"}


@mcp.tool()
def memory_store(
    content: str,
    content_type: str,
    source_path: str,
    metadata: str = None
) -> str:
    """
    [DEPRECATED] Store content in memory with Greek Triad classification.

    NOTE: This tool is deprecated. Use `ingester_ingest` instead, which provides:
    - Auto-classification (no manual content_type required)
    - Entity extraction
    - Provenance tracking
    - No metadata JSON string issues

    Args:
        content: The content to store.
        content_type: Classification type - one of 'episteme' (knowledge/facts),
                      'techne' (practical skills/how-to), or 'doxa' (opinions/beliefs).
        source_path: The source file path for provenance.
        metadata: Optional JSON string with additional metadata.

    Returns:
        Confirmation message with stored concept ID (includes deprecation warning).
    """
    try:
        # Validate content type
        if content_type not in VALID_CONTENT_TYPES:
            return f"Error: Invalid content_type '{content_type}'. Must be one of: {', '.join(VALID_CONTENT_TYPES)}"

        # Parse metadata if provided
        meta_dict = {}
        if metadata:
            try:
                meta_dict = json.loads(metadata)
            except json.JSONDecodeError:
                return "Error: Invalid JSON in metadata parameter"

        # Store as concept with the content type
        concept_id = db_manager.insert_concept(
            type=content_type,
            name=content[:100],  # Use first 100 chars as name
            description=content
        )

        # Store metadata if provided (using memory_metadata table if exists)
        if meta_dict:
            # For MVP, include metadata in the response
            logger.info(f"Stored concept {concept_id} with metadata: {meta_dict}")

        # Add deprecation warning to successful response
        deprecation_notice = "[DEPRECATED: Use ingester_ingest instead] "
        return f"{deprecation_notice}Successfully stored content as {content_type}. Concept ID: {concept_id}. Source: {source_path}"

    except Exception as e:
        logger.error(f"Error storing content: {e}")
        return f"[DEPRECATED: Use ingester_ingest instead] Error storing content: {str(e)}"


@mcp.tool()
def extract_content(
    file_path: str,
    content: str,
    extraction_mode: str = "full"
) -> str:
    """
    Extract entities and concepts from content using LLM-based extraction.

    Args:
        file_path: Path to the source file (for context and provenance).
        content: The text content to extract from.
        extraction_mode: Mode of extraction - 'full' (default), 'entities_only', or 'concepts_only'.

    Returns:
        JSON string containing extracted entities and concepts.
    """
    try:
        # Perform extraction
        result = extraction_manager.extract_from_file(file_path, content)

        # Build response based on mode
        response = {
            "file_path": file_path,
            "extraction_mode": extraction_mode,
        }

        if extraction_mode in ("full", "entities_only"):
            response["entities"] = [
                {"type": e.type, "value": e.value}
                for e in result.entities
            ]

        if extraction_mode in ("full", "concepts_only"):
            response["concepts"] = [
                {"type": c.type, "content": c.content, "source_adr": c.source_adr}
                for c in result.concepts
            ]

        response["summary"] = {
            "entities_count": len(result.entities) if extraction_mode != "concepts_only" else 0,
            "concepts_count": len(result.concepts) if extraction_mode != "entities_only" else 0,
        }

        return json.dumps(response, indent=2)

    except Exception as e:
        logger.error(f"Error extracting content: {e}")
        return json.dumps({"error": str(e), "file_path": file_path})

# =============================================================================
# AGENT TOOLS (Session 18 - PLAN-AGENT-ECOSYSTEM-001 Phase 2)
# DD-020: Hybrid architecture - Python modules with MCP wrappers
# =============================================================================

@mcp.tool()
def interpreter_translate(intent: str) -> str:
    """
    Translate operator intent to system directive.

    Uses the Interpreter agent (DD-012 to DD-014) to convert natural language
    intent into structured system directives with confidence scoring.

    Args:
        intent: Natural language operator intent (e.g., "find all ADRs about security")

    Returns:
        JSON string containing:
        - directive: Structured system directive
        - confidence: 0.0-1.0 confidence score
        - grounded: Whether relevant context was found
        - context_used: Memory items used for grounding
    """
    try:
        from dataclasses import asdict
        from .agents.interpreter import Interpreter, InterpreterConfig

        config = InterpreterConfig(use_llm=True, fallback_to_rules=True)
        interpreter = Interpreter(config=config, db_manager=db_manager, api_key=API_KEY)
        result = interpreter.translate(intent)

        return json.dumps(asdict(result), indent=2)

    except Exception as e:
        logger.error(f"Interpreter translation failed: {e}")
        return json.dumps({"error": str(e), "intent": intent})


@mcp.tool()
def ingester_ingest(
    content: str,
    source_path: str,
    content_type_hint: str = "unknown"
) -> str:
    """
    Ingest content into memory with classification.

    Uses the Ingester agent (DD-015 to DD-019) to classify content using the
    Greek Triad taxonomy and store it with provenance tracking.

    Args:
        content: The text content to ingest
        source_path: Source file path for provenance tracking
        content_type_hint: Classification hint - 'episteme' (knowledge/facts),
                          'techne' (how-to/skills), 'doxa' (opinions), or 'unknown' (auto-classify)

    Returns:
        JSON string containing:
        - concept_ids: IDs of stored concepts
        - entity_ids: IDs of stored entities
        - classification: Final classification (episteme/techne/doxa)
        - ingested_by_agent: Agent ID for provenance
    """
    try:
        from dataclasses import asdict
        from .agents.ingester import Ingester, IngesterConfig

        config = IngesterConfig(max_retries=3, backoff_base=2.0, timeout_seconds=30)
        # E2-FIX-002: Pass extraction_manager for embedding generation
        ingester = Ingester(
            db_manager=db_manager,
            config=config,
            api_key=API_KEY,
            extractor=extraction_manager
        )
        result = ingester.ingest(content, source_path, content_type_hint)

        return json.dumps(asdict(result), indent=2)

    except Exception as e:
        logger.error(f"Ingester ingest failed: {e}")
        return json.dumps({"error": str(e), "source_path": source_path})



# =============================================================================
# SCHEMA INTROSPECTION TOOLS (Session 53 - E2-020 fix)
# Abstraction layer for database schema queries - replaces direct SQL via Bash
# =============================================================================

@mcp.tool()
def schema_info(table_name: str = None) -> str:
    """
    Get database schema information.

    Use this instead of direct SQL queries to inspect database structure.
    Abstracted from underlying database - portable across SQLite/Postgres.

    Args:
        table_name: Optional table name. If provided, returns columns for that table.
                   If omitted, returns list of all tables.

    Returns:
        JSON with table/column info.
    """
    try:
        result = db_manager.get_schema_info(table_name)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"Schema info failed: {e}")
        return json.dumps({"error": str(e)})


@mcp.tool()
def db_query(sql: str) -> str:
    """
    Execute a read-only SQL query against the memory database.

    ONLY SELECT queries are allowed. INSERT/UPDATE/DELETE/DROP are blocked.
    Use this for verification and debugging, not for data modification.

    Args:
        sql: SELECT query to execute

    Returns:
        JSON with columns, rows, and row_count - or error message.
    """
    try:
        result = db_manager.query_read_only(sql)
        return json.dumps(result, indent=2)
    except Exception as e:
        logger.error(f"DB query failed: {e}")
        return json.dumps({"error": str(e)})


if __name__ == "__main__":
    # Initialize DB (ensure schema is up to date)
    # Note: In production, schema migration should be separate, but for MVP we run setup here
    # to ensure new tables exist.
    db_manager.setup()
    mcp.run()

