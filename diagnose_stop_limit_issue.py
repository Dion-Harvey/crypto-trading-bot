#!/usr/bin/env python3
"""
Stop-Limit Order Diagnostic Tool
Helps identify why stop-limit orders aren't being placed after BUY orders
"""

import subprocess
import json
import time

def check_recent_buy_orders():
    """Check recent BUY order attempts and their success/failure"""
    print("🔍 ANALYZING RECENT BUY ORDER ACTIVITY")
    print("=" * 60)
    
    try:
        # Get recent logs with BUY order activity
        result = subprocess.run([
            "ssh", "-i", r"C:\Users\miste\Downloads\cryptobot-key.pem", 
            "ubuntu@3.135.216.32", 
            "cd ~/crypto-trading-bot-deploy && tail -100 bot_log.txt | grep -E 'BUY|MARKET ORDER|STOP-LIMIT|Error|failed|No BTC amount'"
        ], capture_output=True, text=True)
        
        if result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            print(f"📋 Found {len(lines)} relevant log entries:")
            print()
            
            # Analyze the log entries
            buy_attempts = 0
            successful_buys = 0
            failed_buys = 0
            stop_limits_placed = 0
            stop_limit_failures = 0
            
            for line in lines[-20:]:  # Show last 20 relevant entries
                print(f"   {line}")
                
                if "BUY ORDER:" in line and "✅" in line:
                    successful_buys += 1
                elif "BUY ORDER" in line and "❌" in line:
                    failed_buys += 1
                elif "MARKET ORDER PLACED" in line:
                    buy_attempts += 1
                elif "STOP-LIMIT ORDER PLACED" in line:
                    stop_limits_placed += 1
                elif "No BTC amount to protect" in line:
                    stop_limit_failures += 1
            
            print(f"\n📊 SUMMARY:")
            print(f"   BUY Attempts: {buy_attempts}")
            print(f"   Successful BUYs: {successful_buys}")
            print(f"   Failed BUYs: {failed_buys}")
            print(f"   Stop-Limits Placed: {stop_limits_placed}")
            print(f"   Stop-Limit Failures: {stop_limit_failures}")
            
            if stop_limit_failures > 0:
                print(f"\n⚠️ ISSUE DETECTED: {stop_limit_failures} stop-limit failures")
                print("   This suggests BUY orders are failing but being logged as successful")
            
        else:
            print("❌ No recent BUY order activity found")
    
    except Exception as e:
        print(f"❌ Error checking logs: {e}")

def check_account_balance():
    """Check current account balance to see if there are funds for trading"""
    print(f"\n💰 CHECKING ACCOUNT BALANCE")
    print("=" * 40)
    
    try:
        # Get current bot status that includes balance
        result = subprocess.run([
            "ssh", "-i", r"C:\Users\miste\Downloads\cryptobot-key.pem", 
            "ubuntu@3.135.216.32", 
            "cd ~/crypto-trading-bot-deploy && tail -50 bot_log.txt | grep -E 'Balances|USDC|BTC|Portfolio'"
        ], capture_output=True, text=True)
        
        if result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            print("📋 Recent balance information:")
            for line in lines[-5:]:
                print(f"   {line}")
        else:
            print("⚠️ No recent balance information found")
    
    except Exception as e:
        print(f"❌ Error checking balance: {e}")

def check_order_size_requirements():
    """Check if order sizes meet minimum requirements"""
    print(f"\n📏 CHECKING ORDER SIZE REQUIREMENTS")
    print("=" * 50)
    
    try:
        # Get recent position sizing logs
        result = subprocess.run([
            "ssh", "-i", r"C:\Users\miste\Downloads\cryptobot-key.pem", 
            "ubuntu@3.135.216.32", 
            "cd ~/crypto-trading-bot-deploy && tail -100 bot_log.txt | grep -E 'Final:|Target Position|too small|minimum'"
        ], capture_output=True, text=True)
        
        if result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            print("📋 Recent position sizing:")
            for line in lines[-10:]:
                print(f"   {line}")
                
            # Check for minimum order issues
            if any("too small" in line for line in lines):
                print("\n⚠️ ISSUE DETECTED: Order sizes too small")
                print("   Orders below minimum requirements will fail")
            else:
                print("\n✅ Order sizes appear to meet minimum requirements")
                
        else:
            print("❌ No recent position sizing information found")
    
    except Exception as e:
        print(f"❌ Error checking order sizes: {e}")

def provide_recommendations():
    """Provide recommendations based on findings"""
    print(f"\n💡 RECOMMENDATIONS")
    print("=" * 30)
    
    print("If stop-limit orders are not being placed:")
    print("1. Check if BUY orders are actually successful")
    print("2. Verify account has sufficient USDC balance")
    print("3. Ensure order sizes meet minimum requirements ($10+ notional)")
    print("4. Check for API errors in the logs")
    print("5. Monitor the next BUY order attempt")
    
    print(f"\n🔧 MONITORING COMMANDS:")
    print('ssh -i "C:\\Users\\miste\\Downloads\\cryptobot-key.pem" ubuntu@3.135.216.32')
    print("cd ~/crypto-trading-bot-deploy && tail -f bot_log.txt | grep -E 'BUY|STOP|Error'")

if __name__ == "__main__":
    print("🚀 STOP-LIMIT DIAGNOSTIC TOOL")
    print("Analyzing why stop-limit orders aren't being placed...")
    print()
    
    check_recent_buy_orders()
    check_account_balance()
    check_order_size_requirements()
    provide_recommendations()
    
    print("\n" + "=" * 60)
    print("🎯 DIAGNOSTIC COMPLETE")
    print("Monitor the next BUY order to see if the issue is resolved")
