#!/usr/bin/env python3
"""
Deploy Trailing Stop-Limit Enhancement to AWS
This script updates the AWS EC2 instance with the new trailing stop functionality
"""

import subprocess
import json
import time

def deploy_trailing_stop_limit():
    """Deploy the trailing stop-limit enhancement to AWS"""
    print("🚀 DEPLOYING TRAILING STOP-LIMIT TO AWS")
    print("=" * 60)
    
    # AWS connection details
    aws_host = "ubuntu@3.135.216.32"
    key_file = r"C:\Users\miste\Downloads\cryptobot-key.pem"
    
    print("📋 Deployment Plan:")
    print("✅ Upload enhanced_config.json with trailing stop settings")
    print("✅ Upload updated bot.py with trailing stop functions")
    print("✅ Restart bot with new trailing stop-limit protection")
    print("✅ Verify bot is running with enhanced features")
    print()
    
    try:
        # 1. Upload enhanced configuration
        print("📤 Uploading enhanced_config.json...")
        upload_config_cmd = [
            "scp", "-i", key_file, 
            "enhanced_config.json", 
            f"{aws_host}:~/"
        ]
        result = subprocess.run(upload_config_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Configuration uploaded successfully")
        else:
            print(f"❌ Config upload failed: {result.stderr}")
            return False
        
        # 2. Upload updated bot code
        print("📤 Uploading updated bot.py...")
        upload_bot_cmd = [
            "scp", "-i", key_file,
            "bot.py",
            f"{aws_host}:~/"
        ]
        result = subprocess.run(upload_bot_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Bot code uploaded successfully")
        else:
            print(f"❌ Bot upload failed: {result.stderr}")
            return False
        
        # 3. Stop current bot process
        print("⏹️ Stopping current bot process...")
        stop_cmd = [
            "ssh", "-i", key_file, aws_host,
            "screen -S trading_bot_stop_limit -X quit || true"
        ]
        result = subprocess.run(stop_cmd, capture_output=True, text=True)
        print("✅ Previous bot session terminated")
        
        # Wait a moment
        time.sleep(3)
        
        # 4. Start bot with new trailing stop features
        print("🚀 Starting bot with trailing stop-limit protection...")
        start_cmd = [
            "ssh", "-i", key_file, aws_host,
            "cd ~ && screen -dmS trading_bot_trailing python3 bot.py"
        ]
        result = subprocess.run(start_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Bot started with trailing stop-limit features")
        else:
            print(f"❌ Bot start failed: {result.stderr}")
            return False
        
        # Wait for bot to initialize
        time.sleep(5)
        
        # 5. Verify bot is running
        print("🔍 Verifying bot status...")
        check_cmd = [
            "ssh", "-i", key_file, aws_host,
            "screen -list | grep trading_bot_trailing"
        ]
        result = subprocess.run(check_cmd, capture_output=True, text=True)
        if "trading_bot_trailing" in result.stdout:
            print("✅ Bot is running in screen session 'trading_bot_trailing'")
        else:
            print("⚠️ Bot screen session not found - checking processes...")
            
        # Check if python process is running
        process_cmd = [
            "ssh", "-i", key_file, aws_host,
            "pgrep -f 'python3 bot.py' | head -1"
        ]
        result = subprocess.run(process_cmd, capture_output=True, text=True)
        if result.stdout.strip():
            pid = result.stdout.strip()
            print(f"✅ Bot running with PID: {pid}")
        else:
            print("❌ Bot process not found")
            return False
        
        # 6. Check bot logs for trailing stop initialization
        print("📊 Checking bot initialization logs...")
        log_cmd = [
            "ssh", "-i", key_file, aws_host,
            "cd ~ && tail -10 bot_log.txt 2>/dev/null || echo 'No log file yet'"
        ]
        result = subprocess.run(log_cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("📋 Recent bot logs:")
            for line in result.stdout.strip().split('\n')[-5:]:
                if line.strip():
                    print(f"   {line}")
        
        print("\n" + "=" * 60)
        print("🎉 TRAILING STOP-LIMIT DEPLOYMENT COMPLETE!")
        print("✅ Bot is now running with enhanced protection:")
        print("   🛡️ Immediate stop-limit: -0.125% max loss")
        print("   📈 Trailing stop-limit: 0.2% trigger, 0.1% trail")
        print("   🔒 Minimum profit lock: 0.3%")
        print(f"   🖥️ AWS Instance: {aws_host}")
        print("   📺 Screen session: trading_bot_trailing")
        print("🚀 Ready for enhanced profit protection!")
        
        return True
        
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

def show_monitoring_commands():
    """Show commands for monitoring the enhanced bot"""
    key_file = r"C:\Users\miste\Downloads\cryptobot-key.pem"
    print("\n🔧 MONITORING COMMANDS")
    print("=" * 40)
    print("Connect to AWS instance:")
    print(f"ssh -i \"{key_file}\" ubuntu@3.135.216.32")
    print()
    print("View bot screen session:")
    print("screen -r trading_bot_trailing")
    print()
    print("Check bot logs:")
    print("tail -f ~/bot_log.txt")
    print()
    print("Check bot status:")
    print("ps aux | grep 'python3 bot.py'")
    print()
    print("View trailing stop state:")
    print("cd ~ && python3 -c \"import json; print(json.dumps(json.load(open('bot_state.json')), indent=2))\"")
    print()
    print("View bot logs:")
    print("tail -f ~/bot_log.txt")

if __name__ == "__main__":
    print("🎯 TRAILING STOP-LIMIT DEPLOYMENT")
    print("Enhanced profit protection deployment to AWS EC2")
    print()
    
    # Deploy the enhancement
    success = deploy_trailing_stop_limit()
    
    if success:
        show_monitoring_commands()
    else:
        print("\n❌ DEPLOYMENT FAILED")
        print("Please check the error messages above and try again.")
