#!/usr/bin/env bash
# MCP Server Configuration for HAIOS Project

# Get the absolute path to the project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# SQLite databases
NOCODB_DB="${PROJECT_ROOT}/data/nocodb/noco.db"
LANGFLOW_DB="${PROJECT_ROOT}/data/langflow/langflow.db"

# Function to start Claude with MCP servers
start_claude_with_mcp() {
    echo "Starting Claude Code with MCP servers configured for HAIOS..."
    
    # Check if databases exist
    if [[ ! -f "$NOCODB_DB" ]]; then
        echo "⚠️  Warning: NocoDB database not found at $NOCODB_DB"
        echo "   Make sure to run ./setup.sh and ./start.sh first"
    fi
    
    if [[ ! -f "$LANGFLOW_DB" ]]; then
        echo "⚠️  Warning: Langflow database not found at $LANGFLOW_DB"
        echo "   Make sure to run ./setup.sh and ./start.sh first"
    fi
    
    # Start Claude with all MCP servers
    claude \
        --mcp-server "filesystem:${PROJECT_ROOT}" \
        --mcp-server memory \
        --mcp-server "sqlite:${NOCODB_DB} ${LANGFLOW_DB}" \
        "$@"
}

# Function to display MCP configuration
show_mcp_config() {
    cat << EOF
HAIOS MCP Server Configuration:
===============================
• Filesystem Server: ${PROJECT_ROOT}
• Memory Server: Enabled
• SQLite Databases:
  - NocoDB: ${NOCODB_DB}
  - Langflow: ${LANGFLOW_DB}

To start Claude with these MCP servers:
  ./mcp-config.sh

Or manually:
  claude --mcp-server "filesystem:${PROJECT_ROOT}" --mcp-server memory --mcp-server "sqlite:${NOCODB_DB} ${LANGFLOW_DB}"
EOF
}

# Main execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    # Script is being executed directly
    if [[ "$1" == "--info" ]]; then
        show_mcp_config
    else
        start_claude_with_mcp "$@"
    fi
fi