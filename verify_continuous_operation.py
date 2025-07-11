#!/usr/bin/env python3
"""
Verification script to confirm the bot will run continuously without automatic stops
"""

import re
import sys

def verify_bot_continuous_operation():
    """
    Analyze bot.py to ensure it will run continuously without automatic stops
    """
    print("🔍 Verifying Bot Continuous Operation Configuration")
    print("="*60)
    
    try:
        with open('bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for removed automatic stopping patterns
        issues = []
        
        # Check for daily loss automatic pausing
        if 'sleep(3600)' in content or 'sleep.*3600' in content:
            issues.append("❌ Found 1-hour sleep (daily loss pause) - should be removed")
        else:
            print("✅ No daily loss automatic pausing found")
        
        # Check for consecutive loss cooldowns
        if 'sleep(900)' in content or 'sleep.*900' in content:
            issues.append("❌ Found 15-minute cooldown (consecutive losses) - should be removed")
        else:
            print("✅ No consecutive loss automatic cooldowns found")
        
        # Check for system exit calls
        if re.search(r'sys\.exit|exit\(\)', content):
            issues.append("⚠️ Found sys.exit() calls - verify these are only for error conditions")
        
        # Check for break statements in main loop (while True at function level)
        # Look for the main run_continuously function
        run_continuously_match = re.search(r'def run_continuously.*?while True:(.*?)(?=def|\Z)', content, re.DOTALL)
        if run_continuously_match:
            main_loop_content = run_continuously_match.group(1)
            main_loop_breaks = re.findall(r'\n\s*break\s*$', main_loop_content, re.MULTILINE)
            if main_loop_breaks:
                issues.append(f"⚠️ Found {len(main_loop_breaks)} break statements in main trading loop - verify these are appropriate")
            else:
                print("✅ No break statements found in main trading loop")
        else:
            issues.append("⚠️ Could not locate main trading loop for analysis")
        
        # Verify warning messages are present instead of stops
        if 'continuing trading as requested' in content:
            print("✅ Found warning messages instead of automatic stops")
        else:
            issues.append("⚠️ Warning messages for loss limits not found")
        
        # Check that only manual stop is via KeyboardInterrupt
        if 'KeyboardInterrupt' in content:
            print("✅ Manual stop via Ctrl+C (KeyboardInterrupt) is properly handled")
        else:
            issues.append("❌ KeyboardInterrupt handler not found")
        
        # Summary
        print("\n" + "="*60)
        if not issues:
            print("🎉 VERIFICATION PASSED: Bot configured for continuous operation!")
            print("📝 Summary:")
            print("   • No automatic daily loss pausing")
            print("   • No automatic consecutive loss cooldowns") 
            print("   • Warning messages instead of stops")
            print("   • Only stops on manual Ctrl+C or fatal errors")
            print("   • Trade timing cooldowns remain (prevents overtrading)")
            
            return True
        else:
            print("⚠️ VERIFICATION ISSUES FOUND:")
            for issue in issues:
                print(f"   {issue}")
            return False
            
    except FileNotFoundError:
        print("❌ bot.py not found in current directory")
        return False
    except Exception as e:
        print(f"❌ Error reading bot.py: {e}")
        return False

def check_current_configuration():
    """
    Display current bot configuration related to continuous operation
    """
    print("\n🔧 Current Configuration Check")
    print("="*30)
    
    try:
        with open('enhanced_config.json', 'r') as f:
            import json
            config = json.load(f)
        
        risk_config = config.get('risk_management', {})
        
        print(f"Daily Loss Limit: ${risk_config.get('daily_loss_limit_usd', 'Not set')}")
        print(f"Max Consecutive Losses: {risk_config.get('max_consecutive_losses', 'Not set')}")
        print(f"Stop Loss: {risk_config.get('stop_loss_pct', 'Not set'):.1%}")
        print(f"Take Profit: {risk_config.get('take_profit_pct', 'Not set'):.1%}")
        
        print("\n📋 Note: These limits will now generate warnings instead of stopping the bot")
        
    except Exception as e:
        print(f"⚠️ Could not read configuration: {e}")

if __name__ == "__main__":
    success = verify_bot_continuous_operation()
    check_current_configuration()
    
    print("\n" + "="*60)
    if success:
        print("✅ READY: Bot will run continuously until manually stopped!")
        print("💡 To start the bot: python bot.py")
        print("💡 To stop the bot: Press Ctrl+C")
    else:
        print("❌ Issues found - please review before starting the bot")
    
    sys.exit(0 if success else 1)
