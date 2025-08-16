#!/usr/bin/env python3
"""
🚀 MANUAL AWS UPLOAD & RESTART
==============================
Upload critical files and restart bot manually if needed
"""

import subprocess
import os
from datetime import datetime

# AWS connection details
AWS_KEY_FILE = r"C:\Users\miste\Documents\cryptobot-key.pem"
AWS_USER = "ubuntu"
AWS_IP = "3.135.216.32"
AWS_BOT_DIR = "/home/ubuntu/crypto-trading-bot"

def upload_file(local_file):
    """Upload a single file to AWS"""
    if not os.path.exists(local_file):
        print(f"❌ {local_file} - File not found")
        return False
    
    try:
        file_size = os.path.getsize(local_file)
        print(f"📤 Uploading {local_file} ({file_size:,} bytes)...")
        
        scp_cmd = [
            "scp", 
            "-i", AWS_KEY_FILE,
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=10",
            local_file,
            f"{AWS_USER}@{AWS_IP}:{AWS_BOT_DIR}/"
        ]
        
        result = subprocess.run(scp_cmd, capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            print(f"✅ {local_file} uploaded successfully")
            return True
        else:
            print(f"❌ {local_file} upload failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ {local_file} upload error: {e}")
        return False

def restart_bot():
    """Restart the bot on AWS"""
    try:
        print("🛑 Stopping existing bot...")
        
        # Stop bot
        stop_cmd = [
            "ssh", 
            "-i", AWS_KEY_FILE,
            "-o", "StrictHostKeyChecking=no",
            f"{AWS_USER}@{AWS_IP}",
            "pkill -f 'python.*bot.py'"
        ]
        
        subprocess.run(stop_cmd, timeout=10)
        
        print("🚀 Starting bot...")
        
        # Start bot
        start_cmd = [
            "ssh", 
            "-i", AWS_KEY_FILE,
            "-o", "StrictHostKeyChecking=no",
            f"{AWS_USER}@{AWS_IP}",
            f"cd {AWS_BOT_DIR} && nohup python bot.py > bot_output.log 2>&1 &"
        ]
        
        result = subprocess.run(start_cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print("✅ Bot restart command executed")
            return True
        else:
            print(f"❌ Bot restart failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Bot restart error: {e}")
        return False

def main():
    """Manual upload and restart"""
    print("🚀 MANUAL AWS UPLOAD & RESTART")
    print("=" * 40)
    print(f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Critical files to upload
    critical_files = [
        "bot.py",                    # Most important - contains latest fixes
        "enhanced_config.json",      # Configuration
        "enhanced_config.py"         # Config management
    ]
    
    print("📤 UPLOADING CRITICAL FILES")
    print("-" * 30)
    
    upload_results = []
    for file in critical_files:
        success = upload_file(file)
        upload_results.append(success)
    
    successful_uploads = sum(upload_results)
    total_files = len(critical_files)
    
    print(f"\n📊 Upload Summary: {successful_uploads}/{total_files} successful")
    
    if successful_uploads >= 1:  # At least bot.py uploaded
        print("\n🔄 RESTARTING BOT")
        print("-" * 20)
        
        restart_success = restart_bot()
        
        if restart_success:
            print("\n🎉 UPDATE COMPLETED!")
            print("✅ Files uploaded")
            print("✅ Bot restarted")
            print("\n🎯 Your AWS bot now has the latest updates!")
        else:
            print("\n⚠️ PARTIAL SUCCESS")
            print("✅ Files uploaded")
            print("❌ Bot restart failed")
    else:
        print("\n❌ UPLOAD FAILED")
        print("🚨 Manual intervention required")
    
    return successful_uploads >= 1

if __name__ == "__main__":
    main()
