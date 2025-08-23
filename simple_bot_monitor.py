#!/usr/bin/env python3
"""
Simple Bot Monitor - Check bot status without complex dependencies
"""

import os
import time
import json
from datetime import datetime

def check_bot_state():
    """Check bot state file"""
    try:
        with open('bot_state.json', 'r') as f:
            state = json.load(f)
        return state
    except Exception as e:
        return f"❌ Error reading bot state: {e}"

def check_log_file():
    """Check recent bot activity in log"""
    try:
        if os.path.exists('bot_log.txt'):
            with open('bot_log.txt', 'r') as f:
                lines = f.readlines()
            recent_lines = lines[-10:] if len(lines) > 10 else lines
            return recent_lines
        else:
            return ["No log file found"]
    except Exception as e:
        return [f"❌ Error reading log: {e}"]

def check_config():
    """Check current configuration"""
    try:
        with open('enhanced_config.json', 'r') as f:
            config = json.load(f)
        return {
            'current_pair': config.get('current_pair', 'Unknown'),
            'balance_usd': config.get('balance_usd', 'Unknown'),
            'daily_target': config.get('daily_target_profit', 'Unknown'),
            'lstm_enabled': config.get('use_lstm_prediction', False)
        }
    except Exception as e:
        return f"❌ Error reading config: {e}"

def main():
    print("🤖 CRYPTO TRADING BOT - Simple Monitor")
    print("=" * 50)
    print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check bot state
    print("📊 BOT STATE:")
    state = check_bot_state()
    if isinstance(state, dict):
        print(f"   💰 Current Pair: {state.get('current_pair', 'N/A')}")
        print(f"   💵 Balance USD: ${state.get('balance_usd', 'N/A')}")
        print(f"   📈 Daily Profit: ${state.get('daily_profit', 0):.2f}")
        print(f"   🎯 Success Rate: {state.get('success_rate', 0):.1f}%")
        print(f"   🔄 Total Trades: {state.get('total_trades', 0)}")
    else:
        print(f"   {state}")
    print()
    
    # Check configuration
    print("⚙️ CONFIGURATION:")
    config = check_config()
    if isinstance(config, dict):
        print(f"   💱 Trading Pair: {config['current_pair']}")
        print(f"   💰 Balance: ${config['balance_usd']}")
        print(f"   🎯 Daily Target: ${config['daily_target']}")
        print(f"   🧠 LSTM AI: {'✅ Enabled' if config['lstm_enabled'] else '❌ Disabled'}")
    else:
        print(f"   {config}")
    print()
    
    # Check recent activity
    print("📝 RECENT ACTIVITY:")
    recent_logs = check_log_file()
    for log in recent_logs[-5:]:  # Show last 5 lines
        print(f"   {log.strip()}")
    print()
    
    print("🔄 Bot monitoring complete!")
    print("\n💡 To see live activity, check the main bot terminal")

if __name__ == "__main__":
    main()
