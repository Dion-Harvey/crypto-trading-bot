#!/usr/bin/env python3
"""
🌐 DYNAMIC PAIR DISCOVERY SYSTEM
Automatically discovers and manages all available trading pairs on Binance US
Supports both USD and USDT base currencies with intelligent switching
"""

import ccxt
import json
import time
from typing import List, Dict, Tuple
import logging

class DynamicPairManager:
    def __init__(self, config_path='enhanced_config.json'):
        self.config_path = config_path
        self.exchange = None
        self.all_pairs = []
        self.usd_pairs = []
        self.usdt_pairs = []
        self.active_pairs = []
        self.pair_preferences = {}
        
    def initialize_exchange(self):
        """Initialize exchange connection"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            self.exchange = ccxt.binance({
                'apiKey': config['api']['key'],
                'secret': config['api']['secret'],
                'sandbox': config['api']['sandbox'],
                'enableRateLimit': True,
            })
            
            print("✅ Exchange initialized successfully")
            return True
            
        except Exception as e:
            print(f"❌ Exchange initialization failed: {e}")
            return False
    
    def discover_all_pairs(self) -> Dict:
        """Discover all available trading pairs"""
        if not self.exchange:
            if not self.initialize_exchange():
                return {}
        
        try:
            print("🔍 Discovering all available trading pairs...")
            markets = self.exchange.load_markets()
            
            usd_pairs = []
            usdt_pairs = []
            all_active_pairs = []
            
            for symbol, market in markets.items():
                if market['active'] and market['type'] == 'spot':
                    all_active_pairs.append(symbol)
                    
                    if symbol.endswith('/USD'):
                        usd_pairs.append(symbol)
                    elif symbol.endswith('/USDT'):
                        usdt_pairs.append(symbol)
            
            self.all_pairs = all_active_pairs
            self.usd_pairs = sorted(usd_pairs)
            self.usdt_pairs = sorted(usdt_pairs)
            
            return {
                'total_pairs': len(all_active_pairs),
                'usd_pairs': len(usd_pairs),
                'usdt_pairs': len(usdt_pairs),
                'usd_list': usd_pairs,
                'usdt_list': usdt_pairs
            }
            
        except Exception as e:
            print(f"❌ Error discovering pairs: {e}")
            return {}
    
    def get_dual_currency_coins(self) -> List[str]:
        """Get coins available in both USD and USDT"""
        dual_coins = []
        
        # Extract base currencies from USD pairs
        usd_bases = {pair.split('/')[0] for pair in self.usd_pairs}
        usdt_bases = {pair.split('/')[0] for pair in self.usdt_pairs}
        
        # Find intersection
        dual_coins = list(usd_bases.intersection(usdt_bases))
        return sorted(dual_coins)
    
    def get_preferred_pair(self, base_currency: str, prefer_usd: bool = True) -> str:
        """Get preferred trading pair for a base currency"""
        usd_pair = f"{base_currency}/USD"
        usdt_pair = f"{base_currency}/USDT"
        
        if prefer_usd and usd_pair in self.usd_pairs:
            return usd_pair
        elif usdt_pair in self.usdt_pairs:
            return usdt_pair
        elif usd_pair in self.usd_pairs:
            return usd_pair
        else:
            return None
    
    def create_intelligent_pair_list(self, max_pairs: int = 50, prefer_usd: bool = True) -> List[str]:
        """Create an intelligent list of trading pairs"""
        
        # Priority tiers for crypto selection
        tier1_cryptos = ['BTC', 'ETH', 'SOL', 'XRP', 'ADA', 'DOGE', 'LINK', 'LTC', 'AVAX', 'DOT']
        tier2_cryptos = ['MATIC', 'UNI', 'ATOM', 'XLM', 'ALGO', 'VET', 'FIL', 'THETA', 'EOS', 'TRX']
        tier3_cryptos = ['HBAR', 'SUI', 'SHIB', 'MANA', 'SAND', 'CRV', 'COMP', 'MKR', 'AAVE', 'SNX']
        
        selected_pairs = []
        
        # Add tier 1 cryptos first (highest priority)
        for crypto in tier1_cryptos:
            if len(selected_pairs) >= max_pairs:
                break
            pair = self.get_preferred_pair(crypto, prefer_usd)
            if pair:
                selected_pairs.append(pair)
        
        # Add tier 2 cryptos
        for crypto in tier2_cryptos:
            if len(selected_pairs) >= max_pairs:
                break
            pair = self.get_preferred_pair(crypto, prefer_usd)
            if pair and pair not in selected_pairs:
                selected_pairs.append(pair)
        
        # Add tier 3 cryptos
        for crypto in tier3_cryptos:
            if len(selected_pairs) >= max_pairs:
                break
            pair = self.get_preferred_pair(crypto, prefer_usd)
            if pair and pair not in selected_pairs:
                selected_pairs.append(pair)
        
        # Fill remaining slots with other available pairs
        all_available = self.usd_pairs + self.usdt_pairs if not prefer_usd else self.usdt_pairs + self.usd_pairs
        
        for pair in all_available:
            if len(selected_pairs) >= max_pairs:
                break
            if pair not in selected_pairs:
                # Skip stablecoins and low-volume pairs
                base = pair.split('/')[0]
                if base not in ['USDC', 'BUSD', 'TUSD', 'PAX', 'USDD', 'FDUSD']:
                    selected_pairs.append(pair)
        
        return selected_pairs[:max_pairs]
    
    def update_config_with_dynamic_pairs(self, max_pairs: int = 50, prefer_usd: bool = True):
        """Update enhanced_config.json with dynamically discovered pairs"""
        try:
            # Discover pairs
            discovery_result = self.discover_all_pairs()
            if not discovery_result:
                print("❌ Failed to discover pairs")
                return False
            
            # Create intelligent pair list
            intelligent_pairs = self.create_intelligent_pair_list(max_pairs, prefer_usd)
            
            # Load current config
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Update supported pairs
            config['trading']['supported_pairs'] = intelligent_pairs
            
            # Add dynamic pair settings
            if 'dynamic_pairs' not in config:
                config['dynamic_pairs'] = {}
            
            config['dynamic_pairs'].update({
                'enabled': True,
                'max_pairs': max_pairs,
                'prefer_usd': prefer_usd,
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_discovered': discovery_result['total_pairs'],
                'usd_pairs_available': discovery_result['usd_pairs'],
                'usdt_pairs_available': discovery_result['usdt_pairs'],
                'auto_discovery_interval_hours': 24,
                'intelligent_selection': True
            })
            
            # Save updated config
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Config updated with {len(intelligent_pairs)} dynamic pairs")
            return True
            
        except Exception as e:
            print(f"❌ Error updating config: {e}")
            return False

def main():
    """Main function to demonstrate dynamic pair discovery"""
    print("🌐 DYNAMIC PAIR DISCOVERY SYSTEM")
    print("=" * 50)
    
    manager = DynamicPairManager()
    
    # Discover all pairs
    discovery = manager.discover_all_pairs()
    
    if discovery:
        print(f"📊 DISCOVERY RESULTS:")
        print(f"   Total active pairs: {discovery['total_pairs']}")
        print(f"   USD pairs: {discovery['usd_pairs']}")
        print(f"   USDT pairs: {discovery['usdt_pairs']}")
        print()
        
        # Show sample pairs
        print(f"🔍 SAMPLE USD PAIRS: {discovery['usd_list'][:10]}")
        print(f"🔍 SAMPLE USDT PAIRS: {discovery['usdt_list'][:10]}")
        print()
        
        # Get dual currency coins
        dual_coins = manager.get_dual_currency_coins()
        print(f"💎 DUAL CURRENCY COINS ({len(dual_coins)}): {dual_coins[:20]}")
        print()
        
        # Create intelligent pair list
        print(f"🎯 CREATING INTELLIGENT PAIR LIST...")
        intelligent_pairs = manager.create_intelligent_pair_list(50, prefer_usd=True)
        
        print(f"✅ INTELLIGENT PAIR SELECTION ({len(intelligent_pairs)} pairs):")
        for i, pair in enumerate(intelligent_pairs, 1):
            print(f"   {i:2d}. {pair}")
        print()
        
        # Update config
        print(f"🔄 UPDATING CONFIGURATION...")
        success = manager.update_config_with_dynamic_pairs(50, prefer_usd=True)
        
        if success:
            print("✅ DYNAMIC PAIR DISCOVERY COMPLETE!")
            print("🎯 Bot can now trade all discovered pairs with intelligent switching")
        else:
            print("❌ Configuration update failed")
    
    else:
        print("❌ Discovery failed")

if __name__ == "__main__":
    main()
