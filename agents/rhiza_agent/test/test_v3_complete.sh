#!/bin/bash
# Complete test script for Rhiza v3 architecture with all phases

echo "=== Rhiza v3 Complete Test Suite ==="
echo "Testing all three phases with Claude-as-a-Service architecture"
echo "==========================================================="

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if ANTHROPIC_API_KEY is set
if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo -e "${YELLOW}WARNING: ANTHROPIC_API_KEY not set. Will use mock MCP client.${NC}"
    export USE_MOCK_LLM=true
else
    echo -e "${GREEN}ANTHROPIC_API_KEY found. Will attempt to use real Claude server.${NC}"
    export USE_MOCK_LLM=false
fi

# Base directory (go up one level from test/)
cd "$(dirname "$0")/.."

# Test Phase 1 (v3)
echo -e "\n${YELLOW}Testing Phase 1: Strategic Triage (v3)${NC}"
echo "Categories: cs.AI, cs.DC"
python3 adapters/phase1_strategic_triage_v3.py

# Check if priorities file was created
PRIORITY_FILE=$(ls -t reports/phase1_priorities/priorities_*.json 2>/dev/null | head -1)
if [ -z "$PRIORITY_FILE" ]; then
    echo -e "${RED}ERROR: Phase 1 failed to create priorities file${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Phase 1 completed. Output: $PRIORITY_FILE${NC}"

# Extract first theme for Phase 2
THEME=$(python3 -c "
import json
with open('$PRIORITY_FILE') as f:
    data = json.load(f)
    if data['priorities']:
        print(data['priorities'][0]['theme'])
")

if [ -z "$THEME" ]; then
    echo -e "${RED}ERROR: No themes found in Phase 1 output${NC}"
    exit 1
fi

# Test Phase 2 (v3)
echo -e "\n${YELLOW}Testing Phase 2: Tactical Ingestion (v3)${NC}"
echo "Topic: $THEME"
python3 adapters/phase2_tactical_ingestion_v3.py --topic "$THEME"

# Check if triage file was created
TRIAGE_FILE=$(ls -t reports/phase2_triage/triage_*.json 2>/dev/null | head -1)
if [ -z "$TRIAGE_FILE" ]; then
    echo -e "${RED}ERROR: Phase 2 failed to create triage file${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Phase 2 completed. Output: $TRIAGE_FILE${NC}"

# Extract first Tier 1 paper for Phase 3
PAPER_ID=$(python3 -c "
import json
with open('$TRIAGE_FILE') as f:
    data = json.load(f)
    if data['tier_1_papers']:
        print(data['tier_1_papers'][0]['paper_id'])
")

if [ -z "$PAPER_ID" ]; then
    echo -e "${YELLOW}No Tier 1 papers found. Skipping Phase 3.${NC}"
else
    # Test Phase 3 (v3)
    echo -e "\n${YELLOW}Testing Phase 3: Crystal Seed Extraction (v3)${NC}"
    echo "Paper ID: $PAPER_ID"
    python3 adapters/phase3_crystal_seed_v3.py --paper-id "$PAPER_ID"
    
    # Check if crystal seed file was created
    CRYSTAL_FILE=$(ls -t reports/phase3_crystal_seeds/crystal_*.json 2>/dev/null | head -1)
    if [ -z "$CRYSTAL_FILE" ]; then
        echo -e "${RED}ERROR: Phase 3 failed to create crystal seed file${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Phase 3 completed. Output: $CRYSTAL_FILE${NC}"
fi

# Summary
echo -e "\n${GREEN}=== v3 Test Complete ===${NC}"
echo "All phases now use Claude-as-a-Service architecture!"
echo ""
echo "Results:"
echo "- Phase 1: $PRIORITY_FILE"
echo "- Phase 2: $TRIAGE_FILE"
if [ ! -z "$CRYSTAL_FILE" ]; then
    echo "- Phase 3: $CRYSTAL_FILE"
fi

# Architecture comparison
echo -e "\n${YELLOW}Architecture Benefits:${NC}"
echo "✓ Automatic HAiOS context loading"
echo "✓ Centralized LLM governance"
echo "✓ Simplified adapter code"
echo "✓ Mock support for testing"

# Next steps
echo -e "\n${YELLOW}Next Steps:${NC}"
echo "1. Deploy with real Claude server:"
echo "   docker compose --profile rhiza-v3 up -d"
echo ""
echo "2. Update n8n workflows to use v3 adapters"
echo ""
echo "3. Test NocoDB integration with credentials"