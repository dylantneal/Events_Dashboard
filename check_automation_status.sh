#!/bin/bash
# Enhanced Automation Status Checker - Optimized for new 10:15 PM CDT schedule

# Color codes for better visibility
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${CYAN}🚀 Enhanced Automation Status Check${NC}"
echo "==========================================="
echo ""

# Get current times in different zones
LOCAL_TIME=$(date)
UTC_TIME=$(TZ=UTC date)
CDT_TIME=$(TZ=America/Chicago date)

echo -e "${BLUE}🕒 Current Time Context:${NC}"
echo "   Local: $LOCAL_TIME"
echo "   UTC:   $UTC_TIME"
echo "   CDT:   $CDT_TIME"
echo ""

# New automation schedule info
echo -e "${PURPLE}📋 Optimized Schedule (Post Phase-2):${NC}"
echo "   Daily:   3:15 AM UTC = 10:15 PM CDT (Every night)"
echo "   Weekly:  3:30 AM UTC = 10:30 PM CDT (Sunday nights)"  
echo "   Monthly: 3:45 AM UTC = 10:45 PM CDT (Last day of month)"
echo ""

# Check local git status
echo -e "${BLUE}📍 Local Repository Status:${NC}"
if git status --porcelain | grep -q .; then
    echo -e "   ${YELLOW}⚠️  Local changes present${NC}"
    git status --short
else
    echo -e "   ${GREEN}✅ Repository clean and synced${NC}"
fi
echo ""

# Enhanced recent automation activity with timestamps
echo -e "${BLUE}📊 Recent Automation Activity (Last 10):${NC}"
echo "   Commit | UTC Time           | Message"
echo "   -------|--------------------|---------"
git log --pretty=format:"%C(auto)%h%Creset | %C(blue)%ad%Creset | %C(green)%s%Creset" --date=format:'%Y-%m-%d %H:%M:%S' --grep="Auto-update\|🎯\|🤖" -10 2>/dev/null || echo -e "   ${RED}❌ No recent auto-updates found${NC}"
echo ""

# File generation analysis
TODAY=$(date +%Y_%m_%d)
YESTERDAY=$(date -d "yesterday" +%Y_%m_%d 2>/dev/null || date -v-1d +%Y_%m_%d)

echo -e "${BLUE}📅 Generated Files Analysis:${NC}"

