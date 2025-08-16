#!/usr/bin/env python3
"""
Emergency CTSI Protection Script
Places immediate stop-loss protection for unprotected CTSI position
"""
import sys
sys.path.append(".")

try:
    from config import BINANCE_API_KEY, BINANCE_API_SECRET
    import ccxt
    import time
    
    # Initialize exchange
    exchange = ccxt.binanceus({
        'apiKey': BINANCE_API_KEY,
        'secret': BINANCE_API_SECRET,
        'enableRateLimit': True,
        'timeout': 30000
    })
    
    # Get current CTSI balance and price
    balance = exchange.fetch_balance()
    ctsi_balance = balance.get('CTSI', {}).get('free', 0)
    
    if ctsi_balance <= 0:
        print("No CTSI balance to protect")
        exit(0)
    
    print(f"Found CTSI balance: {ctsi_balance}")
    
    # Get current CTSI/USDT price
    symbol = 'CTSI/USDT'
    ticker = exchange.fetch_ticker(symbol)
    current_price = ticker['last']
    position_value = ctsi_balance * current_price
    
    print(f"Current CTSI price: ${current_price:.4f}")
    print(f"Position value: ${position_value:.2f}")
    
    # Calculate stop-loss at 2% below current price for immediate protection
    stop_loss_pct = 0.02  # 2% stop loss
    stop_price = current_price * (1 - stop_loss_pct)
    
    print(f"Setting stop-loss at: ${stop_price:.4f} (-{stop_loss_pct*100:.1f}%)")
    
    # Place stop-market order for immediate protection
    try:
        print("Placing emergency stop-loss order...")
        order = exchange.create_order(
            symbol,
            'STOP_MARKET',
            'sell',
            ctsi_balance,
            None,  # No price for stop market
            {
                'stopPrice': str(stop_price),
                'timeInForce': 'GTC'
            }
        )
        
        if order and order.get('id'):
            print(f"✅ EMERGENCY STOP-LOSS PLACED!")
            print(f"   Order ID: {order['id']}")
            print(f"   Amount: {ctsi_balance} CTSI")
            print(f"   Stop Price: ${stop_price:.4f}")
            print(f"   Position protected against losses > 2%")
            
            # Save order info to a file for tracking
            with open('emergency_protection.txt', 'w') as f:
                f.write(f"Emergency CTSI protection placed\n")
                f.write(f"Order ID: {order['id']}\n")
                f.write(f"Symbol: {symbol}\n")
                f.write(f"Amount: {ctsi_balance}\n")
                f.write(f"Stop Price: ${stop_price:.4f}\n")
                f.write(f"Timestamp: {time.time()}\n")
            
        else:
            print("❌ Stop-loss order failed")
            
    except Exception as e:
        print(f"❌ Error placing stop-loss: {e}")
        
        # Try alternative protection method
        try:
            print("Trying stop-limit as fallback...")
            limit_price = stop_price * 0.998  # Slightly below stop
            
            order = exchange.create_order(
                symbol,
                'stop_loss_limit',
                'sell',
                ctsi_balance,
                limit_price,
                {
                    'stopPrice': str(stop_price),
                    'timeInForce': 'GTC'
                }
            )
            
            if order:
                print(f"✅ FALLBACK STOP-LIMIT PLACED!")
                print(f"   Order ID: {order['id']}")
                print(f"   Stop: ${stop_price:.4f}, Limit: ${limit_price:.4f}")
            
        except Exception as e2:
            print(f"❌ Fallback also failed: {e2}")
            print("🚨 MANUAL INTERVENTION REQUIRED - POSITION REMAINS UNPROTECTED")

except Exception as e:
    print(f"❌ Critical error: {e}")
    import traceback
    traceback.print_exc()
