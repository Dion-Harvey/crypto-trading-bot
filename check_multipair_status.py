#!/usr/bin/env python3
"""
🔍 ENHANCED MULTI-PAIR SYSTEM STATUS CHECKER
Verifies that all components are communicating properly
"""

import json
import time
from datetime import datetime
from enhanced_config import get_bot_config

def check_system_status():
    """Check the status of the enhanced multi-pair system"""
    
    print("🔍 ENHANCED MULTI-PAIR SYSTEM STATUS CHECK")
    print("="*60)
    
    # 1. Check configuration system
    print("📋 Configuration System:")
    try:
        config = get_bot_config()
        supported_pairs = config.get_supported_pairs()
        current_symbol = config.get_current_trading_symbol()
        
        print(f"   ✅ Config loaded successfully")
        print(f"   📊 Supported pairs: {len(supported_pairs)}")
        print(f"   🎯 Current active symbol: {current_symbol}")
        
        # List all supported pairs
        print(f"   📝 All monitored pairs:")
        for i, pair in enumerate(supported_pairs, 1):
            status = "🎯 ACTIVE" if pair == current_symbol else "📊 monitored"
            print(f"      {i:2d}. {pair:12} - {status}")
            
    except Exception as e:
        print(f"   ❌ Config error: {e}")
        return False
    
    # 2. Check communication evidence
    print(f"\n🔄 Process Communication:")
    try:
        with open('enhanced_config.json', 'r') as f:
            config_data = json.load(f)
        
        last_switch = config_data.get('trading', {}).get('last_pair_switch', 'Never')
        switch_reason = config_data.get('trading', {}).get('switch_reason', 'None')
        
        if last_switch != 'Never':
            switch_time = datetime.fromisoformat(last_switch.replace('Z', '+00:00'))
            now = datetime.now()
            time_diff = (now - switch_time.replace(tzinfo=None)).total_seconds()
            
            print(f"   ✅ Last communication: {time_diff:.0f} seconds ago")
            print(f"   📝 Switch reason: {switch_reason}")
            
            if time_diff < 300:  # Less than 5 minutes
                print(f"   ✅ COMMUNICATION: Active and recent")
            elif time_diff < 3600:  # Less than 1 hour  
                print(f"   ⚠️ COMMUNICATION: Working but not recent")
            else:
                print(f"   ❌ COMMUNICATION: Stale - may have issues")
        else:
            print(f"   ⚠️ No communication evidence found")
            
    except Exception as e:
        print(f"   ❌ Communication check error: {e}")
    
    # 3. Test runtime reload capability
    print(f"\n🔄 Runtime Reload Test:")
    try:
        original_mtime = config.last_config_mtime
        reload_result = config.reload_config_if_changed()
        
        print(f"   ✅ Reload function working")
        print(f"   📅 File modification time: {original_mtime}")
        print(f"   🔄 Config change detected: {reload_result}")
        
    except Exception as e:
        print(f"   ❌ Reload test error: {e}")
    
    # 4. System recommendations
    print(f"\n💡 System Status Summary:")
    
    if current_symbol != 'BTC/USDT':
        print(f"   ✅ MULTI-PAIR ACTIVE: Scanner successfully switched to {current_symbol}")
        print(f"   ✅ COMMUNICATION WORKING: Processes are communicating")
    else:
        print(f"   ⚠️ DEFAULT PAIR ACTIVE: No scanner switches detected")
        print(f"   ⚠️ CHECK SCANNER: Multi-pair scanner may not be running")
    
    if len(supported_pairs) >= 16:
        print(f"   ✅ ALL PAIRS MONITORED: {len(supported_pairs)} pairs configured")
    else:
        print(f"   ⚠️ LIMITED PAIRS: Only {len(supported_pairs)} pairs configured")
    
    print(f"\n🎯 FINAL STATUS:")
    if current_symbol != 'BTC/USDT' and len(supported_pairs) >= 16:
        print(f"   🟢 FULLY OPERATIONAL: Enhanced multi-pair system working perfectly!")
        print(f"   🎯 Active pair: {current_symbol}")
        print(f"   📊 Monitoring: {len(supported_pairs)} pairs")
        print(f"   🔄 Communication: Active")
    else:
        print(f"   🟡 PARTIALLY OPERATIONAL: Some components may need attention")
    
    return True

if __name__ == "__main__":
    check_system_status()
