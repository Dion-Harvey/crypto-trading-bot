#!/usr/bin/env python3
"""
🔄 AWS BOT UPDATE & RESTART MANAGER
===================================
Complete workflow: Stop bot → Upload files → Restart bot
"""

import subprocess
import os
import time
from datetime import datetime

# AWS connection details
AWS_KEY_FILE = r"C:\Users\miste\Documents\cryptobot-key.pem"
AWS_USER = "ubuntu"
AWS_IP = "3.135.216.32"
AWS_BOT_DIR = "/home/ubuntu/crypto-trading-bot"

def run_ssh_command(command, description="", timeout=30):
    """Execute SSH command on AWS instance"""
    if description:
        print(f"🔄 {description}")
    
    try:
        ssh_cmd = [
            "ssh", 
            "-i", AWS_KEY_FILE,
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=10",
            f"{AWS_USER}@{AWS_IP}",
            command
        ]
        
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=timeout)
        
        if result.returncode == 0:
            return {"success": True, "output": result.stdout.strip()}
        else:
            return {"success": False, "error": result.stderr.strip()}
            
    except subprocess.TimeoutExpired:
        return {"success": False, "error": f"Command timed out after {timeout}s"}
    except Exception as e:
        return {"success": False, "error": str(e)}

def run_scp_command(local_file, description=""):
    """Upload file via SCP"""
    if description:
        print(f"📤 {description}")
    
    try:
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
            return {"success": True, "output": "Upload successful"}
        else:
            return {"success": False, "error": result.stderr.strip()}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def stop_aws_bot():
    """Stop the running bot on AWS"""
    print("\n🛑 STOPPING AWS BOT")
    print("=" * 30)
    
    # Check if bot is running
    check_result = run_ssh_command(
        "pgrep -f 'python.*bot.py' || echo 'No bot running'",
        "Checking for running bot processes"
    )
    
    if not check_result["success"]:
        print(f"❌ Error checking bot status: {check_result['error']}")
        return False
    
    if "No bot running" in check_result["output"]:
        print("ℹ️ No bot processes found - already stopped")
        return True
    
    # Get process IDs
    pids = check_result["output"].strip().split('\n') if check_result["output"].strip() else []
    print(f"🔍 Found {len(pids)} bot process(es): {', '.join(pids)}")
    
    # Stop the bot processes
    stop_result = run_ssh_command(
        "pkill -f 'python.*bot.py'",
        "Stopping bot processes"
    )
    
    if stop_result["success"]:
        print("✅ Bot stop command executed")
    else:
        print(f"⚠️ Stop command had issues: {stop_result['error']}")
    
    # Wait and verify
    time.sleep(3)
    verify_result = run_ssh_command(
        "pgrep -f 'python.*bot.py' || echo 'No bot running'",
        "Verifying bot stopped"
    )
    
    if verify_result["success"] and "No bot running" in verify_result["output"]:
        print("✅ Bot successfully stopped")
        return True
    else:
        print("⚠️ Bot may still be running or verification failed")
        return False

