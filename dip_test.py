#!/usr/bin/env python3
"""
🎯 DIP DETECTION TEST
Test the enhanced dip detection logic to see if it identifies current conditions as a dip opportunity
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import BINANCE_API_KEY, BINANCE_API_SECRET
from strategies.ma_crossover import fetch_ohlcv
from enhanced_config import get_bot_config
import ccxt
import pandas as pd

# Initialize exchange
exchange = ccxt.binanceus({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_API_SECRET,
    'enableRateLimit': True,
    'timeout': 30000,
    'options': {
        'timeDifference': 1000,
        'adjustForTimeDifference': True
    }
})

def test_enhanced_dip_detection():
    """Test the enhanced dip detection logic"""
    try:
        print("🔍 ENHANCED DIP DETECTION TEST")
        print("=" * 50)
        
        # Get current data
        symbol = 'BTC/USDT'
        df = fetch_ohlcv(exchange, symbol, '1m', 50)
        current_price = df['close'].iloc[-1]
        
        print(f"📊 Current BTC Price: ${current_price:,.2f}")
        
        # Calculate EMAs
        ema_7 = df['close'].ewm(span=7).mean()
        ema_25 = df['close'].ewm(span=25).mean()
        ema7_current = ema_7.iloc[-1]
        ema25_current = ema_25.iloc[-1]
        
        print(f"📈 EMA7: ${ema7_current:,.2f}")
        print(f"📈 EMA25: ${ema25_current:,.2f}")
        
        # Calculate price positions
        price_vs_ema7 = (current_price - ema7_current) / ema7_current
        price_vs_ema25 = (current_price - ema25_current) / ema25_current
        
        print(f"📊 Price vs EMA7: {price_vs_ema7*100:+.2f}%")
        print(f"📊 Price vs EMA25: {price_vs_ema25*100:+.2f}%")
        
        # Calculate momentum
        if len(df) >= 5:
            price_momentum = (current_price - df['close'].iloc[-6]) / df['close'].iloc[-6]
            print(f"📊 Recent Momentum (5-period): {price_momentum*100:+.2f}%")
        else:
            price_momentum = 0
        
        # Calculate RSI
        try:
            price_changes = df['close'].pct_change().fillna(0)
            gains = price_changes.where(price_changes > 0, 0).rolling(14).mean()
            losses = (-price_changes.where(price_changes < 0, 0)).rolling(14).mean()
            rs = gains / losses
            rsi = 100 - (100 / (1 + rs.iloc[-1])) if not pd.isna(rs.iloc[-1]) else 50
        except:
            rsi = 50
        
        # Test enhanced dip conditions (updated thresholds)
        dip_below_ema7 = price_vs_ema7 < 0.001  # Price even slightly below EMA7 (0.1%)
        weak_dip_below_ema7 = price_vs_ema7 < 0.005  # Price within 0.5% of EMA7
        dip_below_ema25 = price_vs_ema25 < -0.002  # Price more than 0.2% below EMA25
        oversold_momentum = price_momentum < -0.002  # Recent downward momentum > 0.2%
        mild_oversold_momentum = price_momentum < 0.002  # Very mild negative or flat momentum
        
        print(f"\n🎯 ENHANCED DIP CONDITIONS:")
        print(f"   Dip below EMA7 (0.1%): {'✅' if dip_below_ema7 else '❌'}")
        print(f"   Weak dip near EMA7 (0.5%): {'✅' if weak_dip_below_ema7 else '❌'}")
        print(f"   Dip below EMA25 (-0.2%): {'✅' if dip_below_ema25 else '❌'}")
        print(f"   Oversold momentum (-0.2%): {'✅' if oversold_momentum else '❌'}")
        print(f"   Mild oversold momentum (0.2%): {'✅' if mild_oversold_momentum else '❌'}")
        print(f"   RSI oversold (<40): {'✅' if rsi < 40 else '❌'} (RSI: {rsi:.1f})")
        print(f"   Strong RSI oversold (<35): {'✅' if rsi < 35 else '❌'}")
        
        # Test enhanced dip signals
        print(f"\n🎯 ENHANCED DIP ANALYSIS:")
        
        # Primary dip signal
        if dip_below_ema7 and (oversold_momentum or rsi < 40):
            confidence = 0.65
            print(f"✅ ENHANCED DIP DETECTED!")
            print(f"   Base confidence: {confidence:.2f}")
            print(f"   Trigger: Price near/below EMA7 + (momentum or RSI oversold)")
            
            if dip_below_ema25:
                confidence += 0.15
                print(f"   Deep dip bonus: +0.15 → {confidence:.2f}")
            
            if rsi < 35:
                confidence += 0.15
                print(f"   Strong RSI oversold bonus: +0.15 → {confidence:.2f}")
            elif rsi < 40:
                confidence += 0.08
                print(f"   RSI oversold bonus: +0.08 → {confidence:.2f}")
            
            final_confidence = min(confidence, 0.9)
            print(f"✅ FINAL DIP SIGNAL: BUY with {final_confidence:.2f} confidence")
        
        # RSI oversold signal
        elif rsi < 35 and weak_dip_below_ema7 and mild_oversold_momentum:
            confidence = 0.55
            print(f"✅ RSI OVERSOLD SIGNAL DETECTED!")
            print(f"   Base confidence: {confidence:.2f}")
            print(f"   Trigger: Strong RSI oversold + price near EMA7 + mild momentum")
            
            if dip_below_ema25:
                confidence += 0.1
                print(f"   Below EMA25 bonus: +0.10 → {confidence:.2f}")
            
            print(f"✅ RSI OVERSOLD SIGNAL: BUY with {confidence:.2f} confidence")
        
        # Moderate dip signal
        elif (dip_below_ema7 or rsi < 40) and price_momentum < 0.005:
            confidence = 0.45
            print(f"✅ MODERATE DIP DETECTED!")
            print(f"   Base confidence: {confidence:.2f}")
            print(f"   Trigger: (Dip below EMA7 or RSI oversold) + mild momentum")
            
            if rsi < 45:
                confidence += 0.05
                print(f"   RSI support bonus: +0.05 → {confidence:.2f}")
            
            if dip_below_ema25:
                confidence += 0.05
                print(f"   Below EMA25 bonus: +0.05 → {confidence:.2f}")
            
            print(f"✅ MODERATE DIP SIGNAL: BUY with {confidence:.2f} confidence")
            
        else:
            print(f"❌ NO DIP SIGNAL")
            print(f"   Current conditions don't meet enhanced dip criteria")
            
            # Check if it would trigger trend following
            ema_spread = abs(ema7_current - ema25_current) / ema25_current * 100
            print(f"\n🔍 TREND ANALYSIS:")
            print(f"   EMA7 > EMA25: {'✅' if ema7_current > ema25_current else '❌'}")
            print(f"   EMA spread > 1%: {'✅' if ema_spread > 1.0 else '❌'} ({ema_spread:.2f}%)")
            print(f"   Price near EMA7 (<1%): {'✅' if price_vs_ema7 < 0.01 else '❌'}")
        
        # Test against thresholds
        config = get_bot_config()
        base_threshold = config.config['strategy_parameters']['confidence_threshold']
        dip_reduction = config.config['strategy_parameters'].get('dip_confidence_reduction', 0.15)
        
        print(f"\n🎯 THRESHOLD ANALYSIS:")
        print(f"   Base threshold: {base_threshold:.3f}")
        print(f"   Dip threshold: {base_threshold - dip_reduction:.3f}")
        
        # Show which signals would pass
        signals_tested = [
            ("Enhanced Dip", 0.73 if dip_below_ema7 and (oversold_momentum or rsi < 40) else 0),
            ("RSI Oversold", 0.55 if rsi < 35 and weak_dip_below_ema7 and mild_oversold_momentum else 0),
            ("Moderate Dip", 0.50 if (dip_below_ema7 or rsi < 40) and price_momentum < 0.005 else 0)
        ]
        
        print(f"\n🎯 SIGNAL THRESHOLD CHECK:")
        for signal_name, confidence in signals_tested:
            if confidence > 0:
                passes_base = confidence >= base_threshold
                passes_dip = confidence >= (base_threshold - dip_reduction)
                print(f"   {signal_name}: {confidence:.2f} - Base: {'✅' if passes_base else '❌'} | Dip: {'✅' if passes_dip else '❌'}")
        
    except Exception as e:
        print(f"❌ Error in dip detection test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_dip_detection()
