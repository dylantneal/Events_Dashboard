#!/bin/bash
# Automation Control Center - Master control interface for all automation systems

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Function to show the main menu
show_main_menu() {
    clear
    echo -e "${BOLD}${CYAN}"
    echo "╔══════════════════════════════════════════════════════════════════════════╗"
    echo "║                    🚀 AUTOMATION CONTROL CENTER                         ║"
    echo "║                      Phase 4 - Complete System                          ║"
    echo "╚══════════════════════════════════════════════════════════════════════════╝"
    echo -e "${NC}"
    echo ""
    
    echo -e "${BOLD}${BLUE}📊 System Status Overview${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Quick status check
    local hours_since=$(git log -1 --grep="Auto-update\|🎯\|🤖" --pretty=format:"%ct" 2>/dev/null)
    if [ -n "$hours_since" ]; then
        local current_time=$(date +%s)
        local hours_diff=$(( (current_time - hours_since) / 3600 ))
        
        if [ $hours_diff -lt 24 ]; then
            echo -e "   ${GREEN}✅ Automation Status: HEALTHY (last run $hours_diff hours ago)${NC}"
        else
            echo -e "   ${YELLOW}⚠️  Automation Status: DELAYED (last run $hours_diff hours ago)${NC}"
        fi
    else
        echo -e "   ${RED}❌ Automation Status: NO RECENT ACTIVITY${NC}"
    fi
    
    # Check today's files
    local today=$(date +%Y_%m_%d)
    if [ -f "slides/gantt_daily_${today}.png" ]; then
        echo -e "   ${GREEN}✅ Today's Chart: AVAILABLE${NC}"
    else
        echo -e "   ${YELLOW}⚠️  Today's Chart: MISSING${NC}"
    fi
    
    # Next automation
    local current_hour=$(date +%H)
    if [ "$current_hour" -lt 22 ]; then
        echo -e "   ${BLUE}🕙 Next Automation: Tonight at 10:15 PM CDT${NC}"
    else
        echo -e "   ${BLUE}🕙 Next Automation: Tomorrow at 10:15 PM CDT${NC}"
    fi
    
    echo ""
    echo -e "${BOLD}${PURPLE}🛠️  Available Actions${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo -e "${CYAN}📊 MONITORING & STATUS${NC}"
    echo "   1) 🔍 Quick Status Check"
    echo "   2) 📋 Comprehensive Health Dashboard"
    echo "   3) 📈 Performance Analysis"
    echo "   4) 🧪 Run System Reliability Tests"
    echo ""
    echo -e "${CYAN}🔧 MANUAL CONTROL${NC}"
    echo "   5) 🚀 Trigger Manual Update"
    echo "   6) 🛡️  Guardian Status & Control"
    echo "   7) 📧 Email Notification Test"
    echo "   8) 🌐 Open GitHub Actions"
    echo ""
    echo -e "${CYAN}📊 REPORTS & ANALYSIS${NC}"
    echo "   9) 📄 Generate Performance Report"
    echo "  10) 📋 View Automation Logs"
    echo "  11) 📅 Schedule Information"
    echo ""
    echo -e "${CYAN}⚙️  SYSTEM MANAGEMENT${NC}"
    echo "  12) 🔄 Update Local Repository"
    echo "  13) 🧹 Clean Up Logs"
    echo "  14) ⚙️  Configuration & Setup"
    echo ""
    echo "   0) 🚪 Exit"
    echo ""
}

