#!/usr/bin/env python3
"""
🌐 BINANCE US COMPREHENSIVE PAIR DISCOVERY
Discover ALL available trading pairs on Binance US and categorize them
"""

import ccxt
import json
from datetime import datetime

def discover_all_binance_us_pairs():
    """Discover all available trading pairs on Binance US"""
    
    try:
        # Initialize Binance US exchange
        exchange = ccxt.binanceus({
            'sandbox': False,
            'enableRateLimit': True,
        })
        
        print("🔍 DISCOVERING ALL BINANCE US TRADING PAIRS...")
        
        # Load markets
        markets = exchange.load_markets()
        
        # Categorize pairs
        usdt_pairs = []
        usd_pairs = []
        btc_pairs = []
        eth_pairs = []
        other_pairs = []
        
        all_pairs = []
        
        for symbol, market in markets.items():
            if market['active'] and market['spot']:
                all_pairs.append(symbol)
                
                # Categorize by quote currency
                if symbol.endswith('/USDT'):
                    usdt_pairs.append(symbol)
                elif symbol.endswith('/USD'):
                    usd_pairs.append(symbol)
                elif symbol.endswith('/BTC'):
                    btc_pairs.append(symbol)
                elif symbol.endswith('/ETH'):
                    eth_pairs.append(symbol)
                else:
                    other_pairs.append(symbol)
        
        # Sort all lists
        all_pairs.sort()
        usdt_pairs.sort()
        usd_pairs.sort()
        btc_pairs.sort()
        eth_pairs.sort()
        other_pairs.sort()
        
        # Create comprehensive categorization
        categorized_pairs = {
            "discovery_timestamp": datetime.now().isoformat(),
            "total_pairs": len(all_pairs),
            "breakdown": {
                "USDT_pairs": len(usdt_pairs),
                "USD_pairs": len(usd_pairs),
                "BTC_pairs": len(btc_pairs),
                "ETH_pairs": len(eth_pairs),
                "other_pairs": len(other_pairs)
            },
            "all_pairs": all_pairs,
            "by_quote_currency": {
                "USDT": usdt_pairs,
                "USD": usd_pairs,
                "BTC": btc_pairs,
                "ETH": eth_pairs,
                "OTHER": other_pairs
            }
        }
        
        # Save to file
        with open('binance_us_all_pairs.json', 'w') as f:
            json.dump(categorized_pairs, f, indent=2)
        
        print(f"✅ DISCOVERY COMPLETE!")
        print(f"📊 TOTAL PAIRS FOUND: {len(all_pairs)}")
        print(f"   💵 USDT pairs: {len(usdt_pairs)}")
        print(f"   💴 USD pairs: {len(usd_pairs)}")
        print(f"   ₿ BTC pairs: {len(btc_pairs)}")
        print(f"   Ⓔ ETH pairs: {len(eth_pairs)}")
        print(f"   🔄 Other pairs: {len(other_pairs)}")
        
        # Show sample of each category
        print(f"\n📋 SAMPLE USDT PAIRS:")
        for pair in usdt_pairs[:10]:
            print(f"   {pair}")
        if len(usdt_pairs) > 10:
            print(f"   ... and {len(usdt_pairs) - 10} more")
            
        print(f"\n📋 SAMPLE USD PAIRS:")
        for pair in usd_pairs[:10]:
            print(f"   {pair}")
        if len(usd_pairs) > 10:
            print(f"   ... and {len(usd_pairs) - 10} more")
        
        return categorized_pairs
        
    except Exception as e:
        print(f"❌ Error discovering pairs: {e}")
        return None

