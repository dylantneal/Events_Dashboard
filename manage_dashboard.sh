#!/bin/bash
# manage_dashboard.sh
# Dashboard management script to prevent multiple instances and monitor API usage

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DASHBOARD_PID_FILE="$PROJECT_DIR/.dashboard.pid"
LOG_FILE="$PROJECT_DIR/logs/dashboard.log"

# Create logs directory if it doesn't exist
mkdir -p "$PROJECT_DIR/logs"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a "$LOG_FILE"
}

check_running_instances() {
    local instances=$(ps aux | grep -E "python.*http\.server.*[0-9]{4}" | grep -v grep | wc -l)
    echo $instances
}

kill_all_instances() {
    log "Stopping all dashboard instances..."
    pkill -f "python.*http.server" 2>/dev/null || true
    sleep 2
    
    # Force kill any remaining instances
    local remaining=$(check_running_instances)
    if [ $remaining -gt 0 ]; then
        warning "Force killing remaining instances..."
        ps aux | grep -E "python.*http\.server.*[0-9]{4}" | grep -v grep | awk '{print $2}' | xargs kill -9 2>/dev/null || true
    fi
    
    remaining=$(check_running_instances)
    if [ $remaining -eq 0 ]; then
        success "All dashboard instances stopped"
    else
        error "Failed to stop all instances. $remaining still running."
    fi
}

start_dashboard() {
    local port=${1:-8000}
    
    # Check if already running
    if [ -f "$DASHBOARD_PID_FILE" ]; then
        local pid=$(cat "$DASHBOARD_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            warning "Dashboard already running on PID $pid"
            return 1
        else
            rm -f "$DASHBOARD_PID_FILE"
        fi
    fi
    
    # Check for other instances
    local instances=$(check_running_instances)
    if [ $instances -gt 0 ]; then
        warning "Found $instances other dashboard instances running"
        read -p "Do you want to stop them and start fresh? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            kill_all_instances
        else
            error "Please stop other instances first"
            return 1
        fi
    fi
    
    # Start dashboard
    log "Starting dashboard on port $port..."
    cd "$PROJECT_DIR"
    python3 -m http.server $port > "$LOG_FILE" 2>&1 &
    local pid=$!
    echo $pid > "$DASHBOARD_PID_FILE"
    
    sleep 2
    if ps -p $pid > /dev/null 2>&1; then
        success "Dashboard started on http://localhost:$port (PID: $pid)"
        log "Dashboard URL: http://localhost:$port"
        return 0
    else
        error "Failed to start dashboard"
        rm -f "$DASHBOARD_PID_FILE"
        return 1
    fi
}

stop_dashboard() {
    if [ -f "$DASHBOARD_PID_FILE" ]; then
        local pid=$(cat "$DASHBOARD_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            log "Stopping dashboard (PID: $pid)..."
            kill $pid
            sleep 2
            if ! ps -p $pid > /dev/null 2>&1; then
                success "Dashboard stopped"
                rm -f "$DASHBOARD_PID_FILE"
            else
                warning "Force killing dashboard..."
                kill -9 $pid
                rm -f "$DASHBOARD_PID_FILE"
            fi
        else
            warning "Dashboard not running (PID file exists but process not found)"
            rm -f "$DASHBOARD_PID_FILE"
        fi
    else
        warning "No dashboard PID file found"
    fi
}

status() {
    echo "=== Dashboard Status ==="
    
    # Check PID file
    if [ -f "$DASHBOARD_PID_FILE" ]; then
        local pid=$(cat "$DASHBOARD_PID_FILE")
        if ps -p $pid > /dev/null 2>&1; then
            success "Dashboard running (PID: $pid)"
            local port=$(netstat -an 2>/dev/null | grep LISTEN | grep ":$pid" | head -1 | awk '{print $4}' | cut -d: -f2)
            if [ -n "$port" ]; then
                echo "  URL: http://localhost:$port"
            fi
        else
            warning "Dashboard PID file exists but process not running"
            rm -f "$DASHBOARD_PID_FILE"
        fi
    else
        echo "Dashboard not running (no PID file)"
    fi
    
    # Check for other instances
    local instances=$(check_running_instances)
    if [ $instances -gt 0 ]; then
        warning "Found $instances other dashboard instances running:"
        ps aux | grep -E "python.*http\.server.*[0-9]{4}" | grep -v grep | while read line; do
            echo "  $line"
        done
    fi
    
    # API usage warning
    echo ""
    echo "=== API Usage Warning ==="
    echo "Each dashboard instance makes API calls every 5 minutes to JSONBin.io"
    echo "Multiple instances can quickly exhaust the free tier (100k requests/month)"
    echo "Current instances: $instances"
    
    if [ $instances -gt 1 ]; then
        error "WARNING: Multiple instances detected! This will consume API requests quickly."
        echo "  Estimated daily API calls: $((instances * 288)) (with 5-minute intervals)"
        echo "  Monthly usage: $((instances * 288 * 30)) calls"
    fi
}

case "${1:-status}" in
    start)
        start_dashboard $2
        ;;
    stop)
        stop_dashboard
        ;;
    restart)
        stop_dashboard
        sleep 2
        start_dashboard $2
        ;;
    kill-all)
        kill_all_instances
        ;;
    status)
        status
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|kill-all|status} [port]"
        echo ""
        echo "Commands:"
        echo "  start [port]    Start dashboard (default port: 8000)"
        echo "  stop           Stop dashboard"
        echo "  restart [port] Restart dashboard"
        echo "  kill-all       Stop all dashboard instances"
        echo "  status         Show dashboard status and API usage"
        echo ""
        echo "Examples:"
        echo "  $0 start 8000"
        echo "  $0 status"
        echo "  $0 kill-all"
        ;;
esac 