# Function to handle user choice
handle_choice() {
    local choice="$1"
    
    case $choice in
        1)
            echo -e "${CYAN}🔍 Running Quick Status Check...${NC}"
            echo ""
            ./check_automation_status.sh
            ;;
        2)
            echo -e "${CYAN}📋 Opening Comprehensive Health Dashboard...${NC}"
            echo ""
            ./automation_health_dashboard.sh
            ;;
        3)
            echo -e "${CYAN}📈 Analyzing Performance...${NC}"
            echo ""
            ./automation_performance_tracker.sh analyze
            ;;
        4)
            echo -e "${CYAN}🧪 Running System Reliability Tests...${NC}"
            echo ""
            ./test_automation_reliability.sh
            ;;
        5)
            echo -e "${CYAN}🚀 Opening Manual Trigger Interface...${NC}"
            echo ""
            ./trigger_manual_update.sh
            ;;
        6)
            echo -e "${CYAN}🛡️  Guardian Status & Control...${NC}"
            echo ""
            echo "Guardian Options:"
            echo "   a) Show Status"
            echo "   b) Run Check"
            echo "   c) Test Capabilities"
            echo "   d) Force Backup"
            echo ""
            read -p "Select option (a-d): " guardian_choice
            
            case $guardian_choice in
                a) ./backup_automation_guardian.sh status ;;
                b) ./backup_automation_guardian.sh check ;;
                c) ./backup_automation_guardian.sh test ;;
                d) ./backup_automation_guardian.sh force-backup ;;
                *) echo "Invalid option" ;;
            esac
            ;;
        7)
            echo -e "${CYAN}📧 Testing Email Notifications...${NC}"
            echo ""
            ./automation_email_notifier.sh test
            ;;
        8)
            echo -e "${CYAN}🌐 Opening GitHub Actions...${NC}"
            if command -v open >/dev/null 2>&1; then
                open "https://github.com/dylantneal/Encore_Dashboard/actions"
            elif command -v xdg-open >/dev/null 2>&1; then
                xdg-open "https://github.com/dylantneal/Encore_Dashboard/actions"
            else
                echo "Open: https://github.com/dylantneal/Encore_Dashboard/actions"
            fi
            ;;
        9)
            echo -e "${CYAN}📄 Generating Performance Report...${NC}"
            echo ""
            ./automation_performance_tracker.sh report
            if [ -f "logs/performance_report.html" ]; then
                echo -e "${GREEN}✅ Report generated: logs/performance_report.html${NC}"
                read -p "Open report in browser? (y/n): " open_report
                if [ "$open_report" = "y" ]; then
                    if command -v open >/dev/null 2>&1; then
                        open "logs/performance_report.html"
                    elif command -v xdg-open >/dev/null 2>&1; then
                        xdg-open "logs/performance_report.html"
                    fi
                fi
            fi
            ;;
        10)
            echo -e "${CYAN}📋 Automation Logs...${NC}"
            echo ""
            echo "Available Logs:"
            echo "   a) Recent automation commits"
            echo "   b) Guardian log"
            echo "   c) Performance log"
            echo "   d) All log files"
            echo ""
            read -p "Select log (a-d): " log_choice
            
            case $log_choice in
                a) 
                    echo "Recent Automation Commits:"
                    git log --oneline --grep="Auto-update\|🎯\|🤖" -10
                    ;;
                b)
                    if [ -f "logs/guardian.log" ]; then
                        echo "Guardian Log (last 20 lines):"
                        tail -20 logs/guardian.log
                    else
                        echo "No guardian log found"
                    fi
                    ;;
                c)
                    if [ -f "logs/performance.log" ]; then
                        echo "Performance Log (last 10 entries):"
                        tail -10 logs/performance.log
                    else
                        echo "No performance log found"
                    fi
                    ;;
                d)
                    echo "All Log Files:"
                    ls -la logs/ 2>/dev/null || echo "No logs directory found"
                    ;;
                *) echo "Invalid option" ;;
            esac
            ;;
        11)
            echo -e "${CYAN}📅 Schedule Information...${NC}"
            echo ""
            if [ -f "OPTIMIZED_AUTOMATION_SCHEDULE.md" ]; then
                echo "=== OPTIMIZED AUTOMATION SCHEDULE ==="
                head -50 OPTIMIZED_AUTOMATION_SCHEDULE.md
                echo ""
                echo "📖 Full schedule: cat OPTIMIZED_AUTOMATION_SCHEDULE.md"
            else
                echo "Schedule documentation not found"
            fi
            ;;
        12)
            echo -e "${CYAN}🔄 Updating Local Repository...${NC}"
            echo ""
            git fetch origin
            git status
            echo ""
            read -p "Pull latest changes? (y/n): " pull_choice
            if [ "$pull_choice" = "y" ]; then
                git pull origin main
                echo -e "${GREEN}✅ Repository updated${NC}"
            fi
            ;;
        13)
            echo -e "${CYAN}🧹 Cleaning Up Logs...${NC}"
            echo ""
            if [ -d "logs" ]; then
                echo "Log files found:"
                ls -la logs/
                echo ""
                read -p "Delete old log files? (y/n): " clean_choice
                if [ "$clean_choice" = "y" ]; then
                    # Keep recent files, clean old ones
                    find logs/ -name "*.log" -mtime +7 -delete 2>/dev/null
                    echo -e "${GREEN}✅ Old log files cleaned${NC}"
                fi
            else
                echo "No logs directory found"
            fi
            ;;
        14)
            echo -e "${CYAN}⚙️  Configuration & Setup...${NC}"
            echo ""
            echo "Configuration Options:"
            echo "   a) View Current Configuration"
            echo "   b) Email Configuration"
            echo "   c) GitHub CLI Setup"
            echo "   d) System Information"
            echo ""
            read -p "Select option (a-d): " config_choice
            
            case $config_choice in
                a)
                    echo "=== CURRENT CONFIGURATION ==="
                    echo "Git Repository:"
                    git remote -v
                    echo ""
                    echo "Python Version:"
                    python3 --version 2>/dev/null || echo "Python 3 not found"
                    echo ""
                    echo "GitHub CLI:"
                    gh --version 2>/dev/null || echo "GitHub CLI not installed"
                    ;;
                b)
                    ./automation_email_notifier.sh config
                    ;;
                c)
                    if command -v gh >/dev/null 2>&1; then
                        gh auth status
                    else
                        echo "GitHub CLI not installed"
                        echo "Install with: brew install gh"
                    fi
                    ;;
                d)
                    echo "=== SYSTEM INFORMATION ==="
                    echo "Operating System: $(uname -s)"
                    echo "Hostname: $(hostname)"
                    echo "Current User: $(whoami)"
                    echo "Current Directory: $(pwd)"
                    echo "Disk Space:"
                    df -h . | tail -1
                    ;;
                *) echo "Invalid option" ;;
            esac
            ;;
        0)
            echo -e "${GREEN}👋 Goodbye! Your automation system is running smoothly.${NC}"
            echo ""
            echo -e "${CYAN}💡 Remember: Tonight at 10:15 PM CDT is your next scheduled automation!${NC}"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ Invalid choice. Please select 0-14.${NC}"
            ;;
    esac
}

