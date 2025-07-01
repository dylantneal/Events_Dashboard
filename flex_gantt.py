#!/usr/bin/env python3
"""
flex_gantt.py
-------------
Create month-by-month Gantt charts from the Marriott (or any similar) pipeline sheet.
Enhanced for dashboard kiosk system with image optimization and manifest generation.
Now supports rolling 3-month window for automatic dashboard updates and calendar views.

Features:
- Automatic event filtering for all charts: "Marriott In-House Events 2025" events are excluded from all views
- ICW event filtering for monthly charts only (ICW events excluded from monthly views but included in weekly/daily for complete visibility)
- Color-coded bars by sales team member (Darren=Green, Dylan=Orange, Sarah=Pink, Eder=Purple, David=Blue)
- Enhanced visual styling with larger titles, better fonts, and professional appearance
- Sales team legend automatically generated
- Rolling 3-month window with automatic cleanup of old charts
- Daily charts with hourly granularity for precise timing
- Professional calendar views with event placement and owner color coding

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

# Generate calendar view for current month
python flex_gantt.py pipeline.xlsx --calendar --dashboard

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
import matplotlib.patches as patches
from matplotlib.patches import Rectangle
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
    ap = argparse.ArgumentParser(description="Create monthly Gantt charts and calendar views.")
    ap.add_argument("workbook", help="Path to the Excel workbook")
    
    # Make months optional when using rolling window
    ap.add_argument(
        "--months",
        nargs="*",
        help="Month numbers or names (e.g. 7 8 12  or  July September). Not needed with --rolling-window or --calendar.",
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
        "--calendar",
        action="store_true",
        help="Generate calendar view for current month",
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
    
    Modern color scheme with lighter tones for black text readability:
    - Darren: Light Emerald (#6ee7b7)
    - Dylan: Light Amber (#fcd34d)  
    - Sarah: Light Rose (#fda4af)
    - Eder: Light Violet (#c4b5fd)
    - David: Light Blue (#93c5fd)
    - Unknown/Unassigned: Light Yellow (#fde047)
    """
    owner_clean = str(owner).strip().lower() if pd.notna(owner) else ""
    
    color_mapping = {
        'darren': '#6ee7b7',    # Light Emerald - Softer green for black text
        'dylan': '#fcd34d',     # Light Amber - Softer orange for black text
        'sarah': '#fda4af',     # Light Rose - Softer pink for black text
        'eder': '#c4b5fd',      # Light Violet - Softer purple for black text
        'david': '#93c5fd',     # Light Blue - Softer blue for black text
    }
    
    # Check for exact matches first, then partial matches
    if owner_clean in color_mapping:
        return color_mapping[owner_clean]
    
    for name, color in color_mapping.items():
        if name in owner_clean:
            return color
    
    # Default color for unknown sellers - light yellow
    return '#fde047'


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


