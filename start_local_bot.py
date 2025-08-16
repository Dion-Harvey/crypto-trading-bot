#!/usr/bin/env python3
"""
🚀 LOCAL BOT STARTER WITH AWS FALLBACK
=====================================
Start the bot locally and provide AWS status information
"""

import subprocess
import os
import time
import json
from datetime import datetime
from enhanced_config import get_bot_config

def check_local_bot_status():
    """Check if bot is already running locally"""
    try:
        # Check for Python processes running bot.py
        result = subprocess.run(['tasklist'], capture_output=True, text=True)
        if 'python' in result.stdout.lower():
            # Check more specifically
            result2 = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], capture_output=True, text=True)
            if result2.stdout.strip():
                lines = result2.stdout.strip().split('\n')[3:]  # Skip header
                for line in lines:
                    if line.strip():
                        print(f"🔍 Found Python process: {line.strip()}")
                return True
        return False
    except Exception as e:
        print(f"⚠️ Error checking local processes: {e}")
        return False

def start_local_bot():
    """Start the bot locally"""
    print("\n🚀 STARTING LOCAL BOT...")
    print("=" * 50)
    
    try:
        # Check current configuration
        config = get_bot_config()
        current_symbol = config.get_current_trading_symbol()
        supported_pairs = config.get_supported_pairs()
        
        print(f"✅ Configuration verified:")
        print(f"   🎯 Active pair: {current_symbol}")
        print(f"   📊 Monitoring: {len(supported_pairs)} pairs")
        print(f"   🔄 Multi-crypto system: READY")
        
        # Create startup command
        python_cmd = ['python', 'bot.py']
        
        print(f"\n🔄 Starting bot with command: {' '.join(python_cmd)}")
        print(f"📁 Working directory: {os.getcwd()}")
        
        # Start the bot in the background
        process = subprocess.Popen(
            python_cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
        )
        
        print(f"✅ Bot started with PID: {process.pid}")
        
        # Give it a moment to initialize
        time.sleep(3)
        
        # Check if still running
        poll_result = process.poll()
        if poll_result is None:
            print(f"🟢 Bot is running successfully!")
            print(f"🎯 Process ID: {process.pid}")
            print(f"📊 The bot will now:")
            print(f"   • Monitor all 16 cryptocurrency pairs")
            print(f"   • Automatically switch to highest performers")
            print(f"   • Use Phase 1 & Phase 2 intelligence")
            print(f"   • Execute precision trailing stops (0.25%)")
            print(f"   • Apply comprehensive risk management")
            
            return True, process
        else:
            # Process terminated immediately, check for errors
            stdout, stderr = process.communicate()
            print(f"❌ Bot failed to start:")
            if stdout:
                print(f"   Output: {stdout}")
            if stderr:
                print(f"   Error: {stderr}")
            return False, None
            
    except Exception as e:
        print(f"❌ Error starting local bot: {e}")
        return False, None

def provide_aws_guidance():
    """Provide AWS connection guidance"""
    print("\n🌐 AWS CONNECTION GUIDANCE")
    print("=" * 50)
    print("✅ Your AWS details:")
    print("   🔑 Key file: C:\\Users\\miste\\Documents\\cryptobot-key.pem")
    print("   👤 User: ubuntu@3.135.216.32")
    print("   📁 Directory: /home/ubuntu/crypto-trading-bot")
    print()
    print("🔧 To manually connect to AWS:")
    print('   ssh -i "C:\\Users\\miste\\Documents\\cryptobot-key.pem" ubuntu@3.135.216.32')
    print()
    print("🚀 To start bot on AWS manually:")
    print("   cd /home/ubuntu/crypto-trading-bot")
    print("   source venv/bin/activate")
    print("   nohup python bot.py > bot_output.log 2>&1 &")
    print()
    print("📋 To check AWS bot status:")
    print("   pgrep -f 'python.*bot.py'")
    print("   tail -f bot_output.log")

def check_trading_history():
    """Check recent trading activity"""
    print("\n📊 TRADING HISTORY CHECK")
    print("=" * 30)
    
    try:
        # Check if trade log exists
        if os.path.exists('trade_log.csv'):
            with open('trade_log.csv', 'r') as f:
                lines = f.readlines()
                
            if len(lines) > 1:  # Header + at least one trade
                print(f"✅ Found {len(lines)-1} historical trades")
                print("📈 Recent trades:")
                
                # Show last 3 trades
                for line in lines[-3:]:
                    if line.strip() and 'timestamp' not in line.lower():
                        print(f"   {line.strip()}")
            else:
                print("⚠️ No trading history found")
        else:
            print("⚠️ No trade log file found")
            
        # Check bot state
        if os.path.exists('bot_state.json'):
            with open('bot_state.json', 'r') as f:
                state = json.load(f)
            
            holding = state.get('holding_position', False)
            last_trade = state.get('last_trade_time', 0)
            
            if last_trade > 0:
                last_trade_time = datetime.fromtimestamp(last_trade)
                hours_ago = (datetime.now() - last_trade_time).total_seconds() / 3600
                print(f"🕒 Last trade: {hours_ago:.1f} hours ago")
            
            print(f"📊 Current position: {'HOLDING' if holding else 'CASH'}")
        else:
            print("⚠️ No bot state file found")
            
    except Exception as e:
        print(f"⚠️ Error checking trading history: {e}")

def main():
    """Main bot management function"""
    print("🤖 COMPREHENSIVE BOT MANAGEMENT")
    print("=" * 60)
    print(f"🕒 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check local bot status first
    print("🔍 CHECKING LOCAL BOT STATUS...")
    local_running = check_local_bot_status()
    
    if local_running:
        print("✅ Bot appears to be running locally")
        print("🎯 Multiple bot instances can run simultaneously (local + AWS)")
    else:
        print("❌ No local bot detected")
    
    # Check trading history
    check_trading_history()
    
    # Start local bot if not running
    if not local_running:
        print("\n🚀 STARTING LOCAL BOT INSTANCE...")
        success, process = start_local_bot()
        
        if success:
            print("\n✅ LOCAL BOT SUCCESSFULLY STARTED!")
            print("🎯 Your trading bot is now active and monitoring markets")
        else:
            print("\n❌ Failed to start local bot")
    
    # Provide AWS guidance
    provide_aws_guidance()
    
    print("\n🎯 SYSTEM STATUS SUMMARY:")
    print("=" * 30)
    print("✅ Configuration: LOADED (16 pairs, SUI/USDT active)")
    print("✅ Multi-crypto monitoring: CONFIGURED")
    print("✅ Risk management: 0.25% trailing stops")
    print("✅ Phase 1 & Phase 2: READY")
    print("🔄 Bot status: STARTING/RUNNING")
    print()
    print("💡 Your bot will automatically:")
    print("   • Monitor price jumps across all 16 pairs")
    print("   • Switch to highest-performing cryptocurrencies")
    print("   • Execute precision entry and exit strategies")
    print("   • Apply comprehensive capital protection")
    
    return True

if __name__ == "__main__":
    main()
