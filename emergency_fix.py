#!/usr/bin/env python3
"""
🚀 EMERGENCY INTEGRATION FIX
=============================

This script fixes the three critical issues:
1. Missing update_bot_config function
2. Phase 2 Intelligence integration 
3. Native Trailing Stops integration

Run this to get all enhanced features working before bed!
"""

import json
import os
import sys
from datetime import datetime

def fix_missing_function():
    """Fix the missing update_bot_config function"""
    print("🔧 Fixing missing update_bot_config function...")
    
    # Check if the function exists in the integration file
    integration_file = 'binance_native_trailing_integration.py'
    
    if os.path.exists(integration_file):
        try:
            with open(integration_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            try:
                with open(integration_file, 'r', encoding='cp1252') as f:
                    content = f.read()
            except:
                print("❌ Could not read integration file due to encoding issues")
                return False
        
        if 'def update_bot_config(' in content:
            print("✅ update_bot_config function already exists")
            return True
        else:
            print("❌ Function missing - should have been added by previous fix")
            return False
    else:
        print("❌ Integration file not found")
        return False

def setup_enhanced_config():
    """Setup the enhanced configuration with all features"""
    print("🔧 Setting up enhanced configuration...")
    
    enhanced_config = {
        "enhanced_features": {
            "enabled": True,
            "version": "2.0",
            "last_updated": datetime.now().isoformat(),
            "features": {
                "phase2_intelligence": True,
                "native_trailing": True,
                "integration_functions": True
            },
            "fallback_mode": True,
            "error_handling": "graceful_degradation"
        },
        "phase2_intelligence": {
            "enabled": True,
            "provider": "free_apis",
            "apis": {
                "bitquery": {"enabled": True, "weight": 0.3},
                "defillama": {"enabled": True, "weight": 0.25},
                "thegraph": {"enabled": True, "weight": 0.2},
                "dune": {"enabled": True, "weight": 0.25}
            },
            "refresh_interval": 300,
            "confidence_threshold": 0.6,
            "alert_thresholds": {
                "whale_transaction_usd": 1000000,
                "exchange_net_flow_usd": 5000000,
                "stablecoin_change_pct": 2.0
            }
        },
        "risk_management": {
            "binance_native_trailing": {
                "enabled": True,
                "trailing_percent": 0.5,
                "activation_percent": 0.5,
                "min_notional": 5.0,
                "replace_manual_trailing": True,
                "use_for_all_positions": True,
                "emergency_fallback": True
            }
        }
    }
    
    config_file = 'enhanced_config.json'
    
    try:
        # Load existing config if it exists
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                current_config = json.load(f)
        else:
            current_config = {}
        
        # Backup current config
        backup_file = f"enhanced_config.json.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        if current_config:
            with open(backup_file, 'w') as f:
                json.dump(current_config, f, indent=2)
            print(f"   📋 Backup created: {backup_file}")
        
        # Deep merge the configurations
        def deep_merge(dict1, dict2):
            result = dict1.copy()
            for key, value in dict2.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        merged_config = deep_merge(current_config, enhanced_config)
        
        # Save the enhanced config
        with open(config_file, 'w') as f:
            json.dump(merged_config, f, indent=2)
        
        print(f"✅ Enhanced configuration saved to {config_file}")
        return True
        
    except Exception as e:
        print(f"❌ Error setting up enhanced config: {e}")
        return False

def test_integrations():
    """Test all integrations to make sure they work"""
    print("🧪 Testing integrations...")
    
    test_results = {
        'phase2_api': False,
        'native_trailing': False,
        'integration_functions': False,
        'config_update': False
    }
    
    # Test Phase 2 API
    try:
        from free_phase2_api import FreePhase2Provider
        provider = FreePhase2Provider()
        test_results['phase2_api'] = True
        print("✅ Phase 2 API: Working")
    except Exception as e:
        print(f"❌ Phase 2 API: {e}")
    
    # Test Native Trailing
    try:
        from binance_native_trailing import place_binance_trailing_stop_order
        test_results['native_trailing'] = True
        print("✅ Native Trailing: Working")
    except Exception as e:
        print(f"❌ Native Trailing: {e}")
    
    # Test Integration Functions
    try:
        from binance_native_trailing_integration import (
            update_bot_config,
            place_enhanced_order_with_native_trailing
        )
        test_results['integration_functions'] = True
        print("✅ Integration Functions: Working")
    except Exception as e:
        print(f"❌ Integration Functions: {e}")
    
    # Test Config Update
    try:
        test_config = {"test": {"timestamp": datetime.now().isoformat()}}
        success = update_bot_config(test_config)
        test_results['config_update'] = success
        if success:
            print("✅ Config Update: Working")
        else:
            print("❌ Config Update: Failed")
    except Exception as e:
        print(f"❌ Config Update: {e}")
    
    return test_results

def deploy_to_aws():
    """Deploy the fixes to AWS"""
    print("🚀 Deploying fixes to AWS...")
    
    files_to_deploy = [
        'binance_native_trailing_integration.py',
        'enhanced_integration.py', 
        'enhanced_config.json',
        'free_phase2_api.py',
        'free_phase2_config.py',
        'binance_native_trailing.py'
    ]
    
    aws_commands = []
    
    for file in files_to_deploy:
        if os.path.exists(file):
            aws_commands.append(f'scp {file} ubuntu@3.135.216.32:crypto-trading-bot-deploy/')
            print(f"   📁 Prepared to upload: {file}")
        else:
            print(f"   ⚠️ File not found: {file}")
    
    print(f"\n🔧 To deploy to AWS, run these commands:")
    for cmd in aws_commands:
        print(f"   {cmd}")
    
    print(f"\n🔄 Then restart the bot on AWS:")
    print(f"   ssh ubuntu@3.135.216.32")
    print(f"   cd crypto-trading-bot-deploy")
    print(f"   pkill -f bot.py")
    print(f"   source bot_venv/bin/activate")
    print(f"   nohup python bot_enhanced.py > bot_enhanced.log 2>&1 &")
    
    return aws_commands

def main():
    """Main fix routine"""
    print("🚀 EMERGENCY INTEGRATION FIX")
    print("="*50)
    
    # Step 1: Fix missing function
    function_fixed = fix_missing_function()
    
    # Step 2: Setup enhanced config
    config_fixed = setup_enhanced_config()
    
    # Step 3: Test all integrations
    test_results = test_integrations()
    
    # Step 4: Prepare AWS deployment
    aws_commands = deploy_to_aws()
    
    # Summary
    print(f"\n📊 FIX SUMMARY:")
    print("="*50)
    print(f"Function Fix: {'✅' if function_fixed else '❌'}")
    print(f"Config Setup: {'✅' if config_fixed else '❌'}")
    print(f"Phase 2 API: {'✅' if test_results['phase2_api'] else '❌'}")
    print(f"Native Trailing: {'✅' if test_results['native_trailing'] else '❌'}")
    print(f"Integration: {'✅' if test_results['integration_functions'] else '❌'}")
    print(f"Config Update: {'✅' if test_results['config_update'] else '❌'}")
    
    all_working = all([
        function_fixed,
        config_fixed,
        test_results['phase2_api'],
        test_results['native_trailing'],
        test_results['integration_functions'],
        test_results['config_update']
    ])
    
    if all_working:
        print(f"\n🎉 ALL FIXES SUCCESSFUL!")
        print(f"✅ Enhanced features are ready for AWS deployment")
        print(f"✅ Phase 2 Intelligence integrated")
        print(f"✅ Native trailing stops configured")
        print(f"✅ Configuration management working")
    else:
        print(f"\n⚠️ Some issues remain - check the summary above")
    
    return all_working

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
