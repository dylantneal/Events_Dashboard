#!/bin/bash
# Automation Performance Tracker - Monitor and track automation performance over time

# Configuration
PERFORMANCE_LOG="logs/performance.log"
BASELINE_FILE="logs/performance_baseline.json"
REPORT_FILE="logs/performance_report.html"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

# Ensure logs directory exists
mkdir -p logs

# Function to log performance data
log_performance() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local utc_timestamp=$(TZ=UTC date '+%Y-%m-%d %H:%M:%S')
    
    # Get last automation info
    local last_commit=$(git log -1 --grep="Auto-update\|🎯\|🤖" --pretty=format:"%H|%ct|%s" 2>/dev/null)
    if [ -n "$last_commit" ]; then
        IFS='|' read -r commit_hash commit_time commit_msg <<< "$last_commit"
        local commit_date=$(date -d "@$commit_time" '+%Y-%m-%d %H:%M:%S' 2>/dev/null || date -r "$commit_time" '+%Y-%m-%d %H:%M:%S')
        local hours_since=$(( ($(date +%s) - commit_time) / 3600 ))
    else
        commit_hash="none"
        commit_time="0"
        commit_msg="No automation found"
        commit_date="N/A"
        hours_since="999"
    fi
    
    # Check file generation
    local today=$(date +%Y_%m_%d)
    local daily_chart_exists=$([ -f "slides/gantt_daily_${today}.png" ] && echo "true" || echo "false")
    
    if [ "$daily_chart_exists" = "true" ]; then
        local daily_chart_time=$(stat -c %Y "slides/gantt_daily_${today}.png" 2>/dev/null || stat -f "%m" "slides/gantt_daily_${today}.png")
        local daily_chart_age=$(( ($(date +%s) - daily_chart_time) / 3600 ))
    else
        daily_chart_time="0"
        daily_chart_age="999"
    fi
    
    # Calculate reliability metrics
    local automation_healthy=$([ $hours_since -lt 24 ] && echo "true" || echo "false")
    local files_current=$([ $daily_chart_age -lt 24 ] && echo "true" || echo "false")
    
    # Determine automation type
    local automation_type="unknown"
    if echo "$commit_msg" | grep -q "🎯"; then
        automation_type="enhanced_daily"
    elif echo "$commit_msg" | grep -q "Weekly"; then
        automation_type="weekly"
    elif echo "$commit_msg" | grep -q "Monthly"; then
        automation_type="monthly"
    elif echo "$commit_msg" | grep -q "Daily"; then
        automation_type="daily"
    fi
    
    # Calculate timing metrics (how close to scheduled time)
    local scheduled_deviation="unknown"
    if [ "$commit_time" != "0" ]; then
        local commit_hour=$(date -d "@$commit_time" '+%H' 2>/dev/null || date -r "$commit_time" '+%H')
        local commit_minute=$(date -d "@$commit_time" '+%M' 2>/dev/null || date -r "$commit_time" '+%M')
        
        # Expected times: 3:15 UTC for daily, 3:30 for weekly, 3:45 for monthly
        case $automation_type in
            "enhanced_daily"|"daily")
                local expected_minutes=$((3 * 60 + 15))  # 3:15 AM
                ;;
            "weekly")
                local expected_minutes=$((3 * 60 + 30))  # 3:30 AM
                ;;
            "monthly")
                local expected_minutes=$((3 * 60 + 45))  # 3:45 AM
                ;;
            *)
                local expected_minutes=$((3 * 60 + 15))  # Default to daily
                ;;
        esac
        
        local actual_minutes=$((commit_hour * 60 + commit_minute))
        scheduled_deviation=$((actual_minutes - expected_minutes))
        
        # Handle day boundary crossover
        if [ $scheduled_deviation -gt 720 ]; then  # More than 12 hours
            scheduled_deviation=$((scheduled_deviation - 1440))  # Subtract 24 hours
        elif [ $scheduled_deviation -lt -720 ]; then  # Less than -12 hours
            scheduled_deviation=$((scheduled_deviation + 1440))  # Add 24 hours
        fi
    fi
    
    # Log entry
    echo "$timestamp|$utc_timestamp|$commit_hash|$commit_time|$commit_date|$commit_msg|$hours_since|$automation_type|$daily_chart_exists|$daily_chart_age|$automation_healthy|$files_current|$scheduled_deviation" >> "$PERFORMANCE_LOG"
}

