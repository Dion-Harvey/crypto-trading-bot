#!/usr/bin/env python3
"""
🚨 EMERGENCY CONFIG UPDATER
Forces configuration updates for emergency asset switching

This module handles emergency configuration updates when major opportunities
like XLM +11.70% are detected but missed by normal switching logic.
"""

import json
import os
from datetime import datetime
from log_utils import log_message

def force_emergency_asset_switch(target_symbol: str, reason: str, config_path: str = "enhanced_config.json"):
    """
    🚨 FORCE EMERGENCY ASSET SWITCH
    
    Updates the bot configuration to immediately switch to the target asset
    for emergency opportunities like XLM +11.70%.
    
    Args:
        target_symbol: The asset to switch to (e.g., 'XLM/USDT')
        reason: Reason for the emergency switch
        config_path: Path to the configuration file
    """
    
    try:
        # Backup current configuration
        backup_path = f"{config_path}.emergency_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Read current configuration
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        # Create backup
        with open(backup_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        log_message(f"📁 CONFIG BACKUP: Created {backup_path}")
        
        # Get current symbol for logging
        current_symbol = config.get('trading', {}).get('symbol', 'UNKNOWN')
        
        # Force asset switch
        if 'trading' not in config:
            config['trading'] = {}
        
        config['trading']['symbol'] = target_symbol
        
        # Add emergency metadata
        config['emergency_switch'] = {
            'activated': True,
            'target_symbol': target_symbol,
            'previous_symbol': current_symbol,
            'reason': reason,
            'switched_at': datetime.now().isoformat(),
            'urgency': 'CRITICAL'
        }
        
        # Write updated configuration
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        log_message(f"🚨 EMERGENCY SWITCH EXECUTED: {current_symbol} → {target_symbol}")
        log_message(f"🎯 REASON: {reason}")
        log_message(f"📝 CONFIG UPDATED: {config_path}")
        
        return True
        
    except Exception as e:
        log_message(f"❌ EMERGENCY SWITCH FAILED: {e}")
        return False

def force_xlm_switch(reason: str = "XLM +11.70% emergency opportunity"):
    """Force switch to XLM/USDT for the current opportunity"""
    
    log_message("🚨 FORCING XLM SWITCH for +11.70% opportunity")
    
    success = force_emergency_asset_switch('XLM/USDT', reason)
    
    if success:
        log_message("✅ XLM EMERGENCY SWITCH: Configuration updated successfully")
        log_message("🔄 BOT RESTART RECOMMENDED: To immediately pick up new configuration")
        return True
    else:
        log_message("❌ XLM EMERGENCY SWITCH FAILED: Manual intervention required")
        return False

def check_and_clear_emergency_switch(config_path: str = "enhanced_config.json"):
    """Check if emergency switch is active and provide status"""
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        emergency_info = config.get('emergency_switch', {})
        
        if emergency_info.get('activated'):
            switched_at = emergency_info.get('switched_at', 'UNKNOWN')
            target_symbol = emergency_info.get('target_symbol', 'UNKNOWN')
            reason = emergency_info.get('reason', 'UNKNOWN')
            
            log_message(f"⚠️ EMERGENCY SWITCH ACTIVE:")
            log_message(f"   Target: {target_symbol}")
            log_message(f"   Reason: {reason}")
            log_message(f"   Activated: {switched_at}")
            
            return {
                'active': True,
                'target_symbol': target_symbol,
                'reason': reason,
                'switched_at': switched_at
            }
        else:
            return {'active': False}
            
    except Exception as e:
        log_message(f"⚠️ Error checking emergency switch status: {e}")
        return {'active': False, 'error': str(e)}

def clear_emergency_switch(config_path: str = "enhanced_config.json"):
    """Clear emergency switch status after opportunity is handled"""
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if 'emergency_switch' in config:
            del config['emergency_switch']
            
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            log_message("✅ EMERGENCY SWITCH CLEARED: Bot returned to normal operation")
            return True
    except Exception as e:
        log_message(f"❌ Error clearing emergency switch: {e}")
        return False

if __name__ == "__main__":
    # Execute emergency XLM switch for current opportunity
    print("🚨 EXECUTING EMERGENCY XLM SWITCH...")
    success = force_xlm_switch()
    
    if success:
        print("✅ Emergency switch completed successfully")
        print("🔄 Please restart the bot to pick up the new configuration")
    else:
        print("❌ Emergency switch failed - check logs for details")
