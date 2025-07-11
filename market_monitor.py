#!/usr/bin/env python3
"""
Market Conditions Monitor - Track when trading conditions improve
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime
import ccxt
from config import BINANCE_API_KEY, BINANCE_API_SECRET
from success_rate_enhancer import SuccessRateEnhancer, check_anti_whipsaw_protection

def check_trading_readiness():
    """Quick check of trading readiness"""
    
    # Load enhanced config
    with open('enhanced_config.json', 'r') as f:
        enhanced_config = json.load(f)
    
    # Initialize exchange
    exchange = ccxt.binanceus({
        'apiKey': BINANCE_API_KEY,
        'secret': BINANCE_API_SECRET,
        'sandbox': False,
        'rateLimit': 1200,
        'options': {'defaultType': 'spot'}
    })
    
    try:
        # Get market data
        ohlcv = exchange.fetch_ohlcv('BTC/USDC', '5m', limit=200)
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        current_price = df['close'].iloc[-1]
        
        # Calculate key indicators
        def calculate_rsi(prices, window=14):
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        
        rsi = calculate_rsi(df['close']).iloc[-1]
        
        # Moving averages
        ema_7 = df['close'].ewm(span=7).mean().iloc[-1]
        ema_25 = df['close'].ewm(span=25).mean().iloc[-1]
        ema_99 = df['close'].ewm(span=99).mean().iloc[-1]
        ma_trend_aligned = ema_7 > ema_25 > ema_99
        
        # Volume
        recent_volume = df['volume'].iloc[-5:].mean()
        avg_volume = df['volume'].iloc[-20:].mean()
        volume_ratio = recent_volume / avg_volume
        volume_ok = volume_ratio > enhanced_config['market_filters']['volume_confirmation_threshold']
        
        # Quality analysis
        enhancer = SuccessRateEnhancer()
        mock_signal = {'action': 'BUY', 'confidence': 0.7, 'vote_count': {'BUY': 5}}
        quality_analysis = enhancer.analyze_signal_quality(df, mock_signal, current_price)
        quality_ok = quality_analysis['overall_quality_score'] >= 0.6
        
        # Anti-whipsaw
        whipsaw_safe = check_anti_whipsaw_protection(mock_signal, current_price, df)
        
        # Summary
        checks = [
            ('Quality Score', quality_ok, f"{quality_analysis['overall_quality_score']:.3f}/0.600"),
            ('MA Trend', ma_trend_aligned, f"EMA7>{ma_trend_aligned}EMA25>EMA99"),
            ('Volume', volume_ok, f"{volume_ratio:.2f}x/{enhanced_config['market_filters']['volume_confirmation_threshold']}x"),
            ('Anti-Whipsaw', whipsaw_safe, "Safe" if whipsaw_safe else "Choppy"),
            ('RSI', 25 <= rsi <= 75, f"{rsi:.1f}")
        ]
        
        passed = sum(1 for _, check, _ in checks if check)
        
        # Status
        if passed >= 4:
            status = "🟢 READY TO TRADE"
        elif passed >= 2:
            status = "🟡 WAIT FOR BETTER CONDITIONS"
        else:
            status = "🔴 POOR CONDITIONS - WAIT"
        
        print(f"⏰ {datetime.now().strftime('%H:%M:%S')} | 💰 ${current_price:,.0f} | {status} ({passed}/5)")
        
        # Details if not ready
        if passed < 4:
            for name, check, value in checks:
                icon = "✅" if check else "❌"
                print(f"   {icon} {name}: {value}")
                
        return passed >= 4
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    print("🔍 BTC Trading Readiness Monitor")
    print("=" * 50)
    check_trading_readiness()
    print("\n💡 Tip: Run this periodically to see when conditions improve")
    print("   The bot will automatically trade when all filters pass!")
