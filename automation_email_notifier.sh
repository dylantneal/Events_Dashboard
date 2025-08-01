#!/bin/bash
# Automation Email Notifier - Send email alerts for automation status

# Configuration (customize these)
EMAIL_RECIPIENT="your-email@example.com"  # Change this to your email
EMAIL_SUBJECT_PREFIX="[Dashboard Automation]"
SMTP_SERVER="smtp.gmail.com"
SMTP_PORT="587"

# Color codes for logging
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Function to log messages
log_message() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')] $1${NC}"
}

# Function to check if email is configured
check_email_config() {
    if [ "$EMAIL_RECIPIENT" = "your-email@example.com" ]; then
        echo -e "${YELLOW}⚠️  Email not configured. Edit this script to set your email address.${NC}"
        echo "   1. Open: automation_email_notifier.sh"
        echo "   2. Change EMAIL_RECIPIENT to your email"
        echo "   3. Configure SMTP settings if needed"
        return 1
    fi
    return 0
}

# Function to send email (requires mailx or similar)
send_email() {
    local subject="$1"
    local body="$2"
    local priority="$3"  # normal, high, low
    
    if ! check_email_config; then
        return 1
    fi
    
    # Try different email methods
    if command -v mail &> /dev/null; then
        echo "$body" | mail -s "$EMAIL_SUBJECT_PREFIX $subject" "$EMAIL_RECIPIENT"
        return $?
    elif command -v mailx &> /dev/null; then
        echo "$body" | mailx -s "$EMAIL_SUBJECT_PREFIX $subject" "$EMAIL_RECIPIENT"
        return $?
    elif command -v sendmail &> /dev/null; then
        {
            echo "To: $EMAIL_RECIPIENT"
            echo "Subject: $EMAIL_SUBJECT_PREFIX $subject"
            echo "Content-Type: text/plain"
            echo ""
            echo "$body"
        } | sendmail "$EMAIL_RECIPIENT"
        return $?
    else
        log_message "❌ No email command found (mail, mailx, or sendmail)"
        echo -e "${YELLOW}💡 Install mail utility: brew install mailutils${NC}"
        return 1
    fi
}

# Function to check automation health and send alerts
check_and_notify() {
    local check_type="$1"  # daily, weekly, monthly, or health
    
    log_message "🔍 Checking automation status..."
    
    # Get last automation time
    last_automation=$(git log -1 --grep="Auto-update\|🎯\|🤖" --pretty=format:"%ct" 2>/dev/null)
    
    if [ -n "$last_automation" ]; then
        current_time=$(date +%s)
        hours_since=$(( (current_time - last_automation) / 3600 ))
        last_commit_msg=$(git log -1 --grep="Auto-update\|🎯\|🤖" --pretty=format:"%s" 2>/dev/null)
        last_commit_date=$(git log -1 --grep="Auto-update\|🎯\|🤖" --pretty=format:"%ad" --date=local 2>/dev/null)
    else
        hours_since=999
        last_commit_msg="No automation found"
        last_commit_date="Unknown"
    fi
    
    # Check current files
    TODAY=$(date +%Y_%m_%d)
    daily_chart_exists=false
    if [ -f "slides/gantt_daily_$TODAY.png" ]; then
        daily_chart_exists=true
        daily_chart_time=$(stat -c %y "slides/gantt_daily_$TODAY.png" 2>/dev/null || stat -f "%Sm" -t "%Y-%m-%d %H:%M:%S" "slides/gantt_daily_$TODAY.png")
    fi
    
    # Determine notification type and content
    case $check_type in
        "daily")
            if [ $hours_since -lt 2 ] && [ "$daily_chart_exists" = true ]; then
                # Success notification
                send_email "✅ Daily Automation Successful" \
"Daily automation completed successfully!

📅 Date: $(date '+%A, %B %d, %Y')
⏰ Completed: $last_commit_date
📊 Today's chart: $daily_chart_time
💬 Commit: $last_commit_msg

