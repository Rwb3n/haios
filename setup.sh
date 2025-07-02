#!/usr/bin/env bash
set -e

# Load env vars
source .env

# Create data dirs
mkdir -p data/n8n data/nocodb data/langflow

# Start services
docker compose up -d

# Print URLs
echo "n8n    -> http://localhost:${N8N_PORT}"
echo "NocoDB -> http://localhost:${NOCODB_PORT}"
echo "Langflow -> http://localhost:${LANGFLOW_PORT}"
