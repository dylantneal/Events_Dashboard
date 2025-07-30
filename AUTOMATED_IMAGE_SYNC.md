# Automated Image Synchronization Guide

This guide explains how the dashboard automatically synchronizes generated images across all screens using GitHub as the central storage.

## Overview

The Encore Dashboard now supports **automatic image synchronization** ensuring all screens display the latest generated charts:

- ✅ **Automatic Git commits** after each image generation
- ✅ **GitHub as central storage** - no additional services needed
- ✅ **Proper cleanup** of old images before pushing
- ✅ **All screens updated** within minutes of generation
- ✅ **Zero manual intervention** once configured

## How It Works

### Image Generation & Distribution Flow

```
1. Cron job triggers (midnight/Monday/1st of month)
           ↓
2. Python script generates new images
           ↓
3. Old images are cleaned up automatically
           ↓
4. New images saved to slides/ directory
           ↓
5. git_auto_commit.py automatically commits & pushes
           ↓
6. GitHub Pages rebuilds with new images
           ↓
7. All screens receive updates (auto-refresh)
```

### Timing Schedule

| Update Type | Schedule | Images Generated | Auto-Commit |
|------------|----------|------------------|-------------|
| Daily | Every midnight | Happening Today chart | ✓ Automatic |
| Weekly | Monday midnight | Happening This Week chart | ✓ Automatic |
| Monthly | 1st at 6 AM | 4-month rolling window + Calendar | ✓ Automatic |

## Initial Setup

### 1. Configure Git Authentication

For the auto-commit feature to work, your server needs push access to GitHub:

#### Option A: SSH Key (Recommended)
```bash
# Generate SSH key if you don't have one
ssh-keygen -t ed25519 -C "dashboard-automation@example.com"

# Add to ssh-agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/id_ed25519

# Copy public key
cat ~/.ssh/id_ed25519.pub
# Add this key to GitHub: Settings → SSH and GPG keys → New SSH key

# Test connection
ssh -T git@github.com

# Configure repository to use SSH
cd /path/to/EncoreDashboard
git remote set-url origin git@github.com:yourusername/EncoreDashboard.git
```

#### Option B: Personal Access Token
```bash
# Create token at: https://github.com/settings/tokens
# Select scopes: repo (all)

# Store credentials
git config --global credential.helper store
git config --global user.name "Dashboard Automation"
git config --global user.email "dashboard@example.com"

# Test by doing a manual push
git push origin main
# Enter username and token when prompted
```

### 2. Test Auto-Commit Script

```bash
# Make the script executable
chmod +x git_auto_commit.py

# Test standalone execution
python3 git_auto_commit.py --type daily

# Check if it worked
git log --oneline -1
```

### 3. Set Up Automated Updates

Use the enhanced setup script:
```bash
./setup_cron.sh
```

Or manually add to crontab:
```bash
crontab -e

# Add these lines:
# Daily updates (midnight)
0 0 * * * cd /path/to/EncoreDashboard && python3 daily_update.py >> logs/cron_daily.log 2>&1

# Weekly updates (Monday midnight)
0 0 * * 1 cd /path/to/EncoreDashboard && python3 weekly_update.py >> logs/cron_weekly.log 2>&1

# Monthly updates (1st at 6 AM)
0 6 1 * * cd /path/to/EncoreDashboard && python3 monthly_update.py >> logs/cron_monthly.log 2>&1
```

## Dashboard Auto-Refresh

The dashboard automatically refreshes to show new images:

### Default Behavior
- Auto-refresh every 5 minutes (configurable)
- GitHub Pages CDN ensures fast delivery
- No manual intervention needed

### Manual Refresh Options
- Press `R` on keyboard
- F5 or browser refresh
- Wait for auto-refresh cycle

### Kiosk Mode Enhancement
For dedicated displays, ensure auto-refresh is working:

```javascript
// In index.html or config.js
window.DASHBOARD_CONFIG = {
    autoReloadInterval: 300000  // 5 minutes (in milliseconds)
};
```

## Monitoring & Troubleshooting

### Check Automation Logs

```bash
# View recent automation activity
tail -f logs/daily_update_$(date +%Y%m%d).log
tail -f logs/weekly_update_$(date +%Y%m%d).log
tail -f logs/monthly_update_$(date +%Y%m%d).log

# Check for git commit success
grep "Auto-committing to GitHub" logs/*.log
grep "pushed to GitHub successfully" logs/*.log
```

### Common Issues & Solutions

#### 1. Git Push Authentication Failed
```bash
# Error: "fatal: Authentication failed"
# Solution: Set up SSH keys or personal access token (see setup above)

# Verify git remote URL
git remote -v

# Switch to SSH if using HTTPS
git remote set-url origin git@github.com:yourusername/EncoreDashboard.git
```

