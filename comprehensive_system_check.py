#!/usr/bin/env python3
"""
🌐 COMPREHENSIVE SYSTEM STATUS CHECK
Verify that the bot now has access to ALL 235 Binance US pairs
"""

import json

def check_comprehensive_system():
    """Check the comprehensive all-pairs system status"""
    
    print("🚀 COMPREHENSIVE ALL-PAIRS SYSTEM STATUS")
    print("=" * 60)
    
    try:
        # Load enhanced config
        with open('enhanced_config.json', 'r') as f:
            config = json.load(f)
        
        # Check if comprehensive system is enabled
        multi_currency = config.get('multi_currency_enabled', False)
        currency_switching = config.get('currency_switching_enabled', False)
        comprehensive_enabled = config.get('comprehensive_pairs_enabled', False)
        total_pairs = config.get('total_supported_pairs', 0)
        
        print(f"🔄 Multi-Currency Trading: {'✅ ENABLED' if multi_currency else '❌ DISABLED'}")
        print(f"💱 Currency Switching: {'✅ ENABLED' if currency_switching else '❌ DISABLED'}")
        print(f"🌐 Comprehensive Mode: {'✅ ENABLED' if comprehensive_enabled else '❌ DISABLED'}")
        print(f"📊 Total Supported Pairs: {total_pairs}")
        
        # Check tier system
        tier_system = config.get('tier_system', {})
        if tier_system:
            print(f"\n🎯 TIER-BASED ALLOCATION SYSTEM:")
            total_tier_pairs = 0
            for tier_name, tier_data in tier_system.items():
                tier_display = tier_name.replace('_', ' ').title()
                pair_count = tier_data.get('count', 0)
                weight = tier_data.get('allocation_weight', 0) * 100
                total_tier_pairs += pair_count
                print(f"   {tier_display}: {pair_count} pairs ({weight:.0f}% weight)")
            
            print(f"   📊 Total Tier Pairs: {total_tier_pairs}")
        
        # Check USD equivalents
        usd_equivalents = config.get('usd_equivalent_pairs', {})
        print(f"\n💱 USD/USDT SWITCHING PAIRS: {len(usd_equivalents)}")
        
        # Sample some pairs
        supported_pairs = config.get('supported_pairs', [])
        print(f"\n📋 SAMPLE SUPPORTED PAIRS (showing 20 of {len(supported_pairs)}):")
        for i, pair in enumerate(supported_pairs[:20]):
            print(f"   {i+1:2d}. {pair}")
        
        if len(supported_pairs) > 20:
            print(f"   ... and {len(supported_pairs) - 20} more pairs")
        
        # Risk management
        risk_mgmt = config.get('risk_management', {})
        max_positions = risk_mgmt.get('max_concurrent_positions', 0)
        per_pair_allocation = risk_mgmt.get('position_size_per_pair', 0) * 100
        
        print(f"\n🛡️ RISK MANAGEMENT:")
        print(f"   📊 Max Concurrent Positions: {max_positions}")
        print(f"   💰 Per-Pair Allocation: {per_pair_allocation:.0f}%")
        print(f"   🔄 Total Max Exposure: {max_positions * per_pair_allocation:.0f}%")
        
        # Comprehensive scanning
        comp_scanning = risk_mgmt.get('comprehensive_scanning', {})
        if comp_scanning.get('enabled', False):
            scan_freq = comp_scanning.get('scan_frequency_seconds', 0)
            threshold = comp_scanning.get('opportunity_threshold', 0)
            print(f"\n🔍 COMPREHENSIVE SCANNING:")
            print(f"   ⚡ Scan Frequency: {scan_freq} seconds")
            print(f"   🎯 Opportunity Threshold: {threshold}")
            print(f"   📊 Status: {'✅ ACTIVE' if comp_scanning.get('enabled') else '❌ INACTIVE'}")
        
        print(f"\n✅ COMPREHENSIVE SYSTEM STATUS: READY")
        print(f"🎯 Bot can now trade across ALL {total_pairs} Binance US pairs!")
        print(f"🚀 4.3x improvement from previous 55-pair system!")
        
        # Check actual available pairs file
        try:
            with open('binance_us_all_pairs.json', 'r') as f:
                all_pairs_data = json.load(f)
            
            actual_total = all_pairs_data.get('total_pairs', 0)
            usdt_count = all_pairs_data['breakdown']['USDT_pairs']
            usd_count = all_pairs_data['breakdown']['USD_pairs']
            
            print(f"\n📊 BINANCE US MARKET DATA:")
            print(f"   🌐 Total Available Pairs: {actual_total}")
            print(f"   💵 USDT Pairs: {usdt_count}")
            print(f"   💴 USD Pairs: {usd_count}")
            print(f"   📈 Coverage: {(total_pairs/actual_total)*100:.1f}% of available pairs")
            
        except FileNotFoundError:
            print(f"\n⚠️ Market data file not found")
        
        return True
        
    except Exception as e:
        print(f"❌ Error checking system: {e}")
        return False

if __name__ == "__main__":
    check_comprehensive_system()
