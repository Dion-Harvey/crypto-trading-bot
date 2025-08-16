#!/usr/bin/env python3
"""
🔍 ENJ POSITION CHECK & PROTECTION
Check actual ENJ balance and place protection if needed
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

def check_enj_position():
    """Check actual ENJ balance and recent trades"""
    try:
        print("🔍 CHECKING ENJ POSITION...")
        
        # Get account balance
        balance = exchange.fetch_balance()
        enj_balance = balance.get('ENJ', {})
        
        print(f"💰 ENJ Balance:")
        print(f"   Free: {enj_balance.get('free', 0)} ENJ")
        print(f"   Used: {enj_balance.get('used', 0)} ENJ") 
        print(f"   Total: {enj_balance.get('total', 0)} ENJ")
        
        # Get current ENJ price
        ticker = exchange.fetch_ticker('ENJ/USDT')
        current_price = ticker['last']
        print(f"📈 Current ENJ Price: ${current_price:.4f}")
        
        # Check for open orders
        try:
            open_orders = exchange.fetch_open_orders('ENJ/USDT')
            print(f"📋 Open ENJ Orders: {len(open_orders)}")
            for order in open_orders:
                print(f"   Order ID: {order['id']}")
                print(f"   Type: {order['type']}")
                print(f"   Side: {order['side']}")
                print(f"   Amount: {order['amount']}")
                print(f"   Price: {order.get('price', 'Market')}")
        except Exception as e:
            print(f"⚠️ Could not fetch open orders: {e}")
        
        return enj_balance.get('total', 0), current_price
        
    except Exception as e:
        print(f"❌ Error checking position: {e}")
        return 0, 0

def place_stop_protection(amount, current_price):
    """Place stop-loss protection for ENJ position"""
    if amount <= 0:
        print("❌ No ENJ position to protect")
        return False
    
    try:
        # Calculate stop price (0.50% below current per user specification)
        stop_price = current_price * 0.995
        
        print(f"\n🛡️ PLACING STOP-LOSS PROTECTION:")
        print(f"   Amount: {amount:.6f} ENJ")
        print(f"   Current Price: ${current_price:.4f}")
        print(f"   Stop Price: ${stop_price:.4f} (0.50% below)")
        
        # Try stop-market order (preferred for Binance US)
        order = exchange.create_order(
            'ENJ/USDT',
            'stop_market',
            'sell',
            amount,
            None,
            {
                'stopPrice': str(stop_price),
                'timeInForce': 'GTC'
            }
        )
        
        if order and order.get('id'):
            print(f"✅ STOP-LOSS PLACED SUCCESSFULLY!")
            print(f"   Order ID: {order['id']}")
            print(f"   Protection: Will sell if ENJ drops to ${stop_price:.4f}")
            
            # Log success
            with open('protection_log.txt', 'a') as f:
                f.write(f"[{datetime.now()}] ✅ Stop-loss placed for {amount:.6f} ENJ\n")
                f.write(f"   Order ID: {order['id']}, Stop: ${stop_price:.4f}\n\n")
            
            return True
        else:
            print("❌ Stop-loss order failed - no order ID returned")
            return False
            
    except Exception as e:
        print(f"❌ Failed to place stop-loss: {e}")
        print("🚨 MANUAL MONITORING REQUIRED!")
        return False

if __name__ == "__main__":
    print("🚨 ENJ POSITION PROTECTION SCRIPT")
    print("=" * 40)
    
    # Check current position
    enj_amount, current_price = check_enj_position()
    
    if enj_amount > 0:
        print(f"\n✅ ENJ Position Found: {enj_amount:.6f} ENJ")
        value_usd = enj_amount * current_price
        print(f"💰 Current Value: ${value_usd:.2f}")
        
        # Place protection
        success = place_stop_protection(enj_amount, current_price)
        
        if success:
            print("\n🎉 ENJ POSITION IS NOW PROTECTED!")
        else:
            print("\n🚨 PROTECTION FAILED - SET MANUAL ALERTS!")
    else:
        print("\n❌ No ENJ position found to protect")
