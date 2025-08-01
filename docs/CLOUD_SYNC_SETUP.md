# Cloud Sync Setup Guide

This guide will help you set up cloud synchronization for your dashboard so that:
- **Gantt charts and calendars** automatically update across all devices
- **Announcements** sync in real-time between all computers
- **Everything works without manual intervention**

## Current Issues and Solutions

### Issue 1: Gantt Charts and Calendars Not Updating Automatically

**Problem**: Your cron jobs are running and generating charts, but they're not reaching other computers because of git sync failures.

**Solution**: 
1. ✅ **Fixed**: Improved git auto-commit script with better conflict handling
2. ✅ **Fixed**: Cleaned up duplicate cron jobs
3. ⚠️ **Action Required**: Set up proper cron jobs (see below)

### Issue 2: Announcements Not Syncing Between Computers

**Problem**: Announcements are stored locally on each device (localStorage).

**Solution**: Enable cloud sync via JSONBin.io (free service).

## Step 1: Clean Up and Restart Cron Jobs

```bash
# Navigate to your project directory
cd "/Users/dylanneal/Documents/Documents - Dylan's MacBook Air/Professional/Technology/WebDev/EncoreDashboard"

# Set up clean cron jobs
./setup_cron.sh
```

Choose option **6** (All three updates) for complete automation.

## Step 2: Set Up Cloud Sync for Announcements

### Option A: Quick Setup (Public Collaborative Board)
Your `config.js` is already configured with a public JSONBin that allows collaborative announcements:

```javascript
cloudSync: {
    enabled: true,
    url: 'https://api.jsonbin.io/v3/b/676b9e9aad19ca34f8db9b12/latest',
    syncInterval: 30000 // 30 seconds
}
```

**This works immediately** - all devices will share announcements!

### Option B: Private Setup (Your Own JSONBin)

1. **Create JSONBin Account**:
   - Go to https://jsonbin.io
   - Sign up for free account
   - Get 100,000 API calls/month free

2. **Create Your Bin**:
   - Click "Create Bin"
   - Name it "Dashboard Announcements"
   - Set content to: `{"announcements": []}`
   - Make it **Public** (or Private with API key)

3. **Update config.js**:
   ```javascript
   cloudSync: {
       enabled: true,
       url: 'https://api.jsonbin.io/v3/b/YOUR_BIN_ID/latest',
       key: 'YOUR_API_KEY', // Only needed for private bins
       syncInterval: 30000
   }
   ```

4. **Test the Setup**:
   ```bash
   # Open your dashboard
   python3 -m http.server 8000
   
   # In browser: http://localhost:8000
   # Create a test announcement
   # Check if it appears on other devices
   ```

## Step 3: Verify Everything Works

### Test Automatic Updates:
```bash
# Manual test of each update type
python3 daily_update.py
python3 weekly_update.py  
python3 monthly_update.py

# Check if changes reach GitHub
git log --oneline -5
```

### Test Announcement Sync:
1. Open dashboard on Computer A
2. Create an announcement
3. Open dashboard on Computer B
4. Announcement should appear within 30 seconds

### Check Cron Jobs:
```bash
# View active cron jobs
crontab -l

# Check recent logs
ls -la logs/
tail -f logs/daily_update_$(date +%Y%m%d).log
```

## Step 4: Deploy to All Devices

### For Each Computer/Device:

1. **Clone or Pull Latest**:
   ```bash
   git clone https://github.com/yourusername/EncoreDashboard.git
   # OR
   git pull origin main
   ```

2. **Copy Configuration**:
   ```bash
   # Make sure config.js exists with your settings
   cp config.example.js config.js
   # Edit config.js with your specific settings
   ```

3. **Set Up Kiosk Mode** (for dedicated displays):
   ```bash
   # Create autostart script
   ./setup_kiosk.sh
   ```

4. **Test Dashboard**:
   ```bash
   python3 -m http.server 8000
   # Open http://localhost:8000
   ```

## Step 5: Monitoring and Maintenance

### Daily Monitoring:
```bash
# Check if updates are working
ls -la slides/
cat logs/daily_update_$(date +%Y%m%d).log | tail -20
```

### Weekly Maintenance:
```bash
# Clean up old logs
find logs/ -name "*.log" -mtime +30 -delete

# Verify git sync is working
git log --oneline --since="1 week ago"
```

### Troubleshooting Commands:
```bash
# Test git sync manually
python3 git_auto_commit.py --type daily

# Force update all charts
python3 force_update_all.py

# Check cron job status
systemctl status cron  # Linux
# OR check system logs on macOS
```

## Expected Behavior After Setup

### Automatic Updates:
- **Daily**: New "Happening Today" chart every midnight
- **Weekly**: New "Happening This Week" chart every Monday
- **Monthly**: New 3-month rolling window + calendar on 1st of month
- **Git Sync**: All changes pushed to GitHub automatically
- **Device Sync**: All devices pull updates within 5 minutes

### Announcement Sync:
- **Real-time**: Announcements appear on all devices within 30 seconds
- **Persistent**: Announcements survive browser restarts
- **Collaborative**: Anyone can add/edit announcements
- **Automatic cleanup**: Expired announcements auto-removed

## Troubleshooting Common Issues

### Git Sync Failures:
```bash
# Check git status
git status
git pull origin main

# Reset if needed
git reset --hard origin/main
```

### Cron Jobs Not Running:
```bash
# Check cron service (Linux)
systemctl status cron

# Check cron logs (macOS)
log show --predicate 'eventMessage contains "cron"' --last 1h
```

### Announcement Sync Issues:
1. Check browser console (F12) for errors
2. Verify `config.js` has correct `cloudSync` settings
3. Test JSONBin URL directly in browser
4. Check network connectivity

### Chart Generation Failures:
```bash
# Test manual generation
python3 flex_gantt.py pipeline.xlsx --daily --dashboard

# Check dependencies
pip3 install -r requirements.txt
```

## Success Indicators

✅ **Working System**:
- Cron jobs run without errors
- New chart files appear in `slides/` directory
- Git commits happen automatically
- All devices show the same content
- Announcements sync between devices
- Logs show successful operations

❌ **Problem Indicators**:
- Empty `slides/` directory
- Git push failures in logs
- Announcements only on one device
- Cron job errors
- Old chart files not updating

## Support

If you encounter issues:
1. Check the logs in `logs/` directory
2. Run manual tests with the commands above
3. Verify your `config.js` settings
4. Ensure all dependencies are installed
5. Check GitHub repository for latest changes

The system is designed to be **completely autonomous** once properly configured. You should never need to manually update charts or sync announcements again! 