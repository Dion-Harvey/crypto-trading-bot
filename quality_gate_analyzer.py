#!/usr/bin/env python3
"""
Quality Gate Analyzer - Debug why signals are failing the minimum quality gate
"""

import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import ccxt
from config import BINANCE_API_KEY, BINANCE_API_SECRET
from success_rate_enhancer import SuccessRateEnhancer, check_anti_whipsaw_protection
from log_utils import log_message

def analyze_quality_gate():
    """Analyze why signals are failing the quality gate"""
    
    print("🔍 QUALITY GATE ANALYZER")
    print("=" * 50)
    
    # Load enhanced config
    with open('enhanced_config.json', 'r') as f:
        enhanced_config = json.load(f)
    
    # Initialize exchange with API keys
    exchange = ccxt.binanceus({
        'apiKey': BINANCE_API_KEY,
        'secret': BINANCE_API_SECRET,
        'sandbox': False,
        'rateLimit': 1200,
        'options': {
            'defaultType': 'spot'
        }
    })
    
    try:
        # Get recent market data
        symbol = 'BTC/USDC'
        timeframe = '5m'
        limit = 200
        
        print(f"📊 Fetching {symbol} data ({timeframe})...")
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
        
        df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
        df.set_index('timestamp', inplace=True)
        
        current_price = df['close'].iloc[-1]
        print(f"💰 Current BTC/USDC Price: ${current_price:,.2f}")
        
        # Calculate technical indicators
        print("\n📈 Technical Analysis:")
        
        # RSI
        def calculate_rsi(prices, window=14):
            delta = prices.diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            return rsi
        
        rsi = calculate_rsi(df['close'])
        current_rsi = rsi.iloc[-1]
        print(f"   RSI: {current_rsi:.1f}")
        
        # Moving averages
        ema_7 = df['close'].ewm(span=7).mean().iloc[-1]
        ema_25 = df['close'].ewm(span=25).mean().iloc[-1]
        ema_99 = df['close'].ewm(span=99).mean().iloc[-1]
        
        print(f"   EMA 7: ${ema_7:.2f}")
        print(f"   EMA 25: ${ema_25:.2f}")
        print(f"   EMA 99: ${ema_99:.2f}")
        
        ma_trend_aligned = ema_7 > ema_25 > ema_99
        print(f"   MA Trend Aligned: {ma_trend_aligned}")
        
        # Volume analysis
        recent_volume = df['volume'].iloc[-5:].mean()
        avg_volume = df['volume'].iloc[-20:].mean()
        volume_ratio = recent_volume / avg_volume
        print(f"   Volume Ratio: {volume_ratio:.2f}x (recent vs avg)")
        
        # Market volatility
        volatility = df['close'].pct_change().rolling(20).std().iloc[-1]
        print(f"   Volatility (20-period): {volatility:.4f}")
        
        # Simulate quality analysis
        print("\n🎯 QUALITY GATE ANALYSIS:")
        
        enhancer = SuccessRateEnhancer()
        
        # Create a mock BUY signal
        mock_signal = {
            'action': 'BUY',
            'confidence': 0.7,
            'vote_count': {'BUY': 5, 'SELL': 2},
            'reason': 'Mock signal for testing'
        }
        
        # Run quality analysis
        quality_analysis = enhancer.analyze_signal_quality(df, mock_signal, current_price)
        
        print(f"📊 Quality Scores:")
        for factor, score in quality_analysis['quality_factors'].items():
            status = "✅" if score >= 0.6 else "⚠️" if score >= 0.4 else "❌"
            print(f"   {status} {factor.replace('_', ' ').title()}: {score:.3f}")
        
        overall_score = quality_analysis['overall_quality_score']
        print(f"\n🎯 Overall Quality Score: {overall_score:.3f}")
        print(f"   Minimum Required: 0.600")
        print(f"   Quality Gate: {'✅ PASS' if overall_score >= 0.6 else '❌ FAIL'}")
        
        # Check individual filters
        print(f"\n🛡️ FILTER ANALYSIS:")
        
        # MA Trend Filter
        market_config = enhanced_config.get('market_filters', {})
        if market_config.get('ma_trend_filter_enabled', True):
            print(f"   MA Trend Filter: {'✅ PASS' if ma_trend_aligned else '❌ FAIL'}")
            if not ma_trend_aligned:
                print(f"     EMA 7 ({ema_7:.2f}) > EMA 25 ({ema_25:.2f}) > EMA 99 ({ema_99:.2f})")
        
        # RSI Range Filter
        rsi_config = market_config.get('rsi_range_filter', {})
        if rsi_config.get('enabled', False):
            avoid_min = rsi_config['avoid_range_min']
            avoid_max = rsi_config['avoid_range_max']
            rsi_in_avoid_range = avoid_min <= current_rsi <= avoid_max
            print(f"   RSI Range Filter: {'❌ FAIL' if rsi_in_avoid_range else '✅ PASS'}")
            if rsi_in_avoid_range:
                print(f"     RSI {current_rsi:.1f} is in choppy range {avoid_min}-{avoid_max}")
        
        # Anti-whipsaw protection
        whipsaw_safe = check_anti_whipsaw_protection(mock_signal, current_price, df)
        print(f"   Anti-Whipsaw: {'✅ PASS' if whipsaw_safe else '❌ FAIL'}")
        
        # Volume confirmation
        volume_confirmed = volume_ratio > enhanced_config['market_filters']['volume_confirmation_threshold']
        print(f"   Volume Confirmation: {'✅ PASS' if volume_confirmed else '❌ FAIL'}")
        print(f"     Required: >{enhanced_config['market_filters']['volume_confirmation_threshold']}x, Current: {volume_ratio:.2f}x")
        
        # Confidence threshold
        confidence_threshold = enhanced_config['strategy_parameters']['confidence_threshold']
        confidence_met = mock_signal['confidence'] >= confidence_threshold
        print(f"   Confidence Threshold: {'✅ PASS' if confidence_met else '❌ FAIL'}")
        print(f"     Required: ≥{confidence_threshold}, Mock Signal: {mock_signal['confidence']}")
        
        # Summary
        print(f"\n📋 SUMMARY:")
        all_checks = [
            ('Quality Gate', overall_score >= 0.6),
            ('MA Trend', ma_trend_aligned),
            ('RSI Range', not (rsi_config.get('enabled', False) and avoid_min <= current_rsi <= avoid_max) if rsi_config.get('enabled', False) else True),
            ('Anti-Whipsaw', whipsaw_safe),
            ('Volume', volume_confirmed),
            ('Confidence', confidence_met)
        ]
        
        passed = sum(1 for _, check in all_checks if check)
        total = len(all_checks)
        
        print(f"   Filters Passed: {passed}/{total}")
        
        if passed == total:
            print("   🎉 All filters would PASS - signal would be accepted")
        else:
            print("   ⚠️ Some filters failed - signal would be rejected")
            print("\n🔧 RECOMMENDATIONS:")
            
            if overall_score < 0.6:
                print("   • Quality score too low - wait for better market conditions")
                
            if not ma_trend_aligned:
                print("   • MA trend not aligned - wait for clearer uptrend")
                
            if rsi_config.get('enabled', False) and avoid_min <= current_rsi <= avoid_max:
                print(f"   • RSI in choppy range ({current_rsi:.1f}) - wait for RSI <{avoid_min} or >{avoid_max}")
                
            if not whipsaw_safe:
                print("   • Anti-whipsaw protection active - market too choppy")
                
            if not volume_confirmed:
                print(f"   • Volume too low - need >{enhanced_config['market_filters']['volume_confirmation_threshold']}x average")
        
        print(f"\n⏰ Analysis completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Exception as e:
        print(f"❌ Error in quality gate analysis: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_quality_gate()
