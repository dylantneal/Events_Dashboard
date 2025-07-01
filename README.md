# Encore Dashboard

A three-layer kiosk dashboard system for displaying Gantt charts with automatic updates, weather information, and real-time clock display.

## Architecture Overview

This system is designed as three cooperating layers:

### 1. Content Generation Layer
- **Python script** (`flex_gantt.py`) that exports Gantt charts and professional calendar views from Excel data
- **Image optimization** using Pillow to create 8-bit indexed color PNGs under 300KB
- **Manifest generation** (`slides.json`) that provides an authoritative playlist
- **Git integration** for versioned content management

### 2. Publication Layer
- **GitHub Pages** for static hosting with automatic HTTPS
- **CI/CD pipeline** that rebuilds on every push
- **Zero runtime costs** and automatic TLS certificate management
- **Atomic updates** via manifest-based content delivery

### 3. Presentation Layer
- **Single HTML file** with embedded CSS and JavaScript
- **Full-screen kiosk mode** with automatic slide rotation
- **Weather integration** via Open-Meteo API with local caching
- **Real-time clock** and responsive design
- **Auto-reload** for kiosk environments

## Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up API key (for accurate weather):**
   ```bash
   # Copy the config template
   cp config.example.js config.js
   
   # Edit config.js and replace YOUR_API_KEY_HERE with your actual OpenWeatherMap API key
   # Get a free API key at: https://openweathermap.org/api
   ```

3. **Generate slides:**
   
   **Option A: Rolling 3-month window (recommended for monthly automation):**
   ```bash
   python3 flex_gantt.py pipeline.xlsx --rolling-window --dashboard
   ```
   
   **Option B: Weekly "Happening This Week" chart:**
   ```bash
   python3 flex_gantt.py pipeline.xlsx --weekly --dashboard
   ```
   
   **Option C: Daily "Happening Today" chart:**
   ```bash
   python3 flex_gantt.py pipeline.xlsx --daily --dashboard
   ```
   
   **Option D: Professional calendar view for current month:**
   ```bash
   python3 flex_gantt.py pipeline.xlsx --calendar --dashboard
   ```
   
   **Option E: Specific months (traditional method):**
   ```bash
   python3 flex_gantt.py pipeline.xlsx --months 7 8 9 10 11 12 --year 2025 --dashboard
   ```

4. **Set up automated updates (optional):**
   ```bash
   ./setup_cron.sh
   ```
   This will test your setup and let you choose between:
   - Monthly updates (3-month rolling window)
   - Weekly updates ("Happening This Week" chart)
   - Daily updates ("Happening Today" chart)
   - Various combinations (recommended for complete automation)

5. **View dashboard:**
   ```bash
   # Using Python's built-in server
   python3 -m http.server 8000
   # Then open http://localhost:8000
   ```

## Dashboard Automation System

The dashboard now supports three types of automated updates with **automatic GitHub synchronization** for multi-screen deployments:

### 🔄 Automatic Image Synchronization (NEW!)

All generated images are automatically committed and pushed to GitHub, ensuring:
- **All screens show the same charts** - no manual deployment needed
- **Updates within minutes** - GitHub Pages rebuilds automatically
- **Zero manual intervention** - completely automated workflow
- **Proper cleanup** - old images removed before pushing

See `AUTOMATED_IMAGE_SYNC.md` for detailed setup instructions.

### 🗓️ Rolling 3-Month Window (Monthly Updates)

Always shows the next 3 months of events, automatically rotating as time progresses.

**How It Works:**
- **Automatic calculation**: Generates charts for the next 3 months from current date
- **Monthly rotation**: When July arrives, removes June's chart and adds October's chart  
- **Smart cleanup**: Automatically removes old chart files that are no longer needed
- **Example timeline**:
  - June 2025 → Shows: July, August, September
  - July 2025 → Shows: August, September, October (removes July)

**Manual Usage:**
```bash
python3 flex_gantt.py pipeline.xlsx --rolling-window --dashboard
python3 monthly_update.py
```

### 📅 "Happening This Week" (Weekly Updates)

Shows events occurring in the current week (Monday to Sunday), updated every Monday.

**How It Works:**
- **Current week focus**: Shows Monday through Sunday of the current week
- **Weekly refresh**: Updates every Monday at midnight with new week's events  
- **Smart cleanup**: Removes previous week's chart when generating new one
- **Better granularity**: Daily view instead of weekly intervals for precise timing

