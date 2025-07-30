#!/bin/bash
# Script to safely disable local cron jobs and rely on GitHub Actions

echo "🔧 Disabling Local Cron Jobs..."
echo "================================"

# Backup current crontab
echo "📦 Backing up current crontab..."
crontab -l > crontab_backup_$(date +%Y%m%d_%H%M%S).txt

# Remove dashboard-related cron jobs
echo "🗑️  Removing dashboard cron jobs..."
crontab -l | grep -v "monthly_update.py" | grep -v "weekly_update.py" | grep -v "daily_update.py" | crontab -

echo "✅ Local cron jobs disabled!"
echo ""
echo "📊 Your automation now runs entirely on GitHub:"
echo "   • Daily updates: Midnight UTC"
echo "   • Weekly updates: Mondays"
echo "   • Monthly updates: 1st of month"
echo ""
echo "🌐 Monitor at: https://github.com/dylantneal/Encore_Dashboard/actions"
echo "📱 Live site: https://www.marquisdashboard.com"