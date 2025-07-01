#!/bin/bash
# setup_cron.sh
# Automated setup script for monthly dashboard updates with calendar views

# Get the current directory (project root)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "====================================="
echo "Dashboard Update Setup (Gantt + Calendar)"
echo "Now with Automatic GitHub Sync!"
echo "====================================="
echo "Project directory: $PROJECT_DIR"
echo ""

# Check git configuration for auto-commit feature
echo "--- Checking Git Configuration ---"
if [ -d "$PROJECT_DIR/.git" ]; then
    echo "✅ Git repository detected"
    
    # Check if remote is configured
    cd "$PROJECT_DIR"
    if git remote get-url origin >/dev/null 2>&1; then
        echo "✅ Git remote configured: $(git remote get-url origin)"
        
        # Check if we can push
        echo "Testing git push access..."
        if git push --dry-run origin main >/dev/null 2>&1; then
            echo "✅ Git push access confirmed - Auto-sync will work!"
            GIT_SYNC_AVAILABLE=true
        else
            echo "⚠️  Cannot push to git remote"
            echo "   Auto-commit will be disabled"
            echo "   To enable: Configure SSH keys or personal access token"
            echo "   See AUTOMATED_IMAGE_SYNC.md for instructions"
            GIT_SYNC_AVAILABLE=false
        fi
    else
        echo "⚠️  No git remote configured"
        echo "   Auto-commit will be disabled"
        GIT_SYNC_AVAILABLE=false
    fi
else
    echo "⚠️  Not a git repository"
    echo "   Auto-commit will be disabled"
    GIT_SYNC_AVAILABLE=false
fi
echo ""

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed or not in PATH"
    echo "Please install Python 3 and try again."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if required files exist
if [ ! -f "$PROJECT_DIR/pipeline.xlsx" ]; then
    echo "❌ Error: pipeline.xlsx not found in project directory"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/flex_gantt.py" ]; then
    echo "❌ Error: flex_gantt.py not found in project directory"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/monthly_update.py" ]; then
    echo "❌ Error: monthly_update.py not found in project directory"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/weekly_update.py" ]; then
    echo "❌ Error: weekly_update.py not found in project directory"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/daily_update.py" ]; then
    echo "❌ Error: daily_update.py not found in project directory"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/calendar_update.py" ]; then
    echo "❌ Error: calendar_update.py not found in project directory"
    exit 1
fi

if [ ! -f "$PROJECT_DIR/git_auto_commit.py" ]; then
    echo "⚠️  Warning: git_auto_commit.py not found"
    echo "   Auto-sync to GitHub will not work"
    echo "   Create this file to enable automatic image distribution"
    GIT_SYNC_AVAILABLE=false
else
    echo "✅ git_auto_commit.py found"
fi

echo "✅ All required files found"

# Test the script
echo ""
echo "Testing the update scripts..."
cd "$PROJECT_DIR"

echo "Testing monthly update script (includes calendar generation)..."
if python3 monthly_update.py; then
    echo "✅ Monthly update test successful! (Gantt charts + Calendar generated)"
else
    echo "❌ Monthly update test failed. Please check the error messages above."
    exit 1
fi

echo ""
echo "Testing calendar update script..."
if python3 calendar_update.py; then
    echo "✅ Calendar update test successful!"
else
    echo "❌ Calendar update test failed. Please check the error messages above."
    exit 1
fi

echo ""
echo "Testing weekly update script..."
if python3 weekly_update.py; then
    echo "✅ Weekly update test successful!"
else
    echo "❌ Weekly update test failed. Please check the error messages above."
    exit 1
fi

echo ""
echo "Testing daily update script..."
if python3 daily_update.py; then
    echo "✅ Daily update test successful!"
else
    echo "❌ Daily update test failed. Please check the error messages above."
    exit 1
fi

echo ""
echo "====================================="
echo "Cron Job Setup"
echo "====================================="
echo ""
echo "Choose automation type:"
echo "1. Monthly updates only (3-month rolling window + calendar)"
echo "2. Weekly updates only ('Happening This Week' chart)"
echo "3. Daily updates only ('Happening Today' chart)"
echo "4. Monthly + Weekly (recommended for general use)"
echo "5. Weekly + Daily (recommended for immediate awareness)"
echo "6. All three updates (complete automation)"
echo "7. Calendar-only updates (professional calendar view)"
echo "8. Manual setup (skip automatic configuration)"
echo ""

read -p "Select option (1-8): " -n 1 -r
echo ""
echo ""