**Manual Usage:**
```bash
python3 flex_gantt.py pipeline.xlsx --weekly --dashboard
python3 weekly_update.py
```

### ⏰ "Happening Today" (Daily Updates)

Shows events occurring today (midnight to 11:59 PM) with hourly granularity, updated at midnight.

**How It Works:**
- **Today's focus**: Shows midnight through 11:59 PM of the current day
- **Daily refresh**: Updates every midnight with new day's events  
- **Smart cleanup**: Removes previous day's chart when generating new one
- **Hourly precision**: Shows time in 4-hour intervals with hour minor ticks for precise scheduling

**Manual Usage:**
```bash
python3 flex_gantt.py pipeline.xlsx --daily --dashboard
python3 daily_update.py
```

### 📅 Professional Calendar View (Monthly Updates)

Shows events in a traditional calendar format with professional styling, color-coded by owner, updated monthly.

**How It Works:**
- **Calendar layout**: Traditional month view with proper week/day grid
- **Event placement**: Events appear on correct dates with owner color coding
- **Multi-day events**: Span across multiple calendar days with visual continuity
- **Professional styling**: Modern typography, glassmorphism effects, and clean layout
- **Monthly refresh**: Updates on the 1st of each month at midnight

**Manual Usage:**
```bash
python3 flex_gantt.py pipeline.xlsx --calendar --dashboard
python3 calendar_update.py
```

### 🚀 Automated Setup

**Easy setup with interactive script:**
```bash
./setup_cron.sh
```

Choose from:
1. **Monthly only**: 3-month rolling window + calendar updates
2. **Weekly only**: "Happening This Week" updates
3. **Daily only**: "Happening Today" updates
4. **Calendar only**: Professional calendar view updates
5. **Monthly + Weekly**: General planning automation
6. **Weekly + Daily**: Immediate awareness automation
7. **All three**: Complete automation (recommended)

**Manual cron setup:**
```bash
crontab -e

# Monthly updates (1st of each month at 6 AM - includes calendar):
0 6 1 * * cd /path/to/EncoreDashboard && python3 monthly_update.py

# Calendar-only updates (1st of each month at midnight):
0 0 1 * * cd /path/to/EncoreDashboard && python3 calendar_update.py

# Weekly updates (every Monday at midnight):
0 0 * * 1 cd /path/to/EncoreDashboard && python3 weekly_update.py

# Daily updates (every day at midnight):
0 0 * * * cd /path/to/EncoreDashboard && python3 daily_update.py
```

### 📊 Log Monitoring

All automation scripts create detailed logs:
```bash
# View logs
ls -la logs/
cat logs/monthly_update_YYYYMMDD.log
cat logs/weekly_update_YYYYMMDD.log
cat logs/daily_update_YYYYMMDD.log

# Monitor real-time
tail -f logs/daily_update_$(date +%Y%m%d).log
```

For complete setup instructions, see `ROLLING_WINDOW_SETUP.md`.

### Production Deployment

#### GitHub Pages (Recommended)

1. **Push to GitHub:**
   ```bash
   git add .
   git commit -m "Update dashboard content"
   git push origin main
   ```

2. **Enable GitHub Pages:**
   - Go to repository Settings → Pages
   - Under **Source**, select **"GitHub Actions"**
   - The workflow will automatically deploy on push

3. **Access Your Dashboard:**
   - Available at: `https://yourusername.github.io/EncoreDashboard/`
   - **Announcements board fully functional** on live site
   - All features work exactly as in local development

#### Important: Cross-Device Announcements
- **Announcements are stored per-device** (browser localStorage)
- **To share between devices:** Use `Ctrl+E` (export) and `Ctrl+I` (import)
- **For kiosks/multiple screens:** Export from admin device, import to each display
- **Backup strategy:** Regular exports with `Ctrl+E`

📖 **See `GITHUB_PAGES_SETUP.md` for complete deployment guide**