# Function to analyze performance trends
analyze_performance() {
    if [ ! -f "$PERFORMANCE_LOG" ]; then
        echo -e "${YELLOW}⚠️  No performance data available yet${NC}"
        return 1
    fi
    
    echo -e "${BOLD}${CYAN}📊 Performance Analysis${NC}"
    echo "═══════════════════════════════════════"
    
    # Count total entries
    local total_entries=$(wc -l < "$PERFORMANCE_LOG")
    echo "   📈 Total performance records: $total_entries"
    
    # Analyze last 7 days
    local seven_days_ago=$(date -d "7 days ago" '+%Y-%m-%d' 2>/dev/null || date -v-7d '+%Y-%m-%d')
    local recent_entries=$(awk -F'|' -v cutoff="$seven_days_ago" '$1 >= cutoff' "$PERFORMANCE_LOG" | wc -l)
    echo "   📅 Records from last 7 days: $recent_entries"
    
    if [ $recent_entries -eq 0 ]; then
        echo -e "   ${YELLOW}⚠️  No recent data for analysis${NC}"
        return 1
    fi
    
    # Calculate success rates
    echo ""
    echo -e "${BLUE}🎯 Reliability Metrics (Last 7 Days):${NC}"
    
    local healthy_count=$(awk -F'|' -v cutoff="$seven_days_ago" '$1 >= cutoff && $11 == "true"' "$PERFORMANCE_LOG" | wc -l)
    local healthy_rate=$(( (healthy_count * 100) / recent_entries ))
    echo "   ✅ Automation health rate: $healthy_rate% ($healthy_count/$recent_entries)"
    
    local current_files_count=$(awk -F'|' -v cutoff="$seven_days_ago" '$1 >= cutoff && $12 == "true"' "$PERFORMANCE_LOG" | wc -l)
    local current_files_rate=$(( (current_files_count * 100) / recent_entries ))
    echo "   📊 Current files rate: $current_files_rate% ($current_files_count/$recent_entries)"
    
    # Analyze timing deviations
    echo ""
    echo -e "${BLUE}⏰ Timing Analysis:${NC}"
    
    # Get timing deviations (exclude unknown values)
    local deviations=$(awk -F'|' -v cutoff="$seven_days_ago" '$1 >= cutoff && $13 != "unknown" {print $13}' "$PERFORMANCE_LOG")
    
    if [ -n "$deviations" ]; then
        local avg_deviation=$(echo "$deviations" | awk '{sum+=$1} END {print int(sum/NR)}')
        local max_deviation=$(echo "$deviations" | sort -n | tail -1)
        local min_deviation=$(echo "$deviations" | sort -n | head -1)
        
        echo "   📊 Average delay: $avg_deviation minutes from scheduled time"
        echo "   📊 Maximum delay: $max_deviation minutes"
        echo "   📊 Minimum delay: $min_deviation minutes"
        
        # Phase 2 improvement assessment
        if [ $avg_deviation -lt 60 ]; then
            echo -e "   ${GREEN}✅ Excellent timing - Phase 2 optimization working well${NC}"
        elif [ $avg_deviation -lt 120 ]; then
            echo -e "   ${YELLOW}⚠️  Good timing - some delays expected${NC}"
        else
            echo -e "   ${RED}❌ Poor timing - may need further optimization${NC}"
        fi
    else
        echo "   ⚠️  No timing data available"
    fi
    
    # Automation type breakdown
    echo ""
    echo -e "${BLUE}📋 Automation Type Breakdown:${NC}"
    
    awk -F'|' -v cutoff="$seven_days_ago" '$1 >= cutoff {print $8}' "$PERFORMANCE_LOG" | sort | uniq -c | while read count type; do
        echo "   📊 $type: $count occurrences"
    done
}

