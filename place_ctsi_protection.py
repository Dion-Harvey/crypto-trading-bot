#!/usr/bin/env python3
"""
Place CTSI stop-limit protection (CTSI/USDT doesn't support trailing stops)
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
        'timeout': 30000,
        'options': {
            'warnOnFetchOpenOrdersWithoutSymbol': False
        }
    })
    
    # Check CTSI balance
    balance = exchange.fetch_balance()
    ctsi_balance = balance.get('CTSI', {}).get('free', 0)
    
    if ctsi_balance <= 0:
        print("No CTSI position to protect")
        exit(0)
    
    # Get current CTSI price
    symbol = 'CTSI/USDT'
    ticker = exchange.fetch_ticker(symbol)
    current_price = ticker['last']
    position_value = ctsi_balance * current_price
    
    print(f"CTSI Position: {ctsi_balance} tokens")
    print(f"Current Price: ${current_price:.4f}")
    print(f"Position Value: ${position_value:.2f}")
    
    # Check for existing orders
    ctsi_orders = exchange.fetch_open_orders(symbol)
    print(f"Current CTSI orders: {len(ctsi_orders)}")
    
    if len(ctsi_orders) == 0:
        print("\n🛡️ PLACING STOP-LIMIT PROTECTION (2% stop loss)")
        
        # Calculate stop-limit prices
        stop_loss_pct = 0.02  # 2% stop loss
        stop_price = current_price * (1 - stop_loss_pct)
        limit_price = stop_price * 0.998  # Slightly below stop for quick execution
        
        try:
            stop_limit_order = exchange.create_order(
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
            
            if stop_limit_order:
                print(f"✅ STOP-LIMIT PROTECTION PLACED!")
                print(f"   Order ID: {stop_limit_order['id']}")
                print(f"   Stop Price: ${stop_price:.4f} (-{stop_loss_pct*100:.1f}%)")
                print(f"   Limit Price: ${limit_price:.4f}")
                print(f"   Amount: {ctsi_balance} CTSI")
                print(f"   Protection Level: ${position_value * (1-stop_loss_pct):.2f}")
                
                # Save to tracking file
                with open('ctsi_protection.txt', 'w') as f:
                    f.write(f"CTSI Stop-Limit Protection Active\n")
                    f.write(f"Order ID: {stop_limit_order['id']}\n")
                    f.write(f"Amount: {ctsi_balance} CTSI\n")
                    f.write(f"Stop Price: ${stop_price:.4f}\n")
                    f.write(f"Limit Price: ${limit_price:.4f}\n")
                    f.write(f"Position Value: ${position_value:.2f}\n")
            
        except Exception as e:
            print(f"❌ Stop-limit failed: {e}")
            print("🚨 POSITION REMAINS UNPROTECTED!")
    else:
        print("✅ Protection already exists")
        for order in ctsi_orders:
            print(f"  Order {order['id']}: {order['type']} {order['side']} {order['amount']}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