3. **Kiosk Setup (Raspberry Pi):**
   ```bash
   # Install Chromium
   sudo apt update && sudo apt install chromium-browser xdotool

   # Create autostart configuration
   mkdir -p ~/.config/autostart
   cat > ~/.config/autostart/dashboard.desktop << EOF
   [Desktop Entry]
   Type=Application
   Name=Dashboard
   Exec=chromium-browser --kiosk --incognito --disable-pinch --overscroll-history-navigation=0 https://yourusername.github.io/EncoreDashboard/
   EOF

   # Create update script
   cat > ~/update_dashboard.sh << EOF
   #!/bin/bash
   cd ~/dashboard
   git pull --ff-only
   xdotool search --onlyvisible --class chromium key F5
   EOF
   chmod +x ~/update_dashboard.sh

   # Set up cron job for updates
   crontab -e
   # Add: */5 * * * * ~/update_dashboard.sh
   ```

## File Structure

```
EncoreDashboard/
├── flex_gantt.py              # Content generation script (monthly/weekly/daily/calendar modes)
├── monthly_update.py          # Automated monthly update script (includes calendar)
├── calendar_update.py         # Automated calendar-only update script
├── weekly_update.py           # Automated weekly update script
├── daily_update.py            # Automated daily update script
├── git_auto_commit.py         # Automatic git commit & push for image sync
├── setup_cron.sh             # Easy automation setup script  
├── pipeline.xlsx             # Source data
├── index.html                # Presentation layer
├── slides/                   # Generated content
│   ├── slides.json           # Manifest file
│   ├── gantt_YYYY_MM.png     # Monthly charts (rolling 3-month window)
│   ├── calendar_YYYY_MM.png  # Professional calendar views
│   ├── gantt_weekly_*.png    # Weekly "Happening This Week" chart
│   └── gantt_daily_*.png     # Daily "Happening Today" chart
├── logs/                     # Automation logs
│   ├── monthly_update_*.log  # Monthly execution logs (Gantt + Calendar)
│   ├── calendar_update_*.log # Calendar execution logs
│   ├── weekly_update_*.log   # Weekly execution logs
│   └── daily_update_*.log    # Daily execution logs
├── .github/workflows/        # CI/CD configuration
├── requirements.txt          # Python dependencies (updated)
├── README.md                 # This file
├── ROLLING_WINDOW_SETUP.md   # Detailed setup guide
├── AUTOMATED_IMAGE_SYNC.md   # Image synchronization setup guide
└── config.example.js         # API configuration template
```

## Features

### Content Generation
- **Excel integration** for easy data updates
- **Automatic image optimization** for fast loading
- **Chronological sorting** of slides
- **Manifest-based playlist** management
- **Automatic GitHub sync** for multi-screen deployments
- **Smart cleanup** of outdated images

### Presentation
- **Responsive design** that works on any screen size
- **Smooth transitions** between slides
- **Real-time weather** with geolocation
- **Live clock** display
- **Offline capability** with cached weather data
- **Dual time notifications**: Voice announcements on the hour + audio chimes at quarter hours
- **Visual progress indicators** for slide timing

### Announcements Board
- **Integrated announcements slide** in the slideshow rotation
- **Scheduled messaging** with start and end date/time
- **Clean, responsive interface** with polished glassmorphism design
- **Dynamic grid layouts** that adapt to any number of announcements
- **Full CRUD operations** (Create, Read, Update, Delete)
- **Click-to-reveal actions** for clean, uncluttered appearance
- **Automatic filtering** showing only current announcements
- **Smart sizing** - all announcements fit on screen simultaneously
- **Data persistence** using browser localStorage
- **Export/Import functionality** for backup and sharing
- **Real-time updates** when announcements expire or become active

### Kiosk Mode
- **Full-screen display** with no browser chrome
- **Automatic updates** every 5 minutes
- **Error handling** with graceful degradation
- **Touch-friendly** interface
- **Keyboard shortcuts** for manual control

## Configuration

### Slide Timing
Edit the `slideInterval` in `index.html` to change slide duration (default: 60 seconds).

### Weather Location
The dashboard automatically detects location or defaults to New York City. To change the default:

```javascript
let lat = 40.7128, lon = -74.0060; // Change these coordinates
```

### Update Frequency
Modify the auto-reload interval in `index.html`:

```javascript
setInterval(() => {
    location.reload();
}, 300000); // 5 minutes (300000ms)
```

### Keyboard Shortcuts
- **→ or Space**: Next slide
- **←**: Previous slide  
- **R**: Reload dashboard
- **C**: Test hourly chime and voice sequence
- **V**: Test current time announcement
- **Q**: Test quarter-hour chime
- **Escape**: Close announcements modal
- **Ctrl+E**: Export announcements data
- **Ctrl+I**: Import announcements data
- **Ctrl+D**: Debug all announcements with timing details

