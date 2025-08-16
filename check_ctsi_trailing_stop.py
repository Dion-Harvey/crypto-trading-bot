#!/usr/bin/env python3
"""
Check CTSI/USDT orders specifically and place trailing stop if needed
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
            'warnOnFetchOpenOrdersWithoutSymbol': False  # Disable warning
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
    
    # Check for existing CTSI orders
    try:
        ctsi_orders = exchange.fetch_open_orders(symbol)
        print(f"\nCTSI/USDT Open Orders: {len(ctsi_orders)}")
        
        has_trailing_stop = False
        has_stop_order = False
        
        for order in ctsi_orders:
            print(f"  Order {order['id']}: {order['type']} {order['side']} {order['amount']} @ {order.get('stopPrice', 'N/A')}")
            if 'TRAILING' in order['type'].upper():
                has_trailing_stop = True
            elif 'STOP' in order['type'].upper():
                has_stop_order = True
        
        if not has_trailing_stop and not has_stop_order:
            print("\n🚨 NO PROTECTION FOUND - PLACING TRAILING STOP!")
            
            # Place trailing stop order
            try:
                trailing_stop_order = exchange.create_order(
                    symbol,
                    'TRAILING_STOP_MARKET',
                    'sell',
                    ctsi_balance,
                    None,
                    {
                        'callbackRate': '2.0',  # 2% trailing distance
                        'timeInForce': 'GTC'
                    }
                )
                
                if trailing_stop_order:
                    print(f"✅ TRAILING STOP PLACED!")
                    print(f"   Order ID: {trailing_stop_order['id']}")
                    print(f"   Callback Rate: 2.0%")
                    print(f"   Amount: {ctsi_balance} CTSI")
                    print(f"   Current Price: ${current_price:.4f}")
                    
            except Exception as trailing_error:
                print(f"❌ Trailing stop failed: {trailing_error}")
                
                # Fallback to regular stop-market
                try:
                    stop_price = current_price * 0.98  # 2% below current
                    stop_order = exchange.create_order(
                        symbol,
                        'STOP_MARKET',
                        'sell',
                        ctsi_balance,
                        None,
                        {
                            'stopPrice': str(stop_price),
                            'timeInForce': 'GTC'
                        }
                    )
                    
                    if stop_order:
                        print(f"✅ STOP-MARKET FALLBACK PLACED!")
                        print(f"   Order ID: {stop_order['id']}")
                        print(f"   Stop Price: ${stop_price:.4f} (-2.0%)")
                        
                except Exception as stop_error:
                    print(f"❌ Stop-market fallback failed: {stop_error}")
                    print("🚨 POSITION REMAINS UNPROTECTED!")
        
        elif has_trailing_stop:
            print("✅ Trailing stop protection already active")
        elif has_stop_order:
            print("✅ Stop order protection already active")
            
    except Exception as e:
        print(f"Error checking CTSI orders: {e}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
