#!/usr/bin/env python3
"""
git_auto_commit.py
------------------
Automatically commits and pushes generated images to GitHub.
Called by the update scripts after image generation.
"""

import subprocess
import sys
import logging
from pathlib import Path
from datetime import datetime

# Set up logging
logger = logging.getLogger(__name__)


def run_command(cmd, cwd=None):
    """Run a shell command and return success status."""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            cwd=cwd,
            check=True
        )
        logger.info(f"Command succeeded: {cmd}")
        logger.debug(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {cmd}")
        logger.error(f"Error: {e.stderr}")
        return False


def auto_commit_and_push(commit_message=None):
    """Automatically commit and push changes to GitHub."""
    try:
        # Default commit message if none provided
        if not commit_message:
            now = datetime.now()
            commit_message = f"Auto-update dashboard images - {now.strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Get the repository root
        repo_root = Path.cwd()
        
        # Check if we're in a git repository
        if not (repo_root / '.git').exists():
            logger.error("Not in a git repository")
            return False
        
        # Add all changes in slides directory
        if not run_command("git add slides/*", cwd=repo_root):
            return False
        
        # Check if there are changes to commit
        result = subprocess.run(
            "git status --porcelain slides/",
            shell=True,
            capture_output=True,
            text=True,
            cwd=repo_root
        )
        
        if not result.stdout.strip():
            logger.info("No changes to commit")
            return True
        
        # Commit changes
        if not run_command(f'git commit -m "{commit_message}"', cwd=repo_root):
            return False
        
        # Push to origin
        if not run_command("git push origin main", cwd=repo_root):
            # Try to pull and merge first, then push again
            logger.info("Push failed, trying to pull and merge...")
            if run_command("git pull origin main --rebase", cwd=repo_root):
                if run_command("git push origin main", cwd=repo_root):
                    logger.info("Successfully pushed after rebase")
                    return True
            return False
        
        logger.info("Successfully committed and pushed changes")
        return True
        
    except Exception as e:
        logger.error(f"Unexpected error in auto_commit_and_push: {e}")
        return False


def main():
    """Main function for standalone execution."""
    import argparse
    
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Auto-commit and push dashboard updates")
    parser.add_argument(
        "--message", "-m",
        help="Custom commit message",
        default=None
    )
    parser.add_argument(
        "--type",
        choices=["monthly", "weekly", "daily", "calendar"],
        help="Type of update for commit message",
        default=None
    )
    
    args = parser.parse_args()
    
    # Set up logging for standalone execution
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Generate commit message based on type
    if args.type and not args.message:
        update_types = {
            "monthly": "Monthly rolling window and calendar update",
            "weekly": "Weekly 'Happening This Week' update",
            "daily": "Daily 'Happening Today' update",
            "calendar": "Monthly calendar view update"
        }
        args.message = f"Auto-update: {update_types.get(args.type, 'Dashboard update')}"
    
    # Run the auto-commit
    success = auto_commit_and_push(args.message)
    
    if success:
        print("✅ Changes committed and pushed successfully")
        sys.exit(0)
    else:
        print("❌ Failed to commit and push changes")
        sys.exit(1)


if __name__ == "__main__":
    main() 