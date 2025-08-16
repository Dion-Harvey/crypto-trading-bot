#!/usr/bin/env python3
"""
🛡️ CRYPTO BOT WATCHDOG - Automatic Bot Monitoring & Recovery
===========================================================

This script continuously monitors the crypto trading bot and automatically 
restarts it if it crashes, becomes unresponsive, or stops trading.

Features:
- Process monitoring (checks if bot process is running)
- Health monitoring (checks if bot is actively trading/logging)
- Log analysis (detects error patterns and hangs)
- State preservation (backs up bot state before restart)
- Auto-recovery (restarts bot with proper environment)
- Alert logging (records all restart events)

Usage:
    python3 crypto-bot-watchdog.py

Run as systemd service for 24/7 monitoring.
"""

import os
import sys
import time
import psutil
import subprocess
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
import signal
import shutil

# Configuration
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BOT_SCRIPT = os.path.join(SCRIPT_DIR, "bot.py")
BOT_VENV = os.path.join(SCRIPT_DIR, ".venv", "bin", "python")
BOT_LOG_FILE = os.path.join(SCRIPT_DIR, "bot_log.txt")
WATCHDOG_LOG_FILE = os.path.join(SCRIPT_DIR, "watchdog.log")
BOT_STATE_FILE = os.path.join(SCRIPT_DIR, "bot_state.json")
ENHANCED_CONFIG_FILE = os.path.join(SCRIPT_DIR, "enhanced_config.json")

# Watchdog settings
CHECK_INTERVAL = 30  # Check every 30 seconds
MAX_RESTART_ATTEMPTS = 5  # Max restarts per hour
RESTART_COOLDOWN = 300  # 5 minutes between restarts
LOG_ACTIVITY_TIMEOUT = 900  # 15 minutes without log activity = problem
MEMORY_THRESHOLD = 500 * 1024 * 1024  # 500MB memory limit
CPU_THRESHOLD = 90  # 90% CPU for 5+ minutes = problem

# Global state
watchdog_state = {
    'bot_pid': None,
    'last_restart': 0,
    'restart_count': 0,
    'last_log_activity': time.time(),
    'high_cpu_start': None,
    'consecutive_errors': 0
}

