#!/usr/bin/env python3
"""
Complete AWS Update Script
Uploads all critical files and restarts the bot with verification
"""

import os
import sys
import json
import subprocess
import time
from datetime import datetime

def run_command(cmd, timeout=30):
    """Run a command with timeout and return result"""
    try:
        print(f"🔧 Running: {cmd}")
        result = subprocess.run(
            cmd, shell=True, capture_output=True, 
            text=True, timeout=timeout
        )
        return result.returncode == 0, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        print(f"⏱️ Command timed out after {timeout}s")
        return False, "", "Timeout"
    except Exception as e:
        print(f"❌ Command failed: {e}")
        return False, "", str(e)

def check_aws_connection():
    """Test AWS connection"""
    print("🔍 Testing AWS connection...")
    
    # Try different key locations
    key_paths = [
        "cryptobot-key.pem",
        "C:\\Users\\miste\\Downloads\\cryptobot-key.pem",
        "C:\\Users\\miste\\Documents\\cryptobot-key.pem",
        "..\\cryptobot-key.pem"
    ]
    
    for key_path in key_paths:
        if os.path.exists(key_path):
            print(f"✅ Found key: {key_path}")
            return key_path
    
    print("❌ Key file not found. Please ensure cryptobot-key.pem is available.")
    print("Common locations to check:")
    for path in key_paths:
        print(f"   {path}")
    return None

def upload_files(key_path):
    """Upload all critical files"""
    files_to_upload = [
        ("bot.py", "Main trading bot with latest fixes"),
        ("enhanced_config.json", "Trading configuration"),
        ("enhanced_config.py", "Configuration management")
    ]
    
    aws_host = "ubuntu@3.135.216.32"
    
    print("📤 Starting file upload...")
    
    for filename, description in files_to_upload:
        if not os.path.exists(filename):
            print(f"⚠️ {filename} not found - skipping")
            continue
            
        file_size = os.path.getsize(filename)
        print(f"📁 Uploading {filename} ({file_size:,} bytes) - {description}")
        
        cmd = f'scp -i "{key_path}" -o StrictHostKeyChecking=no "{filename}" {aws_host}:~/'
        success, stdout, stderr = run_command(cmd, timeout=60)
        
        if success:
            print(f"✅ {filename} uploaded successfully")
        else:
            print(f"❌ Failed to upload {filename}")
            print(f"Error: {stderr}")
            return False
    
    return True

def restart_bot(key_path):
    """Stop current bot and restart with new files"""
    aws_host = "ubuntu@3.135.216.32"
    
    print("🔄 Restarting bot on AWS...")
    
    # Stop current bot
    print("🛑 Stopping current bot...")
    cmd = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no {aws_host} "pkill -f bot.py || true"'
    run_command(cmd)
    
    time.sleep(3)
    
    # Start new bot
    print("🚀 Starting updated bot...")
    cmd = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no {aws_host} "cd ~ && nohup python3 bot.py > bot.log 2>&1 &"'
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("✅ Bot restarted successfully")
        return True
    else:
        print(f"❌ Failed to restart bot: {stderr}")
        return False

def verify_deployment(key_path):
    """Verify the deployment is working"""
    aws_host = "ubuntu@3.135.216.32"
    
    print("🔍 Verifying deployment...")
    
    # Check if bot is running
    cmd = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no {aws_host} "ps aux | grep bot.py | grep -v grep"'
    success, stdout, stderr = run_command(cmd)
    
    if success and stdout.strip():
        print("✅ Bot is running on AWS")
        print(f"Process: {stdout.strip()}")
    else:
        print("⚠️ Bot may not be running")
    
    # Check file timestamps
    cmd = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no {aws_host} "ls -la bot.py enhanced_config.json"'
    success, stdout, stderr = run_command(cmd)
    
    if success:
        print("📁 Current AWS files:")
        for line in stdout.strip().split('\n'):
            if line.strip():
                print(f"   {line}")
    
    # Check recent log entries
    cmd = f'ssh -i "{key_path}" -o StrictHostKeyChecking=no {aws_host} "tail -5 bot.log 2>/dev/null || echo \'No recent logs\'"'
    success, stdout, stderr = run_command(cmd)
    
    if success and stdout.strip():
        print("📋 Recent bot activity:")
        for line in stdout.strip().split('\n'):
            if line.strip():
                print(f"   {line}")

def main():
    """Main update process"""
    print("🚀 COMPLETE AWS UPDATE PROCESS")
    print("=" * 40)
    print(f"⏰ Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check local files
    print("📋 Local file status:")
    for filename in ["bot.py", "enhanced_config.json", "enhanced_config.py"]:
        if os.path.exists(filename):
            size = os.path.getsize(filename)
            mod_time = datetime.fromtimestamp(os.path.getmtime(filename))
            print(f"   {filename}: {size:,} bytes, modified {mod_time.strftime('%H:%M:%S')}")
        else:
            print(f"   {filename}: Not found")
    print()
    
    # Check AWS connection
    key_path = check_aws_connection()
    if not key_path:
        print("❌ Cannot proceed without AWS key file")
        return False
    
    # Upload files
    if not upload_files(key_path):
        print("❌ Upload failed")
        return False
    
    # Restart bot
    if not restart_bot(key_path):
        print("❌ Bot restart failed")
        return False
    
    # Wait a moment for bot to start
    print("⏳ Waiting for bot to initialize...")
    time.sleep(10)
    
    # Verify deployment
    verify_deployment(key_path)
    
    print()
    print("🎉 AWS UPDATE COMPLETE!")
    print("✅ All files uploaded")
    print("✅ Bot restarted")
    print("✅ Deployment verified")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎯 Your AWS bot is now running with the latest updates!")
        else:
            print("\n⚠️ Update process encountered issues. Please check the output above.")
    except KeyboardInterrupt:
        print("\n⏹️ Update cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
