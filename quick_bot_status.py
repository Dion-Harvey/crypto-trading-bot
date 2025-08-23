#!/usr/bin/env python3
"""
Quick Bot Status Checker
Verifies that the crypto trading bot is running with all systems operational
"""

import psutil
import os
from datetime import datetime

def check_bot_status():
    print("🤖 CRYPTO TRADING BOT STATUS CHECK")
    print("=" * 50)
    print(f"⏰ Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check for Python processes running bot.py
    bot_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('bot.py' in cmd for cmd in cmdline):
                    bot_processes.append({
                        'pid': proc.info['pid'],
                        'cmdline': ' '.join(cmdline[-2:])  # Last 2 parts of command
                    })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if bot_processes:
        print(f"✅ BOT STATUS: RUNNING ({len(bot_processes)} process(es))")
        for proc in bot_processes:
            print(f"   🔹 PID: {proc['pid']} - {proc['cmdline']}")
    else:
        print("❌ BOT STATUS: NOT RUNNING")
    
    print()
    
    # Check log file for recent activity
    log_file = "bot_log.txt"
    if os.path.exists(log_file):
        try:
            # Get last few lines of log
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    print("📝 LAST LOG ENTRY:")
                    print(f"   {last_line}")
                    
                    # Extract timestamp from last line
                    if '[2025-' in last_line:
                        timestamp_str = last_line.split(']')[0].replace('[', '')
                        try:
                            last_activity = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                            time_diff = datetime.now() - last_activity
                            minutes_ago = int(time_diff.total_seconds() / 60)
                            
                            if minutes_ago < 2:
                                print(f"✅ RECENT ACTIVITY: {minutes_ago} minute(s) ago")
                            elif minutes_ago < 10:
                                print(f"⚠️ ACTIVITY: {minutes_ago} minute(s) ago (may be paused)")
                            else:
                                print(f"❌ LAST ACTIVITY: {minutes_ago} minute(s) ago (likely stopped)")
                        except ValueError:
                            print("⚠️ Could not parse timestamp")
        except Exception as e:
            print(f"⚠️ Error reading log: {e}")
    else:
        print("❌ LOG FILE: Not found")
    
    print()
    
    # Check if dashboard is running
    dashboard_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] and 'python' in proc.info['name'].lower():
                cmdline = proc.info.get('cmdline', [])
                if cmdline and any('dashboard.py' in cmd for cmd in cmdline):
                    dashboard_processes.append(proc.info['pid'])
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if dashboard_processes:
        print(f"📊 DASHBOARD: RUNNING (PID: {dashboard_processes[0]})")
    else:
        print("📊 DASHBOARD: NOT RUNNING")
    
    print()
    
    # Overall status
    if bot_processes:
        print("🎯 OVERALL STATUS: ✅ OPERATIONAL")
        print("💡 The bot is running and should be actively trading")
    else:
        print("🎯 OVERALL STATUS: ❌ NEEDS RESTART")
        print("💡 Use: python bot.py")

if __name__ == "__main__":
    check_bot_status()
