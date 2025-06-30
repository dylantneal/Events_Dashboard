#!/usr/bin/env python3
"""
daily_update.py
---------------
Automated daily update script for the "Happening Today" dashboard.
This script should be run daily (every midnight) to update the daily chart.

Usage:
    python daily_update.py

This script will:
1. Generate a "Happening Today" chart for the current day (midnight to 11:59 PM)
2. Remove old daily charts that are no longer current
3. Optimize images for dashboard display
4. Update the slides manifest

To set up daily automation on Unix/Linux/macOS:
1. Edit your crontab: crontab -e
2. Add this line to run every day at midnight:
   0 0 * * * cd /path/to/EncoreDashboard && python3 daily_update.py

For Windows Task Scheduler:
1. Create a new task
2. Set trigger to daily
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
log_file = log_dir / f"daily_update_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def cleanup_old_daily_charts():
    """Remove old daily chart files that are not from today."""
    try:
        slides_dir = Path("slides")
        if not slides_dir.exists():
            logger.info("Slides directory does not exist, nothing to clean up")
            return
        
        # Get all daily chart files
        daily_charts = list(slides_dir.glob("gantt_daily_*.png"))
        
        if not daily_charts:
            logger.info("No existing daily charts to clean up")
            return
        
        # Get today's date for comparison
        current_date = datetime.now()
        today_filename = f"gantt_daily_{current_date.strftime('%Y_%m_%d')}.png"
        
        # Remove old daily charts
        removed_count = 0
        for chart in daily_charts:
            if chart.name != today_filename:
                logger.info(f"Removing old daily chart: {chart.name}")
                chart.unlink()
                removed_count += 1
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old daily chart(s)")
        else:
            logger.info("No old daily charts to remove")
            
    except Exception as e:
        logger.error(f"Error cleaning up old daily charts: {e}")


def run_daily_update():
    """Run the flex_gantt script with daily mode."""
    try:
        # Path to the pipeline Excel file
        pipeline_file = Path("pipeline.xlsx")
        
        if not pipeline_file.exists():
            logger.error(f"Pipeline file not found: {pipeline_file}")
            return False
        
        # Clean up old daily charts before generating new one
        cleanup_old_daily_charts()
        
        # Run the flex_gantt script with daily mode
        cmd = [
            "python3", 
            "flex_gantt.py", 
            str(pipeline_file), 
            "--daily", 
            "--dashboard"
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        logger.info("Daily dashboard update completed successfully")
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
    logger.info("Starting daily dashboard update")
    logger.info("=" * 50)
    
    start_time = datetime.now()
    
    success = run_daily_update()
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    if success:
        logger.info(f"Daily update completed successfully in {duration}")
        logger.info("Dashboard 'Happening Today' chart is now updated")
    else:
        logger.error(f"Daily update failed after {duration}")
        sys.exit(1)
    
    logger.info("=" * 50)


if __name__ == "__main__":
    main() 