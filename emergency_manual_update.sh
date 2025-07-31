#!/bin/bash
# emergency_manual_update.sh - Emergency manual update when automation fails

echo "🚨 EMERGENCY MANUAL UPDATE"
echo "========================="
echo ""

# Sync with GitHub first
echo "📥 Syncing with GitHub..."
git fetch origin
git reset --hard origin/main
echo "✅ Local repository synced with GitHub"
echo ""

# Run all update types
echo "📊 Generating all charts..."

echo "  📅 Generating today's chart..."
python3 daily_update.py

echo "  📊 Generating weekly chart..."
python3 weekly_update.py

echo "  📈 Generating monthly charts..."
python3 monthly_update.py

echo "  📅 Generating calendar..."
python3 calendar_update.py

echo ""
echo "✅ All charts regenerated locally"
echo ""

# Check results
echo "📁 Generated files:"
ls -la slides/ | grep "$(date +%Y_%m_%d)" || echo "No files with today's date"
ls -la slides/ | grep "$(date +%Y_%m)" || echo "No files for this month"
echo ""

echo "🎯 EMERGENCY UPDATE COMPLETE!"
echo ""
echo "⚠️  Note: These are LOCAL updates only."
echo "GitHub Actions should handle automatic distribution."
echo "If GitHub Actions is broken, changes won't appear on live site."
echo ""
echo "🌐 Check live site: https://www.marquisdashboard.com"
echo "🔍 Monitor GitHub Actions: https://github.com/dylantneal/Encore_Dashboard/actions"