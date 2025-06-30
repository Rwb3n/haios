#!/bin/bash
set -e

echo "[+] Creating data directories..."
mkdir -p data/n8n data/nocodb agent docs

echo "[+] Starting Docker services..."
docker compose up -d

echo ""
echo "✅ n8n        → http://localhost:${N8N_PORT}"
echo "✅ NocoDB     → http://localhost:${NOCODB_PORT}"
echo "✅ Langflow   → http://localhost:${LANGFLOW_PORT}"
echo "✅ Markdown   → http://localhost:${MARKDOWN_PORT}"