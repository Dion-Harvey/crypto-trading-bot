#!/usr/bin/env python3
"""
🌐 MULTI-CURRENCY TRADING MANAGER
Enhanced system for trading all available Binance pairs with USD/USDT switching
"""

import ccxt
import json
import time
from typing import List, Dict, Optional, Tuple
import logging

class MultiCurrencyManager:
    def __init__(self, config_path='enhanced_config.json'):
        self.config_path = config_path
        self.exchange = None
        self.all_markets = {}
        self.supported_pairs = []
        self.current_base_currency = 'USDT'  # Default to USDT
        
    def initialize(self):
        """Initialize the multi-currency manager"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Get API configuration from the correct location
            api_config = config['api_keys']['binance']
            
            self.exchange = ccxt.binance({
                'apiKey': api_config['api_key'],
                'secret': api_config['api_secret'],
                'sandbox': api_config['sandbox'],
                'enableRateLimit': True,
            })
            
            return True
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            return False
    
    def discover_trading_pairs(self) -> Dict:
        """Discover all available trading pairs"""
        if not self.exchange:
            self.initialize()
        
        try:
            print("🔍 Discovering all Binance trading pairs...")
            self.all_markets = self.exchange.load_markets()
            
            # Categorize pairs
            usd_pairs = []
            usdt_pairs = []
            other_pairs = []
            
            for symbol, market in self.all_markets.items():
                if market['active'] and market['type'] == 'spot':
                    if symbol.endswith('/USD'):
                        usd_pairs.append(symbol)
                    elif symbol.endswith('/USDT'):
                        usdt_pairs.append(symbol)
                    else:
                        other_pairs.append(symbol)
            
            # Create comprehensive pair list
            all_stable_pairs = usd_pairs + usdt_pairs
            
            result = {
                'usd_pairs': sorted(usd_pairs),
                'usdt_pairs': sorted(usdt_pairs),
                'other_pairs': sorted(other_pairs),
                'all_stable_pairs': sorted(all_stable_pairs),
                'total_pairs': len(all_stable_pairs)
            }
            
            print(f"✅ Discovered {len(usd_pairs)} USD pairs and {len(usdt_pairs)} USDT pairs")
            return result
            
        except Exception as e:
            print(f"❌ Error discovering pairs: {e}")
            return {}
    
    def get_tier_based_pairs(self, prefer_usd: bool = False) -> List[str]:
        """Get trading pairs organized by tier priority"""
        
        # Tier 1: Major cryptocurrencies (highest volume, most stable)
        tier1 = ['BTC', 'ETH', 'BNB', 'XRP', 'ADA', 'SOL', 'DOGE', 'DOT', 'MATIC', 'SHIB']
        
        # Tier 2: Popular altcoins
        tier2 = ['AVAX', 'LINK', 'LTC', 'UNI', 'ATOM', 'XLM', 'ALGO', 'VET', 'FIL', 'THETA', 
                'EOS', 'TRX', 'AAVE', 'MKR', 'COMP', 'SNX', 'CRV', 'YFI', 'SUSHI', 'ZEC']
        
        # Tier 3: Emerging and DeFi tokens
        tier3 = ['MANA', 'SAND', 'AXS', 'CHZ', 'ENJ', 'BAT', 'ZRX', 'OMG', 'LRC', 'GRT',
                'HBAR', 'SUI', 'APT', 'OP', 'ARB', 'BLUR', 'PEPE', 'FLOKI', 'BONK', 'WIF']
        
        selected_pairs = []
        base_currency = 'USD' if prefer_usd else 'USDT'
        fallback_currency = 'USDT' if prefer_usd else 'USD'
        
        # Process each tier
        for tier_name, cryptos in [('Tier 1', tier1), ('Tier 2', tier2), ('Tier 3', tier3)]:
            print(f"🎯 Processing {tier_name} cryptocurrencies...")
            
            for crypto in cryptos:
                primary_pair = f"{crypto}/{base_currency}"
                fallback_pair = f"{crypto}/{fallback_currency}"
                
                # Try primary currency first
                if primary_pair in self.all_markets and self.all_markets[primary_pair]['active']:
                    selected_pairs.append(primary_pair)
                # Fall back to secondary currency
                elif fallback_pair in self.all_markets and self.all_markets[fallback_pair]['active']:
                    selected_pairs.append(fallback_pair)
        
        return selected_pairs
    
    def create_comprehensive_pair_list(self, max_pairs: int = 100, prefer_usd: bool = False) -> List[str]:
        """Create a comprehensive list of trading pairs"""
        
        # Get tier-based pairs first
        tier_pairs = self.get_tier_based_pairs(prefer_usd)
        selected_pairs = tier_pairs.copy()
        
        print(f"✅ Selected {len(tier_pairs)} tier-based pairs")
        
        # If we need more pairs, add from available markets
        if len(selected_pairs) < max_pairs:
            base_currency = 'USD' if prefer_usd else 'USDT'
            fallback_currency = 'USDT' if prefer_usd else 'USD'
            
            # Get all available pairs for the preferred currency
            available_primary = [symbol for symbol in self.all_markets.keys() 
                               if symbol.endswith(f'/{base_currency}') and 
                               self.all_markets[symbol]['active']]
            
            available_fallback = [symbol for symbol in self.all_markets.keys() 
                                if symbol.endswith(f'/{fallback_currency}') and 
                                self.all_markets[symbol]['active']]
            
            # Add additional pairs
            for pair in available_primary + available_fallback:
                if len(selected_pairs) >= max_pairs:
                    break
                
                if pair not in selected_pairs:
                    # Skip stablecoins and test tokens
                    base = pair.split('/')[0]
                    skip_tokens = ['USDC', 'BUSD', 'TUSD', 'PAX', 'USDD', 'FDUSD', 'DAI', 'FRAX']
                    
                    if base not in skip_tokens:
                        selected_pairs.append(pair)
        
        return selected_pairs[:max_pairs]
    
    def update_bot_configuration(self, max_pairs: int = 100, prefer_usd: bool = False):
        """Update the bot configuration with new trading pairs"""
        
        try:
            # Discover pairs
            discovery = self.discover_trading_pairs()
            if not discovery:
                return False
            
            # Create comprehensive pair list
            comprehensive_pairs = self.create_comprehensive_pair_list(max_pairs, prefer_usd)
            
            # Load current configuration
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            # Update trading configuration
            config['trading']['supported_pairs'] = comprehensive_pairs
            config['trading']['base_currency'] = 'USD' if prefer_usd else 'USDT'
            
            # Add multi-currency settings
            if 'multi_currency' not in config:
                config['multi_currency'] = {}
            
            config['multi_currency'].update({
                'enabled': True,
                'prefer_usd': prefer_usd,
                'max_pairs': max_pairs,
                'auto_discovery': True,
                'last_updated': time.strftime('%Y-%m-%d %H:%M:%S'),
                'total_discovered_usd': len(discovery['usd_pairs']),
                'total_discovered_usdt': len(discovery['usdt_pairs']),
                'selected_pairs_count': len(comprehensive_pairs),
                'currency_switching_enabled': True,
                'minimum_volume_usd': 1000000  # $1M daily volume minimum
            })
            
            # Enhanced risk management for multi-currency
            if 'risk_management' in config:
                config['risk_management'].update({
                    'max_concurrent_positions': 5,  # Limit concurrent positions
                    'per_pair_max_allocation': 0.1,  # 10% max per pair
                    'currency_diversification': True,
                    'auto_rebalancing': True
                })
            
            # Save updated configuration
            with open(self.config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            print(f"✅ Configuration updated with {len(comprehensive_pairs)} trading pairs")
            print(f"🎯 Base currency preference: {'USD' if prefer_usd else 'USDT'}")
            print(f"📊 Multi-currency trading enabled")
            
            return True
            
        except Exception as e:
            print(f"❌ Configuration update failed: {e}")
            return False
    
    def get_optimal_pair_for_coin(self, coin: str, current_balances: Dict) -> Optional[str]:
        """Get the optimal trading pair for a coin based on current balances"""
        
        usd_pair = f"{coin}/USD"
        usdt_pair = f"{coin}/USDT"
        
        # Check which base currencies we have
        usd_balance = current_balances.get('USD', {}).get('free', 0)
        usdt_balance = current_balances.get('USDT', {}).get('free', 0)
        
        # Prefer the currency we have more of
        if usd_balance > usdt_balance and usd_pair in self.all_markets:
            return usd_pair
        elif usdt_pair in self.all_markets:
            return usdt_pair
        elif usd_pair in self.all_markets:
            return usd_pair
        
        return None
    
    def display_configuration_summary(self):
        """Display a summary of the multi-currency configuration"""
        
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            pairs = config['trading']['supported_pairs']
            multi_config = config.get('multi_currency', {})
            
            print("\n🌐 MULTI-CURRENCY TRADING CONFIGURATION")
            print("=" * 60)
            print(f"📊 Total trading pairs: {len(pairs)}")
            print(f"💱 Base currency preference: {config['trading'].get('base_currency', 'USDT')}")
            print(f"🔄 Currency switching: {'Enabled' if multi_config.get('currency_switching_enabled') else 'Disabled'}")
            print(f"⚡ Auto discovery: {'Enabled' if multi_config.get('auto_discovery') else 'Disabled'}")
            print(f"📅 Last updated: {multi_config.get('last_updated', 'Never')}")
            
            # Show pair breakdown
            usd_count = len([p for p in pairs if p.endswith('/USD')])
            usdt_count = len([p for p in pairs if p.endswith('/USDT')])
            
            print(f"\n📈 PAIR BREAKDOWN:")
            print(f"   USD pairs: {usd_count}")
            print(f"   USDT pairs: {usdt_count}")
            
            print(f"\n🎯 SAMPLE PAIRS:")
            for i, pair in enumerate(pairs[:20], 1):
                print(f"   {i:2d}. {pair}")
            
            if len(pairs) > 20:
                print(f"   ... and {len(pairs) - 20} more pairs")
            
        except Exception as e:
            print(f"❌ Error displaying configuration: {e}")

def main():
    """Main function for multi-currency setup"""
    
    print("🌐 MULTI-CURRENCY TRADING SYSTEM SETUP")
    print("=" * 50)
    
    manager = MultiCurrencyManager()
    
    if not manager.initialize():
        print("❌ Failed to initialize manager")
        return
    
    # Ask user preference
    print("\n💱 CURRENCY PREFERENCE:")
    print("1. Prefer USD pairs (when available)")
    print("2. Prefer USDT pairs (default)")
    
    choice = input("\nEnter your choice (1 or 2, default=2): ").strip()
    prefer_usd = choice == '1'
    
    print("\n📊 PAIR COUNT:")
    max_pairs = input("Maximum trading pairs (default=100): ").strip()
    max_pairs = int(max_pairs) if max_pairs.isdigit() else 100
    
    print(f"\n🔄 Setting up multi-currency trading...")
    print(f"   Currency preference: {'USD' if prefer_usd else 'USDT'}")
    print(f"   Maximum pairs: {max_pairs}")
    
    # Update configuration
    success = manager.update_bot_configuration(max_pairs, prefer_usd)
    
    if success:
        print("\n✅ MULTI-CURRENCY SETUP COMPLETE!")
        manager.display_configuration_summary()
        print("\n🚀 Your bot can now trade all available Binance pairs!")
        print("💡 The bot will automatically switch between USD and USDT as needed")
    else:
        print("\n❌ Setup failed")

if __name__ == "__main__":
    main()
