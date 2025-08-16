#!/usr/bin/env python3
"""
Quick CTSI balance checker for AWS deployment
"""
import sys
sys.path.append(".")

try:
    from config import BINANCE_API_KEY, BINANCE_API_SECRET
    import ccxt
    
    # Initialize exchange
    exchange = ccxt.binanceus({
        'apiKey': BINANCE_API_KEY,
        'secret': BINANCE_API_SECRET,
        'enableRateLimit': True,
        'timeout': 30000
    })
    
    # Fetch balance
    balance = exchange.fetch_balance()
    
    # Check CTSI specifically
    ctsi_balance = balance.get('CTSI', {}).get('free', 0)
    print(f"CTSI Balance: {ctsi_balance}")
    
    # Show all non-zero balances
    print("\nAll non-zero balances:")
    for symbol, data in balance.items():
        if isinstance(data, dict) and data.get('free', 0) > 0:
            print(f"  {symbol}: {data['free']}")
    
    # Check for open orders
    try:
        open_orders = exchange.fetch_open_orders()
        if open_orders:
            print(f"\nOpen orders: {len(open_orders)}")
            for order in open_orders:
                print(f"  {order['symbol']}: {order['side']} {order['amount']} @ {order['price']}")
        else:
            print("\nNo open orders")
    except Exception as e:
        print(f"Error checking open orders: {e}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
