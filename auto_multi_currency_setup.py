#!/usr/bin/env python3
"""
🌐 AUTOMATIC MULTI-CURRENCY SETUP
Automatically configures the bot for all available Binance pairs
"""

import ccxt
import json
import time

def setup_multi_currency_trading():
    """Setup multi-currency trading automatically"""
    
    print("🌐 AUTOMATIC MULTI-CURRENCY SETUP")
    print("=" * 50)
    
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
        
        # Discover all markets
        print("🔍 Discovering all available trading pairs...")
        markets = exchange.load_markets()
        
        # Filter for active spot markets
        usd_pairs = []
        usdt_pairs = []
        
        for symbol, market in markets.items():
            if market['active'] and market['type'] == 'spot':
                if symbol.endswith('/USD'):
                    usd_pairs.append(symbol)
                elif symbol.endswith('/USDT'):
                    usdt_pairs.append(symbol)
        
        print(f"📊 Found {len(usd_pairs)} USD pairs and {len(usdt_pairs)} USDT pairs")
        
        # Create intelligent pair selection
        tier1_cryptos = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOGE', 'DOT', 'MATIC', 'SHIB']
        tier2_cryptos = ['AVAX', 'LINK', 'LTC', 'UNI', 'ATOM', 'XLM', 'ALGO', 'VET', 'FIL', 'THETA']
        tier3_cryptos = ['EOS', 'TRX', 'AAVE', 'MKR', 'COMP', 'SNX', 'CRV', 'MANA', 'SAND', 'CHZ']
        tier4_cryptos = ['HBAR', 'SUI', 'APT', 'OP', 'ARB', 'BLUR', 'PEPE', 'FLOKI', 'BONK', 'WIF']
        
        selected_pairs = []
        
        # Process each tier, preferring USDT but taking USD if needed
        all_tiers = [tier1_cryptos, tier2_cryptos, tier3_cryptos, tier4_cryptos]
        
        for tier in all_tiers:
            for crypto in tier:
                usdt_pair = f"{crypto}/USDT"
                usd_pair = f"{crypto}/USD"
                
                if usdt_pair in usdt_pairs:
                    selected_pairs.append(usdt_pair)
                elif usd_pair in usd_pairs:
                    selected_pairs.append(usd_pair)
        
        # Add more USDT pairs to reach 100 total
        for pair in usdt_pairs:
            if len(selected_pairs) >= 100:
                break
            if pair not in selected_pairs:
                # Skip stablecoins
                base = pair.split('/')[0]
                skip_tokens = ['USDC', 'BUSD', 'TUSD', 'PAX', 'USDD', 'FDUSD', 'DAI']
                if base not in skip_tokens:
                    selected_pairs.append(pair)
        
        # Update configuration
        config['trading']['supported_pairs'] = selected_pairs[:100]
        config['trading']['base_currency'] = 'USDT'
        
        # Add multi-currency settings
        if 'multi_currency' not in config:
            config['multi_currency'] = {}
        
        config['multi_currency'].update({
            'enabled': True,
            'prefer_usd': False,
            'max_pairs': 100,
            'auto_discovery': True,
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S'),
            'total_discovered_usd': len(usd_pairs),
            'total_discovered_usdt': len(usdt_pairs),
            'selected_pairs_count': len(selected_pairs[:100]),
            'currency_switching_enabled': True,
            'minimum_volume_usd': 1000000
        })
        
        # Enhanced risk management
        if 'risk_management' in config:
            config['risk_management'].update({
                'max_concurrent_positions': 5,
                'per_pair_max_allocation': 0.1,
                'currency_diversification': True,
                'auto_rebalancing': True
            })
        
        # Save configuration
        with open('enhanced_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        print("✅ Configuration updated successfully!")
        print(f"🎯 Selected {len(selected_pairs[:100])} trading pairs")
        
        # Display summary
        print("\n📊 MULTI-CURRENCY CONFIGURATION SUMMARY:")
        print("=" * 50)
        print(f"Total pairs: {len(selected_pairs[:100])}")
        
        usd_count = len([p for p in selected_pairs[:100] if p.endswith('/USD')])
        usdt_count = len([p for p in selected_pairs[:100] if p.endswith('/USDT')])
        
        print(f"USD pairs: {usd_count}")
        print(f"USDT pairs: {usdt_count}")
        print(f"Base currency: USDT (with USD fallback)")
        print(f"Auto-switching: Enabled")
        
        print(f"\n🎯 TOP 20 SELECTED PAIRS:")
        for i, pair in enumerate(selected_pairs[:20], 1):
            print(f"   {i:2d}. {pair}")
        
        if len(selected_pairs) > 20:
            print(f"   ... and {len(selected_pairs[:100]) - 20} more pairs")
        
        print(f"\n✅ SETUP COMPLETE!")
        print(f"🚀 Your bot can now trade {len(selected_pairs[:100])} pairs")
        print(f"💱 Automatic USD/USDT switching enabled")
        print(f"🎯 Ready for comprehensive multi-currency trading!")
        
        return True
        
    except Exception as e:
        print(f"❌ Setup failed: {e}")
        return False

if __name__ == "__main__":
    setup_multi_currency_trading()