case $REPLY in
    1)
        echo "Setting up monthly updates (Gantt charts + calendar)..."
        MONTHLY_CRON="0 6 1 * * cd \"$PROJECT_DIR\" && python3 monthly_update.py"
        (crontab -l 2>/dev/null; echo "$MONTHLY_CRON") | crontab -
        echo "✅ Monthly cron job added: Updates on 1st of each month at 6 AM"
        echo "   📊 3-month rolling Gantt charts"
        echo "   📅 Professional calendar view"
        ;;
    2)
        echo "Setting up weekly updates only..."
        WEEKLY_CRON="0 0 * * 1 cd \"$PROJECT_DIR\" && python3 weekly_update.py"
        (crontab -l 2>/dev/null; echo "$WEEKLY_CRON") | crontab -
        echo "✅ Weekly cron job added: Updates every Monday at midnight"
        ;;
    3)
        echo "Setting up daily updates only..."
        DAILY_CRON="0 0 * * * cd \"$PROJECT_DIR\" && python3 daily_update.py"
        (crontab -l 2>/dev/null; echo "$DAILY_CRON") | crontab -
        echo "✅ Daily cron job added: Updates every day at midnight"
        ;;
    4)
        echo "Setting up monthly and weekly updates..."
        MONTHLY_CRON="0 6 1 * * cd \"$PROJECT_DIR\" && python3 monthly_update.py"
        WEEKLY_CRON="0 0 * * 1 cd \"$PROJECT_DIR\" && python3 weekly_update.py"
        (crontab -l 2>/dev/null; echo "$MONTHLY_CRON"; echo "$WEEKLY_CRON") | crontab -
        echo "✅ Cron jobs added:"
        echo "   📅 Monthly: 1st of each month at 6 AM (Gantt + Calendar)"
        echo "   📅 Weekly: Every Monday at midnight"
        ;;
    5)
        echo "Setting up weekly and daily updates..."
        WEEKLY_CRON="0 0 * * 1 cd \"$PROJECT_DIR\" && python3 weekly_update.py"
        DAILY_CRON="0 0 * * * cd \"$PROJECT_DIR\" && python3 daily_update.py"
        (crontab -l 2>/dev/null; echo "$WEEKLY_CRON"; echo "$DAILY_CRON") | crontab -
        echo "✅ Cron jobs added:"
        echo "   📅 Weekly: Every Monday at midnight"
        echo "   📅 Daily: Every day at midnight"
        ;;
    6)
        echo "Setting up all three updates (complete automation)..."
        MONTHLY_CRON="0 6 1 * * cd \"$PROJECT_DIR\" && python3 monthly_update.py"
        WEEKLY_CRON="0 0 * * 1 cd \"$PROJECT_DIR\" && python3 weekly_update.py"
        DAILY_CRON="0 0 * * * cd \"$PROJECT_DIR\" && python3 daily_update.py"
        (crontab -l 2>/dev/null; echo "$MONTHLY_CRON"; echo "$WEEKLY_CRON"; echo "$DAILY_CRON") | crontab -
        echo "✅ All cron jobs added:"
        echo "   📅 Monthly: 1st of each month at 6 AM (Gantt + Calendar)"
        echo "   📅 Weekly: Every Monday at midnight"
        echo "   📅 Daily: Every day at midnight"
        ;;
    7)
        echo "Setting up calendar-only updates..."
        CALENDAR_CRON="0 0 1 * * cd \"$PROJECT_DIR\" && python3 calendar_update.py"
        (crontab -l 2>/dev/null; echo "$CALENDAR_CRON") | crontab -
        echo "✅ Calendar cron job added: Updates on 1st of each month at midnight"
        echo "   📅 Professional calendar view only"
        ;;
    8)
        echo "Skipping automatic cron job setup."
        echo ""
        echo "Manual setup instructions:"
        echo ""
        echo "For monthly updates (3-month rolling window + calendar):"
        echo "   0 6 1 * * cd \"$PROJECT_DIR\" && python3 monthly_update.py"
        echo ""
        echo "For weekly updates ('Happening This Week'):"
        echo "   0 0 * * 1 cd \"$PROJECT_DIR\" && python3 weekly_update.py"
        echo ""
        echo "For daily updates ('Happening Today'):"
        echo "   0 0 * * * cd \"$PROJECT_DIR\" && python3 daily_update.py"
        echo ""
        echo "For calendar-only updates:"
        echo "   0 0 1 * * cd \"$PROJECT_DIR\" && python3 calendar_update.py"
        echo ""
        echo "To add these manually: crontab -e"
        ;;
    *)
        echo "Invalid option. Skipping cron job setup."
        ;;
esac

if [[ $REPLY =~ ^[1-7]$ ]]; then
    echo ""
    echo "Current crontab entries:"
    crontab -l | grep -E "(monthly_update|weekly_update|daily_update|calendar_update|flex_gantt)" || echo "(No matching entries found)"
fi

echo ""
echo "====================================="
echo "Setup Complete!"
echo "====================================="
echo ""
echo "✅ Rolling window functionality is ready"
echo "✅ Professional calendar generation is ready"
echo "✅ Monthly update script is working (includes calendar)" 
echo "✅ Calendar-only update script is working"
echo "✅ Weekly update script is working"
echo "✅ Daily update script is working"
if [ "$GIT_SYNC_AVAILABLE" = "true" ]; then
    echo "✅ Automatic GitHub sync is ENABLED"
    echo "   Images will be pushed to GitHub automatically"
    echo "   All screens will receive updates within minutes"
else
    echo "⚠️  Automatic GitHub sync is DISABLED"
    echo "   Manual git commit and push required after updates"
    echo "   See AUTOMATED_IMAGE_SYNC.md for setup instructions"
fi
echo "📁 Log files will be saved to: $PROJECT_DIR/logs/"
echo "🖼️  Chart files will be updated in: $PROJECT_DIR/slides/"
echo ""
echo "Manual commands:"
echo "- Monthly update: python3 monthly_update.py (Gantt + Calendar)"
echo "- Calendar only: python3 calendar_update.py"
echo "- Weekly update: python3 weekly_update.py"
echo "- Daily update: python3 daily_update.py"
echo "- Manual calendar: python3 flex_gantt.py pipeline.xlsx --calendar --dashboard"
echo "- Manual daily chart: python3 flex_gantt.py pipeline.xlsx --daily --dashboard"
echo "- Manual weekly chart: python3 flex_gantt.py pipeline.xlsx --weekly --dashboard"
echo "- Check logs: ls -la logs/"
echo "- View cron jobs: crontab -l"
echo "" 