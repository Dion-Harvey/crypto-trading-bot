#!/usr/bin/env python3
"""
🛡️ IMMEDIATE POSITION PROTECTION
Place stop-loss orders for current ENJ and EGLD positions using correct Binance US order types
"""

import ccxt
import json
from datetime import datetime

# Load configuration
with open('enhanced_config.json', 'r') as f:
    config = json.load(f)

# Initialize exchange
exchange = ccxt.binanceus({
    'apiKey': config['api_keys']['binance']['api_key'],
    'secret': config['api_keys']['binance']['api_secret'],
    'sandbox': False,
    'enableRateLimit': True,
})

def place_stop_loss_protection(symbol, amount, current_price):
    """
    Place stop-loss protection using Binance US compatible order types
    Tries multiple strategies in order of preference
    """
    # Calculate stop price (0.50% below current per user specification)
    stop_price = current_price * 0.995
    limit_price = stop_price * 0.995  # Limit price slightly below stop
    
    print(f"\n🛡️ PROTECTING {symbol}:")
    print(f"   Amount: {amount:.6f}")
    print(f"   Current: ${current_price:.4f}")
    print(f"   Stop: ${stop_price:.4f} (0.50% below)")
    
    # Strategy 1: Try TRAILING_STOP_MARKET with correct parameters
    try:
        print(f"   🔄 Trying TRAILING_STOP_MARKET with stopLoss parameter...")
        order = exchange.create_order(
            symbol,
            'TRAILING_STOP_MARKET',
            'sell',
            amount,
            None,
            {
                'callbackRate': '0.5',  # 0.50% trailing
                'timeInForce': 'GTC',
                'stopLossOrTakeProfit': 'stopLoss'  # Required for Binance US
            }
        )
        if order and order.get('id'):
            print(f"   ✅ TRAILING STOP PLACED: {order['id']}")
            return order
    except Exception as e:
        print(f"   ❌ TRAILING_STOP_MARKET failed: {e}")
    
    # Strategy 2: Try STOP_LOSS_LIMIT
    try:
        print(f"   🔄 Trying STOP_LOSS_LIMIT...")
        order = exchange.create_order(
            symbol,
            'STOP_LOSS_LIMIT',
            'sell',
            amount,
            limit_price,
            {
                'stopPrice': str(stop_price),
                'timeInForce': 'GTC'
            }
        )
        if order and order.get('id'):
            print(f"   ✅ STOP_LOSS_LIMIT PLACED: {order['id']}")
            return order
    except Exception as e:
        print(f"   ❌ STOP_LOSS_LIMIT failed: {e}")
    
    # Strategy 3: Try basic STOP_LOSS
    try:
        print(f"   🔄 Trying basic STOP_LOSS...")
        order = exchange.create_order(
            symbol,
            'STOP_LOSS',
            'sell',
            amount,
            None,
            {
                'stopPrice': str(stop_price),
                'timeInForce': 'GTC'
            }
        )
        if order and order.get('id'):
            print(f"   ✅ STOP_LOSS PLACED: {order['id']}")
            return order
    except Exception as e:
        print(f"   ❌ STOP_LOSS failed: {e}")
    
    print(f"   ❌ ALL STOP ORDER TYPES FAILED")
    return None

def protect_current_positions():
    """Find and protect current crypto positions"""
    try:
        # Get current balance
        balance = exchange.fetch_balance()
        
        positions = [
            {'symbol': 'ENJ/USDT', 'amount': balance.get('ENJ', {}).get('free', 0)},
            {'symbol': 'EGLD/USDT', 'amount': balance.get('EGLD', {}).get('free', 0)}
        ]
        
        protected_count = 0
        
        for pos in positions:
            if pos['amount'] > 0:
                print(f"\n📊 Found position: {pos['amount']:.6f} {pos['symbol'].split('/')[0]}")
                
                # Get current price
                ticker = exchange.fetch_ticker(pos['symbol'])
                current_price = ticker['last']
                
                # Place protection
                order = place_stop_loss_protection(pos['symbol'], pos['amount'], current_price)
                
                if order:
                    protected_count += 1
                    # Log success
                    with open('protection_success_log.txt', 'a') as f:
                        f.write(f"[{datetime.now()}] ✅ {pos['symbol']} protected\n")
                        f.write(f"   Order ID: {order['id']}\n")
                        f.write(f"   Amount: {pos['amount']:.6f}\n")
                        f.write(f"   Protection: 0.50% stop-loss\n\n")
        
        print(f"\n🎯 PROTECTION SUMMARY:")
        print(f"   Protected: {protected_count} positions")
        print(f"   Failed: {len([p for p in positions if p['amount'] > 0]) - protected_count} positions")
        
        if protected_count > 0:
            print(f"\n✅ SUCCESS: Your positions now have stop-loss protection!")
        else:
            print(f"\n❌ FAILED: Could not place any stop-loss orders")
            print(f"   Manual monitoring still required")
        
    except Exception as e:
        print(f"❌ Error protecting positions: {e}")

if __name__ == "__main__":
    print("🛡️ IMMEDIATE POSITION PROTECTION SCRIPT")
    print("=" * 50)
    print("Attempting to place stop-loss orders for ENJ and EGLD positions...")
    
    protect_current_positions()