### Time Notifications
The dashboard provides both voice announcements and audio chimes:

**Hourly Chime and Voice (Top of the Hour)**
- Plays a pleasant chime followed by voice announcement every hour at :00
- Chime plays first, then after 1.5 seconds, voice announces the time (e.g., "It is 4 PM")
- Uses Web Audio API for chime and Web Speech API for voice with pleasant voice selection
- Test by pressing **C** or running `testChime()` in console
- Test current time anytime by pressing **V** or running `testTimeAnnouncement()` in console

**Quarter-Hour Chimes (15, 30, 45 minutes)**
- Pleasant audio chime only at :15, :30, and :45 minutes past each hour
- Uses Web Audio API for precise timing and quality
- Test by pressing **Q** or running `testQuarterChime()` in console

- No external audio files required for either system

### Audio Troubleshooting

If time notifications aren't working, check the following:

1. **User Interaction**: Modern browsers require user interaction before enabling audio. Simply click anywhere on the page, press any key, or move your mouse to enable audio automatically.

2. **Test Functions**: Use keyboard shortcuts to test audio:
   - Press **C** to test hourly time announcement
   - Press **V** to test current time announcement
   - Press **Q** to test quarter-hour chime

3. **Console Logging**: Check browser console (F12) for detailed audio system status and error messages.

4. **Browser Support**: 
   - Speech synthesis works in Chrome, Safari, Edge, Firefox
   - Web Audio API works in all modern browsers
   - Some browsers may require HTTPS for full functionality

**Test Announcements (For Debugging Only)**
- Test announcements can be created via browser console: `createTestAnnouncements()`
- Clean up test data with: `cleanupTestAnnouncements()`
- The Ctrl+T keyboard shortcut has been disabled to prevent accidental test data creation

## Announcements Board Usage

The dashboard includes a built-in announcements system that allows anyone to create, schedule, and manage announcements that appear in the slideshow rotation.

### Creating Announcements

1. **Access**: When the announcements slide appears in the rotation, you'll see a blue **+** button in the top-left corner
2. **Click the + button** to open the announcement creation modal
3. **Fill in the details**:
   - **Announcement Text**: Your message (supports line breaks)
   - **Start Date & Time**: When the announcement should begin showing
   - **End Date & Time**: When the announcement should stop showing
4. **Click "Create Announcement"** to save

### Managing Announcements

- **Edit**: Click any announcement to reveal edit/delete options, then click ✏️ Edit to modify it
- **Delete**: Click any announcement to reveal options, then click 🗑️ Delete to remove it (requires confirmation)  
- **Clean Interface**: Edit/delete buttons only appear when needed (click to reveal)
- **Automatic Filtering**: Only announcements scheduled for the current time are displayed
- **Real-time Updates**: Announcements automatically appear/disappear based on their schedule

### Advanced Features

**Data Export/Import**:
- **Export**: Press `Ctrl+E` to download all announcements as a JSON backup file
- **Import**: Press `Ctrl+I` to upload and restore announcements from a backup file
- **Merge vs Replace**: When importing, choose to merge with existing data or replace all

**Scheduling Examples**:
- **All-day announcement**: 12:00 AM to 11:59 PM on the same date (defaults to today)
- **Multi-day event**: Set start date to today, end date to next week
- **Specific hours**: 9:00 AM to 5:00 PM for business announcements  
- **Weekend-only**: Friday 5:00 PM to Monday 9:00 AM
- **Same-day events**: Both start and end dates default to today for convenience

**GitHub Pages Deployment**:
- **✅ Fully supported** - all announcements features work on GitHub Pages
- **🔄 Cloud Sync Available** - optional automatic sync across all devices
- **Per-device storage** - announcements stored in browser localStorage (with cloud backup)
- **Multi-device sync** - automatic with cloud sync, or manual export/import
- **Zero setup required** - just enable GitHub Pages with GitHub Actions
- **Automatic HTTPS** - secure by default
- **No server costs** - completely free hosting

**Cloud Sync (New!)**: 
- Enable automatic synchronization across all devices
- Announcements appear instantly on all screens
- See `CLOUD_SYNC_SETUP.md` for 5-minute setup guide
- Uses free JSONBin.io service (100k requests/month free tier)
- Fully optional - dashboard works perfectly without it

### Best Practices

