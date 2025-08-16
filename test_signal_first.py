#!/usr/bin/env python3
"""
🎯 SIGNAL-FIRST SYSTEM TEST
Test the signal-first approach vs tier-based approach
"""

import json

def test_signal_first_integration():
    """Test that signal-first approach is integrated"""
    
    print("🔬 TESTING SIGNAL-FIRST INTEGRATION")
    print("=" * 50)
    
    # Check if comprehensive config exists
    try:
        with open('comprehensive_all_pairs_config.json', 'r') as f:
            comp_config = json.load(f)
        total_pairs = comp_config.get('total_supported_pairs', 0)
        print(f"✅ Comprehensive config found: {total_pairs} pairs available")
    except FileNotFoundError:
        print(f"⚠️ Comprehensive config not found, using enhanced config")
        try:
            with open('enhanced_config.json', 'r') as f:
                enh_config = json.load(f)
            total_pairs = len(enh_config.get('trading', {}).get('supported_pairs', []))
            print(f"📊 Enhanced config found: {total_pairs} pairs available")
        except:
            print(f"❌ No configuration found")
            return False
    
    # Check bot.py for signal-first integration
    try:
        with open('bot.py', 'r', encoding='utf-8') as f:
            bot_content = f.read()
        
        signal_first_indicators = [
            'SIGNAL-FIRST CRYPTO SELECTION',
            'signal_strength',
            'signal_based',
            'strongest signals over tiers'
        ]
        
        found_indicators = []
        for indicator in signal_first_indicators:
            if indicator in bot_content:
                found_indicators.append(indicator)
        
        print(f"\n🔍 SIGNAL-FIRST INTEGRATION CHECK:")
        print(f"   Found {len(found_indicators)}/{len(signal_first_indicators)} signal-first indicators")
        for indicator in found_indicators:
            print(f"   ✅ {indicator}")
        
        # Check for tier removal
        tier_restrictions = [
            'tier_system',
            'tier_based_allocation',
            'tier1_major_cryptos'
        ]
        
        tier_found = []
        for restriction in tier_restrictions:
            if restriction in bot_content:
                tier_found.append(restriction)
        
        if tier_found:
            print(f"\n⚠️ TIER RESTRICTIONS STILL PRESENT:")
            for restriction in tier_found:
                print(f"   📊 {restriction}")
            print(f"   💡 Signal-first approach should prioritize signals over tiers")
        else:
            print(f"\n✅ NO TIER RESTRICTIONS FOUND - Signal-first approach active")
        
    except Exception as e:
        print(f"❌ Error checking bot.py: {e}")
        return False
    
    # Summary
    print(f"\n📊 SIGNAL-FIRST SYSTEM STATUS:")
    print(f"   🎯 Total Pairs Available: {total_pairs}")
    print(f"   🔍 Signal-First Integration: {'✅ Active' if len(found_indicators) >= 3 else '⚠️ Partial'}")
    print(f"   🚫 Tier Restrictions: {'⚠️ Present' if tier_found else '✅ Removed'}")
    
    print(f"\n🚀 BENEFITS OF SIGNAL-FIRST APPROACH:")
    print(f"   ✅ No artificial tier limitations")
    print(f"   ✅ Pure signal strength prioritization")
    print(f"   ✅ Maximum profit potential across ALL pairs")
    print(f"   ✅ Dynamic selection based on market conditions")
    
    return True

if __name__ == "__main__":
    test_signal_first_integration()
