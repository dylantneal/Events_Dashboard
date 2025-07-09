#!/usr/bin/env python3
"""
test_automation.py
------------------
Comprehensive test script to verify dashboard automation is working properly.
Run this to check:
1. Cron job configuration
2. Git sync functionality
3. Cloud sync for announcements
4. Chart generation
"""

import subprocess
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Colors for output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_status(status, message):
    """Print colored status messages."""
    if status == "success":
        print(f"{GREEN}✅ {message}{RESET}")
    elif status == "error":
        print(f"{RED}❌ {message}{RESET}")
    elif status == "warning":
        print(f"{YELLOW}⚠️  {message}{RESET}")
    elif status == "info":
        print(f"{BLUE}ℹ️  {message}{RESET}")

def test_cron_jobs():
    """Test if cron jobs are properly configured."""
    print("\n" + "="*50)
    print("TESTING CRON JOB CONFIGURATION")
    print("="*50)
    
    try:
        result = subprocess.run(['crontab', '-l'], capture_output=True, text=True)
        if result.returncode == 0:
            cron_content = result.stdout
            
            # Check for required cron jobs
            required_jobs = {
                'daily': '0 0 * * * cd',
                'weekly': '0 0 * * 1 cd',
                'monthly': '0 6 1 * * cd'
            }
            
            for job_type, pattern in required_jobs.items():
                if pattern in cron_content and f'{job_type}_update.py' in cron_content:
                    print_status("success", f"{job_type.capitalize()} cron job is configured")
                else:
                    print_status("error", f"{job_type.capitalize()} cron job is MISSING")
                    
            # Show next run times
            print("\n📅 Next scheduled runs:")
            now = datetime.now()
            
            # Daily - next midnight
            next_daily = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            print(f"   Daily: {next_daily.strftime('%Y-%m-%d %H:%M')} (every midnight)")
            
            # Weekly - next Monday
            days_until_monday = (7 - now.weekday()) % 7
            if days_until_monday == 0 and now.hour >= 0:
                days_until_monday = 7
            next_weekly = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=days_until_monday)
            print(f"   Weekly: {next_weekly.strftime('%Y-%m-%d %H:%M')} (every Monday)")
            
            # Monthly - 1st of next month
            if now.day == 1 and now.hour < 6:
                next_monthly = now.replace(hour=6, minute=0, second=0, microsecond=0)
            else:
                next_month = now.replace(day=1) + timedelta(days=32)
                next_monthly = next_month.replace(day=1, hour=6, minute=0, second=0, microsecond=0)
            print(f"   Monthly: {next_monthly.strftime('%Y-%m-%d %H:%M')} (1st of each month)")
            
        else:
            print_status("error", "No cron jobs found!")
            
    except Exception as e:
        print_status("error", f"Failed to check cron jobs: {e}")

def test_git_sync():
    """Test if git sync is working properly."""
    print("\n" + "="*50)
    print("TESTING GIT SYNCHRONIZATION")
    print("="*50)
    
    try:
        # Check git status
        result = subprocess.run(['git', 'status', '--porcelain'], capture_output=True, text=True)
        if result.stdout.strip():
            print_status("warning", "Uncommitted changes in repository")
        else:
            print_status("success", "Repository is clean")
            
        # Check remote configuration
        result = subprocess.run(['git', 'remote', '-v'], capture_output=True, text=True)
        if 'github.com' in result.stdout:
            print_status("success", "GitHub remote is configured")
        else:
            print_status("error", "GitHub remote is NOT configured")
            
        # Test push access
        result = subprocess.run(['git', 'push', '--dry-run', 'origin', 'main'], 
                              capture_output=True, text=True, stderr=subprocess.STDOUT)
        if result.returncode == 0 or 'Everything up-to-date' in result.stdout:
            print_status("success", "Git push access confirmed")
        else:
            print_status("error", "Cannot push to GitHub - check SSH keys")
            
        # Check recent commits
        result = subprocess.run(['git', 'log', '--oneline', '-5'], capture_output=True, text=True)
        print("\n📝 Recent commits:")
        for line in result.stdout.strip().split('\n'):
            if 'Auto-update' in line:
                print(f"   {GREEN}{line}{RESET}")
            else:
                print(f"   {line}")
                
    except Exception as e:
        print_status("error", f"Git test failed: {e}")

