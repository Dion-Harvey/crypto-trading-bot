#!/usr/bin/env python3
"""
Direct EGLD Protection Script
"""
import sys
import os
from dotenv import load_dotenv
sys.path.append('.')

# Load environment
load_dotenv()

try:
    from binance.client import Client
    
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    
    if not api_key or not api_secret:
        print("❌ API credentials not found")
        sys.exit(1)
    
    # Connect to Binance
    client = Client(api_key, api_secret, testnet=False)
    print("✅ Connected to Binance US")
    
    # Get EGLD balance
    account = client.get_account()
    egld_balance = 0
    
    for asset in account['balances']:
        if asset['asset'] == 'EGLD':
            free_balance = float(asset['free'])
            locked_balance = float(asset['locked'])
            egld_balance = free_balance
            print(f"💰 EGLD Balance: {egld_balance:.6f} EGLD")
            print(f"   Free: {free_balance:.6f}, Locked: {locked_balance:.6f}")
            break
    
    if egld_balance <= 0:
        print("⚠️ No EGLD position found to protect")
        sys.exit(0)
    
    # Get current EGLD price
    ticker = client.get_symbol_ticker(symbol='EGLDUSDT')
    current_price = float(ticker['price'])
    print(f"📊 Current EGLD Price: ${current_price:.4f}")
    
    # Check existing orders
    open_orders = client.get_open_orders(symbol='EGLDUSDT')
    print(f"📋 Existing orders: {len(open_orders)}")
    
    has_protection = False
    for order in open_orders:
        if order['side'] == 'SELL':
            print(f"✅ Found protection: {order['type']} @ ${float(order['price']):.4f}")
            has_protection = True
    
    if has_protection:
        print("🛡️ EGLD position already protected!")
        sys.exit(0)
    
    # Calculate stop loss (0.5% below current price)
    stop_loss_price = current_price * 0.995
    quantity_to_protect = egld_balance * 0.999  # Use 99.9% to avoid precision issues
    
    print(f"🚨 PLACING EMERGENCY PROTECTION:")
    print(f"   Quantity: {quantity_to_protect:.6f} EGLD")
    print(f"   Stop Price: ${stop_loss_price:.4f} (-0.5%)")
    
    # Get symbol info for precision
    info = client.get_symbol_info('EGLDUSDT')
    
    # Find price and quantity filters
    price_precision = 4  # Default
    qty_precision = 6    # Default
    
    for f in info['filters']:
        if f['filterType'] == 'PRICE_FILTER':
            tick_size = f['tickSize']
            if '.' in tick_size:
                price_precision = len(tick_size.rstrip('0').split('.')[-1])
        elif f['filterType'] == 'LOT_SIZE':
            step_size = f['stepSize']
            if '.' in step_size:
                qty_precision = len(step_size.rstrip('0').split('.')[-1])
    
    # Round values
    stop_price_rounded = round(stop_loss_price, price_precision)
    quantity_rounded = round(quantity_to_protect, qty_precision)
    
    print(f"🔧 Rounded: Qty={quantity_rounded}, Price=${stop_price_rounded}")
    
    # Place limit sell order as protection
    try:
        order = client.order_limit_sell(
            symbol='EGLDUSDT',
            quantity=quantity_rounded,
            price=str(stop_price_rounded),
            timeInForce='GTC'
        )
        
        print("🎉 PROTECTION SUCCESSFUL!")
        print(f"   Order ID: {order['orderId']}")
        print(f"   Type: {order['type']}")
        print(f"   Price: ${float(order['price']):.4f}")
        print(f"   Quantity: {float(order['origQty']):.6f}")
        print("✅ Your EGLD position is now protected!")
        
    except Exception as e:
        print(f"❌ Protection failed: {e}")
        
        # Try with smaller quantity
        try:
            smaller_qty = round(quantity_to_protect * 0.99, qty_precision)
            print(f"🔄 Retrying with smaller quantity: {smaller_qty}")
            
            order = client.order_limit_sell(
                symbol='EGLDUSDT',
                quantity=smaller_qty,
                price=str(stop_price_rounded),
                timeInForce='GTC'
            )
            
            print("🎉 PROTECTION SUCCESSFUL (smaller quantity)!")
            print(f"   Order ID: {order['orderId']}")
            print(f"   Price: ${float(order['price']):.4f}")
            print(f"   Quantity: {float(order['origQty']):.6f}")
            
        except Exception as e2:
            print(f"❌ Second attempt failed: {e2}")
            print("🚨 MANUAL PROTECTION REQUIRED!")
            print(f"   Place sell order for {quantity_rounded} EGLD at ${stop_price_rounded}")

except Exception as e:
    print(f"❌ Critical error: {e}")
    sys.exit(1)
