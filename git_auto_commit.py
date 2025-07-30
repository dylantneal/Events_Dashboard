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
import time

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
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        logger.error(f"Command failed: {cmd}")
        logger.error(f"Error: {e.stderr}")
        return False, e.stderr


def auto_commit_and_push(commit_message=None):
    """Automatically commit and push changes to GitHub with better conflict handling."""
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
        
        # First, pull any remote changes to avoid conflicts
        logger.info("Pulling latest changes from remote...")
        success, output = run_command("git pull origin main --rebase", cwd=repo_root)
        if not success:
            logger.warning("Pull failed, but continuing with commit...")
        
        # Add all changes in slides directory
        logger.info("Adding slide changes...")
        if not run_command("git add slides/*", cwd=repo_root)[0]:
            logger.error("Failed to add slides directory")
            return False
        
        # Also add any other relevant files that might exist
        additional_files = ["slides/slides.json", "config.js"]
        for file in additional_files:
            if (repo_root / file).exists():
                run_command(f"git add {file}", cwd=repo_root)
                logger.info(f"Added {file}")
            else:
                logger.debug(f"File {file} doesn't exist, skipping")
        
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
        logger.info(f"Committing changes with message: {commit_message}")
        if not run_command(f'git commit -m "{commit_message}"', cwd=repo_root)[0]:
            logger.error("Failed to commit changes")
            return False
        
        # Push to origin with retry logic
        max_retries = 3
        for attempt in range(max_retries):
            logger.info(f"Pushing to GitHub (attempt {attempt + 1}/{max_retries})...")
            success, output = run_command("git push origin main", cwd=repo_root)
            
            if success:
                logger.info("Successfully pushed changes to GitHub")
                return True
            
            if attempt < max_retries - 1:
                logger.info("Push failed, pulling and retrying...")
                # Pull and rebase before retrying
                pull_success, pull_output = run_command("git pull origin main --rebase", cwd=repo_root)
                if not pull_success:
                    logger.warning("Pull failed during retry, but continuing...")
                
                # Wait a bit before retrying
                time.sleep(2)
            else:
                logger.error("Failed to push after all retries")
                return False
        
        return False
        
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
        now = datetime.now()
        update_types = {
            "monthly": f"Monthly 4-month rolling window and calendar update - {now.strftime('%B %Y')}",
            "weekly": f"Weekly 'Happening This Week' update - {now.strftime('%Y-%m-%d')}",
            "daily": f"Daily 'Happening Today' update - {now.strftime('%A, %B %d, %Y')}",
            "calendar": f"Monthly calendar view update - {now.strftime('%B %Y')}"
        }
        args.message = f"Auto-update: {update_types.get(args.type, 'Dashboard update')}"
    
    # Run the auto-commit
    success = auto_commit_and_push(args.message)
    
    if success:
        print("✅ Changes committed and pushed successfully")
        print("🌐 All connected devices will receive updates within minutes")
        sys.exit(0)
    else:
        print("❌ Failed to commit and push changes")
        print("🔧 Manual intervention may be required")
        sys.exit(1)


if __name__ == "__main__":
    main() 