#!/usr/bin/env python3
"""
Simple Bot Test - Check if key functions work
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from bot import test_connection, calculate_position_size, safe_api_call
import ccxt
from config import BINANCE_API_KEY, BINANCE_API_SECRET

def quick_bot_test():
    """Test basic bot functionality"""
    print("🧪 QUICK BOT FUNCTIONALITY TEST")
    print("=" * 50)
    
    try:
        # Test 1: Exchange connection
        print("\n1️⃣ Testing exchange connection...")
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
        
        balance = safe_api_call(exchange.fetch_balance)
        ticker = safe_api_call(exchange.fetch_ticker, 'BTC/USDC')
        
        print(f"   ✅ Balance fetched: {balance['USDC']['free']:.2f} USDC")
        print(f"   ✅ Price fetched: ${ticker['last']:.2f}")
        
        # Test 2: Position sizing calculation
        print("\n2️⃣ Testing position sizing...")
        total_portfolio = balance['total']['USDC'] + (balance['total']['BTC'] * ticker['last'])
        position_size = calculate_position_size(
            current_price=ticker['last'],
            volatility=0.02,
            signal_confidence=0.7,
            total_portfolio_value=total_portfolio
        )
        print(f"   ✅ Position size calculated: ${position_size:.2f}")
        
        # Test 3: Bot connection test
        print("\n3️⃣ Testing bot connection function...")
        test_connection()
        
        print("\n✅ ALL TESTS PASSED!")
        print("🤖 Bot core functionality is working correctly")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    quick_bot_test()