# Check today's files
echo -e "   ${CYAN}Today ($TODAY):${NC}"
if ls slides/gantt_daily_*${TODAY}* >/dev/null 2>&1; then
    DAILY_FILE=$(ls slides/gantt_daily_*${TODAY}* | head -1)
    DAILY_TIME=$(stat -c %y "$DAILY_FILE" 2>/dev/null || stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$DAILY_FILE")
    echo -e "     ${GREEN}✅ Daily chart: $DAILY_TIME${NC}"
else
    echo -e "     ${RED}❌ No daily chart for today${NC}"
fi

if ls slides/gantt_*$(date +%Y_%m).png >/dev/null 2>&1; then
    echo -e "     ${GREEN}✅ Monthly charts present${NC}"
fi

# Check if it's Sunday and look for weekly files
if [ "$(date +%u)" -eq 7 ]; then
    echo -e "   ${CYAN}Weekly Check (Sunday):${NC}"
    if ls slides/gantt_weekly_* >/dev/null 2>&1; then
        WEEKLY_FILE=$(ls -t slides/gantt_weekly_* | head -1)
        WEEKLY_TIME=$(stat -c %y "$WEEKLY_FILE" 2>/dev/null || stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "$WEEKLY_FILE")
        echo -e "     ${GREEN}✅ Latest weekly: $WEEKLY_TIME${NC}"
    else
        echo -e "     ${RED}❌ No weekly chart found${NC}"
    fi
fi

# Check if it's first of month
if [ "$(date +%d)" -eq 1 ]; then
    echo -e "   ${CYAN}Monthly Check (1st of month):${NC}"
    if ls slides/calendar_$(date +%Y_%m).png >/dev/null 2>&1; then
        echo -e "     ${GREEN}✅ Current month calendar exists${NC}"
    else
        echo -e "     ${RED}❌ Current month calendar missing${NC}"
    fi
fi

echo ""

# Next scheduled run prediction
echo -e "${BLUE}⏰ Next Scheduled Automation:${NC}"
CURRENT_HOUR=$(date +%H)
if [ "$CURRENT_HOUR" -lt 22 ]; then
    echo -e "   ${GREEN}🕙 Tonight at 10:15 PM CDT (Daily automation)${NC}"
elif [ "$CURRENT_HOUR" -eq 22 ]; then
    CURRENT_MIN=$(date +%M)
    if [ "$CURRENT_MIN" -lt 15 ]; then
        echo -e "   ${YELLOW}🔥 Daily automation should start in $((15 - CURRENT_MIN)) minutes!${NC}"
    else
        echo -e "   ${GREEN}⚡ Daily automation should be running now or just finished${NC}"
    fi
else
    echo -e "   ${GREEN}🌙 Next: Tomorrow at 10:15 PM CDT (Daily)${NC}"
fi

# Special checks for Sunday/Monday
DAY_OF_WEEK=$(date +%u)
if [ "$DAY_OF_WEEK" -eq 7 ]; then
    echo -e "   ${PURPLE}📅 Today is Sunday - Weekly automation at 10:30 PM CDT${NC}"
fi

# Check if today is last day of month
TOMORROW=$(date -d "tomorrow" +%d 2>/dev/null || date -v+1d +%d)
if [ "$TOMORROW" -eq 1 ]; then
    echo -e "   ${PURPLE}📅 Last day of month - Monthly automation at 10:45 PM CDT${NC}"
fi

echo ""

# Enhanced status summary
echo -e "${BLUE}📋 AUTOMATION HEALTH SUMMARY:${NC}"

# Check for recent automation (within expected window)
HOURS_SINCE_LAST=$(git log -1 --grep="Auto-update\|🎯\|🤖" --pretty=format:"%ct" 2>/dev/null)
if [ -n "$HOURS_SINCE_LAST" ]; then
    CURRENT_TIME=$(date +%s)
    HOURS_DIFF=$(( (CURRENT_TIME - HOURS_SINCE_LAST) / 3600 ))
    
    if [ "$HOURS_DIFF" -lt 24 ]; then
        echo -e "   ${GREEN}✅ Automation ACTIVE (last run $HOURS_DIFF hours ago)${NC}"
    elif [ "$HOURS_DIFF" -lt 48 ]; then
        echo -e "   ${YELLOW}⚠️  Automation DELAYED (last run $HOURS_DIFF hours ago)${NC}"
    else
        echo -e "   ${RED}❌ Automation STALLED (last run $HOURS_DIFF hours ago)${NC}"
    fi
else
    echo -e "   ${RED}❌ No automation activity found${NC}"
fi

# Check today's chart availability
if [ -f "slides/gantt_daily_$(date +%Y_%m_%d).png" ]; then
    echo -e "   ${GREEN}✅ Today's chart available${NC}"
else
    echo -e "   ${YELLOW}⚠️  Today's chart missing (may run tonight)${NC}"
fi

# Repository sync status
if git status --porcelain | grep -q .; then
    echo -e "   ${YELLOW}⚠️  Local repository has uncommitted changes${NC}"
else
    echo -e "   ${GREEN}✅ Repository fully synchronized${NC}"
fi

echo ""

# Quick links section
echo -e "${BLUE}🔗 Quick Access:${NC}"
echo "   📊 GitHub Actions: https://github.com/dylantneal/Encore_Dashboard/actions"
echo "   🌐 Live Dashboard: https://www.marquisdashboard.com"
echo "   📋 Schedule Guide: cat OPTIMIZED_AUTOMATION_SCHEDULE.md"
echo ""

# Troubleshooting section
echo -e "${BLUE}🛠️  Troubleshooting:${NC}"
echo "   🔧 Manual trigger: Go to Actions → Enhanced Daily Dashboard Update → Run workflow"
echo "   🚨 Emergency update: ./emergency_manual_update.sh"
echo "   📖 View schedule: cat OPTIMIZED_AUTOMATION_SCHEDULE.md"
echo "   🔄 Pull latest: git pull origin main"

echo ""
echo -e "${CYAN}✨ Phase 2 Optimization Complete! Expecting reliable 10:15 PM CDT runs.${NC}"