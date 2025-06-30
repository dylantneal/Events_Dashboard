# Dashboard Automation Setup Guide

This guide explains how to set up and use both the rolling 3-month window and weekly "Happening This Week" functionality for your dashboard.

## Overview

The system now supports three types of automated chart generation:

### 🗓️ Rolling 3-Month Window (Monthly Updates)
- **Current behavior**: Shows the next 3 months from today's date
- **Monthly updates**: Automatically removes old charts and adds new ones
- **Example**: In July, it shows August, September, and October charts

### 📅 "Happening This Week" (Weekly Updates)
- **Current behavior**: Shows events for the current week (Monday to Sunday)
- **Weekly updates**: Updates every Monday at midnight
- **Example**: Shows detailed daily view of events happening this week

### ⏰ "Happening Today" (Daily Updates)
- **Current behavior**: Shows events for today (midnight to 11:59 PM)
- **Daily updates**: Updates every day at midnight
- **Example**: Shows hourly view of events happening today with precise timing

## Manual Usage

### Generate Current Rolling Window
To manually generate the current 3-month window:

```bash
python3 flex_gantt.py pipeline.xlsx --rolling-window --dashboard
```

### Generate Weekly Chart
To manually generate the "Happening This Week" chart:

```bash
python3 flex_gantt.py pipeline.xlsx --weekly --dashboard
```

### Generate Daily Chart
To manually generate the "Happening Today" chart:

```bash
python3 flex_gantt.py pipeline.xlsx --daily --dashboard
```

### Traditional Usage (Still Available)
To generate specific months (old behavior):

```bash
python3 flex_gantt.py pipeline.xlsx --months 7 8 9 --year 2025 --dashboard
```

## Automated Monthly Updates

### Option 1: Using the Automation Scripts

**Monthly rolling window update:**
```bash
python3 monthly_update.py
```

**Weekly "Happening This Week" update:**
```bash
python3 weekly_update.py
```

**Daily "Happening Today" update:**
```bash
python3 daily_update.py
```

These scripts will:
1. Generate appropriate charts (monthly rolling window, weekly, or daily)
2. Remove old charts that are no longer needed
3. Optimize images for dashboard display
4. Update the slides manifest
5. Log all activities to `logs/[monthly|weekly|daily]_update_YYYYMMDD.log`

### Option 2: Direct Chart Generation

**Rolling window:**
```bash
python3 flex_gantt.py pipeline.xlsx --rolling-window --dashboard
```

**Weekly chart:**
```bash
python3 flex_gantt.py pipeline.xlsx --weekly --dashboard
```

**Daily chart:**
```bash
python3 flex_gantt.py pipeline.xlsx --daily --dashboard
```

## Setting Up Automatic Scheduling

### macOS/Linux (using cron)

**Easy setup with interactive script:**
```bash
./setup_cron.sh
```

**Manual setup:**

1. Open your crontab for editing:
   ```bash
   crontab -e
   ```

2. Add the appropriate lines:
   ```bash
   # Monthly updates (1st of each month at 6 AM)
   0 6 1 * * cd /path/to/EncoreDashboard && python3 monthly_update.py
   
   # Weekly updates (every Monday at midnight)
   0 0 * * 1 cd /path/to/EncoreDashboard && python3 weekly_update.py
   
   # Daily updates (every day at midnight)
   0 0 * * * cd /path/to/EncoreDashboard && python3 daily_update.py
   ```

3. Replace `/path/to/EncoreDashboard` with your actual project path.

### Windows (using Task Scheduler)

**For Monthly Updates:**
1. Open Task Scheduler
2. Click "Create Basic Task"
3. Name: "Dashboard Monthly Update"
4. Trigger: Monthly, on the 1st day
5. Action: Start a program
6. Program: `python3`
7. Arguments: `monthly_update.py`
8. Start in: Your EncoreDashboard directory path

**For Weekly Updates:**
1. Open Task Scheduler
2. Click "Create Basic Task"
3. Name: "Dashboard Weekly Update"
4. Trigger: Weekly, on Monday
5. Time: 12:00 AM (midnight)
6. Action: Start a program
7. Program: `python3`
8. Arguments: `weekly_update.py`
9. Start in: Your EncoreDashboard directory path

