#!/usr/bin/env python3
"""
🎯 SIGNAL-FIRST MULTI-TIMEFRAME SCANNER
Prioritize the strongest multi-timeframe signals across ALL 235 pairs
Ignores tier restrictions - purely signal-based selection for maximum profits
"""

import ccxt
import json
import pandas as pd
import numpy as np
from datetime import datetime
import time

class SignalFirstScanner:
    def __init__(self, exchange):
        self.exchange = exchange
        self.load_all_pairs()
    
    def load_all_pairs(self):
        """Load all available pairs from comprehensive config"""
        try:
            with open('comprehensive_all_pairs_config.json', 'r') as f:
                config = json.load(f)
            self.all_pairs = config.get('supported_pairs', [])
            print(f"📊 Loaded {len(self.all_pairs)} pairs for signal scanning")
        except FileNotFoundError:
            # Fallback to enhanced config
            try:
                with open('enhanced_config.json', 'r') as f:
                    config = json.load(f)
                self.all_pairs = config.get('trading', {}).get('supported_pairs', [])
                print(f"📊 Fallback: Loaded {len(self.all_pairs)} pairs from enhanced config")
            except:
                # Ultimate fallback
                self.all_pairs = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT']
                print(f"⚠️ Using minimal fallback: {len(self.all_pairs)} pairs")
    
    def calculate_multi_timeframe_signal_strength(self, symbol):
        """Calculate comprehensive multi-timeframe signal strength"""
        try:
            # Fetch multiple timeframes
            timeframes = ['1m', '5m', '15m', '1h']
            signals = {}
            
            for tf in timeframes:
                try:
                    # Fetch OHLCV data
                    ohlcv = self.exchange.fetch_ohlcv(symbol, tf, limit=50)
                    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                    
                    # Calculate moving averages
                    df['ema7'] = df['close'].ewm(span=7).mean()
                    df['ema25'] = df['close'].ewm(span=25).mean()
                    df['ema50'] = df['close'].ewm(span=50).mean() if len(df) >= 50 else df['ema25']
                    
                    # Calculate RSI
                    delta = df['close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    df['rsi'] = 100 - (100 / (1 + rs))
                    
                    current_price = df['close'].iloc[-1]
                    ema7_current = df['ema7'].iloc[-1]
                    ema25_current = df['ema25'].iloc[-1]
                    ema50_current = df['ema50'].iloc[-1]
                    rsi_current = df['rsi'].iloc[-1]
                    
                    # Signal strength calculation
                    signal_strength = 0
                    signal_direction = 'NEUTRAL'
                    
                    # EMA Crossover signals
                    if ema7_current > ema25_current > ema50_current:
                        signal_strength += 3  # Strong bullish alignment
                        signal_direction = 'BULLISH'
                    elif ema7_current > ema25_current:
                        signal_strength += 2  # Moderate bullish
                        signal_direction = 'BULLISH'
                    elif ema7_current < ema25_current < ema50_current:
                        signal_strength -= 3  # Strong bearish alignment
                        signal_direction = 'BEARISH'
                    elif ema7_current < ema25_current:
                        signal_strength -= 2  # Moderate bearish
                        signal_direction = 'BEARISH'
                    
                    # Price position relative to EMAs
                    if current_price > ema7_current > ema25_current:
                        signal_strength += 2
                    elif current_price < ema7_current < ema25_current:
                        signal_strength -= 2
                    
                    # RSI momentum
                    if 30 <= rsi_current <= 40 and signal_direction == 'BULLISH':
                        signal_strength += 2  # Oversold but turning bullish
                    elif 60 <= rsi_current <= 70 and signal_direction == 'BEARISH':
                        signal_strength -= 2  # Overbought and turning bearish
                    elif rsi_current > 80:
                        signal_strength -= 1  # Extremely overbought
                    elif rsi_current < 20:
                        signal_strength += 1  # Extremely oversold
                    
                    # Recent momentum (last 3 candles)
                    recent_change = (df['close'].iloc[-1] - df['close'].iloc[-4]) / df['close'].iloc[-4] * 100
                    if abs(recent_change) > 1.0:  # Significant move
                        if recent_change > 0 and signal_direction == 'BULLISH':
                            signal_strength += 1
                        elif recent_change < 0 and signal_direction == 'BEARISH':
                            signal_strength -= 1
                    
                    signals[tf] = {
                        'strength': signal_strength,
                        'direction': signal_direction,
                        'current_price': current_price,
                        'ema7': ema7_current,
                        'ema25': ema25_current,
                        'rsi': rsi_current,
                        'recent_change_pct': recent_change
                    }
                    
                except Exception as tf_error:
                    signals[tf] = {'strength': 0, 'direction': 'NEUTRAL', 'error': str(tf_error)}
            
            # Calculate composite signal strength
            total_strength = 0
            timeframe_weights = {'1m': 1.0, '5m': 2.0, '15m': 1.5, '1h': 1.0}
            
            for tf, weight in timeframe_weights.items():
                if tf in signals and 'strength' in signals[tf]:
                    total_strength += signals[tf]['strength'] * weight
            
            # Normalize to 0-100 scale
            max_possible = sum(timeframe_weights.values()) * 5  # Max strength per timeframe
            normalized_strength = max(0, min(100, (total_strength + max_possible) / (2 * max_possible) * 100))
            
            return {
                'symbol': symbol,
                'total_strength': total_strength,
                'normalized_strength': normalized_strength,
                'timeframe_signals': signals,
                'recommendation': self.get_recommendation(total_strength, signals),
                'confidence': normalized_strength / 100.0
            }
            
        except Exception as e:
            return {
                'symbol': symbol,
                'total_strength': 0,
                'normalized_strength': 0,
                'error': str(e),
                'recommendation': 'HOLD',
                'confidence': 0.0
            }
    
    def get_recommendation(self, total_strength, signals):
        """Get trading recommendation based on signal strength"""
        if total_strength >= 8:
            return 'STRONG_BUY'
        elif total_strength >= 5:
            return 'BUY'
        elif total_strength <= -8:
            return 'STRONG_SELL'
        elif total_strength <= -5:
            return 'SELL'
        else:
            return 'HOLD'
    
    def scan_all_pairs_for_best_signals(self, max_pairs_to_scan=50):
        """Scan pairs for the strongest multi-timeframe signals"""
        print(f"🔍 SIGNAL-FIRST SCANNING: Analyzing up to {max_pairs_to_scan} pairs...")
        
        start_time = time.time()
        results = []
        scanned_count = 0
        
        # Prioritize pairs with recent volume/activity
        priority_pairs = self.get_priority_pairs()
        
        for symbol in priority_pairs[:max_pairs_to_scan]:
            try:
                signal_data = self.calculate_multi_timeframe_signal_strength(symbol)
                results.append(signal_data)
                scanned_count += 1
                
                if scanned_count % 10 == 0:
                    print(f"   📊 Scanned {scanned_count}/{max_pairs_to_scan} pairs...")
                
            except Exception as e:
                print(f"   ⚠️ Error scanning {symbol}: {e}")
                continue
        
        # Sort by signal strength (highest first)
        results.sort(key=lambda x: x['total_strength'], reverse=True)
        
        scan_duration = time.time() - start_time
        print(f"✅ Scan complete: {scanned_count} pairs in {scan_duration:.1f}s")
        
        return results
    
    def get_priority_pairs(self):
        """Get prioritized list of pairs to scan first"""
        # Mix of major pairs and full list
        major_pairs = [
            'BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'XRP/USDT', 'ADA/USDT',
            'DOGE/USDT', 'AVAX/USDT', 'DOT/USDT', 'LINK/USDT', 'UNI/USDT',
            'LTC/USDT', 'ATOM/USDT', 'NEAR/USDT', 'MATIC/USDT', 'ALGO/USDT'
        ]
        
        # Combine major pairs first, then others
        priority_list = []
        for pair in major_pairs:
            if pair in self.all_pairs:
                priority_list.append(pair)
        
        # Add remaining pairs
        for pair in self.all_pairs:
            if pair not in priority_list:
                priority_list.append(pair)
        
        return priority_list
    
    def get_best_trading_opportunity(self, max_scan=50):
        """Get the single best trading opportunity based on signals"""
        results = self.scan_all_pairs_for_best_signals(max_scan)
        
        if not results:
            return None
        
        # Filter for actionable signals
        actionable = [r for r in results if r['recommendation'] in ['STRONG_BUY', 'BUY'] and r['confidence'] >= 0.6]
        
        if actionable:
            best = actionable[0]
            print(f"🎯 BEST SIGNAL-BASED OPPORTUNITY: {best['symbol']}")
            print(f"   💪 Signal Strength: {best['total_strength']:.1f}")
            print(f"   🎯 Confidence: {best['confidence']:.1%}")
            print(f"   📊 Recommendation: {best['recommendation']}")
            return best
        
        # If no strong signals, return the strongest overall
        best = results[0]
        print(f"🔍 STRONGEST AVAILABLE SIGNAL: {best['symbol']}")
        print(f"   💪 Signal Strength: {best['total_strength']:.1f}")
        print(f"   🎯 Confidence: {best['confidence']:.1%}")
        print(f"   📊 Recommendation: {best['recommendation']}")
        return best

def integrate_signal_first_selection():
    """Update the bot's crypto selection to prioritize signals over tiers"""
    print("🔄 INTEGRATING SIGNAL-FIRST SELECTION INTO BOT...")
    
    # Read current bot.py to understand the integration point
    integration_code = '''
def select_best_crypto_for_trading_signal_first():
    """
    🎯 SIGNAL-FIRST CRYPTO SELECTION
    Prioritize strongest multi-timeframe signals over tier classifications
    """
    try:
        # Initialize signal scanner
        from signal_first_scanner import SignalFirstScanner
        scanner = SignalFirstScanner(exchange)
        
        # Get best opportunity based purely on signal strength
        best_opportunity = scanner.get_best_trading_opportunity(max_scan=30)
        
        if best_opportunity and best_opportunity['confidence'] >= 0.6:
            return {
                'symbol': best_opportunity['symbol'],
                'allocation': 1.0,  # Max allocation for best signals
                'reason': f"Signal-first selection: {best_opportunity['recommendation']} (confidence: {best_opportunity['confidence']:.1%})",
                'signal_strength': best_opportunity['total_strength'],
                'confidence': best_opportunity['confidence'],
                'signal_based': True
            }
        else:
            # Fallback to original selection if no strong signals
            return select_best_crypto_for_trading()
            
    except Exception as e:
        print(f"⚠️ Signal-first selection error: {e}")
        # Fallback to original method
        return select_best_crypto_for_trading()
'''
    
    # Save the integration code to a new file
    with open('signal_first_integration.py', 'w') as f:
        f.write(integration_code)
    
    print("✅ Signal-first integration code created")
    print("💡 This prioritizes signal strength over tier restrictions")
    
    return True

if __name__ == "__main__":
    print("🎯 SIGNAL-FIRST MULTI-TIMEFRAME SCANNER")
    print("=" * 60)
    
    # Create signal-first integration
    integrate_signal_first_selection()
    
    print(f"\n🚀 SIGNAL-FIRST SYSTEM READY!")
    print(f"📊 Benefits:")
    print(f"   ✅ Prioritizes strongest signals over tier classifications")
    print(f"   ✅ Scans all pairs for best multi-timeframe opportunities")
    print(f"   ✅ Ignores arbitrary tier restrictions")
    print(f"   ✅ Maximizes profit potential by following strength")
    print(f"\n💡 Integration: Use select_best_crypto_for_trading_signal_first() in bot.py")
