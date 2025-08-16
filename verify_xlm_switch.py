#!/usr/bin/env python3
"""
🔍 EMERGENCY SWITCH VERIFICATION
Verifies that the emergency switch to XLM/USDT was successful
"""

import json
from datetime import datetime
from log_utils import log_message

def verify_xlm_switch():
    """Verify that the bot is now configured for XLM trading"""
    
    log_message("🔍 VERIFYING XLM EMERGENCY SWITCH")
    
    try:
        # Read current configuration
        with open('enhanced_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Check trading symbol
        current_symbol = config.get('trading', {}).get('symbol', 'UNKNOWN')
        log_message(f"📊 CURRENT TRADING SYMBOL: {current_symbol}")
        
        # Check emergency switch status
        emergency_info = config.get('emergency_switch', {})
        
        if emergency_info.get('activated'):
            target_symbol = emergency_info.get('target_symbol', 'UNKNOWN')
            reason = emergency_info.get('reason', 'UNKNOWN')
            switched_at = emergency_info.get('switched_at', 'UNKNOWN')
            
            log_message("🚨 EMERGENCY SWITCH STATUS: ACTIVE")
            log_message(f"   Target Symbol: {target_symbol}")
            log_message(f"   Previous Symbol: {emergency_info.get('previous_symbol', 'UNKNOWN')}")
            log_message(f"   Reason: {reason}")
            log_message(f"   Switched At: {switched_at}")
            log_message(f"   Urgency: {emergency_info.get('urgency', 'UNKNOWN')}")
            
            # Verify correct configuration
            if current_symbol == 'XLM/USDT' and target_symbol == 'XLM/USDT':
                log_message("✅ VERIFICATION SUCCESSFUL: Bot correctly configured for XLM/USDT")
                log_message("🎯 XLM +11.70% OPPORTUNITY: Bot should now be able to capture this move")
                return True
            else:
                log_message(f"❌ CONFIGURATION MISMATCH: Current={current_symbol}, Target={target_symbol}")
                return False
        else:
            log_message("⚠️ NO EMERGENCY SWITCH DETECTED")
            return False
            
    except Exception as e:
        log_message(f"❌ VERIFICATION ERROR: {e}")
        return False

def check_xlm_support():
    """Verify XLM/USDT is in supported pairs"""
    
    try:
        with open('enhanced_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        supported_pairs = config.get('trading', {}).get('supported_pairs', [])
        
        if 'XLM/USDT' in supported_pairs:
            log_message("✅ XLM/USDT SUPPORT: Confirmed in supported pairs list")
            return True
        else:
            log_message("❌ XLM/USDT NOT FOUND: Not in supported pairs list")
            log_message(f"📋 SUPPORTED PAIRS: {supported_pairs}")
            return False
            
    except Exception as e:
        log_message(f"❌ SUPPORT CHECK ERROR: {e}")
        return False

def generate_status_report():
    """Generate comprehensive status report"""
    
    log_message("=" * 60)
    log_message("🚨 XLM EMERGENCY SWITCH VERIFICATION REPORT")
    log_message("=" * 60)
    
    # Check basic configuration
    config_ok = verify_xlm_switch()
    support_ok = check_xlm_support()
    
    log_message("")
    log_message("📊 SUMMARY:")
    log_message(f"   ✅ Configuration: {'PASS' if config_ok else 'FAIL'}")
    log_message(f"   ✅ XLM Support: {'PASS' if support_ok else 'FAIL'}")
    
    overall_status = config_ok and support_ok
    
    log_message("")
    if overall_status:
        log_message("🎉 OVERALL STATUS: SUCCESS")
        log_message("🚀 Bot is now configured to trade XLM/USDT")
        log_message("📈 Should be able to capture XLM +11.70% opportunity")
        log_message("🔍 Monitor bot logs for XLM trading activity")
    else:
        log_message("❌ OVERALL STATUS: FAILED")
        log_message("🔧 Manual intervention may be required")
        log_message("📞 Check configuration and restart if necessary")
    
    log_message("=" * 60)
    
    return overall_status

if __name__ == "__main__":
    print("🔍 VERIFYING XLM EMERGENCY SWITCH...")
    success = generate_status_report()
    
    if success:
        print("✅ Verification completed successfully")
        print("🎯 Bot should now be trading XLM/USDT")
    else:
        print("❌ Verification failed - check logs")
