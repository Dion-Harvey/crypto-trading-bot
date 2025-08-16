#!/usr/bin/env python3
"""
🔄 AWS Reconnection Helper
Helps reconnect to AWS once instance is restarted
"""

import subprocess
import time

def test_connection(ip_address, max_attempts=5):
    """Test SSH connection to AWS instance"""
    key_file = r"C:\Users\miste\Documents\cryptobot-key.pem"
    
    print(f"🔍 Testing connection to {ip_address}...")
    
    for attempt in range(1, max_attempts + 1):
        print(f"🔄 Attempt {attempt}/{max_attempts}")
        
        try:
            # Quick connection test
            cmd = [
                'ssh', 
                '-i', key_file,
                '-o', 'ConnectTimeout=10',
                '-o', 'StrictHostKeyChecking=no',
                f'ubuntu@{ip_address}',
                'echo "Connection successful"'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            
            if result.returncode == 0 and "Connection successful" in result.stdout:
                print(f"✅ Connection successful!")
                return True
            else:
                print(f"❌ Connection failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Connection timeout")
        except Exception as e:
            print(f"❌ Error: {e}")
        
        if attempt < max_attempts:
            print("⏳ Waiting 30 seconds before retry...")
            time.sleep(30)
    
    return False

def check_bot_status(ip_address):
    """Check if bot is running on AWS"""
    key_file = r"C:\Users\miste\Documents\cryptobot-key.pem"
    
    print(f"\n🤖 Checking bot status on {ip_address}...")
    
    try:
        cmd = [
            'ssh', 
            '-i', key_file,
            '-o', 'ConnectTimeout=10',
            '-o', 'StrictHostKeyChecking=no',
            f'ubuntu@{ip_address}',
            'pgrep -f bot.py && echo "Bot running" || echo "Bot not running"'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            print(f"📊 Status: {result.stdout.strip()}")
            return "Bot running" in result.stdout
        else:
            print(f"⚠️ Could not check bot status: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error checking bot status: {e}")
        return False

def restart_bot(ip_address):
    """Restart bot with uploaded files"""
    key_file = r"C:\Users\miste\Documents\cryptobot-key.pem"
    
    print(f"\n🚀 Restarting bot on {ip_address}...")
    
    try:
        # Stop existing bot and start new one
        cmd = [
            'ssh', 
            '-i', key_file,
            '-o', 'ConnectTimeout=10',
            '-o', 'StrictHostKeyChecking=no',
            f'ubuntu@{ip_address}',
            'cd ~/crypto-trading-bot && pkill -f bot.py; nohup python bot.py > bot_output.log 2>&1 &'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ Bot restart command executed")
            
            # Wait and check if it started
            time.sleep(5)
            if check_bot_status(ip_address):
                print("🎉 Bot restarted successfully!")
                return True
            else:
                print("⚠️ Bot may not have started properly")
                return False
        else:
            print(f"❌ Bot restart failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error restarting bot: {e}")
        return False

def main():
    """Main reconnection helper"""
    print("🔄 AWS RECONNECTION HELPER")
    print("=" * 40)
    print(f"🕒 Time: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    ip_address = "3.135.216.32"
    
    print("📋 Instructions:")
    print("1. Go to AWS EC2 Console")
    print("2. Start your instance if it's stopped")
    print("3. Note if the IP address changed")
    print("4. Press Enter when instance is running")
    print()
    
    input("Press Enter when your AWS instance is running...")
    
    # Test connection
    if test_connection(ip_address):
        print("\n🎉 Connection restored!")
        
        # Check bot status
        bot_running = check_bot_status(ip_address)
        
        if not bot_running:
            print("\n🔄 Bot is not running. Attempting restart...")
            restart_bot(ip_address)
        else:
            print("✅ Bot is already running!")
            
        # Final status
        key_file = r"C:\Users\miste\Documents\cryptobot-key.pem"
        print(f"\n📊 FINAL STATUS:")
        print(f"🔗 Connection: ✅ Working")
        print(f"🤖 Bot: {'✅ Running' if check_bot_status(ip_address) else '❌ Issues'}")
        print(f"\n🔧 Manual commands:")
        print(f'ssh -i "{key_file}" ubuntu@{ip_address}')
        print(f"tail -f ~/crypto-trading-bot/bot_output.log")
        
    else:
        print("\n❌ Connection still failed")
        print("💡 Possible issues:")
        print("   • Instance still starting (wait 2-3 minutes)")
        print("   • IP address changed (check AWS console)")
        print("   • Security group needs updating")
        print("   • Instance has issues (try recreating)")

if __name__ == "__main__":
    main()
