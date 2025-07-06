#!/usr/bin/env bash
set -euo pipefail

# ----------------------------------------------------------------------------
# start.sh: Launch services and display URLs
# ----------------------------------------------------------------------------

# Load environment variables (strip CRLF if present)
if [[ -f .env ]]; then
  if grep -q $'\r' .env; then
    sed -i 's/\r$//' .env
  fi
  set -o allexport
  source .env
  set +o allexport
else
  echo "❌ .env file not found. Please create it before running this script."
  exit 1
fi

# Ensure netcat is available for health checks
if ! command -v nc &>/dev/null; then
  echo "❌ 'nc' (netcat) is required for health checks. Install it and retry."
  exit 1
fi

# Start Docker Compose services
echo "[+] Starting Docker Compose services..."
docker compose up -d

# Health check: wait for each port
wait_for() {
  local port="$1" name="$2"
  echo -n "[+] Waiting for $name on port $port..."
  until nc -z localhost "$port"; do
    echo -n "."
    sleep 2
  done
  echo " done"
}

wait_for "$N8N_PORT" "n8n"
wait_for "$NOCODB_PORT" "NocoDB"
wait_for "${LANGFLOW_PORT:-7860}" "Langflow"

# Display service URLs
cat << EOF

✅ Services are up and running:
   • n8n      → http://localhost:${N8N_PORT}
   • NocoDB   → http://localhost:${NOCODB_PORT}
   • Langflow → http://localhost:${LANGFLOW_PORT:-7860}
EOF
