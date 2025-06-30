#!/usr/bin/env python3
"""
flex_gantt.py
-------------
Create month-by-month Gantt charts from the Marriott (or any similar) pipeline sheet.
Enhanced for dashboard kiosk system with image optimization and manifest generation.
Now supports rolling 3-month window for automatic dashboard updates.

Features:
- Automatic event filtering for all charts: "Marriott In-House Events 2025" events are excluded from all views
- ICW event filtering for monthly charts only (ICW events excluded from monthly views but included in weekly/daily for complete visibility)
- Color-coded bars by sales team member (Darren=Green, Dylan=Orange, Sarah=Pink, Eder=Purple, David=Blue)
- Enhanced visual styling with larger titles, better fonts, and professional appearance
- Sales team legend automatically generated
- Rolling 3-month window with automatic cleanup of old charts
- Daily charts with hourly granularity for precise timing

Usage examples
--------------
# July–September 2025 (same as before)
python flex_gantt.py pipeline.xlsx --months 7 8 9 --year 2025

# Just December 2025
python flex_gantt.py pipeline.xlsx --months December

# February & March 2026, save images to a custom folder
python flex_gantt.py pipeline.xlsx --months 2 3 --year 2026 --outdir ./charts

# Generate optimized slides for dashboard
python flex_gantt.py pipeline.xlsx --months 7 8 9 10 11 12 --year 2025 --dashboard

# Rolling 3-month window (automatically updates for current month +3)
python flex_gantt.py pipeline.xlsx --rolling-window --dashboard

# Happening This Week chart (current week Monday to Sunday)
python flex_gantt.py pipeline.xlsx --weekly --dashboard

# Happening Today chart (current day with hourly granularity)
python flex_gantt.py pipeline.xlsx --daily --dashboard
"""
import sys
import argparse
import calendar
import json
import glob
from pathlib import Path
from urllib.parse import unquote
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from PIL import Image
import os


def month_str_to_int(s: str) -> int:
    """Convert '7', 'Jul', 'July', etc. → 7  (raise ValueError if invalid)."""
    s_clean = s.strip().lower()
    # Numeric?
    if s_clean.isdigit():
        m = int(s_clean)
        if 1 <= m <= 12:
            return m
    # Named month?
    for i in range(1, 13):
        if s_clean in (calendar.month_name[i].lower(), calendar.month_abbr[i].lower()):
            return i
    raise ValueError(f"Unrecognized month: {s}")


def get_rolling_months() -> tuple[list[int], int]:
    """
    Get the next 3 months from current date.
    Returns: (list of month numbers, year for the last month)
    """
    current_date = datetime.now()
    months = []
    years = []
    
    for i in range(3):
        future_date = current_date + relativedelta(months=i+1)
        months.append(future_date.month)
        years.append(future_date.year)
    
    # Return months and the year (handle year transitions)
    return months, years


def get_current_week() -> tuple[pd.Timestamp, pd.Timestamp]:
    """
    Get the current week's start (Monday) and end (Sunday).
    Returns: (week_start, week_end)
    """
    current_date = datetime.now()
    
    # Get Monday of this week (weekday() returns 0=Monday, 6=Sunday)
    days_since_monday = current_date.weekday()
    week_start = current_date - timedelta(days=days_since_monday)
    week_end = week_start + timedelta(days=6)
    
    # Convert to pandas timestamps and set to start/end of day
    week_start = pd.Timestamp(week_start.year, week_start.month, week_start.day)
    week_end = pd.Timestamp(week_end.year, week_end.month, week_end.day, 23, 59, 59)
    
    return week_start, week_end


def get_current_day() -> tuple[pd.Timestamp, pd.Timestamp]:
    """
    Get the current day's start (midnight) and end (11:59:59 PM).
    Returns: (day_start, day_end)
    """
    current_date = datetime.now()
    
    # Start of today (midnight)
    day_start = pd.Timestamp(current_date.year, current_date.month, current_date.day)
    # End of today (11:59:59 PM)
    day_end = pd.Timestamp(current_date.year, current_date.month, current_date.day, 23, 59, 59)
    
    return day_start, day_end


