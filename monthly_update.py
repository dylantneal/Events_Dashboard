#!/usr/bin/env python3
"""
monthly_update.py
-----------------
Automated monthly update script for the dashboard.
This script should be run monthly (e.g., via cron) to maintain the rolling 3-month window.

Usage:
    python monthly_update.py

This script will:
1. Generate charts for the next 3 months from current date
2. Remove old charts that are no longer needed
3. Optimize images for dashboard display
4. Update the slides manifest

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
        
        logger.info("Dashboard update completed successfully")
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
    logger.info("Starting monthly dashboard update")
    logger.info("=" * 50)
    
    start_time = datetime.now()
    
    success = run_dashboard_update()
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    if success:
        logger.info(f"Monthly update completed successfully in {duration}")
        logger.info("Dashboard is now updated with the next 3 months of events")
    else:
        logger.error(f"Monthly update failed after {duration}")
        sys.exit(1)
    
    logger.info("=" * 50)


if __name__ == "__main__":
    main() 