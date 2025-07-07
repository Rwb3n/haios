#!/bin/bash
# Test script for Rhiza MVP - runs all three phases locally

echo "=== Rhiza MVP Test Script ==="
echo "Testing all three phases with mock LLM (no API keys required)"
echo ""

# Set working directory
cd "$(dirname "$0")/adapters"

# Phase 1: Strategic Triage
echo "========================================="
echo "PHASE 1: Strategic Triage"
echo "========================================="
python phase1_strategic_triage_v2.py --categories cs.AI cs.DC

echo ""
echo "Phase 1 complete. Check reports directory for output."
echo "Press Enter to continue to Phase 2..."
read

# Phase 2: Tactical Ingestion
# Use a general topic that should find papers
echo "========================================="
echo "PHASE 2: Tactical Ingestion"
echo "========================================="
python phase2_tactical_ingestion.py --topic "distributed systems"

echo ""
echo "Phase 2 complete. Check reports directory for triage report."
echo "Press Enter to continue to Phase 3..."
read

# Phase 3: Crystal Seed Extraction
# Use a known paper ID that should exist
echo "========================================="
echo "PHASE 3: Crystal Seed Extraction"
echo "========================================="
python phase3_crystal_seed.py --paper-id "2301.00001"

echo ""
echo "========================================="
echo "MVP TEST COMPLETE"
echo "========================================="
echo ""
echo "Check the following locations for outputs:"
echo "- Reports: agents/rhiza_agent/reports/"
echo "- Logs: Check console output above"
echo ""
echo "To test in n8n:"
echo "1. Import the workflow from: agents/rhiza_agent/n8n_workflows/rhiza_mvp_linear.json"
echo "2. Run with input: {\"categories\": [\"cs.AI\", \"cs.DC\"]}"