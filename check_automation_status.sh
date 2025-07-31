#!/bin/bash
# check_automation_status.sh - Monitor GitHub Actions automation status

echo "🔍 Automation Status Check"
echo "========================="
echo ""

# Check local git status
echo "📍 Local Repository Status:"
git status --short || echo "❌ Git status failed"
echo ""

# Check last few commits to see automation activity
echo "📊 Recent Automation Activity:"
git log --oneline -5 --grep="Auto-update\|auto-update" || echo "❌ No recent auto-updates found"
echo ""

# Check if today's files exist
TODAY=$(date +%Y_%m_%d)
YESTERDAY=$(date -d "yesterday" +%Y_%m_%d)

echo "📅 Today's Generated Files ($TODAY):"
ls -la slides/gantt_daily_*${TODAY}* 2>/dev/null || echo "❌ No daily chart for today"
ls -la slides/gantt_weekly_*$(date +%Y_%m_%d)* 2>/dev/null && echo "✅ Weekly chart updated"
ls -la slides/gantt_*$(date +%Y_%m).png 2>/dev/null && echo "✅ Monthly charts present"
echo ""

# Check GitHub Actions URL
echo "🌐 Monitor GitHub Actions:"
echo "   https://github.com/dylantneal/Encore_Dashboard/actions"
echo ""

# Check live site
echo "🚀 Live Dashboard:"
echo "   https://www.marquisdashboard.com"
echo ""

# Summary
echo "✅ AUTOMATION STATUS SUMMARY:"
if git log -1 --grep="Auto-update" --since="24 hours ago" >/dev/null 2>&1; then
    echo "   ✅ Automation is WORKING (updates within 24 hours)"
else
    echo "   ⚠️  No automation updates in last 24 hours"
fi

if [ -f "slides/gantt_daily_$(date +%Y_%m_%d).png" ]; then
    echo "   ✅ Today's chart is available"
else
    echo "   ⚠️  Today's chart missing"
fi

echo ""
echo "💡 If automation appears stuck:"
echo "   1. Check GitHub Actions: https://github.com/dylantneal/Encore_Dashboard/actions"
echo "   2. Manual trigger: Go to Actions → Pick workflow → Run workflow"
echo "   3. Emergency update: Run './emergency_manual_update.sh'"