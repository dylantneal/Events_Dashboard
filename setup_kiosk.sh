#!/bin/bash
# Encore Dashboard Kiosk Setup Script
# Run this on a Raspberry Pi with Raspberry Pi OS Lite

set -e

echo "🎯 Encore Dashboard Kiosk Setup"
echo "================================"

# Configuration
DASHBOARD_URL="${1:-https://yourusername.github.io/EncoreDashboard/}"
UPDATE_INTERVAL="${2:-5}"  # minutes

echo "📋 Configuration:"
echo "  Dashboard URL: $DASHBOARD_URL"
echo "  Update interval: $UPDATE_INTERVAL minutes"
echo ""

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi"
    echo "   It may work on other Linux systems but is not tested"
    echo ""
fi

# Update system
echo "🔄 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install required packages
echo "📦 Installing required packages..."
sudo apt install -y chromium-browser xdotool git curl

# Create dashboard directory
echo "📁 Setting up dashboard directory..."
mkdir -p ~/dashboard
cd ~/dashboard

# Clone the dashboard repository (if it's a git repo)
if [ -d ".git" ]; then
    echo "📥 Updating existing repository..."
    git pull origin main
else
    echo "📥 Cloning dashboard repository..."
    # Note: Replace with your actual repository URL
    git clone https://github.com/yourusername/EncoreDashboard.git .
fi

# Create autostart configuration
echo "🚀 Setting up autostart..."
mkdir -p ~/.config/autostart

cat > ~/.config/autostart/dashboard.desktop << EOF
[Desktop Entry]
Type=Application
Name=Encore Dashboard
Comment=Kiosk Dashboard Display
Exec=chromium-browser --kiosk --incognito --disable-pinch --overscroll-history-navigation=0 --disable-features=VizDisplayCompositor --disable-dev-shm-usage --no-sandbox --disable-setuid-sandbox $DASHBOARD_URL
Terminal=false
X-GNOME-Autostart-enabled=true
EOF

# Create update script
echo "📝 Creating update script..."
cat > ~/update_dashboard.sh << 'EOF'
#!/bin/bash
# Dashboard update script

LOG_FILE="$HOME/dashboard_update.log"
DASHBOARD_DIR="$HOME/dashboard"

echo "$(date): Starting dashboard update" >> "$LOG_FILE"

# Navigate to dashboard directory
cd "$DASHBOARD_DIR" || {
    echo "$(date): Failed to navigate to dashboard directory" >> "$LOG_FILE"
    exit 1
}

# Pull latest changes
if git pull --ff-only origin main >> "$LOG_FILE" 2>&1; then
    echo "$(date): Git pull successful" >> "$LOG_FILE"
    
    # Refresh browser if Chromium is running
    if pgrep chromium > /dev/null; then
        echo "$(date): Refreshing browser" >> "$LOG_FILE"
        xdotool search --onlyvisible --class chromium key F5 >> "$LOG_FILE" 2>&1 || true
    else
        echo "$(date): Chromium not running, skipping refresh" >> "$LOG_FILE"
    fi
else
    echo "$(date): Git pull failed" >> "$LOG_FILE"
fi

# Keep log file size manageable
if [ $(wc -l < "$LOG_FILE") -gt 1000 ]; then
    tail -500 "$LOG_FILE" > "${LOG_FILE}.tmp" && mv "${LOG_FILE}.tmp" "$LOG_FILE"
fi
EOF

chmod +x ~/update_dashboard.sh

# Set up cron job for updates
echo "⏰ Setting up automatic updates..."
CRON_JOB="*/$UPDATE_INTERVAL * * * * $HOME/update_dashboard.sh"

# Remove existing cron job if it exists
(crontab -l 2>/dev/null | grep -v "update_dashboard.sh") | crontab -

# Add new cron job
(crontab -l 2>/dev/null; echo "$CRON_JOB") | crontab -

# Create health check script
echo "🏥 Creating health check script..."
cat > ~/health_check.sh << 'EOF'
#!/bin/bash
# Health check script for dashboard

DASHBOARD_URL="$1"
SLACK_WEBHOOK="$2"

if [ -z "$DASHBOARD_URL" ]; then
    echo "Usage: $0 <dashboard_url> [slack_webhook_url]"
    exit 1
fi

# Check if dashboard is accessible
if curl -f -s "$DASHBOARD_URL" > /dev/null; then
    echo "$(date): Dashboard is healthy"
    exit 0