def cleanup_old_charts(outdir: Path, current_months: list[int], current_years: list[int], preserve_weekly: bool = True, preserve_daily: bool = True) -> None:
    """
    Remove chart files that are not in the current 3-month rolling window.
    Optionally preserves the weekly and daily charts.
    """
    # Get all gantt chart files
    chart_files = list(outdir.glob("gantt_*.png"))
    
    # Create set of current chart filenames we want to keep
    current_charts = set()
    for month, year in zip(current_months, current_years):
        current_charts.add(f"gantt_{year}_{month:02d}.png")
    
    # Always preserve the weekly chart if it exists
    if preserve_weekly:
        weekly_charts = list(outdir.glob("gantt_weekly_*.png"))
        for weekly_chart in weekly_charts:
            current_charts.add(weekly_chart.name)
    
    # Always preserve the daily chart if it exists
    if preserve_daily:
        daily_charts = list(outdir.glob("gantt_daily_*.png"))
        for daily_chart in daily_charts:
            current_charts.add(daily_chart.name)
    
    # Remove files not in current window
    removed_count = 0
    for chart_file in chart_files:
        if chart_file.name not in current_charts:
            print(f"Removing old chart: {chart_file.name}")
            chart_file.unlink()
            removed_count += 1
    
    if removed_count > 0:
        print(f"Cleaned up {removed_count} old chart(s)")
    else:
        print("No old charts to remove")


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="Create monthly Gantt charts.")
    ap.add_argument("workbook", help="Path to the Excel workbook")
    
    # Make months optional when using rolling window
    ap.add_argument(
        "--months",
        nargs="*",
        help="Month numbers or names (e.g. 7 8 12  or  July September). Not needed with --rolling-window.",
    )
    ap.add_argument("--year", type=int, default=2025, help="Calendar year (default 2025)")
    ap.add_argument(
        "--sheet",
        default="Marriott Marquis Pipeline",
        help="Worksheet name (default: 'Marriott Marquis Pipeline')",
    )
    ap.add_argument(
        "--outdir",
        type=Path,
        default=None,
        help="Output directory for PNGs (defaults to workbook folder)",
    )
    ap.add_argument(
        "--dashboard",
        action="store_true",
        help="Generate optimized slides for dashboard kiosk",
    )
    ap.add_argument(
        "--rolling-window",
        action="store_true",
        help="Generate charts for rolling 3-month window (next 3 months from current date)",
    )
    ap.add_argument(
        "--weekly",
        action="store_true",
        help="Generate 'Happening This Week' chart for current week (Monday to Sunday)",
    )
    ap.add_argument(
        "--daily",
        action="store_true",
        help="Generate 'Happening Today' chart for current day (midnight to 11:59 PM)",
    )
    return ap.parse_args()


def load_events(workbook: Path, sheet_name: str) -> pd.DataFrame:
    """Read and tidy the sheet."""
    df = pd.read_excel(workbook, sheet_name=sheet_name)
    df["Event Start Date"] = pd.to_datetime(df["Event Start Date"])
    df["Event End Date"] = pd.to_datetime(df["Event End Date"])
    df.sort_values("Event Start Date", inplace=True)
    return df


def optimize_image_for_dashboard(image_path: Path) -> None:
    """Optimize PNG for dashboard: convert to 8-bit indexed color and strip metadata."""
    try:
        with Image.open(image_path) as img:
            # Convert to RGB if necessary (in case of RGBA)
            if img.mode in ('RGBA', 'LA', 'P'):
                # Create white background for transparency
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = background
            
            # Convert to 8-bit indexed color for smaller file size
            img = img.quantize(colors=256, method=2)  # Method 2 is median cut
            
            # Save optimized version, overwriting original
            img.save(image_path, 'PNG', optimize=True, compress_level=9)
            
            # Get file size for reporting
            size_kb = image_path.stat().st_size / 1024
            print(f"Optimized {image_path.name}: {size_kb:.1f} KB")
            
    except Exception as e:
        print(f"Warning: Could not optimize {image_path.name}: {e}")


