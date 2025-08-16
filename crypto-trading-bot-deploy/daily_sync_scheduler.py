#!/usr/bin/env python3
"""
Daily Trade Log Sync Scheduler
Automated daily execution of trade log synchronization before midnight
"""

import os
import sys
import time
import schedule
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

class DailySyncScheduler:
    def __init__(self):
        self.script_dir = Path(__file__).parent
        self.fetch_script = self.script_dir / 'fetch_recent_trades.py'
        self.sync_script = self.script_dir / 'sync_trade_logs.py'
        
    def run_fetch_trades(self):
        """Execute the fetch_recent_trades.py script"""
        try:
            logger.info("🔄 Starting daily trade log fetch...")
            
            # Run fetch_recent_trades.py
            result = subprocess.run([
                sys.executable, str(self.fetch_script)
            ], capture_output=True, text=True, cwd=str(self.script_dir))
            
            if result.returncode == 0:
                logger.info("✅ Trade log fetch completed successfully")
                logger.info(f"Output: {result.stdout}")
            else:
                logger.error(f"❌ Trade log fetch failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error running fetch script: {e}")
            return False
            
        return True
    
    def run_sync_logs(self):
        """Execute the sync_trade_logs.py script"""
        try:
            logger.info("🔄 Starting log synchronization...")
            
            # Run sync_trade_logs.py
            result = subprocess.run([
                sys.executable, str(self.sync_script)
            ], capture_output=True, text=True, cwd=str(self.script_dir))
            
            if result.returncode == 0:
                logger.info("✅ Log synchronization completed successfully")
                logger.info(f"Output: {result.stdout}")
            else:
                logger.error(f"❌ Log synchronization failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Error running sync script: {e}")
            return False
            
        return True
    
    def daily_sync_job(self):
        """Main daily sync job that runs both scripts"""
        current_time = datetime.now()
        logger.info(f"🕒 Daily sync job started at {current_time}")
        
        # Step 1: Fetch recent trades from Binance
        fetch_success = self.run_fetch_trades()
        
        # Step 2: Sync logs between locations
        sync_success = self.run_sync_logs()
        
        # Report results
        if fetch_success and sync_success:
            logger.info("✅ Daily sync completed successfully!")
            logger.info("📊 Trade logs are now up-to-date and synchronized")
        else:
            logger.error("❌ Daily sync encountered errors - check logs above")
            
        # Add separator for next day
        logger.info("=" * 60)
        
    def start_scheduler(self):
        """Start the daily scheduler"""
        # Schedule the job to run at 11:55 PM daily (5 minutes before midnight)
        schedule.every().day.at("23:55").do(self.daily_sync_job)
        
        logger.info("📅 Daily sync scheduler started")
        logger.info("⏰ Scheduled to run daily at 11:55 PM (5 minutes before midnight)")
        logger.info("🔄 This will fetch recent trades and synchronize logs")
        logger.info("📊 Press Ctrl+C to stop the scheduler")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            logger.info("⏹️ Daily sync scheduler stopped by user")

def main():
    """Main function to run the scheduler"""
    scheduler = DailySyncScheduler()
    
    # Check if scripts exist
    if not scheduler.fetch_script.exists():
        logger.error(f"❌ fetch_recent_trades.py not found at {scheduler.fetch_script}")
        sys.exit(1)
        
    if not scheduler.sync_script.exists():
        logger.error(f"❌ sync_trade_logs.py not found at {scheduler.sync_script}")
        sys.exit(1)
    
    # Provide options
    if len(sys.argv) > 1:
        if sys.argv[1] == "--test":
            logger.info("🧪 Running test sync...")
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
        print("Usage: python daily_sync_scheduler.py [--test|--schedule|--help]")
        print("Use --test to run once, --schedule to start daily automation")

if __name__ == "__main__":
    main()
