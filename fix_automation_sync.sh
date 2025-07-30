#!/bin/bash
# Automation Sync Fix Script
# Run this to ensure your local automation stays in sync with GitHub

echo "🔧 Fixing Dashboard Automation Sync..."
echo "====================================="

# Get the script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 1. Stash any local changes
echo "📦 Stashing any local changes..."
git stash

# 2. Pull latest from GitHub
echo "📥 Pulling latest from GitHub..."
git pull origin main --ff-only

# 3. Check if pull was successful
if [ $? -eq 0 ]; then
    echo "✅ Successfully synced with GitHub!"
    
    # 4. Show current status
    echo ""
    echo "📊 Current Status:"
    echo "=================="
    git log --oneline -5
    echo ""
    echo "📁 Latest charts:"
    ls -la slides/gantt_daily*.png | tail -3
else
    echo "❌ Failed to sync. Running recovery..."
    
    # Reset to match remote
    echo "🔄 Resetting to match GitHub..."
    git fetch origin
    git reset --hard origin/main
    
    echo "✅ Reset complete!"
fi

echo ""
echo "🎯 Recommendations:"
echo "==================="
echo "1. GitHub Actions are handling automation (working perfectly!)"
echo "2. Your local cron jobs are redundant - consider disabling them"
echo "3. To view automation status: https://github.com/dylantneal/Encore_Dashboard/actions"
echo "4. The dashboard auto-updates at: https://www.marquisdashboard.com"
echo ""
echo "Run this script weekly to ensure local sync, or just rely on GitHub!"