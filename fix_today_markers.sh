#!/bin/bash
# Fix Today Markers - Regenerate all charts with current date markers

echo "🔄 Updating Today Markers for Dashboard Charts"
echo "=============================================="

cd "$(dirname "$0")"

# Get current date for logging
TODAY=$(date +"%Y-%m-%d (%A)")
echo "📅 Today is: $TODAY"
echo ""

# 1. Generate today's daily chart
echo "📊 Generating daily chart with today's marker..."
python3 flex_gantt.py pipeline.xlsx --daily --dashboard

# 2. Generate current week's chart with today's marker
echo "📊 Generating weekly chart with today's marker..."
python3 flex_gantt.py pipeline.xlsx --weekly --dashboard

# 3. Generate rolling window (monthly charts) with today's red line
echo "📊 Generating monthly charts with today's red line..."
python3 flex_gantt.py pipeline.xlsx --rolling-window --dashboard

# 4. Generate calendar with today's blue dot
echo "📊 Generating calendar with today's blue dot..."
python3 flex_gantt.py pipeline.xlsx --calendar --dashboard

echo ""
echo "✅ All charts updated with current Today markers!"
echo ""
echo "📈 Generated charts:"
echo "   • Daily: Today's events"
echo "   • Weekly: Current week with today highlighted"
echo "   • Monthly: 3-month view with today's red line"
echo "   • Calendar: July 2025 with today's blue dot"
echo ""
echo "🚀 Pushing to GitHub..."

# Commit and push changes
git add slides/
git commit -m "🎯 Update Today markers - $(date +'%A, %B %d, %Y')"
git push origin main

echo ""
echo "✅ Updates pushed to GitHub!"
echo "🌐 Site will refresh within 5-10 minutes"
echo "💡 Use Ctrl+Shift+R to force browser refresh"