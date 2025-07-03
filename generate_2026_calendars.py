#!/usr/bin/env python3
"""
Generate calendar views for January through June 2026
"""

import subprocess
import sys
from pathlib import Path

def main():
    # Months to generate (January through June)
    months = [1, 2, 3, 4, 5, 6]
    year = 2026
    
    # Output directory
    outdir = Path("calendars_2026")
    outdir.mkdir(exist_ok=True)
    
    # Load events once and generate all calendars
    print(f"Generating calendar views for January through June {year}...")
    
    # We need to modify flex_gantt.py to handle calendar generation for specific months
    # Currently it only generates for the current month
    # Let's create a temporary modified version
    
    # Read the original flex_gantt.py
    with open("flex_gantt.py", "r") as f:
        flex_gantt_content = f.read()
    
    # Create a modified version that accepts month parameter for calendar generation
    # Replace the calendar mode handling to accept month parameter
    modified_content = flex_gantt_content.replace(
        """# Handle calendar mode
    if args.calendar:
        current_date = datetime.now()
        current_month = current_date.month
        current_year = current_date.year
        
        print(f"Calendar mode: generating calendar for {calendar.month_name[current_month]} {current_year}")
        
        # Clean up old calendar files before generating new one
        cleanup_old_calendars(outdir)
        
        # Generate calendar
        df = load_events(wb, args.sheet)
        calendar_for_month(df, current_year, current_month, outdir)""",
        """# Handle calendar mode
    if args.calendar:
        # If months are provided, generate calendars for those months
        if args.months:
            df = load_events(wb, args.sheet)
            year = args.year  # Use the provided year
            
            for month in args.months:
                if isinstance(month, str):
                    month = month_str_to_int(month)
                
                print(f"Calendar mode: generating calendar for {calendar.month_name[month]} {year}")
                calendar_for_month(df, year, month, outdir)
        else:
            # Default to current month if no months specified
            current_date = datetime.now()
            current_month = current_date.month
            current_year = current_date.year
            
            print(f"Calendar mode: generating calendar for {calendar.month_name[current_month]} {current_year}")
            
            # Clean up old calendar files before generating new one
            cleanup_old_calendars(outdir)
            
            # Generate calendar
            df = load_events(wb, args.sheet)
            calendar_for_month(df, current_year, current_month, outdir)"""
    )
    
    # Write the modified version
    with open("flex_gantt_temp.py", "w") as f:
        f.write(modified_content)
    
    # Run the modified script
    cmd = [
        "python3", 
        "flex_gantt_temp.py", 
        "pipeline.xlsx", 
        "--calendar",
        "--months", "1", "2", "3", "4", "5", "6",
        "--year", "2026",
        "--outdir", "calendars_2026"
    ]
    
    print(f"Running command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print(f"Warnings: {result.stderr}")
            
        # Clean up temp file
        Path("flex_gantt_temp.py").unlink()
        
        print("\nCalendar generation complete!")
        print(f"Calendar images saved in: {outdir}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        print(f"Output: {e.stdout}")
        print(f"Error: {e.stderr}")
        # Clean up temp file
        if Path("flex_gantt_temp.py").exists():
            Path("flex_gantt_temp.py").unlink()
        sys.exit(1)

if __name__ == "__main__":
    main() 