def generate_slides_manifest(slides_dir: Path) -> None:
    """Generate slides.json manifest file listing all PNG slides in the directory."""
    # Find all PNG files in slides directory
    png_files = list(slides_dir.glob("*.png"))
    
    if not png_files:
        print("No PNG files found in slides directory")
        return
    
    # Sort files by name (which should be chronological based on our naming)
    png_files.sort(key=lambda x: x.name)
    
    # Create manifest with filenames only (relative to slides directory)
    manifest = {
        "slides": [f.name for f in png_files],
        "generated": pd.Timestamp.now().isoformat(),
        "count": len(png_files),
        "note": "Auto-generated manifest of all PNG files in slides directory"
    }
    
    # Write manifest file
    manifest_path = slides_dir / "slides.json"
    with open(manifest_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    
    print(f"Generated manifest: {manifest_path}")
    print(f"Slides in playlist: {len(png_files)}")
    for i, slide in enumerate(png_files, 1):
        size_kb = slide.stat().st_size / 1024
        print(f"  {i}. {slide.name} ({size_kb:.1f} KB)")


def get_seller_color(owner: str) -> str:
    """
    Get color for seller based on name mapping.
    
    Modern color scheme with sophisticated gradients:
    - Darren: Emerald (#10b981 - Modern Emerald)
    - Dylan: Amber (#f59e0b - Warm Amber)  
    - Sarah: Rose (#f43f5e - Vibrant Rose)
    - Eder: Violet (#8b5cf6 - Rich Violet)
    - David: Blue (#3b82f6 - Modern Blue)
    - Unknown/Unassigned: Slate (#64748b - Professional Slate)
    """
    owner_clean = str(owner).strip().lower() if pd.notna(owner) else ""
    
    color_mapping = {
        'darren': '#10b981',    # Modern Emerald - Fresh, professional green
        'dylan': '#f59e0b',     # Warm Amber - Sophisticated orange
        'sarah': '#f43f5e',     # Vibrant Rose - Modern pink
        'eder': '#8b5cf6',      # Rich Violet - Deep purple  
        'david': '#3b82f6',     # Modern Blue - Clean, professional blue
    }
    
    # Check for exact matches first, then partial matches
    if owner_clean in color_mapping:
        return color_mapping[owner_clean]
    
    for name, color in color_mapping.items():
        if name in owner_clean:
            return color
    
    # Default color for unknown sellers - professional slate
    return '#64748b'


def gantt_for_month(df: pd.DataFrame, year: int, month: int, outdir: Path) -> None:
    """Draw + save a single month's chart, clipping multi-month events."""
    mname = calendar.month_name[month]
    mstart = pd.Timestamp(year, month, 1)
    mend = pd.Timestamp(year, month, calendar.monthrange(year, month)[1])

    # Filter events for this month
    mask = (df["Event Start Date"] <= mend) & (df["Event End Date"] >= mstart)
    sub = df.loc[mask].copy()
    
    # Filter out events containing "ICW" or "Marriott In-House Events 2025" in the name
    icw_mask = ~sub["Event Name"].str.contains("ICW", case=False, na=False)
    marriott_mask = ~sub["Event Name"].str.contains("Marriott In-House Events 2025", case=False, na=False)
    combined_mask = icw_mask & marriott_mask
    sub = sub.loc[combined_mask]
    
    if sub.empty:
        print(f"[{mname}]  No events in sheet for this month (after filtering).")
        return
    
    # Sort by start date in descending order (most recent first)
    # This will display most recent events at the top of the chart
    sub = sub.sort_values("Event Start Date", ascending=False)

    # Clip to the month window and prepare data
    starts, durations, colors = [], [], []
    for _, row in sub.iterrows():
        s = max(row["Event Start Date"], mstart)
        e = min(row["Event End Date"], mend)
        starts.append(s)
        durations.append((e - s).days + 1)
        colors.append(get_seller_color(row.get("Owner", "")))

    # Enhanced plotting with modern styling
    fig_h = max(4.0, len(sub) * 0.4 + 3.5)  # More space for better readability
    fig_w = 20.0  # Optimal width for readability
    
    # Create figure with modern styling
    plt.style.use('default')  # Reset any previous styles
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), constrained_layout=True)
    
    # Modern gradient background
    fig.patch.set_facecolor('#f8fafc')
    ax.set_facecolor('#ffffff')
    
    # Create the horizontal bar chart with enhanced styling
    bars = ax.barh(sub["Event Name"], durations, left=starts, color=colors, 
                   alpha=0.9, edgecolor='white', linewidth=1.5, height=0.7)
    
    # Enhanced bar styling with transparency
    for bar, color in zip(bars, colors):
        bar.set_alpha(0.85)
        bar.set_linewidth(1.5)
        bar.set_edgecolor('white')
    
    # Enhanced styling
    ax.set_xlim(mstart - pd.Timedelta(hours=12), mend + pd.Timedelta(hours=36))
    
    # Use daily ticks to show day numbers
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d"))  # Just day numbers
    
    # Add week indicators with Monday markers (more prominent)
    ax.xaxis.set_minor_locator(mdates.WeekdayLocator(byweekday=mdates.MO))
    
    # Modern grid styling with enhanced week indicators
    ax.grid(axis="x", linestyle="-", linewidth=0.8, alpha=0.15, color='#94a3b8')  # Daily grid lines
    ax.grid(axis="x", which='minor', linestyle="-", linewidth=2.0, alpha=0.4, color='#475569')  # Week boundaries
    ax.set_axisbelow(True)
    
    # Add subtle week boundary indicators and alternating backgrounds
    week_dates = pd.date_range(mstart, mend, freq='W-MON')
    for i, date in enumerate(week_dates):
        if mstart <= date <= mend:
            # Week boundary line
            ax.axvline(x=date, color='#334155', linewidth=2.5, alpha=0.6, zorder=1)
            
            # Alternating week background (every other week gets subtle shading)
            if i % 2 == 1:
                week_end = min(date + pd.Timedelta(days=6, hours=23, minutes=59), mend)
                ax.axvspan(date, week_end, color='#f1f5f9', alpha=0.3, zorder=0)
    
    # Enhanced labels and title with modern typography
    ax.set_xlabel("Date", fontsize=16, fontweight='600', color='#1e293b', 
                  labelpad=15, fontfamily='sans-serif')
    ax.set_ylabel("Events", fontsize=16, fontweight='600', color='#1e293b', 
                  labelpad=15, fontfamily='sans-serif')
    
    # Modern title with enhanced styling
    title_text = ax.set_title(f"Events — {mname} {year}", 
                             fontsize=28, fontweight='700', color='#0f172a', 
                             pad=30, fontfamily='sans-serif')
    title_text.set_bbox(dict(boxstyle="round,pad=0.5", facecolor='#f1f5f9', 
                            alpha=0.8, edgecolor='none'))
    
    # Enhanced x-axis formatting - no rotation needed for day numbers
    plt.xticks(rotation=0, fontsize=11, color='#475569', fontweight='500')
    
    # Better y-axis formatting for event names
    ax.tick_params(axis='y', labelsize=11, colors='#334155', pad=8)
    ax.tick_params(axis='x', labelsize=11, colors='#475569', pad=5)
    
    # Improve the appearance of event names with better typography
    for label in ax.get_yticklabels():
        label.set_fontweight('500')
        label.set_fontfamily('sans-serif')
    
    for label in ax.get_xticklabels():
        label.set_fontweight('500')
        label.set_fontfamily('sans-serif')
        
    # Modern border styling
    for spine in ax.spines.values():
        spine.set_edgecolor('#cbd5e1')
        spine.set_linewidth(1.5)
    
    # Remove top and right spines for cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Create an enhanced legend for the color coding
    if 'Owner' in sub.columns:
        unique_owners = sub['Owner'].dropna().unique()
        legend_elements = []
        for owner in sorted(unique_owners):
            if pd.notna(owner) and str(owner).strip():
                color = get_seller_color(owner)
                legend_elements.append(plt.Rectangle((0,0),1,1, facecolor=color, 
                                                   edgecolor='white', linewidth=1.5,
                                                   label=str(owner).strip(), alpha=0.9))
        
        if legend_elements:
            legend = ax.legend(handles=legend_elements, loc='upper right', 
                             frameon=True, fancybox=True, shadow=True, 
                             framealpha=0.95, facecolor='#f8fafc',
                             edgecolor='#e2e8f0',
                             title='Sales Team', fontsize=11,
                             title_fontsize=13)
            legend.get_title().set_fontweight('600')
            legend.get_title().set_color('#1e293b')
            
            # Style legend text
            for text in legend.get_texts():
                text.set_fontweight('500')
                text.set_color('#374151')

    outfile = outdir / f"gantt_{year}_{month:02d}.png"
    fig.savefig(outfile, dpi=300, bbox_inches='tight', facecolor='#f8fafc', 
                edgecolor='none', pad_inches=0.3, 
                metadata={'Title': f'Events - {mname} {year}', 'Software': 'Encore Dashboard'})
    plt.close(fig)
    
    # Report filtering results
    total_events = len(df.loc[(df["Event Start Date"] <= mend) & (df["Event End Date"] >= mstart)])
    filtered_events = len(sub)
    
    # Calculate individual filter counts
    all_month_events = df.loc[(df["Event Start Date"] <= mend) & (df["Event End Date"] >= mstart)].copy()
    icw_filtered = len(all_month_events[all_month_events["Event Name"].str.contains("ICW", case=False, na=False)])
    marriott_filtered = len(all_month_events[all_month_events["Event Name"].str.contains("Marriott In-House Events 2025", case=False, na=False)])
    total_filtered = total_events - filtered_events
    
    print(f"Saved {outfile}")
    print(f"  Events shown: {filtered_events}, Filtered: {total_filtered} (ICW: {icw_filtered}, Marriott In-House: {marriott_filtered})")