def test_cloud_sync():
    """Test if cloud sync for announcements is working."""
    print("\n" + "="*50)
    print("TESTING CLOUD SYNC (ANNOUNCEMENTS)")
    print("="*50)
    
    try:
        # Read config.js to get cloud sync settings
        config_path = Path('config.js')
        if not config_path.exists():
            print_status("error", "config.js not found!")
            return
            
        config_content = config_path.read_text()
        
        # Extract cloud sync URL (basic parsing)
        if 'cloudSync:' in config_content and 'enabled: true' in config_content:
            print_status("success", "Cloud sync is enabled in config.js")
            
            # Try to find the URL
            import re
            url_match = re.search(r"url:\s*'([^']+)'", config_content)
            if url_match:
                cloud_url = url_match.group(1)
                print_status("info", f"Cloud URL: {cloud_url}")
                
                # Test the URL
                try:
                    response = requests.get(cloud_url, timeout=5)
                    if response.status_code == 200:
                        print_status("success", "Cloud sync URL is accessible")
                        data = response.json()
                        if 'record' in data:
                            announcements = data.get('record', {}).get('announcements', [])
                            print_status("info", f"Current announcements in cloud: {len(announcements)}")
                        else:
                            print_status("warning", "Cloud storage format unexpected")
                    else:
                        print_status("error", f"Cloud sync URL returned status {response.status_code}")
                except requests.exceptions.RequestException as e:
                    print_status("error", f"Cannot reach cloud sync URL: {e}")
            else:
                print_status("error", "Cloud sync URL not found in config.js")
        else:
            print_status("error", "Cloud sync is NOT enabled in config.js")
            
    except Exception as e:
        print_status("error", f"Cloud sync test failed: {e}")

def test_recent_logs():
    """Check recent log files for errors."""
    print("\n" + "="*50)
    print("CHECKING RECENT LOGS")
    print("="*50)
    
    log_dir = Path('logs')
    if not log_dir.exists():
        print_status("warning", "No logs directory found")
        return
        
    # Get most recent log files
    log_files = sorted(log_dir.glob('*.log'), key=lambda x: x.stat().st_mtime, reverse=True)[:5]
    
    if not log_files:
        print_status("warning", "No log files found")
        return
        
    errors_found = False
    for log_file in log_files:
        with open(log_file, 'r') as f:
            content = f.read()
            error_count = content.count('ERROR')
            warning_count = content.count('WARNING')
            
            if error_count > 0:
                print_status("error", f"{log_file.name}: {error_count} errors, {warning_count} warnings")
                errors_found = True
                # Show last error
                lines = content.split('\n')
                for line in reversed(lines):
                    if 'ERROR' in line:
                        print(f"     Last error: {line[:100]}...")
                        break
            elif warning_count > 0:
                print_status("warning", f"{log_file.name}: {warning_count} warnings")
            else:
                print_status("success", f"{log_file.name}: No errors")
    
    if not errors_found:
        print_status("success", "No errors in recent logs")

def test_chart_generation():
    """Test if charts can be generated successfully."""
    print("\n" + "="*50)
    print("TESTING CHART GENERATION")
    print("="*50)
    
    # Check if pipeline.xlsx exists
    if not Path('pipeline.xlsx').exists():
        print_status("error", "pipeline.xlsx not found!")
        return
        
    # Test daily chart generation
    print_status("info", "Testing daily chart generation...")
    result = subprocess.run(['python3', 'flex_gantt.py', 'pipeline.xlsx', '--daily', '--test'], 
                          capture_output=True, text=True)
    if result.returncode == 0:
        print_status("success", "Daily chart generation works")
    else:
        print_status("error", "Daily chart generation failed")
        
    # Check slides directory
    slides_dir = Path('slides')
    if slides_dir.exists():
        png_files = list(slides_dir.glob('*.png'))
        print_status("info", f"Found {len(png_files)} chart files in slides/")
        
        # Check file ages
        now = datetime.now()
        for png_file in png_files:
            age = now - datetime.fromtimestamp(png_file.stat().st_mtime)
            if age.days > 7:
                print_status("warning", f"{png_file.name} is {age.days} days old")

def main():
    """Run all tests."""
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}DASHBOARD AUTOMATION TEST SUITE{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    print(f"Test Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Run all tests
    test_cron_jobs()
    test_git_sync()
    test_cloud_sync()
    test_recent_logs()
    test_chart_generation()
    
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}TEST COMPLETE{RESET}")
    print(f"{BLUE}{'='*60}{RESET}")
    
    print("\n📋 SUMMARY:")
    print("If all tests passed, your automation is rock solid!")
    print("If any tests failed, follow the error messages to fix them.")
    
    print("\n🔧 TROUBLESHOOTING TIPS:")
    print("1. For cron issues: Run './setup_cron.sh' and choose option 6")
    print("2. For git sync issues: Check SSH keys and git remote configuration")
    print("3. For cloud sync issues: Verify config.js has correct JSONBin URL")
    print("4. For chart generation issues: Check pipeline.xlsx and Python dependencies")

if __name__ == "__main__":
    main() 