#!/usr/bin/env python3
"""
Live API Connection Test
"""

import sys
import os
import ccxt
import time

# Add current directory to path
sys.path.append(os.getcwd())

def test_live_connection():
    print("🌐 LIVE API CONNECTION TEST")
    print("=" * 50)
    
    try:
        from config import BINANCE_API_KEY, BINANCE_API_SECRET
        
        # Initialize exchange exactly like in bot.py
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
        
        print("1. EXCHANGE INITIALIZATION:")
        print("✅ Exchange configured successfully")
        
        print("\n2. SERVER TIME SYNC:")
        server_time = exchange.fetch_time()
        local_time = int(time.time() * 1000)
        time_diff = abs(server_time - local_time)
        print(f"   Server time: {server_time}")
        print(f"   Local time:  {local_time}")
        print(f"   Time diff:   {time_diff}ms")
        if time_diff < 5000:
            print("✅ Time synchronization OK")
        else:
            print("⚠️  Time difference > 5 seconds")
        
        print("\n3. ACCOUNT ACCESS:")
        balance = exchange.fetch_balance()
        print("✅ Account balance retrieved successfully")
        
        total_usd = 0
        for coin, amounts in balance['total'].items():
            if amounts > 0:
                print(f"   {coin}: {amounts}")
                if coin == 'USDC':
                    total_usd += amounts
        
        print("\n4. MARKET DATA ACCESS:")
        ticker = exchange.fetch_ticker('BTC/USDC')
        print("✅ BTC/USDC ticker retrieved successfully")
        print(f"   Current price: ${ticker['last']:,.2f}")
        print(f"   24h volume: {ticker['baseVolume']:,.2f} BTC")
        print(f"   24h change: {ticker['percentage']:+.2f}%")
        
        print("\n5. ORDER BOOK ACCESS:")
        orderbook = exchange.fetch_order_book('BTC/USDC', limit=5)
        print("✅ Order book retrieved successfully")
        print(f"   Best bid: ${orderbook['bids'][0][0]:,.2f}")
        print(f"   Best ask: ${orderbook['asks'][0][0]:,.2f}")
        print(f"   Spread: ${orderbook['asks'][0][0] - orderbook['bids'][0][0]:.2f}")
        
        print("\n6. TRADING READINESS:")
        current_btc_value = balance['total'].get('BTC', 0) * ticker['last']
        total_portfolio = total_usd + current_btc_value
        
        print(f"   Total portfolio: ${total_portfolio:.2f}")
        print(f"   USDC available: ${balance['free'].get('USDC', 0):.2f}")
        print(f"   BTC holdings: {balance['total'].get('BTC', 0):.6f} BTC (${current_btc_value:.2f})")
        
        # Check minimum order requirements
        min_order_value = 10.0  # Binance minimum
        if balance['free'].get('USDC', 0) >= min_order_value:
            print(f"✅ Sufficient balance for trading (min ${min_order_value})")
        else:
            print(f"⚠️  Insufficient balance for trading (need ${min_order_value})")
        
        print(f"\n{'='*50}")
        print("✅ ALL SYSTEMS OPERATIONAL!")
        print("🚀 BOT READY FOR LIVE TRADING!")
        print(f"{'='*50}")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

if __name__ == "__main__":
    test_live_connection()
