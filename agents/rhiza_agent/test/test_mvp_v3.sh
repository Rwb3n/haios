#!/bin/bash
# Test script for Rhiza MVP with Claude-as-a-Service (v3)

echo "=== Rhiza MVP v3 Test Suite ==="
echo "Testing with Claude-as-a-Service architecture"
echo "==============================="

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

# Base directory
cd "$(dirname "$0")"

# Test Phase 1 (v3 version)
echo -e "\n${YELLOW}Testing Phase 1: Strategic Triage (v3 with MCP)${NC}"
echo "Categories: cs.AI, cs.DC"
python3 adapters/phase1_strategic_triage_v3.py

# Check if priorities file was created
PRIORITY_FILE=$(ls -t priorities_*.json 2>/dev/null | head -1)
if [ -z "$PRIORITY_FILE" ]; then
    echo -e "${RED}ERROR: Phase 1 failed to create priorities file${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Phase 1 completed. Output: $PRIORITY_FILE${NC}"

# Extract first theme for Phase 2 (using existing v2 adapter for now)
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

echo -e "\n${YELLOW}Testing Phase 2: Tactical Ingestion${NC}"
echo "Topic: $THEME"
python3 adapters/phase2_tactical_ingestion.py --topic "$THEME"

# Check if triage file was created
TRIAGE_FILE=$(ls -t triage_*.json 2>/dev/null | head -1)
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
    echo -e "\n${YELLOW}Testing Phase 3: Crystal Seed Extraction${NC}"
    echo "Paper ID: $PAPER_ID"
    python3 adapters/phase3_crystal_seed.py --paper-id "$PAPER_ID"
    
    # Check if crystal seed file was created
    CRYSTAL_FILE=$(ls -t crystal_seed_*.json 2>/dev/null | head -1)
    if [ -z "$CRYSTAL_FILE" ]; then
        echo -e "${RED}ERROR: Phase 3 failed to create crystal seed file${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Phase 3 completed. Output: $CRYSTAL_FILE${NC}"
fi

# Summary
echo -e "\n${GREEN}=== MVP v3 Test Complete ===${NC}"
echo "Results:"
echo "- Phase 1 (v3): $PRIORITY_FILE"
echo "- Phase 2: $TRIAGE_FILE"
if [ ! -z "$CRYSTAL_FILE" ]; then
    echo "- Phase 3: $CRYSTAL_FILE"
fi

# Docker compose command hint
echo -e "\n${YELLOW}To deploy with Claude server:${NC}"
echo "docker compose --profile rhiza-v3 up -d"
echo ""
echo "This will start:"
echo "- n8n (workflow automation)"
echo "- NocoDB (database)"
echo "- Langflow (AI flows)"
echo "- claude-server (MCP server)"

# Create validation report
echo -e "\n${YELLOW}Generating validation report...${NC}"
cat > validation_report_mvp_v3.md << EOF
# Rhiza MVP v3 Validation Report

**Date**: $(date +%Y-%m-%d)  
**Architecture**: Claude-as-a-Service (v3)  
**Status**: Test Complete

## Test Results

### Phase 1 (v3 with MCP Client)
- Output: $PRIORITY_FILE
- Theme identified: $THEME
- Used ${USE_MOCK_LLM:+mock}${USE_MOCK_LLM:-real} MCP client

### Phase 2 (v2 adapter)
- Output: $TRIAGE_FILE
- Papers analyzed: $(python3 -c "import json; print(json.load(open('$TRIAGE_FILE'))['total_papers_analyzed'])")
- Tier 1 papers: $(python3 -c "import json; print(len(json.load(open('$TRIAGE_FILE'))['tier_1_papers']))")

### Phase 3 (v2 adapter)
$(if [ ! -z "$CRYSTAL_FILE" ]; then
    echo "- Output: $CRYSTAL_FILE"
    echo "- Paper analyzed: $PAPER_ID"
else
    echo "- Skipped (no Tier 1 papers)"
fi)

## Architecture Notes

The v3 architecture introduces:
1. **Claude MCP Server**: Centralized LLM gateway
2. **Automatic Context**: Server loads CLAUDE.md automatically
3. **Simplified Adapters**: No direct API calls needed
4. **Mock Support**: Can test without API keys

## Next Steps

1. Complete v3 refactoring for Phase 2 and Phase 3 adapters
2. Test with real Claude server deployment
3. Implement governance hooks
4. Set up monitoring and logging
EOF

echo -e "${GREEN}✓ Validation report created: validation_report_mvp_v3.md${NC}"