#!/usr/bin/env python3
"""
🤖 Crypto Trading Bot Daemon Runner
Ensures 24/7 operation with automatic restart and monitoring
Designed for AWS EC2 continuous operation
"""

import os
import sys
import time
import signal
import subprocess
import datetime
import logging
from pathlib import Path

# Set up logging
log_file = Path(__file__).parent / "daemon.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class TradingBotDaemon:
    def __init__(self):
        self.bot_script = Path(__file__).parent / "bot.py"
        self.python_executable = sys.executable
        self.process = None
        self.running = True
        self.restart_count = 0
        self.max_restarts_per_hour = 10
        self.restart_times = []
        
        # Signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"🛑 Received signal {signum}, shutting down daemon...")
        self.running = False
        if self.process:
            self.stop_bot()
    
    def start_bot(self):
        """Start the trading bot process"""
        try:
            logger.info("🚀 Starting trading bot...")
            
            # Ensure we're in the correct directory
            os.chdir(Path(__file__).parent)
            
            # Start bot with proper environment
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'  # Ensure real-time output
            
            self.process = subprocess.Popen(
                [self.python_executable, str(self.bot_script)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                bufsize=1,
                env=env
            )
            
            logger.info(f"✅ Bot started with PID: {self.process.pid}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start bot: {e}")
            return False
    
    def stop_bot(self):
        """Stop the trading bot process gracefully"""
        if self.process:
            try:
                logger.info("🛑 Stopping trading bot...")
                
                # Try graceful shutdown first
                self.process.terminate()
                
                # Wait up to 30 seconds for graceful shutdown
                try:
                    self.process.wait(timeout=30)
                    logger.info("✅ Bot stopped gracefully")
                except subprocess.TimeoutExpired:
                    logger.warning("⚠️ Bot didn't stop gracefully, forcing shutdown...")
                    self.process.kill()
                    self.process.wait()
                    logger.info("✅ Bot force-stopped")
                    
            except Exception as e:
                logger.error(f"❌ Error stopping bot: {e}")
            finally:
                self.process = None
    
    def is_bot_healthy(self):
        """Check if the bot process is running and healthy"""
        if not self.process:
            return False
            
        # Check if process is still running
        if self.process.poll() is not None:
            return False
            
        return True
    
    def should_restart(self):
        """Determine if bot should be restarted based on restart limits"""
        now = datetime.datetime.now()
        
        # Remove restart times older than 1 hour
        self.restart_times = [t for t in self.restart_times if (now - t).seconds < 3600]
        
        # Check if we've exceeded restart limit
        if len(self.restart_times) >= self.max_restarts_per_hour:
            logger.error(f"❌ Too many restarts ({len(self.restart_times)}) in the last hour. Waiting...")
            return False
            
        return True
    
    def restart_bot(self):
        """Restart the trading bot"""
        logger.info("🔄 Restarting trading bot...")
        
        # Record restart time
        self.restart_times.append(datetime.datetime.now())
        self.restart_count += 1
        
        # Stop current process
        self.stop_bot()
        
        # Wait a moment before restarting
        time.sleep(5)
        
        # Start new process
        if self.start_bot():
            logger.info(f"✅ Bot restarted successfully (restart #{self.restart_count})")
        else:
            logger.error("❌ Failed to restart bot")
    
    def monitor_bot_output(self):
        """Monitor bot output for issues"""
        if not self.process or not self.process.stdout:
            return
            
        try:
            # Read a line of output (non-blocking)
            line = self.process.stdout.readline()
            if line:
                # Log bot output
                print(f"[BOT] {line.strip()}")
                
                # Check for error patterns
                if any(error in line.lower() for error in ['error', 'exception', 'failed', 'timeout']):
                    logger.warning(f"⚠️ Bot error detected: {line.strip()}")
                    
        except Exception as e:
            logger.error(f"❌ Error reading bot output: {e}")
    
    def run(self):
        """Main daemon loop"""
        logger.info("🤖 Trading Bot Daemon starting...")
        logger.info(f"📂 Working directory: {os.getcwd()}")
        logger.info(f"🐍 Python executable: {self.python_executable}")
        logger.info(f"📄 Bot script: {self.bot_script}")
        
        # Initial bot start
        if not self.start_bot():
            logger.error("❌ Failed to start bot initially. Exiting.")
            return
        
        # Main monitoring loop
        while self.running:
            try:
                # Check bot health
                if not self.is_bot_healthy():
                    logger.warning("⚠️ Bot is not healthy, checking restart conditions...")
                    
                    if self.should_restart():
                        self.restart_bot()
                    else:
                        logger.info("⏳ Waiting before next restart attempt...")
                        time.sleep(300)  # Wait 5 minutes before checking again
                        continue
                
                # Monitor bot output
                self.monitor_bot_output()
                
                # Health check every 30 seconds
                time.sleep(30)
                
                # Log status every 10 minutes
                if int(time.time()) % 600 == 0:
                    logger.info(f"💓 Daemon healthy - Bot PID: {self.process.pid if self.process else 'None'}, Restarts: {self.restart_count}")
                
            except KeyboardInterrupt:
                logger.info("🛑 Daemon stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Daemon error: {e}")
                time.sleep(60)  # Wait before continuing
        
        # Cleanup
        self.stop_bot()
        logger.info("✅ Daemon shutdown complete")

if __name__ == "__main__":
    daemon = TradingBotDaemon()
    daemon.run()
