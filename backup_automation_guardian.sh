#!/bin/bash
# Backup Automation Guardian - Failsafe system for when GitHub Actions fail

# Configuration
MAX_HOURS_WITHOUT_UPDATE=26  # Alert if no update in 26 hours (allows for some delay)
BACKUP_TRIGGER_HOURS=30     # Trigger backup if no update in 30 hours
EMERGENCY_EMAIL="${EMERGENCY_EMAIL:-your-email@example.com}"
GUARDIAN_LOG="logs/guardian.log"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Ensure logs directory exists
mkdir -p logs

# Logging function
log_guardian() {
    local level="$1"
    local message="$2"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" >> "$GUARDIAN_LOG"
    
    case $level in
        "ERROR") echo -e "${RED}❌ [$level] $message${NC}" ;;
        "WARN")  echo -e "${YELLOW}⚠️  [$level] $message${NC}" ;;
        "INFO")  echo -e "${BLUE}ℹ️  [$level] $message${NC}" ;;
        "SUCCESS") echo -e "${GREEN}✅ [$level] $message${NC}" ;;
    esac
}

# Function to check last automation time
get_hours_since_last_automation() {
    local last_automation=$(git log -1 --grep="Auto-update\|🎯\|🤖" --pretty=format:"%ct" 2>/dev/null)
    
    if [ -n "$last_automation" ]; then
        local current_time=$(date +%s)
        echo $(( (current_time - last_automation) / 3600 ))
    else
        echo 999  # No automation found
    fi
}

# Function to check if today's chart exists
check_todays_chart() {
    local today=$(date +%Y_%m_%d)
    [ -f "slides/gantt_daily_${today}.png" ]
}