- **Keep messages concise** - they'll be displayed alongside other dashboard content
- **Use clear dates/times** - consider your audience's timezone
- **Test timing** - create short test announcements to verify scheduling
- **Regular cleanup** - periodically review and delete old announcements
- **Backup data** - export announcements before major changes

### Testing and Debugging

The dashboard includes comprehensive testing tools for announcement scheduling:

**Quick Testing**:
- Press `Ctrl+T` to create test announcements that verify different timing scenarios
- Press `Ctrl+D` to debug all announcements and see detailed timing information
- Check browser console (F12) for detailed test results and scheduling information

**Test Scenarios Created**:
- **Active announcement**: Currently visible (started 30 min ago, ends in 1 hour)
- **Future announcement**: Will appear in 2 minutes and last 8 minutes
- **Expired announcement**: Should not be visible (ended 5 minutes ago)
- **All-day announcement**: Runs from midnight to 11:59 PM today

**Console Commands**:
```javascript
// Create test announcements
createTestAnnouncements();

// Run comprehensive scheduling tests
runSchedulingTests();

// Debug all announcements with timing details
debugAnnouncements();

// Clean up test announcements
cleanupTestAnnouncements();
```

**Real-time Updates**:
- Announcements automatically update every 30 seconds
- Display refreshes when navigating to the announcements slide
- Expired announcements disappear automatically
- Future announcements appear when their start time arrives

## Troubleshooting

### Images Not Loading
- Check that `slides/slides.json` exists and is valid JSON
- Verify PNG files are in the `slides/` directory
- Ensure file permissions allow web server access

### Weather Not Displaying
- Check internet connectivity
- Verify Open-Meteo API is accessible
- Check browser console for CORS errors

### Kiosk Not Updating
- Verify cron job is running: `crontab -l`
- Check git repository access: `git -C ~/dashboard status`
- Test manual update: `~/update_dashboard.sh`

## Advanced Features

### Custom Styling
The dashboard uses CSS custom properties for easy theming:

```css
:root {
    --primary-color: #1e3c72;
    --secondary-color: #2a5298;
    --text-color: white;
}
```

### Adding Widgets
Extend the dashboard by adding new sections to the HTML:

```html
<div class="widget">
    <h3>Custom Widget</h3>
    <div id="widget-content"></div>
</div>
```

### Authentication
For protected dashboards, wrap with Cloudflare Access or Netlify Identity. No code changes required.

## Performance

- **Image optimization** keeps slides under 300KB
- **Lazy loading** for smooth transitions
- **Local caching** reduces API calls
- **CDN delivery** via GitHub Pages

## Monitoring

### Health Check
Create a simple health check script:

```bash
#!/bin/bash
curl -f https://yourusername.github.io/EncoreDashboard/ || \
curl -X POST -H 'Content-type: application/json' \
  --data '{"text":"Dashboard is down!"}' \
  https://hooks.slack.com/services/YOUR/WEBHOOK/URL
```

### Logs
Monitor kiosk logs:
```bash
journalctl -u dashboard.service -f
```

## License

MIT License - see LICENSE file for details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review browser console for errors
3. Create an issue with detailed information

## Security

### API Key Management

**IMPORTANT:** Never commit API keys to version control!

1. **Local Development:**
   - Copy `config.example.js` to `config.js`
   - Add your OpenWeatherMap API key to `config.js`
   - The `config.js` file is automatically ignored by git

2. **Production Deployment:**
   - For GitHub Pages: Use repository secrets and environment variables
   - For other hosts: Use their environment variable systems
   - See the "Production Deployment" section for specific instructions

3. **If you accidentally commit an API key:**
   - Immediately revoke/regenerate the key at OpenWeatherMap
   - Remove it from git history using tools like `git filter-branch`

### Weather API Setup

1. **Get OpenWeatherMap API Key:**
   - Go to [openweathermap.org](https://openweathermap.org/api)
   - Sign up for free (allows 1,000 calls/day)
   - Go to API Keys section and copy your key

2. **Configure the dashboard:**
   ```bash
   cp config.example.js config.js
   # Edit config.js and replace YOUR_API_KEY_HERE with your actual key
   ```

3. **Troubleshooting Weather Issues:**
   - Open browser console (F12) to see error messages
   - Check if your API key is valid and has quota remaining
   - The dashboard falls back to Open-Meteo if OpenWeatherMap fails
   - Weather updates every 10 minutes and caches for 10 minutes 