class WatchdogLogger:
    def __init__(self):
        self.logger = logging.getLogger('crypto_bot_watchdog')
        self.logger.setLevel(logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(WATCHDOG_LOG_FILE)
        file_handler.setLevel(logging.INFO)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s: %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        self.logger.info(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def error(self, message):
        self.logger.error(message)

logger = WatchdogLogger()

def find_bot_process():
    """Find the crypto bot process"""
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            cmdline = proc.info['cmdline']
            if cmdline and len(cmdline) > 1:
                if 'bot.py' in ' '.join(cmdline) and 'python' in cmdline[0]:
                    return proc.info['pid']
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass
    return None

def check_process_health(pid):
    """Check if the bot process is healthy"""
    try:
        proc = psutil.Process(pid)
        
        # Check if process is still running
        if not proc.is_running():
            return False, "Process not running"
        
        # Check memory usage
        memory_info = proc.memory_info()
        if memory_info.rss > MEMORY_THRESHOLD:
            return False, f"High memory usage: {memory_info.rss / 1024 / 1024:.1f}MB"
        
        # Check CPU usage
        cpu_percent = proc.cpu_percent()
        current_time = time.time()
        
        if cpu_percent > CPU_THRESHOLD:
            if watchdog_state['high_cpu_start'] is None:
                watchdog_state['high_cpu_start'] = current_time
            elif current_time - watchdog_state['high_cpu_start'] > 300:  # 5 minutes
                return False, f"High CPU usage: {cpu_percent:.1f}% for 5+ minutes"
        else:
            watchdog_state['high_cpu_start'] = None
        
        return True, "Process healthy"
        
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        return False, f"Process check error: {e}"

def check_log_activity():
    """Check if bot is actively logging (trading activity)"""
    try:
        if not os.path.exists(BOT_LOG_FILE):
            return False, "Log file not found"
        
        # Get last modification time
        last_modified = os.path.getmtime(BOT_LOG_FILE)
        current_time = time.time()
        
        time_since_activity = current_time - last_modified
        
        if time_since_activity > LOG_ACTIVITY_TIMEOUT:
            return False, f"No log activity for {time_since_activity/60:.1f} minutes"
        
        # Check for recent error patterns
        try:
            with open(BOT_LOG_FILE, 'r') as f:
                # Read last 50 lines
                lines = f.readlines()[-50:]
                recent_lines = ''.join(lines)
                
                # Check for critical errors
                error_patterns = [
                    'ConnectionError',
                    'Exchange error',
                    'API key invalid',
                    'Insufficient balance',
                    'Error in trading loop',
                    'Exception',
                    'Traceback'
                ]
                
                error_count = sum(1 for pattern in error_patterns if pattern in recent_lines)
                if error_count > 5:  # More than 5 errors in recent logs
                    return False, f"High error rate: {error_count} errors in recent logs"
        
        except Exception as e:
            logger.warning(f"Could not analyze log content: {e}")
        
        return True, "Log activity normal"
        
    except Exception as e:
        return False, f"Log check error: {e}"

def backup_bot_state():
    """Backup bot state before restart"""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup state file
        if os.path.exists(BOT_STATE_FILE):
            backup_state = f"{BOT_STATE_FILE}.backup_{timestamp}"
            shutil.copy2(BOT_STATE_FILE, backup_state)
            logger.info(f"Bot state backed up to {backup_state}")
        
        # Backup config file
        if os.path.exists(ENHANCED_CONFIG_FILE):
            backup_config = f"{ENHANCED_CONFIG_FILE}.backup_{timestamp}"
            shutil.copy2(ENHANCED_CONFIG_FILE, backup_config)
            logger.info(f"Config backed up to {backup_config}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to backup bot state: {e}")
        return False

def kill_bot_process(pid):
    """Safely terminate the bot process"""
    try:
        proc = psutil.Process(pid)
        
        # Try graceful shutdown first
        proc.terminate()
        
        # Wait up to 10 seconds for graceful shutdown
        try:
            proc.wait(timeout=10)
            logger.info(f"Bot process {pid} terminated gracefully")
            return True
        except psutil.TimeoutExpired:
            # Force kill if graceful shutdown fails
            proc.kill()
            logger.warning(f"Bot process {pid} force killed")
            return True
            
    except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
        logger.error(f"Failed to kill bot process {pid}: {e}")
        return False

def start_bot():
    """Start the crypto bot"""
    try:
        logger.info("Starting crypto bot...")
        
        # Change to script directory
        os.chdir(SCRIPT_DIR)
        
        # Build command
        if os.path.exists(BOT_VENV):
            cmd = [BOT_VENV, BOT_SCRIPT]
        else:
            cmd = ["python3", BOT_SCRIPT]
        
        # Start bot process
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            preexec_fn=os.setsid  # Create new process group
        )
        
        # Wait a moment to see if it starts successfully
        time.sleep(5)
        
        if process.poll() is None:  # Process is still running
            watchdog_state['bot_pid'] = process.pid
            logger.info(f"Bot started successfully with PID {process.pid}")
            return True
        else:
            logger.error("Bot failed to start - process exited immediately")
            return False
            
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        return False

def can_restart():
    """Check if we can restart the bot (rate limiting)"""
    current_time = time.time()
    
    # Reset restart count every hour
    if current_time - watchdog_state['last_restart'] > 3600:
        watchdog_state['restart_count'] = 0
    
    # Check restart limits
    if watchdog_state['restart_count'] >= MAX_RESTART_ATTEMPTS:
        logger.error(f"Maximum restart attempts ({MAX_RESTART_ATTEMPTS}) reached in the last hour")
        return False
    
    # Check cooldown period
    if current_time - watchdog_state['last_restart'] < RESTART_COOLDOWN:
        remaining = RESTART_COOLDOWN - (current_time - watchdog_state['last_restart'])
        logger.info(f"Restart cooldown active - {remaining:.0f}s remaining")
        return False
    
    return True

def restart_bot(reason):
    """Restart the bot with proper cleanup and state backup"""
    if not can_restart():
        return False
    
    logger.warning(f"Restarting bot - Reason: {reason}")
    
    # Backup state
    backup_bot_state()
    
    # Kill existing process if it exists
    if watchdog_state['bot_pid']:
        kill_bot_process(watchdog_state['bot_pid'])
        watchdog_state['bot_pid'] = None
    
    # Wait a moment for cleanup
    time.sleep(10)
    
    # Start bot
    if start_bot():
        watchdog_state['last_restart'] = time.time()
        watchdog_state['restart_count'] += 1
        watchdog_state['consecutive_errors'] = 0
        logger.info(f"Bot restart successful (attempt {watchdog_state['restart_count']})")
        return True
    else:
        watchdog_state['consecutive_errors'] += 1
        logger.error(f"Bot restart failed (consecutive errors: {watchdog_state['consecutive_errors']})")
        return False

def monitor_bot():
    """Main monitoring loop"""
    logger.info("🛡️ Crypto Bot Watchdog started")
    logger.info(f"Monitoring bot script: {BOT_SCRIPT}")
    logger.info(f"Check interval: {CHECK_INTERVAL}s")
    
    while True:
        try:
            # Find bot process
            current_pid = find_bot_process()
            
            if current_pid != watchdog_state['bot_pid']:
                watchdog_state['bot_pid'] = current_pid
                if current_pid:
                    logger.info(f"Bot process detected: PID {current_pid}")
                else:
                    logger.warning("Bot process not found")
            
            # Check if bot should be running but isn't
            if not current_pid:
                logger.warning("Bot process not running - attempting restart")
                if restart_bot("Process not found"):
                    continue
                else:
                    logger.error("Failed to restart bot - waiting before retry")
                    time.sleep(60)  # Wait 1 minute before trying again
                    continue
            
            # Check process health
            process_healthy, process_status = check_process_health(current_pid)
            if not process_healthy:
                logger.warning(f"Bot process unhealthy: {process_status}")
                if restart_bot(f"Process unhealthy: {process_status}"):
                    continue
                else:
                    time.sleep(60)  # Wait before retry
                    continue
            
            # Check log activity
            log_healthy, log_status = check_log_activity()
            if not log_healthy:
                logger.warning(f"Bot activity check failed: {log_status}")
                if restart_bot(f"Activity check failed: {log_status}"):
                    continue
                else:
                    time.sleep(60)  # Wait before retry
                    continue
            
            # All checks passed
            if watchdog_state['consecutive_errors'] > 0:
                logger.info("Bot health restored - monitoring normally")
                watchdog_state['consecutive_errors'] = 0
            
            # Log periodic status
            if int(time.time()) % 600 == 0:  # Every 10 minutes
                logger.info(f"✅ Bot healthy - PID: {current_pid}, {log_status}")
            
        except KeyboardInterrupt:
            logger.info("Watchdog stopped by user")
            break
        except Exception as e:
            logger.error(f"Watchdog error: {e}")
            watchdog_state['consecutive_errors'] += 1
            
            if watchdog_state['consecutive_errors'] > 10:
                logger.error("Too many consecutive watchdog errors - stopping")
                break
        
        time.sleep(CHECK_INTERVAL)

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    logger.info(f"Received signal {signum} - shutting down watchdog")
    sys.exit(0)

if __name__ == "__main__":
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Ensure we're in the right directory
    os.chdir(SCRIPT_DIR)
    
    # Start monitoring
    monitor_bot()
