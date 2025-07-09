#!/bin/bash
# verify_midnight_automation.sh
# Script to verify that midnight automation will work properly

echo "======================================"
echo "MIDNIGHT AUTOMATION VERIFICATION"
echo "======================================"
echo ""

# Get current time
CURRENT_TIME=$(date "+%Y-%m-%d %H:%M:%S")
echo "Current time: $CURRENT_TIME"
echo ""

# Check cron service status
echo "1. CHECKING CRON SERVICE:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if launchctl list | grep -q com.vix.cron; then
        echo "✅ Cron service is running on macOS"
    else
        echo "❌ Cron service NOT running! Run: sudo launchctl load -w /System/Library/LaunchDaemons/com.vix.cron.plist"
    fi
else
    # Linux
    if systemctl is-active --quiet cron; then
        echo "✅ Cron service is running"
    else
        echo "❌ Cron service NOT running! Run: sudo systemctl start cron"
    fi
fi
echo ""

# Check crontab entries
echo "2. CHECKING CRONTAB ENTRIES:"
CRON_COUNT=$(crontab -l 2>/dev/null | grep -c "update.py")
if [ $CRON_COUNT -gt 0 ]; then
    echo "✅ Found $CRON_COUNT automation entries in crontab"
    echo ""
    echo "Your cron jobs:"
    crontab -l | grep "update.py" | while read -r line; do
        echo "   $line"
    done
else
    echo "❌ No automation entries found in crontab!"
fi
echo ""

# Test Python scripts
echo "3. TESTING UPDATE SCRIPTS:"
for script in daily_update.py weekly_update.py monthly_update.py; do
    if [ -f "$script" ]; then
        echo -n "   Testing $script... "
        if python3 -c "import ast; ast.parse(open('$script').read())" 2>/dev/null; then
            echo "✅ Valid Python syntax"
        else
            echo "❌ Syntax error!"
        fi
    else
        echo "   ❌ $script not found!"
    fi
done
echo ""

# Check git configuration
echo "4. CHECKING GIT CONFIGURATION:"
if git remote -v | grep -q "github.com"; then
    echo "✅ GitHub remote configured"
    
    # Test SSH key
    echo -n "   Testing SSH access... "
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        echo "✅ SSH key works"
    else
        echo "⚠️  SSH key may need configuration"
    fi
else
    echo "❌ No GitHub remote found"
fi
echo ""

# Check recent git commits
echo "5. RECENT AUTOMATION ACTIVITY:"
RECENT_COMMITS=$(git log --oneline --since="7 days ago" | grep -c "Auto-update")
if [ $RECENT_COMMITS -gt 0 ]; then
    echo "✅ Found $RECENT_COMMITS auto-update commits in the last 7 days"
    echo "   Recent auto-commits:"
    git log --oneline --since="7 days ago" | grep "Auto-update" | head -5 | while read -r line; do
        echo "   $line"
    done
else
    echo "⚠️  No recent auto-update commits found"
fi
echo ""

# Check for any cron errors
echo "6. CHECKING FOR CRON ERRORS:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS - check system log
    CRON_ERRORS=$(log show --predicate 'eventMessage contains "cron"' --last 24h 2>/dev/null | grep -c ERROR)
    if [ $CRON_ERRORS -eq 0 ]; then
        echo "✅ No cron errors in last 24 hours"
    else
        echo "⚠️  Found $CRON_ERRORS cron errors in system log"
    fi
else
    # Linux - check syslog
    if [ -f /var/log/syslog ]; then
        CRON_ERRORS=$(grep -c "CRON.*ERROR" /var/log/syslog 2>/dev/null || echo "0")
        if [ $CRON_ERRORS -eq 0 ]; then
            echo "✅ No cron errors in syslog"
        else
            echo "⚠️  Found $CRON_ERRORS cron errors"
        fi
    fi
fi
echo ""

# Final summary
echo "======================================"
echo "SUMMARY:"
echo "======================================"

# Calculate next midnight
NEXT_MIDNIGHT=$(date -v+1d -v0H -v0M -v0S "+%Y-%m-%d %H:%M:%S" 2>/dev/null || date -d "tomorrow 00:00:00" "+%Y-%m-%d %H:%M:%S" 2>/dev/null)
echo "Next midnight: $NEXT_MIDNIGHT"
echo ""

echo "At midnight, the following will happen:"
echo "1. daily_update.py will generate 'Happening Today' chart"
echo "2. Charts will be saved to slides/ directory"
echo "3. git_auto_commit.py will push changes to GitHub"
echo "4. All devices pulling from GitHub will get updates"
echo ""

echo "To monitor automation:"
echo "- Check logs: tail -f logs/daily_update_$(date +%Y%m%d).log"
echo "- Watch git: git log --oneline --since='1 day ago'"
echo "- View charts: ls -la slides/"
echo ""

echo "🎯 If all checks passed, your automation is ROCK SOLID!"
echo "🔧 If any issues found, fix them before midnight." 