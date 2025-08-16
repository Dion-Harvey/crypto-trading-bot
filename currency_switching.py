#!/usr/bin/env python3
"""
💱 DYNAMIC CURRENCY SWITCHING MODULE
Handles intelligent switching between USD and USDT pairs based on:
- Liquidity and spreads
- Volume and market conditions  
- Account balance optimization
"""

import ccxt
import json
from typing import Dict, Optional, Tuple, List

class CurrencySwitch:
    def __init__(self, exchange, config_path='enhanced_config.json'):
        self.exchange = exchange
        self.config_path = config_path
        self.usd_equivalents = {}
        self.load_currency_config()
    
    def load_currency_config(self):
        """Load currency switching configuration"""
        try:
            with open(self.config_path, 'r') as f:
                config = json.load(f)
            
            multi_currency = config.get('multi_currency', {})
            self.usd_equivalents = multi_currency.get('usd_equivalents', {})
            
            # Currency switching parameters
            switching_config = config.get('currency_switching', {})
            self.enabled = switching_config.get('enabled', True)
            self.prefer_higher_volume = switching_config.get('prefer_higher_volume', True)
            self.prefer_tighter_spreads = switching_config.get('prefer_tighter_spreads', True)
            self.usd_premium_threshold = switching_config.get('usd_premium_threshold', 0.001)
            self.usdt_default_preference = switching_config.get('usdt_default_preference', True)
            self.liquidity_threshold = switching_config.get('liquidity_threshold', 100000)
            self.spread_threshold = switching_config.get('spread_threshold', 0.002)
            
        except Exception as e:
            print(f"⚠️ Currency config load error: {e}")
            self.enabled = False
    
    def get_optimal_pair(self, base_currency: str, account_balance: Dict) -> Tuple[str, str]:
        """
        Get the optimal trading pair for a base currency
        Returns: (selected_pair, reason)
        """
        
        if not self.enabled:
            return f"{base_currency}/USDT", "Currency switching disabled"
        
        usdt_pair = f"{base_currency}/USDT"
        usd_pair = self.usd_equivalents.get(usdt_pair)
        
        # If no USD equivalent exists, use USDT
        if not usd_pair:
            return usdt_pair, "No USD pair available"
        
        try:
            # Get market data for both pairs
            usdt_analysis = self._analyze_pair(usdt_pair)
            usd_analysis = self._analyze_pair(usd_pair)
            
            if not usdt_analysis or not usd_analysis:
                # Fall back to USDT if analysis fails
                return usdt_pair, "Analysis failed, defaulting to USDT"
            
            # Check account balances
            usdt_balance = account_balance.get('USDT', {}).get('free', 0)
            usd_balance = account_balance.get('USD', {}).get('free', 0)
            
            # Decision logic
            selected_pair, reason = self._make_currency_decision(
                usdt_pair, usd_pair, usdt_analysis, usd_analysis, 
                usdt_balance, usd_balance
            )
            
            return selected_pair, reason
            
        except Exception as e:
            print(f"⚠️ Optimal pair selection error: {e}")
            return usdt_pair, f"Error: {e}, defaulting to USDT"
    
    def _analyze_pair(self, pair: str) -> Optional[Dict]:
        """Analyze a trading pair for liquidity, spread, and volume"""
        try:
            # Get ticker data
            ticker = self.exchange.fetch_ticker(pair)
            
            # Get order book for spread analysis
            order_book = self.exchange.fetch_order_book(pair, limit=5)
            
            # Calculate metrics
            volume_24h = ticker.get('quoteVolume', 0) or 0
            best_bid = order_book['bids'][0][0] if order_book['bids'] else 0
            best_ask = order_book['asks'][0][0] if order_book['asks'] else 0
            
            spread = (best_ask - best_bid) / best_bid if best_bid > 0 else float('inf')
            spread_pct = spread * 100
            
            # Calculate order book depth
            bid_depth = sum([bid[1] for bid in order_book['bids'][:5]])
            ask_depth = sum([ask[1] for ask in order_book['asks'][:5]])
            total_depth = (bid_depth + ask_depth) * best_bid if best_bid > 0 else 0
            
            return {
                'pair': pair,
                'volume_24h': volume_24h,
                'spread_pct': spread_pct,
                'depth_usd': total_depth,
                'best_bid': best_bid,
                'best_ask': best_ask,
                'last_price': ticker.get('last', 0)
            }
            
        except Exception as e:
            print(f"⚠️ Pair analysis error for {pair}: {e}")
            return None
    
    def _make_currency_decision(self, usdt_pair: str, usd_pair: str, 
                               usdt_data: Dict, usd_data: Dict,
                               usdt_balance: float, usd_balance: float) -> Tuple[str, str]:
        """Make the final currency decision based on all factors"""
        
        decision_factors = []
        usdt_score = 0
        usd_score = 0
        
        # Factor 1: Account balance preference
        if usdt_balance > usd_balance * 1.1:  # 10% preference for larger balance
            usdt_score += 2
            decision_factors.append("USDT balance advantage")
        elif usd_balance > usdt_balance * 1.1:
            usd_score += 2
            decision_factors.append("USD balance advantage")
        
        # Factor 2: Volume comparison
        if self.prefer_higher_volume:
            if usdt_data['volume_24h'] > usd_data['volume_24h'] * 1.1:
                usdt_score += 3
                decision_factors.append("USDT higher volume")
            elif usd_data['volume_24h'] > usdt_data['volume_24h'] * 1.1:
                usd_score += 3
                decision_factors.append("USD higher volume")
        
        # Factor 3: Spread comparison
        if self.prefer_tighter_spreads:
            if usdt_data['spread_pct'] < usd_data['spread_pct'] * 0.9:
                usdt_score += 2
                decision_factors.append("USDT tighter spread")
            elif usd_data['spread_pct'] < usdt_data['spread_pct'] * 0.9:
                usd_score += 2
                decision_factors.append("USD tighter spread")
        
        # Factor 4: Liquidity depth
        if usdt_data['depth_usd'] > usd_data['depth_usd'] * 1.1:
            usdt_score += 2
            decision_factors.append("USDT better depth")
        elif usd_data['depth_usd'] > usdt_data['depth_usd'] * 1.1:
            usd_score += 2
            decision_factors.append("USD better depth")
        
        # Factor 5: Default preference
        if self.usdt_default_preference:
            usdt_score += 1
            decision_factors.append("USDT default preference")
        
        # Factor 6: Liquidity threshold check
        if usdt_data['depth_usd'] < self.liquidity_threshold:
            usd_score += 3
            decision_factors.append("USDT low liquidity penalty")
        if usd_data['depth_usd'] < self.liquidity_threshold:
            usdt_score += 3
            decision_factors.append("USD low liquidity penalty")
        
        # Factor 7: Spread threshold check
        if usdt_data['spread_pct'] > self.spread_threshold * 100:
            usd_score += 2
            decision_factors.append("USDT high spread penalty")
        if usd_data['spread_pct'] > self.spread_threshold * 100:
            usdt_score += 2
            decision_factors.append("USD high spread penalty")
        
        # Make final decision
        if usdt_score > usd_score:
            selected_pair = usdt_pair
            winner = "USDT"
        elif usd_score > usdt_score:
            selected_pair = usd_pair
            winner = "USD"
        else:
            # Tie-breaker: use default preference
            selected_pair = usdt_pair if self.usdt_default_preference else usd_pair
            winner = "USDT (tie-breaker)" if self.usdt_default_preference else "USD (tie-breaker)"
        
        # Create detailed reason
        reason = f"{winner} selected (score: {max(usdt_score, usd_score)}) - {', '.join(decision_factors[:3])}"
        
        return selected_pair, reason
    
    def get_currency_analysis_summary(self, base_currency: str) -> Dict:
        """Get detailed analysis summary for debugging"""
        
        usdt_pair = f"{base_currency}/USDT"
        usd_pair = self.usd_equivalents.get(usdt_pair)
        
        if not usd_pair:
            return {"error": "No USD pair available"}
        
        usdt_analysis = self._analyze_pair(usdt_pair)
        usd_analysis = self._analyze_pair(usd_pair)
        
        return {
            "usdt_analysis": usdt_analysis,
            "usd_analysis": usd_analysis,
            "comparison": {
                "volume_winner": "USDT" if usdt_analysis and usd_analysis and 
                               usdt_analysis['volume_24h'] > usd_analysis['volume_24h'] else "USD",
                "spread_winner": "USDT" if usdt_analysis and usd_analysis and 
                               usdt_analysis['spread_pct'] < usd_analysis['spread_pct'] else "USD",
                "depth_winner": "USDT" if usdt_analysis and usd_analysis and 
                              usdt_analysis['depth_usd'] > usd_analysis['depth_usd'] else "USD"
            }
        }

