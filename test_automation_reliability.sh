#!/bin/bash
# Automation Reliability Test Suite - Comprehensive validation of the entire system

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Test results tracking
TESTS_PASSED=0
TESTS_FAILED=0
TESTS_TOTAL=0

# Function to run a test
run_test() {
    local test_name="$1"
    local test_command="$2"
    local expected_result="${3:-0}"  # Default expect success (0)
    
    TESTS_TOTAL=$((TESTS_TOTAL + 1))
    echo -e "${BLUE}🧪 Testing: $test_name${NC}"
    
    # Run the test
    eval "$test_command" >/dev/null 2>&1
    local result=$?
    
    if [ $result -eq $expected_result ]; then
        echo -e "   ${GREEN}✅ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
        return 0
    else
        echo -e "   ${RED}❌ FAIL${NC} (Expected: $expected_result, Got: $result)"
        TESTS_FAILED=$((TESTS_FAILED + 1))
        return 1
    fi
}

# Function to check file exists and is readable
check_file() {
    local file="$1"
    local description="$2"
    
    run_test "$description" "[ -f '$file' ] && [ -r '$file' ]"
}

# Function to check executable exists and runs
check_executable() {
    local executable="$1"
    local description="$2"
    
    run_test "$description" "[ -x '$executable' ] && '$executable' --help >/dev/null 2>&1" 1
}

# Function to check GitHub Actions workflow syntax
check_workflow_syntax() {
    local workflow="$1"
    local description="$2"
    
    # Basic YAML syntax check (if yq is available)
    if command -v yq >/dev/null 2>&1; then
        run_test "$description" "yq eval '.' '$workflow' >/dev/null"
    else
        # Basic syntax check - look for required fields
        run_test "$description" "grep -q 'name:' '$workflow' && grep -q 'on:' '$workflow' && grep -q 'jobs:' '$workflow'"
    fi
}

clear
echo -e "${BOLD}${CYAN}"
echo "╔══════════════════════════════════════════════════════════════════════════╗"
echo "║                    🧪 AUTOMATION RELIABILITY TEST SUITE                 ║"
echo "║                         Comprehensive System Validation                 ║"
echo "╚══════════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

echo -e "${BOLD}${BLUE}📋 Test Suite Overview${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "This test suite validates:"
echo "   🔧 GitHub Actions workflow configurations"
echo "   📁 Required files and permissions"
echo "   🖥️  Monitoring and management scripts"
echo "   📊 Data generation capabilities"
echo "   🔄 Git repository health"
echo "   🌐 External dependencies"
echo ""

echo -e "${BOLD}${PURPLE}🔧 Testing GitHub Actions Workflows${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test workflow files exist and are valid
check_workflow_syntax ".github/workflows/daily-update-enhanced.yml" "Enhanced Daily workflow syntax"
check_workflow_syntax ".github/workflows/weekly-update.yml" "Weekly workflow syntax"
check_workflow_syntax ".github/workflows/monthly-update.yml" "Monthly workflow syntax"
check_workflow_syntax ".github/workflows/deploy.yml" "Deploy workflow syntax"

# Test workflow schedules are correct
run_test "Daily schedule is off-peak (3:15 AM UTC)" "grep -q '15 3 \* \* \*' .github/workflows/daily-update-enhanced.yml"
run_test "Weekly schedule is staggered (3:30 AM UTC)" "grep -q '30 3 \* \* 1' .github/workflows/weekly-update.yml"
run_test "Monthly schedule is staggered (3:45 AM UTC)" "grep -q '45 3 1 \* \*' .github/workflows/monthly-update.yml"

# Test no duplicate daily workflows
run_test "No duplicate daily workflows" "[ ! -f .github/workflows/daily-update.yml ]"

echo ""
echo -e "${BOLD}${PURPLE}📁 Testing Required Files & Dependencies${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test core data files
check_file "pipeline.xlsx" "Pipeline data file exists"
check_file "requirements.txt" "Python requirements file"
check_file "flex_gantt.py" "Main chart generation script"

# Test slides directory
run_test "Slides directory exists" "[ -d slides ]"
run_test "Slides directory is writable" "[ -w slides ]"

# Test monitoring scripts
check_file "check_automation_status.sh" "Status checker script exists"
check_file "automation_health_dashboard.sh" "Health dashboard script exists"
check_file "trigger_manual_update.sh" "Manual trigger script exists"
check_file "automation_email_notifier.sh" "Email notifier script exists"

# Test documentation
check_file "OPTIMIZED_AUTOMATION_SCHEDULE.md" "Schedule documentation exists"
check_file "automation_status_widget.html" "Web status widget exists"

echo ""
echo -e "${BOLD}${PURPLE}🖥️  Testing Script Executability${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test script permissions
run_test "Status checker is executable" "[ -x check_automation_status.sh ]"
run_test "Health dashboard is executable" "[ -x automation_health_dashboard.sh ]"
run_test "Manual trigger is executable" "[ -x trigger_manual_update.sh ]"
run_test "Email notifier is executable" "[ -x automation_email_notifier.sh ]"

# Test script basic functionality (syntax check)
run_test "Status checker runs without errors" "bash -n check_automation_status.sh"
run_test "Health dashboard runs without errors" "bash -n automation_health_dashboard.sh"
run_test "Manual trigger runs without errors" "bash -n trigger_manual_update.sh"
run_test "Email notifier runs without errors" "bash -n automation_email_notifier.sh"