else
    echo "$(date): Dashboard is down!"
    
    # Send Slack notification if webhook is provided
    if [ -n "$SLACK_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"🚨 Dashboard is down! $(date)\"}" \
            "$SLACK_WEBHOOK" > /dev/null 2>&1
    fi
    
    exit 1
fi
EOF

chmod +x ~/health_check.sh

# Create systemd service for monitoring
echo "🔧 Creating systemd service..."
sudo tee /etc/systemd/system/dashboard-monitor.service > /dev/null << EOF
[Unit]
Description=Dashboard Health Monitor
After=network.target

[Service]
Type=oneshot
ExecStart=$HOME/health_check.sh $DASHBOARD_URL
User=$USER
EOF

# Create timer for health checks
sudo tee /etc/systemd/system/dashboard-monitor.timer > /dev/null << EOF
[Unit]
Description=Run dashboard health check every 5 minutes
Requires=dashboard-monitor.service

[Timer]
OnBootSec=1min
OnUnitActiveSec=5min
Unit=dashboard-monitor.service

[Install]
WantedBy=timers.target
EOF

# Enable and start the timer
sudo systemctl daemon-reload
sudo systemctl enable dashboard-monitor.timer
sudo systemctl start dashboard-monitor.timer

# Disable screen saver and power management
echo "💡 Configuring display settings..."
sudo tee /etc/xdg/lxsession/LXDE-pi/autostart > /dev/null << EOF
@xset s off
@xset -dpms
@xset s noblank
EOF

# Configure Chromium for kiosk mode
mkdir -p ~/.config/chromium/Default
cat > ~/.config/chromium/Default/Preferences << EOF
{
  "profile": {
    "default_content_setting_values": {
      "notifications": 2
    }
  },
  "session": {
    "restore_on_startup": 4
  },
  "browser": {
    "window_placement": {
      "maximized": true
    }
  }
}
EOF

# Create a simple status script
echo "📊 Creating status script..."
cat > ~/dashboard_status.sh << 'EOF'
#!/bin/bash
echo "🎯 Encore Dashboard Status"
echo "=========================="
echo ""

echo "📱 Browser Status:"
if pgrep chromium > /dev/null; then
    echo "  ✅ Chromium is running"
else
    echo "  ❌ Chromium is not running"
fi

echo ""
echo "🔄 Update Status:"
if crontab -l 2>/dev/null | grep -q "update_dashboard.sh"; then
    echo "  ✅ Auto-updates are configured"
    crontab -l | grep "update_dashboard.sh"
else
    echo "  ❌ Auto-updates not configured"
fi

echo ""
echo "🏥 Health Monitor:"
if systemctl is-active --quiet dashboard-monitor.timer; then
    echo "  ✅ Health monitoring is active"
else
    echo "  ❌ Health monitoring is not active"
fi

echo ""
echo "📁 Dashboard Directory:"
if [ -d "$HOME/dashboard" ]; then
    echo "  ✅ Dashboard directory exists"
    cd "$HOME/dashboard"
    if [ -d ".git" ]; then
        echo "  📋 Git status:"
        git status --porcelain | head -5
        echo "  🔗 Remote: $(git remote get-url origin 2>/dev/null || echo 'No remote')"
    fi
else
    echo "  ❌ Dashboard directory not found"
fi

echo ""
echo "📋 Recent Logs:"
if [ -f "$HOME/dashboard_update.log" ]; then
    echo "  Last 5 update log entries:"
    tail -5 "$HOME/dashboard_update.log" | sed 's/^/    /'
else
    echo "  No update logs found"
fi
EOF

chmod +x ~/dashboard_status.sh

# Final instructions
echo ""
echo "✅ Setup Complete!"
echo "=================="
echo ""
echo "🎯 Next Steps:"
echo "1. Reboot the Raspberry Pi:"
echo "   sudo reboot"
echo ""
echo "2. After reboot, the dashboard should start automatically"
echo ""
echo "3. Check status anytime with:"
echo "   ~/dashboard_status.sh"
echo ""
echo "4. Manual update:"
echo "   ~/update_dashboard.sh"
echo ""
echo "5. Health check:"
echo "   ~/health_check.sh $DASHBOARD_URL"
echo ""
echo "🔧 Configuration Files:"
echo "  Autostart: ~/.config/autostart/dashboard.desktop"
echo "  Update script: ~/update_dashboard.sh"
echo "  Cron jobs: crontab -l"
echo "  Health monitor: systemctl status dashboard-monitor.timer"
echo ""
echo "📝 Notes:"
echo "- The dashboard will update every $UPDATE_INTERVAL minutes"
echo "- Health checks run every 5 minutes"
echo "- Logs are saved to ~/dashboard_update.log"
echo "- To change the dashboard URL, edit ~/.config/autostart/dashboard.desktop"
echo ""
echo "🚀 Ready to deploy!" 