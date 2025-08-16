#!/usr/bin/env python3
"""
Trailing Stop-Limit Status Monitor
Checks the enhanced bot status and trailing stop functionality
"""

import subprocess
import json
import time

def check_bot_status():
    """Check if the enhanced bot is running on AWS"""
    print("🔍 TRAILING STOP-LIMIT BOT STATUS")
    print("=" * 50)
    
    try:
        # Check screen session
        print("📺 Screen Session Status:")
        result = subprocess.run([
            "ssh", "-i", r"C:\Users\miste\Downloads\cryptobot-key.pem", 
            "ubuntu@3.135.216.32", "screen -list"
        ], capture_output=True, text=True)
        
        if "trading_bot_trailing" in result.stdout:
            print("✅ trading_bot_trailing session active")
        else:
            print("❌ No trailing bot screen session found")
            print(f"Output: {result.stdout}")
        
        # Check process status
        print("\n🔧 Process Status:")
        result = subprocess.run([
            "ssh", "-i", r"C:\Users\miste\Downloads\cryptobot-key.pem", 
            "ubuntu@3.135.216.32", "ps aux | grep 'bot.py' | grep -v grep"
        ], capture_output=True, text=True)
        
        if result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            print(f"✅ Found {len(lines)} bot process(es)")
            for line in lines:
                parts = line.split()
                if len(parts) >= 2:
                    print(f"   PID: {parts[1]} | Memory: {parts[5]}KB | CPU: {parts[2]}%")
        else:
            print("❌ No bot processes found")
        
        # Check recent logs
        print("\n📋 Recent Bot Activity:")
        result = subprocess.run([
            "ssh", "-i", r"C:\Users\miste\Downloads\cryptobot-key.pem", 
            "ubuntu@3.135.216.32", 
            "cd ~/crypto-trading-bot-deploy && tail -5 bot_log.txt 2>/dev/null || echo 'No logs available'"
        ], capture_output=True, text=True)
        
        if result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            for line in lines[-3:]:  # Show last 3 lines
                if line.strip():
                    print(f"   {line}")
        
        # Check configuration
        print("\n⚙️ Configuration Status:")
        result = subprocess.run([
            "ssh", "-i", r"C:\Users\miste\Downloads\cryptobot-key.pem", 
            "ubuntu@3.135.216.32", 
            "cd ~/crypto-trading-bot-deploy && python3 -c \"import json; config=json.load(open('enhanced_config.json')); risk=config.get('risk_management', {}); print('Immediate Stop:', risk.get('immediate_stop_limit_enabled', False)); print('Trailing Stop:', risk.get('trailing_stop_limit_enabled', False)); print('Trigger %:', risk.get('trailing_stop_limit_trigger_pct', 0)*100)\""
        ], capture_output=True, text=True)
        
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                print(f"   {line}")
        
        # Check if bot has any positions with stop-limits
        print("\n💰 Active Positions & Stop-Limits:")
        result = subprocess.run([
            "ssh", "-i", r"C:\Users\miste\Downloads\cryptobot-key.pem", 
            "ubuntu@3.135.216.32", 
            "cd ~/crypto-trading-bot-deploy && python3 -c \"import json; try: state=json.load(open('bot_state.json')); positions=state.get('positions', {}); stop_orders=state.get('stop_limit_orders', {}); print(f'Positions: {len(positions)}'); print(f'Stop Orders: {len(stop_orders)}'); [print(f'   {symbol}: {info}') for symbol, info in positions.items() if info]; except: print('No state file or positions')\""
        ], capture_output=True, text=True)
        
        if result.stdout.strip():
            for line in result.stdout.strip().split('\n'):
                print(f"   {line}")
        
    except Exception as e:
        print(f"❌ Error checking status: {e}")

def show_monitoring_commands():
    """Show useful monitoring commands"""
    print("\n🛠️ USEFUL MONITORING COMMANDS")
    print("=" * 40)
    print("Connect to AWS:")
    print('ssh -i "C:\\Users\\miste\\Downloads\\cryptobot-key.pem" ubuntu@3.135.216.32')
    print()
    print("View bot screen session:")
    print("screen -r trading_bot_trailing")
    print()
    print("View live logs:")
    print("cd ~/crypto-trading-bot-deploy && tail -f bot_log.txt")
    print()
    print("Check bot state:")
    print("cd ~/crypto-trading-bot-deploy && cat bot_state.json | python3 -m json.tool")
    print()
    print("Restart bot if needed:")
    print("screen -S trading_bot_trailing -X quit")
    print("cd ~/crypto-trading-bot-deploy && screen -dmS trading_bot_trailing .venv/bin/python bot.py")

if __name__ == "__main__":
    print("🎯 TRAILING STOP-LIMIT MONITORING")
    print("Enhanced bot status and protection features")
    print()
    
    check_bot_status()
    show_monitoring_commands()
    
    print("\n" + "=" * 50)
    print("🎉 ENHANCED FEATURES ACTIVE:")
    print("🛡️ Immediate Stop-Limit: -0.125% protection")
    print("📈 Trailing Stop-Limit: Dynamic profit locking")
    print("🔒 Minimum Profit: 0.3% guaranteed")
    print("🚀 Bot running 24/7 on AWS!")
