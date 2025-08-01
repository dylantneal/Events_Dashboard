#!/bin/bash
# Automation Health Dashboard - Comprehensive automation analysis and monitoring

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m' # No Color

# Clear screen and show header
clear
echo -e "${BOLD}${CYAN}"
echo "╔═══════════════════════════════════════════════════════════════════════╗"
echo "║                    🚀 AUTOMATION HEALTH DASHBOARD                    ║"
echo "║                     Enhanced Monitoring System                       ║"
echo "╚═══════════════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""

# Function to show status with icon
show_status() {
    local status=$1
    local message=$2
    case $status in
        "success") echo -e "   ${GREEN}✅ $message${NC}" ;;
        "warning") echo -e "   ${YELLOW}⚠️  $message${NC}" ;;
        "error") echo -e "   ${RED}❌ $message${NC}" ;;
        "info") echo -e "   ${BLUE}ℹ️  $message${NC}" ;;
        "pending") echo -e "   ${PURPLE}🔄 $message${NC}" ;;
    esac
}

# Current time in multiple zones
echo -e "${BOLD}${BLUE}🕒 Time Zones & Schedule Context${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
LOCAL_TIME=$(date)
UTC_TIME=$(TZ=UTC date)
CDT_TIME=$(TZ=America/Chicago date)

echo "   🌍 UTC:   $UTC_TIME"
echo "   🏠 Local: $LOCAL_TIME"  
echo "   🇺🇸 CDT:   $CDT_TIME"
echo ""

# Show optimized schedule
echo -e "${BOLD}${PURPLE}📅 Optimized Automation Schedule${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   📊 Daily Updates:   Every night at 3:15 AM UTC (10:15 PM CDT)"
echo "   📈 Weekly Updates:  Sunday nights at 3:30 AM UTC (10:30 PM CDT)"
echo "   📅 Monthly Updates: 1st of month at 3:45 AM UTC (10:45 PM CDT previous day)"
echo ""

# Automation performance analysis
echo -e "${BOLD}${BLUE}📊 Automation Performance Analysis${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Last 7 days of automation
echo "   Last 7 Days Automation History:"
echo "   Date       | Type    | Status | UTC Time    | Local Time"
echo "   -----------|---------|--------|-------------|----------------"

for i in {0..6}; do
    if command -v gdate >/dev/null 2>&1; then
        # macOS with GNU date
        check_date=$(gdate -d "$i days ago" +%Y-%m-%d)
        format_date=$(gdate -d "$i days ago" +%Y_%m_%d)
    else
        # Linux date
        check_date=$(date -d "$i days ago" +%Y-%m-%d 2>/dev/null || date -v-${i}d +%Y-%m-%d)
        format_date=$(date -d "$i days ago" +%Y_%m_%d 2>/dev/null || date -v-${i}d +%Y_%m_%d)
    fi
    
    # Check for automation commits on this date
    automation_commit=$(git log --oneline --since="$check_date 00:00" --until="$check_date 23:59" --grep="Auto-update\|🎯\|🤖" | head -1)
    
    if [ -n "$automation_commit" ]; then
        commit_hash=$(echo "$automation_commit" | cut -d' ' -f1)
        commit_time_utc=$(git show -s --format=%cd --date=format:'%H:%M:%S' $commit_hash)
        commit_time_local=$(git show -s --format=%cd --date=local $commit_hash | cut -d' ' -f4)
        
        if echo "$automation_commit" | grep -q "🎯"; then
            auto_type="Enhanced"
        elif echo "$automation_commit" | grep -q "Weekly"; then
            auto_type="Weekly  "
        elif echo "$automation_commit" | grep -q "Monthly"; then
            auto_type="Monthly "
        else
            auto_type="Daily   "
        fi
        
        echo -e "   $check_date | $auto_type | ${GREEN}✅ Done${NC} | $commit_time_utc | $commit_time_local"
    else
        echo -e "   $check_date | N/A     | ${RED}❌ None${NC} | --:--:-- | --:--:--"
    fi
done

echo ""

# File generation status
echo -e "${BOLD}${BLUE}📁 Generated Files Status${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

TODAY=$(date +%Y_%m_%d)

# Check daily chart
if [ -f "slides/gantt_daily_$TODAY.png" ]; then
    daily_time=$(stat -c %y "slides/gantt_daily_$TODAY.png" 2>/dev/null || stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "slides/gantt_daily_$TODAY.png")
    show_status "success" "Today's daily chart: $daily_time"
else
    show_status "warning" "Today's daily chart missing (may generate tonight)"
fi