def gantt_for_week(df: pd.DataFrame, outdir: Path) -> None:
    """Draw + save a 'Happening This Week' chart for the current week (Monday to Sunday)."""
    week_start, week_end = get_current_week()
    
    # Format week for display
    week_display = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"
    
    # Filter events for this week
    mask = (df["Event Start Date"] <= week_end) & (df["Event End Date"] >= week_start)
    sub = df.loc[mask].copy()
    
    # Filter out Marriott In-House Events 2025 (but keep ICW events for complete visibility)
    # Monthly charts exclude both ICW and Marriott In-House events
    marriott_mask = ~sub["Event Name"].str.contains("Marriott In-House Events 2025", case=False, na=False)
    sub = sub.loc[marriott_mask]
    
    if sub.empty:
        print(f"[This Week]  No events happening this week.")
        return
    
    # Sort by start date in descending order (most recent first)
    # This will display most recent events at the top of the chart
    sub = sub.sort_values("Event Start Date", ascending=False)

    # Clip to the week window and prepare data
    starts, durations, colors = [], [], []
    for _, row in sub.iterrows():
        s = max(row["Event Start Date"], week_start)
        e = min(row["Event End Date"], week_end)
        starts.append(s)
        durations.append((e - s).total_seconds() / 86400 + 1)  # Convert to days
        colors.append(get_seller_color(row.get("Owner", "")))

    # Enhanced plotting with modern styling for weekly view
    fig_h = max(4.5, len(sub) * 0.45 + 3.5)  # More space for weekly view
    fig_w = 20.0
    
    # Create figure with modern styling
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), constrained_layout=True)
    
    # Modern gradient background
    fig.patch.set_facecolor('#f8fafc')
    ax.set_facecolor('#ffffff')
    
    # Create the horizontal bar chart with enhanced styling
    bars = ax.barh(sub["Event Name"], durations, left=starts, color=colors, 
                   alpha=0.9, edgecolor='white', linewidth=1.5, height=0.7)
    
    # Enhanced bar styling with transparency
    for bar, color in zip(bars, colors):
        bar.set_alpha(0.85)
        bar.set_linewidth(1.5)
        bar.set_edgecolor('white')
    
    # Enhanced styling for weekly view
    ax.set_xlim(week_start - pd.Timedelta(hours=6), week_end + pd.Timedelta(hours=18))
    
    # Use daily locator for better weekly granularity
    ax.xaxis.set_major_locator(mdates.DayLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%a\n%b %d"))
    
    # Modern grid styling
    ax.grid(axis="x", linestyle="-", linewidth=1.2, alpha=0.2, color='#64748b')
    ax.grid(axis="x", which='minor', linestyle=":", linewidth=0.8, alpha=0.15, color='#94a3b8')
    ax.set_axisbelow(True)
    
    # Enhanced labels and title with modern typography
    ax.set_xlabel("Date", fontsize=16, fontweight='600', color='#1e293b', 
                  labelpad=15, fontfamily='sans-serif')
    ax.set_ylabel("Events", fontsize=16, fontweight='600', color='#1e293b', 
                  labelpad=15, fontfamily='sans-serif')
    
    # Modern title with enhanced styling
    title_text = ax.set_title(f"Happening This Week — {week_display}", 
                             fontsize=28, fontweight='700', color='#0f172a', 
                             pad=30, fontfamily='sans-serif')
    title_text.set_bbox(dict(boxstyle="round,pad=0.5", facecolor='#f1f5f9', 
                            alpha=0.8, edgecolor='none'))
    
    # Enhanced x-axis formatting
    plt.xticks(rotation=0, fontsize=12, color='#475569', fontweight='500')  # No rotation for weekly view
    
    # Better y-axis formatting for event names
    ax.tick_params(axis='y', labelsize=11, colors='#334155', pad=8)
    ax.tick_params(axis='x', labelsize=11, colors='#475569', pad=5)
    
    # Improve the appearance of event names with better typography
    for label in ax.get_yticklabels():
        label.set_fontweight('500')
        label.set_fontfamily('sans-serif')
    
    for label in ax.get_xticklabels():
        label.set_fontweight('500')
        label.set_fontfamily('sans-serif')
        
    # Modern border styling
    for spine in ax.spines.values():
        spine.set_edgecolor('#cbd5e1')
        spine.set_linewidth(1.5)
    
    # Remove top and right spines for cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Create an enhanced legend for the color coding
    if 'Owner' in sub.columns:
        unique_owners = sub['Owner'].dropna().unique()
        legend_elements = []
        for owner in sorted(unique_owners):
            if pd.notna(owner) and str(owner).strip():
                color = get_seller_color(owner)
                legend_elements.append(plt.Rectangle((0,0),1,1, facecolor=color, 
                                                   edgecolor='white', linewidth=1.5,
                                                   label=str(owner).strip(), alpha=0.9))
        
        if legend_elements:
            legend = ax.legend(handles=legend_elements, loc='upper right', 
                             frameon=True, fancybox=True, shadow=True, 
                             framealpha=0.95, facecolor='#f8fafc',
                             edgecolor='#e2e8f0',
                             title='Sales Team', fontsize=11,
                             title_fontsize=13)
            legend.get_title().set_fontweight('600')
            legend.get_title().set_color('#1e293b')
            
            # Style legend text
            for text in legend.get_texts():
                text.set_fontweight('500')
                text.set_color('#374151')

    # Use Monday's date for filename consistency
    outfile = outdir / f"gantt_weekly_{week_start.strftime('%Y_%m_%d')}.png"
    fig.savefig(outfile, dpi=300, bbox_inches='tight', facecolor='#f8fafc', 
                edgecolor='none', pad_inches=0.3,
                metadata={'Title': f'Happening This Week - {week_display}', 'Software': 'Encore Dashboard'})
    plt.close(fig)
    
    # Report results
    total_events = len(df.loc[(df["Event Start Date"] <= week_end) & (df["Event End Date"] >= week_start)])
    filtered_events = len(sub)
    
    # Calculate Marriott In-House events filtered
    all_week_events = df.loc[(df["Event Start Date"] <= week_end) & (df["Event End Date"] >= week_start)].copy()
    marriott_filtered = len(all_week_events[all_week_events["Event Name"].str.contains("Marriott In-House Events 2025", case=False, na=False)])
    
    print(f"Saved {outfile}")
    print(f"  Weekly events shown: {filtered_events} (includes ICW events, excludes {marriott_filtered} Marriott In-House events)")
    print(f"  Week period: {week_display}")


def gantt_for_day(df: pd.DataFrame, outdir: Path) -> None:
    """Draw + save a 'Happening Today' chart for the current day (midnight to 11:59 PM)."""
    day_start, day_end = get_current_day()
    
    # Format day for display
    day_display = day_start.strftime('%A, %B %d, %Y')
    
    # Filter events for today
    mask = (df["Event Start Date"] <= day_end) & (df["Event End Date"] >= day_start)
    sub = df.loc[mask].copy()
    
    # Filter out Marriott In-House Events 2025 (but keep ICW events for complete visibility)
    # Monthly charts exclude both ICW and Marriott In-House events
    marriott_mask = ~sub["Event Name"].str.contains("Marriott In-House Events 2025", case=False, na=False)
    sub = sub.loc[marriott_mask]
    
    if sub.empty:
        print(f"[Today]  No events happening today.")
        return
    
    # Sort by start date in descending order (most recent first)
    # This will display most recent events at the top of the chart
    sub = sub.sort_values("Event Start Date", ascending=False)

    # Clip to the day window and prepare data
    starts, durations, colors = [], [], []
    for _, row in sub.iterrows():
        s = max(row["Event Start Date"], day_start)
        e = min(row["Event End Date"], day_end)
        starts.append(s)
        durations.append((e - s).total_seconds() / 86400 + 1)  # Convert to days
        colors.append(get_seller_color(row.get("Owner", "")))

    # Enhanced plotting with modern styling for daily view
    fig_h = max(5.0, len(sub) * 0.5 + 4.0)  # More space for daily view
    fig_w = 20.0
    
    # Create figure with modern styling
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), constrained_layout=True)
    
    # Modern gradient background
    fig.patch.set_facecolor('#f8fafc')
    ax.set_facecolor('#ffffff')
    
    # Create the horizontal bar chart with enhanced styling
    bars = ax.barh(sub["Event Name"], durations, left=starts, color=colors, 
                   alpha=0.9, edgecolor='white', linewidth=1.5, height=0.7)
    
    # Enhanced bar styling with transparency
    for bar, color in zip(bars, colors):
        bar.set_alpha(0.85)
        bar.set_linewidth(1.5)
        bar.set_edgecolor('white')
    
    # Enhanced styling for daily view
    ax.set_xlim(day_start - pd.Timedelta(minutes=30), day_end + pd.Timedelta(hours=1))
    
    # Use hourly locator for better daily granularity
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=4))  # Every 4 hours
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    ax.xaxis.set_minor_locator(mdates.HourLocator(interval=1))  # Every hour as minor ticks
    
    # Modern grid styling
    ax.grid(axis="x", linestyle="-", linewidth=1.2, alpha=0.2, color='#64748b')
    ax.grid(axis="x", which='minor', linestyle=":", linewidth=0.8, alpha=0.15, color='#94a3b8')
    ax.set_axisbelow(True)
    
    # Enhanced labels and title with modern typography
    ax.set_xlabel("Time", fontsize=16, fontweight='600', color='#1e293b', 
                  labelpad=15, fontfamily='sans-serif')
    ax.set_ylabel("Events", fontsize=16, fontweight='600', color='#1e293b', 
                  labelpad=15, fontfamily='sans-serif')
    
    # Modern title with enhanced styling
    title_text = ax.set_title(f"Happening Today — {day_display}", 
                             fontsize=28, fontweight='700', color='#0f172a', 
                             pad=30, fontfamily='sans-serif')
    title_text.set_bbox(dict(boxstyle="round,pad=0.5", facecolor='#f1f5f9', 
                            alpha=0.8, edgecolor='none'))
    
    # Enhanced axis formatting
    plt.xticks(rotation=0, fontsize=12, color='#475569', fontweight='500')
    
    # Better y-axis formatting for event names
    ax.tick_params(axis='y', labelsize=11, colors='#334155', pad=8)
    ax.tick_params(axis='x', labelsize=11, colors='#475569', pad=5)
    
    # Improve the appearance of event names with better typography
    for label in ax.get_yticklabels():
        label.set_fontweight('500')
        label.set_fontfamily('sans-serif')
    
    for label in ax.get_xticklabels():
        label.set_fontweight('500')
        label.set_fontfamily('sans-serif')
        
    # Modern border styling
    for spine in ax.spines.values():
        spine.set_edgecolor('#cbd5e1')
        spine.set_linewidth(1.5)
    
    # Remove top and right spines for cleaner look
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    # Create an enhanced legend for the color coding
    if 'Owner' in sub.columns:
        unique_owners = sub['Owner'].dropna().unique()
        legend_elements = []
        for owner in sorted(unique_owners):
            if pd.notna(owner) and str(owner).strip():
                color = get_seller_color(owner)
                legend_elements.append(plt.Rectangle((0,0),1,1, facecolor=color, 
                                                   edgecolor='white', linewidth=1.5,
                                                   label=str(owner).strip(), alpha=0.9))
        
        if legend_elements:
            legend = ax.legend(handles=legend_elements, loc='upper right', 
                             frameon=True, fancybox=True, shadow=True, 
                             framealpha=0.95, facecolor='#f8fafc',
                             edgecolor='#e2e8f0',
                             title='Sales Team', fontsize=11,
                             title_fontsize=13)
            legend.get_title().set_fontweight('600')
            legend.get_title().set_color('#1e293b')
            
            # Style legend text
            for text in legend.get_texts():
                text.set_fontweight('500')
                text.set_color('#374151')

    # Use today's date for filename consistency
    outfile = outdir / f"gantt_daily_{day_start.strftime('%Y_%m_%d')}.png"
    fig.savefig(outfile, dpi=300, bbox_inches='tight', facecolor='#f8fafc', 
                edgecolor='none', pad_inches=0.3,
                metadata={'Title': f'Happening Today - {day_display}', 'Software': 'Encore Dashboard'})
    plt.close(fig)
    
    # Report results
    total_events = len(df.loc[(df["Event Start Date"] <= day_end) & (df["Event End Date"] >= day_start)])
    filtered_events = len(sub)
    
    # Calculate Marriott In-House events filtered
    all_day_events = df.loc[(df["Event Start Date"] <= day_end) & (df["Event End Date"] >= day_start)].copy()
    marriott_filtered = len(all_day_events[all_day_events["Event Name"].str.contains("Marriott In-House Events 2025", case=False, na=False)])
    
    print(f"Saved {outfile}")
    print(f"  Daily events shown: {filtered_events} (includes ICW events, excludes {marriott_filtered} Marriott In-House events)")
    print(f"  Day: {day_display}")


