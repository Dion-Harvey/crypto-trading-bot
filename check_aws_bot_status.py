#!/usr/bin/env python3
"""
🌐 AWS BOT STATUS CHECKER & STARTER
==================================
Check if bot is running on AWS EC2 and start if needed
"""

import subprocess
import time
import sys
from datetime import datetime

# AWS connection details
AWS_KEY_FILE = r"C:\Users\miste\Documents\cryptobot-key.pem"
AWS_USER = "ubuntu"
AWS_IP = "3.135.216.32"
AWS_BOT_DIR = "/home/ubuntu/crypto-trading-bot"

def run_ssh_command(command, timeout=30):
    """Execute SSH command on AWS instance"""
    try:
        ssh_cmd = [
            "ssh", 
            "-i", AWS_KEY_FILE,
            "-o", "StrictHostKeyChecking=no",
            "-o", "ConnectTimeout=10",
            f"{AWS_USER}@{AWS_IP}",
            command
        ]
        
        print(f"🔄 Executing: {command}")
        result = subprocess.run(ssh_cmd, capture_output=True, text=True, timeout=timeout)
        
        if result.returncode == 0:
            return {"success": True, "output": result.stdout.strip(), "error": None}
        else:
            return {"success": False, "output": result.stdout.strip(), "error": result.stderr.strip()}
            
    except subprocess.TimeoutExpired:
        return {"success": False, "output": "", "error": f"Command timed out after {timeout}s"}
    except Exception as e:
        return {"success": False, "output": "", "error": str(e)}

def check_aws_connection():
    """Test AWS connection"""
    print("🌐 Testing AWS connection...")
    result = run_ssh_command("echo 'AWS Connection Test Successful'", timeout=10)
    
    if result["success"]:
        print(f"✅ AWS Connection: {result['output']}")
        return True
    else:
        print(f"❌ AWS Connection Failed: {result['error']}")
        return False

def check_bot_status():
    """Check if bot is running on AWS"""
    print("\n🔍 Checking bot status on AWS...")
    
    # Check for Python processes
    result = run_ssh_command("pgrep -f 'python.*bot.py' || echo 'No bot process found'")
    
    if result["success"]:
        if "No bot process found" in result["output"]:
            print("❌ Bot is NOT running on AWS")
            return False
        else:
            pids = result["output"].strip().split('\n') if result["output"].strip() else []
            print(f"✅ Bot is running on AWS (PIDs: {', '.join(pids)})")
            
            # Get process details
            for pid in pids:
                if pid.strip():
                    detail_result = run_ssh_command(f"ps aux | grep {pid.strip()} | grep -v grep")
                    if detail_result["success"] and detail_result["output"]:
                        print(f"   Process {pid}: {detail_result['output']}")
            
            return True
    else:
        print(f"❌ Error checking bot status: {result['error']}")
        return False

def check_bot_logs():
    """Check recent bot logs"""
    print("\n📋 Checking recent bot activity...")
    
    # Check if log file exists and get recent entries
    result = run_ssh_command(f"cd {AWS_BOT_DIR} && tail -10 bot_log.txt 2>/dev/null || echo 'No log file found'")
    
    if result["success"]:
        if "No log file found" in result["output"]:
            print("⚠️ No bot log file found")
        else:
            print("📄 Recent bot log entries:")
            for line in result["output"].split('\n'):
                if line.strip():
                    print(f"   {line}")
    
    # Check last modification time of critical files
    files_to_check = ["bot.py", "enhanced_config.json", "bot_state.json"]
    
    for file in files_to_check:
        result = run_ssh_command(f"cd {AWS_BOT_DIR} && stat -c '%Y %n' {file} 2>/dev/null || echo 'File not found: {file}'")
        if result["success"] and "File not found" not in result["output"]:
            try:
                timestamp, filename = result["output"].split(' ', 1)
                mod_time = datetime.fromtimestamp(int(timestamp))
                time_diff = datetime.now() - mod_time
                print(f"📁 {filename}: Modified {time_diff.total_seconds()/3600:.1f} hours ago")
            except:
                print(f"📁 {file}: {result['output']}")

def start_bot():
    """Start the bot on AWS"""
    print("\n🚀 Starting bot on AWS...")
    
    # First, ensure we're in the right directory and activate virtual environment
    start_command = f"""
    cd {AWS_BOT_DIR} && 
    source venv/bin/activate && 
    nohup python bot.py > bot_output.log 2>&1 & 
    echo "Bot started with PID: $!"
    """
    
    result = run_ssh_command(start_command, timeout=15)
    
    if result["success"]:
        print(f"✅ Bot start command executed: {result['output']}")
        
        # Wait a moment and check if it's actually running
        time.sleep(3)
        print("\n🔄 Verifying bot started...")
        return check_bot_status()
    else:
        print(f"❌ Failed to start bot: {result['error']}")
        return False

def restart_bot():
    """Restart the bot (kill existing and start new)"""
    print("\n🔄 Restarting bot on AWS...")
    
    # Kill existing bot processes
    kill_result = run_ssh_command("pkill -f 'python.*bot.py' || echo 'No processes to kill'")
    if kill_result["success"]:
        print(f"🛑 Existing processes: {kill_result['output']}")
    
    time.sleep(2)  # Wait for processes to terminate
    
    # Start new bot
    return start_bot()

def main():
    """Main diagnostic and control function"""
    print("🌐 AWS BOT STATUS CHECKER & CONTROLLER")
    print("=" * 50)
    print(f"🕒 Check Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🔗 Target: {AWS_USER}@{AWS_IP}")
    print(f"📁 Bot Directory: {AWS_BOT_DIR}")
    print()
    
    # Test connection
    if not check_aws_connection():
        print("\n❌ Cannot connect to AWS instance")
        print("💡 Check:")
        print("   - Key file path is correct")
        print("   - AWS instance is running")
        print("   - Security groups allow SSH")
        print("   - Internet connection is stable")
        return False
    
    # Check bot status
    bot_running = check_bot_status()
    
    # Check logs regardless
    check_bot_logs()
    
    # Decide what to do
    if not bot_running:
        print("\n❓ Bot is not running. Would you like to start it?")
        print("   Options:")
        print("   1. Start bot")
        print("   2. Just check status")
        
        # For automation, let's start it automatically
        print("\n🤖 Auto-starting bot...")
        success = start_bot()
        
        if success:
            print("\n✅ BOT SUCCESSFULLY STARTED ON AWS!")
            print("🎯 The bot is now running and monitoring all 16 cryptocurrency pairs")
            print("📊 It will automatically switch to the highest-performing assets")
            print("🚀 Phase 1 & Phase 2 intelligence systems are active")
        else:
            print("\n❌ FAILED TO START BOT")
            print("🔧 Manual intervention may be required")
        
        return success
    else:
        print("\n✅ BOT IS ALREADY RUNNING ON AWS!")
        print("🎯 All systems operational")
        return True

if __name__ == "__main__":
    main()
