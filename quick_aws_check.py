#!/usr/bin/env python3
"""
🔍 QUICK AWS SYNC CHECK - Critical Files Only
=============================================
Fast check of most important files for AWS sync status
"""

import subprocess
import os
import hashlib
from datetime import datetime

# AWS connection details  
AWS_KEY_FILE = r"C:\Users\miste\Documents\cryptobot-key.pem"
AWS_USER = "ubuntu"
AWS_IP = "3.135.216.32"
AWS_BOT_DIR = "/home/ubuntu/crypto-trading-bot"

def run_ssh_command(command):
    """Execute SSH command on AWS instance"""
    try:
        ssh_cmd = [
            "ssh", 
            "-i", AWS_KEY_FILE,
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=5",
            f"{AWS_USER}@{AWS_IP}",
            command
        ]
        
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=15)
        return result.stdout.strip() if result.returncode == 0 else "Error"
        
    except Exception as e:
        return "Connection Error"

def quick_sync_check():
    """Quick check of critical files"""
    print("🚀 QUICK AWS SYNC STATUS")
    print("=" * 40)
    
    # Most critical files for trading bot operation
    critical_files = [
        "bot.py",                    # Main trading logic
        "enhanced_config.json",      # Multi-pair configuration  
        "enhanced_config.py",        # Configuration management
        "multi_crypto_monitor.py"    # Multi-crypto monitoring
    ]
    
    print("🔍 Checking critical files...\n")
    
    sync_summary = {"synced": 0, "different": 0, "missing": 0, "error": 0}
    
    for file in critical_files:
        print(f"📁 {file}:")
        
        if not os.path.exists(file):
            print(f"   ❌ Local file missing")
            sync_summary["error"] += 1
            continue
            
        # Get local file info
        local_size = os.path.getsize(file)
        local_modified = datetime.fromtimestamp(os.path.getmtime(file))
        hours_ago = (datetime.now() - local_modified).total_seconds() / 3600
        
        print(f"   💻 Local: {local_size:,} bytes, modified {hours_ago:.1f}h ago")
        
        # Check if file exists on AWS and get size
        aws_check = run_ssh_command(f"stat -c '%s' {AWS_BOT_DIR}/{file} 2>/dev/null || echo 'Missing'")
        
        if aws_check == "Missing":
            print(f"   ☁️ AWS: File not found")
            print(f"   ❌ Status: MISSING FROM AWS")
            sync_summary["missing"] += 1
        elif aws_check == "Connection Error" or aws_check == "Error":
            print(f"   ☁️ AWS: Cannot check (connection issue)")
            print(f"   ⚠️ Status: UNKNOWN")
            sync_summary["error"] += 1
        else:
            aws_size = int(aws_check) if aws_check.isdigit() else 0
            print(f"   ☁️ AWS: {aws_size:,} bytes")
            
            if local_size == aws_size:
                print(f"   ✅ Status: LIKELY SYNCED (same size)")
                sync_summary["synced"] += 1
            else:
                print(f"   ❌ Status: DIFFERENT SIZE (needs update)")
                sync_summary["different"] += 1
        
        print()
    
    # Bot status check
    print("🤖 AWS Bot Status:")
    bot_status = run_ssh_command("pgrep -f 'python.*bot.py' | wc -l")
    
    if bot_status.isdigit() and int(bot_status) > 0:
        print(f"   ✅ Bot is running ({bot_status} process(es))")
        
        # Quick log check
        recent_log = run_ssh_command(f"cd {AWS_BOT_DIR} && tail -1 bot_log.txt 2>/dev/null || echo 'No log'")
        if recent_log != "No log" and recent_log != "Error":
            print(f"   📋 Recent activity: {recent_log[:60]}...")
    else:
        print(f"   ❌ Bot is not running")
    
    print()
    
    # Summary
    total_files = len(critical_files)
    print("📊 SYNC SUMMARY:")
    print(f"   ✅ Synced: {sync_summary['synced']}/{total_files}")
    print(f"   ❌ Different: {sync_summary['different']}/{total_files}")
    print(f"   ⚠️ Missing: {sync_summary['missing']}/{total_files}")
    print(f"   🔴 Errors: {sync_summary['error']}/{total_files}")
    
    sync_percentage = (sync_summary['synced'] / total_files) * 100
    
    if sync_percentage >= 75:
        print(f"\n🟢 OVERALL STATUS: GOOD SYNC ({sync_percentage:.0f}%)")
        if sync_summary['different'] > 0 or sync_summary['missing'] > 0:
            print(f"💡 Some files need updating to AWS")
    else:
        print(f"\n🔴 OVERALL STATUS: POOR SYNC ({sync_percentage:.0f}%)")
        print(f"🚨 Major sync required - AWS bot may be running outdated code")
    
    return sync_summary

def show_upload_commands():
    """Show commands to upload files"""
    print(f"\n🔧 UPLOAD COMMANDS TO UPDATE AWS:")
    print(f"=" * 40)
    print(f"# Upload individual files:")
    
    critical_files = ["bot.py", "enhanced_config.json", "enhanced_config.py", "multi_crypto_monitor.py"]
    
    for file in critical_files:
        if os.path.exists(file):
            print(f'scp -i "{AWS_KEY_FILE}" {file} {AWS_USER}@{AWS_IP}:{AWS_BOT_DIR}/')
    
    print(f"\n# Upload all critical files at once:")
    existing_files = [f for f in critical_files if os.path.exists(f)]
    if existing_files:
        files_str = ' '.join(existing_files)
        print(f'scp -i "{AWS_KEY_FILE}" {files_str} {AWS_USER}@{AWS_IP}:{AWS_BOT_DIR}/')
    
    print(f"\n# Restart bot after upload:")
    print(f'ssh -i "{AWS_KEY_FILE}" {AWS_USER}@{AWS_IP} "cd {AWS_BOT_DIR} && pkill -f bot.py && nohup python bot.py > bot_output.log 2>&1 &"')

if __name__ == "__main__":
    sync_summary = quick_sync_check()
    show_upload_commands()
