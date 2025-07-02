#!/usr/bin/env python3
"""
calendar_update.py
------------------
Automated monthly calendar update script for the professional calendar dashboard.
This script should be run monthly (every 1st at midnight) to update the calendar view.

Usage:
    python calendar_update.py

This script will:
1. Generate a professional calendar view for the current month
2. Remove old calendar files that are no longer current
3. Optimize images for dashboard display
4. Update the slides manifest

To set up monthly automation on Unix/Linux/macOS:
1. Edit your crontab: crontab -e
2. Add this line to run on the 1st of every month at midnight:
   0 0 1 * * cd /path/to/EncoreDashboard && python3 calendar_update.py
3. For redundancy, also run on the 2nd at 12:05 AM:
   5 0 2 * * cd /path/to/EncoreDashboard && python3 calendar_update.py

For Windows Task Scheduler:
1. Create a new task
2. Set trigger to monthly on the 1st and 2nd day
3. Set action to run this script
"""

import sys
import subprocess
import logging
from pathlib import Path
from datetime import datetime

# Set up logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)
log_file = log_dir / f"calendar_update_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def cleanup_old_calendar_files():
    """Remove old calendar files that are not from the current month."""
    try:
        slides_dir = Path("slides")
        if not slides_dir.exists():
            logger.info("Slides directory does not exist, nothing to clean up")
            return
        
        # Get all calendar files
        calendar_files = list(slides_dir.glob("calendar_*.png"))
        
        if not calendar_files:
            logger.info("No existing calendar files to clean up")
            return
        
        # Get current month for comparison
        current_date = datetime.now()
        current_filename = f"calendar_{current_date.strftime('%Y_%m')}.png"
        
        # Remove old calendar files
        removed_count = 0
        for calendar_file in calendar_files:
            # Keep the current month's calendar
            if calendar_file.name != current_filename:
                logger.info(f"Removing old calendar: {calendar_file.name}")
                calendar_file.unlink()
                removed_count += 1
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old calendar file(s)")
        else:
            logger.info("No old calendar files to remove")
            
    except Exception as e:
        logger.error(f"Error cleaning up old calendar files: {e}")


def run_calendar_update():
    """Run the flex_gantt script with calendar mode."""
    try:
        # Path to the pipeline Excel file
        pipeline_file = Path("pipeline.xlsx")
        
        if not pipeline_file.exists():
            logger.error(f"Pipeline file not found: {pipeline_file}")
            return False
        
        # Clean up old calendar files before generating new one
        cleanup_old_calendar_files()
        
        # Run the flex_gantt script with calendar mode
        cmd = [
            "python3", 
            "flex_gantt.py", 
            str(pipeline_file), 
            "--calendar", 
            "--dashboard"
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        logger.info("Calendar update completed successfully")
        logger.info(f"Script output: {result.stdout}")
        
        if result.stderr:
            logger.warning(f"Script warnings: {result.stderr}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Script execution failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False


def main():
    """Main execution function."""
    logger.info("=" * 50)
    logger.info("Starting monthly calendar update")
    logger.info("=" * 50)
    
    start_time = datetime.now()
    current_month = start_time.strftime('%B %Y')
    
    logger.info(f"Generating calendar for: {current_month}")
    
    success = run_calendar_update()
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    if success:
        logger.info(f"Calendar update completed successfully in {duration}")
        logger.info(f"Dashboard calendar for {current_month} is now updated")
        
        # Auto-commit and push changes to GitHub
        logger.info("\n--- Auto-committing to GitHub ---")
        try:
            from git_auto_commit import auto_commit_and_push
            if auto_commit_and_push(f"Auto-update: Calendar view - {current_month}"):
                logger.info("✅ Changes pushed to GitHub successfully")
                logger.info("All screens will receive updates within minutes")
            else:
                logger.warning("⚠️  Failed to push changes to GitHub")
                logger.warning("Manual git commit and push may be required")
        except Exception as e:
            logger.error(f"Error during auto-commit: {e}")
            logger.warning("Manual git commit and push required")
    else:
        logger.error(f"Calendar update failed after {duration}")
        sys.exit(1)
    
    logger.info("=" * 50)


if __name__ == "__main__":
    main() 