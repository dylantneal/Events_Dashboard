#!/usr/bin/env python3
"""
weekly_update.py
----------------
Automated weekly update script for the "Happening This Week" dashboard.
This script should be run weekly (every Monday at midnight) to update the weekly chart.

Usage:
    python weekly_update.py

This script will:
1. Generate a "Happening This Week" chart for the current week (Monday to Sunday)
2. Remove old weekly charts that are no longer current
3. Optimize images for dashboard display
4. Update the slides manifest

To set up weekly automation on Unix/Linux/macOS:
1. Edit your crontab: crontab -e
2. Add this line to run every Monday at midnight:
   0 0 * * 1 cd /path/to/EncoreDashboard && python3 weekly_update.py

For Windows Task Scheduler:
1. Create a new task
2. Set trigger to weekly on Monday
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
log_file = log_dir / f"weekly_update_{datetime.now().strftime('%Y%m%d')}.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


def cleanup_old_weekly_charts():
    """Remove old weekly chart files that are not from the current week."""
    try:
        slides_dir = Path("slides")
        if not slides_dir.exists():
            logger.info("Slides directory does not exist, nothing to clean up")
            return
        
        # Get all weekly chart files
        weekly_charts = list(slides_dir.glob("gantt_weekly_*.png"))
        
        if not weekly_charts:
            logger.info("No existing weekly charts to clean up")
            return
        
        # Get current week's Monday date for comparison
        from datetime import datetime, timedelta
        current_date = datetime.now()
        days_since_monday = current_date.weekday()
        current_monday = current_date - timedelta(days=days_since_monday)
        current_week_filename = f"gantt_weekly_{current_monday.strftime('%Y_%m_%d')}.png"
        
        # Remove old weekly charts
        removed_count = 0
        for chart in weekly_charts:
            if chart.name != current_week_filename:
                logger.info(f"Removing old weekly chart: {chart.name}")
                chart.unlink()
                removed_count += 1
        
        if removed_count > 0:
            logger.info(f"Cleaned up {removed_count} old weekly chart(s)")
        else:
            logger.info("No old weekly charts to remove")
            
    except Exception as e:
        logger.error(f"Error cleaning up old weekly charts: {e}")


def run_weekly_update():
    """Run the flex_gantt script with weekly mode."""
    try:
        # Path to the pipeline Excel file
        pipeline_file = Path("pipeline.xlsx")
        
        if not pipeline_file.exists():
            logger.error(f"Pipeline file not found: {pipeline_file}")
            return False
        
        # Clean up old weekly charts before generating new one
        cleanup_old_weekly_charts()
        
        # Run the flex_gantt script with weekly mode
        cmd = [
            "python3", 
            "flex_gantt.py", 
            str(pipeline_file), 
            "--weekly", 
            "--dashboard"
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True
        )
        
        logger.info("Weekly dashboard update completed successfully")
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
    logger.info("Starting weekly dashboard update")
    logger.info("=" * 50)
    
    start_time = datetime.now()
    
    success = run_weekly_update()
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    if success:
        logger.info(f"Weekly update completed successfully in {duration}")
        logger.info("Dashboard 'Happening This Week' chart is now updated")
    else:
        logger.error(f"Weekly update failed after {duration}")
        sys.exit(1)
    
    logger.info("=" * 50)


if __name__ == "__main__":
    main() 