#### 2. Git Push Rejected (Out of Sync)
```bash
# Error: "rejected... non-fast-forward"
# Solution: Pull latest changes first

git pull origin main --rebase
git push origin main
```

#### 3. Images Not Updating on Screens
```bash
# Check if commits are reaching GitHub
git log --oneline -5

# Check GitHub Pages build status
# Go to: https://github.com/yourusername/EncoreDashboard/actions

# Force refresh on a screen
# Press Ctrl+Shift+R or Cmd+Shift+R
```

#### 4. Cron Jobs Not Running
```bash
# Check if cron is running
sudo service cron status

# Check cron logs
grep CRON /var/log/syslog | tail -20

# Test cron job manually
cd /path/to/EncoreDashboard && python3 daily_update.py
```

## Manual Testing

### Test Each Update Type

```bash
# Test daily update with auto-commit
python3 daily_update.py

# Test weekly update with auto-commit
python3 weekly_update.py

# Test monthly update with auto-commit
python3 monthly_update.py

# Check git log for auto-commits
git log --oneline -10 | grep "Auto-update"
```

### Force Image Regeneration

```bash
# Generate specific chart types manually
python3 flex_gantt.py pipeline.xlsx --daily --dashboard
python3 git_auto_commit.py --type daily

python3 flex_gantt.py pipeline.xlsx --weekly --dashboard
python3 git_auto_commit.py --type weekly

python3 flex_gantt.py pipeline.xlsx --rolling-window --dashboard
python3 flex_gantt.py pipeline.xlsx --calendar --dashboard
python3 git_auto_commit.py --type monthly
```

## Advanced Configuration

### Custom Commit Messages

Edit `git_auto_commit.py` to customize commit messages:

```python
update_types = {
    "monthly": "📅 Monthly dashboard update: 3-month window + calendar",
    "weekly": "📊 Weekly update: This week's events",
    "daily": "📍 Daily update: Today's schedule",
    "calendar": "📆 Calendar view refreshed"
}
```

### Adjust Auto-Refresh Timing

In `index.html`:
```javascript
// Change from 5 minutes to 2 minutes
setInterval(() => {
    location.reload();
}, 120000); // 2 minutes
```

### Email Notifications on Failure

Add email alerts to cron jobs:
```bash
# Install mail utilities
sudo apt-get install mailutils

# Add to crontab
0 0 * * * cd /path/to/EncoreDashboard && python3 daily_update.py || echo "Daily update failed" | mail -s "Dashboard Alert" admin@example.com
```

## Multi-Screen Deployment Best Practices

### 1. Central Server Setup
- Run all cron jobs on ONE server only
- This server needs git push access
- Other screens just display the dashboard

### 2. Screen Configuration
```bash
# On display screens (not the server)
# Just open the dashboard URL
chromium-browser --kiosk https://yourusername.github.io/EncoreDashboard/

# No cron jobs needed on display screens!
```

### 3. Network Considerations
- Ensure all screens have internet access
- GitHub Pages provides CDN for fast delivery
- Consider local caching for offline resilience

## Security Considerations

### Git Credentials
- Use SSH keys over passwords
- Limit token permissions to repository only
- Rotate credentials periodically

### Repository Settings
- Keep repository public for GitHub Pages
- Or use GitHub Pages with private repos (requires GitHub Pro)
- Consider branch protection rules

## Alternative Solution: Cloud Storage

If you prefer not to use GitHub as storage, here's an alternative using cloud storage:

### Using Cloudinary (Free Tier)

1. **Sign up** at cloudinary.com
2. **Install SDK**: `pip install cloudinary`
3. **Configure** in flex_gantt.py:

```python
import cloudinary
import cloudinary.uploader

cloudinary.config(
    cloud_name = "your_cloud_name",
    api_key = "your_api_key",
    api_secret = "your_api_secret"
)

# After saving image locally
def upload_to_cloudinary(local_path, public_id):
    result = cloudinary.uploader.upload(
        local_path,
        public_id=public_id,
        overwrite=True,
        resource_type="image"
    )
    return result['secure_url']
```

4. **Update dashboard** to load from Cloudinary URLs

This approach works but adds complexity compared to the GitHub solution.

## Summary

The automated image sync system ensures:
- ✅ All screens show the same, latest charts
- ✅ No manual intervention needed
- ✅ Proper cleanup of old images
- ✅ Reliable git-based distribution
- ✅ Works with your existing GitHub Pages setup

Once configured, the system runs completely automatically, generating and distributing images according to your schedule. 