**For Daily Updates:**
1. Open Task Scheduler
2. Click "Create Basic Task"
3. Name: "Dashboard Daily Update"
4. Trigger: Daily
5. Time: 12:00 AM (midnight)
6. Action: Start a program
7. Program: `python3`
8. Arguments: `daily_update.py`
9. Start in: Your EncoreDashboard directory path

## How the Rolling Window Works

### Current Date Logic
- The system calculates the next 3 months from today's date
- If today is June 30, 2025, it generates charts for:
  - July 2025
  - August 2025  
  - September 2025

### File Management
- **Old charts removed**: Any chart files not in the current 3-month window
- **New charts added**: Charts for months that don't exist yet
- **Preserved charts**: Charts that are still within the 3-month window

### Example Timeline
```
June 2025 → Shows: July, August, September
July 2025 → Shows: August, September, October (removes July)
August 2025 → Shows: September, October, November (removes August)
```

## File Structure

After running the rolling window update:

```
EncoreDashboard/
├── slides/
│   ├── gantt_2025_07.png           # Current month +1
│   ├── gantt_2025_08.png           # Current month +2  
│   ├── gantt_2025_09.png           # Current month +3
│   ├── gantt_weekly_2025_06_30.png # This week's chart (Monday-Sunday)
│   ├── gantt_daily_2025_06_30.png  # Today's chart (midnight-11:59 PM)
│   └── slides.json                 # Updated manifest
├── logs/
│   ├── monthly_update_YYYYMMDD.log # Monthly automation logs
│   ├── weekly_update_YYYYMMDD.log  # Weekly automation logs
│   └── daily_update_YYYYMMDD.log   # Daily automation logs
├── flex_gantt.py            # Updated script with monthly/weekly/daily modes
├── monthly_update.py        # Monthly automation script
├── weekly_update.py         # Weekly automation script
├── daily_update.py          # Daily automation script
└── pipeline.xlsx            # Your data source
```

## Troubleshooting

### Common Issues

1. **Python command not found**
   - Use `python3` instead of `python`
   - Ensure Python 3 is installed and in your PATH

2. **Permission errors on file deletion**
   - Ensure the script has write permissions to the slides directory
   - Check that chart files aren't being used by other applications

3. **Excel file not found**
   - Ensure `pipeline.xlsx` is in the same directory as the script
   - Check that the file isn't open in Excel (can cause read errors)

### Checking Dependencies

Install required packages:
```bash
pip3 install -r requirements.txt
```

Required packages:
- pandas>=1.5.0
- matplotlib>=3.5.0
- openpyxl>=3.0.0
- Pillow>=9.0.0
- python-dateutil>=2.8.0

## Testing the Setup

### Test Manual Execution

**Rolling window:**
```bash
python3 flex_gantt.py pipeline.xlsx --rolling-window --dashboard
```

**Weekly chart:**
```bash
python3 flex_gantt.py pipeline.xlsx --weekly --dashboard
```

**Daily chart:**
```bash
python3 flex_gantt.py pipeline.xlsx --daily --dashboard
```

### Test Automation Scripts

**Monthly:**
```bash
python3 monthly_update.py
```

**Weekly:**
```bash
python3 weekly_update.py
```

**Daily:**
```bash
python3 daily_update.py
```

### Verify Output
Check that:
- Monthly: 3 PNG files for next 3 months created in `slides/` directory
- Weekly: 1 PNG file for current week created in `slides/` directory
- Daily: 1 PNG file for today created in `slides/` directory
- `slides.json` is updated with the new file list
- Log files are created in `logs/` directory for each automation script

## Customization

### Changing the Window Size
To modify the 3-month window to a different size, edit the `get_rolling_months()` function in `flex_gantt.py`:

```python
for i in range(3):  # Change 3 to your desired number of months
```

### Modifying the Schedule
- **Weekly updates**: Change cron to `0 6 * * 1` (every Monday)
- **Bi-weekly**: Change to `0 6 1,15 * *` (1st and 15th of each month)
- **Different time**: Change `6` to your preferred hour (24-hour format)

## Support

For issues or questions:
1. Check the log files in the `logs/` directory
2. Verify all dependencies are installed
3. Ensure the Excel file is accessible and properly formatted
4. Test manual execution before setting up automation 