# Check weekly chart (latest)
if ls slides/gantt_weekly_* >/dev/null 2>&1; then
    latest_weekly=$(ls -t slides/gantt_weekly_* | head -1)
    weekly_time=$(stat -c %y "$latest_weekly" 2>/dev/null || stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$latest_weekly")
    show_status "success" "Latest weekly chart: $weekly_time"
else
    show_status "error" "No weekly charts found"
fi

# Check monthly charts
current_month=$(date +%Y_%m)
if ls slides/gantt_$current_month*.png >/dev/null 2>&1; then
    show_status "success" "Current month charts available"
else
    show_status "warning" "Current month charts missing"
fi

# Check calendar
if [ -f "slides/calendar_$current_month.png" ]; then
    calendar_time=$(stat -c %y "slides/calendar_$current_month.png" 2>/dev/null || stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "slides/calendar_$current_month.png")
    show_status "success" "Current calendar: $calendar_time"
else
    show_status "warning" "Current month calendar missing"
fi

echo ""

# Automation health assessment
echo -e "${BOLD}${BLUE}🏥 Automation Health Assessment${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Check last automation time
last_automation=$(git log -1 --grep="Auto-update\|🎯\|🤖" --pretty=format:"%ct" 2>/dev/null)
if [ -n "$last_automation" ]; then
    current_time=$(date +%s)
    hours_since=$(( (current_time - last_automation) / 3600 ))
    
    if [ $hours_since -lt 24 ]; then
        show_status "success" "Last automation: $hours_since hours ago (HEALTHY)"
    elif [ $hours_since -lt 48 ]; then
        show_status "warning" "Last automation: $hours_since hours ago (MONITOR)"
    else
        show_status "error" "Last automation: $hours_since hours ago (CRITICAL)"
    fi
else
    show_status "error" "No automation history found"
fi

# Repository status
if git status --porcelain | grep -q .; then
    show_status "warning" "Repository has uncommitted changes"
else
    show_status "success" "Repository is clean and synchronized"
fi

# Check if automation should have run recently
current_hour=$(date +%H)
current_min=$(date +%M)
cdt_hour=$(TZ=America/Chicago date +%H)

if [ "$cdt_hour" -ge 22 ] && [ "$cdt_hour" -lt 23 ]; then
    if [ -f "slides/gantt_daily_$TODAY.png" ]; then
        show_status "success" "Tonight's automation completed successfully"
    else
        show_status "pending" "Tonight's automation may be running or pending"
    fi
fi

echo ""

# Next automation prediction
echo -e "${BOLD}${BLUE}⏰ Next Automation Predictions${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Daily prediction
if [ "$cdt_hour" -lt 22 ]; then
    minutes_until=$(( (22 - cdt_hour) * 60 + (15 - current_min) ))
    show_status "info" "Daily automation in ~$minutes_until minutes (10:15 PM CDT)"
elif [ "$cdt_hour" -eq 22 ] && [ "$current_min" -lt 15 ]; then
    minutes_until=$((15 - current_min))
    show_status "pending" "Daily automation starting in $minutes_until minutes!"
else
    show_status "info" "Next daily automation: Tomorrow at 10:15 PM CDT"
fi

# Weekly prediction
day_of_week=$(date +%u)
if [ "$day_of_week" -eq 7 ]; then
    if [ "$cdt_hour" -lt 22 ] || ([ "$cdt_hour" -eq 22 ] && [ "$current_min" -lt 30 ]); then
        show_status "info" "Weekly automation today at 10:30 PM CDT"
    else
        show_status "info" "Next weekly automation: Next Sunday at 10:30 PM CDT"
    fi
else
    days_until_sunday=$((7 - day_of_week))
    show_status "info" "Next weekly automation: In $days_until_sunday days (Sunday 10:30 PM CDT)"
fi

# Monthly prediction
today=$(date +%d)
if [ "$today" -eq 1 ]; then
    show_status "info" "Monthly automation today at 10:45 PM CDT"
else
    # Calculate next month's first day
    show_status "info" "Next monthly automation: 1st of next month at 10:45 PM CDT"
fi

echo ""

# Quick actions
echo -e "${BOLD}${BLUE}🔧 Quick Actions${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "   📊 GitHub Actions:    https://github.com/dylantneal/Encore_Dashboard/actions"
echo "   🌐 Live Dashboard:    https://www.marquisdashboard.com"
echo "   🔧 Manual Trigger:    ./trigger_manual_update.sh"
echo "   🚨 Emergency Update:  ./emergency_manual_update.sh"
echo "   📖 Schedule Guide:    cat OPTIMIZED_AUTOMATION_SCHEDULE.md"
echo "   🔄 Update Status:     ./check_automation_status.sh"
echo ""

echo -e "${BOLD}${GREEN}🎉 Dashboard generated at: $(date)${NC}"
echo -e "${CYAN}💡 Run this script anytime to check automation health!${NC}"