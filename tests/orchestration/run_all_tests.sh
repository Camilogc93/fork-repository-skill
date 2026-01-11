#!/bin/bash
#
# Run All Orchestration Tests
#
# This script runs all orchestration system tests and provides a summary.
#

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test directory
TEST_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║     Agent Orchestration System - Test Suite                 ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""

# Clean up any previous test artifacts
echo -e "${YELLOW}🧹 Cleaning up previous test artifacts...${NC}"
rm -rf /tmp/test-orchestration-* /tmp/test-messaging-*
echo -e "${GREEN}✓ Cleanup complete${NC}"
echo ""

# Track test results
PASSED=0
FAILED=0
TOTAL=0

# Function to run a test
run_test() {
    local test_file=$1
    local test_name=$(basename "$test_file" .py)

    TOTAL=$((TOTAL + 1))

    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}Running: ${test_name}${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo ""

    if python3 "$test_file"; then
        PASSED=$((PASSED + 1))
        echo ""
        echo -e "${GREEN}✅ ${test_name} PASSED${NC}"
    else
        FAILED=$((FAILED + 1))
        echo ""
        echo -e "${RED}❌ ${test_name} FAILED${NC}"
    fi

    echo ""
}

# Run tests
echo -e "${YELLOW}📋 Running test suite...${NC}"
echo ""

# Test 1: Simple Workflow
run_test "$TEST_DIR/test_simple_workflow.py"

# Test 2: Multi-Agent Coordination
run_test "$TEST_DIR/test_multi_agent.py"

# Test 3: Peer-to-Peer Communication
run_test "$TEST_DIR/test_peer_communication.py"

# Summary
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║                       TEST SUMMARY                           ║${NC}"
echo -e "${BLUE}╚══════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "  Total Tests:   ${TOTAL}"
echo -e "  ${GREEN}Passed:        ${PASSED}${NC}"
if [ $FAILED -gt 0 ]; then
    echo -e "  ${RED}Failed:        ${FAILED}${NC}"
else
    echo -e "  ${GREEN}Failed:        ${FAILED}${NC}"
fi
echo ""

# Calculate success rate
SUCCESS_RATE=$(awk "BEGIN {printf \"%.1f\", ($PASSED/$TOTAL)*100}")

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║          🎉 ALL TESTS PASSED! (100% Success)                 ║${NC}"
    echo -e "${GREEN}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${GREEN}✅ The orchestration system is working correctly!${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}╔══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║   ⚠️  SOME TESTS FAILED (${SUCCESS_RATE}% Success)                      ║${NC}"
    echo -e "${RED}╚══════════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${RED}❌ Please review the test output above for details.${NC}"
    echo ""
    exit 1
fi
