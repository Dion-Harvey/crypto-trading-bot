#!/usr/bin/env python3
"""
Simple Bot Signal Test
Direct test of bot detect_ma_crossover_signals function
"""

def main():
    try:
        print("🔍 TESTING BOT ENHANCED SIGNAL DETECTION")
        print("=" * 50)
        
        # Test imports one by one
        print("📥 Testing imports...")
        import ccxt
        print("✅ ccxt imported")
        
        from config import BINANCE_API_KEY, BINANCE_API_SECRET
        print("✅ config imported")
        
        from strategies.ma_crossover import fetch_ohlcv
        print("✅ ma_crossover imported")
        
        # Initialize exchange
        exchange = ccxt.binanceus({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'enableRateLimit': True,
            'options': {'timeDifference': 1000}
        })
        print("✅ Exchange initialized")
        
        # Get market data
        df = fetch_ohlcv(exchange, 'BTC/USDT', '1m', 50)
        ticker = exchange.fetch_ticker('BTC/USDT')
        current_price = ticker['last']
        
        print(f"📊 Current BTC Price: ${current_price:,.2f}")
        print()
        
        # Now test the bot function import
        print("📥 Importing bot function...")
        from bot import detect_ma_crossover_signals
        print("✅ Enhanced bot function imported")
        
        # Test the actual function
        print("🎯 Testing enhanced signal detection...")
        signal = detect_ma_crossover_signals(df, current_price)
        
        print(f"🎯 ENHANCED SIGNAL RESULTS:")
        print(f"   Action: {signal.get('action', 'N/A')}")
        print(f"   Confidence: {signal.get('confidence', 0):.3f}")
        print(f"   Type: {signal.get('crossover_type', 'N/A')}")
        
        # Compare with threshold
        from enhanced_config import get_bot_config
        config = get_bot_config()
        threshold = config.config['strategy_parameters']['confidence_threshold']
        
        print(f"\n⚖️ THRESHOLD COMPARISON:")
        print(f"   Signal: {signal.get('confidence', 0):.3f}")
        print(f"   Required: {threshold:.3f}")
        
        if signal.get('confidence', 0) >= threshold:
            print("✅ ENHANCED SIGNAL WOULD EXECUTE!")
        else:
            print("❌ Signal below threshold")
            
        print("\n🔍 Enhanced bot signal test completed!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
