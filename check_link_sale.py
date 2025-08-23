#!/usr/bin/env python3

import ccxt
import json
import time
from datetime import datetime, timedelta

def load_config():
    """Load trading configuration"""
    try:
        with open('enhanced_config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ enhanced_config.json not found")
        return None

def check_link_sale():
    """Check current LINK balance and recent trading history"""
    
    print("🔍 LINK SALE INVESTIGATION")
    print("=" * 50)
    
    config = load_config()
    if not config:
        return
    
    # Initialize exchange
    try:
        exchange_config = config['exchange']
        exchange = ccxt.binanceus({
            'apiKey': exchange_config['api_key'],
            'secret': exchange_config['secret'],
            'sandbox': exchange_config.get('testnet', False),
            'enableRateLimit': True,
            'options': {'defaultType': 'spot'}
        })
        
        print("✅ Exchange connection established")
        
    except Exception as e:
        print(f"❌ Exchange connection failed: {e}")
        return
    
    # Check current balance
    print("\n📊 CURRENT BALANCE STATUS:")
    try:
        balance = exchange.fetch_balance()
        link_free = balance['LINK']['free']
        link_used = balance['LINK']['used']
        link_total = balance['LINK']['total']
        
        print(f"   💰 LINK Free Balance: {link_free:.8f}")
        print(f"   🔒 LINK Used Balance: {link_used:.8f}")
        print(f"   📈 LINK Total Balance: {link_total:.8f}")
        
        # Get current LINK price
        ticker = exchange.fetch_ticker('LINK/USDT')
        current_price = ticker['last']
        link_value = link_total * current_price
        
        print(f"   💵 Current LINK Price: ${current_price:.4f}")
        print(f"   💰 Total LINK Value: ${link_value:.2f}")
        
        # Determine status
        if link_total <= 0.001:
            print("   ✅ STATUS: LINK position appears to be SOLD/CLOSED")
        elif link_total >= 0.01:
            print(f"   ⚠️ STATUS: Significant LINK position still exists (${link_value:.2f})")
        else:
            print(f"   💨 STATUS: Small LINK dust remaining ({link_total:.8f} LINK)")
            
    except Exception as e:
        print(f"   ❌ Balance check failed: {e}")
    
    # Check recent trading history
    print("\n📈 RECENT LINK/USDT TRADING HISTORY:")
    try:
        # Get trades from last 24 hours
        since = int((datetime.now() - timedelta(hours=24)).timestamp() * 1000)
        trades = exchange.fetch_my_trades('LINK/USDT', since=since, limit=20)
        
        if not trades:
            print("   📭 No LINK/USDT trades in last 24 hours")
        else:
            print(f"   📊 Found {len(trades)} trades in last 24 hours:")
            
            total_bought = 0
            total_sold = 0
            
            for trade in reversed(trades[-10:]):  # Show last 10 trades
                timestamp = datetime.fromtimestamp(trade['timestamp'] / 1000)
                side = trade['side'].upper()
                amount = trade['amount']
                price = trade['price']
                cost = trade['cost']
                
                if side == 'BUY':
                    total_bought += amount
                    print(f"   🟢 {timestamp.strftime('%H:%M:%S')} BUY  {amount:.6f} LINK @ ${price:.4f} = ${cost:.2f}")
                else:
                    total_sold += amount  
                    print(f"   🔴 {timestamp.strftime('%H:%M:%S')} SELL {amount:.6f} LINK @ ${price:.4f} = ${cost:.2f}")
            
            print(f"\n   📊 24h Summary:")
            print(f"   🟢 Total Bought: {total_bought:.6f} LINK")
            print(f"   🔴 Total Sold: {total_sold:.6f} LINK")
            print(f"   📈 Net Position: {total_bought - total_sold:+.6f} LINK")
            
    except Exception as e:
        print(f"   ❌ Trade history check failed: {e}")
    
    # Check open orders
    print("\n📋 OPEN ORDERS:")
    try:
        open_orders = exchange.fetch_open_orders('LINK/USDT')
        
        if not open_orders:
            print("   📭 No open LINK/USDT orders")
        else:
            print(f"   📊 Found {len(open_orders)} open orders:")
            for order in open_orders:
                side = order['side'].upper()
                amount = order['amount']
                price = order['price']
                order_type = order['type'].upper()
                status = order['status'].upper()
                
                print(f"   🔸 {side} {amount:.6f} LINK @ ${price:.4f} ({order_type}, {status})")
                
    except Exception as e:
        print(f"   ❌ Open orders check failed: {e}")
    
    print("\n" + "=" * 50)
    print("🔍 LINK INVESTIGATION COMPLETE")

if __name__ == "__main__":
    check_link_sale()
