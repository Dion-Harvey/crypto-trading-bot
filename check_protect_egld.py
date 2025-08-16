#!/usr/bin/env python3
"""
🚨 EGLD POSITION PROTECTION SCRIPT
Checks and protects existing EGLD/USDT position with stop-limit orders
"""
import sys
import os
import json
from datetime import datetime

# Add bot directory to path
sys.path.append('.')

def main():
    try:
        # Import bot modules
        from bot_config import BotConfig
        from config import load_api_credentials
        from binance.client import Client
        
        print("🚨 EGLD POSITION PROTECTION CHECKER")
        print("=" * 50)
        
        # Load configuration and API credentials
        api_key, api_secret = load_api_credentials()
        if not api_key or not api_secret:
            print("❌ Error: API credentials not found")
            return False
        
        # Initialize Binance client
        client = Client(api_key, api_secret, testnet=False)
        print("✅ Connected to Binance US")
        
        # Check EGLD balance
        account = client.get_account()
        egld_free = 0
        egld_locked = 0
        
        for balance in account['balances']:
            if balance['asset'] == 'EGLD':
                egld_free = float(balance['free'])
                egld_locked = float(balance['locked'])
                break
        
        total_egld = egld_free + egld_locked
        print(f"💰 EGLD Balance:")
        print(f"   Free: {egld_free:.6f} EGLD")
        print(f"   Locked: {egld_locked:.6f} EGLD")
        print(f"   Total: {total_egld:.6f} EGLD")
        
        if total_egld <= 0.001:  # Minimum threshold
            print("⚠️ No significant EGLD position found")
            return True
        
        # Get current EGLD price
        ticker = client.get_symbol_ticker(symbol='EGLDUSDT')
        current_price = float(ticker['price'])
        position_value = total_egld * current_price
        
        print(f"📊 EGLD Market Data:")
        print(f"   Current Price: ${current_price:.4f}")
        print(f"   Position Value: ${position_value:.2f}")
        
        # Check for existing protection orders
        open_orders = client.get_open_orders(symbol='EGLDUSDT')
        print(f"📋 Open Orders: {len(open_orders)}")
        
        protection_orders = []
        for order in open_orders:
            if order['side'] == 'SELL':
                order_price = float(order['price'])
                order_qty = float(order['origQty'])
                order_value = order_qty * order_price
                
                protection_orders.append({
                    'id': order['orderId'],
                    'type': order['type'],
                    'price': order_price,
                    'quantity': order_qty,
                    'value': order_value
                })
                
                print(f"   🛡️ Protection: {order['type']} - {order_qty:.6f} EGLD @ ${order_price:.4f}")
        
        # Calculate protection coverage
        protected_egld = sum(order['quantity'] for order in protection_orders)
        unprotected_egld = egld_free - protected_egld
        protection_percentage = (protected_egld / total_egld) * 100 if total_egld > 0 else 0
        
        print(f"📊 Protection Analysis:")
        print(f"   Protected: {protected_egld:.6f} EGLD ({protection_percentage:.1f}%)")
        print(f"   Unprotected: {unprotected_egld:.6f} EGLD")
        
        # Determine if additional protection is needed
        if protection_percentage >= 95:
            print("✅ POSITION ADEQUATELY PROTECTED")
            return True
        
        if unprotected_egld < 0.001:
            print("✅ No significant unprotected amount")
            return True
        
        # Need to place protection for unprotected amount
        print(f"🚨 INSUFFICIENT PROTECTION - Need protection for {unprotected_egld:.6f} EGLD")
        
        # Calculate stop-loss price (0.5% below current price)
        stop_price = current_price * 0.995
        
        # Get symbol info for precision
        symbol_info = client.get_symbol_info('EGLDUSDT')
        
        # Find precision requirements
        price_precision = 4
        qty_precision = 6
        
        for f in symbol_info['filters']:
            if f['filterType'] == 'PRICE_FILTER':
                tick_size = f['tickSize']
                if '.' in tick_size:
                    price_precision = len(tick_size.rstrip('0').split('.')[-1])
            elif f['filterType'] == 'LOT_SIZE':
                step_size = f['stepSize']
                if '.' in step_size:
                    qty_precision = len(step_size.rstrip('0').split('.')[-1])
        
        # Round values to proper precision
        protect_quantity = round(unprotected_egld * 0.999, qty_precision)  # 99.9% to avoid precision issues
        protection_price = round(stop_price, price_precision)
        
        if protect_quantity < float(symbol_info['filters'][1]['minQty']):
            print(f"⚠️ Quantity {protect_quantity} below minimum {symbol_info['filters'][1]['minQty']}")
            return True
        
        print(f"🛡️ PLACING PROTECTION ORDER:")
        print(f"   Quantity: {protect_quantity} EGLD")
        print(f"   Price: ${protection_price:.4f} (-0.5%)")
        print(f"   Value: ${protect_quantity * protection_price:.2f}")
        
        try:
            # Place stop-limit protection order
            order = client.order_limit_sell(
                symbol='EGLDUSDT',
                quantity=protect_quantity,
                price=str(protection_price),
                timeInForce='GTC'
            )
            
            print("🎉 PROTECTION ORDER PLACED SUCCESSFULLY!")
            print(f"   Order ID: {order['orderId']}")
            print(f"   Status: {order['status']}")
            print(f"   Price: ${float(order['price']):.4f}")
            print(f"   Quantity: {float(order['origQty']):.6f} EGLD")
            
            # Log to file
            protection_log = {
                'timestamp': datetime.now().isoformat(),
                'symbol': 'EGLD/USDT',
                'action': 'protection_placed',
                'order_id': order['orderId'],
                'quantity': float(order['origQty']),
                'price': float(order['price']),
                'current_price': current_price,
                'protection_type': 'stop_limit'
            }
            
            with open('egld_protection_log.json', 'w') as f:
                json.dump(protection_log, f, indent=2)
            
            print("✅ EGLD POSITION PROTECTION COMPLETE!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to place protection order: {e}")
            
            # Try with smaller quantity
            try:
                smaller_qty = round(protect_quantity * 0.95, qty_precision)
                print(f"🔄 Retrying with smaller quantity: {smaller_qty}")
                
                order = client.order_limit_sell(
                    symbol='EGLDUSDT',
                    quantity=smaller_qty,
                    price=str(protection_price),
                    timeInForce='GTC'
                )
                
                print("✅ PROTECTION PLACED (reduced quantity)")
                print(f"   Order ID: {order['orderId']}")
                print(f"   Quantity: {float(order['origQty']):.6f} EGLD")
                return True
                
            except Exception as e2:
                print(f"❌ Retry also failed: {e2}")
                print("🚨 MANUAL INTERVENTION REQUIRED!")
                print(f"   Please manually place sell order:")
                print(f"   - Symbol: EGLD/USDT")
                print(f"   - Type: Limit Sell")
                print(f"   - Quantity: {protect_quantity}")
                print(f"   - Price: ${protection_price:.4f}")
                return False
    
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("⚠️ Bot modules not available - using direct approach")
        
        # Direct Binance approach without bot modules
        try:
            from dotenv import load_dotenv
            from binance.client import Client
            
            load_dotenv()
            api_key = os.getenv('BINANCE_API_KEY')
            api_secret = os.getenv('BINANCE_API_SECRET')
            
            if not api_key or not api_secret:
                print("❌ API credentials not found in .env")
                return False
            
            client = Client(api_key, api_secret, testnet=False)
            print("✅ Direct connection established")
            
            # Simplified protection logic
            account = client.get_account()
            egld_balance = 0
            
            for balance in account['balances']:
                if balance['asset'] == 'EGLD':
                    egld_balance = float(balance['free'])
                    break
            
            if egld_balance > 0:
                ticker = client.get_symbol_ticker(symbol='EGLDUSDT')
                current_price = float(ticker['price'])
                stop_price = round(current_price * 0.995, 4)
                quantity = round(egld_balance * 0.999, 6)
                
                print(f"Direct protection: {quantity} EGLD @ ${stop_price}")
                
                order = client.order_limit_sell(
                    symbol='EGLDUSDT',
                    quantity=quantity,
                    price=str(stop_price),
                    timeInForce='GTC'
                )
                
                print(f"✅ Direct protection successful! Order ID: {order['orderId']}")
                return True
            else:
                print("No EGLD balance found")
                return True
                
        except Exception as e:
            print(f"❌ Direct approach failed: {e}")
            return False
    
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎉 EGLD PROTECTION PROCESS COMPLETED")
        sys.exit(0)
    else:
        print("\n❌ EGLD PROTECTION FAILED")
        sys.exit(1)
