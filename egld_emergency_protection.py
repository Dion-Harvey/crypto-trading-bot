#!/usr/bin/env python3
"""
🚨 IMMEDIATE EGLD PROTECTION
Uses bot's existing infrastructure to protect EGLD position
"""

def protect_egld_position():
    """Protect existing EGLD position with stop-loss order"""
    import sys
    import os
    from datetime import datetime
    
    try:
        print("🚨 EGLD PROTECTION INITIALIZING...")
        
        # Import bot's existing modules
        sys.path.append(os.getcwd())
        
        # Try to import the config and client setup
        from config import load_api_credentials
        
        api_key, api_secret = load_api_credentials()
        if not api_key or not api_secret:
            print("❌ API credentials not loaded")
            return False
        
        print("✅ API credentials loaded")
        
        # Import client (try different approaches)
        try:
            from binance.client import Client
        except ImportError:
            try:
                from binance import Client
            except ImportError:
                try:
                    import binance
                    Client = binance.Client
                except ImportError:
                    print("❌ Binance client not available")
                    return False
        
        # Initialize client
        client = Client(api_key, api_secret, testnet=False)
        print("✅ Binance client connected")
        
        # Get account balances
        account_info = client.get_account()
        
        # Find EGLD balance
        egld_balance = None
        for asset in account_info['balances']:
            if asset['asset'] == 'EGLD':
                free_balance = float(asset['free'])
                locked_balance = float(asset['locked'])
                egld_balance = {
                    'free': free_balance,
                    'locked': locked_balance,
                    'total': free_balance + locked_balance
                }
                break
        
        if not egld_balance or egld_balance['total'] <= 0:
            print("⚠️ No EGLD position found")
            return True
        
        print(f"💰 EGLD Position Found:")
        print(f"   Free: {egld_balance['free']:.6f}")
        print(f"   Locked: {egld_balance['locked']:.6f}") 
        print(f"   Total: {egld_balance['total']:.6f}")
        
        # Get current EGLD price
        ticker = client.get_symbol_ticker(symbol='EGLDUSDT')
        current_price = float(ticker['price'])
        position_value = egld_balance['total'] * current_price
        
        print(f"📊 Current Price: ${current_price:.4f}")
        print(f"📊 Position Value: ${position_value:.2f}")
        
        # Check for existing stop-loss orders
        open_orders = client.get_open_orders(symbol='EGLDUSDT')
        
        protection_exists = False
        for order in open_orders:
            if order['side'] == 'SELL':
                print(f"✅ Existing protection: {order['type']} @ ${float(order['price']):.4f}")
                protection_exists = True
        
        if protection_exists:
            print("🛡️ EGLD position already protected!")
            return True
        
        # No protection exists - place stop-loss order
        if egld_balance['free'] <= 0:
            print("⚠️ No free EGLD balance to protect (all locked)")
            return True
        
        print("🚨 NO PROTECTION FOUND - PLACING STOP-LOSS ORDER")
        
        # Calculate stop-loss parameters
        stop_loss_percentage = 0.5  # 0.5% stop loss
        stop_price = current_price * (1 - stop_loss_percentage / 100)
        
        # Use 99% of free balance to avoid precision issues
        quantity_to_protect = egld_balance['free'] * 0.99
        
        # Round to proper precision (typical for EGLD: 6 decimals for quantity, 4 for price)
        quantity_rounded = round(quantity_to_protect, 6)
        stop_price_rounded = round(stop_price, 4)
        
        print(f"🛡️ Stop-Loss Order Details:")
        print(f"   Quantity: {quantity_rounded} EGLD")
        print(f"   Stop Price: ${stop_price_rounded:.4f} (-{stop_loss_percentage}%)")
        print(f"   Current Price: ${current_price:.4f}")
        
        # Place limit sell order as stop-loss protection
        try:
            order = client.order_limit_sell(
                symbol='EGLDUSDT',
                quantity=f"{quantity_rounded:.6f}",
                price=f"{stop_price_rounded:.4f}",
                timeInForce='GTC'
            )
            
            print("🎉 STOP-LOSS ORDER PLACED SUCCESSFULLY!")
            print(f"   Order ID: {order['orderId']}")
            print(f"   Status: {order['status']}")
            print(f"   Price: ${float(order['price']):.4f}")
            print(f"   Quantity: {float(order['origQty']):.6f} EGLD")
            
            # Log the protection
            protection_log = {
                'timestamp': datetime.now().isoformat(),
                'symbol': 'EGLD/USDT',
                'order_id': order['orderId'],
                'type': 'stop_loss_protection',
                'quantity': float(order['origQty']),
                'price': float(order['price']),
                'current_price': current_price,
                'protection_percentage': stop_loss_percentage
            }
            
            import json
            with open('egld_protection.json', 'w') as f:
                json.dump(protection_log, f, indent=2)
            
            print("✅ EGLD POSITION PROTECTION COMPLETE!")
            print("📝 Protection details logged to egld_protection.json")
            
            return True
            
        except Exception as order_error:
            print(f"❌ Failed to place stop-loss order: {order_error}")
            
            # Try with smaller quantity
            try:
                smaller_quantity = round(quantity_to_protect * 0.95, 6)
                print(f"🔄 Retrying with smaller quantity: {smaller_quantity}")
                
                order = client.order_limit_sell(
                    symbol='EGLDUSDT',
                    quantity=f"{smaller_quantity:.6f}",
                    price=f"{stop_price_rounded:.4f}",
                    timeInForce='GTC'
                )
                
                print("✅ Protection placed with smaller quantity!")
                print(f"   Order ID: {order['orderId']}")
                return True
                
            except Exception as retry_error:
                print(f"❌ Retry failed: {retry_error}")
                
                # Manual instructions
                print("\n🚨 AUTOMATIC PROTECTION FAILED - MANUAL ACTION REQUIRED:")
                print("Please manually place this order on Binance:")
                print(f"   Symbol: EGLD/USDT")
                print(f"   Type: Limit Sell")
                print(f"   Quantity: {quantity_rounded}")
                print(f"   Price: ${stop_price_rounded:.4f}")
                print("   Time in Force: GTC (Good Till Cancelled)")
                
                return False
    
    except Exception as e:
        print(f"❌ Critical error: {e}")
        print("\n🚨 MANUAL PROTECTION REQUIRED:")
        print("1. Open Binance US")
        print("2. Go to EGLD/USDT trading pair")
        print("3. Place a LIMIT SELL order:")
        print("   - Use your EGLD balance")
        print("   - Set price 0.5% below current market price")
        return False

if __name__ == "__main__":
    print("🚨 EGLD EMERGENCY PROTECTION SCRIPT")
    print("=" * 50)
    
    success = protect_egld_position()
    
    if success:
        print("\n✅ EGLD PROTECTION PROCESS COMPLETED SUCCESSFULLY")
    else:
        print("\n❌ EGLD PROTECTION FAILED - MANUAL INTERVENTION REQUIRED")
        print("Please place a manual stop-loss order for your EGLD position")
