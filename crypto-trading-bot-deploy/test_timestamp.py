#!/usr/bin/env python3
"""
Test timestamp synchronization with Binance
"""

import ccxt
import time
from config import BINANCE_API_KEY, BINANCE_API_SECRET

def test_timestamps():
    """Test various timestamp strategies"""
    
    print("🔍 TIMESTAMP DIAGNOSTIC TEST")
    print("="*50)
    
    # Test 1: Raw local time
    local_time = int(time.time() * 1000)
    print(f"Local time: {local_time}")
    
    # Test 2: Try different offset strategies
    offsets_to_test = [0, -1000, -2000, -3000, -4000, -5000, -6000, 1000, 2000]
    
    for offset in offsets_to_test:
        print(f"\n🧪 Testing offset: {offset}ms")
        
        try:
            # Create exchange with specific offset
            test_exchange = ccxt.binanceus({
                'apiKey': BINANCE_API_KEY,
                'secret': BINANCE_API_SECRET,
                'enableRateLimit': True,
                'timeout': 10000,
                'options': {'timeDifference': offset}
            })
            
            # Try a simple API call
            balance = test_exchange.fetch_balance()
            print(f"✅ SUCCESS with offset {offset}ms")
            print(f"   Account USDT: ${balance['USDT']['free']:.2f}")
            print(f"   Account BTC: {balance['BTC']['free']:.6f}")
            break
            
        except Exception as e:
            error_str = str(e)
            if 'timestamp' in error_str.lower() and '-1021' in error_str:
                print(f"❌ TIMESTAMP ERROR with offset {offset}ms: {e}")
            else:
                print(f"⚠️ OTHER ERROR with offset {offset}ms: {e}")
                # If it's not a timestamp error, this offset might actually work
                if 'Invalid API-key' not in error_str:
                    print(f"   -> This might work for trading (non-timestamp error)")
                    break

if __name__ == "__main__":
    test_timestamps()
