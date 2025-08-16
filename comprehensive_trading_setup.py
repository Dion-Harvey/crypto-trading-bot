#!/usr/bin/env python3
"""
🌐 COMPREHENSIVE TRADING PAIRS CONFIGURATION
Sets up the bot to trade a comprehensive list of major cryptocurrencies
with intelligent USD/USDT pair switching
"""

import json
import time

def setup_comprehensive_trading():
    """Setup comprehensive trading with major cryptocurrency pairs"""
    
    print("🌐 COMPREHENSIVE TRADING SETUP")
    print("=" * 45)
    
    try:
        # Load current configuration
        with open('enhanced_config.json', 'r') as f:
            config = json.load(f)
        
        # Comprehensive list of major trading pairs
        # Based on market cap, volume, and availability on major exchanges
        comprehensive_pairs = [
            # Tier 1: Major cryptocurrencies (highest priority)
            "BTC/USDT", "ETH/USDT", "BNB/USDT", "XRP/USDT", "ADA/USDT", 
            "SOL/USDT", "DOGE/USDT", "DOT/USDT", "MATIC/USDT", "SHIB/USDT",
            
            # Tier 2: Popular altcoins
            "AVAX/USDT", "LINK/USDT", "LTC/USDT", "UNI/USDT", "ATOM/USDT",
            "XLM/USDT", "ALGO/USDT", "VET/USDT", "FIL/USDT", "THETA/USDT",
            
            # Tier 3: DeFi and emerging tokens
            "AAVE/USDT", "MKR/USDT", "COMP/USDT", "SNX/USDT", "CRV/USDT",
            "MANA/USDT", "SAND/USDT", "CHZ/USDT", "ENJ/USDT", "BAT/USDT",
            
            # Tier 4: Layer 2 and new generation
            "HBAR/USDT", "SUI/USDT", "APT/USDT", "OP/USDT", "ARB/USDT",
            "BLUR/USDT", "PEPE/USDT", "FLOKI/USDT", "BONK/USDT", "WIF/USDT",
            
            # Tier 5: Additional popular tokens
            "EOS/USDT", "TRX/USDT", "ZRX/USDT", "OMG/USDT", "LRC/USDT",
            "GRT/USDT", "DYDX/USDT", "GMX/USDT", "JUP/USDT", "WLD/USDT",
            
            # Tier 6: Meme and trending tokens
            "DOGE/USDT", "SHIB/USDT", "PEPE/USDT", "FLOKI/USDT", "BONK/USDT",
            
            # Tier 7: Staking and utility tokens
            "BNB/USDT", "MATIC/USDT", "ATOM/USDT", "DOT/USDT", "ALGO/USDT",
            
            # Tier 8: Gaming and metaverse
            "MANA/USDT", "SAND/USDT", "AXS/USDT", "CHZ/USDT", "ENJ/USDT",
            
            # Tier 9: Infrastructure and oracles
            "LINK/USDT", "VET/USDT", "FIL/USDT", "THETA/USDT", "GRT/USDT",
            
            # Tier 10: Additional opportunities
            "NEAR/USDT", "ICP/USDT", "FTM/USDT", "ONE/USDT", "HBAR/USDT"
        ]
        
        # Remove duplicates while preserving order
        seen = set()
        unique_pairs = []
        for pair in comprehensive_pairs:
            if pair not in seen:
                seen.add(pair)
                unique_pairs.append(pair)
        
        # USD equivalents mapping (for when USDT isn't available)
        usd_equivalents = {
            "BTC/USDT": "BTC/USD",
            "ETH/USDT": "ETH/USD",
            "XRP/USDT": "XRP/USD",
            "ADA/USDT": "ADA/USD",
            "SOL/USDT": "SOL/USD",
            "DOGE/USDT": "DOGE/USD",
            "DOT/USDT": "DOT/USD",
            "MATIC/USDT": "MATIC/USD",
            "AVAX/USDT": "AVAX/USD",
            "LINK/USDT": "LINK/USD",
            "LTC/USDT": "LTC/USD",
            "UNI/USDT": "UNI/USD",
            "ATOM/USDT": "ATOM/USD",
            "XLM/USDT": "XLM/USD"
        }
        
        # Update trading configuration
        config['trading']['supported_pairs'] = unique_pairs[:80]  # Limit to 80 pairs for performance
        config['trading']['base_currency'] = 'USDT'
        
        # Comprehensive multi-currency configuration
        config['multi_currency'] = {
            'enabled': True,
            'prefer_usd': False,
            'usd_fallback_enabled': True,
            'usd_equivalents': usd_equivalents,
            'max_pairs': 80,
            'auto_discovery': False,
            'static_configuration': True,
            'last_updated': time.strftime('%Y-%m-%d %H:%M:%S'),
            'selected_pairs_count': len(unique_pairs[:80]),
            'currency_switching_enabled': True,
            'intelligent_pair_selection': True,
            'tier_based_selection': True,
            'volume_threshold_usd': 500000,  # $500K minimum daily volume
            'market_cap_consideration': True
        }
        
        # Enhanced risk management for multiple currencies
        config['risk_management'].update({
            'max_concurrent_positions': 3,  # Conservative for multi-currency
            'per_pair_max_allocation': 0.15,  # 15% max per pair
            'currency_diversification': True,
            'auto_rebalancing': True,
            'position_correlation_limit': 0.7,
            'sector_diversification': True,
            'max_meme_token_allocation': 0.1,  # 10% max in meme tokens
            'tier1_preference_weight': 2.0,
            'dynamic_position_sizing': True
        })
        
        # Enhanced strategy parameters for multi-currency
        config['strategy_parameters'].update({
            'pair_rotation_enabled': True,
            'opportunity_scanning_interval': 30,  # 30 seconds
            'cross_pair_analysis': True,
            'momentum_detection_enabled': True,
            'sector_momentum_tracking': True,
            'relative_strength_analysis': True
        })
        
        # Add currency switching logic parameters
        config['currency_switching'] = {
            'enabled': True,
            'prefer_higher_volume': True,
            'prefer_tighter_spreads': True,
            'usd_premium_threshold': 0.001,  # Switch to USD if 0.1% better
            'usdt_default_preference': True,
            'dynamic_switching': True,
            'liquidity_threshold': 100000,  # $100K minimum liquidity
            'spread_threshold': 0.002  # 0.2% max spread
        }
        
        # Save updated configuration
        with open('enhanced_config.json', 'w') as f:
            json.dump(config, f, indent=2)
        
        # Display comprehensive summary
        print("✅ COMPREHENSIVE TRADING CONFIGURED!")
        print("=" * 50)
        
        print(f"📊 Trading Configuration:")
        print(f"   Total pairs: {len(unique_pairs[:80])}")
        print(f"   Base currency: USDT (with USD fallback)")
        print(f"   Currency switching: Enabled")
        print(f"   Max concurrent positions: 3")
        print(f"   Per-pair allocation: 15%")
        
        # Show tier breakdown
        tier_counts = {
            'Tier 1 (Major)': 10,
            'Tier 2 (Popular)': 10, 
            'Tier 3 (DeFi)': 10,
            'Tier 4 (Layer 2)': 10,
            'Tier 5+ (Others)': len(unique_pairs[:80]) - 40
        }
        
        print(f"\n🎯 Tier Distribution:")
        for tier, count in tier_counts.items():
            print(f"   {tier}: {count} pairs")
        
        print(f"\n💱 USD/USDT Switching:")
        print(f"   Available USD pairs: {len(usd_equivalents)}")
        print(f"   Automatic switching: Enabled")
        print(f"   Preference: USDT → USD fallback")
        
        print(f"\n🔝 Top 30 Trading Pairs:")
        for i, pair in enumerate(unique_pairs[:30], 1):
            usd_available = "✅" if pair in usd_equivalents else "❌"
            print(f"   {i:2d}. {pair:12s} (USD: {usd_available})")
        
        if len(unique_pairs) > 30:
            print(f"   ... and {len(unique_pairs[:80]) - 30} more pairs")
        
        print(f"\n🚀 Enhanced Features:")
        print(f"   ✅ Multi-currency trading (USDT + USD)")
        print(f"   ✅ Intelligent pair selection")
        print(f"   ✅ Tier-based prioritization") 
        print(f"   ✅ Risk-adjusted position sizing")
        print(f"   ✅ Sector diversification")
        print(f"   ✅ Momentum detection across pairs")
        print(f"   ✅ Dynamic currency switching")
        
        print(f"\n💡 Configuration Complete!")
        print(f"🎯 Your bot can now trade {len(unique_pairs[:80])} major cryptocurrencies")
        print(f"🔄 Automatic USD/USDT switching based on liquidity and spreads")
        print(f"📈 Optimized for maximum opportunities across all markets")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration failed: {e}")
        return False

if __name__ == "__main__":
    setup_comprehensive_trading()
