#!/usr/bin/env python3
"""
monthly_update.py
-----------------
Automated monthly update script for the dashboard.
This script should be run monthly (e.g., via cron) to maintain the rolling 4-month window and update the calendar.

Usage:
    python monthly_update.py

This script will:
1. Generate charts for the next 3 months from current date
2. Generate a professional calendar view for the current month
3. Remove old charts that are no longer needed
4. Optimize images for dashboard display
5. Update the slides manifest

To set up monthly automation on Unix/Linux/macOS:
1. Edit your crontab: crontab -e
2. Add this line to run on the 1st of every month at 6 AM:
   0 6 1 * * cd /path/to/EncoreDashboard && python monthly_update.py

For Windows Task Scheduler:
1. Create a new task
2. Set trigger to monthly on the 1st day
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
log_file = log_dir / f"monthly_update_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def run_dashboard_update():
    """Run the flex_gantt script with rolling window mode."""
    try:
        # Path to the pipeline Excel file
        pipeline_file = Path("pipeline.xlsx")
        
        if not pipeline_file.exists():
            logger.error(f"Pipeline file not found: {pipeline_file}")
            return False
        
        # Run the flex_gantt script with rolling window mode
        cmd = [
            "python3", 
            "flex_gantt.py", 
            str(pipeline_file), 
            "--rolling-window", 
            "--dashboard"
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        logger.info("Rolling window dashboard update completed successfully")
        logger.info(f"Script output: {result.stdout}")
        
        if result.stderr:
            logger.warning(f"Script warnings: {result.stderr}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Rolling window script execution failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in rolling window update: {e}")
        return False


def run_calendar_update():
    """Run the flex_gantt script with calendar mode."""
    try:
        # Path to the pipeline Excel file
        pipeline_file = Path("pipeline.xlsx")
        
        if not pipeline_file.exists():
            logger.error(f"Pipeline file not found: {pipeline_file}")
            return False
        
        # Run the flex_gantt script with calendar mode
        cmd = [
            "python3", 
            "flex_gantt.py", 
            str(pipeline_file), 
            "--calendar", 
            "--dashboard"
        ]
        
        logger.info(f"Running calendar command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        logger.info("Calendar update completed successfully")
        logger.info(f"Calendar output: {result.stdout}")
        
        if result.stderr:
            logger.warning(f"Calendar warnings: {result.stderr}")
        
        return True
        
    except subprocess.CalledProcessError as e:
        logger.error(f"Calendar script execution failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error in calendar update: {e}")
        return False


def main():
    """Main execution function."""
    logger.info("=" * 60)
    logger.info("Starting monthly dashboard and calendar update")
    logger.info("=" * 60)
    
    start_time = datetime.now()
    current_month = start_time.strftime('%B %Y')
    
    logger.info(f"Update date: {current_month}")
    
    # Run rolling window update
    logger.info("\n--- Rolling Window Update ---")
    rolling_success = run_dashboard_update()
    
    # Run calendar update
    logger.info("\n--- Calendar Update ---")
    calendar_success = run_calendar_update()
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    # Report results
    if rolling_success and calendar_success:
        logger.info(f"\n✅ Monthly update completed successfully in {duration}")
        logger.info("Dashboard is now updated with:")
        logger.info("  • Current month + next 3 months of Gantt charts (rolling window)")
        logger.info(f"  • {current_month} calendar view")
        
        # Auto-commit and push changes to GitHub
        logger.info("\n--- Auto-committing to GitHub ---")
        try:
            from git_auto_commit import auto_commit_and_push
            if auto_commit_and_push(f"Auto-update: Monthly dashboard update - {current_month}"):
                logger.info("✅ Changes pushed to GitHub successfully")
                logger.info("All screens will receive updates within minutes")
            else:
                logger.warning("⚠️  Failed to push changes to GitHub")
                logger.warning("Manual git commit and push may be required")
        except Exception as e:
            logger.error(f"Error during auto-commit: {e}")
            logger.warning("Manual git commit and push required")
            
    elif rolling_success and not calendar_success:
        logger.warning(f"\n⚠️  Partial success after {duration}")
        logger.warning("Rolling window updated successfully, but calendar update failed")
        sys.exit(1)
    elif not rolling_success and calendar_success:
        logger.warning(f"\n⚠️  Partial success after {duration}")
        logger.warning("Calendar updated successfully, but rolling window update failed")
        sys.exit(1)
    else:
        logger.error(f"\n❌ Monthly update failed after {duration}")
        logger.error("Both rolling window and calendar updates failed")
        sys.exit(1)
    
    logger.info("=" * 60)


if __name__ == "__main__":
    main() 