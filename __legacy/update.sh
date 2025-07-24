#!/bin/bash
set -e

echo "[+] Pulling the latest versions of all service images..."
# This command pulls newer images if they exist, but doesn't change running containers.
docker compose pull

echo "[+] Stopping and removing old containers to apply updates..."
# The 'up -d' command will automatically recreate containers if a newer image was pulled.
# The '--remove-orphans' flag cleans up any old services you might have removed from the compose file.
docker compose up -d --remove-orphans

echo ""
echo "✅ Update process complete. Services have been restarted with the latest pulled images."
echo "Running containers:"
docker compose ps