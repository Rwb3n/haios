#!/bin/bash
# HAIOS Canon Linter - Master ADR Hygiene Validation Script
#
# Part of: EXEC_PLAN_AUTOMATE_ADR_HYGIENE_V1
# Purpose: Execute all ADR hygiene checks to prevent architectural drift
# 
# Exit codes:
# 0 = All validations passed
# 1 = One or more validations failed
# 2 = Script execution error

set -e  # Exit on any error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${BLUE}🛡️  HAIOS Canon Linter - ADR Hygiene Validation${NC}"
echo "===================================================="
echo "Project root: $PROJECT_ROOT"
echo "Script directory: $SCRIPT_DIR"
echo ""

# Track overall success
OVERALL_SUCCESS=true

# Function to run a validation check
run_check() {
    local check_name="$1"
    local script_path="$2"
    local description="$3"
    
    echo -e "${BLUE}🔍 Running: $check_name${NC}"
    echo "Description: $description"
    echo "Script: $script_path"
    echo ""
    
    if [[ ! -f "$script_path" ]]; then
        echo -e "${RED}❌ ERROR: Script not found: $script_path${NC}"
        OVERALL_SUCCESS=false
        return 1
    fi
    
    # Run the check and capture both stdout and stderr
    if python3 "$script_path" 2>&1; then
        echo -e "${GREEN}✅ $check_name: PASSED${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}❌ $check_name: FAILED${NC}"
        echo ""
        OVERALL_SUCCESS=false
        return 1
    fi
}

# Change to project root for consistent paths
cd "$PROJECT_ROOT"

echo -e "${BLUE}📋 Running ADR Hygiene Validation Checks...${NC}"
echo ""

# Check 1: Annotation Duplicate Detection
run_check \
    "Annotation Duplicate Detection" \
    "$SCRIPT_DIR/check_dupe_annotations.py" \
    "Scans for duplicate entries in EmbeddedAnnotationBlocks"

# Check 2: Cross-Reference Link Validation
run_check \
    "Cross-Reference Link Validation" \
    "$SCRIPT_DIR/check_cross_references.py" \
    "Validates all internal links and ADR references"

# Check 3: Diagram Compliance
run_check \
    "Diagram Compliance Validation" \
    "$SCRIPT_DIR/check_diagram_compliance.py" \
    "Checks for missing required diagrams in ADRs"

# Final summary
echo "===================================================="
if [[ "$OVERALL_SUCCESS" == "true" ]]; then
    echo -e "${GREEN}🎉 ALL VALIDATIONS PASSED${NC}"
    echo -e "${GREEN}✅ HAIOS Canon is clean and compliant${NC}"
    echo ""
    echo "The ADR documentation is free from:"
    echo "  • Duplicate annotation entries"
    echo "  • Broken internal links"
    echo "  • Missing required diagrams"
    echo ""
    exit 0
else
    echo -e "${RED}💥 VALIDATION FAILURES DETECTED${NC}"
    echo -e "${RED}❌ HAIOS Canon has hygiene issues that need attention${NC}"
    echo ""
    echo "Please review the output above and fix the identified issues."
    echo "Re-run this script after making corrections."
    echo ""
    exit 1
fi