🌐 View dashboard: https://www.marquisdashboard.com
📊 GitHub Actions: https://github.com/dylantneal/Encore_Dashboard/actions

✨ Your dashboard is up to date!"
                log_message "✅ Daily success notification sent"
            fi
            ;;
            
        "failure")
            if [ $hours_since -gt 25 ]; then
                # Failure notification
                send_email "❌ Automation Failure Alert" \
"⚠️ Dashboard automation appears to have failed!

🚨 Issue: No automation activity in $hours_since hours
📅 Last successful run: $last_commit_date
💬 Last commit: $last_commit_msg
📊 Today's chart status: $([ "$daily_chart_exists" = true ] && echo "✅ Present" || echo "❌ Missing")

🔧 Recommended actions:
1. Check GitHub Actions: https://github.com/dylantneal/Encore_Dashboard/actions
2. Trigger manual update: ./trigger_manual_update.sh
3. Check automation health: ./automation_health_dashboard.sh

This is an automated alert from your dashboard monitoring system."
                log_message "❌ Failure notification sent"
            fi
            ;;
            
        "health")
            # Weekly health report
            send_email "📊 Weekly Automation Health Report" \
"📋 Weekly Dashboard Automation Report

📊 Automation Statistics (Last 7 Days):
- Last automation: $hours_since hours ago
- Status: $([ $hours_since -lt 24 ] && echo "✅ Healthy" || echo "⚠️ Needs attention")
- Today's chart: $([ "$daily_chart_exists" = true ] && echo "✅ Available" || echo "❌ Missing")

🔄 Recent Activity:
$last_commit_msg
Completed: $last_commit_date

📈 Next Scheduled Updates:
- Daily: Tonight at 10:15 PM CDT
- Weekly: Next Sunday at 10:30 PM CDT  
- Monthly: 1st of next month at 10:45 PM CDT

🌐 Dashboard: https://www.marquisdashboard.com
📊 Monitor: https://github.com/dylantneal/Encore_Dashboard/actions

This is your weekly automated health report."
            log_message "📊 Health report sent"
            ;;
    esac
}

# Main script logic
case "${1:-health}" in
    "daily")
        check_and_notify "daily"
        ;;
    "failure")
        check_and_notify "failure"
        ;;
    "health")
        check_and_notify "health"
        ;;
    "test")
        if check_email_config; then
            send_email "🧪 Test Notification" \
"This is a test email from your Dashboard Automation monitoring system.

✅ Email configuration is working correctly!
📅 Sent: $(date)
🖥️  From: $(hostname)

Your automation notifications are ready to go!"
            if [ $? -eq 0 ]; then
                log_message "✅ Test email sent successfully"
            else
                log_message "❌ Test email failed"
            fi
        fi
        ;;
    "config")
        echo -e "${BLUE}📧 Email Configuration:${NC}"
        echo "   Recipient: $EMAIL_RECIPIENT"
        echo "   SMTP Server: $SMTP_SERVER:$SMTP_PORT"
        echo ""
        if check_email_config; then
            echo -e "${GREEN}✅ Configuration looks good${NC}"
            echo -e "${YELLOW}💡 Run: $0 test${NC}"
        else
            echo -e "${YELLOW}⚠️  Please configure email settings${NC}"
        fi
        ;;
    *)
        echo "📧 Automation Email Notifier"
        echo "Usage: $0 [daily|failure|health|test|config]"
        echo ""
        echo "Commands:"
        echo "  daily   - Send daily success notification"
        echo "  failure - Send failure alert if automation is stuck"
        echo "  health  - Send weekly health report"
        echo "  test    - Send test email"
        echo "  config  - Show configuration"
        echo ""
        echo "Setup:"
        echo "  1. Edit this script to set your email address"
        echo "  2. Test: $0 test"
        echo "  3. Add to cron for automatic notifications"
        ;;
esac