def main() -> None:
    args = parse_args()
    
    # Handle URL-encoded characters in the path
    decoded_workbook = unquote(args.workbook)
    wb = Path(decoded_workbook).expanduser().resolve()
    
    if not wb.exists():
        sys.exit(f"Workbook not found: {wb}")

    # Use slides directory if dashboard mode is enabled
    if args.dashboard:
        outdir = Path("slides")
        outdir.mkdir(parents=True, exist_ok=True)
    else:
        outdir = args.outdir or wb.parent
        outdir.mkdir(parents=True, exist_ok=True)

    # Handle daily mode
    if args.daily:
        print(f"Daily mode: generating 'Happening Today' chart")
        day_start, day_end = get_current_day()
        print(f"  Day: {day_start.strftime('%A, %B %d, %Y')}")
        
        # Generate daily chart
        df = load_events(wb, args.sheet)
        gantt_for_day(df, outdir)
        
    # Handle weekly mode
    elif args.weekly:
        print(f"Weekly mode: generating 'Happening This Week' chart")
        week_start, week_end = get_current_week()
        print(f"  Week: {week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}")
        
        # Generate weekly chart
        df = load_events(wb, args.sheet)
        gantt_for_week(df, outdir)
        
    # Handle rolling window mode
    elif args.rolling_window:
        months, years = get_rolling_months()
        print(f"Rolling window mode: generating charts for next 3 months")
        for i, (month, year) in enumerate(zip(months, years)):
            month_name = calendar.month_name[month]
            print(f"  {i+1}. {month_name} {year}")
        
        # Clean up old charts before generating new ones
        cleanup_old_charts(outdir, months, years)
        
        # Generate charts for each month/year combination
        df = load_events(wb, args.sheet)
        
        for month, year in zip(months, years):
            # Filter data for this specific month/year
            month_start = pd.Timestamp(year, month, 1)
            month_end = pd.Timestamp(year, month, calendar.monthrange(year, month)[1])
            month_df = df[(df["Event End Date"] >= month_start) & (df["Event Start Date"] <= month_end)]
            gantt_for_month(month_df, year, month, outdir)
        
    else:
        # Original behavior - validate months argument
        if not args.months:
            sys.exit("Error: --months is required unless using --rolling-window, --weekly, or --daily")
            
        # Convert requested months to integers (deduplicate & sort)
        try:
            months = sorted({month_str_to_int(m) for m in args.months})
        except ValueError as e:
            sys.exit(e)

        df = load_events(wb, args.sheet)

        # Filter the dataframe once for the whole requested span (speed)
        span_start = pd.Timestamp(args.year, months[0], 1)
        span_end = pd.Timestamp(
            args.year, months[-1], calendar.monthrange(args.year, months[-1])[1]
        )
        df = df[(df["Event End Date"] >= span_start) & (df["Event Start Date"] <= span_end)]

        for m in months:
            gantt_for_month(df, args.year, m, outdir)
    
    # If in dashboard mode, optimize images and generate manifest
    if args.dashboard:
        print("\nOptimizing images for dashboard...")
        for png_file in outdir.glob("*.png"):
            optimize_image_for_dashboard(png_file)
        
        print("\nGenerating slides manifest...")
        generate_slides_manifest(outdir)


if __name__ == "__main__":
    main()
