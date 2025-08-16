#!/usr/bin/env python3
"""
🌐 ENHANCED MULTI-CURRENCY PAIR DISCOVERY
Discovers available pairs and enhances the bot configuration
"""

import ccxt
import json
import time

def discover_available_pairs():
    """Discover pairs using ticker data"""
    
    print("🌐 ENHANCED PAIR DISCOVERY")
    print("=" * 40)
    
    try:
        # Load configuration
        with open('enhanced_config.json', 'r') as f:
            config = json.load(f)
        
        # Initialize exchange
        api_config = config['api_keys']['binance']
        exchange = ccxt.binance({
            'apiKey': api_config['api_key'],
            'secret': api_config['api_secret'],
            'sandbox': api_config['sandbox'],
            'enableRateLimit': True,
        })
        
        print("✅ Exchange initialized")
        
        # Get ticker data to discover active pairs
        print("🔍 Fetching ticker data...")
        tickers = exchange.fetch_tickers()
        
        # Filter for USD and USDT pairs
        usd_pairs = []
        usdt_pairs = []
        
        for symbol in tickers.keys():
            if symbol.endswith('/USD'):
                usd_pairs.append(symbol)
            elif symbol.endswith('/USDT'):
                usdt_pairs.append(symbol)
        
        print(f"📊 Discovered pairs from tickers:")
        print(f"   USD pairs: {len(usd_pairs)}")
        print(f"   USDT pairs: {len(usdt_pairs)}")
        
        # Create comprehensive pair list based on tiers
        print(f"\n🎯 Creating intelligent pair selection...")
        
        # Define crypto tiers by market cap and trading volume
        tier1 = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOGE', 'DOT', 'MATIC', 'SHIB']
        tier2 = ['AVAX', 'LINK', 'LTC', 'UNI', 'ATOM', 'XLM', 'ALGO', 'VET', 'FIL', 'THETA', 'EOS', 'TRX']
        tier3 = ['AAVE', 'MKR', 'COMP', 'SNX', 'CRV', 'MANA', 'SAND', 'CHZ', 'ENJ', 'BAT', 'ZRX', 'OMG']
        tier4 = ['HBAR', 'SUI', 'APT', 'OP', 'ARB', 'BLUR', 'PEPE', 'FLOKI', 'BONK', 'WIF', 'DYDX', 'GMX']
        
        selected_pairs = []
        tier_stats = {}
        
        # Process each tier
        for tier_name, cryptos in [('Tier 1', tier1), ('Tier 2', tier2), ('Tier 3', tier3), ('Tier 4', tier4)]:
            tier_count = 0
            print(f"   Processing {tier_name}...")
            
            for crypto in cryptos:
                usdt_pair = f"{crypto}/USDT"
                usd_pair = f"{crypto}/USD"
                
                # Prefer USDT, fallback to USD
                if usdt_pair in usdt_pairs:
                    selected_pairs.append(usdt_pair)
                    tier_count += 1
                elif usd_pair in usd_pairs:
                    selected_pairs.append(usd_pair)
                    tier_count += 1
            
            tier_stats[tier_name] = tier_count
            print(f"     Selected: {tier_count} pairs")
        
        # Add additional high-volume pairs to reach target count
        print(f"\n🔍 Adding additional high-volume pairs...")
        
        # Get volume data for remaining pairs
        remaining_usdt = [p for p in usdt_pairs if p not in selected_pairs]
        remaining_usd = [p for p in usd_pairs if p not in selected_pairs]
        
        # Sort by 24h volume (if available) and add top performers
        volume_pairs = []
        for pair in remaining_usdt + remaining_usd:
            try:
                ticker = tickers.get(pair, {})
                volume = ticker.get('quoteVolume', 0) or 0
                if volume > 1000000:  # $1M+ daily volume
                    volume_pairs.append((pair, volume))
            except:
                continue
        
        # Sort by volume and add top pairs
        volume_pairs.sort(key=lambda x: x[1], reverse=True)
        
        for pair, volume in volume_pairs[:50]:  # Add top 50 by volume
            if len(selected_pairs) >= 100:
                break
            if pair not in selected_pairs:
                # Skip stablecoins
                base = pair.split('/')[0]
                skip_tokens = ['USDC', 'BUSD', 'TUSD', 'PAX', 'USDD', 'FDUSD', 'DAI', 'FRAX']
                if base not in skip_tokens:
                    selected_pairs.append(pair)
        
        print(f"   Added: {len(selected_pairs) - sum(tier_stats.values())} volume-based pairs")
        
        # Update configuration
        config['trading']['supported_pairs'] = selected_pairs[:100]
        
        # Enhanced multi-currency configuration
        config['multi_currency'] = {
            'enabled': True,
            'prefer_usd': False,
            'max_pairs': 100,
            'auto_discovery': True,
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S'),
            'discovery_method': 'ticker_based',
            'total_discovered_usd': len(usd_pairs),
            'total_discovered_usdt': len(usdt_pairs),
            'selected_pairs_count': len(selected_pairs[:100]),
            'currency_switching_enabled': True,
            'tier_distribution': tier_stats,
            'volume_threshold_usd': 1000000,
            'auto_pair_refresh_hours': 24
        }
        
        # Enhanced risk management for multi-currency
        config['risk_management'].update({
            'max_concurrent_positions': 5,
            'per_pair_max_allocation': 0.1,
            'currency_diversification': True,
            'auto_rebalancing': True,
            'position_correlation_limit': 0.7
        })
        
        # Save configuration
        with open('enhanced_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        # Display results
        print(f"\n✅ MULTI-CURRENCY SETUP COMPLETE!")
        print("=" * 50)
        print(f"📊 Configuration Summary:")
        print(f"   Total pairs selected: {len(selected_pairs[:100])}")
        
        usd_count = len([p for p in selected_pairs[:100] if p.endswith('/USD')])
        usdt_count = len([p for p in selected_pairs[:100] if p.endswith('/USDT')])
        
        print(f"   USD pairs: {usd_count}")
        print(f"   USDT pairs: {usdt_count}")
        print(f"   Base preference: USDT with USD fallback")
        
        print(f"\n🎯 Tier Distribution:")
        for tier, count in tier_stats.items():
            print(f"   {tier}: {count} pairs")
        
        print(f"\n🔝 Top 25 Selected Pairs:")
        for i, pair in enumerate(selected_pairs[:25], 1):
            currency_type = "USD" if pair.endswith('/USD') else "USDT"
            print(f"   {i:2d}. {pair:15s} ({currency_type})")
        
        if len(selected_pairs) > 25:
            print(f"   ... and {len(selected_pairs[:100]) - 25} more pairs")
        
        print(f"\n🚀 Features Enabled:")
        print(f"   ✅ Multi-currency trading (USD + USDT)")
        print(f"   ✅ Automatic pair discovery")
        print(f"   ✅ Volume-based pair selection")
        print(f"   ✅ Risk-adjusted position sizing")
        print(f"   ✅ Currency diversification")
        
        print(f"\n💡 Your bot can now trade {len(selected_pairs[:100])} different cryptocurrencies!")
        print(f"🔄 It will automatically choose between USD and USDT pairs")
        print(f"📈 Focus on high-volume, liquid markets for better execution")
        
        return True
        
    except Exception as e:
        print(f"❌ Discovery failed: {e}")
        return False

if __name__ == "__main__":
    discover_available_pairs()
