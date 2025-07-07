#!/bin/bash
# Quick Fix Script for Dashboard Issues
# Run this to immediately update all charts to current date

echo "🔧 Quick Fix: Updating Dashboard to July 7, 2025"
echo "=================================================="

# Create logs directory if it doesn't exist
mkdir -p logs

# Update all chart types for current date
echo "📊 Generating today's chart (July 7, 2025)..."
python3 flex_gantt.py pipeline.xlsx --daily --dashboard

echo "📅 Generating this week's chart (July 7-13, 2025)..."
python3 flex_gantt.py pipeline.xlsx --weekly --dashboard

echo "🗓️ Generating monthly rolling window..."
python3 flex_gantt.py pipeline.xlsx --rolling-window --dashboard

echo "📋 Generating calendar view..."
python3 flex_gantt.py pipeline.xlsx --calendar --dashboard

echo ""
echo "✅ Charts updated! Check slides/ directory:"
ls -la slides/

echo ""
echo "📄 Updated manifest:"
cat slides/slides.json

echo ""
echo "🔧 Next steps:"
echo "1. Set up config.js for announcement sync"
echo "2. Configure cron jobs for automation"
echo "3. Test on your browser"

echo ""
echo "Quick commands:"
echo "- Copy config: cp config.example.js config.js"
echo "- Setup automation: ./setup_cron.sh"
echo "- View dashboard: open index.html" 