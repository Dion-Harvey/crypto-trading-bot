#!/usr/bin/env python3
"""
Simple Daily Trade Log Sync (No External Dependencies)
Automated daily execution of trade log synchronization before midnight
"""

import os
import sys
import time
import threading
import subprocess
from datetime import datetime, timedelta
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_sync.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class SimpleDailySync:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.fetch_script = self.script_dir / 'fetch_recent_trades.py'
        self.sync_script = self.script_dir / 'sync_trade_logs.py'
        self.running = False
        
    def run_fetch_trades(self):
        """Execute the fetch_recent_trades.py script"""
        try:
            logger.info("[SYNC] Starting daily trade log fetch...")
            
            # Run fetch_recent_trades.py
            result = subprocess.run([
                sys.executable, str(self.fetch_script)
            ], capture_output=True, text=True, cwd=str(self.script_dir), encoding='utf-8')
            
            if result.returncode == 0:
                logger.info("[SUCCESS] Trade log fetch completed successfully")
                logger.info(f"Output: {result.stdout}")
            else:
                logger.error(f"[ERROR] Trade log fetch failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Error running fetch script: {e}")
            return False
            
        return True
    
    def run_sync_logs(self):
        """Execute the sync_trade_logs.py script"""
        try:
            logger.info("[SYNC] Starting log synchronization...")
            
            # Run sync_trade_logs.py
            result = subprocess.run([
                sys.executable, str(self.sync_script)
            ], capture_output=True, text=True, cwd=str(self.script_dir), encoding='utf-8')
            
            if result.returncode == 0:
                logger.info("[SUCCESS] Log synchronization completed successfully")
                logger.info(f"Output: {result.stdout}")
            else:
                logger.error(f"[ERROR] Log synchronization failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"[ERROR] Error running sync script: {e}")
            return False
            
        return True
    
    def daily_sync_job(self):
        """Main daily sync job that runs both scripts"""
        current_time = datetime.now()
        logger.info(f"[DAILY] Daily sync job started at {current_time}")
        
        # Step 1: Fetch recent trades from Binance
        fetch_success = self.run_fetch_trades()
        
        # Step 2: Sync logs between locations
        sync_success = self.run_sync_logs()
        
        # Report results
        if fetch_success and sync_success:
            logger.info("[SUCCESS] Daily sync completed successfully!")
            logger.info("[INFO] Trade logs are now up-to-date and synchronized")
        else:
            logger.error("[ERROR] Daily sync encountered errors - check logs above")
            
        # Add separator for next day
        logger.info("=" * 60)
        
    def calculate_seconds_until_time(self, target_hour, target_minute):
        """Calculate seconds until target time"""
        now = datetime.now()
        target_time = now.replace(hour=target_hour, minute=target_minute, second=0, microsecond=0)
        
        # If target time has passed today, schedule for tomorrow
        if target_time <= now:
            target_time += timedelta(days=1)
            
        return (target_time - now).total_seconds()
    
    def schedule_daily_sync(self):
        """Schedule the daily sync to run at 11:55 PM"""
        def run_scheduler():
            while self.running:
                # Calculate seconds until 11:55 PM
                seconds_until_sync = self.calculate_seconds_until_time(23, 55)
                
                logger.info(f"[SCHEDULE] Next sync scheduled in {seconds_until_sync/3600:.1f} hours")
                
                # Wait until it's time
                time.sleep(seconds_until_sync)
                
                if self.running:  # Check if still running after sleep
                    self.daily_sync_job()
        
        # Start scheduler in a separate thread
        scheduler_thread = threading.Thread(target=run_scheduler, daemon=True)
        scheduler_thread.start()
        
    def start_scheduler(self):
        """Start the daily scheduler"""
        self.running = True
        
        logger.info("[SCHEDULE] Daily sync scheduler started")
        logger.info("[SCHEDULE] Scheduled to run daily at 11:55 PM (5 minutes before midnight)")
        logger.info("[INFO] This will fetch recent trades and synchronize logs")
        logger.info("[INFO] Press Ctrl+C to stop the scheduler")
        
        # Schedule the daily sync
        self.schedule_daily_sync()
        
        try:
            while self.running:
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("[STOP] Daily sync scheduler stopped by user")
            self.running = False

def main():
    """Main function to run the scheduler"""
    scheduler = SimpleDailySync()
    
    # Check if scripts exist
    if not scheduler.fetch_script.exists():
        logger.error(f"[ERROR] fetch_recent_trades.py not found at {scheduler.fetch_script}")
        sys.exit(1)
        
    if not scheduler.sync_script.exists():
        logger.error(f"[ERROR] sync_trade_logs.py not found at {scheduler.sync_script}")
        sys.exit(1)
    
    # Provide options
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            logger.info("[TEST] Running test sync...")
            scheduler.daily_sync_job()
            sys.exit(0)
        elif sys.argv[1] == "--schedule":
            scheduler.start_scheduler()
        elif sys.argv[1] == "--help":
            print("Daily Sync Scheduler Options:")
            print("  --test     Run sync once immediately (for testing)")
            print("  --schedule Start the daily scheduler")
            print("  --help     Show this help message")
            sys.exit(0)
    else:
        print("Daily Sync Scheduler")
        print("Usage: python simple_daily_sync.py [--test|--schedule|--help]")
        print("Use --test to run once, --schedule to start daily automation")

if __name__ == "__main__":
    main()
