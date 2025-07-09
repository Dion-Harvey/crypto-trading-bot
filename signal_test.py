#!/usr/bin/env python3
"""
Real-time Signal Test
Check current MA7/MA25 signals and market conditions
"""

def test_current_signals():
    try:
        import ccxt
        from config import BINANCE_API_KEY, BINANCE_API_SECRET
        from strategies.ma_crossover import fetch_ohlcv
        from log_utils import log_message
        from enhanced_config import get_bot_config
        
        print("🔍 REAL-TIME SIGNAL TEST")
        print("=" * 50)
        
        # Initialize exchange
        exchange = ccxt.binanceus({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'enableRateLimit': True,
            'options': {'timeDifference': 1000}
        })
        
        # Get current market data
        df = fetch_ohlcv(exchange, 'BTC/USDC', '1h', 50)
        ticker = exchange.fetch_ticker('BTC/USDC')
        current_price = ticker['last']
        
        print(f"📊 Current BTC Price: ${current_price:,.2f}")
        print(f"📈 24h Change: {ticker['percentage']:+.2f}%")
        print()
        
        # Test MA7/MA25 signals
        if len(df) >= 25:
            ma_7 = df['close'].rolling(7).mean()
            ma_25 = df['close'].rolling(25).mean()
            
            ma7_current = ma_7.iloc[-1]
            ma25_current = ma_25.iloc[-1]
            ma7_previous = ma_7.iloc[-2]
            ma25_previous = ma_25.iloc[-2]
            
            # Crossover detection
            golden_cross = (ma7_previous <= ma25_previous) and (ma7_current > ma25_current)
            death_cross = (ma7_previous >= ma25_previous) and (ma7_current < ma25_current)
            
            ma_spread = abs(ma7_current - ma25_current) / ma25_current * 100
            price_above_ma7 = current_price > ma7_current
            price_above_ma25 = current_price > ma25_current
            
            print("🎯 MA7/MA25 ANALYSIS:")
            print(f"   MA7: ${ma7_current:,.2f}")
            print(f"   MA25: ${ma25_current:,.2f}")
            print(f"   Spread: {ma_spread:.3f}%")
            print(f"   Price vs MA7: {'Above' if price_above_ma7 else 'Below'} ({((current_price/ma7_current-1)*100):+.2f}%)")
            print(f"   Price vs MA25: {'Above' if price_above_ma25 else 'Below'} ({((current_price/ma25_current-1)*100):+.2f}%)")
            print()
            
            # Signal analysis
            if golden_cross:
                signal = "🟢 GOLDEN CROSS - STRONG BUY SIGNAL"
                confidence = 0.85
            elif death_cross:
                signal = "🔴 DEATH CROSS - STRONG SELL SIGNAL"
                confidence = 0.85
            elif ma7_current > ma25_current and ma_spread > 1.0:
                signal = "📈 BULLISH TREND CONTINUATION"
                confidence = 0.75 + (min(ma_spread, 5) / 5 * 0.15)
            elif ma7_current < ma25_current and ma_spread > 1.0:
                signal = "📉 BEARISH TREND CONTINUATION"
                confidence = 0.75 + (min(ma_spread, 5) / 5 * 0.15)
            else:
                signal = "⏳ NO CLEAR SIGNAL"
                confidence = 0.0
            
            print(f"🎯 CURRENT SIGNAL: {signal}")
            print(f"🔥 Confidence: {confidence:.3f}")
            
            # Check against config threshold
            config = get_bot_config()
            threshold = config.config['strategy_parameters']['confidence_threshold']
            print(f"⚖️ Required Threshold: {threshold:.3f}")
            
            if confidence >= threshold:
                print("✅ SIGNAL STRONG ENOUGH FOR TRADE")
            else:
                print("❌ SIGNAL TOO WEAK - Below threshold")
                print(f"   Need {threshold - confidence:.3f} more confidence")
            
            print()
            
            # Volume analysis
            if 'volume' in df.columns:
                try:
                    recent_volume = df['volume'].iloc[-10:].mean()
                    avg_volume = df['volume'].iloc[-50:].mean()
                    volume_ratio = recent_volume / avg_volume
                    
                    print(f"📊 Volume Analysis:")
                    print(f"   Recent 10h Avg: {recent_volume:,.0f}")
                    print(f"   50h Average: {avg_volume:,.0f}")
                    print(f"   Volume Ratio: {volume_ratio:.2f}x")
                    
                    if volume_ratio > 1.2:
                        print("   ✅ High volume supports signal")
                    else:
                        print("   ⚠️ Low volume - weaker signal")
                except:
                    print("   ⚠️ Volume data unavailable")
            
            log_message(f"🔍 SIGNAL TEST: {signal}, Confidence: {confidence:.3f}, Threshold: {threshold:.3f}")
            
        else:
            print("❌ Insufficient data for analysis")
        
        print()
        print("🔍 Signal test completed!")
        
    except Exception as e:
        print(f"❌ Signal test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_current_signals()
