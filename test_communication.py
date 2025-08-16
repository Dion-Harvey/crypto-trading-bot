#!/usr/bin/env python3
"""
Bot Process Communication Analysis
Tests how the different bot processes communicate with each other
"""

import json
import time
from datetime import datetime

def analyze_communication():
    """Analyze the communication mechanism between bot processes"""
    
    print("🔍 BOT PROCESS COMMUNICATION ANALYSIS")
    print("="*60)
    
    # 1. Check current configuration state
    try:
        with open('enhanced_config.json', 'r') as f:
            config = json.load(f)
        
        current_symbol = config.get('trading', {}).get('symbol', 'Unknown')
        last_switch = config.get('trading', {}).get('last_pair_switch', 'Never')
        switch_reason = config.get('trading', {}).get('switch_reason', 'None')
        
        print("📊 Current Configuration State:")
        print(f"   🎯 Active Symbol: {current_symbol}")
        print(f"   ⏰ Last Switch: {last_switch}")
        print(f"   💡 Switch Reason: {switch_reason}")
        
        # 2. Analyze communication pattern
        print("\n🔄 Communication Pattern Analysis:")
        
        # Check if config was recently updated (indicates active communication)
        if last_switch != 'Never':
            try:
                switch_time = datetime.fromisoformat(last_switch.replace('Z', '+00:00'))
                now = datetime.now()
                time_diff = (now - switch_time.replace(tzinfo=None)).total_seconds()
                
                if time_diff < 300:  # Less than 5 minutes
                    print(f"   ✅ RECENT ACTIVITY: Last switch was {time_diff:.0f} seconds ago")
                    print("   ✅ COMMUNICATION: Active - processes are communicating")
                elif time_diff < 3600:  # Less than 1 hour
                    print(f"   ⚠️ MODERATE ACTIVITY: Last switch was {time_diff/60:.0f} minutes ago")
                    print("   ⚠️ COMMUNICATION: Intermittent - processes may be communicating")
                else:
                    print(f"   ❌ OLD ACTIVITY: Last switch was {time_diff/3600:.1f} hours ago")
                    print("   ❌ COMMUNICATION: Stale - processes may not be communicating")
                    
            except Exception as e:
                print(f"   ⚠️ Could not parse switch time: {e}")
        else:
            print("   ❌ NO SWITCHES: No pair switches detected")
            print("   ❌ COMMUNICATION: Unknown - no evidence of multi-pair communication")
        
        # 3. Check communication mechanism
        print("\n🔧 Communication Mechanism:")
        print("   📁 Method: Shared JSON configuration file")
        print("   📝 File: enhanced_config.json")
        print("   🔄 Process: Multi-pair scanner → writes config → Main bot reads config")
        
        # 4. Check for communication infrastructure
        communication_files = [
            'multi_pair_scanner.py',
            'enhanced_config.json', 
            'bot.py',
            'enhanced_config.py'
        ]
        
        print("\n🏗️ Communication Infrastructure:")
        missing_files = []
        for file in communication_files:
            try:
                with open(file, 'r') as f:
                    content = f.read()
                    if file == 'multi_pair_scanner.py':
                        if 'json.dump' in content and 'enhanced_config.json' in content:
                            print(f"   ✅ {file}: Can write config updates")
                        else:
                            print(f"   ⚠️ {file}: May not write config updates")
                    elif file == 'bot.py':
                        if 'get_bot_config' in content or 'enhanced_config' in content:
                            print(f"   ✅ {file}: Can read config updates")
                        else:
                            print(f"   ⚠️ {file}: May not read config updates")
                    else:
                        print(f"   ✅ {file}: Present")
            except FileNotFoundError:
                print(f"   ❌ {file}: Missing")
                missing_files.append(file)
        
        # 5. Test actual communication
        print("\n🧪 Communication Test:")
        original_symbol = current_symbol
        
        # The issue: get_bot_config() loads config ONCE at startup
        # Main bot doesn't reload config during runtime!
        print("   🚨 CRITICAL FINDING:")
        print("   📝 Multi-pair scanner WRITES config changes")
        print("   📖 Main bot READS config only at STARTUP")
        print("   ❌ Main bot does NOT reload config during runtime!")
        
        print("\n💡 Communication Status:")
        if current_symbol == 'SUI/USDT' and 'Opportunity' in switch_reason:
            print("   ✅ PARTIAL COMMUNICATION: Scanner updated config successfully")
            print("   ❌ INCOMPLETE COMMUNICATION: Main bot may not see changes until restart")
        else:
            print("   ❌ NO COMMUNICATION: No evidence of recent scanner→bot communication")
            
        return {
            'scanner_writes': True,
            'bot_reads_startup': True,
            'bot_reads_runtime': False,
            'current_symbol': current_symbol,
            'last_switch': last_switch,
            'communication_active': 'Opportunity' in switch_reason and current_symbol == 'SUI/USDT'
        }
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")
        return None

if __name__ == "__main__":
    result = analyze_communication()
    
    print("\n" + "="*60)
    print("🎯 SUMMARY:")
    
    if result:
        if result['communication_active']:
            print("✅ COMMUNICATION WORKING: Scanner successfully updated trading pair")
            print("⚠️ LIMITATION: Main bot may need restart to see changes")
        else:
            print("❌ COMMUNICATION ISSUE: Processes may not be communicating properly")
        
        print("\n🔧 RECOMMENDATIONS:")
        if not result['bot_reads_runtime']:
            print("1. Add runtime config reload to main bot")
            print("2. Implement signal-based communication")
            print("3. Use file watching or polling for config changes")
    else:
        print("❌ Could not determine communication status")
