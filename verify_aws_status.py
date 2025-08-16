#!/usr/bin/env python3
"""
🔍 AWS UPDATE STATUS VERIFICATION
=================================
Quick check to verify if files were uploaded and bot restarted
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

def run_ssh_command(command, timeout=15):
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
        
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=timeout)
        return result.stdout.strip() if result.returncode == 0 else "Error"
        
    except Exception as e:
        return f"Connection Error: {e}"

def get_file_hash(filepath):
    """Get MD5 hash of a local file"""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()[:8]
    except Exception as e:
        return "Error"

def verify_upload_status():
    """Verify if files were uploaded successfully"""
    print("🔍 VERIFYING AWS UPLOAD STATUS")
    print("=" * 40)
    
    # Test connection first
    connection_test = run_ssh_command("echo 'Connected'", timeout=5)
    if "Connected" not in connection_test:
        print(f"❌ Cannot connect to AWS: {connection_test}")
        return False
    
    print("✅ AWS connection successful")
    
    # Check critical files
    critical_files = ["bot.py", "enhanced_config.json", "enhanced_config.py"]
    
    upload_success = True
    
    for file in critical_files:
        print(f"\n📁 Checking {file}:")
        
        if not os.path.exists(file):
            print(f"   ⚠️ Local file not found")
            continue
            
        # Get local file info
        local_hash = get_file_hash(file)
        local_size = os.path.getsize(file)
        local_mod = datetime.fromtimestamp(os.path.getmtime(file))
        
        print(f"   💻 Local:  {local_hash}... ({local_size:,} bytes, {local_mod.strftime('%H:%M:%S')})")
        
        # Check AWS file
        aws_size = run_ssh_command(f"stat -c '%s' {AWS_BOT_DIR}/{file} 2>/dev/null || echo 'Missing'")
        aws_hash = run_ssh_command(f"md5sum {AWS_BOT_DIR}/{file} 2>/dev/null | cut -d' ' -f1 | cut -c1-8 || echo 'Missing'")
        
        if aws_size == "Missing" or aws_hash == "Missing":
            print(f"   ❌ AWS:    File missing")
            upload_success = False
        else:
            print(f"   ☁️ AWS:    {aws_hash}... ({aws_size} bytes)")
            
            if local_hash == aws_hash and str(local_size) == aws_size:
                print(f"   ✅ Status: SYNCED")
            else:
                print(f"   ❌ Status: DIFFERENT")
                upload_success = False
    
    return upload_success

def check_bot_status():
    """Check if bot is running on AWS"""
    print(f"\n🤖 AWS BOT STATUS")
    print("=" * 25)
    
    # Check for running bot processes
    bot_check = run_ssh_command("pgrep -f 'python.*bot.py' | wc -l")
    
    if bot_check.isdigit() and int(bot_check) > 0:
        process_count = int(bot_check)
        print(f"✅ Bot is running ({process_count} process(es))")
        
        # Get process IDs
        pids = run_ssh_command("pgrep -f 'python.*bot.py'")
        if pids != "Error":
            print(f"🔍 Process IDs: {pids.replace(chr(10), ', ')}")
        
        # Check recent activity
        recent_output = run_ssh_command(f"cd {AWS_BOT_DIR} && tail -2 bot_output.log 2>/dev/null || echo 'No output'")
        if recent_output != "No output" and recent_output != "Error":
            print(f"📋 Recent activity:")
            for line in recent_output.split('\n'):
                if line.strip():
                    print(f"   {line}")
        
        return True
    else:
        print(f"❌ Bot is not running")
        
        # Check for any error logs
        error_check = run_ssh_command(f"cd {AWS_BOT_DIR} && tail -3 bot_output.log 2>/dev/null || echo 'No log'")
        if error_check != "No log" and error_check != "Error":
            print(f"📋 Last output:")
            for line in error_check.split('\n'):
                if line.strip():
                    print(f"   {line}")
        
        return False

def main():
    """Main verification function"""
    print("🔍 AWS UPDATE STATUS VERIFICATION")
    print("=" * 50)
    print(f"🕒 Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Verify uploads
    upload_success = verify_upload_status()
    
    # Check bot status
    bot_running = check_bot_status()
    
    # Summary
    print(f"\n📊 UPDATE STATUS SUMMARY")
    print("=" * 35)
    
    if upload_success and bot_running:
        print("✅ Files uploaded successfully")
        print("✅ Bot restarted and running")
        print("🎉 UPDATE COMPLETED SUCCESSFULLY!")
        print()
        print("🎯 Your AWS bot is now running with:")
        print("   • Latest stop-limit order fixes")
        print("   • Aligned 0.25% trailing stops")
        print("   • Enhanced risk management")
        print("   • All recent optimizations")
        
    elif upload_success and not bot_running:
        print("✅ Files uploaded successfully")
        print("❌ Bot is not running")
        print("⚠️ RESTART REQUIRED")
        print()
        print("🔧 To manually restart:")
        print(f'   ssh -i "{AWS_KEY_FILE}" {AWS_USER}@{AWS_IP}')
        print(f"   cd {AWS_BOT_DIR}")
        print(f"   nohup python bot.py > bot_output.log 2>&1 &")
        
    elif not upload_success and bot_running:
        print("❌ File upload incomplete")
        print("✅ Bot is running (old version)")
        print("⚠️ UPLOAD REQUIRED")
        print()
        print("🔧 Files still need to be uploaded manually")
        
    else:
        print("❌ File upload incomplete")
        print("❌ Bot is not running")
        print("🚨 MANUAL INTERVENTION REQUIRED")
    
    return upload_success and bot_running

if __name__ == "__main__":
    success = main()
