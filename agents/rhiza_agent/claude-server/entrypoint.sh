#!/bin/bash
set -e

# Verify Claude CLI is installed
if ! command -v claude &> /dev/null; then
    echo "Claude CLI not found. Installing..."
    curl -fsSL https://console.anthropic.com/install.sh | sh
fi

# Verify API key is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "ERROR: ANTHROPIC_API_KEY environment variable is not set"
    exit 1
fi

# Log startup
echo "Starting Claude MCP Server..."
echo "Project directory: $(pwd)"
echo "Claude version: $(claude --version 2>/dev/null || echo 'unknown')"

# Check if CLAUDE.md exists
if [ -f "CLAUDE.md" ]; then
    echo "Found CLAUDE.md in project root"
else
    echo "WARNING: CLAUDE.md not found in project root"
fi

# Execute the command passed to the container
exec "$@"