# Function to trigger GitHub Actions workflow via API
trigger_github_action() {
    local workflow="$1"
    local workflow_file="$2"
    
    log_guardian "INFO" "Attempting to trigger $workflow via GitHub API"
    
    # Try GitHub CLI first
    if command -v gh >/dev/null 2>&1; then
        if gh workflow run "$workflow_file" --ref main 2>/dev/null; then
            log_guardian "SUCCESS" "GitHub workflow triggered via CLI: $workflow"
            return 0
        else
            log_guardian "WARN" "GitHub CLI trigger failed for $workflow"
        fi
    fi
    
    # Try curl with GitHub API (requires token)
    if [ -n "$GITHUB_TOKEN" ]; then
        local repo=$(git remote get-url origin | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')
        local api_url="https://api.github.com/repos/$repo/actions/workflows/$workflow_file/dispatches"
        
        if curl -s -X POST "$api_url" \
           -H "Authorization: token $GITHUB_TOKEN" \
           -H "Accept: application/vnd.github.v3+json" \
           -d '{"ref":"main"}' | grep -q "message"; then
            log_guardian "ERROR" "GitHub API trigger failed for $workflow"
            return 1
        else
            log_guardian "SUCCESS" "GitHub workflow triggered via API: $workflow"
            return 0
        fi
    fi
    
    log_guardian "ERROR" "Unable to trigger $workflow - no authentication method available"
    return 1
}

# Function to run local backup generation
run_local_backup() {
    log_guardian "INFO" "Starting local backup chart generation"
    
    # Check if we can run the chart generation locally
    if [ ! -f "flex_gantt.py" ]; then
        log_guardian "ERROR" "flex_gantt.py not found - cannot run local backup"
        return 1
    fi
    
    if ! command -v python3 >/dev/null 2>&1; then
        log_guardian "ERROR" "Python 3 not available - cannot run local backup"
        return 1
    fi
    
    # Try to generate today's chart
    log_guardian "INFO" "Generating daily chart locally"
    if python3 flex_gantt.py pipeline.xlsx --daily --dashboard 2>>logs/backup_generation.log; then
        log_guardian "SUCCESS" "Local daily chart generation completed"
    else
        log_guardian "ERROR" "Local daily chart generation failed"
        return 1
    fi
    
    # Try to generate other charts if it's the right day
    local day_of_week=$(date +%u)
    if [ "$day_of_week" -eq 7 ]; then  # Sunday
        log_guardian "INFO" "Generating weekly chart locally (Sunday)"
        if python3 flex_gantt.py pipeline.xlsx --weekly --dashboard 2>>logs/backup_generation.log; then
            log_guardian "SUCCESS" "Local weekly chart generation completed"
        else
            log_guardian "WARN" "Local weekly chart generation failed"
        fi
    fi
    
    # Check if it's first of month
    if [ "$(date +%d)" -eq 1 ]; then
        log_guardian "INFO" "Generating monthly charts locally (1st of month)"
        if python3 flex_gantt.py pipeline.xlsx --rolling-window --dashboard 2>>logs/backup_generation.log; then
            log_guardian "SUCCESS" "Local monthly chart generation completed"
        else
            log_guardian "WARN" "Local monthly chart generation failed"
        fi
        
        if python3 flex_gantt.py pipeline.xlsx --calendar --dashboard 2>>logs/backup_generation.log; then
            log_guardian "SUCCESS" "Local calendar generation completed"
        else
            log_guardian "WARN" "Local calendar generation failed"
        fi
    fi
    
    # Commit and push changes if successful
    if git add slides/ && git diff --staged --quiet; then
        log_guardian "INFO" "No new files generated by backup"
        return 0
    else
        log_guardian "INFO" "Committing backup-generated files"
        if git commit -m "🛡️ Backup Guardian: Emergency chart generation - $(date +'%A, %B %d, %Y')" &&
           git push origin main; then
            log_guardian "SUCCESS" "Backup-generated charts committed and pushed"
            return 0
        else
            log_guardian "ERROR" "Failed to commit/push backup-generated charts"
            return 1
        fi
    fi
}

# Function to send emergency notification
send_emergency_notification() {
    local situation="$1"
    local action_taken="$2"
    
    log_guardian "INFO" "Sending emergency notification: $situation"
    
    # Use the email notifier if configured
    if [ -x "automation_email_notifier.sh" ]; then
        # Create custom emergency message
        local email_body="🚨 AUTOMATION GUARDIAN ALERT

Situation: $situation
Action Taken: $action_taken
Time: $(date)
Host: $(hostname)

📊 System Status:
- Hours since last automation: $(get_hours_since_last_automation)
- Today's chart exists: $(check_todays_chart && echo "Yes" || echo "No")
- Repository status: $(git status --porcelain | wc -l) files changed

🔧 Recommended Actions:
1. Check GitHub Actions: https://github.com/$(git remote get-url origin | sed 's/.*github.com[:/]\([^/]*\/[^/]*\)\.git/\1/')/actions
2. Review guardian logs: cat $GUARDIAN_LOG
3. Manual trigger: ./trigger_manual_update.sh

This is an automated alert from your Backup Automation Guardian."

        echo "$email_body" | mail -s "[URGENT] Dashboard Automation Guardian Alert" "$EMERGENCY_EMAIL" 2>/dev/null ||
        log_guardian "WARN" "Failed to send emergency email notification"
    fi
}

# Function to check system health and take action
check_and_guard() {
    local hours_since=$(get_hours_since_last_automation)
    local today_chart_exists=$(check_todays_chart && echo "true" || echo "false")
    local current_hour=$(date +%H)
    
    log_guardian "INFO" "Guardian check: ${hours_since}h since last automation, today's chart: $today_chart_exists"
    
    # Determine if action is needed
    if [ $hours_since -lt $MAX_HOURS_WITHOUT_UPDATE ] && [ "$today_chart_exists" = "true" ]; then
        log_guardian "INFO" "System healthy - no action needed"
        return 0
    fi
    
    # Warning level - automation is delayed but not critical yet
    if [ $hours_since -ge $MAX_HOURS_WITHOUT_UPDATE ] && [ $hours_since -lt $BACKUP_TRIGGER_HOURS ]; then
        log_guardian "WARN" "Automation delayed (${hours_since}h) but within tolerance"
        
        # Try to trigger GitHub Actions if it's been more than 25 hours
        if [ $hours_since -ge 25 ]; then
            log_guardian "INFO" "Attempting GitHub Actions recovery trigger"
            if trigger_github_action "Enhanced Daily Dashboard Update" "daily-update-enhanced.yml"; then
                log_guardian "SUCCESS" "Recovery trigger sent - monitoring for completion"
                send_emergency_notification "Automation delayed ${hours_since} hours" "GitHub Actions recovery trigger sent"
            else
                log_guardian "ERROR" "Recovery trigger failed"
            fi
        fi
        return 0
    fi
    
    # Critical level - backup action required
    if [ $hours_since -ge $BACKUP_TRIGGER_HOURS ]; then
        log_guardian "ERROR" "CRITICAL: No automation for ${hours_since} hours - activating backup"
        
        # Try GitHub Actions trigger first
        local github_success=false
        if trigger_github_action "Enhanced Daily Dashboard Update" "daily-update-enhanced.yml"; then
            github_success=true
            log_guardian "INFO" "GitHub Actions emergency trigger sent - waiting 10 minutes"
            send_emergency_notification "CRITICAL: ${hours_since}h without automation" "Emergency GitHub Actions trigger sent"
            
            # Wait 10 minutes and check if it worked
            sleep 600
            local new_hours_since=$(get_hours_since_last_automation)
            if [ $new_hours_since -lt $hours_since ]; then
                log_guardian "SUCCESS" "GitHub Actions emergency trigger successful"
                return 0
            else
                log_guardian "WARN" "GitHub Actions emergency trigger did not complete in time"
            fi
        fi
        
        # If GitHub Actions failed or didn't complete, run local backup
        if [ "$github_success" = "false" ] || [ $(get_hours_since_last_automation) -ge $BACKUP_TRIGGER_HOURS ]; then
            log_guardian "INFO" "Falling back to local backup generation"
            
            if run_local_backup; then
                log_guardian "SUCCESS" "Local backup generation completed successfully"
                send_emergency_notification "CRITICAL: ${hours_since}h without automation" "Local backup generation completed successfully"
                return 0
            else
                log_guardian "ERROR" "Local backup generation failed - SYSTEM NEEDS MANUAL INTERVENTION"
                send_emergency_notification "CRITICAL FAILURE: ${hours_since}h without automation" "Both GitHub Actions and local backup failed - MANUAL INTERVENTION REQUIRED"
                return 1
            fi
        fi
    fi
    
    # Special case: Missing today's chart even with recent automation
    if [ "$today_chart_exists" = "false" ] && [ $hours_since -lt 12 ]; then
        log_guardian "WARN" "Recent automation but missing today's chart - triggering chart generation"
        if trigger_github_action "Enhanced Daily Dashboard Update" "daily-update-enhanced.yml"; then
            log_guardian "SUCCESS" "Chart regeneration trigger sent"
        else
            log_guardian "INFO" "Attempting local chart generation"
            run_local_backup
        fi
    fi
}

# Function to run guardian in daemon mode
run_daemon() {
    local check_interval="${1:-3600}"  # Default 1 hour
    
    log_guardian "INFO" "Starting Backup Automation Guardian in daemon mode (check every ${check_interval}s)"
    
    while true; do
        check_and_guard
        sleep "$check_interval"
    done
}

# Function to show guardian status
show_status() {
    echo -e "${BOLD}${CYAN}🛡️  Backup Automation Guardian Status${NC}"
    echo "═══════════════════════════════════════════════════════════"
    
    local hours_since=$(get_hours_since_last_automation)
    local today_chart_exists=$(check_todays_chart && echo "✅ Yes" || echo "❌ No")
    
    echo "   ⏰ Hours since last automation: $hours_since"
    echo "   📊 Today's chart exists: $today_chart_exists"
    echo "   🚨 Alert threshold: $MAX_HOURS_WITHOUT_UPDATE hours"
    echo "   🛡️  Backup trigger threshold: $BACKUP_TRIGGER_HOURS hours"
    echo "   📧 Emergency email: $EMERGENCY_EMAIL"
    echo "   📝 Guardian log: $GUARDIAN_LOG"
    
    echo ""
    if [ $hours_since -lt $MAX_HOURS_WITHOUT_UPDATE ]; then
        echo -e "   ${GREEN}✅ Status: HEALTHY${NC}"
    elif [ $hours_since -lt $BACKUP_TRIGGER_HOURS ]; then
        echo -e "   ${YELLOW}⚠️  Status: MONITORING (delayed but acceptable)${NC}"
    else
        echo -e "   ${RED}🚨 Status: CRITICAL (backup action required)${NC}"
    fi
    
    echo ""
    echo "Recent guardian activity:"
    if [ -f "$GUARDIAN_LOG" ]; then
        tail -5 "$GUARDIAN_LOG" | while read -r line; do
            echo "   $line"
        done
    else
        echo "   No guardian log found"
    fi
}

# Main script logic
case "${1:-check}" in
    "check")
        echo -e "${CYAN}🛡️  Running Backup Automation Guardian check...${NC}"
        echo ""
        check_and_guard
        ;;
    "daemon")
        run_daemon "${2:-3600}"
        ;;
    "status")
        show_status
        ;;
    "test")
        echo -e "${CYAN}🧪 Testing Guardian capabilities...${NC}"
        echo ""
        
        log_guardian "INFO" "Guardian test initiated"
        
        # Test GitHub Actions trigger capability
        echo "Testing GitHub Actions trigger capability..."
        if command -v gh >/dev/null 2>&1; then
            if gh auth status >/dev/null 2>&1; then
                echo -e "   ${GREEN}✅ GitHub CLI authenticated${NC}"
            else
                echo -e "   ${YELLOW}⚠️  GitHub CLI not authenticated${NC}"
            fi
        else
            echo -e "   ${YELLOW}⚠️  GitHub CLI not installed${NC}"
        fi
        
        # Test local generation capability
        echo "Testing local generation capability..."
        if [ -f "flex_gantt.py" ] && command -v python3 >/dev/null 2>&1; then
            echo -e "   ${GREEN}✅ Local generation capable${NC}"
        else
            echo -e "   ${RED}❌ Local generation not available${NC}"
        fi
        
        # Test email notification
        echo "Testing email notification capability..."
        if command -v mail >/dev/null 2>&1; then
            echo -e "   ${GREEN}✅ Email command available${NC}"
        else
            echo -e "   ${YELLOW}⚠️  Email command not available${NC}"
        fi
        
        log_guardian "INFO" "Guardian test completed"
        ;;
    "force-backup")
        echo -e "${YELLOW}⚠️  Forcing backup generation...${NC}"
        run_local_backup
        ;;
    "help"|*)
        echo "🛡️  Backup Automation Guardian"
        echo ""
        echo "Usage: $0 [command] [options]"
        echo ""
        echo "Commands:"
        echo "  check         - Run single guardian check (default)"
        echo "  daemon [sec]  - Run continuous monitoring (default: 3600s intervals)"
        echo "  status        - Show current guardian status"
        echo "  test          - Test guardian capabilities"
        echo "  force-backup  - Force local backup generation"
        echo "  help          - Show this help"
        echo ""
        echo "Configuration:"
        echo "  Edit this script to configure email and thresholds"
        echo "  Set GITHUB_TOKEN environment variable for API triggers"
        echo "  Install GitHub CLI (gh) for easier workflow triggers"
        echo ""
        echo "Examples:"
        echo "  $0 check                    # Single check"
        echo "  $0 daemon 1800             # Check every 30 minutes"
        echo "  $0 status                  # Show current status"
        ;;
esac

# Exit with appropriate code
exit $?