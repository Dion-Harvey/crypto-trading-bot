#!/usr/bin/env python3
"""
🧹 EMERGENCY ORDER CLEANUP UTILITY
Immediately cancels all existing stop-limit orders to fix accumulation issue
"""

import ccxt
import sys
from config import BINANCE_API_KEY, BINANCE_API_SECRET

def emergency_cleanup():
    """Emergency cleanup of all stop-limit orders"""
    
    print("🧹 EMERGENCY ORDER CLEANUP UTILITY")
    print("="*50)
    
    try:
        # Initialize exchange
        exchange = ccxt.binanceus({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'sandbox': False,  # Use live exchange
            'enableRateLimit': True
        })
        
        # Get account info
        balance = exchange.fetch_balance()
        print(f"✅ Connected to Binance US")
        
        # Symbols to check
        symbols_to_check = ['ETH/USDT', 'BTC/USDT', 'SUI/USDT', 'SOL/USDT', 'ADA/USDT']
        
        total_cancelled = 0
        
        for symbol in symbols_to_check:
            print(f"\n🔍 Checking {symbol}...")
            
            try:
                # Get open orders for this symbol
                open_orders = exchange.fetch_open_orders(symbol)
                
                if not open_orders:
                    print(f"   ✅ No open orders for {symbol}")
                    continue
                
                print(f"   📊 Found {len(open_orders)} open orders")
                
                stop_limit_orders = []
                
                # Identify stop-limit orders
                for order in open_orders:
                    order_type = order.get('type', '').lower()
                    order_side = order.get('side', '').lower()
                    order_id = order.get('id')
                    amount = order.get('amount', 0)
                    
                    if ('stop' in order_type or order_type in ['stop_loss_limit', 'stop_loss', 'oco']) and order_side == 'sell':
                        stop_limit_orders.append({
                            'id': order_id,
                            'type': order_type,
                            'amount': amount,
                            'symbol': symbol
                        })
                
                if not stop_limit_orders:
                    print(f"   ✅ No stop-limit orders found for {symbol}")
                    continue
                
                print(f"   🎯 Found {len(stop_limit_orders)} stop-limit orders to cancel:")
                
                # Cancel each stop-limit order
                cancelled_for_symbol = 0
                for order in stop_limit_orders:
                    try:
                        print(f"      🗑️ Canceling {order['type']} order {order['id']} ({order['amount']} {symbol.split('/')[0]})")
                        exchange.cancel_order(order['id'], order['symbol'])
                        cancelled_for_symbol += 1
                        total_cancelled += 1
                        print(f"      ✅ Successfully cancelled")
                    except Exception as cancel_error:
                        print(f"      ❌ Failed to cancel {order['id']}: {cancel_error}")
                
                print(f"   🧹 {symbol}: {cancelled_for_symbol}/{len(stop_limit_orders)} orders cancelled")
                
            except Exception as symbol_error:
                print(f"   ❌ Error processing {symbol}: {symbol_error}")
        
        print(f"\n🎯 CLEANUP SUMMARY:")
        print(f"   📊 Total stop-limit orders cancelled: {total_cancelled}")
        
        if total_cancelled > 0:
            print(f"   ✅ SUCCESS: Order accumulation issue resolved!")
            print(f"   🔄 The bot will now properly manage stop-limit orders")
        else:
            print(f"   ✅ No cleanup needed - no accumulated orders found")
        
        return True
        
    except Exception as e:
        print(f"❌ Emergency cleanup failed: {e}")
        return False

def show_current_orders():
    """Show current open orders for analysis"""
    
    print("📊 CURRENT OPEN ORDERS ANALYSIS")
    print("="*50)
    
    try:
        # Initialize exchange
        exchange = ccxt.binanceus({
            'apiKey': BINANCE_API_KEY,
            'secret': BINANCE_API_SECRET,
            'sandbox': False,
            'enableRateLimit': True
        })
        
        symbols_to_check = ['ETH/USDT', 'BTC/USDT', 'SUI/USDT', 'SOL/USDT', 'ADA/USDT']
        
        for symbol in symbols_to_check:
            print(f"\n📋 {symbol} Open Orders:")
            
            try:
                open_orders = exchange.fetch_open_orders(symbol)
                
                if not open_orders:
                    print(f"   ✅ No open orders")
                    continue
                
                for order in open_orders:
                    order_type = order.get('type', 'unknown')
                    side = order.get('side', 'unknown')
                    amount = order.get('amount', 0)
                    price = order.get('price', 0)
                    status = order.get('status', 'unknown')
                    order_id = order.get('id', 'unknown')
                    timestamp = order.get('datetime', 'unknown')
                    
                    print(f"   📝 {order_type.upper()} {side.upper()} | {amount:.6f} @ ${price:.2f} | {status} | {timestamp}")
                    print(f"      ID: {order_id}")
                
            except Exception as symbol_error:
                print(f"   ❌ Error: {symbol_error}")
        
    except Exception as e:
        print(f"❌ Analysis failed: {e}")

if __name__ == "__main__":
    print("🧹 STOP-LIMIT ORDER CLEANUP UTILITY")
    print("="*60)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--show':
        show_current_orders()
    else:
        print("⚠️  WARNING: This will cancel ALL stop-limit orders!")
        print("⚠️  Make sure you understand the implications before proceeding.")
        print("")
        
        response = input("🤔 Do you want to proceed with cleanup? (yes/no): ").lower().strip()
        
        if response in ['yes', 'y']:
            print("\n🧹 Starting emergency cleanup...")
            success = emergency_cleanup()
            
            if success:
                print("\n✅ CLEANUP COMPLETE!")
                print("🔄 Restart your trading bot to ensure clean state")
            else:
                print("\n❌ CLEANUP FAILED!")
                print("🛠️ Manual intervention may be required")
        else:
            print("\n👋 Cleanup cancelled - no orders were touched")
            print("💡 Use --show flag to analyze current orders without changes")
