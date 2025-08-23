#!/usr/bin/env python3
"""
Bot Monitor - Continuously checks if the bot is running and restarts if needed
"""
import time
import subprocess
import os
import sys
from datetime import datetime

def is_bot_running():
    """Check if bot.py process is specifically running"""
    try:
        # Check for python processes running bot.py specifically
        result = subprocess.run(['powershell', 'Get-WmiObject Win32_Process | Where-Object {$_.Name -eq "python.exe" -and $_.CommandLine -like "*bot.py*"} | Select-Object ProcessId,CommandLine'], 
                              capture_output=True, text=True, check=False)
        
        # Also check if bot_log.txt is being actively written to (within last 5 minutes)
        log_active = False
        try:
            if os.path.exists('bot_log.txt'):
                log_mtime = os.path.getmtime('bot_log.txt')
                current_time = time.time()
                # If log was modified within last 5 minutes, consider bot active
                log_active = (current_time - log_mtime) < 300
        except:
            pass
        
        # Bot is running if we find bot.py process OR log is actively being written
        has_bot_process = 'bot.py' in result.stdout
        
        if has_bot_process and log_active:
            return True
        elif has_bot_process and not log_active:
            # Process exists but no recent log activity - might be stuck
            print(f"[{datetime.now()}] ⚠️ Bot process found but no recent log activity")
            return False
        elif not has_bot_process and log_active:
            # No process but recent log activity - something's wrong
            print(f"[{datetime.now()}] ⚠️ Recent log activity but no bot process found")
            return False
        else:
            return False
            
    except Exception as e:
        print(f"[{datetime.now()}] ⚠️ Error checking bot status: {e}")
        return False

def start_bot():
    """Start the bot"""
    try:
        print(f"[{datetime.now()}] Starting bot...")
        subprocess.Popen(['python', 'bot.py', '--local-testing'], 
                        creationflags=subprocess.CREATE_NEW_PROCESS_GROUP if os.name == 'nt' else 0)
        return True
    except Exception as e:
        print(f"[{datetime.now()}] Error starting bot: {e}")
        return False

def main():
    print("🤖 Bot Monitor Started")
    print("This will monitor the bot and restart it if it stops")
    print("Press Ctrl+C to stop monitoring")
    
    restart_count = 0
    last_restart = None
    last_status_report = None
    
    while True:
        try:
            current_time = datetime.now()
            bot_is_running = is_bot_running()
            
            if not bot_is_running:
                # Avoid rapid restarts (wait at least 2 minutes between restarts)
                if last_restart is None or (current_time - last_restart).seconds > 120:
                    restart_count += 1
                    print(f"[{current_time}] ❌ Bot not running (restart #{restart_count})")
                    print(f"[{current_time}] 🔍 Detailed check: No bot.py process found or log inactive")
                    
                    if start_bot():
                        last_restart = current_time
                        print(f"[{current_time}] ✅ Bot restarted successfully")
                    else:
                        print(f"[{current_time}] ❌ Failed to restart bot")
                        break
                else:
                    time_since_restart = (current_time - last_restart).seconds
                    print(f"[{current_time}] ⏳ Bot stopped but waiting before restart (waited {time_since_restart}s/120s)")
            else:
                # Only report status every 10 minutes instead of every 30 seconds
                if last_status_report is None or (current_time - last_status_report).seconds > 600:
                    print(f"[{current_time}] ✅ Bot confirmed running - bot.py process + active logging")
                    last_status_report = current_time
            
            # Check every 30 seconds
            time.sleep(30)
            
        except KeyboardInterrupt:
            print(f"\n[{datetime.now()}] Monitor stopped by user")
            break
        except Exception as e:
            print(f"[{datetime.now()}] Monitor error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
