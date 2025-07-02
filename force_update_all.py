#!/usr/bin/env python3
"""
force_update_all.py
-------------------
Force regenerate all dashboard content immediately.
Useful for testing or when you need all charts updated right away.

Usage:
    python3 force_update_all.py
"""

import subprocess
import sys
from datetime import datetime
from pathlib import Path


def run_script(script_name, description):
    """Run a Python script and return success status."""
    print(f"\n{'='*60}")
    print(f"Running {description}...")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            ["python3", script_name],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"Error: {e.stderr}")
        return False


def main():
    """Run all update scripts to force refresh all content."""
    print(f"\nFORCE UPDATE ALL DASHBOARD CONTENT")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    # Check if required files exist
    required_files = ["daily_update.py", "weekly_update.py", "monthly_update.py", "calendar_update.py"]
    for file in required_files:
        if not Path(file).exists():
            print(f"❌ Error: {file} not found!")
            sys.exit(1)
    
    # Run all updates
    success_count = 0
    total_count = 4
    
    # Daily update (Today's events)
    if run_script("daily_update.py", "Daily Update (Happening Today)"):
        success_count += 1
    
    # Weekly update (This week's events)
    if run_script("weekly_update.py", "Weekly Update (Happening This Week)"):
        success_count += 1
    
    # Monthly update (3-month rolling window)
    if run_script("monthly_update.py", "Monthly Update (3-Month Window + Calendar)"):
        success_count += 1
    
    # Final summary
    print(f"\n{'='*60}")
    print(f"SUMMARY: {success_count}/{total_count} updates completed successfully")
    print(f"Finished at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    if success_count == total_count:
        print("✅ All dashboard content has been updated!")
        print("Reload your browser to see the latest charts.")
    else:
        print("⚠️  Some updates failed. Check the logs for details.")
        sys.exit(1)


if __name__ == "__main__":
    main() 