def create_tier_based_comprehensive_config(pairs_data):
    """Create comprehensive configuration with ALL pairs organized by tiers"""
    
    if not pairs_data:
        print("❌ No pairs data available")
        return None
    
    # Define major cryptocurrencies by market cap and trading volume
    tier1_cryptos = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOGE', 'AVAX', 'DOT', 'UNI', 'LINK']
    tier2_cryptos = ['LTC', 'BCH', 'XLM', 'ATOM', 'NEAR', 'MATIC', 'ALGO', 'VET', 'FIL', 'ETC', 'AAVE', 'GRT', 'SAND', 'MANA', 'CRV']
    tier3_cryptos = ['COMP', 'MKR', 'SNX', 'BAL', 'YFI', 'UMA', 'REN', 'LRC', 'ENJ', 'BAT', 'ZRX', 'STORJ', 'NKN', 'NU', 'REP']
    
    usdt_pairs = pairs_data['by_quote_currency']['USDT']
    usd_pairs = pairs_data['by_quote_currency']['USD']
    
    # Combine USDT and USD pairs for primary trading
    primary_pairs = usdt_pairs + usd_pairs
    
    # Categorize into tiers
    tier1_pairs = []
    tier2_pairs = []
    tier3_pairs = []
    tier4_pairs = []
    
    for pair in primary_pairs:
        crypto = pair.split('/')[0]
        if crypto in tier1_cryptos:
            tier1_pairs.append(pair)
        elif crypto in tier2_cryptos:
            tier2_pairs.append(pair)
        elif crypto in tier3_cryptos:
            tier3_pairs.append(pair)
        else:
            tier4_pairs.append(pair)
    
    # Create comprehensive configuration
    comprehensive_config = {
        "multi_currency_enabled": True,
        "currency_switching_enabled": True,
        "total_supported_pairs": len(primary_pairs),
        "tier_system": {
            "tier1_major_cryptos": {
                "count": len(tier1_pairs),
                "allocation_weight": 0.4,
                "pairs": tier1_pairs
            },
            "tier2_popular_cryptos": {
                "count": len(tier2_pairs),
                "allocation_weight": 0.3,
                "pairs": tier2_pairs
            },
            "tier3_defi_altcoins": {
                "count": len(tier3_pairs),
                "allocation_weight": 0.2,
                "pairs": tier3_pairs
            },
            "tier4_emerging_tokens": {
                "count": len(tier4_pairs),
                "allocation_weight": 0.1,
                "pairs": tier4_pairs
            }
        },
        "supported_pairs": primary_pairs,
        "usd_equivalent_pairs": {},
        "risk_management": {
            "max_concurrent_positions": 5,  # Increased for more pairs
            "position_size_per_pair": 0.10,  # 10% per pair (5 positions max = 50% total)
            "diversification_required": True,
            "sector_limits": {
                "max_per_tier": {
                    "tier1": 2,  # Max 2 positions in tier 1
                    "tier2": 2,  # Max 2 positions in tier 2
                    "tier3": 1,  # Max 1 position in tier 3
                    "tier4": 1   # Max 1 position in tier 4
                }
            }
        }
    }
    
    # Create USD equivalent mapping for currency switching
    usd_equivalents = {}
    for usdt_pair in usdt_pairs:
        crypto = usdt_pair.split('/')[0]
        usd_pair = f"{crypto}/USD"
        if usd_pair in usd_pairs:
            usd_equivalents[usdt_pair] = usd_pair
    
    comprehensive_config["usd_equivalent_pairs"] = usd_equivalents
    
    print(f"📊 COMPREHENSIVE CONFIGURATION CREATED:")
    print(f"   🎯 Total Pairs: {len(primary_pairs)}")
    print(f"   🥇 Tier 1 (Major): {len(tier1_pairs)} pairs")
    print(f"   🥈 Tier 2 (Popular): {len(tier2_pairs)} pairs")
    print(f"   🥉 Tier 3 (DeFi): {len(tier3_pairs)} pairs")
    print(f"   🔹 Tier 4 (Emerging): {len(tier4_pairs)} pairs")
    print(f"   💱 USD Equivalents: {len(usd_equivalents)} pairs")
    
    return comprehensive_config

if __name__ == "__main__":
    print("🚀 BINANCE US COMPREHENSIVE PAIR DISCOVERY")
    print("=" * 50)
    
    # Discover all pairs
    pairs_data = discover_all_binance_us_pairs()
    
    if pairs_data:
        # Create comprehensive configuration
        config = create_tier_based_comprehensive_config(pairs_data)
        
        if config:
            # Save comprehensive configuration
            with open('comprehensive_all_pairs_config.json', 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"\n✅ COMPREHENSIVE CONFIGURATION SAVED!")
            print(f"📄 File: comprehensive_all_pairs_config.json")
            print(f"🎯 Ready for ALL {config['total_supported_pairs']} Binance US pairs!")
            
            # Show tier breakdown
            print(f"\n📊 TIER BREAKDOWN:")
            for tier_name, tier_data in config['tier_system'].items():
                print(f"   {tier_name}: {tier_data['count']} pairs ({tier_data['allocation_weight']*100:.0f}% weight)")
