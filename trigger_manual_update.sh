#!/bin/bash
# Manual Update Trigger - Convenient way to manually trigger GitHub Actions workflows

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

echo -e "${BOLD}${CYAN}🔧 Manual Automation Trigger${NC}"
echo "================================="
echo ""

# Check if gh CLI is available
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠️  GitHub CLI (gh) not found.${NC}"
    echo "   Installing GitHub CLI will allow automatic workflow triggering."
    echo "   For now, use the manual method below."
    echo ""
fi

echo -e "${BLUE}📋 Available Workflows:${NC}"
echo "   1. 🎯 Enhanced Daily Update (Recommended)"
echo "   2. 📊 Weekly Update"  
echo "   3. 📅 Monthly Update"
echo "   4. 🌐 Open GitHub Actions (Manual trigger)"
echo ""

read -p "Select workflow to trigger (1-4): " choice

case $choice in
    1)
        echo -e "${GREEN}🎯 Triggering Enhanced Daily Update...${NC}"
        if command -v gh &> /dev/null; then
            gh workflow run "Enhanced Daily Dashboard Update" --ref main
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Workflow triggered successfully!${NC}"
                echo "   📊 Check status: https://github.com/dylantneal/Encore_Dashboard/actions"
                echo "   ⏱️  Expected completion: ~5-10 minutes"
            else
                echo -e "${RED}❌ Failed to trigger workflow via CLI${NC}"
                echo "   Please use manual method below."
            fi
        else
            echo -e "${YELLOW}📱 Manual trigger required:${NC}"
            echo "   1. Go to: https://github.com/dylantneal/Encore_Dashboard/actions"
            echo "   2. Click 'Enhanced Daily Dashboard Update'"
            echo "   3. Click 'Run workflow' button"
            echo "   4. Select 'main' branch and click 'Run workflow'"
        fi
        ;;
    2)
        echo -e "${GREEN}📊 Triggering Weekly Update...${NC}"
        if command -v gh &> /dev/null; then
            gh workflow run "Weekly Dashboard Update" --ref main
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Workflow triggered successfully!${NC}"
            else
                echo -e "${RED}❌ Failed to trigger workflow via CLI${NC}"
            fi
        else
            echo -e "${YELLOW}📱 Manual trigger required:${NC}"
            echo "   1. Go to: https://github.com/dylantneal/Encore_Dashboard/actions"
            echo "   2. Click 'Weekly Dashboard Update'"
            echo "   3. Click 'Run workflow' button"
        fi
        ;;
    3)
        echo -e "${GREEN}📅 Triggering Monthly Update...${NC}"
        if command -v gh &> /dev/null; then
            gh workflow run "Monthly Dashboard Update" --ref main
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Workflow triggered successfully!${NC}"
            else
                echo -e "${RED}❌ Failed to trigger workflow via CLI${NC}"
            fi
        else
            echo -e "${YELLOW}📱 Manual trigger required:${NC}"
            echo "   1. Go to: https://github.com/dylantneal/Encore_Dashboard/actions"
            echo "   2. Click 'Monthly Dashboard Update'"
            echo "   3. Click 'Run workflow' button"
        fi
        ;;
    4)
        echo -e "${BLUE}🌐 Opening GitHub Actions...${NC}"
        if command -v open &> /dev/null; then
            open "https://github.com/dylantneal/Encore_Dashboard/actions"
        elif command -v xdg-open &> /dev/null; then
            xdg-open "https://github.com/dylantneal/Encore_Dashboard/actions"
        else
            echo "   Go to: https://github.com/dylantneal/Encore_Dashboard/actions"
        fi
        ;;
    *)
        echo -e "${RED}❌ Invalid selection${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${BLUE}📊 After triggering:${NC}"
echo "   ⏱️  Wait 5-10 minutes for completion"
echo "   🔄 Check status: ./check_automation_status.sh"
echo "   📊 Monitor progress: https://github.com/dylantneal/Encore_Dashboard/actions"
echo "   🌐 View results: https://www.marquisdashboard.com"

echo ""
echo -e "${CYAN}💡 Tip: Install GitHub CLI for easier automation: brew install gh${NC}"