def calendar_for_month(df: pd.DataFrame, year: int, month: int, outdir: Path) -> None:
    """Draw + save a professional calendar view for the specified month."""
    import textwrap
    from matplotlib.patches import FancyBboxPatch
    
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
    
    # Create figure with optimal sizing for calendar
    fig_w, fig_h = 22.0, 18.0  # Larger size for better readability
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), constrained_layout=True)
    
    # Elegant gradient background
    fig.patch.set_facecolor('#fafbfc')
    ax.set_facecolor('#ffffff')
    
    # Set up calendar grid starting with Sunday
    calendar.setfirstweekday(calendar.SUNDAY)
    cal = calendar.monthcalendar(year, month)
    num_weeks = len(cal)
    
    # Set axis limits with generous padding for professional appearance
    ax.set_xlim(-0.1, 7.1)
    ax.set_ylim(-0.15, num_weeks + 1.4)
    
    # Remove axis ticks and labels
    ax.set_xticks([])
    ax.set_yticks([])
    
    # Remove spines
    for spine in ax.spines.values():
        spine.set_visible(False)
    
    # Sophisticated title design
    title_text = ax.set_title(f"{mname} {year}", 
                             fontsize=48, fontweight='800', color='#1a202c', 
                             pad=60, fontfamily='sans-serif')
    title_text.set_bbox(dict(boxstyle="round,pad=0.8", 
                            facecolor='#ffffff', alpha=0.98,
                            edgecolor='#e2e8f0', linewidth=1.5))
    
        # Clean day names header with uniform styling
    day_names = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
    
    # Add subtle background bar for all headers
    header_bg = FancyBboxPatch((0, num_weeks + 0.1), 7, 0.8,
                              boxstyle="round,pad=0.02",
                              facecolor='#f8fafc', alpha=0.8,
                              edgecolor='#e5e7eb', linewidth=1)
    ax.add_patch(header_bg)
    
    for i, day_name in enumerate(day_names):
        # Uniform styling for all days
        header_color = '#f0f9ff'
        border_color = '#3b82f6'
        text_color = '#1e40af'
            
        ax.text(i + 0.5, num_weeks + 0.5, day_name, 
                ha='center', va='center', fontsize=18, fontweight='700',
                color=text_color, fontfamily='sans-serif')
        
        # Clean header cells with uniform borders
        header_rect = FancyBboxPatch((i + 0.05, num_weeks + 0.15), 0.9, 0.7,
                                   boxstyle="round,pad=0.02",
                                   facecolor=header_color, alpha=0.8,
                                   edgecolor=border_color, linewidth=2)
        ax.add_patch(header_rect)
    
    # Draw clean calendar grid with uniform design
    for week_idx, week in enumerate(cal):
        y_pos = num_weeks - week_idx - 1
        
        for day_idx, day in enumerate(week):
            x_pos = day_idx
            
            # Clean cell design with uniform appearance
            if day == 0:
                # Muted cells for days from other months
                cell_rect = FancyBboxPatch((x_pos + 0.04, y_pos + 0.04), 0.92, 0.92,
                                         boxstyle="round,pad=0.02",
                                         facecolor='#f9fafb', alpha=0.4,
                                         edgecolor='#f3f4f6', linewidth=1)
            else:
                # Uniform cell design for all days
                cell_color = '#ffffff'  # Clean white background
                border_color = '#6b7280'
                inner_border = '#e5e7eb'
                shadow_color = '#9ca3af'
                    
                # Subtle outer shadow
                shadow_rect = FancyBboxPatch((x_pos + 0.06, y_pos + 0.02), 0.92, 0.92,
                                           boxstyle="round,pad=0.02",
                                           facecolor=shadow_color, alpha=0.08,
                                           edgecolor='none')
                ax.add_patch(shadow_rect)
                
                # Main cell with elegant borders
                cell_rect = FancyBboxPatch((x_pos + 0.04, y_pos + 0.04), 0.92, 0.92,
                                         boxstyle="round,pad=0.02",
                                         facecolor=cell_color, alpha=0.98,
                                         edgecolor=border_color, linewidth=1.5)
                ax.add_patch(cell_rect)
                
                # Inner highlight border for depth
                inner_rect = FancyBboxPatch((x_pos + 0.06, y_pos + 0.06), 0.88, 0.88,
                                          boxstyle="round,pad=0.01",
                                          facecolor='none',
                                          edgecolor=inner_border, linewidth=1, alpha=0.6)
                ax.add_patch(inner_rect)
            
            # Enhanced day number styling
            if day != 0:
                # Check if this is today
                today = datetime.now()
                is_today = (today.year == year and today.month == month and today.day == day)
                
                if is_today:
                    # Beautiful today indicator with modern design
                    # Outer glow
                    glow_circle = plt.Circle((x_pos + 0.2, y_pos + 0.8), 0.18,
                                           color='#3b82f6', alpha=0.2)
                    ax.add_patch(glow_circle)
                    
                    # Main today indicator
                    today_circle = plt.Circle((x_pos + 0.2, y_pos + 0.8), 0.14,
                                            color='#3b82f6', alpha=0.95)
                    ax.add_patch(today_circle)
                    
                    # Inner highlight
                    highlight_circle = plt.Circle((x_pos + 0.2, y_pos + 0.8), 0.12,
                                                color='#60a5fa', alpha=0.3)
                    ax.add_patch(highlight_circle)
                    
                    day_color = '#ffffff'
                    day_weight = '800'
                    day_size = 16
                else:
                    day_color = '#1f2937'  # Strong color for all days
                    day_weight = '700'
                    day_size = 15
                
                ax.text(x_pos + 0.2, y_pos + 0.8, str(day),
                       ha='center', va='center', fontsize=day_size, 
                       fontweight=day_weight, color=day_color,
                       fontfamily='sans-serif')
    
    # Add events to calendar with continuous multi-day spans
    if not sub.empty:
        # Track events per day to handle vertical stacking
        events_per_day = {}
        
        # First pass: count events per day to determine maximum events on any day
        max_events_per_day = 0
        for _, event in sub.iterrows():
            event_start = max(event["Event Start Date"], mstart)
            event_end = min(event["Event End Date"], mend)
            
            current_date = event_start.date()
            end_date = event_end.date()
            
            while current_date <= end_date:
                if current_date.month == month:
                    day_key = current_date.day
                    if day_key not in events_per_day:
                        events_per_day[day_key] = 0
                    events_per_day[day_key] += 1
                    max_events_per_day = max(max_events_per_day, events_per_day[day_key])
                current_date += timedelta(days=1)
        
        # Reset counter for actual placement
        events_per_day = {}
        
        # Calculate optimal event height for better readability
        max_events_to_fit = min(max_events_per_day, 5)  # Limit to 5 events max per day for better readability
        event_height = min(0.18, 0.8 / max_events_to_fit)  # Larger height for better text readability
        event_spacing = 0.03  # Better spacing between events
        
        for _, event in sub.iterrows():
            event_start = max(event["Event Start Date"], mstart)
            event_end = min(event["Event End Date"], mend)
            
            # Get owner color
            owner_color = get_seller_color(event.get("Owner", ""))
            event_name = str(event["Event Name"])
            
            # Calculate all days this event spans within the month
            span_start = event_start.date()
            span_end = event_end.date()
            
            # Group consecutive days by week and position to create continuous spans
            event_spans = []  # List of (start_pos, end_pos, week_y) tuples
            
            current_date = span_start
            while current_date <= span_end:
                if current_date.month == month:
                    # Find position in calendar
                    day = current_date.day
                    
                    # Find which week and day of week
                    for week_idx, week in enumerate(cal):
                        if day in week:
                            day_idx = week.index(day)
                            y_pos = num_weeks - week_idx - 1
                            x_pos = day_idx
                            break
                    else:
                        current_date += timedelta(days=1)
                        continue
                    
                    # Find consecutive days in the same week
                    span_start_x = x_pos
                    span_y = y_pos
                    span_end_x = x_pos
                    
                    # Look ahead for consecutive days in same week
                    look_ahead_date = current_date + timedelta(days=1)
                    while (look_ahead_date <= span_end and 
                           look_ahead_date.month == month and
                           span_end_x < 6):  # Don't go past Saturday
                        
                        look_ahead_day = look_ahead_date.day
                        # Check if next day is in same week
                        for week_idx, week in enumerate(cal):
                            if look_ahead_day in week:
                                look_ahead_day_idx = week.index(look_ahead_day)
                                look_ahead_y_pos = num_weeks - week_idx - 1
                                if (look_ahead_y_pos == span_y and 
                                    look_ahead_day_idx == span_end_x + 1):
                                    span_end_x = look_ahead_day_idx
                                    current_date = look_ahead_date
                                    look_ahead_date += timedelta(days=1)
                                else:
                                    break
                                break
                        else:
                            break
                    
                    event_spans.append((span_start_x, span_end_x, span_y))
                
                current_date += timedelta(days=1)
            
            # Draw continuous event spans
            for span_start_x, span_end_x, span_y in event_spans:
                # Track events for vertical stacking at the start position
                day_key = (span_start_x, span_y)
                if day_key not in events_per_day:
                    events_per_day[day_key] = 0
                
                # Calculate vertical offset for this event
                event_index = events_per_day[day_key]
                base_offset = 0.08
                event_y_offset = base_offset + event_index * (event_height + event_spacing)
                
                # Skip if event would go outside cell boundaries
                if event_y_offset + event_height > 0.92:
                    continue
                
                events_per_day[day_key] += 1
                
                # Calculate continuous span dimensions
                rect_x = span_start_x + 0.06
                rect_width = (span_end_x - span_start_x + 1) - 0.12  # Account for padding
                rect_y = span_y + event_y_offset
                rect_height = event_height
                
                # Add subtle shadow for depth
                shadow_rect = FancyBboxPatch((rect_x + 0.01, rect_y - 0.01), rect_width, rect_height,
                                           boxstyle="round,pad=0.02",
                                           facecolor='#000000', alpha=0.1,
                                           edgecolor='none')
                ax.add_patch(shadow_rect)
                
                # Create beautiful continuous event box
                event_rect = FancyBboxPatch((rect_x, rect_y), rect_width, rect_height,
                                          boxstyle="round,pad=0.02",
                                          facecolor=owner_color, alpha=0.9,
                                          edgecolor='white', linewidth=2)
                ax.add_patch(event_rect)
                
                # Add subtle inner highlight for depth
                highlight_rect = FancyBboxPatch((rect_x + 0.005, rect_y + 0.005), 
                                              rect_width - 0.01, rect_height - 0.01,
                                              boxstyle="round,pad=0.005",
                                              facecolor='white', alpha=0.2,
                                              edgecolor='none')
                ax.add_patch(highlight_rect)
                
                # Add event text with smart sizing based on total span width
                font_size = max(9, min(12, int(event_height * 50)))
                
                # Center positioning for text across entire span
                text_x = rect_x + rect_width/2
                text_y = rect_y + rect_height/2
                
                # Calculate available width for text based on entire span
                available_width = rect_width - 0.1  # Leave padding
                
                # Estimate character width (rough approximation)
                char_width = font_size * 0.007
                max_chars = int(available_width / char_width)
                
                # Smart truncation based on available space across full span
                display_name = event_name
                if len(event_name) > max_chars and max_chars > 0:
                    if max_chars > 10:  # Try word boundaries if reasonable space
                        words = event_name.split()
                        truncated = ""
                        for word in words:
                            if len(truncated + word) <= max_chars - 3:
                                truncated += word + " "
                            else:
                                break
                        display_name = truncated.strip() + "..." if truncated.strip() else event_name[:max_chars-3] + "..."
                    else:
                        display_name = event_name[:max_chars-3] + "..." if max_chars > 3 else event_name[:max_chars]
                
                # Draw text in black for better readability on colored backgrounds
                ax.text(text_x, text_y, display_name,
                       ha='center', va='center', fontsize=font_size, 
                       fontweight='600', color='black',
                       fontfamily='sans-serif')
    
    # Create an elegant legend positioned to avoid Monday coverage
    if 'Owner' in sub.columns and not sub.empty:
        unique_owners = sub['Owner'].dropna().unique()
        if len(unique_owners) > 0:
            legend_elements = []
            for owner in sorted(unique_owners):
                if pd.notna(owner) and str(owner).strip():
                    color = get_seller_color(owner)
                    legend_elements.append(Rectangle((0,0),1,1, facecolor=color, 
                                                   edgecolor='white', linewidth=1.8,
                                                   label=str(owner).strip(), alpha=0.9))
            
            if legend_elements:
                # Position legend in bottom right to avoid covering Monday
                legend = ax.legend(handles=legend_elements, loc='lower right', 
                                 bbox_to_anchor=(0.98, 0.02),
                                 frameon=True, fancybox=True, shadow=True, 
                                 framealpha=0.96, facecolor='#ffffff',
                                 edgecolor='#d1d5db',
                                 title='Sales Team', fontsize=11,
                                 title_fontsize=13)
                legend.get_title().set_fontweight('700')
                legend.get_title().set_color('#1f2937')
                legend.get_title().set_fontfamily('sans-serif')
                
                # Enhanced legend text styling
                for text in legend.get_texts():
                    text.set_fontweight('600')
                    text.set_color('#374151')
                    text.set_fontfamily('sans-serif')
                
                # Enhanced legend frame styling
                legend.get_frame().set_boxstyle("round,pad=0.5")
                legend.get_frame().set_linewidth(1.5)
    
    # Add beautiful month stats with elegant styling
    if not sub.empty:
        stats_text = f"Total Events: {len(sub)}"
        ax.text(7.05, -0.08, stats_text,
               ha='right', va='bottom', fontsize=13, 
               fontweight='700', color='#374151',
               fontfamily='sans-serif',
               bbox=dict(boxstyle="round,pad=0.4", facecolor='#ffffff', 
                        alpha=0.95, edgecolor='#d1d5db', linewidth=1.5))
    
    outfile = outdir / f"calendar_{year}_{month:02d}.png"
    fig.savefig(outfile, dpi=300, bbox_inches='tight', facecolor='#f8fafc', 
                edgecolor='none', pad_inches=0.4, 
                metadata={'Title': f'Calendar - {mname} {year}', 'Software': 'Encore Dashboard'})
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
    print(f"  Calendar events shown: {filtered_events}, Filtered: {total_filtered} (ICW: {icw_filtered}, Marriott In-House: {marriott_filtered})")


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

    # Handle calendar mode
    if args.calendar:
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        
        print(f"Calendar mode: generating calendar for {calendar.month_name[current_month]} {current_year}")
        
        # Generate calendar
        df = load_events(wb, args.sheet)
        calendar_for_month(df, current_year, current_month, outdir)
        
    # Handle daily mode
    elif args.daily:
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
            sys.exit("Error: --months is required unless using --rolling-window, --weekly, --daily, or --calendar")
            
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
