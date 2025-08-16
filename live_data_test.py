#!/usr/bin/env python3
"""
Live Data Polling Test - Verify Binance US real-time data
"""

import time
import sys
import ccxt
from datetime import datetime
from config import BINANCE_API_KEY, BINANCE_API_SECRET

# Initialize exchange
exchange = ccxt.binanceus({
    'apiKey': BINANCE_API_KEY,
    'secret': BINANCE_API_SECRET,
    'enableRateLimit': True,
    'timeout': 30000,
    'rateLimit': 1200,
    'options': {
        'recvWindow': 10000,
        'timeDifference': 1000,
        'adjustForTimeDifference': True
    }
})

def test_live_data_polling():
    """Test live data polling from Binance US"""
    print("🔍 LIVE DATA POLLING TEST")
    print("=" * 50)
    
    previous_price = None
    poll_count = 0
    
    try:
        for i in range(10):  # Test 10 polls
            poll_count += 1
            
            # Get current timestamp
            timestamp = datetime.now().strftime("%H:%M:%S")
            
            # Fetch live ticker data
            ticker = exchange.fetch_ticker('BTC/USDC')
            current_price = ticker['last']
            bid = ticker['bid']
            ask = ticker['ask']
            volume = ticker['quoteVolume']
            
            # Calculate price change if we have previous data
            price_change = 0
            if previous_price:
                price_change = current_price - previous_price
                change_pct = (price_change / previous_price) * 100
            else:
                change_pct = 0
            
            # Display data
            print(f"📊 Poll #{poll_count} @ {timestamp}")
            print(f"   💰 BTC/USDC: ${current_price:,.2f}")
            print(f"   📈 Bid: ${bid:,.2f} | Ask: ${ask:,.2f}")
            print(f"   📊 Volume: ${volume:,.2f}")
            
            if previous_price:
                change_symbol = "📈" if price_change >= 0 else "📉"
                print(f"   {change_symbol} Change: ${price_change:+.2f} ({change_pct:+.3f}%)")
            
            print(f"   🕐 Exchange Time: {ticker['datetime']}")
            print("-" * 40)
            
            previous_price = current_price
            
            # Wait 5 seconds between polls
            if i < 9:  # Don't sleep on last iteration
                time.sleep(5)
                
    except Exception as e:
        print(f"❌ Error during data polling: {e}")
        return False
    
    print(f"✅ Live data polling test completed - {poll_count} successful polls")
    return True

def test_historical_data_fetch():
    """Test fetching historical OHLCV data"""
    print("\n🏛️ HISTORICAL DATA TEST")
    print("=" * 50)
    
    try:
        # Import fetch_ohlcv function
        from strategies.ma_crossover import fetch_ohlcv
        
        # Fetch 1-minute data
        df_1m = fetch_ohlcv(exchange, 'BTC/USDC', '1m', 10)
        print(f"📊 1-minute data: {len(df_1m)} candles")
        print(f"   Latest close: ${df_1m['close'].iloc[-1]:,.2f}")
        print(f"   Time range: {df_1m.index[0]} to {df_1m.index[-1]}")
        
        # Fetch 1-hour data
        df_1h = fetch_ohlcv(exchange, 'BTC/USDC', '1h', 50)
        print(f"📊 1-hour data: {len(df_1h)} candles")
        print(f"   Latest close: ${df_1h['close'].iloc[-1]:,.2f}")
        print(f"   Time range: {df_1h.index[0]} to {df_1h.index[-1]}")
        
        # Check if data is current (within last few minutes)
        latest_time = df_1m.index[-1]
        current_time = datetime.now()
        time_diff = (current_time - latest_time).total_seconds()
        
        if time_diff < 300:  # Within 5 minutes
            print(f"✅ Data is current (latest: {time_diff:.0f}s ago)")
        else:
            print(f"⚠️ Data may be stale (latest: {time_diff:.0f}s ago)")
            
        return True
        
    except Exception as e:
        print(f"❌ Error fetching historical data: {e}")
        return False

if __name__ == "__main__":
    print("🚀 BINANCE US LIVE DATA VERIFICATION")
    print("=" * 60)
    
    # Test 1: Live ticker polling
    live_test_success = test_live_data_polling()
    
    # Test 2: Historical data fetch
    historical_test_success = test_historical_data_fetch()
    
    # Summary
    print("\n📋 TEST SUMMARY")
    print("=" * 30)
    print(f"Live Data Polling: {'✅ PASS' if live_test_success else '❌ FAIL'}")
    print(f"Historical Data: {'✅ PASS' if historical_test_success else '❌ FAIL'}")
    
    if live_test_success and historical_test_success:
        print("\n🎉 ALL TESTS PASSED - Bot can access live Binance US data!")
    else:
        print("\n⚠️ Some tests failed - Check connection and API keys")
