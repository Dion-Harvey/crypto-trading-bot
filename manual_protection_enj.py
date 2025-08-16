#!/usr/bin/env python3
"""
🚨 EMERGENCY ENJ POSITION PROTECTION
Manual trailing stop for unprotected ENJ position
Position: 129.9 ENJ at $0.0973 entry price
"""

import ccxt
import json
import time
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

def place_manual_stop_loss():
    """
    Place manual stop-loss for the unprotected ENJ position
    Parameters per user specification:
    - Stop at 0.50% below current price
    """
    try:
        symbol = 'ENJ/USDT'
        amount = 129.9  # ENJ amount from failed trade
        entry_price = 0.0973  # Reported average price
        
        # Get current price
        ticker = exchange.fetch_ticker(symbol)
        current_price = ticker['last']
        
        # Calculate stop price (0.50% below current price per user specification)
        stop_price = current_price * 0.995  # 0.50% below current
        
        print(f"🎯 ENJ POSITION PROTECTION")
        print(f"   Position: {amount} ENJ")
        print(f"   Entry Price: ${entry_price:.4f}")
        print(f"   Current Price: ${current_price:.4f}")
        print(f"   Stop Price: ${stop_price:.4f} (0.50% below current)")
        
        # Try to place stop-market order (simplest protection)
        try:
            order = exchange.create_order(
                symbol,
                'stop_market',
                'sell',
                amount,
                None,  # Market order - no limit price
                {
                    'stopPrice': str(stop_price),
                    'timeInForce': 'GTC'
                }
            )
            
            if order and order.get('id'):
                print(f"✅ STOP-LOSS PROTECTION ACTIVE!")
                print(f"   Order ID: {order['id']}")
                print(f"   Will sell {amount} ENJ if price drops to ${stop_price:.4f}")
                
                # Log the success
                with open('manual_protection_log.txt', 'a') as f:
                    f.write(f"[{datetime.now()}] ✅ Manual stop-loss placed for ENJ\n")
                    f.write(f"   Order ID: {order['id']}\n")
                    f.write(f"   Amount: {amount} ENJ\n")
                    f.write(f"   Stop Price: ${stop_price:.4f}\n")
                    f.write(f"   Current Price: ${current_price:.4f}\n\n")
                
                return order
        
        except Exception as e:
            print(f"❌ Stop-market order failed: {e}")
            
            # Fallback: Try stop-limit order
            limit_price = stop_price * 0.995  # 0.5% below stop price
            try:
                order = exchange.create_order(
                    symbol,
                    'stop_loss_limit',
                    'sell',
                    amount,
                    limit_price,
                    {
                        'stopPrice': str(stop_price),
                        'timeInForce': 'GTC'
                    }
                )
                
                if order and order.get('id'):
                    print(f"✅ STOP-LIMIT PROTECTION ACTIVE!")
                    print(f"   Order ID: {order['id']}")
                    print(f"   Stop Price: ${stop_price:.4f}")
                    print(f"   Limit Price: ${limit_price:.4f}")
                    return order
                    
            except Exception as e2:
                print(f"❌ Stop-limit order also failed: {e2}")
                print("🚨 MANUAL MONITORING REQUIRED - Set manual alerts!")
                return None
    
    except Exception as e:
        print(f"❌ Failed to protect ENJ position: {e}")
        return None

def monitor_enj_position():
    """
    Monitor ENJ position and provide manual trailing stop updates
    """
    symbol = 'ENJ/USDT'
    entry_price = 0.0973
    highest_price = entry_price
    
    print(f"🔍 MONITORING ENJ POSITION...")
    print(f"   Entry: ${entry_price:.4f}")
    print("   Press Ctrl+C to stop monitoring")
    
    try:
        while True:
            ticker = exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            
            # Track highest price for trailing calculation
            if current_price > highest_price:
                highest_price = current_price
            
            # Calculate trailing stop (0.50% below highest price achieved)
            trailing_stop_price = highest_price * 0.995
            
            # Calculate profit/loss
            pnl_pct = ((current_price - entry_price) / entry_price) * 100
            
            print(f"\r🎯 ENJ: ${current_price:.4f} | High: ${highest_price:.4f} | Trail: ${trailing_stop_price:.4f} | P&L: {pnl_pct:+.2f}%", end="")
            
            # Alert if approaching trail stop
            if current_price <= trailing_stop_price and current_price > entry_price:
                print(f"\n🚨 APPROACHING TRAILING STOP! Current: ${current_price:.4f} vs Trail: ${trailing_stop_price:.4f}")
            
            time.sleep(10)  # Update every 10 seconds
            
    except KeyboardInterrupt:
        print(f"\n👋 Monitoring stopped. Final price: ${current_price:.4f}")

if __name__ == "__main__":
    print("🚨 ENJ POSITION EMERGENCY PROTECTION")
    print("=" * 50)
    
    # Try to place automatic stop-loss first
    protection_order = place_manual_stop_loss()
    
    if protection_order:
        print("\n✅ Automatic protection active!")
        print("   Your ENJ position now has stop-loss protection.")
    else:
        print("\n🚨 AUTOMATIC PROTECTION FAILED")
        print("   Starting manual monitoring mode...")
        monitor_enj_position()