# Main program loop
main() {
    while true; do
        show_main_menu
        echo -n "Enter your choice (0-14): "
        read choice
        echo ""
        
        handle_choice "$choice"
        
        echo ""
        echo -e "${YELLOW}Press Enter to continue...${NC}"
        read
    done
}

# Check if running with arguments (non-interactive mode)
if [ $# -gt 0 ]; then
    case "$1" in
        "status")
            ./check_automation_status.sh
            ;;
        "health")
            ./automation_health_dashboard.sh
            ;;
        "test")
            ./test_automation_reliability.sh
            ;;
        "guardian")
            ./backup_automation_guardian.sh status
            ;;
        "trigger")
            ./trigger_manual_update.sh
            ;;
        "help")
            echo "🚀 Automation Control Center"
            echo ""
            echo "Usage: $0 [command]"
            echo ""
            echo "Commands:"
            echo "  status   - Quick status check"
            echo "  health   - Health dashboard"
            echo "  test     - Reliability tests"
            echo "  guardian - Guardian status"
            echo "  trigger  - Manual trigger"
            echo "  help     - Show this help"
            echo ""
            echo "Run without arguments for interactive menu"
            ;;
        *)
            echo "Unknown command: $1"
            echo "Run '$0 help' for available commands"
            exit 1
            ;;
    esac
else
    # Interactive mode
    main
fi