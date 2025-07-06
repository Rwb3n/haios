#!/usr/bin/env bash
# MCP Server Configuration for HAIOS Project

# Get the absolute path to the project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# SQLite databases
NOCODB_DB="${PROJECT_ROOT}/data/nocodb/noco.db"
LANGFLOW_DB="${PROJECT_ROOT}/data/langflow/langflow.db"

# Function to configure MCP servers
configure_mcp_servers() {
    echo "Configuring MCP servers for HAIOS project..."
    
    # Check if databases exist
    if [[ ! -f "$NOCODB_DB" ]]; then
        echo "⚠️  Warning: NocoDB database not found at $NOCODB_DB"
        echo "   Make sure to run ./setup.sh and ./start.sh first"
    fi
    
    if [[ ! -f "$LANGFLOW_DB" ]]; then
        echo "⚠️  Warning: Langflow database not found at $LANGFLOW_DB"
        echo "   Make sure to run ./setup.sh and ./start.sh first"
    fi
    
    # Add filesystem server
    echo "Adding filesystem server..."
    claude mcp add --scope project haios-filesystem npx @modelcontextprotocol/server-filesystem "${PROJECT_ROOT}"
    
    # Add memory server
    echo "Adding memory server..."
    claude mcp add --scope project haios-memory npx @modelcontextprotocol/server-memory
    
    # Add SQLite server for NocoDB
    if [[ -f "$NOCODB_DB" ]]; then
        echo "Adding SQLite server for NocoDB..."
        claude mcp add --scope project haios-nocodb npx @modelcontextprotocol/server-sqlite "${NOCODB_DB}"
    fi
    
    # Add SQLite server for Langflow
    if [[ -f "$LANGFLOW_DB" ]]; then
        echo "Adding SQLite server for Langflow..."
        claude mcp add --scope project haios-langflow npx @modelcontextprotocol/server-sqlite "${LANGFLOW_DB}"
    fi
    
    # Add Playwright server
    echo "Adding Playwright server..."
    claude mcp add --scope project haios-playwright npx @playwright/mcp@latest
    
    echo ""
    echo "✅ MCP servers configured successfully!"
    echo ""
    echo "To view configured servers:"
    echo "  claude mcp list"
    echo ""
    echo "To start Claude with these servers:"
    echo "  claude"
}

# Function to display current MCP configuration
show_mcp_config() {
    echo "HAIOS MCP Server Configuration:"
    echo "==============================="
    echo ""
    echo "To view currently configured MCP servers:"
    echo "  claude mcp list"
    echo ""
    echo "Expected servers:"
    echo "• haios-filesystem: File access to ${PROJECT_ROOT}"
    echo "• haios-memory: Knowledge graph for context persistence"
    echo "• haios-nocodb: SQLite access to ${NOCODB_DB}"
    echo "• haios-langflow: SQLite access to ${LANGFLOW_DB}"
    echo "• haios-playwright: Browser automation capabilities"
    echo ""
    echo "To reconfigure servers:"
    echo "  ./mcp-config.sh setup"
}

# Function to remove existing HAIOS MCP servers
remove_mcp_servers() {
    echo "Removing existing HAIOS MCP servers..."
    claude mcp remove haios-filesystem 2>/dev/null
    claude mcp remove haios-memory 2>/dev/null
    claude mcp remove haios-nocodb 2>/dev/null
    claude mcp remove haios-langflow 2>/dev/null
    claude mcp remove haios-playwright 2>/dev/null
    echo "✅ Existing servers removed"
}

# Function to cleanup duplicate MCP servers
cleanup_duplicates() {
    echo "Cleaning up duplicate and unnecessary MCP servers..."
    
    # Remove non-haios prefixed duplicates
    echo "Removing duplicate filesystem server..."
    claude mcp remove filesystem 2>/dev/null
    
    echo "Removing duplicate memory server..."
    claude mcp remove memory 2>/dev/null
    
    echo "Removing duplicate nocodb-sqlite server..."
    claude mcp remove nocodb-sqlite 2>/dev/null
    
    echo "Removing duplicate langflow-sqlite server..."
    claude mcp remove langflow-sqlite 2>/dev/null
    
    echo "Removing brave-search server..."
    claude mcp remove brave-search 2>/dev/null
    
    echo ""
    echo "✅ Duplicate and unnecessary servers cleaned up"
    echo ""
    echo "Remaining MCP servers:"
    claude mcp list
}

# Main execution
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    case "$1" in
        setup)
            configure_mcp_servers
            ;;
        remove)
            remove_mcp_servers
            ;;
        cleanup)
            cleanup_duplicates
            ;;
        --info|info)
            show_mcp_config
            ;;
        *)
            echo "Usage: $0 {setup|remove|cleanup|info}"
            echo ""
            echo "Commands:"
            echo "  setup   - Configure all MCP servers for HAIOS"
            echo "  remove  - Remove all HAIOS MCP servers"
            echo "  cleanup - Remove duplicate non-HAIOS MCP servers"
            echo "  info    - Display current configuration info"
            echo ""
            echo "After setup, start Claude normally with: claude"
            ;;
    esac
fi