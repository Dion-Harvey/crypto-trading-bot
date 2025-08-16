#!/usr/bin/env python3
"""
🚨 EMERGENCY BOT RESTART
Restarts the bot to pick up emergency configuration changes
"""

import subprocess
import sys
import time
import psutil
from log_utils import log_message

def find_bot_process():
    """Find running bot process"""
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if 'python' in proc.info['name'].lower():
                cmdline = ' '.join(proc.info['cmdline'])
                if 'bot.py' in cmdline:
                    return proc.info['pid']
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return None

def emergency_restart():
    """Emergency restart for XLM opportunity"""
    
    log_message("🚨 EMERGENCY BOT RESTART: Applying XLM switch")
    
    # Find and stop existing bot
    bot_pid = find_bot_process()
    if bot_pid:
        try:
            process = psutil.Process(bot_pid)
            log_message(f"🛑 STOPPING BOT: PID {bot_pid}")
            process.terminate()
            time.sleep(3)
            
            if process.is_running():
                log_message("⚡ FORCE KILLING BOT")
                process.kill()
                time.sleep(1)
                
            log_message("✅ BOT STOPPED SUCCESSFULLY")
        except Exception as e:
            log_message(f"⚠️ Error stopping bot: {e}")
    else:
        log_message("ℹ️ No running bot process found")
    
    # Wait a moment
    time.sleep(2)
    
    # Start bot with new configuration
    log_message("🚀 STARTING BOT WITH XLM EMERGENCY CONFIG")
    
    try:
        # Start bot in background
        subprocess.Popen([
            'C:/Users/miste/Documents/crypto-trading-bot/crypto-trading-bot/.venv/Scripts/python.exe',
            'bot.py'
        ], creationflags=subprocess.CREATE_NEW_CONSOLE)
        
        log_message("✅ BOT RESTARTED: Should now be trading XLM/USDT")
        log_message("🎯 EMERGENCY SWITCH: Bot configured for XLM +11.70% opportunity")
        
        return True
        
    except Exception as e:
        log_message(f"❌ BOT RESTART FAILED: {e}")
        return False

if __name__ == "__main__":
    print("🚨 EMERGENCY BOT RESTART FOR XLM OPPORTUNITY")
    success = emergency_restart()
    
    if success:
        print("✅ Emergency restart completed")
        print("🎯 Bot should now be trading XLM/USDT")
        print("📊 Monitor logs to confirm XLM trading activity")
    else:
        print("❌ Emergency restart failed")
        print("🔧 Manual bot restart may be required")
