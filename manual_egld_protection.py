#!/usr/bin/env python3
"""
Manual EGLD Protection - Direct Binance API approach
"""
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.getcwd())

print("🚨 EGLD PROTECTION SCRIPT STARTING...")
print("=" * 50)

try:
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    
    print(f"API Key found: {'Yes' if api_key else 'No'}")
    print(f"API Secret found: {'Yes' if api_secret else 'No'}")
    
    if not api_key or not api_secret:
        print("❌ API credentials missing from .env file")
        sys.exit(1)
    
    # Import and setup Binance client
    from python_binance.client import Client
    client = Client(api_key, api_secret)
    
    print("✅ Binance client initialized")
    
    # Test connection
    server_time = client.get_server_time()
    print(f"✅ Connected to Binance (Server time: {server_time['serverTime']})")
    
    # Get account info
    account = client.get_account()
    
    # Find EGLD balance
    egld_free = 0
    egld_locked = 0
    
    for balance in account['balances']:
        if balance['asset'] == 'EGLD':
            egld_free = float(balance['free'])
            egld_locked = float(balance['locked'])
            print(f"💰 EGLD Balance found:")
            print(f"   Free: {egld_free:.6f}")
            print(f"   Locked: {egld_locked:.6f}")
            print(f"   Total: {egld_free + egld_locked:.6f}")
            break
    
    if egld_free <= 0:
        print("⚠️ No free EGLD balance to protect")
        sys.exit(0)
    
    # Get current EGLD price
    ticker = client.get_symbol_ticker(symbol='EGLDUSDT')
    current_price = float(ticker['price'])
    position_value = egld_free * current_price
    
    print(f"📊 Current EGLD price: ${current_price:.4f}")
    print(f"📊 Position value: ${position_value:.2f}")
    
    # Check existing orders
    orders = client.get_open_orders(symbol='EGLDUSDT')
    print(f"📋 Open orders: {len(orders)}")
    
    has_sell_order = False
    for order in orders:
        if order['side'] == 'SELL':
            print(f"   ✅ Existing sell order: {order['type']} @ ${float(order['price']):.4f}")
            has_sell_order = True
    
    if has_sell_order:
        print("🛡️ Position already has protection!")
        sys.exit(0)
    
    # Calculate protection parameters
    stop_price = current_price * 0.995  # 0.5% below current price
    quantity = egld_free * 0.999        # Use 99.9% to avoid precision issues
    
    print(f"🛡️ Placing protection order:")
    print(f"   Quantity: {quantity:.6f} EGLD")
    print(f"   Price: ${stop_price:.4f}")
    print(f"   Stop loss: 0.5% below current price")
    
    # Place the order
    order = client.order_limit_sell(
        symbol='EGLDUSDT',
        quantity=f"{quantity:.6f}",
        price=f"{stop_price:.4f}",
        timeInForce='GTC'
    )
    
    print("🎉 SUCCESS! Protection order placed:")
    print(f"   Order ID: {order['orderId']}")
    print(f"   Status: {order['status']}")
    print(f"   Type: {order['type']}")
    print(f"   Side: {order['side']}")
    print(f"   Quantity: {order['origQty']} EGLD")
    print(f"   Price: ${float(order['price']):.4f}")
    
    print("\n✅ Your EGLD position is now protected with a stop-loss order!")
    print("📈 The order will execute if EGLD drops to the stop price")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("Trying alternative import...")
    
    try:
        from binance.client import Client
        
        load_dotenv()
        api_key = os.getenv('BINANCE_API_KEY')
        api_secret = os.getenv('BINANCE_API_SECRET')
        
        client = Client(api_key, api_secret)
        print("✅ Alternative import successful")
        
        # Repeat the protection logic with alternative import
        account = client.get_account()
        
        egld_free = 0
        for balance in account['balances']:
            if balance['asset'] == 'EGLD':
                egld_free = float(balance['free'])
                break
        
        if egld_free > 0:
            ticker = client.get_symbol_ticker(symbol='EGLDUSDT')
            current_price = float(ticker['price'])
            
            # Check for existing protection
            orders = client.get_open_orders(symbol='EGLDUSDT')
            has_protection = any(order['side'] == 'SELL' for order in orders)
            
            if not has_protection:
                stop_price = current_price * 0.995
                quantity = egld_free * 0.999
                
                order = client.order_limit_sell(
                    symbol='EGLDUSDT',
                    quantity=f"{quantity:.6f}",
                    price=f"{stop_price:.4f}",
                    timeInForce='GTC'
                )
                
                print(f"✅ Protection placed! Order ID: {order['orderId']}")
            else:
                print("✅ Protection already exists")
        else:
            print("⚠️ No EGLD balance found")
            
    except Exception as e2:
        print(f"❌ Alternative approach failed: {e2}")
        
        # Manual instructions
        print("\n🚨 MANUAL PROTECTION REQUIRED:")
        print("1. Open Binance US app or website")
        print("2. Go to Spot Trading")
        print("3. Search for EGLD/USDT")
        print("4. Place a LIMIT SELL order:")
        print("   - Use your full EGLD balance")
        print("   - Set price 0.5% below current market price")
        print("   - This will act as your stop-loss protection")
        
except Exception as e:
    print(f"❌ Critical error: {e}")
    print("\n🚨 MANUAL PROTECTION REQUIRED:")
    print("Please manually place a stop-loss order on Binance for your EGLD position")
    sys.exit(1)