# Function to generate HTML performance report
generate_html_report() {
    if [ ! -f "$PERFORMANCE_LOG" ]; then
        echo -e "${YELLOW}⚠️  No performance data for report generation${NC}"
        return 1
    fi
    
    echo -e "${BLUE}📄 Generating HTML performance report...${NC}"
    
    cat > "$REPORT_FILE" << 'EOF'
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Dashboard Automation Performance Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 16px;
            padding: 30px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.1);
        }
        .header {
            text-align: center;
            margin-bottom: 40px;
            padding-bottom: 20px;
            border-bottom: 2px solid #f0f0f0;
        }
        .header h1 {
            color: #333;
            margin: 0;
            font-size: 2.5em;
        }
        .header .subtitle {
            color: #666;
            margin-top: 10px;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }
        .metric-card {
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
            padding: 20px;
            border-radius: 12px;
            text-align: center;
        }
        .metric-value {
            font-size: 2em;
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        .metric-label {
            color: #666;
            font-size: 0.9em;
        }
        .chart-container {
            margin: 40px 0;
            background: #f9f9f9;
            padding: 20px;
            border-radius: 12px;
        }
        .chart-container h3 {
            text-align: center;
            color: #333;
            margin-bottom: 20px;
        }
        .chart-wrapper {
            position: relative;
            height: 400px;
        }
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
        }
        .status-good { background: #4ade80; }
        .status-warning { background: #fbbf24; }
        .status-error { background: #f87171; }
        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 20px;
            border-top: 2px solid #f0f0f0;
            color: #666;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 Dashboard Automation Performance Report</h1>
            <div class="subtitle">
                Generated on <span id="reportDate"></span><br>
                Post Phase-2 Optimization Analysis
            </div>
        </div>

        <div class="metrics-grid" id="metricsGrid">
            <!-- Metrics will be populated by JavaScript -->
        </div>

        <div class="chart-container">
            <h3>📈 Automation Success Rate Over Time</h3>
            <div class="chart-wrapper">
                <canvas id="successChart"></canvas>
            </div>
        </div>

        <div class="chart-container">
            <h3>⏰ Timing Deviation from Schedule</h3>
            <div class="chart-wrapper">
                <canvas id="timingChart"></canvas>
            </div>
        </div>

        <div class="chart-container">
            <h3>📊 Automation Type Distribution</h3>
            <div class="chart-wrapper">
                <canvas id="typeChart"></canvas>
            </div>
        </div>

        <div class="footer">
            <p>📊 Performance data tracked since Phase 3 implementation</p>
            <p>🔄 Report auto-generated by Automation Performance Tracker</p>
        </div>
    </div>

    <script>
        // Set report generation date
        document.getElementById('reportDate').textContent = new Date().toLocaleString();

        // Performance data (will be populated by shell script)
        const performanceData = PERFORMANCE_DATA_PLACEHOLDER;

        // Calculate metrics
        function calculateMetrics(data) {
            const recent = data.filter(entry => {
                const entryDate = new Date(entry.timestamp);
                const weekAgo = new Date();
                weekAgo.setDate(weekAgo.getDate() - 7);
                return entryDate >= weekAgo;
            });

            const healthyCount = recent.filter(entry => entry.automation_healthy === 'true').length;
            const currentFilesCount = recent.filter(entry => entry.files_current === 'true').length;
            const avgTiming = recent
                .filter(entry => entry.scheduled_deviation !== 'unknown')
                .reduce((sum, entry) => sum + parseInt(entry.scheduled_deviation), 0) / recent.length || 0;

            return {
                totalRecords: data.length,
                recentRecords: recent.length,
                healthRate: recent.length > 0 ? Math.round((healthyCount / recent.length) * 100) : 0,
                filesRate: recent.length > 0 ? Math.round((currentFilesCount / recent.length) * 100) : 0,
                avgDelay: Math.round(avgTiming)
            };
        }

        // Populate metrics
        function populateMetrics(metrics) {
            const grid = document.getElementById('metricsGrid');
            grid.innerHTML = `
                <div class="metric-card">
                    <div class="metric-value">${metrics.healthRate}%</div>
                    <div class="metric-label">
                        <span class="status-indicator ${metrics.healthRate >= 90 ? 'status-good' : metrics.healthRate >= 70 ? 'status-warning' : 'status-error'}"></span>
                        Automation Health Rate
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${metrics.filesRate}%</div>
                    <div class="metric-label">
                        <span class="status-indicator ${metrics.filesRate >= 90 ? 'status-good' : metrics.filesRate >= 70 ? 'status-warning' : 'status-error'}"></span>
                        File Currency Rate
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${metrics.avgDelay}m</div>
                    <div class="metric-label">
                        <span class="status-indicator ${Math.abs(metrics.avgDelay) <= 30 ? 'status-good' : Math.abs(metrics.avgDelay) <= 90 ? 'status-warning' : 'status-error'}"></span>
                        Average Schedule Delay
                    </div>
                </div>
                <div class="metric-card">
                    <div class="metric-value">${metrics.recentRecords}</div>
                    <div class="metric-label">
                        <span class="status-indicator status-good"></span>
                        Records (Last 7 Days)
                    </div>
                </div>
            `;
        }

        // Initialize charts and populate data
        if (performanceData && performanceData.length > 0) {
            const metrics = calculateMetrics(performanceData);
            populateMetrics(metrics);
            
            // Note: Chart implementation would go here
            // For brevity, showing placeholder
            console.log('Performance data loaded:', performanceData.length, 'records');
        } else {
            document.getElementById('metricsGrid').innerHTML = '<div class="metric-card"><div class="metric-value">No Data</div><div class="metric-label">Performance tracking starting...</div></div>';
        }
    </script>
</body>
</html>
EOF

    # Process performance data and inject into HTML
    if [ -f "$PERFORMANCE_LOG" ]; then
        # Convert log to JSON format
        local json_data="["
        local first=true
        
        while IFS='|' read -r timestamp utc_timestamp commit_hash commit_time commit_date commit_msg hours_since automation_type daily_chart_exists daily_chart_age automation_healthy files_current scheduled_deviation; do
            if [ "$first" = true ]; then
                first=false
            else
                json_data="$json_data,"
            fi
            
            json_data="$json_data{\"timestamp\":\"$timestamp\",\"utc_timestamp\":\"$utc_timestamp\",\"commit_hash\":\"$commit_hash\",\"commit_time\":\"$commit_time\",\"commit_date\":\"$commit_date\",\"commit_msg\":\"$commit_msg\",\"hours_since\":\"$hours_since\",\"automation_type\":\"$automation_type\",\"daily_chart_exists\":\"$daily_chart_exists\",\"daily_chart_age\":\"$daily_chart_age\",\"automation_healthy\":\"$automation_healthy\",\"files_current\":\"$files_current\",\"scheduled_deviation\":\"$scheduled_deviation\"}"
        done < "$PERFORMANCE_LOG"
        
        json_data="$json_data]"
        
        # Inject data into HTML
        sed -i.bak "s/PERFORMANCE_DATA_PLACEHOLDER/$json_data/g" "$REPORT_FILE"
        rm -f "${REPORT_FILE}.bak"
    fi
    
    echo -e "${GREEN}✅ HTML report generated: $REPORT_FILE${NC}"
}

# Function to establish baseline metrics
establish_baseline() {
    echo -e "${CYAN}📊 Establishing performance baseline...${NC}"
    
    # Record current state as baseline
    log_performance
    
    # Create baseline metrics file
    cat > "$BASELINE_FILE" << EOF
{
    "baseline_date": "$(date '+%Y-%m-%d %H:%M:%S')",
    "phase": "post-phase-2-optimization",
    "expected_schedule": {
        "daily": "03:15 UTC",
        "weekly": "03:30 UTC", 
        "monthly": "03:45 UTC"
    },
    "target_metrics": {
        "health_rate_target": 95,
        "timing_deviation_target": 30,
        "file_currency_target": 95
    },
    "monitoring_enabled": true
}
EOF
    
    echo -e "${GREEN}✅ Baseline established${NC}"
    echo "   📁 Baseline file: $BASELINE_FILE"
    echo "   📊 Performance log: $PERFORMANCE_LOG"
}

# Main script logic
case "${1:-log}" in
    "log")
        echo -e "${BLUE}📊 Logging performance data...${NC}"
        log_performance
        echo -e "${GREEN}✅ Performance data logged${NC}"
        ;;
    "analyze")
        analyze_performance
        ;;
    "report")
        generate_html_report
        ;;
    "baseline")
        establish_baseline
        ;;
    "monitor")
        echo -e "${CYAN}🔍 Starting continuous performance monitoring...${NC}"
        echo "   Logging performance every hour"
        echo "   Press Ctrl+C to stop"
        
        while true; do
            log_performance
            echo "   $(date): Performance logged"
            sleep 3600  # 1 hour
        done
        ;;
    "status")
        echo -e "${BOLD}${CYAN}📊 Performance Tracker Status${NC}"
        echo "═══════════════════════════════════════════"
        
        if [ -f "$PERFORMANCE_LOG" ]; then
            local entries=$(wc -l < "$PERFORMANCE_LOG")
            local latest=$(tail -1 "$PERFORMANCE_LOG" | cut -d'|' -f1)
            echo "   📈 Total records: $entries"
            echo "   📅 Latest record: $latest"
        else
            echo "   📊 No performance data yet"
        fi
        
        if [ -f "$BASELINE_FILE" ]; then
            local baseline_date=$(grep baseline_date "$BASELINE_FILE" | cut -d'"' -f4)
            echo "   📊 Baseline established: $baseline_date"
        else
            echo "   ⚠️  No baseline established"
        fi
        
        echo "   📁 Performance log: $PERFORMANCE_LOG"
        echo "   📄 HTML report: $REPORT_FILE"
        ;;
    "help"|*)
        echo "📊 Automation Performance Tracker"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  log       - Log current performance data (default)"
        echo "  analyze   - Analyze performance trends"
        echo "  report    - Generate HTML performance report"  
        echo "  baseline  - Establish performance baseline"
        echo "  monitor   - Start continuous monitoring"
        echo "  status    - Show tracker status"
        echo "  help      - Show this help"
        echo ""
        echo "Files:"
        echo "  $PERFORMANCE_LOG - Performance data log"
        echo "  $BASELINE_FILE - Baseline metrics"
        echo "  $REPORT_FILE - HTML report"
        ;;
esac

exit 0