def safe_get_optimal_pair(exchange, base_currency: str, account_balance: Dict, 
                         config_path='enhanced_config.json') -> Tuple[str, str]:
    """
    Safe wrapper for getting optimal trading pair
    Returns: (pair, reason)
    """
    try:
        currency_switch = CurrencySwitch(exchange, config_path)
        return currency_switch.get_optimal_pair(base_currency, account_balance)
    except Exception as e:
        print(f"⚠️ Currency switching error: {e}")
        return f"{base_currency}/USDT", f"Error: {e}, using USDT default"

def display_currency_analysis(exchange, base_currency: str, config_path='enhanced_config.json'):
    """Display detailed currency analysis for debugging"""
    try:
        currency_switch = CurrencySwitch(exchange, config_path)
        analysis = currency_switch.get_currency_analysis_summary(base_currency)
        
        print(f"\n💱 CURRENCY ANALYSIS: {base_currency}")
        print("=" * 40)
        
        if "error" in analysis:
            print(f"❌ {analysis['error']}")
            return
        
        usdt_data = analysis.get('usdt_analysis', {})
        usd_data = analysis.get('usd_analysis', {})
        comparison = analysis.get('comparison', {})
        
        if usdt_data:
            print(f"📊 {base_currency}/USDT:")
            print(f"   Volume: ${usdt_data['volume_24h']:,.0f}")
            print(f"   Spread: {usdt_data['spread_pct']:.3f}%")
            print(f"   Depth: ${usdt_data['depth_usd']:,.0f}")
        
        if usd_data:
            print(f"📊 {base_currency}/USD:")
            print(f"   Volume: ${usd_data['volume_24h']:,.0f}")
            print(f"   Spread: {usd_data['spread_pct']:.3f}%")
            print(f"   Depth: ${usd_data['depth_usd']:,.0f}")
        
        print(f"\n🏆 Winners:")
        print(f"   Volume: {comparison.get('volume_winner', 'N/A')}")
        print(f"   Spread: {comparison.get('spread_winner', 'N/A')}")
        print(f"   Depth: {comparison.get('depth_winner', 'N/A')}")
        
    except Exception as e:
        print(f"❌ Analysis error: {e}")

if __name__ == "__main__":
    # Test the currency switching module
    print("💱 CURRENCY SWITCHING MODULE TEST")
    print("=" * 40)
    
    # This would normally be used within the bot
    print("✅ Currency switching module ready")
    print("🔄 Integration with main bot required for full functionality")