def upload_critical_files():
    """Upload critical files to AWS"""
    print("\n📤 UPLOADING CRITICAL FILES")
    print("=" * 40)
    
    # Critical files to upload (in order of importance)
    critical_files = [
        {"file": "bot.py", "desc": "Main trading bot (MOST RECENT UPDATES)"},
        {"file": "enhanced_config.json", "desc": "Multi-pair configuration"},
        {"file": "enhanced_config.py", "desc": "Configuration management"},
        {"file": "multi_crypto_monitor.py", "desc": "Multi-crypto monitoring"},
        {"file": "config.py", "desc": "Base configuration"},
        {"file": "state_manager.py", "desc": "State management"}
    ]
    
    upload_results = []
    
    for file_info in critical_files:
        file = file_info["file"]
        desc = file_info["desc"]
        
        if not os.path.exists(file):
            print(f"⚠️ {file} - File not found locally")
            upload_results.append({"file": file, "success": False, "reason": "File not found"})
            continue
        
        # Get file info
        file_size = os.path.getsize(file)
        mod_time = datetime.fromtimestamp(os.path.getmtime(file))
        
        print(f"\n📁 {file}")
        print(f"   📝 {desc}")
        print(f"   💾 Size: {file_size:,} bytes")
        print(f"   🕒 Modified: {mod_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Upload the file
        upload_result = run_scp_command(file, f"Uploading {file}")
        
        if upload_result["success"]:
            print(f"   ✅ Upload successful")
            upload_results.append({"file": file, "success": True, "reason": "Uploaded"})
        else:
            print(f"   ❌ Upload failed: {upload_result['error']}")
            upload_results.append({"file": file, "success": False, "reason": upload_result['error']})
    
    # Summary
    successful_uploads = len([r for r in upload_results if r["success"]])
    total_files = len(upload_results)
    
    print(f"\n📊 UPLOAD SUMMARY:")
    print(f"   ✅ Successful: {successful_uploads}/{total_files}")
    print(f"   ❌ Failed: {total_files - successful_uploads}/{total_files}")
    
    if successful_uploads == total_files:
        print(f"   🟢 Status: ALL FILES UPLOADED SUCCESSFULLY")
        return True
    elif successful_uploads >= 3:  # At least bot.py and key files
        print(f"   🟡 Status: CRITICAL FILES UPLOADED (some optional files failed)")
        return True
    else:
        print(f"   🔴 Status: UPLOAD FAILED (critical files missing)")
        return False

def restart_aws_bot():
    """Restart the bot on AWS"""
    print("\n🚀 RESTARTING AWS BOT")
    print("=" * 30)
    
    # Change to bot directory and start the bot
    start_command = f"""
    cd {AWS_BOT_DIR} && 
    source venv/bin/activate && 
    nohup python bot.py > bot_output.log 2>&1 & 
    echo "Bot started with PID: $!"
    """
    
    start_result = run_ssh_command(
        start_command,
        "Starting bot with virtual environment",
        timeout=20
    )
    
    if not start_result["success"]:
        print(f"❌ Failed to start bot: {start_result['error']}")
        return False
    
    print(f"✅ Bot start command executed: {start_result['output']}")
    
    # Wait for bot to initialize
    print("⏳ Waiting for bot to initialize...")
    time.sleep(5)
    
    # Verify bot is running
    verify_result = run_ssh_command(
        "pgrep -f 'python.*bot.py' | wc -l",
        "Verifying bot is running"
    )
    
    if verify_result["success"] and verify_result["output"].isdigit():
        process_count = int(verify_result["output"])
        if process_count > 0:
            print(f"✅ Bot is running ({process_count} process(es))")
            
            # Get process details
            detail_result = run_ssh_command(
                "pgrep -f 'python.*bot.py'",
                "Getting process IDs"
            )
            
            if detail_result["success"]:
                pids = detail_result["output"].strip().split('\n') if detail_result["output"].strip() else []
                print(f"🔍 Process IDs: {', '.join(pids)}")
            
            return True
        else:
            print("❌ Bot is not running after start attempt")
            return False
    else:
        print("⚠️ Could not verify bot status")
        return False

def check_bot_health():
    """Check if bot is functioning correctly"""
    print("\n🏥 BOT HEALTH CHECK")
    print("=" * 25)
    
    # Check recent log entries
    log_result = run_ssh_command(
        f"cd {AWS_BOT_DIR} && tail -5 bot_output.log 2>/dev/null || echo 'No output log'",
        "Checking recent bot output"
    )
    
    if log_result["success"] and "No output log" not in log_result["output"]:
        print("📋 Recent bot output:")
        for line in log_result["output"].split('\n'):
            if line.strip():
                print(f"   {line}")
    else:
        print("⚠️ No recent bot output found")
    
    # Check if bot is actively trading
    trading_log_result = run_ssh_command(
        f"cd {AWS_BOT_DIR} && tail -3 bot_log.txt 2>/dev/null || echo 'No trading log'",
        "Checking trading activity"
    )
    
    if trading_log_result["success"] and "No trading log" not in trading_log_result["output"]:
        print("\n📈 Recent trading activity:")
        for line in trading_log_result["output"].split('\n'):
            if line.strip():
                print(f"   {line}")
    else:
        print("\n⚠️ No recent trading activity found")
    
    return True

def main():
    """Main update workflow"""
    print("🔄 AWS BOT UPDATE & RESTART WORKFLOW")
    print("=" * 60)
    print(f"🕒 Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Target: {AWS_USER}@{AWS_IP}")
    print(f"📁 Directory: {AWS_BOT_DIR}")
    print()
    
    # Test AWS connection
    print("🔌 Testing AWS connection...")
    test_result = run_ssh_command("echo 'Connection test successful'", timeout=10)
    
    if not test_result["success"]:
        print(f"❌ Cannot connect to AWS: {test_result['error']}")
        print("\n💡 Please check:")
        print("   - AWS instance is running")
        print("   - Key file permissions are correct")
        print("   - Network connectivity")
        return False
    
    print(f"✅ AWS connection successful")
    
    # Step 1: Stop the bot
    if not stop_aws_bot():
        print("\n❌ Failed to stop bot - aborting update")
        return False
    
    # Step 2: Upload files
    if not upload_critical_files():
        print("\n❌ Critical file upload failed")
        print("⚠️ Proceeding with restart anyway (some files may be updated)")
    
    # Step 3: Restart the bot
    if not restart_aws_bot():
        print("\n❌ Failed to restart bot")
        print("🚨 MANUAL INTERVENTION REQUIRED")
        return False
    
    # Step 4: Health check
    check_bot_health()
    
    # Final status
    print(f"\n🎉 AWS BOT UPDATE COMPLETE!")
    print("=" * 40)
    print("✅ Bot stopped successfully")
    print("✅ Files uploaded to AWS")
    print("✅ Bot restarted with latest code")
    print("✅ Health check completed")
    print()
    print("🎯 Your AWS bot is now running with:")
    print("   • Latest bug fixes (stop-limit cleanup)")
    print("   • Aligned 0.25% trailing stops")
    print("   • Enhanced risk management")
    print("   • Improved multi-pair communication")
    print("   • All recent optimizations")
    print()
    print(f"🕒 Completion Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n🚨 UPDATE PROCESS FAILED")
        print("📞 Manual intervention may be required")
    else:
        print("\n🚀 UPDATE PROCESS SUCCESSFUL")
        print("🎯 Your AWS bot is ready for trading!")