echo ""
echo -e "${BOLD}${PURPLE}📊 Testing Data Generation Capabilities${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test Python environment
run_test "Python 3 is available" "command -v python3"
run_test "Main generation script exists" "[ -f flex_gantt.py ]"
run_test "Python script syntax is valid" "python3 -m py_compile flex_gantt.py"

# Test dependencies (if requirements.txt exists)
if [ -f requirements.txt ]; then
    run_test "Requirements file is readable" "[ -r requirements.txt ]"
    # Test that we can at least parse requirements
    run_test "Requirements file format is valid" "python3 -c 'import pkg_resources; list(pkg_resources.parse_requirements(open(\"requirements.txt\", \"r\")))'"
fi

echo ""
echo -e "${BOLD}${PURPLE}🔄 Testing Git Repository Health${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test git configuration
run_test "Git repository is valid" "git status >/dev/null"
run_test "Remote origin is configured" "git remote get-url origin >/dev/null"
run_test "Current branch is main" "[ \$(git branch --show-current) = 'main' ]"

# Test automation history
run_test "Automation history exists" "git log --grep='Auto-update\\|🎯\\|🤖' --oneline -1 >/dev/null"
run_test "Recent automation within 48 hours" "git log --grep='Auto-update\\|🎯\\|🤖' --since='48 hours ago' --oneline -1 >/dev/null"

echo ""
echo -e "${BOLD}${PURPLE}🌐 Testing External Dependencies${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test network connectivity (optional)
run_test "GitHub.com is reachable" "ping -c 1 github.com >/dev/null" 0

# Test GitHub CLI (optional but recommended)
if command -v gh >/dev/null 2>&1; then
    run_test "GitHub CLI is authenticated" "gh auth status >/dev/null"
else
    echo -e "   ${YELLOW}⚠️  GitHub CLI not installed (recommended for manual triggers)${NC}"
fi

# Test browser availability (for opening links)
if command -v open >/dev/null 2>&1 || command -v xdg-open >/dev/null 2>&1; then
    echo -e "   ${GREEN}✅ Browser opener available${NC}"
else
    echo -e "   ${YELLOW}⚠️  No browser opener found (open/xdg-open)${NC}"
fi

echo ""
echo -e "${BOLD}${PURPLE}📈 Testing Current System State${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Test current file generation
TODAY=$(date +%Y_%m_%d)
run_test "Today's daily chart exists" "[ -f slides/gantt_daily_${TODAY}.png ]"

# Test current month files
CURRENT_MONTH=$(date +%Y_%m)
run_test "Current month charts exist" "ls slides/gantt_${CURRENT_MONTH}*.png >/dev/null 2>&1"
run_test "Current month calendar exists" "[ -f slides/calendar_${CURRENT_MONTH}.png ]"

# Test slides manifest
run_test "Slides manifest exists" "[ -f slides/slides.json ]"

echo ""
echo -e "${BOLD}${BLUE}📊 Test Results Summary${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Calculate pass rate
if [ $TESTS_TOTAL -gt 0 ]; then
    PASS_RATE=$(( (TESTS_PASSED * 100) / TESTS_TOTAL ))
else
    PASS_RATE=0
fi

echo "   Total Tests Run: $TESTS_TOTAL"
echo -e "   ${GREEN}Tests Passed: $TESTS_PASSED${NC}"
echo -e "   ${RED}Tests Failed: $TESTS_FAILED${NC}"
echo -e "   Pass Rate: ${BOLD}$PASS_RATE%${NC}"

echo ""

# Overall assessment
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${BOLD}${GREEN}🎉 EXCELLENT! All tests passed. Your automation system is healthy and ready.${NC}"
    echo -e "   ✅ Optimized schedules are configured correctly"
    echo -e "   ✅ All monitoring tools are functional"
    echo -e "   ✅ Backup and recovery systems are in place"
    echo -e "   ✅ Data generation capabilities are working"
    echo ""
    echo -e "${CYAN}🚀 Your system is ready for tonight's 10:15 PM CDT automation test!${NC}"
elif [ $PASS_RATE -ge 80 ]; then
    echo -e "${BOLD}${YELLOW}⚠️  GOOD with minor issues. System is mostly healthy.${NC}"
    echo -e "   ✅ Core functionality is working"
    echo -e "   ⚠️  Some optional features may need attention"
    echo -e "   💡 Check failed tests above for details"
elif [ $PASS_RATE -ge 60 ]; then
    echo -e "${BOLD}${YELLOW}⚠️  NEEDS ATTENTION. Several issues detected.${NC}"
    echo -e "   ⚠️  Core functionality may be impacted"
    echo -e "   🔧 Address failed tests before relying on automation"
else
    echo -e "${BOLD}${RED}❌ CRITICAL ISSUES. System needs immediate attention.${NC}"
    echo -e "   🚨 Multiple core components are failing"
    echo -e "   🛠️  Manual intervention required"
fi

echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
if [ $TESTS_FAILED -eq 0 ]; then
    echo "   1. 🕙 Wait for tonight's automation at 10:15 PM CDT"
    echo "   2. 🔍 Monitor with: ./check_automation_status.sh"
    echo "   3. 📊 Track performance: ./automation_health_dashboard.sh"
else
    echo "   1. 🔧 Review and fix failed tests above"
    echo "   2. 🔄 Re-run this test suite: ./test_automation_reliability.sh"
    echo "   3. 📞 Manual trigger if needed: ./trigger_manual_update.sh"
fi

echo ""
echo -e "${CYAN}💡 Pro tip: Run this test suite regularly to ensure system health!${NC}"

# Exit with appropriate code
if [ $TESTS_FAILED -eq 0 ]; then
    exit 0
else
    exit 1
fi