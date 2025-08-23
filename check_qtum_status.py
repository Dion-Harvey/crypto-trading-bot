#!/usr/bin/env python3

"""
Quick script to check current QTUM position and orders
"""

import ccxt
import json
import time
from config import load_config

def check_qtum_status():
    """Check current QTUM position and any existing orders"""
    
    print("🔍 QTUM Position Status Check")
    print("=" * 30)
    
    try:
        # Load configuration
        config = load_config()
        
        # Initialize exchange
        exchange = ccxt.binanceus({
            'apiKey': config['api_key'],
            'secret': config['api_secret'],
            'sandbox': config.get('sandbox', False),
            'enableRateLimit': True,
        })
        
        symbol = 'QTUM/USDT'
        
        # Check balance
        print(f"💰 Current Balance:")
        balance = exchange.fetch_balance()
        qtum_balance = balance.get('QTUM', {}).get('free', 0)
        qtum_total = balance.get('QTUM', {}).get('total', 0)
        usdt_balance = balance.get('USDT', {}).get('free', 0)
        
        print(f"   QTUM Free: {qtum_balance:.8f}")
        print(f"   QTUM Total: {qtum_total:.8f}")
        print(f"   USDT Free: ${usdt_balance:.2f}")
        
        # Get current price
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        position_value = qtum_balance * current_price
        
        print(f"\n📊 Current Market:")
        print(f"   QTUM Price: ${current_price:.4f}")
        print(f"   Position Value: ${position_value:.2f}")
        
        # Check open orders
        print(f"\n📋 Open Orders for {symbol}:")
        try:
            open_orders = exchange.fetch_open_orders(symbol)
            
            if open_orders:
                for order in open_orders:
                    print(f"   🆔 {order['id']}: {order['type']} {order['side']} {order['amount']:.8f} QTUM")
                    if 'stopPrice' in order.get('info', {}):
                        print(f"      Stop Price: ${float(order['info']['stopPrice']):.4f}")
                    if order.get('price'):
                        print(f"      Limit Price: ${order['price']:.4f}")
                    print(f"      Status: {order['status']}")
                    print(f"      Created: {order['datetime']}")
                    print()
            else:
                print(f"   ❌ No open orders found for {symbol}")
                if qtum_balance > 0.0001:
                    print(f"   🚨 WARNING: You have QTUM but NO STOP-LOSS PROTECTION!")
                    print(f"   💡 Run emergency_qtum_stop_loss.py to protect your position")
        
        except Exception as e:
            print(f"   ❌ Error fetching open orders: {e}")
        
        # Position summary
        print(f"\n📊 Position Summary:")
        if qtum_balance > 0.0001:
            print(f"   ✅ Active QTUM Position: {qtum_balance:.8f} QTUM (${position_value:.2f})")
            
            # Check if protected
            if open_orders:
                stop_orders = [o for o in open_orders if 'stop' in o['type'].lower()]
                if stop_orders:
                    print(f"   🛡️ PROTECTED: {len(stop_orders)} stop-loss order(s) active")
                else:
                    print(f"   🚨 UNPROTECTED: No stop-loss orders found!")
            else:
                print(f"   🚨 UNPROTECTED: No stop-loss orders found!")
        else:
            print(f"   ❌ No active QTUM position")
            
    except Exception as e:
        print(f"❌ Status check failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_qtum_status()
